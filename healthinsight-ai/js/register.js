/* ============================================================
   register.js — Registration Page Logic
   ============================================================ */
'use strict';

document.addEventListener('DOMContentLoaded', () => {
  const form       = document.getElementById('registerForm');
  const passIn     = document.getElementById('regPassword');
  const passConfirm= document.getElementById('regPassConfirm');
  const passToggle = document.getElementById('passToggle');
  const confToggle = document.getElementById('confToggle');
  const strengthBar= document.getElementById('strengthBar');
  const strengthTxt= document.getElementById('strengthText');
  const submitBtn  = form.querySelector('[type="submit"]');

  /* ── Password Toggles ───────── */
  const addToggle = (btn, input) => {
    btn.addEventListener('click', () => {
      const show = input.type === 'password';
      input.type = show ? 'text' : 'password';
      btn.querySelector('i').className = `fas fa-eye${show ? '-slash' : ''}`;
    });
  };
  addToggle(passToggle, passIn);
  addToggle(confToggle, passConfirm);

  /* ── Password Strength ────────── */
  const calcStrength = (p) => {
    let score = 0;
    if (p.length >= 8)  score++;
    if (p.length >= 12) score++;
    if (/[A-Z]/.test(p)) score++;
    if (/[0-9]/.test(p)) score++;
    if (/[^A-Za-z0-9]/.test(p)) score++;
    return score;
  };

  const strengthLabels = ['', 'Very Weak', 'Weak', 'Fair', 'Strong', 'Very Strong'];
  const strengthColors = ['', '#EF4444', '#F97316', '#FACC15', '#22C55E', '#16A34A'];

  passIn.addEventListener('input', () => {
    const score = calcStrength(passIn.value);
    const pct   = (score / 5) * 100;
    strengthBar.style.width = pct + '%';
    strengthBar.style.background = strengthColors[score] || '#e2e8f0';
    strengthTxt.textContent = passIn.value ? strengthLabels[score] || '' : '';
    strengthTxt.style.color = strengthColors[score] || 'inherit';
  });

  /* ── Validation Helpers ──────── */
  const setError = (input, msg) => {
    input.classList.add('error');
    const err = input.closest('.form-group').querySelector('.form-error');
    if (err) err.textContent = msg;
    return false;
  };
  const clearError = (input) => {
    input.classList.remove('error');
    const err = input.closest('.form-group').querySelector('.form-error');
    if (err) err.textContent = '';
    return true;
  };

  const rules = {
    regName:        (v) => v.trim().length >= 2 ? null : 'Full name must be at least 2 characters.',
    regEmail:       (v) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v) ? null : 'Please enter a valid email.',
    regPhone:       (v) => /^\+?[\d\s\-()]{7,15}$/.test(v) ? null : 'Please enter a valid phone number.',
    regAge:         (v) => (parseInt(v) >= 1 && parseInt(v) <= 120) ? null : 'Age must be between 1 and 120.',
    regGender:      (v) => v ? null : 'Please select your gender.',
    regPassword:    (v) => v.length >= 8 ? null : 'Password must be at least 8 characters.',
    regPassConfirm: (v) => v === passIn.value ? null : 'Passwords do not match.',
  };

  Object.keys(rules).forEach(id => {
    const el = document.getElementById(id);
    if (!el) return;
    el.addEventListener('blur', () => {
      const err = rules[id](el.value);
      err ? setError(el, err) : clearError(el);
    });
  });

  /* ── Submit ──────────────────── */
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    let valid = true;

    Object.keys(rules).forEach(id => {
      const el = document.getElementById(id);
      if (!el) return;
      const err = rules[id](el.value);
      if (err) { setError(el, err); valid = false; }
      else clearError(el);
    });

    const terms = document.getElementById('acceptTerms');
    if (terms && !terms.checked) {
      window.HI.Toast.warning('Please accept the Terms & Conditions.');
      valid = false;
    }

    if (!valid) return;

    submitBtn.disabled = true;
    submitBtn.innerHTML = '<div class="spinner spinner-sm"></div>&nbsp;Creating Account…';

    await new Promise(r => setTimeout(r, 2000));

    window.HI.Toast.success('Account created successfully!');
    setTimeout(() => window.location.href = 'login.html', 1200);
  });
});
