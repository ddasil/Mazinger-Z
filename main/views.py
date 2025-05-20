from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
import random
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q, CharField
from django.db.models.functions import Cast
from chartsongs.models import ChartSong
# from analyze.models import Song
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .models import Lovelist
from .models import TagSearchLog
from collections import Counter
from django.utils.http import urlencode

def main(request):
    songs = list(ChartSong.objects.filter(
        lylics__isnull=False
    ).exclude(
        lylics=''
    ).exclude(
        lylics__exact='None'
    ))

    if not songs:
        return render(request, 'index.html', {'quiz_song': None})

    first_song = random.choice(songs)

    # ✅ 동건 추가, section2용 최신 앨범 커버 이미지 5개
    # top5 = ChartSong.objects.exclude(album_cover_url='').order_by('-id')[:5] # 상위 5개
    all_cover_songs = list(ChartSong.objects.exclude(album_cover_url='')) # 랜덤 5개
    random.shuffle(all_cover_songs) # 랜덤 5개
    top5 = all_cover_songs[:5] # 랜덤 5개
    cover_songs = top5

    return render(request, 'index.html', {
        'quiz_song': first_song,
        'cover_songs': top5,   # 👉 동건 추가, section2 용
    })

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

# 날씨 때문에 추가
# ✅ 위경도 → KMA 격자 좌표 변환 함수
def convert_to_grid(lat, lon):
    RE = 6371.00877  # 지구 반지름(km)
    GRID = 5.0       # 격자 간격(km)
    SLAT1 = 30.0     # 표준 위도1
    SLAT2 = 60.0     # 표준 위도2
    OLON = 126.0     # 기준점 경도
    OLAT = 38.0      # 기준점 위도
    XO = 43          # 기준점 X좌표
    YO = 136         # 기준점 Y좌표

    DEGRAD = math.pi / 180.0
    re = RE / GRID
    slat1 = SLAT1 * DEGRAD
    slat2 = SLAT2 * DEGRAD
    olon = OLON * DEGRAD
    olat = OLAT * DEGRAD

    sn = math.tan(math.pi * 0.25 + slat2 * 0.5) / math.tan(math.pi * 0.25 + slat1 * 0.5)
    sn = math.log(math.cos(slat1) / math.cos(slat2)) / math.log(sn)
    sf = math.tan(math.pi * 0.25 + slat1 * 0.5)
    sf = (sf ** sn * math.cos(slat1)) / sn
    ro = math.tan(math.pi * 0.25 + olat * 0.5)
    ro = re * sf / (ro ** sn)

    ra = math.tan(math.pi * 0.25 + lat * DEGRAD * 0.5)
    ra = re * sf / (ra ** sn)
    theta = lon * DEGRAD - olon
    if theta > math.pi: theta -= 2.0 * math.pi
    if theta < -math.pi: theta += 2.0 * math.pi
    theta *= sn

    x = int(ra * math.sin(theta) + XO + 0.5)
    y = int(ro - ra * math.cos(theta) + YO + 0.5)
    return {"nx": x, "ny": y}


@csrf_exempt
def get_weather_genre(request):
    sido = request.GET.get("sido")
    gugun = request.GET.get("gugun")

    if not sido or not gugun:
        return JsonResponse({"error": "지역 정보 누락"}, status=400)

    try:
        # ✅ Kakao 주소 검색 API로 위경도 얻기
        query = f"{sido} {gugun}"
        kakao_key = config("KAKAO_API_KEY")
        kakao_url = f"https://dapi.kakao.com/v2/local/search/address.json?query={query}"
        headers = {"Authorization": f"KakaoAK {kakao_key}"}
        kakao_response = requests.get(kakao_url, headers=headers)
        kakao_res = kakao_response.json()

        if "documents" not in kakao_res or not kakao_res["documents"]:
            return JsonResponse({"error": "좌표 변환 실패"}, status=404)

        lon = float(kakao_res["documents"][0]["x"])
        lat = float(kakao_res["documents"][0]["y"])

        # ✅ 위경도 → 격자 변환
        grid = convert_to_grid(lat, lon)
        nx, ny = grid["nx"], grid["ny"]

        # ✅ 기준 시각 계산 (초단기 실황: 10분 단위 → 가장 가까운 30분 전 시각 사용)
        now = datetime.now()
        minute = now.minute
        if minute < 45:
            now -= timedelta(hours=1)
        base_date = now.strftime("%Y%m%d")
        base_time = now.strftime("%H30")  # 초단기 실황 기준 시간

        # ✅ 기상청 초단기 실황 API 호출
        kma_key = config("KMA_SERVICE_KEY_ENCODED")
        kma_url = (
            f"http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst"
            f"?serviceKey={kma_key}&dataType=JSON&numOfRows=100&pageNo=1"
            f"&base_date={base_date}&base_time={base_time}&nx={nx}&ny={ny}"
        )

        res = requests.get(kma_url)
        print("KMA 요청 URL:", kma_url)
        print("KMA 응답 상태코드:", res.status_code)
        print("KMA 응답 본문:", res.text)

        data = res.json()

        try:
            items = data["response"]["body"]["items"]["item"]
        except Exception as e:
            return JsonResponse({
                "pty": "0",
                "note": "기상청 실황 데이터 없음",
                "kma_response": data
            }, status=200)

        # ✅ PTY 항목 추출 (실시간 관측값: obsrValue 사용)
        pty = next((item["obsrValue"] for item in items if item["category"] == "PTY"), "0")

        return JsonResponse({"pty": pty})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)




# ✅ 시/도에 따른 구/군 리스트 반환
def get_guguns(request):
    sido = request.GET.get("sido")
    if not sido:
        return JsonResponse({"guguns": []})
    
    gugun_map = {
        "서울특별시": ["강남구", "강동구", "강북구", "강서구", "관악구", "광진구", "구로구", "금천구", "노원구", "도봉구", "동대문구", "동작구", "마포구", "서대문구", "서초구", "성동구", "성북구", "송파구", "양천구", "영등포구", "용산구", "은평구", "종로구", "중구", "중랑구"],
        "부산광역시": ["강서구", "금정구", "기장군", "남구", "동구", "동래구", "부산진구", "북구", "사상구", "사하구", "서구", "수영구", "연제구", "영도구", "중구", "해운대구"],
        "대구광역시": ["남구", "달서구", "달성군", "동구", "북구", "서구", "수성구", "중구"],
        "인천광역시": ["강화군", "계양구", "남동구", "동구", "미추홀구", "부평구", "서구", "연수구", "옹진군", "중구"],
        "광주광역시": ["광산구", "남구", "동구", "북구", "서구"],
        "대전광역시": ["대덕구", "동구", "서구", "유성구", "중구"],
        "울산광역시": ["남구", "동구", "북구", "울주군", "중구"],
        "세종특별자치시": ["세종시"],
        "경기도": ["가평군", "고양시 덕양구", "고양시 일산동구", "고양시 일산서구", "과천시", "광명시", "광주시", "구리시", "군포시", "김포시", "남양주시", "동두천시", "부천시", "성남시 분당구", "성남시 수정구", "성남시 중원구", "수원시 권선구", "수원시 영통구", "수원시 장안구", "수원시 팔달구", "시흥시", "안산시 단원구", "안산시 상록구", "안성시", "안양시 동안구", "안양시 만안구", "양주시", "양평군", "여주시", "연천군", "오산시", "용인시 기흥구", "용인시 수지구", "용인시 처인구", "의왕시", "의정부시", "이천시", "파주시", "평택시", "포천시", "하남시", "화성시"],
        "강원특별자치도": ["강릉시", "고성군", "동해시", "삼척시", "속초시", "양구군", "양양군", "영월군", "원주시", "인제군", "정선군", "철원군", "춘천시", "태백시", "평창군", "홍천군", "화천군", "횡성군"],
        "충청북도": ["괴산군", "단양군", "보은군", "영동군", "옥천군", "음성군", "제천시", "증평군", "진천군", "청주시 상당구", "청주시 서원구", "청주시 청원구", "청주시 흥덕구", "충주시"],
        "충청남도": ["계룡시", "공주시", "금산군", "논산시", "당진시", "보령시", "부여군", "서산시", "서천군", "아산시", "예산군", "천안시 동남구", "천안시 서북구", "청양군", "태안군", "홍성군"],
        "전라북도": ["고창군", "군산시", "김제시", "남원시", "무주군", "부안군", "순창군", "완주군", "익산시", "임실군", "장수군", "전주시 덕진구", "전주시 완산구", "정읍시", "진안군"],
        "전라남도": ["강진군", "고흥군", "곡성군", "광양시", "구례군", "나주시", "담양군", "목포시", "무안군", "보성군", "순천시", "신안군", "여수시", "영광군", "영암군", "완도군", "장성군", "장흥군", "진도군", "함평군", "해남군", "화순군"],
        "경상북도": ["경산시", "경주시", "고령군", "구미시", "군위군", "김천시", "문경시", "봉화군", "상주시", "성주군", "안동시", "영덕군", "영양군", "영주시", "영천시", "예천군", "울릉군", "울진군", "의성군", "청도군", "청송군", "칠곡군", "포항시 남구", "포항시 북구"],
        "경상남도": ["거제시", "거창군", "고성군", "김해시", "남해군", "밀양시", "사천시", "산청군", "양산시", "의령군", "진주시", "창녕군", "창원시 마산합포구", "창원시 마산회원구", "창원시 성산구", "창원시 의창구", "창원시 진해구", "통영시", "하동군", "함안군", "함양군", "합천군"],
        "제주특별자치도": ["서귀포시", "제주시"]
    }

    guguns = gugun_map.get(sido, [])
    return JsonResponse({"guguns": guguns})

def quiz_song_view(request):
    songs = list(ChartSong.objects.filter(
        lylics__isnull=False
    ).exclude(
        lylics=''
    ).exclude(
        lylics__exact='None'
    ))

    if not songs:
        return render(request, 'quiz_song.html', {'quiz_song': None})

    quiz_song = random.choice(songs)
    return render(request, 'quiz_song.html', {'quiz_song': quiz_song})

def get_popular_tags(limit=5):
    tags = TagSearchLog.objects.values_list("tag", flat=True)
    counter = Counter(tags)
    return [tag for tag, _ in counter.most_common(limit)]

# 진섭이추가 
# 동건이수정
def search_results_view(request):
    query = request.GET.get('q', '').strip()
    page_number = request.GET.get('page')
    results = []

    # ✅ 인기 태그: 항상 노출
    popular_tags = get_popular_tags()

    if query:
        print(f"[🔍 DEBUG] query = '{query}'")

        # ✅ 태그 검색일 경우 로그 저장 (중복 새로고침 방지)
        if query.startswith('#'):
            last_tag = request.session.get('last_searched_tag')
            if last_tag != query:
                TagSearchLog.objects.create(tag=query)
                request.session['last_searched_tag'] = query
            else:
                print(f"[🚫 SKIP] '{query}'는 직전 태그와 동일하므로 저장 생략")
        else:
            # 일반 검색 시에는 태그 세션 초기화
            request.session['last_searched_tag'] = None

        matching_ids = set()

        # 👉 1. 해시태그 검색 (태그에 #포함된 값이 있어야 매치됨)
        if query.startswith('#'):
            for song in ChartSong.objects.only('id', 'emotion_tags', 'keywords'):
                if isinstance(song.emotion_tags, list):
                    if query in [tag.strip() for tag in song.emotion_tags]:
                        print(f"[🎯 TAG MATCH - EMOTION] {song.title}")
                        matching_ids.add(song.id)
                if isinstance(song.keywords, list):
                    if query in [tag.strip() for tag in song.keywords]:
                        print(f"[🎯 TAG MATCH - KEYWORD] {song.title}")
                        matching_ids.add(song.id)

        # 👉 2. 일반 검색 (제목, 가수, 가사)
        else:
            base_ids = ChartSong.objects.filter(
                Q(title__icontains=query) |
                Q(artist__icontains=query) |
                Q(lylics__icontains=query)
            ).values_list('id', flat=True)
            matching_ids.update(base_ids)

        # 👉 최종 결과 조회
        results_queryset = ChartSong.objects.filter(id__in=list(matching_ids)).distinct()
        paginator = Paginator(results_queryset, 10)
        results = paginator.get_page(page_number)

    return render(request, 'search_results.html', {
        'query': query,
        'results': results,
        'popular_tags': popular_tags,
    })




def results_music_info_view(request):
    title = request.GET.get('title')
    artist = request.GET.get('artist')
    song_obj = ChartSong.objects.filter(title=title, artist=artist).first()

    is_liked = False
    liked_songs = []
    like_count = Lovelist.objects.filter(title=title, artist=artist,is_liked=True).count()  # ✅ 이 줄 추가

    if song_obj:
        # 기본 정보
        genre = song_obj.normalized_genre
        release_date = getattr(song_obj, 'release_date', '')
        cover_url = getattr(song_obj, 'album_cover_url', '')
        lyrics = getattr(song_obj, 'lylics', '') 
        emotion_tags = song_obj.emotion_tags  # 동건 추가
        keywords = song_obj.keywords          # 동건 추가

        # 동건 추가
        # ✅ 문자열이면 json.loads() 처리
        if isinstance(emotion_tags, str):
            try:
                emotion_tags = json.loads(emotion_tags)
            except:
                emotion_tags = []

        # 동건 추가
        if isinstance(keywords, str):
            try:
                keywords = json.loads(keywords)
            except:
                keywords = []

        song_info = {
            'title': title,
            'artist': artist,
            'genre': genre,
            'release_date': release_date,
            'cover_url': cover_url,
            'lyrics': lyrics, # ✅ 가사도 전달
            'emotion_tags': emotion_tags,   # 동건 추가
            'keywords': keywords,           # 동건 추가
        }


        if request.user.is_authenticated:
            is_liked = Lovelist.objects.filter(user=request.user, title=title, artist=artist, is_liked=True ).exists()
            liked_songs = Lovelist.objects.filter(user=request.user, is_liked=True)

    else:
        song_info = {}

    return render(request, 'results_music_info.html', {
        'song': song_info,
        'is_liked': is_liked,
        'liked_songs': liked_songs,
        'like_count': like_count,  # ✅ 추가
        })

def check_auth(request):
    return JsonResponse({"is_authenticated": request.user.is_authenticated})

@csrf_exempt
@login_required
def add_or_remove_like(request):
    data = json.loads(request.body)
    title = data.get("title")
    artist = data.get("artist")
    cover_url = data.get("cover_url", "")

    obj, created = Lovelist.objects.get_or_create(
        user=request.user,
        title=title,
        artist=artist,
        defaults={'cover_url': cover_url, 'is_liked': True}
    )

    # ✅ 이미 존재하면 좋아요 상태 반전
    if not created:
        obj.is_liked = not obj.is_liked
        if not obj.cover_url and cover_url:
            obj.cover_url = cover_url
        obj.save()
        count = Lovelist.objects.filter(title=title, artist=artist, is_liked=True).count()
        return JsonResponse({
            "status": "removed" if not obj.is_liked else "added",
            "count": count
        })

    # ✅ 새로 생성된 경우
    count = Lovelist.objects.filter(title=title, artist=artist, is_liked=True).count()
    return JsonResponse({"status": "added", "count": count})

# 0520 동건 수정

# 좋아요 목록 비동기 최신화 (직접 새로고침 x)
@login_required
def liked_songs_html(request):
    liked_songs = Lovelist.objects.filter(user=request.user, is_liked=True)
    html = ""
    for song in liked_songs:
        query = urlencode({'title': song.title, 'artist': song.artist})
        html += f"""
        <li>
          <a href='/music-info/?{query}'>
            <strong>{song.title}</strong><br>
            <span class='artist-name'>{song.artist}</span>
          </a>
        </li>
        """
    if not liked_songs:
        html = "<li>좋아요한 곡이 없습니다.</li>"
    return HttpResponse(html)