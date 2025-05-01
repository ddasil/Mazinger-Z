from django.core.management.base import BaseCommand
from chartsongs.models import ChartSong
import pandas as pd
import os
import glob
import time
import requests
from datetime import date, datetime, timedelta
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

# ✅ API 설정
# ✅ .env에서 민감 정보 불러오기
SPOTIFY_CLIENT_ID = config('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = config('SPOTIFY_CLIENT_SECRET')
LASTFM_API_KEY = config('LASTFM_API_KEY')
USERNAME = config('SPOTIFY_USERNAME')
PASSWORD = config('SPOTIFY_PASSWORD')

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))

GENRE_MAP = {
    'k-pop': '댄스', 'k-rap': '랩/힙합', 'k-ballad': '발라드', 'k-rock': '록/메탈',
    'soundtrack': 'OST', 'pop': '팝', 'art pop': '팝', 'r&b': '알앤비',
    'synthpop': '팝', 'hip hop': '랩/힙합', 'my music discovery': '기타',
    'indie': '인디', 'edm': '일렉트로닉', 'electronic': '일렉트로닉',
    'house': '하우스', 'techno': '테크노', 'jazz': '재즈', 'blues': '블루스',
    'folk': '포크', 'classical': '클래식', 'reggae': '레게'
}

def normalize_genre(genre):
    if pd.isna(genre) or not genre:
        return '기타'
    genre_parts = [g.strip().lower() for g in genre.split(',')]
    for g in genre_parts:
        if g in GENRE_MAP:
            return GENRE_MAP[g]
    return genre

genre_cache = {}

def get_spotify_genre(title, artist):
    try:
        results = sp.search(q=f"{title} {artist}", type='track', limit=1)
        track = results['tracks']['items'][0]
        artist_id = track['artists'][0]['id']
        artist_info = sp.artist(artist_id)
        genres = artist_info.get('genres', [])
        return ', '.join(genres) if genres else ''
    except:
        return ''

def get_lastfm_genre(title, artist):
    try:
        params = {"method": "track.getTopTags", "artist": artist, "track": title,
                  "api_key": LASTFM_API_KEY, "format": "json"}
        res = requests.get("http://ws.audioscrobbler.com/2.0/", params=params)
        tags = res.json().get('toptags', {}).get('tag', [])
        if isinstance(tags, list) and tags:
            return ', '.join([tag['name'] for tag in tags[:2]])
    except:
        pass
    return ''

def get_melon_genre(song_id):
    try:
        url = f"https://www.melon.com/song/detail.htm?songId={song_id}"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        for dt in soup.select("div.meta > dl > dt"):
            if "장르" in dt.text:
                dd = dt.find_next_sibling("dd")
                return dd.text.strip() if dd else ''
    except:
        return ''

def get_genie_genre(song_id):
    try:
        url = f"https://www.genie.co.kr/detail/songInfo?xgnm={song_id}"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        for dt in soup.select("div.info-zone dt"):
            if "장르" in dt.text:
                dd = dt.find_next_sibling("dd")
                a_tag = dd.find("a") if dd else None
                return a_tag.text.strip() if a_tag else (dd.text.strip() if dd else '')
    except:
        return ''

def get_genre_fallback(song_id, title, artist, platform):
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

def fetch_melon_chart(limit=100):
    url = "https://www.melon.com/chart/index.htm"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    chart = []
    rows = soup.select("div.service_list_song table tbody tr")
    for row in rows[:limit]:
        title_tag = row.select_one("div.ellipsis.rank01 a")
        artist_tag = row.select_one("div.ellipsis.rank02 a")
        link_tag = row.select_one("a[href*='goSongDetail']")
        if not title_tag or not artist_tag or not link_tag:
            continue
        song_id = link_tag.get("href", "").split("'")[1]
        title = title_tag.text.strip()
        artist = artist_tag.text.strip()
        genre = get_genre_fallback(song_id, title, artist, platform='melon')
        chart.append({'title': title, 'artist': artist, 'genre': genre})
    return pd.DataFrame(chart)

def fetch_genie_chart(limit=100):
    headers = {"User-Agent": "Mozilla/5.0"}
    chart = []
    for page in range(1, 3):
        url = f"https://www.genie.co.kr/chart/top200?pg={page}"
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        rows = soup.select("table.list-wrap > tbody > tr")
        for row in rows:
            title_tag = row.select_one("a.title")
            artist_tag = row.select_one("a.artist")
            onclick = title_tag.get("onclick", "") if title_tag else ""
            try:
                song_id = onclick.split("'")[1]
            except:
                continue
            if not title_tag or not artist_tag:
                continue
            title = title_tag.text.strip().replace("TITLE", "").strip()
            artist = artist_tag.text.strip()
            genre = get_genre_fallback(song_id, title, artist, platform='genie')
            chart.append({'title': title, 'artist': artist, 'genre': genre})
            if len(chart) >= limit:
                break
    return pd.DataFrame(chart)

def fetch_spotify_csv():
    today = datetime.now()
    offset = (today.weekday() - 3) % 7
    latest_thursday = today - timedelta(days=offset)
    previous_thursday = latest_thursday - timedelta(weeks=1)
    date_str = previous_thursday.strftime("%Y-%m-%d")
    options = webdriver.ChromeOptions()
    prefs = {"download.default_directory": os.getcwd()}
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 20)

    try:
        driver.get("https://charts.spotify.com/charts/view/regional-global-weekly/latest")
        wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@data-testid="charts-login"]'))).click()
        wait.until(EC.url_contains("accounts.spotify.com"))
        username_input = wait.until(EC.presence_of_element_located((By.ID, "login-username")))
        username_input.send_keys(USERNAME)
        wait.until(EC.element_to_be_clickable((By.ID, "login-button"))).click()
        time.sleep(3)
        try:
            pw_login_button = wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//button[contains(text(), "Log in with a password") or contains(text(), "비밀번호로 로그인하기")]')))
            pw_login_button.click()
        except:
            pass
        password_input = wait.until(EC.presence_of_element_located((By.ID, "login-password")))
        password_input.send_keys(PASSWORD)
        wait.until(EC.element_to_be_clickable((By.ID, "login-button"))).click()
        time.sleep(5)

        driver.get(f"https://charts.spotify.com/charts/view/regional-global-weekly/{date_str}")
        download_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@aria-labelledby="csv_download"]')))
        download_button.click()
        print(f"✅ Downloaded Spotify CSV for {date_str}")
        time.sleep(5)
    finally:
        driver.quit()

def fetch_spotify_chart():
    list_of_files = glob.glob('regional-global-weekly-*.csv')
    if not list_of_files:
        raise FileNotFoundError("❌ Spotify CSV 파일이 없습니다!")
    latest_file = max(list_of_files, key=os.path.getmtime)
    df = pd.read_csv(latest_file)
    if 'track_name' in df.columns and 'artist_names' in df.columns:
        df = df[['track_name', 'artist_names']].rename(columns={'track_name': 'title', 'artist_names': 'artist'})
    elif 'Track Name' in df.columns and 'Artist' in df.columns:
        df = df[['Track Name', 'Artist']].rename(columns={'Track Name': 'title', 'Artist': 'artist'})
    else:
        raise ValueError("❌ 예상 못한 Spotify CSV 컬럼명")
    df['genre'] = df.apply(lambda row: get_genre_fallback('', row['title'], row['artist'], 'spotify'), axis=1)

    # DB 저장 끝나면 CSV 삭제
    os.remove(latest_file)
    print(f"✅ CSV 파일 {latest_file} 삭제 완료!")
    return df

class Command(BaseCommand):
    help = '멜론, 지니, 스포티파이 차트 DB 저장'

    def handle(self, *args, **options):
        fetch_spotify_csv()
        melon_df = fetch_melon_chart()
        genie_df = fetch_genie_chart()
        spotify_df = fetch_spotify_chart()

        for df in [melon_df, genie_df, spotify_df]:
            df['normalized_genre'] = df['genre'].apply(normalize_genre)

        combined_df = pd.concat([melon_df, genie_df, spotify_df], ignore_index=True)
        dedup_df = combined_df.drop_duplicates(subset=['title', 'artist', 'normalized_genre'])

        song_objs = [
            ChartSong(title=row['title'], artist=row['artist'], normalized_genre=row['normalized_genre'])
            for _, row in dedup_df.iterrows()
        ]
        ChartSong.objects.bulk_create(song_objs, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS(f'✅ {len(song_objs)}곡 DB에 저장 완료!'))


