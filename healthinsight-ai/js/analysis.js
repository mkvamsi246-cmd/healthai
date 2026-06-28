/* ============================================================
   analysis.js — Report Analysis Page Logic
   ============================================================ */
'use strict';

document.addEventListener('DOMContentLoaded', () => {

  /* ── Medical Data ───────────────────────────────────────────── */
  const medicalValues = [
    { param: 'Blood Sugar (Fasting)', value: '126',  unit: 'mg/dL', normal: '70–100',  pct: 75,  status: 'high' },
    { param: 'HbA1c',                 value: '7.2',  unit: '%',     normal: '< 5.7',   pct: 75,  status: 'borderline' },
    { param: 'Blood Pressure',        value: '128/82',unit: 'mmHg', normal: '< 120/80',pct: 65,  status: 'borderline' },
    { param: 'Heart Rate',            value: '74',   unit: 'bpm',   normal: '60–100',  pct: 40,  status: 'normal' },
    { param: 'LDL Cholesterol',       value: '148',  unit: 'mg/dL', normal: '< 100',   pct: 88,  status: 'high' },
    { param: 'HDL Cholesterol',       value: '52',   unit: 'mg/dL', normal: '> 40',    pct: 30,  status: 'normal' },
    { param: 'Hemoglobin',            value: '13.8', unit: 'g/dL',  normal: '13.5–17.5',pct: 45, status: 'normal' },
    { param: 'Creatinine',            value: '1.1',  unit: 'mg/dL', normal: '0.74–1.35',pct: 50, status: 'normal' },
    { param: 'BMI',                   value: '27.4', unit: 'kg/m²', normal: '18.5–24.9',pct: 70, status: 'borderline' },
    { param: 'Triglycerides',         value: '186',  unit: 'mg/dL', normal: '< 150',   pct: 85,  status: 'high' },
  ];

  const statusLabels = { normal: 'Normal', borderline: 'Borderline', high: 'High', low: 'Low' };

  /* ── Medical Table ──────────────────────────────────────────── */
  const tbody = document.getElementById('medValuesBody');
  if (tbody) {
    tbody.innerHTML = medicalValues.map(r => `
      <tr>
        <td><strong>${r.param}</strong></td>
        <td><strong>${r.value}</strong> <span style="color:var(--text-muted);font-size:.8rem">${r.unit}</span></td>
        <td><span style="color:var(--text-muted);font-size:.85rem">${r.normal} ${r.unit}</span></td>
        <td>
          <div class="value-bar-wrap">
            <div class="value-mini-bar">
              <div class="value-mini-fill ${r.status}" style="width:${r.pct}%"></div>
            </div>
          </div>
        </td>
        <td>
          <span class="value-status ${r.status}">
            <i class="fas fa-${r.status==='normal'?'check':r.status==='high'?'arrow-up':'minus'}"></i>
            ${statusLabels[r.status]}
          </span>
        </td>
      </tr>
    `).join('');
  }

  /* ── Risk Gauges ────────────────────────────────────────────── */
  const risks = [
    { id: 'heartRisk',    label: 'Heart Disease', pct: 35, level: 'Moderate', cls: 'risk-med'  },
    { id: 'diabetesRisk', label: 'Diabetes',      pct: 62, level: 'High',     cls: 'risk-high' },
    { id: 'kidneyRisk',   label: 'Kidney Disease',pct: 18, level: 'Low',      cls: 'risk-low'  },
    { id: 'strokeRisk',   label: 'Stroke',        pct: 22, level: 'Low',      cls: 'risk-low'  },
  ];

  const riskGrid = document.getElementById('riskGrid');
  if (riskGrid) {
    riskGrid.innerHTML = risks.map(r => {
      const R    = 40; // circle radius
      const circ = 2 * Math.PI * R;
      const dash = circ - (r.pct / 100) * circ;
      return `
        <div class="risk-card ${r.cls}">
          <div class="risk-gauge">
            <svg viewBox="0 0 100 100">
              <circle class="track" cx="50" cy="50" r="${R}" />
              <circle class="fill" cx="50" cy="50" r="${R}"
                stroke-dasharray="${circ}"
                stroke-dashoffset="${circ}"
                data-dash="${dash}"
                style="stroke-dashoffset:${circ}" />
            </svg>
            <div class="risk-pct">${r.pct}%</div>
          </div>
          <h4>${r.label}</h4>
          <span class="risk-level">${r.level} Risk</span>
        </div>
      `;
    }).join('');

    // Animate
    requestAnimationFrame(() => {
      riskGrid.querySelectorAll('.fill').forEach(el => {
        setTimeout(() => {
          el.style.transition = 'stroke-dashoffset 1.5s cubic-bezier(.4,0,.2,1)';
          el.style.strokeDashoffset = el.dataset.dash;
        }, 300);
      });
    });
  }

  /* ── Health Score Donut ─────────────────────────────────────── */
  const donutEl = document.getElementById('scoreDonut');
  if (donutEl) {
    const score = 74;
    const R     = 55;
    const circ  = 2 * Math.PI * R;
    const fill  = (score / 100) * circ;
    donutEl.innerHTML = `
      <svg viewBox="0 0 140 140">
        <circle fill="none" stroke="var(--border)" stroke-width="12" cx="70" cy="70" r="${R}"/>
        <circle fill="none" stroke="url(#scoreGrad)" stroke-width="12" cx="70" cy="70" r="${R}"
                stroke-linecap="round"
                stroke-dasharray="${circ}" stroke-dashoffset="${circ}"
                id="scoreCircle" style="transform:rotate(-90deg);transform-origin:center"/>
        <defs>
          <linearGradient id="scoreGrad" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stop-color="var(--primary)"/>
            <stop offset="100%" stop-color="var(--secondary)"/>
          </linearGradient>
        </defs>
      </svg>
      <div class="score-donut-label">
        <span class="score-donut-num" id="scoreNum">0</span>
        <span class="score-donut-sub">Health Score</span>
      </div>
    `;
    setTimeout(() => {
      const circle = document.getElementById('scoreCircle');
      circle.style.transition = 'stroke-dashoffset 1.8s cubic-bezier(.4,0,.2,1)';
      circle.style.strokeDashoffset = circ - fill;
      window.HI.animateCounter(document.getElementById('scoreNum'), score, 1800, '');
    }, 400);
  }

  /* ── Download Report ─────────────────────────────────────────── */
  const downloadBtn = document.getElementById('downloadReport');
  if (downloadBtn) {
    downloadBtn.addEventListener('click', () => {
      window.HI.Toast.info('Generating PDF report… Please wait.');
      setTimeout(() => window.HI.Toast.success('Report downloaded successfully!'), 2000);
    });
  }
});
