// ✅ AI 분석
function analyzeTitleWithAI(title) {
  return fetch('/music/analyze-title/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title })
  })
    .then(res => res.json())
    .catch(err => {
      console.error("🔥 AI 분석 실패:", err);
      return { artist: null, title: null };
    });
}

// ✅ 유튜브 검색
function searchMusic() {
  const query = document.getElementById('searchInput').value;
  if (!query) return;

  saveRecentKeyword(query);

  fetch(`https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&q=${encodeURIComponent(query)}&videoCategoryId=10&maxResults=5&key=${API_KEY}`)
    .then(res => res.json())
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
    .catch(err => console.error("🔥 유튜브 검색 실패:", err));
}

// ✅ 영상 클릭 → 페이지 이동
function openPanel(videoId, originalTitle) {
  analyzeTitleWithAI(originalTitle).then(({ artist, title }) => {
    if (artist && title) {
      const url = `/music/lyrics-info/?artist=${encodeURIComponent(artist)}&title=${encodeURIComponent(title)}&videoId=${encodeURIComponent(videoId)}`;
      window.location.href = url;
    } else {
      alert('AI로 가수/곡명을 추출하지 못했습니다.');
    }
  });
}

// ✅ 자동완성
function handleInputChange() {
  const query = document.getElementById('searchInput').value;
  const recentDiv = document.getElementById('recentKeywords');
  const suggestionsDiv = document.getElementById('suggestions');

  if (!query.trim()) {
    showRecentKeywords();
    return;
  }
  recentDiv.style.display = 'none';
  suggestionsDiv.innerHTML = '';

  fetch(`/music/autocomplete/?q=${encodeURIComponent(query)}`)
    .then(response => response.json())
    .then(data => handleSuggestions(data))
    .catch(err => console.error("🔥 자동완성 요청 실패:", err));
}

function handleSuggestions(data) {
  const suggestionsDiv = document.getElementById('suggestions');
  suggestionsDiv.innerHTML = '';
  const suggestions = data.suggestions || [];

  if (suggestions.length === 0) {
    suggestionsDiv.style.display = 'none';
    return;
  }

  suggestions.forEach(suggestion => {
    const item = document.createElement('div');
    item.textContent = suggestion;
    item.onclick = () => {
      document.getElementById('searchInput').value = suggestion;
      suggestionsDiv.innerHTML = '';
      suggestionsDiv.style.display = 'none';
    };
    suggestionsDiv.appendChild(item);
  });

  suggestionsDiv.style.display = 'block';
}

// ✅ 최근 검색어
function saveRecentKeyword(keyword) {
  let keywords = JSON.parse(localStorage.getItem("recentKeywords") || "[]");
  keywords = [keyword, ...keywords.filter(k => k !== keyword)].slice(0, 10);
  localStorage.setItem("recentKeywords", JSON.stringify(keywords));
}

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
        row.textContent = kw;
        row.onclick = () => {
          document.getElementById("searchInput").value = kw;
          recentDiv.style.display = 'none';
        };
        recentDiv.appendChild(row);
      });

      const clearBtn = document.createElement("div");
      clearBtn.textContent = "전체 삭제 🗑️";
      clearBtn.onclick = () => {
        localStorage.removeItem("recentKeywords");
        showRecentKeywords();
      };

      recentDiv.appendChild(clearBtn);
      recentDiv.style.display = "block";
      suggestionsDiv.style.display = "none";
    }
  }
}

window.onload = function() {
  const urlParams = new URLSearchParams(window.location.search);
  const q = urlParams.get('q');
  if (q) {
    document.getElementById('searchInput').value = q;
    searchMusic();
  }
};

/* ✅ 음성인식 */
let recognition = null;
let isManuallyStopped = false;

const micBtn = document.getElementById('micBtn');
const stopBtn = document.getElementById('stopBtn');
const searchInput = document.getElementById('searchInput');

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
