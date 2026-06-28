/* ============================================================
   login.js — Login Page Logic
   ============================================================ */
'use strict';

document.addEventListener('DOMContentLoaded', () => {
  const form      = document.getElementById('loginForm');
  const emailIn   = document.getElementById('loginEmail');
  const passIn    = document.getElementById('loginPassword');
  const passToggle= document.getElementById('passToggle');
  const rememberCb= document.getElementById('rememberMe');
  const errMsg    = document.getElementById('loginError');
  const submitBtn = form.querySelector('[type="submit"]');

  /* ── Password Toggle ─────── */
  passToggle.addEventListener('click', () => {
    const show = passIn.type === 'password';
    passIn.type = show ? 'text' : 'password';
    passToggle.querySelector('i').className = `fas fa-eye${show ? '-slash' : ''}`;
  });

  /* ── Validation ──────────── */
  const validateField = (el, condition, msg) => {
    const err = el.closest('.form-group').querySelector('.form-error');
    if (!condition) {
      el.classList.add('error');
      if (err) err.textContent = msg;
      return false;
    }
    el.classList.remove('error');
    if (err) err.textContent = '';
    return true;
  };

  emailIn.addEventListener('blur', () =>
    validateField(emailIn, /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailIn.value), 'Please enter a valid email.'));
  passIn.addEventListener('blur', () =>
    validateField(passIn, passIn.value.length >= 6, 'Password must be at least 6 characters.'));

  /* ── Submit ──────────────── */
  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const v1 = validateField(emailIn, /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailIn.value), 'Please enter a valid email.');
    const v2 = validateField(passIn, passIn.value.length >= 6, 'Password must be at least 6 characters.');
    if (!v1 || !v2) return;

    // Simulate async login
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<div class="spinner spinner-sm"></div>&nbsp;Signing in…';

    await new Promise(r => setTimeout(r, 1600));

    // Demo: accept any valid email/pass combo
    const demoEmail = 'demo@healthinsight.ai';
    const demoPass  = 'demo1234';

    if (emailIn.value === demoEmail && passIn.value === demoPass) {
      if (rememberCb.checked) localStorage.setItem('hi-user', JSON.stringify({ email: emailIn.value }));
      window.HI.Toast.success('Welcome back! Redirecting…');
      setTimeout(() => window.location.href = 'dashboard.html', 1200);
    } else {
      // Accept any credentials for demo purposes
      localStorage.setItem('hi-user', JSON.stringify({ email: emailIn.value }));
      window.HI.Toast.success('Login successful! Redirecting to dashboard…');
      setTimeout(() => window.location.href = 'dashboard.html', 1200);
    }

    submitBtn.disabled = false;
    submitBtn.innerHTML = '<i class="fas fa-arrow-right-to-bracket"></i> Sign In';
  });

  /* ── Forgot Password Modal ── */
  const forgotLink = document.getElementById('forgotPassword');
  if (forgotLink) {
    forgotLink.addEventListener('click', (e) => {
      e.preventDefault();
      window.HI.Modal.open(`
        <h3 style="margin-bottom:8px">Reset Password</h3>
        <p style="margin-bottom:24px;font-size:.9rem">Enter your email and we'll send a reset link.</p>
        <div class="form-group">
          <label class="form-label">Email Address</label>
          <div class="input-group">
            <i class="fas fa-envelope input-icon"></i>
            <input type="email" class="form-control" id="resetEmail" placeholder="you@example.com">
          </div>
        </div>
        <button class="btn btn-primary w-full" id="sendResetBtn" style="justify-content:center">
          <i class="fas fa-paper-plane"></i> Send Reset Link
        </button>
      `, {
        onOpen: (modal) => {
          modal.querySelector('#sendResetBtn').addEventListener('click', () => {
            window.HI.Toast.success('Reset link sent! Check your inbox.');
            window.HI.Modal.close();
          });
        }
      });
    });
  }

  /* ── Pre-fill from remember ── */
  const saved = JSON.parse(localStorage.getItem('hi-user') || 'null');
  if (saved && saved.email) {
    emailIn.value = saved.email;
    if (rememberCb) rememberCb.checked = true;
  }
});
