/* ============================================================
   dashboard.js — Main Dashboard Logic
   ============================================================ */
'use strict';

document.addEventListener('DOMContentLoaded', () => {

  /* ── Chart Bars ─────────────────────────────────────────────── */
  const weekData    = [68, 72, 69, 75, 78, 80, 82];
  const weekLabels  = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  const chartArea   = document.getElementById('weeklyChart');

  if (chartArea) {
    const maxH = 160;
    const maxVal = Math.max(...weekData);

    chartArea.innerHTML = weekData.map((v, i) => `
      <div class="chart-bar-wrap">
        <div class="chart-bar" style="height:${(v / maxVal) * maxH}px"
             title="Health Score: ${v}"></div>
        <span class="chart-bar-label">${weekLabels[i]}</span>
      </div>
    `).join('');
  }

  /* ── Animate stat counters ──────────────────────────────────── */
  document.querySelectorAll('[data-count]').forEach(el => {
    const target = parseFloat(el.dataset.count);
    const suffix = el.dataset.suffix || '';
    window.HI.animateCounter(el, target, 1800, suffix);
  });

  /* ── Recent Reports Table ───────────────────────────────────── */
  const recentReports = [
    { name: 'Blood Test Report',     date: 'Jun 20, 2025', type: 'PDF', status: 'Analyzed',  score: 82 },
    { name: 'HbA1c & Glucose Panel', date: 'Jun 12, 2025', type: 'PDF', status: 'Analyzed',  score: 75 },
    { name: 'Lipid Profile',         date: 'May 28, 2025', type: 'IMG', status: 'Analyzed',  score: 78 },
    { name: 'Kidney Function Test',  date: 'May 10, 2025', type: 'PDF', status: 'Pending',   score: 70 },
    { name: 'Full Body Checkup',     date: 'Apr 22, 2025', type: 'PDF', status: 'Analyzed',  score: 68 },
  ];

  const tbody = document.getElementById('recentReportsBody');
  if (tbody) {
    tbody.innerHTML = recentReports.map(r => `
      <tr>
        <td>
          <div style="display:flex;align-items:center;gap:10px">
            <div style="width:36px;height:36px;border-radius:8px;background:${r.type==='PDF'?'#FEE2E2':'#DBEAFE'};
                        display:flex;align-items:center;justify-content:center;
                        color:${r.type==='PDF'?'#EF4444':'#2563EB'};font-size:.85rem;flex-shrink:0">
              <i class="fas fa-${r.type==='PDF'?'file-pdf':'file-image'}"></i>
            </div>
            <span style="font-weight:600;font-size:.88rem">${r.name}</span>
          </div>
        </td>
        <td>${r.date}</td>
        <td><span class="badge ${r.type==='PDF'?'badge-danger':'badge-info'}">${r.type}</span></td>
        <td>
          <span class="badge ${r.status==='Analyzed'?'badge-success':'badge-warning'}">
            ${r.status==='Analyzed'?'<i class="fas fa-check"></i>':'<i class="fas fa-clock"></i>'} ${r.status}
          </span>
        </td>
        <td><strong style="color:var(--primary)">${r.score}</strong>/100</td>
        <td>
          <div style="display:flex;gap:8px">
            <a href="analysis.html" class="btn btn-sm btn-primary" style="padding:6px 14px">
              <i class="fas fa-eye"></i> View
            </a>
          </div>
        </td>
      </tr>
    `).join('');
  }

  /* ── Activity Timeline ──────────────────────────────────────── */
  const activities = [
    { icon: 'fa-file-medical', color: '#2563EB', title: 'Blood Test Report Uploaded', sub: 'File: blood_test_june.pdf', time: '2h ago' },
    { icon: 'fa-brain',       color: '#14B8A6', title: 'AI Analysis Completed',       sub: 'Health Score: 82/100',     time: '2h ago' },
    { icon: 'fa-chart-line',  color: '#22C55E', title: 'Progress Updated',            sub: 'HbA1c improved by 0.9',   time: '5h ago' },
    { icon: 'fa-bell',        color: '#FACC15', title: 'Reminder: Annual Checkup',    sub: 'Due in 7 days',           time: '1d ago' },
    { icon: 'fa-user-check',  color: '#8B5CF6', title: 'Profile Completed',           sub: '100% complete',           time: '3d ago' },
  ];

  const activityEl = document.getElementById('activityList');
  if (activityEl) {
    activityEl.innerHTML = activities.map(a => `
      <div class="activity-item">
        <div class="activity-dot-wrap">
          <div class="activity-dot" style="background:${a.color}"></div>
          <div class="activity-line"></div>
        </div>
        <div class="activity-content">
          <div class="activity-title">${a.title}</div>
          <div class="activity-sub">${a.sub}</div>
        </div>
        <div class="activity-time">${a.time}</div>
      </div>
    `).join('');
  }

  /* ── Notifications dropdown demo ────────────────────────────── */
  const notifBtn = document.getElementById('notifBtn');
  if (notifBtn) {
    notifBtn.addEventListener('click', () => {
      window.HI.Toast.info('3 new notifications');
    });
  }

  /* ── User avatar initials ───────────────────────────────────── */
  const avatarEl = document.getElementById('userAvatar');
  if (avatarEl) {
    const user = JSON.parse(localStorage.getItem('hi-user') || '{}');
    if (user.name) {
      avatarEl.textContent = user.name.slice(0, 2).toUpperCase();
    }
    avatarEl.addEventListener('click', () => window.location.href = 'profile.html');
  }
});
