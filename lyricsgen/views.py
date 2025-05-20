from django.shortcuts import render, redirect
from openai import OpenAI
import os
import requests
import time
import uuid
from dotenv import load_dotenv
from django.core.files.base import ContentFile
from .models import GeneratedLyrics
from django.urls import reverse

# ✅ 환경 변수 로딩 및 OpenAI 클라이언트 생성
load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# ✅ 제목 추출 함수
def extract_title(lyrics_text):
    if "제목:" in lyrics_text:
        return lyrics_text.split("제목:")[1].split("가사:")[0].strip()
    return lyrics_text.splitlines()[0].strip() if lyrics_text else "제목 없음"

# ✅ 가사 보기 페이지 (GET)
def lyrics_home(request):
    open_id = request.GET.get('open_id')

    if request.user.is_authenticated:
        user_filter = {'user': request.user}
    else:
        temp_user_id = request.session.session_key
        user_filter = {'temp_user_id': temp_user_id} if temp_user_id else {}

    all_lyrics = GeneratedLyrics.objects.filter(**user_filter).order_by('-created_at')

    if open_id:
        try:
            selected_lyrics = GeneratedLyrics.objects.get(id=open_id)
        except GeneratedLyrics.DoesNotExist:
            selected_lyrics = all_lyrics.first()
    else:
        selected_lyrics = all_lyrics.first()

    return render(request, 'lyrics.html', {
        'all_lyrics': all_lyrics,
        'selected_lyrics': selected_lyrics,
        'prompt': selected_lyrics.prompt if selected_lyrics else '',
        'style': selected_lyrics.style if selected_lyrics else '',
        'lyrics': selected_lyrics.lyrics if selected_lyrics else '',
        'language': selected_lyrics.language if selected_lyrics else '',
        'elapsed_time': selected_lyrics.duration if selected_lyrics else '',
        'new_lyrics': selected_lyrics,
        'title': extract_title(selected_lyrics.lyrics) if selected_lyrics else '',
    })

# ✅ 가사 생성 요청 (POST)
def generate_lyrics(request):
    if request.method == 'POST':
        prompt = request.POST.get('prompt')
        style = request.POST.get('style')
        language = request.POST.get('language')

        # ✅ 임시 세션 생성
        if not request.session.session_key:
            request.session.create()
        temp_user_id = request.session.session_key

        start_time = time.time()

        lang_phrase = {
            'english': " in English",
            'korean': " in Korean",
            'japanese': " in Japanese",
            'chinese': " in Chinese",
            'thai': " in Thai"
        }.get(language, "")

        # ✅ GPT 호출
        try:
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
            print("🔥 GPT 응답 확인:", full_text)

            if "제목:" in full_text and "가사:" in full_text:
                title = full_text.split("제목:")[1].split("가사:")[0].strip()
                lyrics = full_text.split("가사:")[1].strip()
            else:
                lines = full_text.splitlines()
                title = lines[0].strip() if lines else f"{prompt}의 노래"
                lyrics = "\n".join(lines[1:]).strip() if len(lines) > 1 else full_text

        except Exception as e:
            print("❌ GPT 호출 실패:", e)
            title = f"{prompt}의 노래"
            lyrics = "가사 생성에 실패했습니다. 다시 시도해주세요."

        # ✅ 앨범 이미지 생성 (DALL-E)
        clean_prompt = prompt.replace("'", "").replace('"', '').strip()
        dalle_prompt = f"A {style} style album cover for a song about {clean_prompt}"
        image_filename = f"{uuid.uuid4()}.png"
        image_content = b''

        try:
            image_response = client.images.generate(
                model="dall-e-3",
                prompt=dalle_prompt[:1000],
                size="1024x1024",
                quality="standard",
                n=1
            )
            image_url = image_response.data[0].url
            image_content = requests.get(image_url).content
        except Exception as e:
            print("❌ 이미지 생성 실패:", e)

        elapsed_time = round(time.time() - start_time, 2)

        # ✅ 결과 DB 저장
        new_lyrics = GeneratedLyrics(
            prompt=prompt,
            style=style,
            lyrics=lyrics,
            duration=elapsed_time,
            language=language,
            user=request.user if request.user.is_authenticated else None,
            temp_user_id=None if request.user.is_authenticated else temp_user_id
        )
        new_lyrics.image_file.save(image_filename, ContentFile(image_content))
        new_lyrics.save()

        # ✅ 리다이렉트: 새로고침 시 재생성 방지
        return redirect(f"{reverse('lyrics_root')}?open_id={new_lyrics.id}")

    # GET 방식으로 접근 시 홈으로 이동
    return redirect('lyrics_home')

from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404

@require_POST
def edit_lyrics(request, pk):
    lyrics_obj = get_object_or_404(GeneratedLyrics, pk=pk)
    new_lyrics = request.POST.get('lyrics', '').strip()

    # 수정 권한 확인 (옵션)
    if request.user != lyrics_obj.user and not request.user.is_anonymous:
        return redirect('lyrics_root')

    lyrics_obj.lyrics = new_lyrics
    lyrics_obj.save()
    return redirect(f"{reverse('lyrics_root')}?open_id={pk}")

@require_POST
def delete_lyrics(request, pk):
    lyrics_obj = get_object_or_404(GeneratedLyrics, pk=pk)

    # 삭제 권한 확인 (옵션)
    if request.user != lyrics_obj.user and not request.user.is_anonymous:
        return redirect('lyrics_root')

    lyrics_obj.delete()
    return redirect('lyrics_root')
