// ✅ 대댓글 버튼 클릭 시 해당 댓글의 답글 폼을 토글
document.addEventListener('DOMContentLoaded', function () {
  const replyButtons = document.querySelectorAll('.reply-btn');

  replyButtons.forEach(button => {
    button.addEventListener('click', function () {
      const commentId = this.getAttribute('data-id');
      const form = document.getElementById(`reply-form-${commentId}`);
      if (form) {
        form.classList.toggle('hidden');  // 보이기/숨기기 토글
      }
    });
  });

  // ✅ 비로그인 시 글쓰기 버튼 클릭 시 로그인 유도
  const writeBtn = document.querySelector('.btn-write.not-logged-in-write');
  if (writeBtn) {
    writeBtn.addEventListener('click', function (e) {
      e.preventDefault();
      const confirmLogin = confirm("로그인이 필요한 기능입니다. 로그인하시겠습니까?");
      if (confirmLogin) {
        window.location.href = "/accounts/login/?next=" + encodeURIComponent(window.location.pathname);
      }
    });
  }

  // ✅ 비로그인 시 스크랩 버튼 클릭 시 로그인 유도
  const scrapButtons = document.querySelectorAll('.btn-scrap.not-logged-in');
  scrapButtons.forEach(button => {
    button.addEventListener('click', function (e) {
      e.preventDefault();
      const confirmLogin = confirm("로그인이 필요한 기능입니다. 로그인하시겠습니까?");
      if (confirmLogin) {
        window.location.href = "/accounts/login/?next=" + encodeURIComponent(window.location.pathname);
      }
    });
  });
});
