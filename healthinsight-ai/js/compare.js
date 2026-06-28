/* ============================================================
   compare.js — Compare Reports Page Logic
   ============================================================ */
'use strict';

document.addEventListener('DOMContentLoaded', () => {

  const compareData = [
    { param: 'HbA1c',              prev: '8.1%',       curr: '7.2%',       diff: '-0.9%', diffVal: -0.9, status: 'improved' },
    { param: 'Blood Sugar',        prev: '142 mg/dL',  curr: '126 mg/dL',  diff: '-16',   diffVal: -16,  status: 'improved' },
    { param: 'LDL Cholesterol',    prev: '162 mg/dL',  curr: '148 mg/dL',  diff: '-14',   diffVal: -14,  status: 'improved' },
    { param: 'HDL Cholesterol',    prev: '48 mg/dL',   curr: '52 mg/dL',   diff: '+4',    diffVal: 4,    status: 'improved' },
    { param: 'Blood Pressure',     prev: '132/86 mmHg',curr: '128/82 mmHg',diff: '-4/-4', diffVal: -4,   status: 'improved' },
    { param: 'Triglycerides',      prev: '192 mg/dL',  curr: '186 mg/dL',  diff: '-6',    diffVal: -6,   status: 'improved' },
    { param: 'Hemoglobin',         prev: '13.8 g/dL',  curr: '13.8 g/dL',  diff: '0',     diffVal: 0,    status: 'same'     },
    { param: 'Creatinine',         prev: '1.0 mg/dL',  curr: '1.1 mg/dL',  diff: '+0.1',  diffVal: 0.1,  status: 'worse'    },
    { param: 'BMI',                prev: '28.1',        curr: '27.4',        diff: '-0.7',  diffVal: -0.7, status: 'improved' },
    { param: 'Heart Rate',         prev: '78 bpm',      curr: '74 bpm',      diff: '-4',    diffVal: -4,   status: 'improved' },
  ];

  const statusIcon = { improved: 'fa-arrow-trend-up', worse: 'fa-arrow-trend-down', same: 'fa-minus' };
  const statusLabel = { improved: 'Improved', worse: 'Worse', same: 'No Change' };

  /* ── Comparison Table ────────────────────── */
  const tbody = document.getElementById('compareBody');
  if (tbody) {
    tbody.innerHTML = compareData.map(r => `
      <tr>
        <td><strong>${r.param}</strong></td>
        <td style="color:var(--primary);font-weight:600">${r.prev}</td>
        <td style="color:var(--secondary);font-weight:600">${r.curr}</td>
        <td>
          <div class="compare-diff ${r.status}">
            <i class="fas ${statusIcon[r.status]}"></i>
            ${r.diff}
          </div>
        </td>
        <td>
          <span class="compare-status ${r.status}">
            <i class="fas ${statusIcon[r.status]}"></i>
            ${statusLabel[r.status]}
          </span>
        </td>
      </tr>
    `).join('');
  }

  /* ── Overall stats ──────────────────────── */
  const improved = compareData.filter(r => r.status === 'improved').length;
  const worse    = compareData.filter(r => r.status === 'worse').length;
  const pct      = Math.round((improved / compareData.length) * 100);

  const impEl = document.getElementById('overallPct');
  if (impEl) window.HI.animateCounter(impEl, pct, 1800, '%');

  const statImproved = document.getElementById('statImproved');
  const statWorse    = document.getElementById('statWorse');
  if (statImproved) statImproved.textContent = improved;
  if (statWorse)    statWorse.textContent    = worse;

  /* ── Score bars ─────────────────────────── */
  const prevBar = document.getElementById('prevScoreBar');
  const currBar = document.getElementById('currScoreBar');
  if (prevBar) setTimeout(() => prevBar.style.width = '68%', 400);
  if (currBar) setTimeout(() => currBar.style.width = '82%', 600);

  /* ── Report selectors ───────────────────── */
  const selPrev = document.getElementById('selectPrev');
  const selCurr = document.getElementById('selectCurr');
  const cmpBtn  = document.getElementById('compareBtn');

  if (cmpBtn) {
    cmpBtn.addEventListener('click', () => {
      if (selPrev.value === selCurr.value) {
        window.HI.Toast.warning('Please select two different reports to compare.');
        return;
      }
      window.HI.Toast.info('Comparison updated!');
    });
  }

  /* ── Mini chart bars ────────────────────── */
  const miniChartEl = document.getElementById('progressChart');
  if (miniChartEl) {
    const data = [68, 70, 74, 72, 78, 82];
    const labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
    const max = Math.max(...data);
    miniChartEl.innerHTML = `
      <div style="display:flex;align-items:flex-end;gap:12px;height:120px;padding:10px 0">
        ${data.map((v, i) => `
          <div style="flex:1;display:flex;flex-direction:column;align-items:center;gap:6px">
            <span style="font-size:.7rem;font-weight:700;color:var(--primary)">${v}</span>
            <div style="width:100%;background:linear-gradient(180deg,var(--primary),var(--secondary));
                        border-radius:6px 6px 0 0;height:${(v/max)*80}px;opacity:.8"></div>
            <span style="font-size:.68rem;color:var(--text-muted)">${labels[i]}</span>
          </div>
        `).join('')}
      </div>
    `;
  }
});
