// ----------------- NAVIGATION & CARD LOGIC -----------------
const navIcon = document.getElementById('navIcon');
const wrapper = document.querySelector('.wrapper');
const menuLinks = document.querySelectorAll('.side-menu li');

navIcon?.addEventListener('click', () => {
  wrapper.classList.toggle('nav-open');
});

menuLinks.forEach(link => {
  link.addEventListener('click', () => {
    const targetId = link.getAttribute('data-target');
    document.getElementById(targetId)?.scrollIntoView({ behavior: 'smooth' });
    wrapper.classList.remove('nav-open');
  });
});

document.addEventListener('click', (event) => {
  const isMenuOpen = wrapper.classList.contains('nav-open');
  const isNavIcon = event.target.closest('#navIcon');
  const isSideMenu = event.target.closest('.side-menu');
  if (isMenuOpen && !isNavIcon && !isSideMenu) {
    wrapper.classList.remove('nav-open');
  }
});

// ----------------- CARD SLIDER -----------------
const cards = document.querySelectorAll('.card');
let currentIndex = 0;

function updateCards(index) {
  cards.forEach(card => card.classList.remove('prev2', 'prev', 'active', 'next', 'next2'));
  if (cards[index]) cards[index].classList.add('active');
  if (cards[index - 1]) cards[index - 1].classList.add('prev');
  if (cards[index - 2]) cards[index - 2].classList.add('prev2');
  if (cards[index + 1]) cards[index + 1].classList.add('next');
  if (cards[index + 2]) cards[index + 2].classList.add('next2');
}
cards.forEach((card, index) => {
  card.addEventListener("click", () => {
    if (!card.classList.contains("active")) {
      currentIndex = index;
      updateCards(currentIndex);
      return;
    }
    const link = card.dataset.link;
    if (link) {
      const rect = card.getBoundingClientRect();
      const clone = card.cloneNode(true);
      clone.classList.add("expand");
      Object.assign(clone.style, {
        position: "fixed",
        top: `${rect.top}px`,
        left: `${rect.left}px`,
        width: `${rect.width}px`,
        height: `${rect.height}px`,
        margin: "0",
        zIndex: 9999,
        transform: "none",
        transition: "all 0.8s ease-in-out",
      });
      document.body.appendChild(clone);
      void clone.offsetWidth;
      Object.assign(clone.style, {
        top: "0", left: "0", width: "100vw", height: "100vh", transform: "scale(1.05)"
      });
      setTimeout(() => window.location.href = link, 800);
    }
  });
});
updateCards(currentIndex);

// ----------------- CAR ANIMATION -----------------
const car = document.getElementById("carTrigger");
const carSlideContent = document.getElementById("carSlideContent");

if (car && carSlideContent) {
  const observer = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        car.style.transition = "transform 1.5s ease-in-out, opacity 1.5s ease-in-out";
        car.style.transform = "translateX(-150vw) scale(0.4)";
        car.style.opacity = "0";
        carSlideContent.classList.add("active");
        setTimeout(() => car.style.display = "none", 1500);
        observer.unobserve(car);
      }
    });
  }, { threshold: 0.5 });
  observer.observe(car);
}

// ----------------- SECTION3 DYNAMIC CONTENT -----------------
document.querySelectorAll('.content-menu button').forEach(button => {
  button.addEventListener('click', () => {
    const type = button.dataset.type;
    const container = document.getElementById('section3Content');

    if (type === 'preference') {
      fetch('/preference/')
        .then(res => res.text())
        .then(html => {
          container.innerHTML = html;
          const script2 = document.createElement('script');
          script2.src = '/static/js/weather_score_map.js';
          document.body.appendChild(script2);
          const script3 = document.createElement('script');
          script3.src = '/static/js/preference.js';
          script3.onload = () => {
            if (typeof initPreferenceTest === 'function') initPreferenceTest();
            else console.error("❌ initPreferenceTest 함수가 정의되지 않았습니다.");
          };
          document.body.appendChild(script3);
        });
    } 
    
     // 노래퀴즈
    else if (type === 'quiz_song') {
      function loadQuizContent() {
        fetch('/quiz_song/')
          .then(res => res.text())
          .then(html => {
            container.innerHTML = html;

            const containerEl = container.querySelector('.quiz-container');
            const submitButton = container.querySelector('#submitAnswer');
            const retryButton = container.querySelector('#retryButton');
            const answerInput = container.querySelector('#answerInput');
            const lyricSnippet = container.querySelector('#lyricSnippet');

            if (!containerEl) return;

            const correctAnswer = containerEl.getAttribute('data-answer');
            const originalLyrics = containerEl.getAttribute('data-lyrics');
            let attemptCount = 0;

            function resetState() {
              attemptCount = 0;
              lyricSnippet.innerHTML = originalLyrics;
              lyricSnippet.style.color = '';
              answerInput.value = '';
              answerInput.style.display = 'inline-block';
              submitButton.style.display = 'inline-block';
              retryButton.style.display = 'none';
            }

            submitButton?.addEventListener('click', () => {
              const userAnswer = answerInput.value.trim().toLowerCase();
              attemptCount++;

              if (userAnswer === correctAnswer) {
                lyricSnippet.innerHTML = `${originalLyrics}<br><span style="color: lightgreen;">✅ 정답입니다! (${correctAnswer})</span>`;
                answerInput.style.display = 'none';
                submitButton.style.display = 'none';
                retryButton.style.display = 'inline-block';
              } else {
                if (attemptCount < 3) {
                  lyricSnippet.innerHTML = `${originalLyrics}<br><span style="color: salmon;">❌ 틀렸습니다! (${attemptCount}/3)</span>`;
                } else {
                  lyricSnippet.innerHTML = `${originalLyrics}<br><span style="color: salmon;">❌ 기회를 전부 소진했습니다.<br>정답 : ${correctAnswer}</span>`;
                  answerInput.style.display = 'none';
                  submitButton.style.display = 'none';
                  retryButton.style.display = 'inline-block';
                }
              }
            });

            retryButton?.addEventListener('click', (event) => {
              event.preventDefault();
              loadQuizContent();  // ✅ 새로 fetch해서 다시 로드
            });
          });
      }

      loadQuizContent(); // ✅ 최초 실행
    }

    // 노래퀴즈 끝
  });
});

// ----------------- CONTACT MODAL + GLITCH -----------------
document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("modal");
  const closeModalBtn = document.getElementById("closeModalBtn");
  const contactForm = document.getElementById("contactForm");
  const openModalBtn = document.getElementById("openModalBtn");
  const homeButton = document.querySelector('#contactForm button[type="submit"]');

  closeModalBtn?.addEventListener("click", () => modal.style.display = "none");
  openModalBtn?.addEventListener("click", () => modal.style.display = "flex");
  homeButton?.addEventListener("click", (event) => {
    event.preventDefault();
    window.location.reload();
  });
  contactForm?.reset();

  const $filter = document.querySelector('.svg-sprite');
  const $turb = $filter?.querySelector('#filter feTurbulence');
  if ($turb) {
    const turbVal = { val: 0.000001 };
    const turbValX = { val: 0.000001 };
    const glitchTimeline = () => {
      const timeline = gsap.timeline({
        repeat: -1,
        repeatDelay: 2,
        paused: true,
        onUpdate: () => $turb.setAttribute('baseFrequency', turbVal.val + ' ' + turbValX.val)
      });
      timeline
        .to(turbValX, { val: 0.5, duration: 0.1 })
        .to(turbVal, { val: 0.02, duration: 0.1 })
        .set(turbValX, { val: 0.000001 })
        .set(turbVal, { val: 0.000001 })
        .to(turbValX, { val: 0.4, duration: 0.2 }, 0.4)
        .to(turbVal, { val: 0.002, duration: 0.2 }, 0.4)
        .set(turbValX, { val: 0.000001 })
        .set(turbVal, { val: 0.000001 });

      return {
        start: () => timeline.play(0),
        stop: () => timeline.pause()
      };
    };

    const btnGlitch = glitchTimeline();
    document.querySelectorAll('.btn-glitch').forEach(button => {
      button.addEventListener('mouseenter', () => {
        button.classList.add('btn-glitch-active');
        btnGlitch.start();
      });
      button.addEventListener('mouseleave', () => {
        button.classList.remove('btn-glitch-active');
        btnGlitch.stop();
      });
    });
  }

  window.addEventListener('pageshow', function (event) {
    if (event.persisted) window.location.reload();
  });
});

// 진섭이출가
// ✅ 검색 버튼 클릭 시 /search/?q=... 로 이동
document.querySelectorAll('#searchBox').forEach(searchBox => {
  const input = searchBox.querySelector('input');
  const button = searchBox.querySelector('button');

  if (button && input) {
    // 클릭 시 검색
    button.addEventListener('click', function (e) {
      e.preventDefault();
      const query = input.value.trim();
      if (query) {
        window.location.href = `/search/?q=${encodeURIComponent(query)}`;
      }
    });

    // Enter 키 눌렀을 때도 검색
    input.addEventListener('keypress', function (e) {
      if (e.key === 'Enter') {
        e.preventDefault();
        button.click();
      }
    });
  }
});