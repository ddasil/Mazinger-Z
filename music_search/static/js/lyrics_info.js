window.onload = async function () {
  const urlParams = new URLSearchParams(window.location.search);
  const artist = urlParams.get('artist');
  const title = urlParams.get('title');
  const videoId = urlParams.get('videoId');

  if (artist && title) {
    await fetchLyrics(artist, title);
    fetchTrackFromApple(`${artist} ${title}`);
  }

  const youtubePlayer = document.getElementById('youtubePlayer');
  if (videoId && videoId !== 'no-video') {
    youtubePlayer.src = `https://www.youtube.com/embed/${videoId}?autoplay=1`;
    youtubePlayer.style.display = 'block';
  } else {
    youtubePlayer.src = '';
    youtubePlayer.style.display = 'none';
  }
};

async function fetchLyrics(artist, title) {
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
    translatedLyrics.detected = `<p class="lyrics-content">${originalLyrics}</p>`;

    const translationRes = await fetch('/music/translate-lyrics/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ lyrics: data.lyrics })
    });
    const translations = await translationRes.json();

    // 🔍 여기에 로그 추가!
    console.log("🔍 번역 응답:", translations);
    console.log("✅ 저장된 영어:", translatedLyrics.en);

    translatedLyrics.ko = Array.isArray(translations.ko) ? translations.ko.join('<br>') : (translations.ko || originalLyrics);
    translatedLyrics.en = Array.isArray(translations.en) ? translations.en.join('<br>') : (translations.en || '');
    translatedLyrics.ja = Array.isArray(translations.ja) ? translations.ja.join('<br>') : (translations.ja || '');
    translatedLyrics.zh = Array.isArray(translations.zh) ? translations.zh.join('<br>') : (translations.zh || '');


    // ✅ 이 줄 다음에 실제 저장 확인용 로그 추가!
    console.log("✅ 저장된 영어:", translatedLyrics.en);
    console.log("✅ 저장된 일본어:", translatedLyrics.ja);
    console.log("✅ 저장된 중국어:", translatedLyrics.zh);


    lyricsContent.innerHTML = translatedLyrics[translations.detected] || translatedLyrics.detected;

    document.getElementById("loadingOverlay").style.display = "none";  // ✅ 로딩 종료

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
    document.getElementById("loadingOverlay").style.display = "none";  // ✅ 실패 시도 닫기
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

const translatedLyrics = { ko: "", en: "", ja: "", zh: "", detected: "" };

function translateLyrics(lang) {
  const lyricsContent = document.getElementById('lyricsContent');
  if (translatedLyrics[lang] && translatedLyrics[lang].length > 0) {
    lyricsContent.innerHTML = `<p class="lyrics-content">${translatedLyrics[lang]}</p>`;  // ✅ <p> 생략
  } else {
    lyricsContent.innerHTML = "⚠️ 번역본이 없습니다.";
  }
}

function redirectSearch() {
  const query = document.getElementById('searchInput').value;
  if (query) {
    window.location.href = `/music/?q=${encodeURIComponent(query)}`;
  }
}


document.addEventListener('DOMContentLoaded', function () {
  const micBtn = document.getElementById('micBtn');
  const stopBtn = document.getElementById('stopBtn');
  const searchInput = document.getElementById('searchInput');
  let recognition = null;
  let isManuallyStopped = false;

  if (!micBtn || !stopBtn || !searchInput) return;

  micBtn.addEventListener('click', () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("이 브라우저는 음성 인식을 지원하지 않습니다.");
      return;
    }

    recognition = new SpeechRecognition();
    recognition.lang = 'ko-KR';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.start();
    micBtn.style.display = "none";
    stopBtn.style.display = "inline";

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      searchInput.value = transcript;
      stopMicRecognitionUI();
    };

    recognition.onerror = (event) => {
      if (!isManuallyStopped) {
        alert("음성 인식 오류: " + event.error);
      }
      stopMicRecognitionUI();
    };

    recognition.onend = () => {
      stopMicRecognitionUI();
      isManuallyStopped = false;
    };
  });

  stopBtn.addEventListener('click', () => {
    if (recognition) {
      isManuallyStopped = true;
      recognition.stop();
    }
    stopMicRecognitionUI();
  });

  function stopMicRecognitionUI() {
    micBtn.style.display = "inline";
    stopBtn.style.display = "none";
  }
});


document.getElementById('favoriteBtn').addEventListener('click', () => {
  const title = document.querySelector('#infoContent h3')?.textContent?.replace('노래 제목 : ', '');
  const artist = document.querySelector('#infoContent p')?.textContent?.replace('아티스트 :', '').trim();
  const albumCover = document.getElementById('albumCover').src;

  fetch('/music/toggle-favorite/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({ title, artist, albumCover })
  })
    .then(res => res.json())
    .then(data => {
      const btn = document.getElementById('favoriteBtn');
      if (data.status === 'added') btn.textContent = '❤️';
      else if (data.status === 'removed') btn.textContent = '🤍';
    });
});

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}