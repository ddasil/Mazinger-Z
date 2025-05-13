window.onload = function () {
  const urlParams = new URLSearchParams(window.location.search);
  const artist = urlParams.get('artist');
  const title = urlParams.get('title');
  const videoId = urlParams.get('videoId');

  // ✅ 1. 유튜브 영상 iframe 먼저 보이게
  const youtubePlayer = document.getElementById('youtubePlayer');
  youtubePlayer.style.display = 'block';
  if (videoId && videoId !== 'no-video') {
    setTimeout(() => {
      youtubePlayer.src = `https://www.youtube.com/embed/${videoId}?autoplay=1`;
    }, 10); // 10ms 뒤에 iframe src 세팅 (렌더링 우선)
  } else {
    youtubePlayer.src = '';
    youtubePlayer.style.display = 'none';
  }

  // ✅ 2. 앨범 정보: 먼저 로딩 시도 (DOM 먼저 보여진 상태에서)
  if (artist && title) {
    setTimeout(() => {
      fetchTrackFromApple(`${artist} ${title}`);
    }, 20); // 미세한 delay로 우선 렌더링 유도
  }

  // ✅ 3. 가사 및 감성 분석: 늦게 시작해도 무관
  if (artist && title) {
    setTimeout(() => {
      fetchLyricsTranslateAndTag(artist, title);
    }, 500); // UX 상 느껴지지 않을 정도로 뒤에 실행
  }
};



async function fetchLyricsTranslateAndTag(artist, title) {
  const lyricsContent = document.getElementById('lyricsContent');
  lyricsContent.innerHTML = "🎤 가사 로딩 중...";

  try {
    const res = await fetch('/music/lyrics/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ artist, title })
    });
    const data = await res.json();
    if (!data.lyrics) {
      lyricsContent.innerHTML = "❌ 가사를 불러올 수 없습니다.";
      return;
    }

    const originalLyrics = data.lyrics.replace(/\n/g, '<br>');
    translatedLyrics.original = data.lyrics ? data.lyrics.replace(/(\r\n|\r|\n)/g, '<br>') : '';
    translatedLyrics.ko = data.ko_lyrics ? data.ko_lyrics.replace(/(\r\n|\r|\n)/g, '<br>') : '';
    translatedLyrics.en = data.en_lyrics ? data.en_lyrics.replace(/(\r\n|\r|\n)/g, '<br>') : '';
    translatedLyrics.ja = data.ja_lyrics ? data.ja_lyrics.replace(/(\r\n|\r|\n)/g, '<br>') : '';
    translatedLyrics.zh = data.zh_lyrics ? data.zh_lyrics.replace(/(\r\n|\r|\n)/g, '<br>') : '';

    //     // ✅ 이 줄 다음에 실제 저장 확인용 로그 추가!
    // console.log("✅ 저장된 영어:", translatedLyrics.en);
    // console.log("✅ 저장된 일본어:", translatedLyrics.ja);
    // console.log("✅ 저장된 중국어:", translatedLyrics.zh);
    console.log("🎯 응답 데이터 확인:", data);
    console.log("🇰🇷 ko:", data.ko_lyrics);
    console.log("🇺🇸 en:", data.en_lyrics);
    console.log("🇯🇵 ja:", data.ja_lyrics);
    console.log("🇨🇳 zh:", data.zh_lyrics);


    lyricsContent.innerHTML = translatedLyrics.original || "⚠️ 가사를 불러올 수 없습니다.";

    // 번역이 끝난 후에 다음 코드 추가
    await fetch('/music/save-tagged-song/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title,
        artist,
        lyrics: data.lyrics
      })
    })
    .then(res => res.json())
    .then(response => {
      if (response.status === 'success') {
        console.log("✅ 태그 저장 완료:", response.tags);
      } else {
        console.warn("⚠️ 태그 저장 실패:", response.error);
      }
    })
    .catch(err => console.error("🔥 저장 요청 실패:", err));

  } catch (err) {
    console.error("🔥 가사 요청 또는 번역 실패:", err);
    lyricsContent.innerHTML = "⚠️ 가사 로딩 중 오류 발생!";
  }
}

function fetchTrackFromApple(query) {
  const infoContent = document.getElementById('infoContent');
  const albumCover = document.getElementById('albumCover');
  infoContent.innerHTML = "🎵 Apple Music 정보 로딩 중...";

  fetch(`https://itunes.apple.com/search?term=${encodeURIComponent(query)}&entity=musicTrack&limit=1`)
    .then(res => res.json())
    .then(data => {
      if (data.results && data.results.length > 0) {
        const track = data.results[0];
        albumCover.src = track.artworkUrl100.replace('100x100', '600x600');
        infoContent.innerHTML = `
          <h3>노래 제목 : ${track.trackName}</h3>
          <p><strong>아티스트 :</strong> ${track.artistName}</p>
          <p><strong>앨범 :</strong> ${track.collectionName}</p>
          <p><strong>발매일 :</strong> ${new Date(track.releaseDate).toLocaleDateString()}</p>
          <p><strong>장르 :</strong> ${track.primaryGenreName}</p>
        `;
      } else {
        infoContent.innerHTML = "🎵 Apple Music에서 곡 정보를 찾을 수 없습니다.";
      }
    })
    .catch(err => {
      console.error("🔥 Apple Music 검색 실패:", err);
      infoContent.innerHTML = "⚠️ Apple Music 정보 로딩 실패!";
    });
}

const translatedLyrics = {
  original: "",
  ko: "",
  en: "",
  ja: "",
  zh: ""
};

function translateLyrics(lang) {
  const lyricsContent = document.getElementById('lyricsContent');
  const selectedLyrics = translatedLyrics[lang] || `⚠️ 해당 언어 가사가 없습니다.`;
  lyricsContent.innerHTML = `<p class="lyrics-content">${selectedLyrics}</p>`;
}

function redirectSearch() {
  const query = document.getElementById('searchInput').value;
  if (query) {
    window.location.href = `/music/?q=${encodeURIComponent(query)}`;
  }
}
