from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import os
import json
from openai import OpenAI
import requests
from bs4 import BeautifulSoup
import lyricsgenius

# ✅ API 키 세팅
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
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

            # 크롤링
            res = requests.get(song.url)
            soup = BeautifulSoup(res.text, 'html.parser')
            lyrics_divs = soup.find_all("div", attrs={"data-lyrics-container": "true"})
            lyrics = "\n".join(div.get_text(separator="\n").strip() for div in lyrics_divs)

            return JsonResponse({"lyrics": lyrics.strip() or "가사를 찾을 수 없습니다."})
        except Exception as e:
            print("🔥 get_lyrics 예외 발생:", e)
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({'error': 'Only POST requests are allowed.'}, status=405)
