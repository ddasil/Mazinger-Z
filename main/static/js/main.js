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

        setTimeout(() => {
          car.style.display = "none";
        }, 1500);

        observer.unobserve(car);
      }
    });
  }, {
    threshold: 0.5,
  });

  observer.observe(car);
}

const eventData = {
  '2024-04-25': ['static/images/apple.png', 'static/images/apple.png'],
  '2024-04-28': ['static/images/apple.png'],
};

const calendarBox = document.getElementById('calendarBox');
const posterBox = document.getElementById('posterBox');

// 달력 생성
for (let d = 1; d <= 30; d++) {
  const dateStr = `2024-04-${d.toString().padStart(2, '0')}`;
  const day = document.createElement('div');
  day.classList.add('day');
  if (eventData[dateStr]) {
    day.classList.add('has-event');
  }
  day.textContent = d;
  day.addEventListener('click', () => {
    renderPosters(dateStr);
  });
  calendarBox.appendChild(day);
}

function renderPosters(dateStr) {
  posterBox.innerHTML = '';
  const posters = eventData[dateStr];
  if (posters) {
    posters.forEach(src => {
      const img = document.createElement('img');
      img.src = src;
      img.style.width = '150px';
      img.style.borderRadius = '8px';
      posterBox.appendChild(img);
    });
  } else {
    posterBox.innerHTML = '<h2>집에 가고 싶습니다.</h2>';
  }
}


document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("modal");
  const closeModalBtn = document.getElementById("closeModalBtn");
  const contactForm = document.getElementById("contactForm");
  const openModalBtn = document.getElementById("openModalBtn");
  const homeButton = document.querySelector('#contactForm button[type="submit"]');

  closeModalBtn.addEventListener("click", () => {
    modal.style.display = "none";
  });

  openModalBtn.addEventListener("click", () => {
    modal.style.display = "flex";
  });

  homeButton.addEventListener("click", (event) => {
    event.preventDefault();
    window.location.reload(); // ✅ 그냥 새로고침
  });

  contactForm.reset();
});


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