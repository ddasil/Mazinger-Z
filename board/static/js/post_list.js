function handleScrap(button) {
  const postCard = button.closest('.post-card');
  const postId = postCard.dataset.postId;

  fetch(`/scrap/${postId}/`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCSRFToken(),
      'X-Requested-With': 'XMLHttpRequest'
    }
  })
  .then(response => {
    if (response.status === 403) {
      alert("로그인이 필요한 항목입니다.");
      return;
    }
    return response.json();
  })
  .then(data => {
    if (data.scrapped) {
      button.style.color = "#ff5e5e";
    } else {
      button.style.color = "#aaa";
    }
  });
}

function getCSRFToken() {
  const name = 'csrftoken';
  const cookies = document.cookie.split(';');
  for (let cookie of cookies) {
    cookie = cookie.trim();
    if (cookie.startsWith(name + '=')) {
      return decodeURIComponent(cookie.substring(name.length + 1));
    }
  }
  return '';
}