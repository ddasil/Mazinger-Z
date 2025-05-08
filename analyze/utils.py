import os
import json
import requests
from dotenv import load_dotenv
from openai import OpenAI
from bs4 import BeautifulSoup
import lyricsgenius
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from transformers import pipeline

# 🔥 Hugging Face 감정 분석기 로드
emotion_classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", top_k=None)

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
GENIUS_TOKEN = os.getenv("GENIUS_ACCESS_TOKEN")
genius = lyricsgenius.Genius(GENIUS_TOKEN, skip_non_songs=True, excluded_terms=["(Remix)", "(Live)"])

SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET
))

# ✅ Lyrics.ovh API
def get_lyrics_from_lyrics_ovh(artist, title):
    url = f"https://api.lyrics.ovh/v1/{artist}/{title}"
    try:
        res = requests.get(url)
        if res.status_code == 200:
            data = res.json()
            lyrics = data.get('lyrics', '❌ 가사를 찾을 수 없습니다')
            return lyrics if lyrics.strip() else '❌ 가사를 찾을 수 없습니다'
        return '❌ 가사를 찾을 수 없습니다'
    except Exception as e:
        print(f"🔥 Lyrics.ovh API 오류 발생: {e}")
        return '❌ 가사를 찾을 수 없습니다'

# ✅ Melon (예제용)
def get_lyrics_from_melon(title, artist):
    try:
        url = 'https://www.melon.com/chart/index.htm'
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        return '❌ 멜론 크롤링은 아직 구현되지 않았습니다'
    except Exception as e:
        print(f"🔥 Melon 크롤링 오류 발생: {e}")
        return '❌ 멜론 크롤링 실패'

# ✅ J-Lyrics (예제용)
def get_lyrics_from_jlyrics(title, artist):
    try:
        search_url = f"http://search.j-lyric.net/index.php?kt={title}&ct={artist}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(search_url, headers=headers)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        return '❌ J-Lyrics 크롤링은 아직 구현되지 않았습니다'
    except Exception as e:
        print(f"🔥 J-Lyrics 크롤링 오류 발생: {e}")
        return '❌ J-Lyrics 크롤링 실패'

# ✅ GPT 백업 (주석처리)
# def generate_lyrics_by_title(song_title: str) -> str:
#     prompt = f"""
#     "{song_title}"라는 노래의 전체 가사를 검색해서 가사를 최대한 정확하고 길게 작성해줘.
#     가사는 반드시 줄바꿈(\n)을 포함해줘. 1절부터 끝까지 자세히.
#     모르는 부분이 있으면 더 찾아봐서 정확하게 작성해줘줘
#     피처링, 앨범 정보, 가사, OST, MV 등은 무시하고 곡의 가사만 추출해줘.
#     """
#     response = client.chat.completions.create(
#         model="gpt-3.5-turbo",
#         messages=[{"role": "user", "content": prompt}],
#         temperature=0.7,
#     )
#     return response.choices[0].message.content

# ✅ Genius API
def search_lyrics_from_genius(artist: str, title: str) -> str:
    try:
        song = genius.search_song(f"{title} {artist}", artist)
        if not song or not song.lyrics:
            song = genius.search_song(title, artist)
        if not song or not song.url:
            return "❌ Genius에서 곡을 찾을 수 없습니다."

        res = requests.get(song.url)
        soup = BeautifulSoup(res.text, 'html.parser')

        page_title = soup.find("title").get_text().lower()
        if 'english translation' in page_title:
            return "❌ 영어 번역 가사를 제외했습니다."

        lyrics_divs = soup.find_all("div", attrs={"data-lyrics-container": "true"})
        if not lyrics_divs:
            lyrics_divs = soup.find_all("div", class_="Lyrics__Container")
        if not lyrics_divs:
            return "❌ 가사를 찾을 수 없습니다."

        raw_lyrics = "\n".join(div.get_text(separator="\n").strip() for div in lyrics_divs)

        def clean_lyrics(raw: str) -> str:
            skip_keywords = [
                "Contributors", "Translations", "Romanization",
                "English", "Français", "Deutsch", "Español",
                "Read More", "Song Info", "Artist", "You may also like", "Copyright",
                "About this song"
            ]
            lines = raw.splitlines()
            filtered = [line.strip() for line in lines if line.strip() and not any(kw in line for kw in skip_keywords)]
            return "\n".join(filtered).strip()

        cleaned_lyrics = clean_lyrics(raw_lyrics)
        print("Cleaned lyrics:", cleaned_lyrics)
        return cleaned_lyrics or "❌ 가사를 찾을 수 없습니다."

    except Exception as e:
        print(f"🔥 Genius API 오류 발생: {e}")
        return "❌ Genius 호출 실패"

# ✅ 통합 가사 가져오기
def get_lyrics(title: str, artist: str, country='global') -> str:
    lyrics = search_lyrics_from_genius(artist, title)
    if "❌" not in lyrics and len(lyrics) >= 30:
        return lyrics

    print("⚠️ Genius 실패 → Lyrics.ovh 시도")
    lyrics = get_lyrics_from_lyrics_ovh(artist, title)
    if "❌" not in lyrics and len(lyrics) >= 30:
        return lyrics

    if country == 'kr':
        print("⚠️ Genius 실패 → Melon 시도")
        lyrics = get_lyrics_from_melon(title, artist)
        if "❌" not in lyrics and len(lyrics) >= 30:
            return lyrics

    if country == 'jp':
        print("⚠️ Genius 실패 → J-Lyrics 시도")
        lyrics = get_lyrics_from_jlyrics(title, artist)
        if "❌" not in lyrics and len(lyrics) >= 30:
            return lyrics

    # print("⚠️ 모든 소스 실패 → GPT 생성 시도")
    # lyrics = generate_lyrics_by_title(title)

    return '❌ 가사를 찾을 수 없습니다'


# ✅ 감성 분석
def analyze_lyrics_emotions(lyrics: str) -> dict:
    prompt = f"""
    아래는 노래 가사입니다. 이 가사에 대해 다음 10가지 감정에 대해 0~1 점수로 분석해 주세요:
    감정: 사랑, 즐거움, 열정, 행복, 슬픔, 외로움, 그리움, 놀람, 분노, 두려움

    가사:
    {lyrics}

    감성 분석 결과를 JSON 형식으로 반환해주세요.
    예시: 
    {{
      "사랑": 0.8,
      "슬픔": 0.2,
      "기쁨": 0.4,
      "열정": 0.7,
      ...
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

# 감정 점수를 %로 변환
def normalize_emotion_scores(raw_scores: dict) -> dict:
    if "error" in raw_scores:
        return raw_scores
    total = sum(raw_scores.values())
    if total == 0:
        return raw_scores
    return {k: round((v / total) * 100, 2) for k, v in raw_scores.items()}

# ✅ 표준 아티스트 이름 가져오기
def get_standard_artist_name(artist_name):
    try:
        url = f"https://musicbrainz.org/ws/2/artist/?query={artist_name}&fmt=json"
        headers = {'User-Agent': 'YourAppName/1.0 ( your@email.com )'}
        response = requests.get(url, headers=headers)
        data = response.json()

        if 'artists' not in data or not data['artists']:
            return artist_name

        artist = data['artists'][0]
        standard_name = artist.get('name', artist_name)

        if 'aliases' in artist:
            for alias in artist['aliases']:
                if alias.get('name', '').lower() == artist_name.lower():
                    return standard_name

        return standard_name

    except Exception as e:
        print(f"🔥 MusicBrainz API 오류 발생: {e}")
        return artist_name


