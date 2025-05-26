// ✅ 1. 페이지 로드 시 초기 실행: 검색창 초기화, 자동완성 바인딩, 쿼리 파라미터로 자동검색 처리
window.onload = function () {
  const urlParams = new URLSearchParams(window.location.search);
  const q = urlParams.get('q');

  if (q) {
    document.getElementById('searchInput').value = q;
    searchMusic(); // URL에 쿼리 있으면 자동 검색 실행
  }

  hideSuggestions();

  // ✅ 자동완성 입력 이벤트 바인딩
  document.getElementById('searchInput').addEventListener('input', handleInputChange);

  // ✅ Enter 키 입력 시 검색 실행 및 자동완성 닫기
document.getElementById('searchInput').addEventListener('keydown', function (event) {
  const suggestionsDiv = document.getElementById('suggestions');
  if (suggestionsDiv.style.display === 'block' && suggestionItems.length > 0) {
    if (event.key === 'ArrowDown') {
      event.preventDefault();
      selectedSuggestionIndex = (selectedSuggestionIndex + 1) % suggestionItems.length;
      updateSuggestionActive();
    } else if (event.key === 'ArrowUp') {
      event.preventDefault();
      selectedSuggestionIndex = (selectedSuggestionIndex - 1 + suggestionItems.length) % suggestionItems.length;
      updateSuggestionActive();
    } else if (event.key === 'Enter') {
      if (selectedSuggestionIndex >= 0 && suggestionItems[selectedSuggestionIndex]) {
        event.preventDefault();
        document.getElementById('searchInput').value = suggestionItems[selectedSuggestionIndex].textContent;
        hideSuggestions();
        searchMusic();
        return;
      }
    }
  }
  // 엔터 기본 동작 (자동완성창 없을 때만 실행)
  if (event.key === 'Enter') {
    event.preventDefault();
    hideSuggestions();
    searchMusic();
  }
});

function updateSuggestionActive() {
  suggestionItems.forEach((item, idx) => {
    if (idx === selectedSuggestionIndex) {
      item.classList.add('active');
      item.scrollIntoView({ block: "nearest" });
    } else {
      item.classList.remove('active');
    }
  });
}
    // ✅ 🔴 검색 버튼 클릭 시에도 검색 실행되도록 이벤트 바인딩 (이 부분을 반드시 추가!)
  const searchButton = document.querySelector('.search-btn');
  if (searchButton) {
    searchButton.addEventListener('click', function () {
      hideSuggestions(); // 추천어창 숨기기
      searchMusic();     // 유튜브 검색 실행
    });
  }
};

// ✅ 2. 검색창 입력 시 자동완성 API 요청 함수
function handleInputChange() {
  const input = document.getElementById('searchInput');
  const suggestionsDiv = document.getElementById('suggestions');

  if (!suggestionsDiv) return;  // ✅ suggestions 요소 없으면 함수 종료

  if (!input.value.trim()) {
    // ✅ 이 부분이 반드시 필요!
    suggestionsDiv.style.display = 'none';
    suggestionsDiv.innerHTML = '';
    suggestionItems = [];
    selectedSuggestionIndex = -1;
    return;
  }

  if (document.activeElement !== input) return; // 검색창이 포커스 상태일 때만 실행

  // 이하 자동완성 API 요청 로직 유지
  const query = input.value;
  fetch(`/music/autocomplete/?q=${encodeURIComponent(query)}`)
    .then(response => response.json())
    .then(data => handleSuggestions(data))
    .catch(err => console.error("🔥 자동완성 요청 실패:", err));
}


// ✅ 3. 추천어 목록을 HTML로 표시하는 함수
function handleSuggestions(data) {
  const suggestionsDiv = document.getElementById('suggestions');
  if (!suggestionsDiv) return;

  suggestionsDiv.innerHTML = '';
  const suggestions = data.suggestions || [];

  if (suggestions.length === 0) {
    suggestionsDiv.style.display = 'none';
    suggestionItems = [];
    selectedSuggestionIndex = -1;
    return;
  }

  suggestionItems = [];

  suggestions.forEach((suggestion, idx) => {
    const item = document.createElement('div');
    item.textContent = suggestion;
    item.classList.add('suggestion-item');
    item.onclick = () => {
      document.getElementById('searchInput').value = suggestion;
      suggestionsDiv.innerHTML = '';
      suggestionsDiv.style.display = 'none';
      searchMusic(); // ← 이 줄을 추가하면 클릭 후 바로 검색!
    };
    suggestionsDiv.appendChild(item);
    suggestionItems.push(item);
  });

  selectedSuggestionIndex = -1;
  suggestionsDiv.style.display = 'block';
}


let allResults = [];
let currentPage = 1;
const RESULTS_PER_PAGE = 5;


// ✅ 4. 검색 실행 함수 - 유튜브 API 호출 후 결과 렌더링
function searchMusic() {
  const query = document.getElementById('searchInput').value;
  if (!query) return;

  hideSuggestions(); // 검색 시 자동완성 닫기
  
  // 혹시라도 suggestions 박스가 남아있는 현상 방지:
  const suggestionsDiv = document.getElementById('suggestions');
  if (suggestionsDiv) {
    suggestionsDiv.style.display = 'none';
    suggestionsDiv.innerHTML = '';
  }

  // 🔥 YouTube Data API로 25개까지 검색
  fetch(`https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&q=${encodeURIComponent(query)}&videoCategoryId=10&maxResults=25&key=${API_KEY}`)
    .then(res => res.json())
    .then(data => {
      console.log("🔥 API 응답 결과:", data);
      if (!data.items || data.items.length === 0) {
        document.getElementById('results').innerHTML = '<p style="color:white;">검색 결과가 없습니다.</p>';
        document.getElementById('pagination').style.display = 'none';
        return;
      }
    
      allResults = data.items;
      currentPage = 1;
      renderResultsPage(currentPage);
      document.querySelector('.results-box').style.display = 'block';
      document.getElementById('pagination').style.display = 'block';
      document.getElementById('searchInput').value = '';
    })
    .catch(err => {
      console.error("🔥 유튜브 검색 실패:", err);
      document.getElementById('searchInput').value = '';
      handleInputChange();
    });
}

// ✅ 🔥 페이지별 결과 렌더링
function renderResultsPage(page) {
  const results = document.getElementById('results');
  results.innerHTML = "";

  const start = (page - 1) * RESULTS_PER_PAGE;
  const end = start + RESULTS_PER_PAGE;
  const paginatedItems = allResults.slice(start, end);

  paginatedItems.forEach(item => {
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

  renderPagination(); // 페이지네이션 버튼 다시 렌더링
}

// ✅ 🔥 페이지네이션 바 렌더링
function renderPagination() {
  const pagination = document.getElementById('pagination');
  if (!pagination) return; // 없으면 무시

  pagination.innerHTML = "";

  const pageCount = Math.ceil(allResults.length / RESULTS_PER_PAGE);

  for (let i = 1; i <= pageCount; i++) {
    const btn = document.createElement('button');
    btn.textContent = i;
    btn.classList.add('page-btn');
    if (i === currentPage) btn.classList.add('active');

    btn.addEventListener('click', () => {
      currentPage = i;
      renderResultsPage(currentPage);
    });

    pagination.appendChild(btn);
  }
}

// ✅ 5. 썸네일 클릭 시 AI로 곡 제목 분석 후 상세 페이지 이동
function openPanel(videoId, originalTitle) {
  analyzeTitleWithAI(originalTitle).then(({ artist, title }) => {
    if (artist && title) {
      const url = `/music/lyrics-info/?artist=${encodeURIComponent(artist)}&title=${encodeURIComponent(title)}&videoId=${encodeURIComponent(videoId)}`;
      window.location.href = url; // 상세페이지로 이동
    } else {
      alert('AI로 가수/곡명을 추출하지 못했습니다.');
    }
  });
}

// ✅ 6. 영상 제목을 GPT에게 보내서 artist/title 추출하는 함수
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

// ✅ 7. 자동완성 박스 숨기는 유틸 함수
function hideSuggestions() {
  const suggestions = document.getElementById('suggestions');
  if (suggestions) {
    suggestions.style.display = 'none';
    suggestions.innerHTML = ''; // 자동완성 내용 초기화
  }
}

// ✅ 8. 음성 인식 기능 (마이크 버튼 클릭 시 검색어 받아오기)
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
    searchInput.value = transcript; // 인식된 텍스트를 입력창에 넣기
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
    recognition.stop(); // 음성 인식 종료
  }
  stopMicRecognitionUI();
});

// ✅ 음성 인식 UI 초기화 함수
function stopMicRecognitionUI() {
  micBtn.style.display = "inline";
  stopBtn.style.display = "none";
}

// 자동완성창 닫기용 바디 클릭 리스너
document.addEventListener('click', function (e) {
  const searchInput = document.getElementById('searchInput');
  const suggestionsDiv = document.getElementById('suggestions');
  if (!suggestionsDiv) return;

  // input, suggestions 영역 외 클릭시 닫기
  if (
    !searchInput.contains(e.target) &&
    !suggestionsDiv.contains(e.target)
  ) {
    hideSuggestions();
  }
});