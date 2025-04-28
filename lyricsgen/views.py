from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from openai import OpenAI
import os
import requests
import time
import uuid
from dotenv import load_dotenv
from django.core.files.base import ContentFile
from .models import GeneratedLyrics


# 환경 변수에서 OpenAI API 키 로딩
load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# 메인 페이지 뷰
def lyrics_home(request):
    if request.user.is_authenticated:
        all_lyrics = GeneratedLyrics.objects.filter(user=request.user).order_by('-created_at')[:5]
    else:
        all_lyrics = None
    return render(request, 'lyrics.html', {
        'all_lyrics': all_lyrics
    })


# 가사 생성 및 이미지 생성 뷰
@login_required
def generate_lyrics(request):
    if request.method == 'POST':
        prompt = request.POST.get('prompt')
        style = request.POST.get('style')
        language = request.POST.get('language')
        start_time = time.time()

        # 언어 조건 생성
        if language == 'english':
            lang_phrase = " in English"
        elif language == 'korean':
            lang_phrase = " in Korean"
        elif language == 'japanese':
            lang_phrase = " in Japanese"
        elif language == 'chinese':
            lang_phrase = " in Chinese"
        elif language == 'thai':
            lang_phrase = " in Thai"
        else:
            lang_phrase = ""

        # GPT 가사 생성 요청
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "user",
                "content": f"""Write a {style} style song {lang_phrase} about '{prompt}'.
Please provide the result in the format:

제목: [song title]
가사:
[lyrics here]
"""
            }]
        )

        full_text = response.choices[0].message.content.strip()
        if "제목:" in full_text and "가사:" in full_text:
            title = full_text.split("제목:")[1].split("가사:")[0].strip()
            lyrics = full_text.split("가사:")[1].strip()
        else:
            title = f"{prompt}의 노래"
            lyrics = full_text

        # 이미지 프롬프트 생성
        clean_prompt = prompt.replace("'", "").replace('"', '').strip()
        clean_style = style.replace("'", "").replace('"', '').strip()
        dalle_prompt = f"A {clean_style} style album cover for a song about {clean_prompt}"
        if len(dalle_prompt) > 1000:
            dalle_prompt = dalle_prompt[:1000]

        image_filename = f"{uuid.uuid4()}.png"

        try:
            image_response = client.images.generate(
                model="dall-e-3",
                prompt=dalle_prompt,
                size="1024x1024",
                quality="standard",
                n=1
            )
            image_url = image_response.data[0].url
            image_content = requests.get(image_url).content
        except Exception as e:
            print("❌ 이미지 생성 실패:", e)
            image_content = b''

        elapsed_time = round(time.time() - start_time, 2)

        # 생성된 데이터 DB 저장
        new_lyrics = GeneratedLyrics(
            prompt=prompt,
            style=style,
            lyrics=lyrics,
            duration=elapsed_time,
            language=language,
            user=request.user  # ✅ 로그인한 사용자 저장
        )
        new_lyrics.image_file.save(image_filename, ContentFile(image_content))
        new_lyrics.save()

        return render(request, 'lyrics.html', {
            'prompt': prompt,
            'style': style,
            'lyrics': lyrics,
            'language': language,
            'elapsed_time': elapsed_time,
            'new_lyrics': new_lyrics,
            'all_lyrics': GeneratedLyrics.objects.filter(user=request.user).order_by('-created_at')[:5],
            'title': title
        })

    return render(request, 'lyrics.html')
