from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

from django.http import JsonResponse
from django.db.models import Q
from chartsongs.models import ChartSong
# from analyze.models import Song

def main(request):
    return render(request, 'index.html')

def preference_view(request):
    return render(request, "preference.html") # 메인 음악 취향 검사

# ✅ 추천 장르로 관련 곡 5개 불러오기
def recommend_by_genre(request):
    genre = request.GET.get("genre", "").lower()

    GENRE_MAP = {
        "r&b": ["r&b", "rnb", "알앤비", "groovy", "pop soul", "soul"],
        "랩/힙합": ["랩/힙합", "rap", "rage rap", "pop rap", "latin hip hop", "southern hip hop"],
        "발라드": ["발라드", "love songs", "sad", "ballad"],
        "일렉트로닉": ["일렉트로닉", "electropop", "synthpop", "synthwave", "downtempo", "trip hop"],
        "록/메탈": ["rock", "록/메탈", "alt-pop", "alternative", "album rock", "metal", "grunge"],
        "팝": ["팝", "pop", "indie pop", "folk pop", "soft pop", "pop rock"],
        "인디": ["인디", "indie", "bedroom pop", "indie rock", "indie pop", "hindi indie"],
        "ost": ["ost", "soundtrack"],
        "k-pop, edm": ["k-pop", "kpop", "edm", "전자음악", "댄스", "club"],
    }

    match_genres = []
    for key, keywords in GENRE_MAP.items():
        if genre in keywords or key in genre:
            match_genres = keywords
            break

    if not match_genres:
        return JsonResponse({"songs": []})

    # ✅ 복합 장르 문자열에도 대응 (icontains 기반 검색)
    query = Q()
    for keyword in match_genres:
        query |= Q(normalized_genre__icontains=keyword)

    songs = (
        ChartSong.objects.filter(query)
        .order_by("?")
        .values("title", "artist", "normalized_genre")[:10]  # ✅ 최대 10개로 확장 가능
    )

    return JsonResponse({"songs": list(songs)})