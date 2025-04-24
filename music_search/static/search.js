// 🎵 자동 가수/곡명 분석 함수 (백엔드 호출)
function analyzeTitleWithAI(title) {
  fetch('/music/analyze-title/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title })
  })
    .then(res => res.json())
    .then(data => {
      console.log("🎤 AI 분석 결과:", data);

      const artist = data.artist;
      const track = data.title;

      if (artist && track) {
        const searchQuery = `${artist} ${track}`;
        console.log("🔍 Apple Music 검색어:", searchQuery);
        fetchTrackFromApple(searchQuery); // 🔄 Apple Music API 검색 실행
        fetchLyrics(artist, track);       // 🎤 가사 요청 추가!
      }
    })
    .catch(err => {
      console.error("🔥 AI 분석 실패:", err);
    });
}

// 🎤 Genius API + 크롤링을 이용한 가사 요청 함수
function fetchLyrics(artist, title) {
  const lyricsBox = document.getElementById('lyricsBox');
  lyricsBox.innerHTML = "🎤 가사 로딩 중...";

  fetch('/music/lyrics/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ artist, title })
  })
    .then(res => res.json())
    .then(data => {
      if (data.lyrics) {
        lyricsBox.innerHTML = `
          <h3>📄 가사</h3>
          <pre style="text-align: left; white-space: pre-wrap;">${data.lyrics}</pre>
        `;
      } else {
        lyricsBox.innerHTML = "❌ 가사를 불러올 수 없습니다.";
      }
    })
    .catch(err => {
      console.error("🔥 가사 요청 실패:", err);
      lyricsBox.innerHTML = "⚠️ 가사 로딩 중 오류 발생!";
    });
}

// ✅ 최근 검색어 기능 관련 함수들
function getStoredKeywords() {
  return JSON.parse(localStorage.getItem("recentKeywords") || "[]");
}

function storeKeyword(keyword) {
  let keywords = getStoredKeywords();
  keywords = [keyword, ...keywords.filter(k => k !== keyword)].slice(0, 5);
  localStorage.setItem("recentKeywords", JSON.stringify(keywords));
}

function deleteKeyword(keyword) {
  let keywords = getStoredKeywords().filter(k => k !== keyword);
  localStorage.setItem("recentKeywords", JSON.stringify(keywords));
  showRecentKeywords();
}

function clearAllKeywords() {
  localStorage.removeItem("recentKeywords");
  showRecentKeywords();
}

function showRecentKeywords() {
  const query = document.getElementById("searchInput").value;
  const recentDiv = document.getElementById("recentKeywords");
  const suggestionsDiv = document.getElementById("suggestions");

  if (query.trim()) {
    recentDiv.style.display = "none";
    return;
  }

  const keywords = getStoredKeywords();
  recentDiv.innerHTML = '';

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
        recentDiv.style.display = "none";
      };

      const delBtn = document.createElement("button");
      delBtn.textContent = "❌";
      delBtn.style.border = "none";
      delBtn.style.background = "transparent";
      delBtn.style.cursor = "pointer";
      delBtn.style.fontSize = "14px";
      delBtn.onclick = () => deleteKeyword(kw);

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
    clearBtn.onclick = clearAllKeywords;

    recentDiv.appendChild(clearBtn);
    recentDiv.style.display = "block";
    suggestionsDiv.style.display = "none";
  } else {
    recentDiv.style.display = "none";
  }
}

function handleInputChange() {
  document.getElementById("recentKeywords").style.display = "none";
  getSuggestions();
}

// 🔍 유튜브 검색 + 결과 표시
function searchMusic() {
  const query = document.getElementById('searchInput').value;
  if (!query) return;

  storeKeyword(query);
  document.getElementById("recentKeywords").style.display = "none";

  const url = `https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&q=${encodeURIComponent(query)}&videoCategoryId=10&maxResults=5&key=${API_KEY}`;

  fetch(url)
    .then(response => response.json())
    .then(data => {
      const resultsDiv = document.getElementById('results');
      resultsDiv.innerHTML = "";

      if (data.items) {
        data.items.forEach(item => {
          const videoId = item.id.videoId;
          const videoTitle = item.snippet.title;
          const thumbnail = item.snippet.thumbnails.medium.url;

          const videoElement = `
            <div class="video">
              <img src="${thumbnail}" alt="${videoTitle}" onclick="openPanel('${videoId}', \`${videoTitle}\`)">
              <p title="${videoTitle}">${videoTitle}</p>
            </div>
          `;
          resultsDiv.innerHTML += videoElement;
        });
      }
    });
}

// 🎵 Apple Music에서 곡 정보 가져오기
function fetchTrackFromApple(query) {
  const infoDiv = document.getElementById('trackInfo');
  const searchTerm = encodeURIComponent(query);
  console.log("📡 iTunes 요청어:", query);
  fetch(`https://itunes.apple.com/search?term=${searchTerm}&entity=musicTrack&limit=1`)
    .then(res => res.json())
    .then(data => {
      console.log("📦 iTunes 응답 데이터:", data);
      if (data.results && data.results.length > 0) {
        const track = data.results[0];
        infoDiv.innerHTML = `
          <h3>${track.trackName}</h3>
          <p>👤 ${track.artistName}</p>
          <p>💼 ${track.collectionName}</p>
          <p>📅 ${new Date(track.releaseDate).toLocaleDateString()}</p>
          <img src="${track.artworkUrl100.replace('100x100', '300x300')}" alt="앨범 커버">
        `;
      } else {
        infoDiv.innerHTML = "🎵 Apple Music에서 곡 정보를 찾을 수 없습니다.";
      }
    });
}

// ▶️ 패널 열기 + 영상 & 트랙 & 가사 표시
function openPanel(videoId, title) {
  analyzeTitleWithAI(title);
  const panel = document.getElementById('sidePanel');
  const content = document.getElementById('panelContent');

  content.innerHTML = `
    <h2>${title}</h2>
    <iframe src="https://www.youtube.com/embed/${videoId}?autoplay=1" frameborder="0" allowfullscreen></iframe>
    <div class="track-info" id="trackInfo">🎵 Apple Music 정보 로딩 중...</div>
    <div id="lyricsBox">🎤 가사 로딩 중...</div>
  `;

  panel.classList.add('open');
}

function closePanel() {
  document.getElementById('sidePanel').classList.remove('open');
  document.getElementById('panelContent').innerHTML = '';
}

// 🔍 유튜브 자동완성 기능
function getSuggestions() {
  const query = document.getElementById('searchInput').value;
  if (!query) {
    document.getElementById('suggestions').innerHTML = '';
    return;
  }

  const script = document.createElement('script');
  script.src = `https://suggestqueries.google.com/complete/search?client=firefox&ds=yt&q=${encodeURIComponent(query)}&callback=handleSuggestions`;
  document.body.appendChild(script);
}

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

function hideSuggestions() {
  setTimeout(() => {
    document.getElementById('suggestions').innerHTML = '';
    document.getElementById('recentKeywords').style.display = 'none';
  }, 200);
}
