// 🎵 자동 가수/곡명 분석 함수 (백엔드 호출)
function analyzeTitleWithAI(title) {
  fetch('/music/analyze-title/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title })
  })
    .then(res => res.json())
    .then(data => {
      const artist = data.artist;
      const track = data.title;
      if (artist && track) {
        const searchQuery = `${artist} ${track}`;
        fetchTrackFromApple(searchQuery);
        fetchLyrics(artist, track);
      }
    })
    .catch(err => {
      console.error("🔥 AI 분석 실패:", err);
    });
}

// 🎤 Genius API + 크롤링을 이용한 가사 요청 함수
function fetchLyrics(artist, title) {
  const lyricsPanel = document.getElementById('lyricsPanel');
  if (!lyricsPanel) return;
  lyricsPanel.innerHTML = `
    <div style="display:flex;justify-content:center;align-items:center;height:100%;color:#888;">
      🎤 가사 로딩 중...
    </div>
  `;
  lyricsPanel.classList.remove('hidden');
  lyricsPanel.classList.add('open');

  fetch('/music/lyrics/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ artist, title })
  })
    .then(res => res.json())
    .then(data => {
      if (data.lyrics) {
        lyricsPanel.innerHTML = `
          <h3>📄 가사</h3>
          <div class="lyrics-content">${data.lyrics.replace(/\n/g, '<br>')}</div>
        `;

        // 글씨 크기 조정
        const lyricsContent = document.querySelector('.lyrics-content');
        if (lyricsContent) {
          lyricsContent.style.fontSize = '20px';  // 원하는 글씨 크기로 설정
        }

      } else {
        lyricsPanel.innerHTML = "❌ 가사를 불러올 수 없습니다.";
      }
    })
    .catch(err => {
      console.error("🔥 가사 요청 실패:", err);
      lyricsPanel.innerHTML = "⚠️ 가사 로딩 중 오류 발생!";
    });
}

// ▶️ 가사 패널 토글
function toggleLyricsPanel() {
  const lyricsPanel = document.getElementById('lyricsPanel');
  const recentPanel = document.getElementById('recentPanel');
  if (!lyricsPanel || !recentPanel) return;

  if (lyricsPanel.classList.contains('open')) {
    lyricsPanel.classList.remove('open');
  } else {
    lyricsPanel.classList.add('open');
    recentPanel.classList.remove('open');
    
  }
}

// 🔍 검색창 자동완성 (django 서버가 구글 sugges api 호출하는 방법)
function handleInputChange() {
  const query = document.getElementById('searchInput').value;
  const recentDiv = document.getElementById('recentKeywords');
  
  if (!query.trim()) {
    showRecentKeywords();
    return;
  }
  recentDiv.style.display = 'none';

  // ✅ Django 서버로 요청
  fetch(`/music/autocomplete/?q=${encodeURIComponent(query)}`)
    .then(response => response.json())
    .then(data => {
      handleSuggestions(["", data.suggestions]);
    })
    .catch(err => {
      console.error("🔥 자동완성 요청 실패:", err);
    });
}

// 🔍 유튜브 검색 실행
function searchMusic() {
  const query = document.getElementById('searchInput').value;
  if (!query) return;

  saveRecentKeyword(query);

  fetch(`https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&q=${encodeURIComponent(query)}&videoCategoryId=10&maxResults=5&key=${API_KEY}`)
    .then(response => response.json())
    .then(data => {
      const results = document.getElementById('results');
      results.innerHTML = "";
      if (data.items) {
        data.items.forEach(item => {
          const videoId = item.id.videoId;
          const title = item.snippet.title;
          const thumbnail = item.snippet.thumbnails.medium.url;
          results.innerHTML += `
            <div class="video">
              <img src="${thumbnail}" alt="${title}" onclick="openPanel('${videoId}', \`${title}\`)">
              <p title="${title}">${title}</p>
            </div>
          `;
        });
      }
    })
    .catch(err => {
      console.error("🔥 유튜브 검색 실패:", err);
    });
}

// ▶️ 영상 클릭 시 패널 열기 + 최근 시청 저장
function openPanel(videoId, title) {
  saveRecentlyWatched(title, videoId);
  analyzeTitleWithAI(title);

  const panel = document.getElementById("sidePanel");
  panel.classList.add("open");

  const panelContent = document.getElementById('panelContent');
  panelContent.innerHTML = `
    <h2>${title}</h2>
    <iframe src="https://www.youtube.com/embed/${videoId}?autoplay=1" frameborder="0" allowfullscreen></iframe>
    <div id="trackInfo">🎵 Apple Music 정보 로딩 중...</div>
  `;
}

// ▶️ 자동완성 결과 렌더링
function handleSuggestions(data) {
  const suggestionsDiv = document.getElementById('suggestions');
  suggestionsDiv.innerHTML = '';
  const [_, suggestions] = data;

  suggestions.slice(0, 6).forEach(suggestion => {
    const item = document.createElement('div');
    item.textContent = suggestion;
    item.onclick = () => {
      document.getElementById('searchInput').value = suggestion;
      suggestionsDiv.innerHTML = '';
    };
    suggestionsDiv.appendChild(item);
  });
}
window.handleSuggestions = handleSuggestions;

// ▶️ 검색창 포커스 시 최근 검색어 보여주기
function showRecentKeywords() {
  const recentDiv = document.getElementById('recentKeywords');
  const suggestionsDiv = document.getElementById('suggestions');
  const query = document.getElementById('searchInput').value;

  recentDiv.innerHTML = '';
  if (!query.trim()) {
    const keywords = JSON.parse(localStorage.getItem("recentKeywords") || "[]");
    if (keywords.length > 0) {
      keywords.forEach(kw => {
        const row = document.createElement("div");
        row.style.display = "flex";
        row.style.justifyContent = "space-between";
        row.style.alignItems = "center";
        row.style.padding = "6px 8px";
        row.style.borderBottom = "1px solid #eee";

        const span = document.createElement("span");
        span.textContent = kw;
        span.style.flex = "1";
        span.style.cursor = "pointer";
        span.onclick = () => {
          document.getElementById("searchInput").value = kw;
        };

        const delBtn = document.createElement("button");
        delBtn.textContent = "❌";
        delBtn.style.border = "none";
        delBtn.style.background = "transparent";
        delBtn.style.cursor = "pointer";
        delBtn.style.fontSize = "14px";
        delBtn.onclick = () => deleteRecentKeyword(kw);

        row.appendChild(span);
        row.appendChild(delBtn);
        recentDiv.appendChild(row);
      });

      const clearBtn = document.createElement("button");
      clearBtn.textContent = "전체 삭제 🗑️";
      clearBtn.style.width = "100%";
      clearBtn.style.padding = "8px";
      clearBtn.style.marginTop = "6px";
      clearBtn.style.border = "none";
      clearBtn.style.background = "#f8f8f8";
      clearBtn.style.cursor = "pointer";
      clearBtn.style.borderTop = "1px solid #ddd";
      clearBtn.onclick = clearAllRecentKeywords;

      recentDiv.appendChild(clearBtn);
      recentDiv.style.display = "block";
      suggestionsDiv.style.display = "none";
    }
  }
}

// ▶️ 최근 검색어 저장/삭제
function saveRecentKeyword(keyword) {
  let keywords = JSON.parse(localStorage.getItem("recentKeywords") || "[]");
  keywords = [keyword, ...keywords.filter(k => k !== keyword)].slice(0, 5);
  localStorage.setItem("recentKeywords", JSON.stringify(keywords));
}
function deleteRecentKeyword(keyword) {
  let keywords = JSON.parse(localStorage.getItem("recentKeywords") || "[]");
  keywords = keywords.filter(k => k !== keyword);
  localStorage.setItem("recentKeywords", JSON.stringify(keywords));
  showRecentKeywords();
}
function clearAllRecentKeywords() {
  localStorage.removeItem("recentKeywords");
  showRecentKeywords();
}
function hideSuggestions() {
  setTimeout(() => {
    document.getElementById('suggestions').innerHTML = '';
    document.getElementById('recentKeywords').style.display = 'none';
  }, 200);
}

// ▶️ 최근 시청 저장/목록 UI
function saveRecentlyWatched(title, videoId) {
  let list = JSON.parse(localStorage.getItem("recentVideos") || "[]");
  list = list.filter(item => item.title !== title);
  list.unshift({ title, videoId });
  list = list.slice(0, 5);
  localStorage.setItem("recentVideos", JSON.stringify(list));
}
function updateRecentList() {
  const list = JSON.parse(localStorage.getItem("recentVideos") || "[]");
  const container = document.getElementById("recentList");
  container.innerHTML = "";

  list.forEach(({ title, videoId }) => {
    const div = document.createElement("div");
    div.textContent = title;
    div.className = "recent-item";
    div.onclick = () => openPanel(videoId, title);
    container.appendChild(div);
  });
}
function toggleRecentPanel() {
  const panel = document.getElementById("recentPanel");
  const lyricsPanel = document.getElementById("lyricsPanel");
  if (panel) {
    panel.classList.toggle("open");
    panel.classList.remove("hidden");
  }
  if (lyricsPanel) {
    lyricsPanel.classList.remove("open");
  }
  updateRecentList();
}

// ▶️ Apple Music 곡 정보
function fetchTrackFromApple(query) {
  const trackInfoDiv = document.getElementById('trackInfo');
  const searchTerm = encodeURIComponent(query);

  fetch(`https://itunes.apple.com/search?term=${searchTerm}&entity=musicTrack&limit=1`)
    .then(res => res.json())
    .then(data => {
      if (data.results && data.results.length > 0) {
        const track = data.results[0];
        trackInfoDiv.innerHTML = `
          <h3>노래 제목 : ${track.trackName}</h3>
          <p><strong>아티스트 :</strong> ${track.artistName}</p>
          <p><strong>앨범 :</strong> ${track.collectionName}</p>
          <p><strong>발매일 :</strong> ${new Date(track.releaseDate).toLocaleDateString()}</p>
          <p><strong>장르 :</strong> ${track.primaryGenreName}</p>
          <img src="${track.artworkUrl100.replace('100x100', '300x300')}" alt="앨범 커버">
        `;
      } else {
        trackInfoDiv.innerHTML = "🎵 Apple Music에서 곡 정보를 찾을 수 없습니다.";
      }
    })
    .catch(err => {
      console.error("🔥 Apple Music 검색 실패:", err);
    });
}

// ▶️ 패널 닫기
function closePanel() {
  document.getElementById('sidePanel').classList.remove('open');
}

// ▶️ 모든 버튼 이벤트 연결
document.addEventListener('DOMContentLoaded', () => {
  const toggleLyrics = document.getElementById('toggleLyrics');
  if (toggleLyrics) {
    toggleLyrics.addEventListener('click', toggleLyricsPanel);
  }

  const toggleRecent = document.getElementById("toggleRecent");
  if (toggleRecent) {
    toggleRecent.addEventListener("click", toggleRecentPanel);
  }

  const searchInput = document.getElementById('searchInput');
  if (searchInput) {
    searchInput.addEventListener('keypress', (event) => {
      if (event.key === 'Enter') {
        event.preventDefault();
        searchMusic();
      }
    });
  }
});

// ✅ 가사 번역 기능
const translatedLyrics = {
  ko: "",
  en: "",
  ja: "",
  zh: ""
};

function translateLyrics(lang) {
  const lyricsContent = document.getElementById('lyricsContent');
  if (translatedLyrics[lang]) {
    lyricsContent.innerHTML = translatedLyrics[lang];
  } else {
    lyricsContent.innerHTML = "⚠️ 번역본이 없습니다.";
  }
}

// ✅ 가사 가져오고 자동번역하는 함수
async function fetchLyrics(artist, title) {
  const lyricsPanel = document.getElementById('lyricsPanel');
  if (!lyricsPanel) return;
  
  lyricsPanel.innerHTML = `
    <h3>📄 가사</h3>
    <div class="translation-buttons">
      <button onclick="translateLyrics('ko')">한국어</button>
      <button onclick="translateLyrics('en')">영어</button>
      <button onclick="translateLyrics('ja')">일본어</button>
      <button onclick="translateLyrics('zh')">중국어</button>
    </div>
    <div id="lyricsContent">🎤 가사 로딩 중...</div>
  `;
  lyricsPanel.classList.remove('hidden');
  lyricsPanel.classList.add('open');

  try {
    // 1. 가사 가져오기
    const res = await fetch('/music/lyrics/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ artist, title })
    });
    const data = await res.json();

    if (!data.lyrics) {
      document.getElementById('lyricsContent').innerHTML = "❌ 가사를 불러올 수 없습니다.";
      return;
    }

    const originalLyrics = data.lyrics.replace(/\n/g, '<br>');

    // 2. 번역 요청
    const translationRes = await fetch('/music/translate-lyrics/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ lyrics: data.lyrics })
    });

    const translations = await translationRes.json();

    // 3. 감지된 언어 저장
    const detectedLang = translations.detected; // 감지된 언어 (ko, en, ja, zh)

    // 4. 가져온 가사 저장
    translatedLyrics[detectedLang] = `<p class="lyrics-content">${originalLyrics}</p>`;

    // 5. 번역된 가사 저장
    if (translations.en) translatedLyrics['en'] = `<p class="lyrics-content">${translations.en.replace(/\n/g, '<br>')}</p>`;
    if (translations.ja) translatedLyrics['ja'] = `<p class="lyrics-content">${translations.ja.replace(/\n/g, '<br>')}</p>`;
    if (translations.zh) translatedLyrics['zh'] = `<p class="lyrics-content">${translations.zh.replace(/\n/g, '<br>')}</p>`;
    if (translations.ko) translatedLyrics['ko'] = `<p class="lyrics-content">${translations.ko.replace(/\n/g, '<br>')}</p>`;

    // 6. 감지된 원본 가사 기본 표시
    document.getElementById('lyricsContent').innerHTML = translatedLyrics[detectedLang];

  } catch (err) {
    console.error("🔥 가사 또는 번역 요청 실패:", err);
    document.getElementById('lyricsContent').innerHTML = "⚠️ 가사 로딩 중 오류 발생!";
  }
}