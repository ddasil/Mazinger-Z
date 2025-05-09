// ✅ 질문 목록 정의
const questions = [
  "친구들이랑 모이면 내가 분위기를 주도하는 편이다.",
  "주말에는 야외 활동이나 운동을 즐긴다.",
  "영화나 드라마를 보면 쉽게 감정이입한다.",
  "최신 유행이나 신상 아이템을 궁금해하는 편이다.",
  "혼자 카페나 방에서 조용히 쉬는 걸 좋아한다.",
  "나는 즉흥적으로 계획을 바꾸는 걸 즐긴다.",
  "오래된 물건이나 빈티지 감성을 좋아한다."
];

let current = 0;
let answers = Array(questions.length).fill(null);
let selectedSido = null;
let selectedGugun = null;

// ✅ 버튼 색상 클래스 매핑
function getButtonClass(idx) {
  return ["strong-disagree", "disagree", "neutral", "agree", "strong-agree"][idx];
}

// ✅ 질문 출력
function loadQuestion() {
  const qBox = document.getElementById("question-box");
  const nextBtn = document.getElementById("next-btn");
  const resultBtn = document.getElementById("result-btn");

  if (!qBox) return;

  if (current >= questions.length) {
    // 문항이 끝나면 지역 선택 화면으로 전환
    qBox.style.display = "none";
    nextBtn.style.display = "none";
    resultBtn.style.display = "none";
    document.getElementById("region-question").style.display = "block";
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
  `;

  if (answers[current] !== null) {
    const selected = qBox.querySelectorAll("button")[answers[current] - 1];
    if (selected) selected.classList.add("selected");
  }

  document.getElementById("prev-btn").disabled = current === 0;
  nextBtn.style.display = current < questions.length - 1 ? "inline-block" : "none";
  resultBtn.style.display = "none";
}

// ✅ 답변 선택 시 다음 문항으로
function selectAnswer(value, btn) {
  answers[current] = value;
  document.querySelectorAll(".answer-buttons button").forEach(b => b.classList.remove("selected"));
  btn.classList.add("selected");

  setTimeout(() => {
    current++;
    loadQuestion();
    updateProgress();
  }, 300);
}

// ✅ 이전 문항 이동
function prevQuestion() {
  if (current > 0) {
    current--;
    document.getElementById("region-question").style.display = "none";
    document.getElementById("question-box").style.display = "block";
    document.getElementById("next-btn").style.display = "inline-block";
    loadQuestion();
    updateProgress();
  }
}

// ✅ 진행도 바 표시
function updateProgress() {
  const percent = (current / questions.length) * 100;
  document.getElementById("progress").style.width = `${percent}%`;
}

// ✅ 시/도 선택 시 구/군 목록 가져오기
function onSidoSelect(sido) {
  console.log("🔍 선택된 시도:", sido);

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
    })
    .catch(() => {
      alert("구/군 정보를 불러오는 데 실패했습니다.");
    });
}

// ✅ 구/군 선택 시 자동으로 결과 계산
function onGugunSelect(gugun) {
  selectedGugun = gugun;
  if (selectedSido && selectedGugun) calculateResult();
}

// ✅ 최종 점수 계산 → 장르 추천
function calculateResult() {
  if (!selectedSido || !selectedGugun) {
    alert("지역 선택이 누락되었습니다.");
    return;
  }

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
      if (final.bright >= 4 && final.fast >= 4 && final.emotion >= 4 && final.trendy >= 4) genre = "K-pop, EDM";
      else if (final.calm >= 4 && final.emotion >= 4 && final.classic >= 4) genre = "발라드, 재즈";
      else if (final.fast >= 4 && final.emotion <= 2 && final.trendy >= 4) genre = "힙합, 일렉트로닉";
      else if (final.calm >= 4 && final.emotion <= 2 && final.classic >= 4) genre = "클래식, 인디";
      else if (final.bright >= 4 && final.fast >= 4 && final.trendy >= 4 && final.emotion <= 2) genre = "록, 메탈";
      else genre = "OST, R&B";

      document.getElementById("result").innerText = `추천 장르: ${genre}`;
      localStorage.setItem("preferenceResult", genre);

      fetch(`/recommend_by_genre/?genre=${encodeURIComponent(genre)}`)
        .then(res => res.json())
        .then(data => {
          const recDiv = document.getElementById("recommend-songs");
          recDiv.innerHTML = "<div class='recommend-title'>추천 음악</div>";

          if (data.songs.length === 0) {
            recDiv.innerHTML += "<p>추천 곡이 없습니다.</p>";
            return;
          }

          data.songs.forEach(song => {
            const div = document.createElement("div");
            div.className = "recommended-song";
            div.innerText = `${song.title} - ${song.artist} (${song.normalized_genre})`;
            div.onclick = () => {
              window.location.href = `/music/?q=${encodeURIComponent(song.title + " " + song.artist)}`;
            };
            recDiv.appendChild(div);
          });
        });
    })
    .catch(err => {
      console.error("날씨 API 오류:", err);
      alert("날씨 정보를 불러오는 데 실패했습니다.");
    });
}

// ✅ preference 테스트 초기화 함수 (main.js에서 수동 호출)
function initPreferenceTest() {
  current = 0;
  answers = Array(questions.length).fill(null);
  loadQuestion();
  updateProgress();

  const sidoSelect = document.getElementById("sido-select");
  if (sidoSelect) {
    const sidos = [
      "서울특별시", "부산광역시", "대구광역시", "인천광역시", "광주광역시", "대전광역시",
      "울산광역시", "세종특별자치시", "경기도", "강원특별자치도", "충청북도", "충청남도",
      "전라북도", "전라남도", "경상북도", "경상남도", "제주특별자치도"
    ];
    sidos.forEach(sido => {
      const option = document.createElement("option");
      option.value = sido;
      option.textContent = sido;
      sidoSelect.appendChild(option);
    });
  }
}
