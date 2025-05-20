function showLyricsModal(title, lyrics) {
  const modal = document.getElementById("lyricsModal");
  const backdrop = document.getElementById("modalBackdropLyrics");
  document.getElementById("modalTitle").innerText = `🎵 ${title}`;
  document.getElementById("modalLyrics").innerText = lyrics;
  backdrop.style.display = "block";
  modal.style.display = "flex";
  setTimeout(() => {
    modal.classList.add("show");
  }, 10);
}

function closeModal() {
  const modal = document.getElementById("lyricsModal");
  const backdrop = document.getElementById("modalBackdropLyrics");
  modal.classList.remove("show");
  setTimeout(() => {
    modal.style.display = "none";
    backdrop.style.display = "none";
  }, 300);
}

document.addEventListener("keydown", function(e) {
  if (e.key === "Escape") {
    closeModal();
  }
});


const micBtn = document.getElementById('mic-btn'); 
const stopBtn = document.getElementById('stop-recognition');
const promptInput = document.getElementById('prompt-input');

let recognition = null;
let isManuallyStopped = false;

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
    promptInput.value = transcript;
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
    isManuallyStopped = false;  // 사용자가 중단한 경우 초기화
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


// 진섭이 추가 
