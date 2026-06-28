/* ============================================================
   reports.js — My Reports Page Logic
   ============================================================ */
'use strict';

document.addEventListener('DOMContentLoaded', () => {
  const reports = [
    { id: 1, name: 'Blood Test Report – June 2025',   date: 'Jun 20, 2025', type: 'pdf', category: 'blood',   score: 82, size: '2.4 MB' },
    { id: 2, name: 'HbA1c & Glucose Panel',           date: 'Jun 12, 2025', type: 'pdf', category: 'diabetes',score: 75, size: '1.8 MB' },
    { id: 3, name: 'Lipid Profile – May',             date: 'May 28, 2025', type: 'img', category: 'cholesterol',score:78,size:'3.1 MB' },
    { id: 4, name: 'Kidney Function Test',             date: 'May 10, 2025', type: 'pdf', category: 'kidney',  score: 70, size: '1.2 MB' },
    { id: 5, name: 'Full Body Checkup – April',       date: 'Apr 22, 2025', type: 'pdf', category: 'general', score: 68, size: '5.6 MB' },
    { id: 6, name: 'CBC – Complete Blood Count',      date: 'Apr 05, 2025', type: 'pdf', category: 'blood',   score: 72, size: '1.5 MB' },
    { id: 7, name: 'Thyroid Panel',                   date: 'Mar 18, 2025', type: 'img', category: 'thyroid', score: 80, size: '2.8 MB' },
    { id: 8, name: 'Urine Analysis Report',           date: 'Mar 02, 2025', type: 'pdf', category: 'kidney',  score: 76, size: '0.9 MB' },
  ];

  const categoryLabels = {
    blood: 'Blood Test', diabetes: 'Diabetes', cholesterol: 'Lipid',
    kidney: 'Kidney', general: 'General', thyroid: 'Thyroid',
  };
  const categoryColors = {
    blood: '#FEE2E2:#EF4444', diabetes: '#FEF9C3:#A16207', cholesterol: '#DBEAFE:#2563EB',
    kidney: '#D1FAE5:#059669', general: '#EDE9FE:#7C3AED', thyroid: '#FCE7F3:#DB2777',
  };

  let currentFilter = 'all';
  let searchQuery   = '';
  let viewMode      = 'grid';
  let allReports    = [...reports];

  const grid   = document.getElementById('reportsContainer');
  const noRes  = document.getElementById('noResults');
  const searchIn = document.getElementById('searchReports');
  const dateFilter = document.getElementById('filterDate');
  const typeFilter = document.getElementById('filterType');

  const getColor = (cat) => {
    const parts = (categoryColors[cat] || '#DBEAFE:#2563EB').split(':');
    return { bg: parts[0], text: parts[1] };
  };

  const render = () => {
    let data = allReports.filter(r => {
      const matchSearch = r.name.toLowerCase().includes(searchQuery.toLowerCase());
      const matchType   = currentFilter === 'all' || r.category === currentFilter || r.type === currentFilter;
      return matchSearch && matchType;
    });

    // Sort
    if (dateFilter && dateFilter.value === 'oldest') data.sort((a, b) => a.id - b.id);
    else data.sort((a, b) => b.id - a.id);

    if (!data.length) {
      grid.innerHTML = '';
      noRes.classList.add('visible');
      return;
    }
    noRes.classList.remove('visible');

    grid.className = viewMode === 'grid' ? 'reports-grid' : 'reports-list';

    grid.innerHTML = data.map(r => {
      const c = getColor(r.category);
      return `
        <div class="report-card" data-id="${r.id}">
          <div class="report-card-top">
            <div class="report-file-icon ${r.type}">
              <i class="fas fa-${r.type === 'pdf' ? 'file-pdf' : 'file-image'}"></i>
            </div>
            <div class="report-card-meta">
              <div class="report-card-name">${r.name}</div>
              <div class="report-card-date"><i class="fas fa-calendar-alt" style="font-size:.75rem"></i> ${r.date} &bull; ${r.size}</div>
              <span class="report-card-type-badge badge"
                    style="background:${c.bg};color:${c.text};margin-top:6px">${categoryLabels[r.category]}</span>
            </div>
          </div>
          <div class="report-card-score">
            <span style="font-size:.82rem;color:var(--text-muted)">Health Score</span>
            <span class="score-pill">${r.score}/100</span>
          </div>
          <div class="report-card-actions">
            <a href="analysis.html" class="btn btn-sm btn-primary"><i class="fas fa-eye"></i> View</a>
            <a href="analysis.html" class="btn btn-sm btn-secondary"><i class="fas fa-brain"></i> Analyze</a>
            <a href="compare.html"  class="btn btn-sm btn-outline"><i class="fas fa-scale-balanced"></i> Compare</a>
            <button class="btn btn-sm btn-danger" onclick="deleteReport(${r.id})" style="padding:8px 12px">
              <i class="fas fa-trash"></i>
            </button>
          </div>
        </div>
      `;
    }).join('');
  };

  window.deleteReport = (id) => {
    window.HI.Modal.open(`
      <h3 style="margin-bottom:8px">Delete Report?</h3>
      <p style="margin-bottom:24px;font-size:.9rem">This action cannot be undone. The report will be permanently deleted.</p>
      <div style="display:flex;gap:12px">
        <button class="btn btn-outline w-full" id="cancelDel" style="justify-content:center">Cancel</button>
        <button class="btn btn-danger w-full" id="confirmDel" style="justify-content:center">
          <i class="fas fa-trash"></i> Delete
        </button>
      </div>
    `, {
      onOpen: (modal) => {
        modal.querySelector('#cancelDel').addEventListener('click', window.HI.Modal.close);
        modal.querySelector('#confirmDel').addEventListener('click', () => {
          allReports = allReports.filter(r => r.id !== id);
          render();
          window.HI.Modal.close();
          window.HI.Toast.success('Report deleted successfully.');
        });
      }
    });
  };

  // Listeners
  searchIn && searchIn.addEventListener('input', () => { searchQuery = searchIn.value; render(); });
  typeFilter && typeFilter.addEventListener('change', () => { currentFilter = typeFilter.value; render(); });
  dateFilter && dateFilter.addEventListener('change', render);

  // View toggles
  document.querySelectorAll('.view-toggle-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.view-toggle-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      viewMode = btn.dataset.view;
      render();
    });
  });

  // Report count
  const countEl = document.getElementById('reportCount');
  if (countEl) countEl.textContent = reports.length;

  render();
});
