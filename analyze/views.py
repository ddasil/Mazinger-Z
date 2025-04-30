# analyze/views.py
from django.shortcuts import render, redirect
from .utils import get_lyrics, analyze_lyrics_emotions, normalize_emotion_scores
# from .models import UserSong, Song  # DB 모델을 주석 처리하여 사용하지 않음
# from django.contrib.auth.decorators import login_required  

# 감성 분석 뷰 (입력 → 분석 → 결과 렌더링)
# @login_required  # 로그인한 사용자만 접근 가능하도록 설정
def analyze_input_view(request):
    if request.method == "POST":
        title = request.POST.get("title")  # 사용자 입력 제목
        artist = request.POST.get("artist")  # 사용자 입력 가수

        # 1. 가사 가져오기
        lyrics = get_lyrics(title, artist)  # get_lyrics 함수를 호출하여 가사 가져오기

        # 가사 가져오기 실패 처리
        if "❌" in lyrics or len(lyrics) < 30:  # 만약 가사가 30자 이하이거나 실패한 경우
            return render(request, "analyze_result.html", {  # 실패한 경우 결과를 출력합니다.
                "title": title,
                "lyrics": "가사를 가져올 수 없습니다.",
                "result": {},
                "top3": []
            })

        # 2. 감정 분석 수행
        raw_result = analyze_lyrics_emotions(lyrics)  # 감성 분석 함수 호출

        # 감성 분석 실패 시 처리
        if "error" in raw_result:  # 만약 감성 분석이 실패하면
            return render(request, "analyze_result.html", {  # 실패한 경우 결과를 출력합니다.
                "title": title,
                "lyrics": lyrics,
                "result": {},
                "top3": []
            })

        # 3. 감성 점수 정리 및 상위 3개 추출
        result = normalize_emotion_scores(raw_result)  # 감성 점수 퍼센트로 변환
        sorted_result = sorted(result.items(), key=lambda x: x[1], reverse=True)  # 점수 내림차순으로 정렬
        top3 = [emotion for emotion, _ in sorted_result[:3]]  # 상위 3개 감정 추출

        # DB에 Song 모델에 곡 저장
        # song = Song.objects.create(
        #     title=title,
        #     artist=artist,
        #     lyrics=lyrics,
        #     tags=top3  # 상위 3개 감성 태그 저장
        #     )

        # DB 저장을 주석 처리 (아래 코드 부분)
        # user_song = UserSong.objects.create(  # 사용자 입력 데이터를 DB에 저장
        #     user=request.user,  # 현재 로그인한 사용자
        #     title=title,
        #     artist=artist,
        #     lyrics=lyrics,
        #     top3_emotions=top3  # 감성 분석 결과 (상위 3개 감정)
        # )

        # 4. 결과 템플릿 렌더링
        return render(request, "analyze_result.html", {  # 분석 결과를 analyze_result.html에 렌더링
            "title": title,
            "lyrics": lyrics,
            "result": result,  # 감성 분석 결과
            "top3": sorted_result[:3]  # 상위 3개 감정
        })

    # GET 요청이면 입력창 렌더링
    return render(request, "analyze_input.html")



# 루트 접근 시 분석 입력 폼으로 리디렉션
def home_redirect(request):
    return redirect('analyze')  # 홈(루트) 경로가 분석 페이지로 리디렉션


# 감정 태그 기반 추천 뷰
def recommend_by_emotion(request, tag):

    # DB를 사용하지 않고, 더미 데이터를 사용하여 추천 (db를 사용하면 삭제 해야함함)-----------------
    dummy_songs = [
         # 기존 데이터 ...
        {"title": "봄날", "artist": "BTS", "emotion_tags": ["슬픔", "외로움"]},
        {"title": "Love Dive", "artist": "IVE", "emotion_tags": ["설렘", "기쁨"]},
        {"title": "시간을 거슬러", "artist": "린", "emotion_tags": ["그리움", "향수"]},
        {"title": "Blinding Lights", "artist": "The Weeknd", "emotion_tags": ["열정", "행복"]},
        
        # 팝송 5곡
        {"title": "Stay", "artist": "The Kid LAROI & Justin Bieber", "emotion_tags": ["사랑", "슬픔"]},
        {"title": "Shape of You", "artist": "Ed Sheeran", "emotion_tags": ["행복", "열정"]},
        {"title": "Levitating", "artist": "Dua Lipa", "emotion_tags": ["기쁨", "설렘"]},
        {"title": "Save Your Tears", "artist": "The Weeknd", "emotion_tags": ["슬픔", "외로움"]},
        {"title": "Good 4 U", "artist": "Olivia Rodrigo", "emotion_tags": ["분노", "슬픔"]},
        
        # 한국 유명 곡들 10곡 수정
        {"title": "눈, 코, 입", "artist": "태양", "emotion_tags": ["사랑", "그리움"]},
        {"title": "Dynamite", "artist": "BTS", "emotion_tags": ["기쁨", "행복"]},
        {"title": "가시", "artist": "버즈", "emotion_tags": ["슬픔", "외로움"]},
        {"title": "Bad Boy", "artist": "Red Velvet", "emotion_tags": ["열정", "사랑"]},
        {"title": "어떻게 이별까지 사랑하겠어, 널 사랑하는 거지", "artist": "AKMU", "emotion_tags": ["슬픔", "그리움"]},
        {"title": "봄, 여름, 가을, 겨울", "artist": "BIGBANG", "emotion_tags": ["그리움", "외로움"]},
        {"title": "아로하", "artist": "조정석", "emotion_tags": ["사랑", "기쁨"]},  # 정확한 아티스트로 수정
        {"title": "Cheer Up", "artist": "TWICE", "emotion_tags": ["기쁨", "설렘"]},
        {"title": "거짓말", "artist": "BIGBANG", "emotion_tags": ["슬픔", "분노"]},
        {"title": "Love Scenario", "artist": "iKON", "emotion_tags": ["슬픔", "그리움"]}
]
#-----------------------------------------여기까지 삭제


    # 감정이 포함된 곡만 필터링 (db를 사용하면 삭제해야함함)
    filtered_songs = [song for song in dummy_songs if tag in song["emotion_tags"]]

 # 감정 태그에 맞는 노래를 DB에서 찾기
    # filtered_songs = Song.objects.filter(top3_emotions__contains=[tag])  # 감정 태그가 포함된 노래 필터링
 
    return render(request, "recommendations.html", {
        "tag": tag,
        "songs": filtered_songs  # 추천 결과
    })
