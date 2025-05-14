document.addEventListener('DOMContentLoaded', function () {
  const replyButtons = document.querySelectorAll('.reply-btn');

  replyButtons.forEach(button => {
    button.addEventListener('click', function () {
      const commentId = this.getAttribute('data-id');
      const form = document.getElementById(`reply-form-${commentId}`);
      if (form) {
        form.classList.toggle('hidden');
      }
    });
  });
});
