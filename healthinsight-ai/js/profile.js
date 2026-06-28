/* ============================================================
   profile.js — Profile Page Logic
   ============================================================ */
'use strict';

document.addEventListener('DOMContentLoaded', () => {

  /* ── Score History Bars ──────────────────────────────────────── */
  const scoreHistory = [
    { date: 'Jan 2025', score: 64 },
    { date: 'Feb 2025', score: 66 },
    { date: 'Mar 2025', score: 69 },
    { date: 'Apr 2025', score: 72 },
    { date: 'May 2025', score: 78 },
    { date: 'Jun 2025', score: 82 },
  ];

  const histList = document.getElementById('scoreHistoryList');
  if (histList) {
    histList.innerHTML = scoreHistory.map(s => `
      <div class="score-history-item">
        <span class="score-history-date">${s.date}</span>
        <div class="score-history-bar">
          <div class="score-history-fill" data-width="${s.score}"
               style="width:0%;transition:width 1s ease"></div>
        </div>
        <span class="score-history-value">${s.score}</span>
      </div>
    `).join('');

    setTimeout(() => {
      histList.querySelectorAll('.score-history-fill').forEach(el => {
        el.style.width = el.dataset.width + '%';
      });
    }, 400);
  }

  /* ── Change Password Modal ───────────────────────────────────── */
  const changePwBtn = document.getElementById('changePasswordBtn');
  if (changePwBtn) {
    changePwBtn.addEventListener('click', () => {
      window.HI.Modal.open(`
        <h3 style="margin-bottom:8px">Change Password</h3>
        <p style="margin-bottom:24px;font-size:.9rem">Enter your current and new password below.</p>
        <div class="form-group">
          <label class="form-label">Current Password</label>
          <input type="password" class="form-control" id="cpCurrent" placeholder="••••••••">
        </div>
        <div class="form-group">
          <label class="form-label">New Password</label>
          <input type="password" class="form-control" id="cpNew" placeholder="••••••••">
        </div>
        <div class="form-group">
          <label class="form-label">Confirm New Password</label>
          <input type="password" class="form-control" id="cpConfirm" placeholder="••••••••">
        </div>
        <button class="btn btn-primary w-full" id="savePasswordBtn" style="justify-content:center">
          <i class="fas fa-lock"></i> Update Password
        </button>
      `, {
        onOpen: (modal) => {
          modal.querySelector('#savePasswordBtn').addEventListener('click', () => {
            const np = modal.querySelector('#cpNew').value;
            const nc = modal.querySelector('#cpConfirm').value;
            if (np !== nc) {
              window.HI.Toast.error('New passwords do not match.');
              return;
            }
            if (np.length < 8) {
              window.HI.Toast.error('Password must be at least 8 characters.');
              return;
            }
            window.HI.Toast.success('Password updated successfully!');
            window.HI.Modal.close();
          });
        }
      });
    });
  }

  /* ── Edit Info inline ───────────────────────────────────────── */
  document.querySelectorAll('.info-edit-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const field = btn.closest('.info-field');
      const valEl = field.querySelector('.info-value');
      const currentText = valEl.firstChild.textContent.trim();
      const fieldName = field.querySelector('.info-label').textContent;

      window.HI.Modal.open(`
        <h3 style="margin-bottom:8px">Edit ${fieldName}</h3>
        <div class="form-group" style="margin-top:20px">
          <input type="text" class="form-control" id="editFieldInput" value="${currentText}">
        </div>
        <div style="display:flex;gap:12px;margin-top:4px">
          <button class="btn btn-outline w-full" id="cancelEdit" style="justify-content:center">Cancel</button>
          <button class="btn btn-primary w-full" id="saveEdit" style="justify-content:center">
            <i class="fas fa-check"></i> Save
          </button>
        </div>
      `, {
        onOpen: (modal) => {
          modal.querySelector('#cancelEdit').addEventListener('click', window.HI.Modal.close);
          modal.querySelector('#saveEdit').addEventListener('click', () => {
            const newVal = modal.querySelector('#editFieldInput').value;
            // Update displayed value (keep icon if any)
            const icon = valEl.querySelector('i');
            valEl.textContent = newVal;
            if (icon) valEl.prepend(icon);
            window.HI.Toast.success(`${fieldName} updated!`);
            window.HI.Modal.close();
          });
        }
      });
    });
  });

  /* ── Avatar upload ───────────────────────────────────────────── */
  const avatarBtn = document.getElementById('avatarEdit');
  const avatarEl  = document.getElementById('profileAvatarBig');
  if (avatarBtn && avatarEl) {
    avatarBtn.addEventListener('click', () => {
      const input = document.createElement('input');
      input.type  = 'file';
      input.accept = 'image/*';
      input.onchange = (e) => {
        const file = e.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = (ev) => {
          avatarEl.innerHTML = `<img src="${ev.target.result}" alt="Avatar">`;
          window.HI.Toast.success('Profile picture updated!');
        };
        reader.readAsDataURL(file);
      };
      input.click();
    });
  }

  /* ── Logout ──────────────────────────────────────────────────── */
  const logoutBtn = document.getElementById('logoutBtn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
      window.HI.Modal.open(`
        <div style="text-align:center;padding:12px 0">
          <div style="width:64px;height:64px;border-radius:50%;background:#FEE2E2;
                      display:flex;align-items:center;justify-content:center;
                      margin:0 auto 20px;font-size:1.8rem;color:var(--danger)">
            <i class="fas fa-right-from-bracket"></i>
          </div>
          <h3 style="margin-bottom:8px">Sign Out?</h3>
          <p style="margin-bottom:28px;font-size:.9rem">You'll be redirected to the login page.</p>
          <div style="display:flex;gap:12px">
            <button class="btn btn-outline w-full" id="cancelLogout" style="justify-content:center">Cancel</button>
            <button class="btn btn-danger w-full" id="confirmLogout" style="justify-content:center">
              <i class="fas fa-right-from-bracket"></i> Sign Out
            </button>
          </div>
        </div>
      `, {
        onOpen: (modal) => {
          modal.querySelector('#cancelLogout').addEventListener('click', window.HI.Modal.close);
          modal.querySelector('#confirmLogout').addEventListener('click', () => {
            localStorage.removeItem('hi-user');
            window.location.href = 'login.html';
          });
        }
      });
    });
  }
});
