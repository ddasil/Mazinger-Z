// ✅ 모달 및 폼 요소들 선언
let passwordModal, editModal;
let nicknameInput, birthdayInput, phoneInput, profileSelect, submitBtn;
let jsNicknameError, jsPhoneError;
let originalValues = {};  // 초기 입력값 저장 (변경 감지용)

// 🔓 비밀번호 확인 모달 열기
function openPasswordModal() {
  passwordModal.classList.add("show");
}

// 🔐 비밀번호 확인 모달 닫기
function closePasswordModal() {
  passwordModal.classList.remove("show");
}

// ✏️ 프로필 수정 모달 열기
function openModal() {
  editModal.classList.add("show");
  updateSubmitState();  // 수정 가능한 상태인지 체크
}

// 🔁 프로필 수정 모달 닫기
function closeModal() {
  editModal.classList.remove("show");
}

// 🧪 닉네임 유효성 검사 (한글, 영문, 숫자, 밑줄만 허용)
function validateNickname(nickname) {
  return /^[\w가-힣]+$/.test(nickname);
}

// ✅ 닉네임 중복 검사 (백엔드 AJAX)
function checkNicknameDuplicate(nickname, callback) {
  fetch(`/accounts/check_nickname/?nickname=${encodeURIComponent(nickname)}`)
    .then(res => res.json())
    .then(data => {
      nicknameInput.dataset.duplicate = data.duplicate;
      callback();
    })
    .catch(err => {
      console.error("중복 닉네임 확인 오류:", err);
      nicknameInput.dataset.duplicate = "false";
      callback();
    });
}

// 📱 전화번호 자동 포맷 (예: 010-1234-5678)
function formatPhoneNumber(value) {
  const cleaned = value.replace(/\D/g, "").slice(0, 11);  // 숫자만 추출, 11자리까지
  if (cleaned.length < 4) return cleaned;
  if (cleaned.length < 8) return `${cleaned.slice(0, 3)}-${cleaned.slice(3)}`;
  return `${cleaned.slice(0, 3)}-${cleaned.slice(3, 7)}-${cleaned.slice(7)}`;
}

// 📞 전화번호 유효성 검사
function validatePhoneNumber(콜) {
  return /^010-\d{4}-\d{4}$/.test(콜);
}

// 🔄 제출 버튼 활성화 여부 갱신
function updateSubmitState() {
  const currentValues = {
    nickname: nicknameInput.value.trim(),
    birthday: birthdayInput.value,
    phone: phoneInput.value.trim(),
    picture: profileSelect.value
  };

  // 어떤 필드든 값이 변경되었는지 확인
  const changed = Object.keys(currentValues).some(
    key => currentValues[key] !== originalValues[key]
  );

  // 유효성 검사
  const nicknameValid = validateNickname(currentValues.nickname);
  const phoneValid = validatePhoneNumber(currentValues.phone);
  const isDuplicate = nicknameInput.dataset.duplicate === "true";

  // 모든 조건 만족 시 수정 버튼 활성화
  submitBtn.disabled = !(nicknameValid && phoneValid && !isDuplicate && changed);

  // ⚠️ 닉네임 오류 표시
  if (!nicknameValid) {
    nicknameInput.style.border = "2px solid red";
    jsNicknameError.innerText = "한글, 영문, 숫자, 밑줄(_)만 사용할 수 있습니다.";
  } else if (isDuplicate) {
    nicknameInput.style.border = "2px solid red";
    jsNicknameError.innerText = "이미 사용 중인 닉네임입니다.";
  } else {
    nicknameInput.style.border = "2px solid green";
    jsNicknameError.innerText = "";
  }

  // ⚠️ 전화번호 오류 표시
  if (!phoneValid) {
    phoneInput.style.border = "2px solid red";
    jsPhoneError.innerText = "전화번호는 010-1234-5678 형식이어야 합니다.";
  } else {
    phoneInput.style.border = "2px solid green";
    jsPhoneError.innerText = "";
  }
}

// 🔐 비밀번호 확인 후 모달 열기
function verifyPassword() {
  const password = document.getElementById("confirmPassword").value;
  if (password.trim() === "") {
    alert("비밀번호를 입력하세요.");
    return;
  }

  // ✅ HTML의 <meta name="csrf-token"> 에서 CSRF 토큰 가져오기
  const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

  // ✅ 서버로 비밀번호 확인 요청 보내기
  fetch("verify_password/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken
    },
    body: JSON.stringify({ password: password })
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      document.getElementById("hiddenPassword").value = password;  // 다음 요청을 위해 저장
      closePasswordModal();
      openModal();
    } else {
      alert("비밀번호가 올바르지 않습니다.");
    }
  })
  .catch(err => {
    console.error("비밀번호 확인 오류:", err);
    alert("서버 오류가 발생했습니다.");
  });
}

// 🧩 전역 접근 가능하게 함수 등록
window.verifyPassword = verifyPassword;
window.openModal = openModal;
window.closeModal = closeModal;
window.closePasswordModal = closePasswordModal;

// ✅ 문서 로딩 완료 시 DOM 초기화
document.addEventListener("DOMContentLoaded", function () {
  // 🔗 DOM 요소 캐싱
  passwordModal = document.getElementById("passwordModal");
  editModal = document.getElementById("editModal");
  const openBtn = document.getElementById("openPasswordBtn");

  nicknameInput = document.getElementById("id_nickname");
  birthdayInput = document.getElementById("id_birthday");
  phoneInput = document.getElementById("id_phone_number");
  profileSelect = document.getElementById("id_profile_picture");
  submitBtn = document.getElementById("submit-btn");

  // 🧨 닉네임 오류 메시지 표시용 <p> 추가
  jsNicknameError = document.createElement("p");
  jsNicknameError.classList.add("error");
  jsNicknameError.style.color = "red";
  nicknameInput.insertAdjacentElement("afterend", jsNicknameError);

  // 🧨 전화번호 오류 메시지 표시용 <p> 추가
  jsPhoneError = document.createElement("p");
  jsPhoneError.classList.add("error");
  jsPhoneError.style.color = "red";
  phoneInput.insertAdjacentElement("afterend", jsPhoneError);

  // 🧾 현재 입력값 저장 (변경 감지용)
  originalValues = {
    nickname: nicknameInput.value.trim(),
    birthday: birthdayInput.value,
    phone: phoneInput.value.trim(),
    picture: profileSelect.value
  };

  // ✅ 수정 버튼 클릭 이벤트
  if (openBtn) openBtn.addEventListener("click", openPasswordModal);

  // ✅ 실시간 닉네임 변경 감지 및 중복 확인
  nicknameInput.addEventListener("input", () => {
    const value = nicknameInput.value.trim();
    if (!validateNickname(value)) {
      nicknameInput.dataset.duplicate = "false";
      updateSubmitState();
      return;
    }
    checkNicknameDuplicate(value, updateSubmitState);
  });

  // ✅ 생일 변경 시 상태 갱신
  birthdayInput.addEventListener("change", updateSubmitState);

  // ✅ 전화번호 입력 시 자동 포맷 + 상태 갱신
  phoneInput.addEventListener("input", () => {
    const formatted = formatPhoneNumber(phoneInput.value);
    phoneInput.value = formatted;
    updateSubmitState();
  });

  // ✅ 프로필 이미지 변경 시 미리보기 갱신
  profileSelect.addEventListener("change", () => {
    const previewImg = document.getElementById("profilePreview");
    previewImg.src = `/static/images/profiles/${profileSelect.value}`;
    updateSubmitState();
  });

  // ✅ 최초 로딩 시 닉네임 중복 여부 초기 검사
  checkNicknameDuplicate(nicknameInput.value.trim(), updateSubmitState);
});

const itemsPerPage = 10;
let allLyricsData = [];

// ✅ 전체 가사 목록 불러오기 + 초기 렌더링
function loadLyricsTable(page = 1) {
  const table = document.getElementById('user-lyrics-table');
  table.style.display = 'table';

  fetch('/accounts/user-generated-lyrics/')
    .then(res => res.json())
    .then(data => {
      allLyricsData = data.lyrics || [];
      renderLyricsPage(page);
    })
    .catch(error => {
      console.error('❌ 가사 불러오기 실패:', error);
    });
}

// ✅ 현재 페이지의 가사 목록 렌더링
function renderLyricsPage(page) {
  const tbody = document.getElementById('user-lyrics-body');
  tbody.innerHTML = '';

  const start = (page - 1) * itemsPerPage;
  const pageData = allLyricsData.slice(start, start + itemsPerPage);

  if (pageData.length === 0) {
    const row = document.createElement('tr');
    const cell = document.createElement('td');
    cell.colSpan = 3;
    cell.textContent = '등록된 가사가 없습니다.';
    row.appendChild(cell);
    tbody.appendChild(row);
    return;
  }

  pageData.forEach(item => {
    const row = document.createElement('tr');
    row.dataset.lyricId = item.id;  // ✅ 여기 추가!

    const selectTd = document.createElement('td');
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    selectTd.appendChild(checkbox);

    const titleTd = document.createElement('td');
    titleTd.textContent = `${item.prompt} (${item.style}/${item.language})`;

    const dateTd = document.createElement('td');
    dateTd.textContent = item.created_at || '날짜 없음';

    row.appendChild(selectTd);
    row.appendChild(titleTd);
    row.appendChild(dateTd);

    row.style.cursor = 'pointer';
    row.addEventListener('click', (e) => {
      if (e.target.tagName.toLowerCase() !== 'input') {
        sessionStorage.removeItem('modal_once_shown');
        window.location.href = `/lyricsgen/?open_id=${item.id}`;
      }
    });

    tbody.appendChild(row);
  });

  renderPagination(Math.ceil(allLyricsData.length / itemsPerPage), page);
  bindSelectAll();
}

// ✅ 페이지네이션 버튼 생성
function renderPagination(totalPages, currentPage) {
  const pagination = document.getElementById("pagination");
  pagination.innerHTML = '';

  const safeTotalPages = Math.max(totalPages, 1);
  for (let i = 1; i <= safeTotalPages; i++) {
    const button = document.createElement('button');
    button.textContent = i;
    if (i === currentPage) button.classList.add('active');
    button.addEventListener('click', () => renderLyricsPage(i));
    pagination.appendChild(button);
  }
}

// ✅ 체크박스 전체 선택 기능
function bindSelectAll() {
  const selectAllCheckbox = document.getElementById('select-all');
  if (selectAllCheckbox) {
    selectAllCheckbox.addEventListener('change', function () {
      const checkboxes = document.querySelectorAll('#user-lyrics-body input[type="checkbox"]');
      checkboxes.forEach(cb => cb.checked = this.checked);
    });
  }
}

// ✅ 버튼 클릭 시 동작
document.querySelectorAll('.mypage-link-btn').forEach(btn => {
  btn.addEventListener('click', function () {
    document.querySelectorAll('.mypage-link-btn').forEach(b => b.classList.remove('active'));
    this.classList.add('active');

    const type = this.dataset.type;
    if (type === "lyrics") {
      loadLyricsTable();
    } else {
      console.log("다른 버튼 클릭");
    }
  });
});

// ✅ 첫 페이지 진입 시 자동으로 "내가 만든 가사" 클릭
document.addEventListener("DOMContentLoaded", function () {
  const firstBtn = document.querySelector('.mypage-link-btn.lyrics-btn');
  if (firstBtn) firstBtn.click();
});

document.getElementById('delete-selected').addEventListener('click', function () {
  const checkedRows = document.querySelectorAll('#user-lyrics-body tr input[type="checkbox"]:checked');
  if (checkedRows.length === 0) {
    alert("삭제할 항목을 선택하세요.");
    return;
  }

  const idsToDelete = Array.from(checkedRows).map(cb => {
    return cb.closest('tr').dataset.lyricId;
  });

  if (!confirm("정말 삭제하시겠습니까?")) return;

  // ✅ CSRF 토큰 추출
  const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

  fetch('/accounts/delete-lyrics/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken
    },
    body: JSON.stringify({ ids: idsToDelete })
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      alert("삭제되었습니다.");
      loadLyricsTable();  // 목록 갱신
    } else {
      alert("삭제 실패. 다시 시도해주세요.");
    }
  })
  .catch(err => {
    console.error("❌ 삭제 요청 실패:", err);
  });
});
