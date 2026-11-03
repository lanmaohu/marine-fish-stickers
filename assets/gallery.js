if (new URLSearchParams(location.search).has('preview')) document.body.classList.add('preview');

document.querySelectorAll('.backgrounds button').forEach(button => {
  button.addEventListener('click', () => {
    document.body.dataset.bg = button.dataset.bg;
    document.querySelectorAll('.backgrounds button').forEach(other => {
      const active = other === button;
      other.classList.toggle('active', active);
      other.setAttribute('aria-pressed', String(active));
    });
  });
});

document.querySelectorAll('.compare').forEach(button => {
  button.addEventListener('click', () => {
    const card = button.closest('.card');
    const img = card.querySelector('.fish');
    const showReference = !card.classList.contains('is-reference');
    card.classList.toggle('is-reference', showReference);
    img.src = showReference ? img.dataset.reference : img.dataset.sticker;
    img.alt = card.dataset.name + (showReference ? '参考照片' : '贴纸');
    button.textContent = showReference ? '返回贴纸' : '看参考照片';
    button.setAttribute('aria-pressed', String(showReference));
  });
});

const search = document.getElementById('search');
search.addEventListener('input', () => {
  const query = search.value.trim().toLowerCase();
  let count = 0;
  document.querySelectorAll('.card').forEach(card => {
    const visible = card.dataset.search.toLowerCase().includes(query);
    card.hidden = !visible;
    count += Number(visible);
  });
  document.querySelector('.empty').hidden = count !== 0;
  document.getElementById('result-count').textContent = `${count} 种鱼`;
});

// Browsers treat local file downloads differently; offer the original in a new tab.
if (location.protocol === 'file:') {
  document.querySelectorAll('a[download]').forEach(link => {
    link.removeAttribute('download');
    link.target = '_blank';
    link.rel = 'noopener';
    if (link.classList.contains('single-download')) link.textContent = '打开 PNG ↗';
  });
}
