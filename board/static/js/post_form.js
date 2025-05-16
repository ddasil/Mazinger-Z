document.addEventListener('DOMContentLoaded', function () {
  const openBtn = document.getElementById('openLovelistModal');
  const closeBtn = document.getElementById('closeLovelistModal');
  const modal = document.getElementById('lovelistModal');
  const backdrop = document.getElementById('lovelistModalBackdrop');
  const preview = document.getElementById('selectedSongsPreview');

  if (!openBtn || !closeBtn || !modal || !backdrop || !preview) {
    console.warn("❗ 요소 중 하나 이상을 찾을 수 없습니다.");
    return;
  }

  // ✅ 팝업 열기 - 기존 선택된 곡 체크 유지
  openBtn.addEventListener('click', () => {
    modal.classList.add('show');
    backdrop.classList.add('show');

    // 선택된 곡 ID들 수집
    const checkedIds = new Set();
    preview.querySelectorAll('li[data-id]').forEach(li => {
      checkedIds.add(li.dataset.id);
    });

    // 다시 체크 상태 반영
    modal.querySelectorAll('input[name="songs"]').forEach(cb => {
      cb.checked = checkedIds.has(cb.value);
    });
  });

  // ✅ 팝업 닫기 + 선택된 곡 미리보기 갱신
  closeBtn.addEventListener('click', () => {
    modal.classList.remove('show');
    backdrop.classList.remove('show');

    const checkboxes = modal.querySelectorAll('input[name="songs"]:checked');
    const selectedMap = new Map(); // 중복 방지

    if (checkboxes.length === 0) {
      preview.innerHTML = `<p class="no-selection">선택된 곡이 없습니다.</p>`;
      return;
    }

    let html = `<p><strong>선택된 곡:</strong></p><ul>`;

    checkboxes.forEach(cb => {
      const songId = cb.value;
      const label = cb.parentElement.textContent.trim();

      if (!selectedMap.has(songId)) {
        selectedMap.set(songId, label);
        html += `
          <li data-id="${songId}">
            ${label}
            <button type="button" class="remove-song" data-id="${songId}" style="margin-left:10px;">❌</button>
          </li>
        `;
      }
    });

    html += `</ul>`;
    preview.innerHTML = html;

    // ✅ 선택 취소 버튼 기능 연결
    preview.querySelectorAll('.remove-song').forEach(button => {
      button.addEventListener('click', (e) => {
        const id = e.target.dataset.id;
        // 체크박스도 해제
        const checkbox = modal.querySelector(`input[name="songs"][value="${id}"]`);
        if (checkbox) checkbox.checked = false;

        // 미리보기에서도 제거
        e.target.closest('li').remove();

        // 항목 없으면 안내 문구 출력
        if (preview.querySelectorAll('li').length === 0) {
          preview.innerHTML = `<p class="no-selection">선택된 곡이 없습니다.</p>`;
        }
      });
    });
  });

  // ✅ 백드롭 클릭 시도 팝업 닫기
  backdrop.addEventListener('click', () => {
    modal.classList.remove('show');
    backdrop.classList.remove('show');
  });
});
