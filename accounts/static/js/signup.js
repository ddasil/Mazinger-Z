document.addEventListener("DOMContentLoaded", function () {
  const usernameInput = document.getElementById("id_username");
  const checkMessage = document.getElementById("username-check");
  const passwordInput = document.getElementById("id_password1");
  const passwordCheck = document.getElementById("password-check");
  const phoneInput = document.getElementById("id_phone_number");

  // ✅ 전화번호 자동 하이픈 및 유효성
  function formatPhoneNumber(value) {
    const cleaned = value.replace(/\D/g, "").slice(0, 11);
    if (cleaned.length < 4) return cleaned;
    if (cleaned.length < 8) return `${cleaned.slice(0, 3)}-${cleaned.slice(3)}`;
    return `${cleaned.slice(0, 3)}-${cleaned.slice(3, 7)}-${cleaned.slice(7, 11)}`;
  }

  function validatePhoneNumber(phone) {
    return /^010-\d{4}-\d{4}$/.test(phone);
  }

  if (phoneInput) {
    phoneInput.addEventListener("input", () => {
      phoneInput.value = formatPhoneNumber(phoneInput.value);

      if (validatePhoneNumber(phoneInput.value)) {
        phoneInput.style.border = "2px solid lightgreen";
      } else {
        phoneInput.style.border = "2px solid red";
      }
    });
  }

  // ✅ 아이디 중복 체크
  if (usernameInput) {
    usernameInput.addEventListener("input", function () {
      const username = usernameInput.value.trim();
      if (!username) {
        checkMessage.textContent = "";
        return;
      }

      fetch(`/accounts/check_username/?username=${encodeURIComponent(username)}`)
        .then(res => res.json())
        .then(data => {
          if (data.available) {
            checkMessage.textContent = "사용 가능한 아이디입니다.";
            checkMessage.style.color = "lightgreen";
          } else {
            checkMessage.textContent = "이미 사용 중인 아이디입니다.";
            checkMessage.style.color = "red";
          }
        })
        .catch(err => {
          checkMessage.textContent = "서버 오류";
          checkMessage.style.color = "orange";
        });
    });
  }

  // ✅ 비밀번호 조건 검사 (JS 실시간 피드백)
  if (passwordInput) {
    passwordInput.addEventListener("input", function () {
      const pw = passwordInput.value;
      if (pw.length < 8) {
        passwordCheck.textContent = "비밀번호는 8자 이상이어야 합니다.";
        passwordCheck.style.color = "red";
      } else if (/^\d+$/.test(pw)) {
        passwordCheck.textContent = "숫자만으로는 사용할 수 없습니다.";
        passwordCheck.style.color = "red";
      } else {
        passwordCheck.textContent = "사용 가능한 비밀번호입니다.";
        passwordCheck.style.color = "lightgreen";
      }
    });
  }
});