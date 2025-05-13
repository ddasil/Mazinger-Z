from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import yt_dlp
import uuid
import os
import json
from openai import OpenAI
import openai
import requests
from bs4 import BeautifulSoup
import lyricsgenius


# ✅ API 키 세팅
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
client = OpenAI(api_key=settings.OPENAI_API_KEY)
GENIUS_TOKEN = os.getenv("GENIUS_ACCESS_TOKEN")
genius = lyricsgenius.Genius(GENIUS_TOKEN, skip_non_songs=True, excluded_terms=["(Remix)", "(Live)"])

# ✅ 메인 검색 페이지
def search_view(request):
    return render(request, 'search.html', {
        'youtube_api_key': settings.YOUTUBE_API_KEY
    })

# ✅ GPT로 영상 제목 분석: 가수 / 곡명 추출
@csrf_exempt
def analyze_title(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        title = body.get('title', '')

        prompt = f"""
        다음 유튜브 영상 제목에서 가수와 곡명을 JSON 형식으로 추출해줘.
        - 형식: {{ "artist": ..., "title": ... }}
        - 피처링, 앨범 정보, 가사, OST, MV 등은 무시하고 곡의 메인 정보만 추출해줘.
        예: "{title}"
        """

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            content = response.choices[0].message.content
            parsed = json.loads(content)
        except Exception as e:
            print("🔥 GPT 분석 예외:", e)
            parsed = {"artist": None, "title": None, "error": str(e)}

        return JsonResponse(parsed)

    return JsonResponse({'error': 'Only POST requests are allowed.'}, status=405)

# ✅ Genius API + 크롤링으로 가사 가져오기
@csrf_exempt
def get_lyrics(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            artist = body.get("artist")
            title = body.get("title")

            print(f"🎤 가사 요청: artist={artist}, title={title}")

            if not artist or not title:
                return JsonResponse({"error": "Missing artist or title"}, status=400)

            song = genius.search_song(title, artist)
            if not song or not song.url:
                return JsonResponse({"error": "No song found on Genius"}, status=404)

            # 🕸️ 크롤링
            res = requests.get(song.url)
            soup = BeautifulSoup(res.text, 'html.parser')
            lyrics_divs = soup.find_all("div", attrs={"data-lyrics-container": "true"})
            raw_lyrics = "\n".join(div.get_text(separator="\n").strip() for div in lyrics_divs)

            # 🧼 메타데이터 제거 함수
            def clean_lyrics(raw: str) -> str:
                skip_keywords = [
                    "Contributors", "Translations", "Romanization",
                    "English", "Français", "Deutsch", "Español"
                ]
                lines = raw.splitlines()
                filtered = [
                    line.strip() for line in lines
                    if line.strip() and not any(kw in line for kw in skip_keywords)
                ]
                return "\n".join(filtered).strip()

            cleaned_lyrics = clean_lyrics(raw_lyrics)

            return JsonResponse({
                "lyrics": cleaned_lyrics or "가사를 찾을 수 없습니다."
            })

        except Exception as e:
            print("🔥 get_lyrics 예외 발생:", e)
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({'error': 'Only POST requests are allowed.'}, status=405)


@csrf_exempt
def translate_lyrics(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        original_lyrics = body.get('lyrics', '')

        if not original_lyrics:
            return JsonResponse({"error": "No lyrics provided"}, status=400)

        try:
            # 언어 감지
            detect_prompt = f"""
            다음 가사의 주된 언어가 무엇인지 알려줘. 답변은 Korean, English, Japanese, Chinese 중 하나로만.
            가사:
            {original_lyrics}
            """

            detect_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": detect_prompt}],
                temperature=0
            )
            detected_language = detect_response.choices[0].message.content.strip()

            all_languages = {
                'Korean': 'ko',
                'English': 'en',
                'Japanese': 'ja',
                'Chinese': 'zh'
            }
            target_languages = {k: v for k, v in all_languages.items() if k != detected_language}

            # 번역 요청
            translate_prompt = f"""
            다음 가사를 {', '.join(target_languages.keys())}로 번역해줘.

            **주의사항**:
            - 반드시 JSON 포맷으로만 출력해.
            - JSON 이외에 다른 텍스트(예: 설명, 인사말)는 절대 추가하지 마.
            - 키는 "{list(target_languages.values())[0]}","{list(target_languages.values())[1]}","{list(target_languages.values())[2]}" 형태여야 해.

            가사:
            {original_lyrics}
            """

            translate_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": translate_prompt}],
                temperature=0.3
            )

            # 📌 추가할 부분
            print("🔥 detect_response:", detect_response.choices[0].message.content)
            print("🔥 translate_response:", translate_response.choices[0].message.content)

            translations = json.loads(translate_response.choices[0].message.content)

            # 📌 여기 추가해
            if isinstance(translations.get('en'), dict):
                translations['en'] = "\n".join(translations['en'].values())

            if isinstance(translations.get('ja'), dict):
                translations['ja'] = "\n".join(translations['ja'].values())

            if isinstance(translations.get('zh'), dict):
                translations['zh'] = "\n".join(translations['zh'].values())


            response_data = {
                'detected': all_languages.get(detected_language, 'unknown'),
                **translations
            }
            return JsonResponse(response_data)

        except Exception as e:
            print(f"🔥 번역 에러 발생: {e}")
            return JsonResponse({"error": "번역 실패", "detail": str(e)}, status=500)
        
# YouTube 영상 ➔ mp3 파일 다운로드 
@csrf_exempt
def download_mp3(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            video_url = body.get('url')

            if not video_url:
                return JsonResponse({'error': 'No video URL provided'}, status=400)

            # ✅ 저장할 파일 이름 생성 (UUID로 중복 방지)
            unique_id = uuid.uuid4().hex
            output_path = os.path.join(settings.MEDIA_ROOT, f"{unique_id}")

            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': output_path,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                # 'quiet': True,
                'ffmpeg_location': 'C:/ffmpeg/bin/ffmpeg.exe',  # ✅ 이 줄 추가!
            }

            # ✅ 다운로드 실행
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])

            # ✅ 다운로드 성공하면 media 경로 반환
            media_url = request.build_absolute_uri(settings.MEDIA_URL + f"{unique_id}.mp3")
            return JsonResponse({'success': True, 'url': media_url})

        except Exception as e:
            print("🔥 mp3 다운로드 에러:", e)
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Only POST method allowed'}, status=405)


# 자동완성(django 서버가 구글 sugges api 호출하는 방법)
def autocomplete(request):
    query = request.GET.get('q', '')
    if not query:
        return JsonResponse({'suggestions': []})

    try:
        # 구글 Suggest API 요청
        response = requests.get(
            'https://suggestqueries.google.com/complete/search',
            params={
                'client': 'firefox',  # 여기는 그대로 둬도 됨
                'ds': 'yt',           # 유튜브 전용 데이터소스
                'q': query
            },
            timeout=5
        )
        result = response.json()
        suggestions = result[1] if len(result) > 1 else []
        return JsonResponse({'suggestions': suggestions})

    except Exception as e:
        print(f"Autocomplete Error: {e}")
        return JsonResponse({'suggestions': []})


@csrf_exempt
def delete_mp3(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        mp3_url = data.get('mp3Url')

        if not mp3_url:
            return JsonResponse({'success': False, 'error': 'No mp3Url provided'})

        filename = os.path.basename(mp3_url)
        file_path = os.path.join(settings.MEDIA_ROOT, filename)

        print("🔥 요청된 mp3Url:", mp3_url)
        print("🧩 추출된 파일명:", filename)
        print("🧨 실제 삭제 대상 경로:", file_path)


        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print("✅ 삭제 성공:", file_path)
                return JsonResponse({'success': True})
            else:
                print("❌ 파일 없음:", file_path)
                return JsonResponse({'success': False, 'error': 'File not found'})
        except Exception as e:
            print("❗ 삭제 중 오류:", str(e))
            return JsonResponse({'success': False, 'error': str(e)})



