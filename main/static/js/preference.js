<<<<<<< HEAD
// // ✅ 문항과 응답 레이블 정의 (변수 중복 선언 방지용 IIFE 래핑)
// (() => {
//   const questions = [
//     "친구들이랑 모이면 내가 분위기를 주도하는 편이다.",
//     "주말에는 야외 활동이나 운동을 즐긴다.",
//     "영화나 드라마를 보면 쉽게 감정이입한다.",
//     "최신 유행이나 신상 아이템을 궁금해하는 편이다.",
//     "혼자 카페나 방에서 조용히 쉬는 걸 좋아한다.",
//     "나는 즉흥적으로 계획을 바꾸는 걸 즐긴다.",
//     "오래된 물건이나 빈티지 감성을 좋아한다."
//   ];

//   const scaleLabels = ["반대", "약간 반대", "중립", "약간 동의", "동의"];
//   let answers = JSON.parse(localStorage.getItem("preferenceAnswers")) || Array(questions.length).fill(null);
//   let current = parseInt(localStorage.getItem("preferenceCurrent")) || 0;

//   window.initPreferenceTest = function () {
//     loadQuestion();
//     updateProgress();

//     const resultBtn = document.getElementById("result-btn");
//     if (resultBtn) resultBtn.disabled = answers.includes(null);

//     const prevBtn = document.getElementById("prev-btn");
//     if (prevBtn) prevBtn.disabled = current === 0;
//   };

//   function loadQuestion() {
//     const qDiv = document.getElementById("questions");
//     if (!qDiv) return;
//     qDiv.innerHTML = `
//       <div class="question">Q. ${questions[current]}</div>
//       <div class="answer-buttons">
//         ${scaleLabels
//           .map(
//             (label, idx) =>
//               `<button class="answer-btn ${getButtonClass(idx)}" onclick="selectAnswer(${idx + 1}, this)">${label}</button>`
//           )
//           .join("")}
//       </div>
//     `;

//     if (answers[current] !== null) {
//       const selectedButton = qDiv.querySelectorAll(".answer-buttons button")[
//         answers[current] - 1
//       ];
//       if (selectedButton) selectedButton.classList.add("selected");
//     }
//   }

//   window.selectAnswer = function (value, btn) {
//     answers[current] = value;
//     localStorage.setItem("preferenceAnswers", JSON.stringify(answers));

//     const buttons = document.querySelectorAll(".answer-buttons button");
//     buttons.forEach((b) => b.classList.remove("selected"));
//     btn.classList.add("selected");

//     setTimeout(() => {
//       current++;
//       localStorage.setItem("preferenceCurrent", current);

//       if (current < questions.length) {
//         loadQuestion();
//       } else {
//         const resultBtn = document.getElementById("result-btn");
//         if (resultBtn) {
//           resultBtn.classList.add("active");
//           resultBtn.disabled = false;
//         }
//       }
//       updateProgress();
//     }, 300);
//   };

//   function getButtonClass(idx) {
//     return [
//       "strong-disagree",
//       "disagree",
//       "neutral",
//       "agree",
//       "strong-agree",
//     ][idx];
//   }

//   function updateProgress() {
//     const progress = document.getElementById("progress");
//     if (progress) {
//       const percent = (current / questions.length) * 100;
//       progress.style.width = `${percent}%`;
//     }

//     const prevBtn = document.getElementById("prev-btn");
//     if (prevBtn) prevBtn.disabled = current === 0;
//   }

//   window.prevQuestion = function () {
//     if (current > 0) {
//       current--;
//       localStorage.setItem("preferenceCurrent", current);
//       loadQuestion();
//       updateProgress();
//     }
//   };

//   window.calculateResult = function () {
//     if (answers.includes(null)) {
//       alert("모든 질문에 답해주세요!");
//       return;
//     }

//     const [bright, fast, emotion, trendy, calm, indie, classic] = answers;

//     let genre = "팝";
//     if (bright >= 4 && fast >= 4 && emotion >= 4 && trendy >= 4)
//       genre = "K-pop, EDM";
//     else if (calm >= 4 && emotion >= 4 && classic >= 4)
//       genre = "발라드, 재즈";
//     else if (fast >= 4 && emotion <= 2 && trendy >= 4)
//       genre = "힙합, 일렉트로닉";
//     else if (calm >= 4 && emotion <= 2 && classic >= 4)
//       genre = "클래식, 인디";
//     else if (bright >= 4 && fast >= 4 && trendy >= 4 && emotion <= 2)
//       genre = "록, 메탈";
//     else genre = "OST, R&B";

//     document.getElementById("result").innerText = `추천 장르: ${genre}`;
//     localStorage.setItem("preferenceResult", genre);

//     fetch(`/recommend_by_genre/?genre=${encodeURIComponent(genre)}`)
//       .then((response) => response.json())
//       .then((data) => {
//         const recDiv = document.getElementById("recommend-songs");
//         if (data.songs.length === 0) {
//           recDiv.innerHTML = "<p style='color:white;'>추천 음악이 없습니다.</p>";
//           return;
//         }

//         recDiv.innerHTML = `<div class="recommend-title">추천 음악</div>` +
//           data.songs
//             .map(
//               (song) =>
//                 `<div class="recommended-song" onclick="window.location.href='/music/?q=${encodeURIComponent(
//                   song.title + " " + song.artist
//                 )}'">
//                   ${song.title} - ${song.artist} (${song.genre})
//                 </div>`
//             )
//             .join("");
//       });
//   };

//   window.restorePreferenceState = function () {
//     const savedResult = localStorage.getItem("preferenceResult");
//     if (savedResult) {
//       document.getElementById("result").innerText = `추천 장르: ${savedResult}`;
//     }
//   };
// })();



// ✅ 질문 배열 정의
window.questions = [
=======
// ✅ 질문 목록 정의
const questions = [
>>>>>>> dayoung
  "친구들이랑 모이면 내가 분위기를 주도하는 편이다.",
  "주말에는 야외 활동이나 운동을 즐긴다.",
  "영화나 드라마를 보면 쉽게 감정이입한다.",
  "최신 유행이나 신상 아이템을 궁금해하는 편이다.",
  "혼자 카페나 방에서 조용히 쉬는 걸 좋아한다.",
  "나는 즉흥적으로 계획을 바꾸는 걸 즐긴다.",
  "오래된 물건이나 빈티지 감성을 좋아한다."
];

<<<<<<< HEAD
// ✅ 사용자 응답 및 현재 질문 인덱스 로딩
window.answers = JSON.parse(localStorage.getItem("preferenceAnswers")) || Array(window.questions.length).fill(null);
window.current = parseInt(localStorage.getItem("preferenceCurrent")) || 0;

// ✅ ⚠️ 방어 로직: current가 질문 개수를 넘으면 초기화
if (window.current >= window.questions.length) {
  window.current = 0;
  window.answers = Array(window.questions.length).fill(null);
  localStorage.setItem("preferenceCurrent", "0");
  localStorage.setItem("preferenceAnswers", JSON.stringify(window.answers));
}

// ✅ 초기화 함수
window.initPreferenceTest = () => {
  loadQuestion();
  updateProgress();

  const resultBtn = document.getElementById("result-btn");
  if (resultBtn) resultBtn.disabled = window.answers.includes(null);

  const prevBtn = document.getElementById("prev-btn");
  if (prevBtn) prevBtn.disabled = window.current === 0;
};

// ✅ 현재 질문 렌더링
function loadQuestion() {
  const qDiv = document.getElementById("questions");
  if (!qDiv) return;

  qDiv.innerHTML = `
    <div class="question">Q. ${window.questions[window.current]}</div>
    <div class="answer-buttons">
      ${["반대", "약간 반대", "중립", "약간 동의", "동의"]
        .map((label, idx) =>
          `<button class="answer-btn ${getButtonClass(idx)}" onclick="selectAnswer(${idx + 1}, this)">${label}</button>`
        ).join("")}
    </div>
  `;

  if (window.answers[window.current] !== null) {
    const selectedButton = qDiv.querySelectorAll(".answer-buttons button")[window.answers[window.current] - 1];
    if (selectedButton) selectedButton.classList.add("selected");
  }
}

// ✅ 답변 선택 처리
window.selectAnswer = function (value, btn) {
  window.answers[window.current] = value;
  localStorage.setItem("preferenceAnswers", JSON.stringify(window.answers));

  document.querySelectorAll(".answer-buttons button").forEach(b => b.classList.remove("selected"));
  btn.classList.add("selected");

  setTimeout(() => {
    window.current++;
    localStorage.setItem("preferenceCurrent", window.current);

    if (window.current < window.questions.length) {
      loadQuestion();
    } else {
      const resultBtn = document.getElementById("result-btn");
      if (resultBtn) {
        resultBtn.classList.add("active");
        resultBtn.disabled = false;
      }
    }
    updateProgress();
  }, 300);
};

// ✅ 이전 질문으로 이동
window.prevQuestion = function () {
  if (window.current > 0) {
    window.current--;
    localStorage.setItem("preferenceCurrent", window.current);
    loadQuestion();
    updateProgress();
  }
};

// ✅ 버튼 클래스 스타일링용
=======
let current = 0;
let answers = Array(questions.length).fill(null);
let selectedSido = null;
let selectedGugun = null;

// ✅ 시/도 초기 옵션 추가
function populateSidoOptions() {
  const sidoSelect = document.getElementById("sido-select");
  const sidoList = [
    "서울특별시", "부산광역시", "대구광역시", "인천광역시", "광주광역시",
    "대전광역시", "울산광역시", "세종특별자치시", "경기도", "강원특별자치도",
    "충청북도", "충청남도", "전라북도", "전라남도", "경상북도", "경상남도", "제주특별자치도"
  ];

  sidoList.forEach(sido => {
    const option = document.createElement("option");
    option.value = sido;
    option.textContent = sido;
    sidoSelect.appendChild(option);
  });
}

// ✅ 색상 클래스 매핑
>>>>>>> dayoung
function getButtonClass(idx) {
  return ["strong-disagree", "disagree", "neutral", "agree", "strong-agree"][idx];
}

<<<<<<< HEAD
// ✅ 진행도 바 업데이트
function updateProgress() {
  const progress = document.getElementById("progress");
  if (progress) {
    const percent = (window.current / window.questions.length) * 100;
    progress.style.width = `${percent}%`;
  }

  const prevBtn = document.getElementById("prev-btn");
  if (prevBtn) prevBtn.disabled = window.current === 0;
}

// ✅ 최종 결과 계산 및 추천 곡 요청
window.calculateResult = function () {
  if (window.answers.includes(null)) {
    alert("모든 질문에 답해주세요!");
    return;
  }

  const [bright, fast, emotion, trendy, calm, indie, classic] = window.answers;

  let genre = "팝";
  if (bright >= 4 && fast >= 4 && emotion >= 4 && trendy >= 4) genre = "K-pop, EDM";
  else if (calm >= 4 && emotion >= 4 && classic >= 4) genre = "발라드, 재즈";
  else if (fast >= 4 && emotion <= 2 && trendy >= 4) genre = "힙합, 일렉트로닉";
  else if (calm >= 4 && emotion <= 2 && classic >= 4) genre = "클래식, 인디";
  else if (bright >= 4 && fast >= 4 && trendy >= 4 && emotion <= 2) genre = "록, 메탈";
  else genre = "OST, R&B";

  document.getElementById("result").innerText = `추천 장르: ${genre}`;
  localStorage.setItem("preferenceResult", genre);

  fetch(`/recommend_by_genre/?genre=${encodeURIComponent(genre)}`)
    .then((response) => response.json())
    .then((data) => {
      const recDiv = document.getElementById("recommend-songs");
      recDiv.innerHTML = "<div class='recommend-title' style='color:white;'>추천 음악</div>";

      if (data.songs.length === 0) {
        recDiv.innerHTML += "<p style='color:white;'>추천 곡이 없습니다.</p>";
        return;
      }

      data.songs.forEach((song) => {
        const div = document.createElement("div");
        div.className = "recommended-song";
        div.style.color = "white";
        div.style.cursor = "pointer";
        div.style.marginBottom = "5px";
        div.innerText = `${song.title} - ${song.artist} (${song.normalized_genre})`;
        div.onclick = () => {
          window.location.href = `/music/?q=${encodeURIComponent(song.title + " " + song.artist)}`;
        };
        recDiv.appendChild(div);
      });
    });
};

// ✅ 저장된 추천 결과 복원
window.restorePreferenceState = function () {
  const savedResult = localStorage.getItem("preferenceResult");
  if (savedResult) {
    document.getElementById("result").innerText = `추천 장르: ${savedResult}`;
  }
};
=======
// ✅ 질문 로딩 및 버튼 렌더링
function loadQuestion() {
  const qBox = document.getElementById("question-box");
  if (!qBox) return;

  if (current >= questions.length) {
    qBox.style.display = "none";
    document.getElementById("region-question").style.display = "block";
    updateResultButtonState();
    return;
  }

  const labels = ["반대", "약간 반대", "중립", "약간 동의", "동의"];
  qBox.innerHTML = `
    <div class="question">Q${current + 1}. ${questions[current]}</div>
    <div class="answer-buttons">
      ${labels.map((label, idx) => `
        <button class="answer-btn ${getButtonClass(idx)}" onclick="selectAnswer(${idx + 1}, this)">${label}</button>
      `).join("")}
    </div>
    <div class="nav-buttons">
      <button id="prev-btn" onclick="prevQuestion()">이전</button>
      <button id="next-btn" onclick="loadQuestion()">다음</button>
    </div>
  `;

  // ✅ 버튼 제어는 반드시 렌더링 이후에!
  setTimeout(() => {
    const prevBtn = document.getElementById("prev-btn");
    const nextBtn = document.getElementById("next-btn");

    if (prevBtn) prevBtn.disabled = current === 0;
    if (nextBtn) nextBtn.style.display = current < questions.length - 1 ? "inline-block" : "none";

    if (answers[current] !== null) {
      const selected = document.querySelectorAll(".answer-buttons button")[answers[current] - 1];
      if (selected) selected.classList.add("selected");
    }
  }, 0);
}

// ✅ 답변 선택 시 다음 질문
function selectAnswer(value, btn) {
  answers[current] = value;
  document.querySelectorAll(".answer-buttons button").forEach(b => b.classList.remove("selected"));
  btn.classList.add("selected");

  setTimeout(() => {
    current++;
    loadQuestion();
    updateProgress();
    updateResultButtonState();
  }, 300);
}

// ✅ 이전 질문으로 이동
function prevQuestion() {
  if (current > 0) {
    current--;
    loadQuestion();
    updateProgress();
    updateResultButtonState();
  }
}

// ✅ 진행 바 업데이트
function updateProgress() {
  const percent = (current / questions.length) * 100;
  document.getElementById("progress").style.width = `${percent}%`;
}

// ✅ 시/도 선택 시 구군 로딩
function onSidoSelect(sido) {
  selectedSido = sido;
  selectedGugun = null;

  const gugunSelect = document.getElementById("gugun-select");
  gugunSelect.innerHTML = '<option value="">구/군을 선택하세요</option>';
  gugunSelect.disabled = true;

  fetch(`/get_guguns/?sido=${encodeURIComponent(sido)}`)
    .then(res => res.json())
    .then(data => {
      data.guguns.forEach(gugun => {
        const option = document.createElement("option");
        option.value = gugun;
        option.textContent = gugun;
        gugunSelect.appendChild(option);
      });
      gugunSelect.disabled = false;
      updateResultButtonState();
    });
}

// ✅ 구군 선택 처리
function onGugunSelect(gugun) {
  selectedGugun = gugun;
  updateResultButtonState();
}

// ✅ 결과 버튼 활성화 조건 체크
function updateResultButtonState() {
  const resultBtn = document.getElementById("result-btn");
  const regionReady = selectedSido && selectedGugun;
  const allAnswered = answers.every(ans => ans !== null);
  const canClick = regionReady && allAnswered;

  if (resultBtn) {
    resultBtn.disabled = !canClick;
    if (canClick) {
      resultBtn.classList.add("active");
    } else {
      resultBtn.classList.remove("active");
    }
  }
}

// ✅ 결과 계산 및 추천 요청
function calculateResult() {
  if (!selectedSido || !selectedGugun) return;

  fetch(`/get_weather_genre/?sido=${encodeURIComponent(selectedSido)}&gugun=${encodeURIComponent(selectedGugun)}`)
    .then(res => res.json())
    .then(data => {
      const pty = data.pty || "0";
      const weatherBonus = weatherScoreMap[pty] || {};
      const [bright, fast, emotion, trendy, calm, indie, classic] = answers;

      const final = {
        bright: (bright || 0) + (weatherBonus.bright || 0),
        fast: (fast || 0) + (weatherBonus.fast || 0),
        emotion: (emotion || 0) + (weatherBonus.emotion || 0),
        trendy: (trendy || 0) + (weatherBonus.trendy || 0),
        calm: (calm || 0) + (weatherBonus.calm || 0),
        indie: (indie || 0) + (weatherBonus.indie || 0),
        classic: (classic || 0) + (weatherBonus.classic || 0)
      };

      let genre = "팝";
      if (final.bright >= 4 && final.fast >= 4 && final.emotion >= 4) genre = "K-pop, EDM";
      else if (final.calm >= 4 && final.emotion >= 4) genre = "발라드";
      else if (final.fast >= 4 && final.trendy >= 4) genre = "힙합, 일렉트로닉";
      else genre = "OST, R&B";

      document.getElementById("result").innerText = `추천 장르: ${genre}`;
      fetch(`/recommend_by_genre/?genre=${encodeURIComponent(genre)}`)
        .then(res => res.json())
        .then(data => {
          const recDiv = document.getElementById("recommend-songs");
          recDiv.innerHTML = "<div class='recommend-title'>추천 음악</div>";
          data.songs.forEach(song => {
            const div = document.createElement("div");
            div.className = "recommended-song";
            div.innerText = `${song.title} - ${song.artist} (${song.normalized_genre})`;
            recDiv.appendChild(div);
          });
        });
    });
}

function restartPreference() {
  current = 0;
  answers = Array(questions.length).fill(null);
  selectedSido = null;
  selectedGugun = null;

  document.getElementById("sido-select").selectedIndex = 0;
  document.getElementById("gugun-select").innerHTML = '<option value="">구/군을 선택하세요</option>';
  document.getElementById("gugun-select").disabled = true;

  document.getElementById("question-box").style.display = "block";
  document.getElementById("region-question").style.display = "none";
  document.getElementById("result").innerText = "";
  document.getElementById("recommend-songs").innerHTML = "";

  updateProgress();
  updateResultButtonState();
  loadQuestion();
}


// ✅ 초기 실행 함수
function initPreferenceTest() {
  populateSidoOptions(); // ✅ 시/도 목록 초기화
  current = 0;
  answers = Array(questions.length).fill(null);
  selectedSido = null;
  selectedGugun = null;

  document.getElementById("question-box").style.display = "block";
  document.getElementById("region-question").style.display = "none";
  document.getElementById("result").innerText = "";
  document.getElementById("recommend-songs").innerHTML = "";

  loadQuestion();
  updateProgress();
  updateResultButtonState();
}

// ✅ DOM 로딩 후 실행
document.addEventListener("DOMContentLoaded", initPreferenceTest);
>>>>>>> dayoung
