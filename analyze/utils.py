import os
import json
import requests
from dotenv import load_dotenv
from openai import OpenAI
from bs4 import BeautifulSoup
import lyricsgenius

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
GENIUS_TOKEN = os.getenv("GENIUS_ACCESS_TOKEN")
genius = lyricsgenius.Genius(GENIUS_TOKEN, skip_non_songs=True, excluded_terms=["(Remix)", "(Live)"])

# GPT로 가사 생성 (백업용)
def generate_lyrics_by_title(song_title: str) -> str:
    prompt = f"""
    "{song_title}"라는 노래의 전체 가사를 최대한 정확하고 길게 작성해줘.
    가사는 반드시 줄바꿈(\n)을 포함해줘. 1절부터 끝까지 자세히.
    잘 모르는 부분은 자연스럽게 이어서 써줘.
    피처링, 앨범 정보, 가사, OST, MV 등은 무시하고 곡의 가사만 추출해줘.
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response.choices[0].message.content

# Genius API로 가사 가져오기
def search_lyrics_from_genius(artist: str, title: str) -> str:
    try:
        song = genius.search_song(title, artist)
        if not song or not song.url:
            return "❌ Genius에서 곡을 찾을 수 없습니다."

        # 🕸️ 가사 페이지 크롤링
        res = requests.get(song.url)
        soup = BeautifulSoup(res.text, 'html.parser')

        # 가사 페이지에서 가사를 포함하는 div를 찾아서 추출
        lyrics_divs = soup.find_all("div", attrs={"data-lyrics-container": "true"})

        # 가사 텍스트 추출
        raw_lyrics = "\n".join(div.get_text(separator="\n").strip() for div in lyrics_divs)

        # 디버깅: 원본 가사 출력 (필터링 전)
        print("Original lyrics:", raw_lyrics)

        # 불필요한 메타데이터나 설명을 필터링하는 함수
        def clean_lyrics(raw: str) -> str:
            # 추가로 제거해야 할 텍스트 필터링 (언어, 설명, 메타데이터 등)
            skip_keywords = [
                "Contributors", "Translations", "Romanization",  # 가사 외의 번역, 기여자 관련 부분
                "English", "Français", "Deutsch", "Español",  # 여러 언어 버전 관련 부분
                "Read More", "Song Info", "Artist", "You may also like", "Copyright",  # 사이트 내 다른 텍스트 관련 부분
                "Copyright", "About this song"  # 가사 외의 저작권 관련 텍스트
            ]
            
            # 가사에서 한 줄씩 처리하면서 불필요한 텍스트를 제거
            lines = raw.splitlines()
            filtered = [
                line.strip() for line in lines
                if line.strip() and not any(kw in line for kw in skip_keywords)
            ]
            
            return "\n".join(filtered).strip()

        # 필터링된 가사 반환
        cleaned_lyrics = clean_lyrics(raw_lyrics)

        # 디버깅: 필터링된 가사 출력
        print("Cleaned lyrics:", cleaned_lyrics)

        # 가사가 없으면 "가사를 찾을 수 없습니다." 메시지 반환
        return cleaned_lyrics or "❌ 가사를 찾을 수 없습니다."

    except Exception as e:
        # 에러 발생 시 로그 출력 및 오류 메시지 반환
        print(f"🔥 Genius API 오류 발생: {e}")
        return "❌ Genius 호출 실패"

# 통합 가사 가져오기 (Genius 먼저 → 실패하면 GPT 백업)
def get_lyrics(title: str, artist: str) -> str:
    lyrics = search_lyrics_from_genius(artist, title)
    if "❌" in lyrics or len(lyrics) < 30:
        print("⚠️ Genius에서 가사 못 찾음, GPT로 추정 시도")
        lyrics = generate_lyrics_by_title(title)
    return lyrics

# 감성 분석
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
