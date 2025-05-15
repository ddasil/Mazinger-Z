from django.shortcuts import render, redirect
from .utils import (
    get_lyrics,
    analyze_lyrics_emotions,
    extract_keywords_from_lyrics,
    get_genre,
    normalize_genre,
    get_release_date_from_genius_url,
    normalize_emotion_scores,
    clean_lyrics
)

from chartsongs.models import ChartSong
from lyricsgenius import Genius
from decouple import config
import random
from analyze.models import UserSong

# ✅ Genius API 클라이언트 초기화
genius = Genius(
    config("GENIUS_ACCESS_TOKEN"),
    skip_non_songs=True,
    remove_section_headers=True
)

    # ✅ 감성 분석 메인 뷰
    # - 사용자 입력 받은 제목/아티스트로 감정 분석 수행
    # - 기존 데이터가 있으면 보완 저장, 없으면 새로 저장함
    # - 로그인 사용자는 UserSong에도 저장됨
def analyze_input_view(request):
    if request.method == "POST":
        # 사용자가 입력한 제목, 아티스트명, 수동 가사 입력, 국가 정보 받기
        title_input = request.POST.get("title").strip()
        artist_input = request.POST.get("artist").strip()
        manual_lyrics = request.POST.get("manual_lyrics")
        country = request.POST.get("country", "global")

        try:
            # ✅ 이미 DB에 저장된 곡이면 불러오기 (중복 저장 방지)
            existing = ChartSong.objects.get(title=title_input, artist=artist_input)
            lyrics = existing.lylics  # 기존 가사 사용
            lyrics = clean_lyrics(lyrics)  # 전처리
            print("✅ DB에서 가사 불러옴")

            updated = False  # 변경 여부 체크

            # ✅ 감정 태그가 없으면 분석 후 저장
            if not existing.emotion_tags:
                emotion_scores = analyze_lyrics_emotions(lyrics)
                emotion_scores = normalize_emotion_scores(emotion_scores)
                emotion_tags = [k for k, v in sorted(emotion_scores.items(), key=lambda x: -x[1])[:3]]
                existing.emotion_tags = emotion_tags
                updated = True
            else:
                # 이미 있다면 분석은 다시 하지만 저장은 하지 않음
                emotion_scores = analyze_lyrics_emotions(lyrics)
                emotion_scores = normalize_emotion_scores(emotion_scores)
                emotion_tags = existing.emotion_tags

            # ✅ 키워드 없으면 새로 추출
            if not existing.keywords:
                keywords = extract_keywords_from_lyrics(lyrics)
                existing.keywords = keywords
                updated = True
            else:
                keywords = existing.keywords

            # ✅ 장르 정보 없을 경우 외부 플랫폼 통해 가져옴
            if not existing.normalized_genre:
                platform = request.POST.get("platform", "melon")
                song_id = ""
                genre = get_genre(song_id, title_input, artist_input, platform)
                normalized_genre = normalize_genre(genre)
                existing.normalized_genre = normalized_genre
                updated = True
                if not normalized_genre or normalized_genre == "기타":
                    print(f"⚠️ 장르 미확인: {title_input} - {artist_input} → {genre}")

            # ✅ 발매일 정보 없을 경우 Genius에서 크롤링
            if not existing.release_date:
                song = genius.search_song(title_input, artist_input)
                if song and song.url:
                    existing.release_date = get_release_date_from_genius_url(song.url)
                    # 앨범 커버, genius_id도 함께 저장
                    if not existing.album_cover_url:
                        existing.album_cover_url = song.song_art_image_url
                    if not existing.genius_id:
                        existing.genius_id = song.id
                    updated = True

            if updated:
                existing.save()  # 변경사항이 있으면 저장
                print(f"✅ 기존 곡 정보 보완 저장 완료: {title_input} - {artist_input}")

        except ChartSong.DoesNotExist:
            # ✅ DB에 없는 곡일 경우: 가사 수집/분석 후 새로 저장
            lyrics = manual_lyrics.strip() if manual_lyrics else get_lyrics(title_input, artist_input, country=country)
            lyrics = clean_lyrics(lyrics)

            # ❌ 오류 또는 너무 짧은 가사일 경우 수동 입력 페이지로
            if "❌" in lyrics or len(lyrics) < 30:
                return render(request, "manual_lyrics_input.html", {
                    "title": title_input,
                    "artist": artist_input,
                })

            # ✅ 감정 분석 및 키워드 추출
            emotion_scores = analyze_lyrics_emotions(lyrics)
            emotion_scores = normalize_emotion_scores(emotion_scores)
            emotion_tags = [k for k, v in sorted(emotion_scores.items(), key=lambda x: -x[1])[:3]]
            keywords = extract_keywords_from_lyrics(lyrics)

            # ✅ 장르 추출 및 정규화
            platform = request.POST.get("platform", "melon")
            song_id = ""
            genre = get_genre(song_id, title_input, artist_input, platform)
            normalized_genre = normalize_genre(genre)
            if not normalized_genre or normalized_genre == "기타":
                print(f"⚠️ 장르 미확인: {title_input} - {artist_input} → {genre}")

            # ✅ Genius에서 곡 정보 가져오기
            song = genius.search_song(title_input, artist_input)
            genius_id = song.id if song else None
            album_cover_url = song.song_art_image_url if song else None
            release_date = get_release_date_from_genius_url(song.url) if song and song.url else None

            # ✅ Genius ID 중복 체크 → 저장 방지
            if genius_id and ChartSong.objects.filter(genius_id=genius_id).exists():
                print(f"⚠️ 이미 저장된 곡입니다: genius_id={genius_id}")
            else:
                # ✅ 최종적으로 ChartSong에 저장
                ChartSong.objects.create(
                    title=title_input,
                    artist=artist_input,
                    normalized_genre=normalized_genre,
                    lylics=lyrics,
                    emotion_tags=emotion_tags,
                    keywords=keywords,
                    genius_id=genius_id,
                    album_cover_url=album_cover_url,
                    release_date=release_date
                )

                # ✅ 로그인 사용자의 경우 UserSong에도 저장
                if request.user.is_authenticated:
                    try:
                        # 중복 저장 방지
                        UserSong.objects.get(user=request.user, title=title_input, artist=artist_input)
                    except UserSong.DoesNotExist:
                        # 사용자별 감정 기록 저장
                        UserSong.objects.create(
                            user=request.user,
                            title=title_input,
                            artist=artist_input,
                            top3_emotions=emotion_tags
                        )

        # ✅ 상위 3개 감정을 추출하여 결과 페이지에 전달
        top3 = [(k, v) for k, v in sorted(emotion_scores.items(), key=lambda x: -x[1])[:3]]

        return render(request, "analyze_result.html", {
            "title": title_input,
            "artist": artist_input,
            "result": emotion_scores,
            "top3": top3,
            "keywords": keywords,
            "lyrics": lyrics
        })

    # GET 요청 시: 분석 입력 폼을 보여줌
    return render(request, "analyze_input.html")

# ✅ 홈 진입 시 분석 페이지로 리디렉션
def home_redirect(request):
    return redirect('analyze')

# ✅ 감정 태그 클릭 시 해당 감정을 가진 곡 추천해주는 뷰
def recommend_by_emotion(request, tag):
    try:
        # 최근 등록된 곡은 제외하고 추천
        last_song = ChartSong.objects.latest('id')
        all_songs = ChartSong.objects.exclude(title=last_song.title, artist=last_song.artist)
    except ChartSong.DoesNotExist:
        all_songs = ChartSong.objects.all()

    # 해당 감정 태그가 포함된 곡 필터링
    filtered_songs = [
        song for song in all_songs
        if tag.strip() in [t.strip() for t in song.emotion_tags or []]
    ]
    # 랜덤으로 최대 5개 추출
    filtered_songs = random.sample(filtered_songs, min(len(filtered_songs), 5)) 

    return render(request, "recommendations.html", {
        "tag": tag,
        "songs": filtered_songs
    })
