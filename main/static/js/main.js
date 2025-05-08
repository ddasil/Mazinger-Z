// // ✅ nav 메뉴 토글
// const navIcon = document.getElementById('navIcon');
// const wrapper = document.querySelector('.wrapper');
// const menuLinks = document.querySelectorAll('.side-menu li');

// navIcon.addEventListener('click', () => {
//   wrapper.classList.toggle('nav-open');
// });

// menuLinks.forEach(link => {
//   link.addEventListener('click', () => {
//     const targetId = link.getAttribute('data-target');
//     document.getElementById(targetId).scrollIntoView({ behavior: 'smooth' });
//     wrapper.classList.remove('nav-open');
//   });
// });

// document.addEventListener('click', (event) => {
//   const isMenuOpen = wrapper.classList.contains('nav-open');
//   const isNavIcon = event.target.closest('#navIcon');
//   const isSideMenu = event.target.closest('.side-menu');
//   if (isMenuOpen && !isNavIcon && !isSideMenu) {
//     wrapper.classList.remove('nav-open');
//   }
// });

// // ✅ 카드 회전 슬라이드
// const cards = document.querySelectorAll('.card');
// let currentIndex = 0;

// function updateCards(index) {
//   cards.forEach(card => card.classList.remove('prev2', 'prev', 'active', 'next', 'next2'));
//   if (cards[index]) cards[index].classList.add('active');
//   if (cards[index - 1]) cards[index - 1].classList.add('prev');
//   if (cards[index - 2]) cards[index - 2].classList.add('prev2');
//   if (cards[index + 1]) cards[index + 1].classList.add('next');
//   if (cards[index + 2]) cards[index + 2].classList.add('next2');
// }

// cards.forEach((card, index) => {
//   card.addEventListener("click", () => {
//     if (!card.classList.contains("active")) {
//       currentIndex = index;
//       updateCards(currentIndex);
//       return;
//     }

//     const link = card.dataset.link;
//     if (link) {
//       const rect = card.getBoundingClientRect();
//       const clone = card.cloneNode(true);
//       clone.classList.add("expand");
//       document.body.appendChild(clone);

//       clone.style.position = "fixed";
//       clone.style.top = `${rect.top}px`;
//       clone.style.left = `${rect.left}px`;
//       clone.style.width = `${rect.width}px`;
//       clone.style.height = `${rect.height}px`;
//       clone.style.margin = "0";
//       clone.style.zIndex = 9999;
//       clone.style.transform = "none";
//       clone.style.transition = "all 0.8s ease-in-out";

//       void clone.offsetWidth;

//       clone.style.top = "0";
//       clone.style.left = "0";
//       clone.style.width = "100vw";
//       clone.style.height = "100vh";
//       clone.style.transform = "scale(1.05)";

//       setTimeout(() => {
//         window.location.href = link;
//       }, 800);
//     }
//   });
// });
// updateCards(currentIndex);

// // ✅ section3: 자동차가 지나가고 콘텐츠 등장
// const carTrigger = document.getElementById("carTrigger");
// const carSlideContent = document.getElementById("carSlideContent");

// if (carTrigger && carSlideContent) {
//   const observer = new IntersectionObserver(entries => {
//     entries.forEach(entry => {
//       if (entry.isIntersecting) {
//         carTrigger.style.transform = "translateX(-150vw)";
//         carTrigger.style.opacity = 0;
//         carSlideContent.classList.add("active");
//       }
//     });
//   }, { threshold: 0.6 });

//   observer.observe(carTrigger);
// }

// // ✅ section3 메뉴 클릭 시 콘텐츠 로딩
// document.querySelectorAll('.content-menu button').forEach(button => {
//   button.addEventListener('click', () => {
//     const type = button.dataset.type;
//     const container = document.getElementById('section3Content');

//     if (type === 'preference') {
//       fetch('/preference/')
//       .then(res => res.text())
//       .then(html => {
//         container.innerHTML = html;
    
//         const script = document.createElement('script');
//         script.src = '/static/js/preference.js';
    
//         // ✅ preference.js 로딩 완료 후 초기화 함수 실행
//         script.onload = () => {
//           if (typeof initPreferenceTest === "function") {
//             initPreferenceTest();
//           } else {
//             console.error("⚠️ initPreferenceTest 함수가 정의되지 않았습니다.");
//           }
//         };
    
//         container.appendChild(script);
//       });
//     } else if (type === 'guess') {
//       container.innerHTML = `<h2>가사로 노래 제목 맞추기 Coming Soon...</h2>`;
//     }
//   });
// });

// // ✅ CONTACT 모달
// document.addEventListener("DOMContentLoaded", () => {
//   const modal = document.getElementById("modal");
//   const closeModalBtn = document.getElementById("closeModalBtn");
//   const contactForm = document.getElementById("contactForm");
//   const openModalBtn = document.getElementById("openModalBtn");
//   const homeButton = document.querySelector('#contactForm button[type="submit"]');

//   closeModalBtn?.addEventListener("click", () => {
//     modal.style.display = "none";
//   });

//   openModalBtn?.addEventListener("click", () => {
//     modal.style.display = "flex";
//   });

//   homeButton?.addEventListener("click", (event) => {
//     event.preventDefault();
//     window.location.reload();
//   });

//   contactForm?.reset();
// });

// // ✅ 글리치 버튼 효과
// document.addEventListener("DOMContentLoaded", () => {
//   const $filter = document.querySelector('.svg-sprite');
//   const $turb = $filter.querySelector('#filter feTurbulence');
//   const turbVal = { val: 0.000001 };
//   const turbValX = { val: 0.000001 };

//   const glitchTimeline = () => {
//     const timeline = gsap.timeline({
//       repeat: -1,
//       repeatDelay: 2,
//       paused: true,
//       onUpdate: () => {
//         $turb.setAttribute('baseFrequency', turbVal.val + ' ' + turbValX.val);
//       }
//     });

//     timeline
//       .to(turbValX, { val: 0.5, duration: 0.1 })
//       .to(turbVal, { val: 0.02, duration: 0.1 })
//       .set(turbValX, { val: 0.000001 })
//       .set(turbVal, { val: 0.000001 })
//       .to(turbValX, { val: 0.4, duration: 0.2 }, 0.4)
//       .to(turbVal, { val: 0.002, duration: 0.2 }, 0.4)
//       .set(turbValX, { val: 0.000001 })
//       .set(turbVal, { val: 0.000001 });

//     return {
//       start: () => timeline.play(0),
//       stop: () => timeline.pause()
//     };
//   };

//   const btnGlitch = glitchTimeline();

//   document.querySelectorAll('.btn-glitch').forEach(button => {
//     button.addEventListener('mouseenter', () => {
//       button.classList.add('btn-glitch-active');
//       btnGlitch.start();
//     });
//     button.addEventListener('mouseleave', () => {
//       button.classList.remove('btn-glitch-active');
//       btnGlitch.stop();
//     });
//   });

//   window.addEventListener('pageshow', function (event) {
//     if (event.persisted) {
//       window.location.reload();
//     }
//   });
// });


// ✅ nav 메뉴 토글
const navIcon = document.getElementById('navIcon');
const wrapper = document.querySelector('.wrapper');
const menuLinks = document.querySelectorAll('.side-menu li');

navIcon.addEventListener('click', () => {
  wrapper.classList.toggle('nav-open');
});

menuLinks.forEach(link => {
  link.addEventListener('click', () => {
    const targetId = link.getAttribute('data-target');
    document.getElementById(targetId).scrollIntoView({ behavior: 'smooth' });
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

// ✅ 카드 회전 슬라이드
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
      document.body.appendChild(clone);

      clone.style.position = "fixed";
      clone.style.top = `${rect.top}px`;
      clone.style.left = `${rect.left}px`;
      clone.style.width = `${rect.width}px`;
      clone.style.height = `${rect.height}px`;
      clone.style.margin = "0";
      clone.style.zIndex = 9999;
      clone.style.transform = "none";
      clone.style.transition = "all 0.8s ease-in-out";

      void clone.offsetWidth;

      clone.style.top = "0";
      clone.style.left = "0";
      clone.style.width = "100vw";
      clone.style.height = "100vh";
      clone.style.transform = "scale(1.05)";

      setTimeout(() => {
        window.location.href = link;
      }, 800);
    }
  });
});
updateCards(currentIndex);

// ✅ section3: 자동차가 지나가고 콘텐츠 등장
const carTrigger = document.getElementById("carTrigger");
const carSlideContent = document.getElementById("carSlideContent");

if (carTrigger && carSlideContent) {
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        carTrigger.style.transform = "translateX(-150vw)";
        carTrigger.style.opacity = 0;
        carSlideContent.classList.add("active");
      }
    });
  }, { threshold: 0.6 });

  observer.observe(carTrigger);
}

// ✅ section3 메뉴 클릭 시 콘텐츠 로딩
document.querySelectorAll('.content-menu button').forEach(button => {
  button.addEventListener('click', () => {
    const type = button.dataset.type;
    const container = document.getElementById('section3Content');

    if (type === 'preference') {
      // 👉 서버에서 preference.html 내용을 받아오기
      fetch('/preference/')
        .then(res => res.text())
        .then(html => {
          // 👉 받은 HTML을 섹션3에 삽입
          container.innerHTML = html;

          // 👉 preference.js 파일을 동적으로 로딩 (기존 script 태그는 작동 안 함)
          const script = document.createElement('script');
          script.src = '/static/js/preference.js';

          // ✅ 스크립트가 로드된 후 함수 수동 실행
          script.onload = () => {
            if (typeof initPreferenceTest === 'function') {
              initPreferenceTest();  // ✅ 직접 호출
            } else {
              console.error("⚠️ initPreferenceTest 함수가 정의되지 않았습니다.");
            }
          };

          // ⚠️ container가 아닌 document.body에 추가해야 브라우저가 실행 인식함
          document.body.appendChild(script);
        });
    } else if (type === 'guess') {
      container.innerHTML = `<h2>가사로 노래 제목 맞추기 Coming Soon...</h2>`;
    }
  });
});

// ✅ CONTACT 모달
document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("modal");
  const closeModalBtn = document.getElementById("closeModalBtn");
  const contactForm = document.getElementById("contactForm");
  const openModalBtn = document.getElementById("openModalBtn");
  const homeButton = document.querySelector('#contactForm button[type="submit"]');

  closeModalBtn?.addEventListener("click", () => {
    modal.style.display = "none";
  });

  openModalBtn?.addEventListener("click", () => {
    modal.style.display = "flex";
  });

  homeButton?.addEventListener("click", (event) => {
    event.preventDefault();
    window.location.reload();
  });

  contactForm?.reset();
});

// ✅ 글리치 버튼 효과
document.addEventListener("DOMContentLoaded", () => {
  const $filter = document.querySelector('.svg-sprite');
  const $turb = $filter.querySelector('#filter feTurbulence');
  const turbVal = { val: 0.000001 };
  const turbValX = { val: 0.000001 };

  const glitchTimeline = () => {
    const timeline = gsap.timeline({
      repeat: -1,
      repeatDelay: 2,
      paused: true,
      onUpdate: () => {
        $turb.setAttribute('baseFrequency', turbVal.val + ' ' + turbValX.val);
      }
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

  window.addEventListener('pageshow', function (event) {
    if (event.persisted) {
      window.location.reload();
    }
  });
});
