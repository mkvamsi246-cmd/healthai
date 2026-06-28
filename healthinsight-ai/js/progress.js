/* ============================================================
   progress.js — Health Progress Page Logic
   ============================================================ */
'use strict';

document.addEventListener('DOMContentLoaded', () => {

  /* ── Trend Data ──────────────────────────────────────────────── */
  const trends = {
    bloodSugar: { values: [142, 138, 134, 130, 128, 126], labels: ['Jan','Feb','Mar','Apr','May','Jun'], color: 'red', unit: 'mg/dL', current: '126', change: '-11.3%', dir: 'down' },
    hba1c:      { values: [8.1, 7.9, 7.7, 7.6, 7.4, 7.2], labels: ['Jan','Feb','Mar','Apr','May','Jun'], color: 'orange', unit: '%',    current: '7.2', change: '-11.1%', dir: 'down' },
    bp:         { values: [135, 134, 132, 130, 129, 128], labels: ['Jan','Feb','Mar','Apr','May','Jun'], color: 'blue', unit: 'mmHg',  current: '128',  change: '-5.2%',  dir: 'down' },
    weight:     { values: [88, 87, 86.5, 86, 85.5, 84.8], labels: ['Jan','Feb','Mar','Apr','May','Jun'], color: 'purple', unit: 'kg',  current: '84.8', change: '-3.6%',  dir: 'down' },
    bmi:        { values: [28.1, 27.9, 27.8, 27.7, 27.5, 27.4], labels: ['Jan','Feb','Mar','Apr','May','Jun'], color: 'teal', unit: 'kg/m²', current: '27.4', change: '-2.5%', dir: 'down' },
    cholesterol:{ values: [182, 178, 172, 168, 160, 148], labels: ['Jan','Feb','Mar','Apr','May','Jun'], color: 'orange', unit: 'mg/dL', current: '148', change: '-18.7%', dir: 'down' },
    score:      { values: [64, 66, 69, 72, 78, 82], labels: ['Jan','Feb','Mar','Apr','May','Jun'], color: 'green', unit: '/100', current: '82', change: '+28.1%', dir: 'up' },
  };

  /* ── Render Sparklines ───────────────────────────────────────── */
  const renderSparkline = (containerId, data) => {
    const el = document.getElementById(containerId);
    if (!el) return;
    const max = Math.max(...data.values);
    const min = Math.min(...data.values);
    const range = max - min || 1;
    const bars = data.values.map(v => ({ h: Math.round(((v - min) / range) * 50 + 10), label: v }));

    el.innerHTML = `
      <div class="sparkline">
        ${bars.map(b => `
          <div class="chart-bar-wrap">
            <div class="spark-bar ${data.color}" style="height:${b.h}px" title="${b.label} ${data.unit}"></div>
          </div>
        `).join('')}
      </div>
      <div class="spark-labels">
        <span>${data.labels[0]}</span>
        <span>${data.labels[Math.floor(data.labels.length/2)]}</span>
        <span>${data.labels[data.labels.length-1]}</span>
      </div>
    `;
  };

  // Map trend IDs to containers
  const trendMap = {
    'spark-bloodsugar': trends.bloodSugar,
    'spark-hba1c':      trends.hba1c,
    'spark-bp':         trends.bp,
    'spark-weight':     trends.weight,
    'spark-bmi':        trends.bmi,
    'spark-chol':       trends.cholesterol,
    'spark-score':      trends.score,
  };
  Object.entries(trendMap).forEach(([id, data]) => renderSparkline(id, data));

  /* ── Big Overview Chart ──────────────────────────────────────── */
  const bigChart = document.getElementById('overallChart');
  if (bigChart) {
    const scoreData = [64, 66, 69, 72, 78, 82];
    const labels    = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
    const max       = 100;

    bigChart.innerHTML = `
      <div class="big-chart-bars">
        ${scoreData.map((v, i) => `
          <div class="big-bar-wrap">
            <span class="big-bar-value">${v}</span>
            <div class="big-bar" style="height:${(v/max)*180}px"></div>
            <span class="big-bar-label">${labels[i]}</span>
          </div>
        `).join('')}
      </div>
    `;
  }

  /* ── Monthly Cards ───────────────────────────────────────────── */
  const monthlyData = [
    { month: 'January',   score: 64, change: '--',    dir: 'neutral' },
    { month: 'February',  score: 66, change: '+3.1%', dir: 'up' },
    { month: 'March',     score: 69, change: '+4.5%', dir: 'up' },
    { month: 'April',     score: 72, change: '+4.3%', dir: 'up' },
    { month: 'May',       score: 78, change: '+8.3%', dir: 'up' },
    { month: 'June',      score: 82, change: '+5.1%', dir: 'up' },
  ];

  const monthlyGrid = document.getElementById('monthlyCards');
  if (monthlyGrid) {
    monthlyGrid.innerHTML = monthlyData.map(m => `
      <div class="monthly-card">
        <div class="monthly-month">${m.month}</div>
        <div class="monthly-score" style="background:linear-gradient(135deg,var(--primary),var(--secondary));
             -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text">${m.score}</div>
        <div class="monthly-change ${m.dir === 'up' ? 'up' : m.dir === 'down' ? 'down' : ''}">${m.change}</div>
      </div>
    `).join('');
  }

  /* ── Timeline ────────────────────────────────────────────────── */
  const timelineData = [
    { date: 'Jun 20, 2025', title: 'Blood Test Report', tags: ['Glucose', 'HbA1c', 'CBC'], icon: 'fa-vial' },
    { date: 'Jun 12, 2025', title: 'HbA1c Panel',        tags: ['HbA1c', 'Insulin'],         icon: 'fa-droplet' },
    { date: 'May 28, 2025', title: 'Lipid Profile',       tags: ['LDL', 'HDL', 'Total Chol'],icon: 'fa-heart-pulse' },
    { date: 'May 10, 2025', title: 'Kidney Function',     tags: ['Creatinine', 'BUN'],        icon: 'fa-kidney' },
    { date: 'Apr 22, 2025', title: 'Full Body Checkup',   tags: ['All Parameters'],           icon: 'fa-user-doctor' },
  ];

  const timelineEl = document.getElementById('reportTimeline');
  if (timelineEl) {
    timelineEl.innerHTML = timelineData.map(t => `
      <div class="timeline-item">
        <div class="timeline-dot"><i class="fas ${t.icon}"></i></div>
        <div class="timeline-body">
          <div class="timeline-date">${t.date}</div>
          <div class="timeline-title">${t.title}</div>
          <div class="timeline-tags">
            ${t.tags.map(tag => `<span class="timeline-tag">${tag}</span>`).join('')}
          </div>
        </div>
      </div>
    `).join('');
  }
});
