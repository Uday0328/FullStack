/* ================================================================
   ADMIN.JS — Admin dashboard interactions
   ================================================================ */

document.addEventListener('DOMContentLoaded', () => {

  // ── Auto-dismiss flash messages ────────────────────────────────
  const flashes = document.querySelectorAll('.flash');
  flashes.forEach(flash => {
    setTimeout(() => {
      flash.style.transition = 'opacity 0.4s ease';
      flash.style.opacity = '0';
      setTimeout(() => flash.remove(), 400);
    }, 5000);
  });

  // ── Delete confirmation dialogs ─────────────────────────────────
  document.querySelectorAll('[data-confirm]').forEach(btn => {
    btn.addEventListener('click', e => {
      const msg = btn.dataset.confirm || 'Are you sure?';
      if (!confirm(msg)) {
        e.preventDefault();
      }
    });
  });

  // ── Character counters for textareas ───────────────────────────
  document.querySelectorAll('textarea[maxlength]').forEach(textarea => {
    const maxLen = parseInt(textarea.getAttribute('maxlength'));
    const counter = document.createElement('div');
    counter.className = 'admin-form-hint';
    counter.style.textAlign = 'right';
    counter.textContent = `0 / ${maxLen}`;
    textarea.parentElement.appendChild(counter);

    textarea.addEventListener('input', () => {
      const len = textarea.value.length;
      counter.textContent = `${len} / ${maxLen}`;
      counter.style.color = len > maxLen * 0.9 ? '#ffb347' : '';
    });
  });

  // ── Sidebar active state ───────────────────────────────────────
  const currentPath = window.location.pathname;
  document.querySelectorAll('.sidebar-link').forEach(link => {
    if (link.getAttribute('href') === currentPath) {
      link.classList.add('active');
    }
  });

});
