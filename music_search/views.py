# ✅ music_search/views.py 기능 순서도 (실제 작동 흐름 기반)

# 1. search_view
#    - 검색창 페이지 출력

# 2. autocomplete
#    - 검색어 자동완성 요청 처리 (검색창 입력 중 호출됨)

# 3. analyze_title
#    - 유튜브 영상 제목 → GPT를 통해 가수/곡명 분석 (검색 결과 클릭 시 실행)

# 4. lyrics_info_view
#    - 분석된 가수/곡명/영상 ID 기반으로 상세 페이지 렌더링 (검색 후 상세화면 진입 시)

# 5. get_lyrics
#    - Genius API + 크롤링으로 가사 추출, GPT로 다국어 번역 → DB 저장 (가사 자동 조회 시 호출됨)

# 8. translate_to (보조 함수)
#    - 가사 내용을 특정 언어로 GPT 번역 (get_lyrics 내부에서 사용)

# 9. extract_tags_from_lyrics
#    - 가사로부터 감정/상황 태그 추출 (save_tagged_song_view에서 사용)

# 10. save_tagged_song_view
#     - 추출된 태그 + 가사 + 제목/가수 정보 → TaggedSong DB 저장

from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from openai import OpenAI
from .models import TaggedSong
from .models import FullLyrics
from chartsongs.models import ChartSong
import os
import json
import requests
import lyricsgenius
from datetime import datetime

# ✅ API 키 세팅
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
client = OpenAI(api_key=settings.OPENAI_API_KEY)
GENIUS_TOKEN = os.getenv("GENIUS_ACCESS_TOKEN")
genius = lyricsgenius.Genius(GENIUS_TOKEN, skip_non_songs=True, excluded_terms=["(Remix)", "(Live)"])
genius.timeout = 15  # ✅ 추가

# ✅ 1. 메인 검색 페이지 렌더링
# YouTube API 키를 search.html 템플릿으로 전달
def search_view(request):
    return render(request, 'search.html', {
        'youtube_api_key': settings.YOUTUBE_API_KEY,
    })

# ✅ 2. 검색어 자동완성 기능
def autocomplete(request):
    query = request.GET.get('q', '')  # 검색어 파라미터 받기
    if not query:
        return JsonResponse({'suggestions': []})  # 빈 검색어일 경우 빈 리스트 반환

    try:
        # Google Suggest API 호출 (YouTube 검색어 추천)
        response = requests.get(
            'https://suggestqueries.google.com/complete/search',
            params={'client': 'firefox', 'ds': 'yt', 'q': query},  # ds=yt는 YouTube 데이터소스
            timeout=5
        )
        result = response.json()
        suggestions = result[1] if len(result) > 1 else []
        return JsonResponse({'suggestions': suggestions})  # 추천어 리스트 반환
    except Exception as e:
        return JsonResponse({'suggestions': []})  # 실패 시 빈 리스트 반환


# ✅ 3. GPT로 영상 제목에서 가수/곡명 추출
@csrf_exempt
def analyze_title(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        title = body.get('title', '')

        prompt = f"""
        다음 유튜브 영상 제목에서 가수와 곡명을 JSON 형식으로 추출해줘.
        - 형식: {{ "artist": ..., "title": ... }}
        - 피처링, 앨범 정보, 가사, OST, MV 등은 무시
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
            parsed = {"artist": None, "title": None, "error": str(e)}

        return JsonResponse(parsed)
    return JsonResponse({'error': 'Only POST requests are allowed.'}, status=405)

# ✅ 4. 가사 기반 상세 페이지 렌더링 (곡 선택 시)
def lyrics_info_view(request):
    artist = request.GET.get('artist', '').strip()
    title = request.GET.get('title', '').strip()
    video_id = request.GET.get('videoId')

    if not artist or not title or not video_id:
        return render(request, 'lyrics_info.html', {
            'error': 'Missing artist, title, or videoId'
        })

    return render(request, 'lyrics_info.html', {
        'artist': artist,
        'title': title,
        'video_id': video_id,
        'youtube_api_key': settings.YOUTUBE_API_KEY,
        'is_favorite': False,
    })

# ✅ 5. Genius API + GPT로 다국어 가사 수집 및 저장
@csrf_exempt
def get_lyrics(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            artist = body.get("artist")
            title = body.get("title")


            if not artist or not title:
                return JsonResponse({"error": "Missing artist or title"}, status=400)
            
             # ✅ 1. 기존에 DB에 저장된 가사가 있는지 확인 (캐시처럼 사용)
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
                pass # 없으면 새로 수집 진행

            song = genius.search_song(title, artist)
            if not song or not song.lyrics:
                return JsonResponse({"error": "No song found on Genius"}, status=404)
            
            # ✅ 3. 가사 정제 (쓸모없는 태그 제거)
            def clean_lyrics(raw):
                skip_keywords = ["Contributors", "Translations", "Romanization"]
                section_tags = ["[Chorus", "[Verse", "[Bridge"]
                lines = raw.splitlines()
                return "\n".join([
                    line.strip() for line in lines
                    if line.strip() and not any(kw in line for kw in skip_keywords) and not any(line.startswith(tag) for tag in section_tags)
                ])

            cleaned_lyrics = clean_lyrics(song.lyrics)
            # ✅ 4. GPT로 다국어 번역 요청
            ko = translate_to("한국어", cleaned_lyrics)
            en = translate_to("영어", cleaned_lyrics)
            ja = translate_to("일본어", cleaned_lyrics)
            zh = translate_to("중국어", cleaned_lyrics)

            # ✅ 5. DB 저장 (다음부터는 바로 불러올 수 있음)
            FullLyrics.objects.create(
                title=title, artist=artist, original=cleaned_lyrics,
                ko=ko, en=en, ja=ja, zh=zh
            )

            # ✅ ChartSong 저장 로직
            try:
                genius_id = song.id
                album_cover_url = song.song_art_image_url
                release_str = song.release_date
                release_date = None

                if release_str:
                    try:
                        release_date = datetime.strptime(release_str, "%Y-%m-%d").date()
                    except ValueError:
                        try:
                            release_date = datetime.strptime(release_str, "%B %d, %Y").date()
                        except ValueError:
                            print("⚠️ 날짜 파싱 실패:", release_str)

                if not ChartSong.objects.filter(genius_id=genius_id).exists():
                    emotion_tags = extract_tags_from_lyrics(cleaned_lyrics)
                    keywords = extract_tags_from_lyrics(cleaned_lyrics)

                    ChartSong.objects.create(
                        title=title,
                        artist=artist,
                        normalized_genre="기타",  # 현재는 고정값
                        lylics=cleaned_lyrics,
                        emotion_tags=emotion_tags,
                        keywords=keywords,
                        album_cover_url=album_cover_url,
                        release_date=release_date,
                        genius_id=genius_id
                    )
                    print(f"✅ ChartSong 저장 완료: {artist} - {title}")
                else:
                    print(f"ℹ️ 이미 존재함 (ChartSong): {artist} - {title}")

            except Exception as e:
                import traceback
                print("❌ ChartSong 저장 중 오류 발생")
                traceback.print_exc()


            # ✅ 6. 프론트엔드로 JSON 응답
            return JsonResponse({
                "lyrics": cleaned_lyrics,
                "ko_lyrics": ko,
                "en_lyrics": en,
                "ja_lyrics": ja,
                "zh_lyrics": zh,
            })
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({'error': 'Only POST requests allowed'}, status=405)


# ✅ 8. 번역 보조 함수
def translate_to(language_name, cleaned_lyrics):
    prompt = f"""
    다음 노래 가사를 {language_name}로 번역해줘. 줄 순서 유지, 요약 금지

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
        return ""

# ✅ 9. GPT 기반 감정/상황 태그 추출 함수
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
        return []

# ✅ 10. 태그와 함께 곡을 DB에 저장하는 API
@csrf_exempt
def save_tagged_song_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        title = data.get("title")
        artist = data.get("artist")
        lyrics = data.get("lyrics")

        if not (title and artist and lyrics):
            return JsonResponse({"error": "Missing fields"}, status=400)

        if TaggedSong.objects.filter(title=title, artist=artist).exists():
            return JsonResponse({"status": "skipped", "message": "이미 저장된 곡입니다."})

        tags = extract_tags_from_lyrics(lyrics)
        if tags:
            TaggedSong.objects.create(title=title, artist=artist, lyrics=lyrics, tags=tags)
            return JsonResponse({"status": "success", "tags": tags})
        else:
            return JsonResponse({"error": "No tags generated"}, status=500)
