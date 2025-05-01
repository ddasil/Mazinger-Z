from django.shortcuts import render
from openai import OpenAI
from decouple import config
import requests
import re

client = OpenAI(api_key=config("OPENAI_API_KEY"))

def get_book_image(book_title): # 책 이미지 가져오기
    headers = {"Authorization": f"KakaoAK {config('KAKAO_API_KEY')}"}
    params = {"query": book_title, "sort": "accuracy"} # 정확도 향상
    url = "https://dapi.kakao.com/v3/search/book"
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    if data.get("documents"):
        for book in data["documents"]:
            if book.get("thumbnail") and book.get("width", 0) > 400 and book.get("height", 0) > 300: # 해상도 개선
                return book["thumbnail"]
        return data["documents"][0].get("thumbnail")
    return "/static/no_book.png" # 이미지 없을시 기본 이미지

def get_place_image(place_name): # 여행지 이미지 가져오기
    headers = {"Authorization": f"KakaoAK {config('KAKAO_API_KEY')}"}
    search_query = f"{place_name} 여행지"
    params = {"query": search_query, "sort": "accuracy"} # 정확도 향상
    url = "https://dapi.kakao.com/v2/search/image"
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    if data.get("documents"):
        for img in data["documents"]:
            if img.get("width", 0) > 400 and img.get("height", 0) > 300: # 해상도 개선
                return img.get("image_url")
    return "/static/no_travel.png" # 이미지 없을시 기본 이미지

def extract_lines(start_tag, lines):
    result = []
    collecting = False
    for line in lines:
        if start_tag in line:
            collecting = True
            continue
        if collecting and re.match(r"^\d+\.", line.strip()):
            result.append(line.strip())
        elif collecting and not line.strip():
            break
    return result

def search_song(request): # gpt 이용 검색
    if request.method == "GET":
        query = request.GET.get("q")
        count = int(request.GET.get("count", 3))

        if query:
            prompt = f"""
            노래 제목이 '{query}'야. 이 노래 분위기에 어울리는 
            1. 책 {count}권 (제목과 작가만),
            2. 여행지 {count}곳 (장소명만)

            번호를 붙여서 아래 형식으로 추천해줘:

            책 추천:
            1. '제목' - 작가
            2. ...

            여행지 추천:
            1. 장소명
            2. ...
            """

            response = client.chat.completions.create(
                # model="gpt-4",
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )

            gpt_result = response.choices[0].message.content
            lines = gpt_result.splitlines()

            book_lines = extract_lines("책 추천:", lines)[:count]
            travel_lines = extract_lines("여행지 추천:", lines)[:count]

            books = []
            for line in book_lines:
                match = re.match(r"\d+\.\s*['\"]?(.+?)['\"]?\s*-\s*(.+)", line)
                if match:
                    title, author = match.groups()
                    books.append({
                        "title": title.strip(),
                        "author": author.strip(),
                        "image": get_book_image(title)
                    })

            travels = []
            for line in travel_lines:
                match = re.match(r"\d+\.\s*(.+)", line)
                if match:
                    place = match.group(1).strip()
                    travels.append({
                        "place": place,
                        "image": get_place_image(place)
                    })


            return render(request, "results.html", {
                "song": query,
                "books": books,
                "travels": travels,
            })

    return render(request, "search.html")