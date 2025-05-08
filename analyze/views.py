from django.shortcuts import render, redirect
from .utils import get_lyrics, analyze_lyrics_emotions, normalize_emotion_scores, get_standard_artist_name
from .models import UserSong, Song
from django.contrib.auth.decorators import login_required
import random

# 🎯 분석 입력 및 처리 뷰
# @login_required
def analyze_input_view(request):
    if request.method == "POST":
        # 📌 사용자 입력값 수집
        title_input = request.POST.get("title").strip()
        artist_input = request.POST.get("artist").strip()
        manual_lyrics = request.POST.get("manual_lyrics")
        country = request.POST.get("country", "global")

        # 📌 정규화 및 표준화
        title_clean = title_input.lower()
        standard_artist_raw = get_standard_artist_name(artist_input)
        standard_artist_clean = standard_artist_raw.lower()

        # 📌 가사 수집
        if manual_lyrics:
            lyrics = manual_lyrics.strip()
        else:
            lyrics = get_lyrics(title_clean, artist_input, country=country)
            if (
                "❌" in lyrics or
                len(lyrics) < 30 or
                "죄송" in lyrics or
                "찾을 수 없습니다" in lyrics
            ):
                return render(request, "manual_lyrics_input.html", {
                    "title": title_input,
                    "artist": artist_input,
                })

        # ✅ 감성 분석
        raw_result = analyze_lyrics_emotions(lyrics)
        if "error" in raw_result:
            return render(request, "analyze_result.html", {
                "title": title_input,
                "artist": artist_input,
                "lyrics": lyrics,
                "result": {},
                "top3": [],
                "top3_emotions": [],
                "warning": "감성 분석에 실패했습니다."
            })

        # ✅ 결과 정리
        result = normalize_emotion_scores(raw_result)
        sorted_result = sorted(result.items(), key=lambda x: x[1], reverse=True)
        top3 = sorted_result[:3]  # ✅ (감정, 점수) 튜플
        top3_emotions = [emotion for emotion, _ in top3]  # ✅ 감정 이름 리스트

        # ✅ DB 저장
        if not Song.objects.filter(title__iexact=title_clean, artist__iexact=standard_artist_clean).exists():
            Song.objects.create(
                title=title_clean,
                artist=standard_artist_raw,
                top2_emotions=top3_emotions[:2],
                top3_emotions=top3_emotions
            )

        if request.user.is_authenticated:
            if not UserSong.objects.filter(user=request.user, title__iexact=title_clean, artist__iexact=standard_artist_clean).exists():
                UserSong.objects.create(
                    user=request.user,
                    title=title_clean,
                    artist=standard_artist_raw,
                    top3_emotions=top3_emotions
                )

                
        # ✅ 분석 결과 렌더링
        return render(request, "analyze_result.html", {
            "title": title_input,
            "artist": artist_input,
            "lyrics": lyrics,
            "result": result,
            "top3": top3,  # ✅ 감정+점수 튜플
            "top3_emotions": top3_emotions,  # ✅ 감정 이름만 리스트 (추천 링크용)
            "warning": ""
        })

    return render(request, "analyze_input.html")


# 🎯 홈 접근 시 자동 분석 페이지로 리디렉션
def home_redirect(request):
    return redirect('analyze')


# 🎯 추천곡 필터링 뷰: 감정 태그 기준으로 추천
def recommend_by_emotion(request, tag):
    try:
        # 📌 가장 최근 분석한 곡을 제외 (중복 방지 목적)
        last_song = Song.objects.latest('created_at')
        all_songs = Song.objects.exclude(title=last_song.title, artist=last_song.artist)
    except Song.DoesNotExist:
        # 📌 데이터가 없을 경우 예외 처리
        all_songs = Song.objects.all()

    # ✅ 해당 감정을 포함하는 곡만 필터링
    filtered_songs = [
        song for song in all_songs
        if tag.strip() in [t.strip() for t in song.top2_emotions]
    ]

    # ✅ 최대 5곡만 무작위 샘플링
    filtered_songs = random.sample(filtered_songs, min(len(filtered_songs), 5))

    # ✅ 추천곡 페이지 렌더링
    return render(request, "recommendations.html", {
        "tag": tag,
        "songs": filtered_songs
    })
