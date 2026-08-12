/* ================================================================
   CONTACT.JS — AJAX contact form submission with toast notifications
   ================================================================ */

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('contact-form');
  if (!form) return;

  form.addEventListener('submit', handleContactSubmit);

  // Real-time validation clear
  form.querySelectorAll('.form-control').forEach(input => {
    input.addEventListener('input', () => {
      clearFieldError(input);
    });
  });
});

async function handleContactSubmit(e) {
  e.preventDefault();
  const form = e.target;
  const submitBtn = form.querySelector('#submit-btn');
  const btnText = submitBtn.querySelector('.btn-text');
  const btnSpinner = submitBtn.querySelector('.btn-spinner');

  // Clear previous errors
  clearAllErrors(form);

  // Client-side validation
  const name = form.querySelector('#contact-name').value.trim();
  const email = form.querySelector('#contact-email').value.trim();
  const message = form.querySelector('#contact-message').value.trim();

  let hasErrors = false;

  if (!name || name.length < 2) {
    showFieldError(form.querySelector('#contact-name'), 'Name must be at least 2 characters.');
    hasErrors = true;
  }

  if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    showFieldError(form.querySelector('#contact-email'), 'Please enter a valid email address.');
    hasErrors = true;
  }

  if (!message || message.length < 10) {
    showFieldError(form.querySelector('#contact-message'), 'Message must be at least 10 characters.');
    hasErrors = true;
  }

  if (hasErrors) return;

  // Show loading state
  submitBtn.disabled = true;
  if (btnText) btnText.textContent = 'Sending...';
  if (btnSpinner) btnSpinner.style.display = 'inline-block';

  try {
    const response = await fetch('/api/contact', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, message })
    });

    const data = await response.json();

    if (data.success) {
      showToast('✅', data.message || "Message sent! I'll get back to you soon.", 'success');
      form.reset();
    } else {
      const errors = data.errors || ['Something went wrong. Please try again.'];
      errors.forEach(err => showToast('❌', err, 'error'));
    }

  } catch (err) {
    console.error('Contact form error:', err);
    showToast('❌', 'Network error. Please check your connection and try again.', 'error');
  } finally {
    submitBtn.disabled = false;
    if (btnText) btnText.textContent = 'Send Message';
    if (btnSpinner) btnSpinner.style.display = 'none';
  }
}

function showFieldError(input, message) {
  input.classList.add('error');
  const errorEl = input.parentElement.querySelector('.form-error');
  if (errorEl) {
    errorEl.textContent = message;
    errorEl.classList.add('show');
  }
}

function clearFieldError(input) {
  input.classList.remove('error');
  const errorEl = input.parentElement.querySelector('.form-error');
  if (errorEl) errorEl.classList.remove('show');
}

function clearAllErrors(form) {
  form.querySelectorAll('.form-control').forEach(input => clearFieldError(input));
}

// ── Toast System ──────────────────────────────────────────────────

function getOrCreateToastContainer() {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }
  return container;
}

function showToast(icon, message, type = 'success', duration = 5000) {
  const container = getOrCreateToastContainer();
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.setAttribute('role', 'alert');
  toast.innerHTML = `
    <span class="toast-icon">${icon}</span>
    <span class="toast-message">${message}</span>
    <button class="toast-close" aria-label="Close notification">×</button>
  `;

  container.appendChild(toast);

  const closeBtn = toast.querySelector('.toast-close');
  const dismiss = () => {
    toast.style.animation = 'toast-out 0.3s ease forwards';
    setTimeout(() => toast.remove(), 300);
  };

  closeBtn.addEventListener('click', dismiss);
  setTimeout(dismiss, duration);
}

// Export showToast for other modules
window.showToast = showToast;
