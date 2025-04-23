from django.shortcuts import render                      # HTML 템플릿을 출력하는 함수
from openai import OpenAI                                # OpenAI GPT 및 이미지 생성 클라이언트
import os                                                # 환경변수 접근용
import requests                                          # 이미지 다운로드용
import time                                              # 생성 시간 측정용
import uuid                                              # 고유 파일명 생성용
from dotenv import load_dotenv                           # .env 파일 불러오기
from django.core.files.base import ContentFile           # 이미지 저장에 사용
from .models import GeneratedLyrics                      # 생성된 결과를 저장할 모델

# .env에서 API 키 불러오기 + OpenAI 클라이언트 초기화
load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# /lyrics/ 메인 페이지 (입력 폼 + 최근 생성된 가사 목록)
def lyrics_home(request):
    all_lyrics = GeneratedLyrics.objects.order_by('-created_at')[:5]
    return render(request, 'lyrics.html', {
        'all_lyrics': all_lyrics
    })

# 1~6: 가사 생성 및 이미지 처리 뷰 (/lyrics/generate/)
def generate_lyrics(request):
    if request.method == 'POST':

        # 1. 사용자 입력 받기
        prompt = request.POST.get('prompt')  # 노래 주제
        style = request.POST.get('style')    # 선택한 노래 스타일
        start_time = time.time()             # 시작 시간 측정
        language = request.POST.get('language')  # 언어 선택값 받아오기

        # 언어에 따라 조건 붙이기
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

        # 2. GPT로 가사 생성 요청 (ChatCompletion API 사용)
        # GPT에게 제목과 가사 모두 요청
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

        # 응답 파싱: 제목과 가사 분리
        full_text = response.choices[0].message.content.strip()
        if "제목:" in full_text and "가사:" in full_text:
            title = full_text.split("제목:")[1].split("가사:")[0].strip()
            lyrics = full_text.split("가사:")[1].strip()
        else:
            title = f"{prompt}의 노래"
            lyrics = full_text

        # 3. DALL·E로 앨범 이미지 생성 (안정성 보강됨)
        clean_prompt = prompt.replace("'", "").replace('"', '').strip()
        clean_style = style.replace("'", "").replace('"', '').strip()

        # 길이 제한 (DALL·E는 최대 1000자)
        dalle_prompt = f"A {clean_style} style album cover for a song about {clean_prompt}"
        if len(dalle_prompt) > 1000:
            dalle_prompt = dalle_prompt[:1000]

        # 고유한 이미지 파일 이름
        image_filename = f"{uuid.uuid4()}.png"

        # 이미지 생성 요청 (예외 방어 포함)
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


        # 4. 생성에 걸린 시간 계산
        elapsed_time = round(time.time() - start_time, 2)

        # 5. DB에 생성 결과 저장 (GeneratedLyrics 모델 사용)
        new_lyrics = GeneratedLyrics(
            prompt=prompt,
            style=style,
            lyrics=lyrics,
            duration=elapsed_time,
            language=language
        )
        new_lyrics.image_file.save(image_filename, ContentFile(image_content))  # 이미지 파일 저장
        new_lyrics.save()

        # 6. 결과를 템플릿에 넘겨서 출력
        return render(request, 'lyrics.html', {
            'prompt': prompt,              # 입력 주제
            'style': style,                # 입력 스타일
            'lyrics': lyrics,              # 생성 가사
            'language': language,          # 언어 정보 넘겨줌
            'elapsed_time': elapsed_time,  # 생성 시간
            'new_lyrics': new_lyrics,       # 저장된 DB 객체 (이미지 URL 접근용)
            # 마지막에 템플릿으로 데이터 넘길 때 추가
            'all_lyrics': GeneratedLyrics.objects.order_by('-created_at')[:5],
            'title': title


        })

    # GET 요청이면 입력 폼만 보여줌
    return render(request, 'lyrics.html')