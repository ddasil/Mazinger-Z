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

# ✅ Genius API 클라이언트 초기화
genius = Genius(
    config("GENIUS_ACCESS_TOKEN"),
    skip_non_songs=True,
    remove_section_headers=True
)

def analyze_input_view(request):
    if request.method == "POST":
        title_input = request.POST.get("title").strip()
        artist_input = request.POST.get("artist").strip()
        manual_lyrics = request.POST.get("manual_lyrics")
        country = request.POST.get("country", "global")

        try:
            existing = ChartSong.objects.get(title=title_input, artist=artist_input)
            lyrics = existing.lylics
            lyrics = clean_lyrics(lyrics)
            print("✅ DB에서 가사 불러옴")

            updated = False

            if not existing.emotion_tags:
                emotion_scores = analyze_lyrics_emotions(lyrics)
                emotion_scores = normalize_emotion_scores(emotion_scores)
                emotion_tags = [k for k, v in sorted(emotion_scores.items(), key=lambda x: -x[1])[:3]]
                existing.emotion_tags = emotion_tags
                updated = True
            else:
                emotion_scores = analyze_lyrics_emotions(lyrics)
                emotion_scores = normalize_emotion_scores(emotion_scores)
                emotion_tags = existing.emotion_tags

            if not existing.keywords:
                keywords = extract_keywords_from_lyrics(lyrics)
                existing.keywords = keywords
                updated = True
            else:
                keywords = existing.keywords

            if not existing.normalized_genre:
                platform = request.POST.get("platform", "melon")
                song_id = ""
                genre = get_genre(song_id, title_input, artist_input, platform)
                normalized_genre = normalize_genre(genre)
                existing.normalized_genre = normalized_genre
                updated = True
                if not normalized_genre or normalized_genre == "기타":
                    print(f"⚠️ 장르 미확인: {title_input} - {artist_input} → {genre}")

            if not existing.release_date:
                song = genius.search_song(title_input, artist_input)
                if song and song.url:
                    existing.release_date = get_release_date_from_genius_url(song.url)
                    if not existing.album_cover_url:
                        existing.album_cover_url = song.song_art_image_url
                    if not existing.genius_id:
                        existing.genius_id = song.id
                    updated = True

            if updated:
                existing.save()
                print(f"✅ 기존 곡 정보 보완 저장 완료: {title_input} - {artist_input}")

        except ChartSong.DoesNotExist:
            lyrics = manual_lyrics.strip() if manual_lyrics else get_lyrics(title_input, artist_input, country=country)
            lyrics = clean_lyrics(lyrics)

            if "❌" in lyrics or len(lyrics) < 30:
                return render(request, "manual_lyrics_input.html", {
                    "title": title_input,
                    "artist": artist_input,
                })

            emotion_scores = analyze_lyrics_emotions(lyrics)
            emotion_scores = normalize_emotion_scores(emotion_scores)
            emotion_tags = [k for k, v in sorted(emotion_scores.items(), key=lambda x: -x[1])[:3]]
            keywords = extract_keywords_from_lyrics(lyrics)

            platform = request.POST.get("platform", "melon")
            song_id = ""
            genre = get_genre(song_id, title_input, artist_input, platform)
            normalized_genre = normalize_genre(genre)
            if not normalized_genre or normalized_genre == "기타":
                print(f"⚠️ 장르 미확인: {title_input} - {artist_input} → {genre}")

            song = genius.search_song(title_input, artist_input)
            genius_id = song.id if song else None
            album_cover_url = song.song_art_image_url if song else None
            release_date = get_release_date_from_genius_url(song.url) if song and song.url else None

            if genius_id and ChartSong.objects.filter(genius_id=genius_id).exists():
                print(f"⚠️ 이미 저장된 곡입니다: genius_id={genius_id}")
            else:
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

        top3 = [(k, v) for k, v in sorted(emotion_scores.items(), key=lambda x: -x[1])[:3]]

        return render(request, "analyze_result.html", {
            "title": title_input,
            "artist": artist_input,
            "result": emotion_scores,
            "top3": top3,
            "keywords": keywords,
            "lyrics": lyrics
        })

    return render(request, "analyze_input.html")

def home_redirect(request):
    return redirect('analyze')

def recommend_by_emotion(request, tag):
    try:
        last_song = ChartSong.objects.latest('id')
        all_songs = ChartSong.objects.exclude(title=last_song.title, artist=last_song.artist)
    except ChartSong.DoesNotExist:
        all_songs = ChartSong.objects.all()

    filtered_songs = [
        song for song in all_songs
        if tag.strip() in [t.strip() for t in song.emotion_tags or []]
    ]

    filtered_songs = random.sample(filtered_songs, min(len(filtered_songs), 5))

    return render(request, "recommendations.html", {
        "tag": tag,
        "songs": filtered_songs
    })
