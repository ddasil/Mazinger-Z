const micBtn = document.getElementById('mic-btn');
const micIcon = micBtn.querySelector('i');
const promptInput = document.getElementById('prompt-input');
let recognition = null;
let isRecording = false;

micBtn.addEventListener('click', () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        alert("이 브라우저는 음성 인식을 지원하지 않습니다.");
        return;
    }

    if (!isRecording) {
        // 시작
        recognition = new SpeechRecognition();
        recognition.lang = 'ko-KR';
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;

        recognition.start();
        isRecording = true;
        micIcon.classList.remove('fa-microphone');
        micIcon.classList.add('fa-stop');

        recognition.onresult = (event) => {
            promptInput.value = event.results[0][0].transcript;
        };

        recognition.onerror = (event) => {
            alert("음성 인식 오류: " + event.error);
        };

        recognition.onend = () => {
            isRecording = false;
            micIcon.classList.remove('fa-stop');
            micIcon.classList.add('fa-microphone');
        };
    } else {
        // 중지
        recognition.stop();
        isRecording = false;
        micIcon.classList.remove('fa-stop');
        micIcon.classList.add('fa-microphone');
    }
});