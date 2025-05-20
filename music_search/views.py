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
import re
from .models import TaggedSong
from django.contrib.auth.decorators import login_required
# from .models import FavoriteSong
from .models import FullLyrics
from django.db.models.functions import Lower


# ✅ API 키 세팅
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
client = OpenAI(api_key=settings.OPENAI_API_KEY)
GENIUS_TOKEN = os.getenv("GENIUS_ACCESS_TOKEN")
genius = lyricsgenius.Genius(GENIUS_TOKEN, skip_non_songs=True, excluded_terms=["(Remix)", "(Live)"])
genius.timeout = 15  # ✅ 추가

# ✅ 메인 검색 페이지
def search_view(request):
    # favorites = []
    # if request.user.is_authenticated:
    #     favorites = FavoriteSong.objects.filter(user=request.user)
    return render(request, 'search.html', {
        'youtube_api_key': settings.YOUTUBE_API_KEY,
        # 'favorites': favorites,   ← ❌ 이 줄도 제거
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

# ✅ 여기에 넣어라
def translate_to(language_name, cleaned_lyrics):
    prompt = f"""
    다음 노래 가사를 {language_name}로 번역해줘.

    - 절대 요약하지 말고 모든 줄을 번역할 것
    - 줄 순서와 줄바꿈은 그대로 유지할 것
    - 결과는 문자열 하나로만 출력하고, 설명 없이 바로 시작할 것

    가사:
    {cleaned_lyrics}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"🔥 번역 실패 ({language_name}):", e)
        return ""


# ✅ Genius API + 크롤링으로 가사 가져오기
@csrf_exempt
def get_lyrics(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            artist = body.get("artist")
            title = body.get("title")
            if not artist or not title:
                return JsonResponse({"error": "Missing artist or title"}, status=400)

            # ✅ FullLyrics에 이미 저장된 경우 바로 반환
            try:
                existing = FullLyrics.objects.get(title=title, artist=artist)
                return JsonResponse({
                    "lyrics": existing.original,
                    "ko_lyrics": existing.ko,
                    "en_lyrics": existing.en,
                    "ja_lyrics": existing.ja,
                    "zh_lyrics": existing.zh,
                })
            except FullLyrics.DoesNotExist:
                pass

            # ✅ Genius API 호출
            song = genius.search_song(title, artist)
            if not song or not song.lyrics:
                return JsonResponse({"error": "No song found on Genius"}, status=404)

            # ✅ 가사 정제
            def clean_lyrics(raw):
                skip_keywords = ["Contributors", "Translations", "Romanization", "English", "Français", "Deutsch", "Español"]
                section_tags = ["[Chorus", "[Pre-Chorus", "[Verse", "[Bridge", "[Outro", "[Intro"]  # 괄호 열기까지 비교

                lines = raw.splitlines()
                cleaned = []
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    if any(kw in line for kw in skip_keywords):
                        continue
                    if any(line.startswith(tag) for tag in section_tags):
                        continue
                    cleaned.append(line)
                return "\n".join(cleaned)

            raw_lyrics = song.lyrics
            cleaned_lyrics = clean_lyrics(raw_lyrics)

            # # ✅ GPT에게 모든 언어로 번역 요청
            # translate_prompt = f"""
            # 다음 가사를 한국어, 영어, 일본어, 중국어로 모두 번역해줘.

            # - 줄 순서와 줄바꿈을 유지할 것
            # - 절대 요약하지 말 것
            # - 형식: {{
            #     "ko": "...",
            #     "en": "...",
            #     "ja": "...",
            #     "zh": "..."
            # }}

            # 가사:
            # {cleaned_lyrics}
            # """

            # response = client.chat.completions.create(
            #     model="gpt-3.5-turbo",
            #     messages=[{"role": "user", "content": translate_prompt}],
            #     temperature=0.3
            # )

            # # ✅ JSON 추출
            # try:
            #     raw_content = response.choices[0].message.content
            #     match = re.search(r'\{[\s\S]*?\}', raw_content)
            #     if not match:
            #         raise ValueError("JSON 블록이 응답에 포함되지 않음")
            #     translations = json.loads(match.group())
            # except Exception as e:
            #     print("🔥 JSON 파싱 실패:", e)
            #     print("🔥 전체 응답 내용:", response.choices[0].message.content)
            #     return JsonResponse({"error": "GPT 응답 파싱 실패", "detail": str(e)}, status=500)


            # # ✅ 🔽 이 아래에 추가
            # for lang in ['ko', 'en', 'ja', 'zh']:
            #     if isinstance(translations.get(lang), dict):
            #         translations[lang] = "\n".join(translations[lang].values())

            # ✅ 언어별 GPT 번역 요청
            ko = translate_to("한국어", cleaned_lyrics)
            en = translate_to("영어", cleaned_lyrics)
            ja = translate_to("일본어", cleaned_lyrics)
            zh = translate_to("중국어", cleaned_lyrics)

            # ✅ DB 저장
            FullLyrics.objects.create(
                title=title,
                artist=artist,
                original=cleaned_lyrics,
                ko=ko,
                en=en,
                ja=ja,
                zh=zh
            )

            return JsonResponse({
                "lyrics": cleaned_lyrics,
                "ko_lyrics": ko,
                "en_lyrics": en,
                "ja_lyrics": ja,
                "zh_lyrics": zh,
            })

        except Exception as e:
            print("🔥 get_lyrics 예외 발생:", e)
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({'error': 'Only POST requests are allowed.'}, status=405)


# @csrf_exempt
# def translate_lyrics(request):
#     if request.method == 'POST':
#         body = json.loads(request.body)
#         original_lyrics = body.get('lyrics', '')

#         if not original_lyrics:
#             return JsonResponse({"error": "No lyrics provided"}, status=400)

#         try:
#             # 언어 감지
#             detect_prompt = f"""
#             다음 가사의 주된 언어가 무엇인지 알려줘. 답변은 Korean, English, Japanese, Chinese 중 하나로만.
#             가사:
#             {original_lyrics}
#             """
#             detect_response = client.chat.completions.create(
#                 model="gpt-3.5-turbo",
#                 messages=[{"role": "user", "content": detect_prompt}],
#                 temperature=0
#             )
#             detected_language = detect_response.choices[0].message.content.strip()

#             # Step 2: 번역 대상 언어 만들기
#             all_languages = {
#                 'Korean': 'ko', 
#                 'English': 'en', 
#                 'Japanese': 'ja', 
#                 'Chinese': 'zh'
#                 }
            

#             lang_map = {
#             'Korean': 'ko', 'English': 'en', 'Japanese': 'ja', 'Chinese': 'zh'
#              }
#             detected_code = lang_map.get(detected_language, 'unknown')
#             if detected_code == 'unknown':
#                 return JsonResponse({'error': 'Unsupported language detected'}, status=400)

#             remaining_codes = [code for code in lang_map.values() if code != detected_code]



#             # Step 3: 번역 프롬프트 생성
#             translate_prompt = f"""
#             다음 가사를 {', '.join(remaining_codes)}로 완전히 번역해줘.

#             - 반드시 **모든 줄과 문장**을 번역할 것
#             - **줄 순서와 형식을 그대로 유지**할 것 (줄바꿈 포함)
#             - **절대 요약하지 마** (가사 전체를 빠짐없이 번역해야 함)
#             - 설명, 예시, 제목, 인삿말 모두 제거
#             - 출력은 반드시 JSON 형식이어야 하며, 다음과 같은 키만 사용할 것:{', '.join(remaining_codes)}
#             - 값은 해당 언어로 전체 가사를 줄 단위로 번역한 문자열이어야 함 (line breaks 포함)
#             - JSON 전체는 반드시 **중괄호 하나로 시작해서 하나로 끝나야 한다**. 여러 개의 JSON 블록으로 나누지 마.

#             아래는 번역할 가사입니다:

#             {original_lyrics}
#             """

#             translate_response = client.chat.completions.create(
#                 model="gpt-3.5-turbo",
#                 messages=[{"role": "user", "content": translate_prompt}],
#                 temperature=0.3
#             )

#             # 📌 추가할 부분
#             print("🔥 detect_response:", detect_response.choices[0].message.content)
#             print("🔥 translate_response:", translate_response.choices[0].message.content)

#             # ✅ JSON 문자열만 추출진섭추가가
#             import re
#             match = re.search(r'\{.*\}', translate_response.choices[0].message.content, re.DOTALL)
#             if not match:
#                 return JsonResponse({"error": "JSON 파싱 실패"}, status=500)

#             translations = json.loads(match.group())
#             #진섭추가끝

#             # 📌 여기 추가해
#             if isinstance(translations.get('en'), dict):
#                 translations['en'] = "\n".join(translations['en'].values())

#             if isinstance(translations.get('ja'), dict):
#                 translations['ja'] = "\n".join(translations['ja'].values())

#             if isinstance(translations.get('zh'), dict):
#                 translations['zh'] = "\n".join(translations['zh'].values())


#             response_data = {
#                 'detected': detected_code,
#                 'ko': translations.get('ko', ''),
#                 'en': translations.get('en', ''),
#                 'ja': translations.get('ja', ''),
#                 'zh': translations.get('zh', '')
#             }
#             return JsonResponse(response_data)

#         except Exception as e:
#             print(f"🔥 번역 에러 발생: {e}")
#             return JsonResponse({"error": "번역 실패", "detail": str(e)}, status=500)
        

#     return JsonResponse({'error': 'Only POST requests are allowed.'}, status=405)


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
        


# lyrics_info.html 처리 view 추가

def lyrics_info_view(request):
    artist = request.GET.get('artist', '').strip()
    title = request.GET.get('title', '').strip()
    video_id = request.GET.get('videoId')

    if not artist or not title or not video_id:
        return render(request, 'lyrics_info.html', {
            'error': 'Missing artist, title, or videoId'
        })

    is_favorite = False

    # # ✅ 로그인 한 경우에만 쿼리 실행
    # if request.user.is_authenticated:
    #     is_favorite = FavoriteSong.objects.annotate(
    #         title_lower=Lower('title'),
    #         artist_lower=Lower('artist')
    #     ).filter(
    #         user=request.user,
    #         title_lower=title.lower(),
    #         artist_lower=artist.lower()
    #     ).exists()

    return render(request, 'lyrics_info.html', {
        'artist': artist,
        'title': title,
        'video_id': video_id,
        'youtube_api_key': settings.YOUTUBE_API_KEY,
        'is_favorite': is_favorite,
    })


# 태그 자동 추출 함수 생성
def extract_tags_from_lyrics(lyrics):
    prompt = f"""
    아래는 노래 가사입니다. 이 가사를 바탕으로 일상생활과 관련된 주제 32가지를 추출해 주세요.
    결과는 배열 형태의 한국어 태그 3개로만 주세요. 예: ["운동", "영화","산책"]
    
    가사:
    {lyrics}
    결과:"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        result = response.choices[0].message.content.strip()
        tags = eval(result) if result.startswith("[") else []
        return tags[:3]
    except Exception as e:
        print("🔥 태그 추출 실패:", e)
        return []
    
#저장용 API 뷰 함수
@csrf_exempt
def save_tagged_song_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        title = data.get("title")
        artist = data.get("artist")
        lyrics = data.get("lyrics")

        if not (title and artist and lyrics):
            return JsonResponse({"error": "Missing fields"}, status=400)
        
        # ✅ 이미 저장된 곡인지 확인
        if TaggedSong.objects.filter(title=title, artist=artist).exists():
            return JsonResponse({"status": "skipped", "message": "이미 저장된 곡입니다."})

        tags = extract_tags_from_lyrics(lyrics)
        if tags:
            TaggedSong.objects.create(title=title, artist=artist, lyrics=lyrics, tags=tags)
            return JsonResponse({"status": "success", "tags": tags})
        else:
            return JsonResponse({"error": "No tags generated"}, status=500)
        

# @login_required
# @csrf_exempt
# def toggle_favorite(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         title = data.get('title')
#         artist = data.get('artist')
#         album_cover_url = data.get('albumCover', '')
#         video_id = data.get('videoId', '')  # ✅ 추가

#         favorite, created = FavoriteSong.objects.get_or_create(
#             user=request.user,
#             title=title,
#             artist=artist,
#             defaults={
#                 'album_cover_url': album_cover_url,
#                 'video_id': video_id  # ✅ 저장
#                 }
#         )
#         if not created:
#             favorite.delete()
#             return JsonResponse({'status': 'removed'})
#         return JsonResponse({'status': 'added'})
#     return JsonResponse({'error': 'Invalid request'}, status=400)