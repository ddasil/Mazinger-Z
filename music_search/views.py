import os
import json
import requests
import lyricsgenius
from datetime import datetime
from dotenv import load_dotenv
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from openai import OpenAI
from .models import TaggedSong, FullLyrics
from chartsongs.models import ChartSong
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Spotify API 키 설정
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")

spotify_client = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET
))


load_dotenv()

LASTFM_API_KEY = os.getenv('LASTFM_API_KEY')
GENIUS_TOKEN = os.getenv("GENIUS_ACCESS_TOKEN")
genius = lyricsgenius.Genius(GENIUS_TOKEN, skip_non_songs=True, excluded_terms=["(Remix)", "(Live)"])
genius.timeout = 15

client = OpenAI(api_key=settings.OPENAI_API_KEY)

# 1. 메인 검색 페이지 렌더링
def search_view(request):
    return render(request, 'search.html', {
        'youtube_api_key': settings.YOUTUBE_API_KEY,
    })

# 2. 검색어 자동완성 기능
def autocomplete(request):
    query = request.GET.get('q', '')
    if not query:
        return JsonResponse({'suggestions': []})

    try:
        response = requests.get(
            'https://suggestqueries.google.com/complete/search',
            params={'client': 'firefox', 'ds': 'yt', 'q': query},
            timeout=5
        )
        result = response.json()
        suggestions = result[1] if len(result) > 1 else []
        return JsonResponse({'suggestions': suggestions})
    except:
        return JsonResponse({'suggestions': []})

# 3. GPT로 영상 제목에서 가수/곡명 추출
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
    return JsonResponse({'error': 'Only POST requests allowed.'}, status=405)

# 4. 가사 기반 상세 페이지 렌더링
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

# 5. Genius API + GPT로 다국어 가사 수집 및 저장
@csrf_exempt
def get_lyrics(request):
    if request.method == "POST":
        body = json.loads(request.body)
        artist = body.get("artist")
        title = body.get("title")

        if not artist or not title:
            return JsonResponse({"error": "Missing artist or title"}, status=400)

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

        song = genius.search_song(title, artist)
        if not song or not song.lyrics:
            return JsonResponse({"error": "No song found on Genius"}, status=404)

        cleaned_lyrics = clean_lyrics(song.lyrics)
        ko = translate_to("한국어", cleaned_lyrics)
        en = translate_to("영어", cleaned_lyrics)
        ja = translate_to("일본어", cleaned_lyrics)
        zh = translate_to("중국어", cleaned_lyrics)

        FullLyrics.objects.create(
            title=title, artist=artist, original=cleaned_lyrics,
            ko=ko, en=en, ja=ja, zh=zh
        )

        try:
            genius_id = song.id
            album_cover_url = song.song_art_image_url
            release_str = getattr(song, 'release_date', None)
            release_date = parse_release_date(release_str)

            if not ChartSong.objects.filter(genius_id=genius_id).exists():
                ChartSong.objects.create(
                    title=title,
                    artist=artist,
                    normalized_genre=get_combined_genre(title, artist),  # ✅ 필수 수정
                    lylics=cleaned_lyrics,
                    emotion_tags=extract_tags_from_lyrics(cleaned_lyrics),
                    keywords=extract_tags_from_lyrics(cleaned_lyrics),
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

        return JsonResponse({
            "lyrics": cleaned_lyrics,
            "ko_lyrics": ko,
            "en_lyrics": en,
            "ja_lyrics": ja,
            "zh_lyrics": zh,
        })
    return JsonResponse({'error': 'Only POST requests allowed'}, status=405)

# 보조 함수: 가사 정제
def clean_lyrics(raw):
    skip_keywords = ["Contributors", "Translations", "Romanization"]
    section_tags = ["[Chorus", "[Verse", "[Bridge"]
    lines = raw.splitlines()
    return "\n".join([
        line.strip() for line in lines
        if line.strip() and not any(kw in line for kw in skip_keywords)
        and not any(line.startswith(tag) for tag in section_tags)
    ])

# 보조 함수: 발매일 파싱
def parse_release_date(release_str):
    if release_str:
        for fmt in ("%Y-%m-%d", "%B %d, %Y"):
            try:
                return datetime.strptime(release_str, fmt).date()
            except:
                continue
    return None

def get_combined_genre(title, artist):
    lastfm_genre = get_lastfm_genre(title, artist)
    spotify_genre = get_spotify_genre(title, artist)

    combined_genres = [g for g in [spotify_genre, lastfm_genre] if g]
    return ', '.join(combined_genres[:2]) if combined_genres else "기타"

def get_spotify_genre(title, artist):
    try:
        results = spotify_client.search(q=f'track:{title} artist:{artist}', type='track', limit=1)
        tracks = results.get('tracks', {}).get('items', [])
        if not tracks:
            return ''
        
        artist_id = tracks[0]['artists'][0]['id']
        artist_info = spotify_client.artist(artist_id)
        genres = artist_info.get('genres', [])
        return ', '.join(genres[:2]) if genres else ''
    except Exception as e:
        print(f"Spotify genre fetch error: {e}")
        return ''

# Last.fm에서 장르 불러오기
def get_lastfm_genre(title, artist):
    try:
        res = requests.get("http://ws.audioscrobbler.com/2.0/", params={
            "method": "track.getTopTags",
            "artist": artist,
            "track": title,
            "api_key": LASTFM_API_KEY,
            "format": "json"
        })
        data = res.json()
        tags = data.get('toptags', {}).get('tag', [])
        valid_tags = [tag['name'] for tag in tags if tag['name'].lower() not in {'기타', 'other', 'unknown'}]
        return ', '.join(valid_tags[:2]) if valid_tags else ''
    except:
        return ''

# GPT 번역 보조
def translate_to(language, lyrics):
    prompt = f"{lyrics}\n\nTranslate to {language}:"
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except:
        return ""

# GPT 태그 추출
def extract_tags_from_lyrics(lyrics):
    prompt = f"""
    다음 노래 가사를 읽고, 가사의 주제 또는 분위기를 나타내는 한국어 태그 3개를 배열 형태로만 제공하세요. 
    반드시 아래 예시와 같은 형식으로 답하세요.
    예시: ["사랑", "이별", "슬픔"]

    가사:
    {lyrics}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        result = response.choices[0].message.content.strip()

        # 더 안정적인 JSON 파싱
        tags = json.loads(result)
        if isinstance(tags, list) and len(tags) == 3:
            return tags
        else:
            print(f"Invalid tags format: {result}")
            return []
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        return []
    except Exception as e:
        print(f"❌ GPT error: {e}")
        return []


# 태그와 곡 DB 저장
@csrf_exempt
def save_tagged_song_view(request):
    data = json.loads(request.body)
    title, artist, lyrics = data.get("title"), data.get("artist"), data.get("lyrics")
    if TaggedSong.objects.filter(title=title, artist=artist).exists():
        return JsonResponse({"status": "skipped"})
    TaggedSong.objects.create(title=title, artist=artist, lyrics=lyrics, tags=extract_tags_from_lyrics(lyrics))
    return JsonResponse({"status": "success"})
