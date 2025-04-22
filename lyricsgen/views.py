from django.shortcuts import render
from openai import OpenAI
import os
from dotenv import load_dotenv

# .env에서 API 키 로드
load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# [추가] /lyrics/ 첫 진입 시 보여줄 기본 화면
def lyrics_home(request):
    return render(request, 'lyricsgen/lyrics.html')

# POST 요청 시 가사 생성
def generate_lyrics(request):
    if request.method == 'POST':
        prompt = request.POST.get('prompt')
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": f"Write song lyrics about: {prompt}"}
            ]
        )
        lyrics = response.choices[0].message.content.strip()
        return render(request, 'lyricsgen/lyrics.html', {
            'prompt': prompt,
            'lyrics': lyrics
        })
    return render(request, 'lyricsgen/lyrics.html')
