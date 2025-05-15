import os
import json
import requests
from openai import OpenAI
from decouple import config
import requests
from bs4 import BeautifulSoup
import lyricsgenius
from decouple import config
import re, time
from datetime import datetime
import requests
from decouple import config
from urllib.parse import quote_plus
import pandas as pd
from decouple import config
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# ✅ 장르 캐시 딕셔너리 정의 (get_genre에서 사용됨)
genre_cache = {}

# ✅ OpenAI 클라이언트
GENIUS_TOKEN = config("GENIUS_ACCESS_TOKEN")
genius = lyricsgenius.Genius(GENIUS_TOKEN, skip_non_songs=True, remove_section_headers=True)
SPOTIFY_CLIENT_ID = config('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = config('SPOTIFY_CLIENT_SECRET')
LASTFM_API_KEY = config('LASTFM_API_KEY')
client = OpenAI(api_key=config("OPENAI_API_KEY"))

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=config("SPOTIFY_CLIENT_ID"),
    client_secret=config("SPOTIFY_CLIENT_SECRET")
))



# ✅ 감성 분석 (GPT 기반)
def analyze_lyrics_emotions(lyrics: str) -> dict:
    prompt = f"""
    아래는 노래 가사입니다. 이 가사에 대해 다음 10가지 감정에 대해 0~1 점수로 분석해 주세요:
    감정: 사랑, 즐거움, 열정, 행복, 슬픔, 외로움, 그리움, 놀람, 분노, 두려움

    가사:
    {lyrics}

    감성 분석 결과를 JSON 형식으로 반환해주세요.
    예시: {{
      "사랑": 0.8,
      "슬픔": 0.2,
      "행복": 0.4,
      "열정": 0.7
    }}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        print("🔥 감성 분석 오류:", e)
        return {"error": str(e)}

# ✅ 감성 점수 정규화 (합이 100%)
def normalize_emotion_scores(raw_scores: dict) -> dict:
    if "error" in raw_scores:
        return raw_scores
    total = sum(raw_scores.values())
    if total == 0:
        return raw_scores
    return {k: round((v / total) * 100, 2) for k, v in raw_scores.items()}

# ✅ 키워드 추출 (GPT 기반)
def extract_keywords_from_lyrics(lyrics):
    prompt = f"""
    아래는 노래 가사입니다. 이 가사에서 중요한 키워드 7개를 한국어로 추출해줘.
    - 출력 형식: ["단어1", "단어2", ..., "단어7"]
    - 설명 없이 JSON 배열만 출력해줘

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
        return json.loads(result) if result.startswith("[") else []
    except Exception as e:
        print("❌ 키워드 추출 실패:", e)
        return []




# ✅ LastFM 기반 장르 추출
def get_lastfm_genre(title, artist):
    try:
        res = requests.get("http://ws.audioscrobbler.com/2.0/",
            params={
                "method": "track.getTopTags",
                "artist": artist,
                "track": title,
                "api_key": config("LASTFM_API_KEY"),
                "format": "json"
            })
        tags = res.json().get('toptags', {}).get('tag', [])
        return ', '.join([tag['name'] for tag in tags[:2]]) if tags else ''
    except:
        return ''

# ✅ 장르 정규화 (영문 → 한글 통일)

GENRE_MAP = {
    'k-pop': '댄스', 'k-rap': '랩/힙합', 'k-ballad': '발라드', 'k-rock': '록/메탈',
    'soundtrack': 'OST', 'pop': '팝', 'r&b': '알앤비', 'hip hop': '랩/힙합',
    'indie': '인디', 'edm': '일렉트로닉', 'electronic': '일렉트로닉', 'house': '하우스',
    'techno': '테크노', 'jazz': '재즈', 'blues': '블루스', 'folk': '포크',
    'classical': '클래식', 'reggae': '레게'
}




def normalize_genre(genre):
    if pd.isna(genre) or not genre:
        return '기타'
    genre_parts = [g.strip().lower() for g in genre.split(',')]
    for g in genre_parts:
        if g in GENRE_MAP:
            return GENRE_MAP[g]
    # 매핑 안 되는 경우 → 원래 영문 장르 그대로 반환 (기타로 덮어쓰지 않음)
    return genre

def get_spotify_genre(title, artist):
    try:
        res = sp.search(q=f"{title} {artist}", type='track', limit=1)
        track = res['tracks']['items'][0]
        artist_id = track['artists'][0]['id']
        artist_info = sp.artist(artist_id)
        return ', '.join(artist_info.get('genres', []))
    except:
        return ''

def get_lastfm_genre(title, artist):
    try:
        res = requests.get("http://ws.audioscrobbler.com/2.0/",
            params={"method": "track.getTopTags", "artist": artist, "track": title,
                    "api_key": LASTFM_API_KEY, "format": "json"})
        tags = res.json().get('toptags', {}).get('tag', [])
        return ', '.join([tag['name'] for tag in tags[:2]]) if tags else ''
    except:
        return ''

def get_melon_genre(song_id):
    try:
        res = requests.get(f"https://www.melon.com/song/detail.htm?songId={song_id}",
                           headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")
        for dt in soup.select("div.meta > dl > dt"):
            if "장르" in dt.text:
                dd = dt.find_next_sibling("dd")
                return dd.text.strip() if dd else ''
    except:
        return ''

def get_genie_genre(song_id):
    try:
        # f-string으로 URL을 잘 생성하도록 수정
        res = requests.get(f"https://www.genie.co.kr/detail/songInfo?xgnm={song_id}",
                           headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")
        for dt in soup.select("div.info-zone dt"):
            if "장르" in dt.text:
                dd = dt.find_next_sibling("dd")
                a_tag = dd.find("a") if dd else None
                return a_tag.text.strip() if a_tag else (dd.text.strip() if dd else '')
    except Exception as e:
        print(f"❌ {e}")
        return ''

def get_genre(song_id, title, artist, platform):
    key = (title.lower(), artist.lower())
    if key in genre_cache:
        print("🟡 [cache hit]")
        return genre_cache[key]

    print(f"🔍 [get_genre] Trying to get genre for: {title} - {artist}")
    genre = ''

    if platform == 'melon':
        genre = get_melon_genre(song_id)
        print("melon →", genre)
    if not genre:
        genre = get_genie_genre(song_id)  # 여기에서 제대로 song_id가 전달되는지 확인
        print("genie →", genre)
    if not genre:
        genre = get_spotify_genre(title, artist)
        print("spotify →", genre)
    if not genre:
        genre = get_lastfm_genre(title, artist)
        print("lastfm →", genre)

    genre_cache[key] = genre or ''
    return genre or ''

def get_lyrics(title, artist, country="global"):
    try:
        song = genius.search_song(title, artist)
        if song and song.lyrics:
            return song.lyrics
        else:
            return "❌ 가사 없음"
    except Exception as e:
        print("❌ get_lyrics 실패:", e)
        return "❌ 가사 없음"
    
# 🎯 Genius 웹페이지에서 발매일 크롤링 (새 구조 대응)
def get_release_date_from_genius_url(song_url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(song_url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        spans = soup.find_all("span")
        for span in spans:
            text = span.get_text(strip=True)
            if any(month in text for month in [
                "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
            ]):
                if any(char.isdigit() for char in text):
                    try:
                        # ✅ 문자열 날짜를 datetime.date 객체로 변환
                        parsed = datetime.strptime(text, "%b. %d, %Y").date()
                        return parsed
                    except ValueError:
                        pass  # 구조는 맞지만 변환 안되면 넘어감

    except Exception as e:
        print("❌ 발매일 크롤링 실패:", e)

    return None

# ✅ 가사에서 불필요한 메타 정보 제거
def clean_lyrics(raw_lyrics: str) -> str:
    lines = raw_lyrics.strip().splitlines()

    # ✅ 1. 첫 줄이 설명문 (5단어 이상, [Verse] 아님)이면 제거
    if lines and len(lines[0].split()) >= 5 and not re.match(r"\[.*\]", lines[0]):
        lines = lines[1:]

    # ✅ 2. contributor, read more, translator 정보 제거
    lines = [line for line in lines if not re.search(r'(contributor|translator|read more)', line.lower())]

    # ✅ 3. 너무 많은 줄바꿈 정리
    lyrics = '\n'.join(lines)
    lyrics = re.sub(r'\n{3,}', '\n\n', lyrics)

    return lyrics.strip()

