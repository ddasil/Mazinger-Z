# from django.core.management.base import BaseCommand
# from chartsongs.models import ChartSong
# import pandas as pd
# import os
# import glob
# import time
# import requests
# from datetime import date, datetime, timedelta
# from bs4 import BeautifulSoup
# import spotipy
# from spotipy.oauth2 import SpotifyClientCredentials
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager
# from decouple import config

# # ✅ API 설정
# # ✅ .env에서 민감 정보 불러오기
# SPOTIFY_CLIENT_ID = config('SPOTIFY_CLIENT_ID')
# SPOTIFY_CLIENT_SECRET = config('SPOTIFY_CLIENT_SECRET')
# LASTFM_API_KEY = config('LASTFM_API_KEY')
# USERNAME = config('SPOTIFY_USERNAME')
# PASSWORD = config('SPOTIFY_PASSWORD')

# sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
#     client_id=SPOTIFY_CLIENT_ID,
#     client_secret=SPOTIFY_CLIENT_SECRET
# ))

# GENRE_MAP = {
#     'k-pop': '댄스', 'k-rap': '랩/힙합', 'k-ballad': '발라드', 'k-rock': '록/메탈',
#     'soundtrack': 'OST', 'pop': '팝', 'art pop': '팝', 'r&b': '알앤비',
#     'synthpop': '팝', 'hip hop': '랩/힙합', 'my music discovery': '기타',
#     'indie': '인디', 'edm': '일렉트로닉', 'electronic': '일렉트로닉',
#     'house': '하우스', 'techno': '테크노', 'jazz': '재즈', 'blues': '블루스',
#     'folk': '포크', 'classical': '클래식', 'reggae': '레게'
# }

# def normalize_genre(genre):
#     if pd.isna(genre) or not genre:
#         return '기타'
#     genre_parts = [g.strip().lower() for g in genre.split(',')]
#     for g in genre_parts:
#         if g in GENRE_MAP:
#             return GENRE_MAP[g]
#     return genre

# genre_cache = {}

# def get_spotify_genre(title, artist):
#     try:
#         results = sp.search(q=f"{title} {artist}", type='track', limit=1)
#         track = results['tracks']['items'][0]
#         artist_id = track['artists'][0]['id']
#         artist_info = sp.artist(artist_id)
#         genres = artist_info.get('genres', [])
#         return ', '.join(genres) if genres else ''
#     except:
#         return ''

# def get_lastfm_genre(title, artist):
#     try:
#         params = {"method": "track.getTopTags", "artist": artist, "track": title,
#                   "api_key": LASTFM_API_KEY, "format": "json"}
#         res = requests.get("http://ws.audioscrobbler.com/2.0/", params=params)
#         tags = res.json().get('toptags', {}).get('tag', [])
#         if isinstance(tags, list) and tags:
#             return ', '.join([tag['name'] for tag in tags[:2]])
#     except:
#         pass
#     return ''

# def get_melon_genre(song_id):
#     try:
#         url = f"https://www.melon.com/song/detail.htm?songId={song_id}"
#         headers = {"User-Agent": "Mozilla/5.0"}
#         res = requests.get(url, headers=headers)
#         soup = BeautifulSoup(res.text, "html.parser")
#         for dt in soup.select("div.meta > dl > dt"):
#             if "장르" in dt.text:
#                 dd = dt.find_next_sibling("dd")
#                 return dd.text.strip() if dd else ''
#     except:
#         return ''

# def get_genie_genre(song_id):
#     try:
#         url = f"https://www.genie.co.kr/detail/songInfo?xgnm={song_id}"
#         headers = {"User-Agent": "Mozilla/5.0"}
#         res = requests.get(url, headers=headers)
#         soup = BeautifulSoup(res.text, "html.parser")
#         for dt in soup.select("div.info-zone dt"):
#             if "장르" in dt.text:
#                 dd = dt.find_next_sibling("dd")
#                 a_tag = dd.find("a") if dd else None
#                 return a_tag.text.strip() if a_tag else (dd.text.strip() if dd else '')
#     except:
#         return ''

# def get_genre_fallback(song_id, title, artist, platform):
#     key = (title.lower(), artist.lower())
#     if key in genre_cache:
#         return genre_cache[key]

#     genre = get_spotify_genre(title, artist) or get_lastfm_genre(title, artist)
#     if not genre and platform == 'melon':
#         genre = get_melon_genre(song_id)
#     elif not genre and platform == 'genie':
#         genre = get_genie_genre(song_id)

#     genre_cache[key] = genre or ''
#     time.sleep(0.1)
#     return genre or ''

# def fetch_melon_chart(limit=100):
#     url = "https://www.melon.com/chart/index.htm"
#     headers = {"User-Agent": "Mozilla/5.0"}
#     res = requests.get(url, headers=headers)
#     soup = BeautifulSoup(res.text, "html.parser")
#     chart = []
#     rows = soup.select("div.service_list_song table tbody tr")
#     for row in rows[:limit]:
#         title_tag = row.select_one("div.ellipsis.rank01 a")
#         artist_tag = row.select_one("div.ellipsis.rank02 a")
#         link_tag = row.select_one("a[href*='goSongDetail']")
#         if not title_tag or not artist_tag or not link_tag:
#             continue
#         song_id = link_tag.get("href", "").split("'")[1]
#         title = title_tag.text.strip()
#         artist = artist_tag.text.strip()
#         genre = get_genre_fallback(song_id, title, artist, platform='melon')
#         chart.append({'title': title, 'artist': artist, 'genre': genre})
#     return pd.DataFrame(chart)

# def fetch_genie_chart(limit=100):
#     headers = {"User-Agent": "Mozilla/5.0"}
#     chart = []
#     for page in range(1, 3):
#         url = f"https://www.genie.co.kr/chart/top200?pg={page}"
#         res = requests.get(url, headers=headers)
#         soup = BeautifulSoup(res.text, "html.parser")
#         rows = soup.select("table.list-wrap > tbody > tr")
#         for row in rows:
#             title_tag = row.select_one("a.title")
#             artist_tag = row.select_one("a.artist")
#             onclick = title_tag.get("onclick", "") if title_tag else ""
#             try:
#                 song_id = onclick.split("'")[1]
#             except:
#                 continue
#             if not title_tag or not artist_tag:
#                 continue
#             title = title_tag.text.strip().replace("TITLE", "").strip()
#             artist = artist_tag.text.strip()
#             genre = get_genre_fallback(song_id, title, artist, platform='genie')
#             chart.append({'title': title, 'artist': artist, 'genre': genre})
#             if len(chart) >= limit:
#                 break
#     return pd.DataFrame(chart)

# def fetch_spotify_csv():
#     today = datetime.now()
#     offset = (today.weekday() - 3) % 7
#     latest_thursday = today - timedelta(days=offset)
#     previous_thursday = latest_thursday - timedelta(weeks=1)
#     date_str = previous_thursday.strftime("%Y-%m-%d")
#     options = webdriver.ChromeOptions()
#     prefs = {"download.default_directory": os.getcwd()}
#     options.add_experimental_option("prefs", prefs)

#     driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
#     wait = WebDriverWait(driver, 20)

#     try:
#         driver.get("https://charts.spotify.com/charts/view/regional-global-weekly/latest")
#         wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@data-testid="charts-login"]'))).click()
#         wait.until(EC.url_contains("accounts.spotify.com"))
#         username_input = wait.until(EC.presence_of_element_located((By.ID, "login-username")))
#         username_input.send_keys(USERNAME)
#         wait.until(EC.element_to_be_clickable((By.ID, "login-button"))).click()
#         time.sleep(3)
#         try:
#             pw_login_button = wait.until(EC.element_to_be_clickable(
#                 (By.XPATH, '//button[contains(text(), "Log in with a password") or contains(text(), "비밀번호로 로그인하기")]')))
#             pw_login_button.click()
#         except:
#             pass
#         password_input = wait.until(EC.presence_of_element_located((By.ID, "login-password")))
#         password_input.send_keys(PASSWORD)
#         wait.until(EC.element_to_be_clickable((By.ID, "login-button"))).click()
#         time.sleep(5)

#         driver.get(f"https://charts.spotify.com/charts/view/regional-global-weekly/{date_str}")
#         download_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@aria-labelledby="csv_download"]')))
#         download_button.click()
#         print(f"✅ Downloaded Spotify CSV for {date_str}")
#         time.sleep(5)
#     finally:
#         driver.quit()

# def fetch_spotify_chart():
#     list_of_files = glob.glob('regional-global-weekly-*.csv')
#     if not list_of_files:
#         raise FileNotFoundError("❌ Spotify CSV 파일이 없습니다!")
#     latest_file = max(list_of_files, key=os.path.getmtime)
#     df = pd.read_csv(latest_file)
#     if 'track_name' in df.columns and 'artist_names' in df.columns:
#         df = df[['track_name', 'artist_names']].rename(columns={'track_name': 'title', 'artist_names': 'artist'})
#     elif 'Track Name' in df.columns and 'Artist' in df.columns:
#         df = df[['Track Name', 'Artist']].rename(columns={'Track Name': 'title', 'Artist': 'artist'})
#     else:
#         raise ValueError("❌ 예상 못한 Spotify CSV 컬럼명")
#     df['genre'] = df.apply(lambda row: get_genre_fallback('', row['title'], row['artist'], 'spotify'), axis=1)

#     # DB 저장 끝나면 CSV 삭제
#     os.remove(latest_file)
#     print(f"✅ CSV 파일 {latest_file} 삭제 완료!")
#     return df

# class Command(BaseCommand):
#     help = '멜론, 지니, 스포티파이 차트 DB 저장'

#     def handle(self, *args, **options):
#         fetch_spotify_csv()
#         melon_df = fetch_melon_chart()
#         genie_df = fetch_genie_chart()
#         spotify_df = fetch_spotify_chart()

#         for df in [melon_df, genie_df, spotify_df]:
#             df['normalized_genre'] = df['genre'].apply(normalize_genre)

#         combined_df = pd.concat([melon_df, genie_df, spotify_df], ignore_index=True)
#         dedup_df = combined_df.drop_duplicates(subset=['title', 'artist', 'normalized_genre'])

#         song_objs = [
#             ChartSong(title=row['title'], artist=row['artist'], normalized_genre=row['normalized_genre'])
#             for _, row in dedup_df.iterrows()
#         ]
#         ChartSong.objects.bulk_create(song_objs, ignore_conflicts=True)
#         self.stdout.write(self.style.SUCCESS(f'✅ {len(song_objs)}곡 DB에 저장 완료!'))





# from django.core.management.base import BaseCommand
# from chartsongs.models import ChartSong
# import pandas as pd
# import os
# import glob
# import time
# import requests
# import lyricsgenius
# from datetime import datetime, timedelta
# from bs4 import BeautifulSoup
# import spotipy
# from spotipy.oauth2 import SpotifyClientCredentials
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager
# from decouple import config
# import re

# # ✅ .env에서 민감 정보 불러오기
# SPOTIFY_CLIENT_ID = config('SPOTIFY_CLIENT_ID')
# SPOTIFY_CLIENT_SECRET = config('SPOTIFY_CLIENT_SECRET')
# LASTFM_API_KEY = config('LASTFM_API_KEY')
# GENIUS_API_KEY = config('GENIUS_ACCESS_TOKEN')
# USERNAME = config('SPOTIFY_USERNAME')
# PASSWORD = config('SPOTIFY_PASSWORD')

# sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
#     client_id=SPOTIFY_CLIENT_ID,
#     client_secret=SPOTIFY_CLIENT_SECRET
# ))

# genius = lyricsgenius.Genius(GENIUS_API_KEY, skip_non_songs=True, excluded_terms=["(Remix)", "(Live)"], remove_section_headers=True)

# GENRE_MAP = {
#     'k-pop': '댄스', 'k-rap': '랩/힙합', 'k-ballad': '발라드', 'k-rock': '록/메탈',
#     'soundtrack': 'OST', 'pop': '팝', 'art pop': '팝', 'r&b': '알앤비',
#     'synthpop': '팝', 'hip hop': '랩/힙합', 'my music discovery': '기타',
#     'indie': '인디', 'edm': '일렉트로닉', 'electronic': '일렉트로닉',
#     'house': '하우스', 'techno': '테크노', 'jazz': '재즈', 'blues': '블루스',
#     'folk': '포크', 'classical': '클래식', 'reggae': '레게'
# }

# def normalize_genre(genre):
#     if pd.isna(genre) or not genre:
#         return '기타'
#     genre_parts = [g.strip().lower() for g in genre.split(',')]
#     for g in genre_parts:
#         if g in GENRE_MAP:
#             return GENRE_MAP[g]
#     return genre

# def clean_lyrics(raw_lyrics):
#     """가사에서 메타데이터, Contributors, Translations, [] 구간, () 괄호 내용 제거"""
#     cleaned = re.sub(r'\d+\s+Contributors', '', raw_lyrics)
#     cleaned = re.sub(r'Translations[\s\S]*?Lyrics', '', cleaned, flags=re.MULTILINE)
#     cleaned = re.sub(r'\[.*?\]', '', cleaned)
#     cleaned = re.sub(r'\(.*?\)', '', cleaned)
#     cleaned = re.sub(r'^[^\n]*Lyrics', '', cleaned, flags=re.MULTILINE)
#     lines = [line.strip() for line in cleaned.split('\n') if line.strip()]
#     return '\n'.join(lines)

# def fetch_lyrics(artist, title):
#     try:
#         song = genius.search_song(title, artist)
#         if song and song.lyrics:
#             return clean_lyrics(song.lyrics)
#     except Exception as e:
#         print(f"❌ 가사 실패: {title} - {artist}, 이유: {e}")
#     return ''

# def fetch_melon_chart(limit=100):
#     url = "https://www.melon.com/chart/index.htm"
#     headers = {"User-Agent": "Mozilla/5.0"}
#     res = requests.get(url, headers=headers)
#     soup = BeautifulSoup(res.text, "html.parser")
#     chart = []
#     rows = soup.select("div.service_list_song table tbody tr")
#     for row in rows[:limit]:
#         title_tag = row.select_one("div.ellipsis.rank01 a")
#         artist_tag = row.select_one("div.ellipsis.rank02 a")
#         link_tag = row.select_one("a[href*='goSongDetail']")
#         if not title_tag or not artist_tag or not link_tag:
#             continue
#         song_id = link_tag.get("href", "").split("'")[1]
#         title = title_tag.text.strip()
#         artist = artist_tag.text.strip()
#         chart.append({'title': title, 'artist': artist, 'platform': 'melon'})
#     return pd.DataFrame(chart)

# def fetch_genie_chart(limit=100):
#     headers = {"User-Agent": "Mozilla/5.0"}
#     chart = []
#     for page in range(1, 3):
#         url = f"https://www.genie.co.kr/chart/top200?pg={page}"
#         res = requests.get(url, headers=headers)
#         soup = BeautifulSoup(res.text, "html.parser")
#         rows = soup.select("table.list-wrap > tbody > tr")
#         for row in rows:
#             title_tag = row.select_one("a.title")
#             artist_tag = row.select_one("a.artist")
#             if not title_tag or not artist_tag:
#                 continue
#             title = title_tag.text.strip().replace("TITLE", "").strip()
#             artist = artist_tag.text.strip()
#             chart.append({'title': title, 'artist': artist, 'platform': 'genie'})
#             if len(chart) >= limit:
#                 break
#     return pd.DataFrame(chart)

# def fetch_spotify_csv():
#     today = datetime.now()
#     offset = (today.weekday() - 3) % 7
#     latest_thursday = today - timedelta(days=offset)
#     date_str = (latest_thursday - timedelta(weeks=1)).strftime("%Y-%m-%d")
#     options = webdriver.ChromeOptions()
#     prefs = {"download.default_directory": os.getcwd()}
#     options.add_experimental_option("prefs", prefs)
#     driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
#     wait = WebDriverWait(driver, 20)
#     try:
#         driver.get("https://charts.spotify.com/charts/view/regional-global-weekly/latest")
#         wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@data-testid="charts-login"]'))).click()
#         wait.until(EC.url_contains("accounts.spotify.com"))
#         username_input = wait.until(EC.presence_of_element_located((By.ID, "login-username")))
#         username_input.send_keys(USERNAME)
#         wait.until(EC.element_to_be_clickable((By.ID, "login-button"))).click()
#         time.sleep(3)
#         try:
#             pw_login_button = wait.until(EC.element_to_be_clickable(
#                 (By.XPATH, '//button[contains(text(), "Log in with a password") or contains(text(), "비밀번호로 로그인하기")]')))
#             pw_login_button.click()
#         except:
#             pass
#         password_input = wait.until(EC.presence_of_element_located((By.ID, "login-password")))
#         password_input.send_keys(PASSWORD)
#         wait.until(EC.element_to_be_clickable((By.ID, "login-button"))).click()
#         time.sleep(5)
#         driver.get(f"https://charts.spotify.com/charts/view/regional-global-weekly/{date_str}")
#         download_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@aria-labelledby="csv_download"]')))
#         download_button.click()
#         print(f"✅ Downloaded Spotify CSV for {date_str}")
#         time.sleep(5)
#     finally:
#         driver.quit()

# def fetch_spotify_chart():
#     list_of_files = glob.glob('regional-global-weekly-*.csv')
#     if not list_of_files:
#         raise FileNotFoundError("❌ Spotify CSV 파일이 없습니다!")
#     latest_file = max(list_of_files, key=os.path.getmtime)
#     df = pd.read_csv(latest_file)
#     if 'track_name' in df.columns and 'artist_names' in df.columns:
#         df = df[['track_name', 'artist_names']].rename(columns={'track_name': 'title', 'artist_names': 'artist'})
#     elif 'Track Name' in df.columns and 'Artist' in df.columns:
#         df = df[['Track Name', 'Artist']].rename(columns={'Track Name': 'title', 'Artist': 'artist'})
#     else:
#         raise ValueError("❌ 예상 못한 Spotify CSV 컬럼명")
#     os.remove(latest_file)
#     return df

# class Command(BaseCommand):
#     help = '멜론, 지니, 스포티파이 차트 DB 저장 + 가사 업데이트'

#     def handle(self, *args, **options):
#         fetch_spotify_csv()
#         melon_df = fetch_melon_chart()
#         genie_df = fetch_genie_chart()
#         spotify_df = fetch_spotify_chart()
#         combined_df = pd.concat([melon_df, genie_df, spotify_df], ignore_index=True)
#         combined_df.drop_duplicates(subset=['title', 'artist'], inplace=True)
        
#         # ✅ 하위 20개만 처리
#         # combined_df = combined_df.tail(20)

#         for idx, row in combined_df.iterrows():
#             title, artist = row['title'], row['artist']
#             lyrics = fetch_lyrics(artist, title)
#             # normalized_genre = normalized_genre(genre)
#             normalized_genre = '기타'
#             ChartSong.objects.update_or_create(
#                 title=title,
#                 artist=artist,
#                 normalized_genre=normalized_genre,
#                 defaults={'lylics': lyrics}
#             )
#             print(f"✅ 업데이트 완료: {title} - {artist}")

#         self.stdout.write(self.style.SUCCESS('✅ 모든 곡 DB 저장 및 가사 업데이트 완료!'))


from django.core.management.base import BaseCommand
from chartsongs.models import ChartSong
import pandas as pd
import os, glob, time, requests, re
import lyricsgenius
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from decouple import config

# ✅ 환경변수
SPOTIFY_CLIENT_ID = config('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = config('SPOTIFY_CLIENT_SECRET')
LASTFM_API_KEY = config('LASTFM_API_KEY')
GENIUS_API_KEY = config('GENIUS_ACCESS_TOKEN')
USERNAME = config('SPOTIFY_USERNAME')
PASSWORD = config('SPOTIFY_PASSWORD')

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))
genius = lyricsgenius.Genius(GENIUS_API_KEY, skip_non_songs=True, excluded_terms=["(Remix)", "(Live)"], remove_section_headers=True)

GENRE_MAP = {
    'k-pop': '댄스', 'k-rap': '랩/힙합', 'k-ballad': '발라드', 'k-rock': '록/메탈',
    'soundtrack': 'OST', 'pop': '팝', 'r&b': '알앤비', 'hip hop': '랩/힙합',
    'indie': '인디', 'edm': '일렉트로닉', 'electronic': '일렉트로닉', 'house': '하우스',
    'techno': '테크노', 'jazz': '재즈', 'blues': '블루스', 'folk': '포크',
    'classical': '클래식', 'reggae': '레게'
}

genre_cache = {}

def normalize_genre(genre):
    if pd.isna(genre) or not genre:
        return '기타'
    genre_parts = [g.strip().lower() for g in genre.split(',')]
    for g in genre_parts:
        if g in GENRE_MAP:
            return GENRE_MAP[g]
    # 매핑 안 되는 경우 → 원래 영문 장르 그대로 반환 (기타로 덮어쓰지 않음)
    return genre

def get_spotify_genre(title, artist):
    try:
        res = sp.search(q=f"{title} {artist}", type='track', limit=1)
        track = res['tracks']['items'][0]
        artist_id = track['artists'][0]['id']
        artist_info = sp.artist(artist_id)
        return ', '.join(artist_info.get('genres', []))
    except:
        return ''

def get_lastfm_genre(title, artist):
    try:
        res = requests.get("http://ws.audioscrobbler.com/2.0/",
            params={"method": "track.getTopTags", "artist": artist, "track": title,
                    "api_key": LASTFM_API_KEY, "format": "json"})
        tags = res.json().get('toptags', {}).get('tag', [])
        return ', '.join([tag['name'] for tag in tags[:2]]) if tags else ''
    except:
        return ''

def get_melon_genre(song_id):
    try:
        res = requests.get(f"https://www.melon.com/song/detail.htm?songId={song_id}",
                           headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")
        for dt in soup.select("div.meta > dl > dt"):
            if "장르" in dt.text:
                dd = dt.find_next_sibling("dd")
                return dd.text.strip() if dd else ''
    except:
        return ''

def get_genie_genre(song_id):
    try:
        res = requests.get(f"https://www.genie.co.kr/detail/songInfo?xgnm={song_id}",
                           headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")
        for dt in soup.select("div.info-zone dt"):
            if "장르" in dt.text:
                dd = dt.find_next_sibling("dd")
                a_tag = dd.find("a") if dd else None
                return a_tag.text.strip() if a_tag else (dd.text.strip() if dd else '')
    except:
        return ''

def get_genre(song_id, title, artist, platform):
    key = (title.lower(), artist.lower())
    if key in genre_cache:
        return genre_cache[key]
    genre = get_spotify_genre(title, artist) or get_lastfm_genre(title, artist)
    if not genre and platform == 'melon':
        genre = get_melon_genre(song_id)
    elif not genre and platform == 'genie':
        genre = get_genie_genre(song_id)
    genre_cache[key] = genre or ''
    time.sleep(0.1)
    return genre or ''

def clean_lyrics(raw_lyrics):
    cleaned = re.sub(r'\d+\s+Contributors', '', raw_lyrics)
    cleaned = re.sub(r'Translations[\s\S]*?Lyrics', '', cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r'\[.*?\]|\(.*?\)', '', cleaned)
    cleaned = re.sub(r'^[^\n]*Lyrics', '', cleaned, flags=re.MULTILINE)
    return '\n'.join([line.strip() for line in cleaned.split('\n') if line.strip()])

def fetch_lyrics(artist, title):
    try:
        song = genius.search_song(title, artist)
        if song and song.lyrics:
            return clean_lyrics(song.lyrics)
    except:
        pass
    return ''

def fetch_melon_chart():
    res = requests.get("https://www.melon.com/chart/index.htm", headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(res.text, "html.parser")
    chart = []
    for row in soup.select("div.service_list_song table tbody tr"):
        title_tag = row.select_one("div.ellipsis.rank01 a")
        artist_tag = row.select_one("div.ellipsis.rank02 a")
        link_tag = row.select_one("a[href*='goSongDetail']")
        if title_tag and artist_tag and link_tag:
            song_id = link_tag.get("href", "").split("'")[1]
            chart.append({'title': title_tag.text.strip(), 'artist': artist_tag.text.strip(),
                          'song_id': song_id, 'platform': 'melon'})
    return pd.DataFrame(chart)

def fetch_genie_chart():
    chart = []
    for page in range(1, 3):
        res = requests.get(f"https://www.genie.co.kr/chart/top200?pg={page}",
                           headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")
        for row in soup.select("table.list-wrap > tbody > tr"):
            title_tag = row.select_one("a.title")
            artist_tag = row.select_one("a.artist")
            onclick = title_tag.get("onclick", "") if title_tag else ""
            try:
                song_id = onclick.split("'")[1]
            except:
                continue
            if title_tag and artist_tag:
                chart.append({'title': title_tag.text.strip().replace("TITLE", "").strip(),
                              'artist': artist_tag.text.strip(),
                              'song_id': song_id, 'platform': 'genie'})
    return pd.DataFrame(chart)

def fetch_spotify_csv():
    today = datetime.now()
    date_str = (today - timedelta(days=(today.weekday() - 3) % 7 + 7)).strftime("%Y-%m-%d")
    options = webdriver.ChromeOptions()
    prefs = {"download.default_directory": os.getcwd()}
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 20)
    try:
        driver.get("https://charts.spotify.com/charts/view/regional-global-weekly/latest")
        wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@data-testid="charts-login"]'))).click()
        wait.until(EC.url_contains("accounts.spotify.com"))
        wait.until(EC.presence_of_element_located((By.ID, "login-username"))).send_keys(USERNAME)
        wait.until(EC.element_to_be_clickable((By.ID, "login-button"))).click()
        time.sleep(3)
        try:
            wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//button[contains(text(), "Log in with a password")]'))).click()
        except:
            pass
        wait.until(EC.presence_of_element_located((By.ID, "login-password"))).send_keys(PASSWORD)
        wait.until(EC.element_to_be_clickable((By.ID, "login-button"))).click()
        time.sleep(5)
        driver.get(f"https://charts.spotify.com/charts/view/regional-global-weekly/{date_str}")
        wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@aria-labelledby="csv_download"]'))).click()
        time.sleep(5)
    finally:
        driver.quit()

def fetch_spotify_chart():
    files = glob.glob('regional-global-weekly-*.csv')
    if not files:
        raise FileNotFoundError("❌ Spotify CSV 파일이 없습니다!")
    latest_file = max(files, key=os.path.getmtime)
    df = pd.read_csv(latest_file)
    if 'track_name' in df.columns and 'artist_names' in df.columns:
        df = df[['track_name', 'artist_names']].rename(columns={'track_name': 'title', 'artist_names': 'artist'})
    elif 'Track Name' in df.columns and 'Artist' in df.columns:
        df = df[['Track Name', 'Artist']].rename(columns={'Track Name': 'title', 'Artist': 'artist'})
    os.remove(latest_file)
    return df

# class Command(BaseCommand):
#     help = '멜론, 지니, 스포티파이 차트 + 장르 + 가사 통합 저장'

#     def handle(self, *args, **options):
#         fetch_spotify_csv()
#         melon_df = fetch_melon_chart()
#         genie_df = fetch_genie_chart()
#         spotify_df = fetch_spotify_chart()
#         combined_df = pd.concat([melon_df, genie_df, spotify_df], ignore_index=True)
#         combined_df.drop_duplicates(subset=['title', 'artist'], inplace=True)
#         # combined_df = combined_df.tail(20)  # ✅ 주석 풀면 하위 20개만 실행

#         for _, row in combined_df.iterrows():
#             title, artist, song_id, platform = row.get('title'), row.get('artist'), row.get('song_id', ''), row.get('platform', 'spotify')
#             genre = get_genre(song_id, title, artist, platform)
#             normalized_genre = normalize_genre(genre)
#             obj, _ = ChartSong.objects.get_or_create(title=title, artist=artist, normalized_genre=normalized_genre)
#             if not obj.lylics:
#                 obj.lylics = fetch_lyrics(artist, title)
#                 obj.save()
#             print(f"✅ 저장 완료: {title} - {artist} ({normalized_genre})")

#         self.stdout.write(self.style.SUCCESS('✅ 모든 곡 DB 저장 및 가사/장르 업데이트 완료!'))





# ✅ 추가: 감정 분석 + 키워드 추출 + 저장 로직

from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_lyrics_emotions(lyrics: str) -> dict:
    prompt = f"""
    아래는 노래 가사입니다. 이 가사에 대해 다음 10가지 감정에 대해 0~1 점수로 분석해 주세요:
    감정: 사랑, 즐거움, 열정, 행복, 슬픔, 외로움, 그리움, 놀람, 분노, 두려움

    가사:
    {lyrics}

    감성 분석 결과를 JSON 형식으로 반환해주세요.
    예시: 
    {{
      "사랑": 0.8,
      "슬픔": 0.2,
      "행복": 0.4,
      "열정": 0.7
    }}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        print("🔥 감성 분석 오류:", e)
        return {"error": str(e)}

def extract_keywords_from_lyrics(lyrics):
    prompt = f"""
    아래는 노래 가사입니다. 이 가사에서 중요한 키워드 7개를 한국어로 추출해줘.
    - 출력 형식: ["단어1", "단어2", ..., "단어7"]
    - 설명 없이 JSON 배열만 출력해줘

    가사:
    {lyrics}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        result = response.choices[0].message.content.strip()
        return json.loads(result) if result.startswith("[") else []
    except Exception as e:
        print("❌ 키워드 추출 실패:", e)
        return []



class Command(BaseCommand):
    help = '멜론, 지니, 스포티파이 차트 + 장르 + 가사 통합 저장'

    def handle(self, *args, **options):
        fetch_spotify_csv()
        melon_df = fetch_melon_chart()
        genie_df = fetch_genie_chart()
        spotify_df = fetch_spotify_chart()
        combined_df = pd.concat([melon_df, genie_df, spotify_df], ignore_index=True)
        combined_df.drop_duplicates(subset=['title', 'artist'], inplace=True)
        # combined_df = combined_df.tail(20)  # ✅ 주석 풀면 하위 20개만 실행

        for _, row in combined_df.iterrows():
                    title, artist, song_id, platform = row.get('title'), row.get('artist'), row.get('song_id', ''), row.get('platform', 'spotify')
                    genre = get_genre(song_id, title, artist, platform)
                    normalized_genre = normalize_genre(genre)

                    if ChartSong.objects.filter(title=title, artist=artist, normalized_genre=normalized_genre).exists():
                        print(f"⚠️ 이미 존재: {title} - {artist} ({normalized_genre})")
                        continue

                    lyrics = fetch_lyrics(artist, title)
                    if not lyrics:
                        print(f"❌ 가사 없음: {title} - {artist}")
                        continue

                    # ✅ 감성 분석 실행 (GPT)
                    emotion_scores = analyze_lyrics_emotions(lyrics)
                    if "error" in emotion_scores:
                        continue
                    top3_emotions = sorted(emotion_scores.items(), key=lambda x: -x[1])[:3]
                    emotion_tags = [k for k, v in top3_emotions]

                    keywords = extract_keywords_from_lyrics(lyrics)

                    ChartSong.objects.create(
                        title=title,
                        artist=artist,
                        normalized_genre=normalized_genre,
                        lylics=lyrics,
                        emotion_tags=emotion_tags,
                        keywords=keywords
                    )
                    print(f"✅ 저장 및 분석 완료: {title} - {artist} ({normalized_genre})")