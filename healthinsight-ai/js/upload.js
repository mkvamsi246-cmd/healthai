/* ============================================================
   upload.js — Upload Page Logic
   ============================================================ */
'use strict';

document.addEventListener('DOMContentLoaded', () => {
  const zone        = document.getElementById('dropZone');
  const fileInput   = document.getElementById('fileInput');
  const progressCard= document.getElementById('uploadProgress');
  const progressFill= document.getElementById('progressFill');
  const progressPct = document.getElementById('progressPct');
  const fileName    = document.getElementById('uploadFileName');
  const fileSize    = document.getElementById('uploadFileSize');
  const previewArea = document.getElementById('previewArea');
  const uploadedList= document.getElementById('uploadedList');

  let uploadedFiles = [
    { name: 'blood_test_june_2025.pdf', size: '2.4 MB', type: 'pdf', date: 'Jun 20, 2025', id: 1 },
    { name: 'hba1c_panel_june_2025.pdf',size: '1.8 MB', type: 'pdf', date: 'Jun 12, 2025', id: 2 },
    { name: 'lipid_profile_may.jpg',    size: '3.1 MB', type: 'img', date: 'May 28, 2025', id: 3 },
  ];

  /* ── Render uploaded list ────────────────── */
  const renderList = () => {
    if (!uploadedList) return;
    uploadedList.innerHTML = uploadedFiles.map(f => `
      <div class="uploaded-item" id="file-${f.id}">
        <div class="uploaded-item-icon ${f.type}">
          <i class="fas fa-${f.type === 'pdf' ? 'file-pdf' : 'file-image'}"></i>
        </div>
        <div class="uploaded-item-info">
          <div class="uploaded-item-name">${f.name}</div>
          <div class="uploaded-item-meta">${f.size} &bull; ${f.date}</div>
        </div>
        <div class="uploaded-item-actions">
          <a href="analysis.html" class="btn btn-sm btn-secondary" title="Analyze">
            <i class="fas fa-brain"></i>
          </a>
          <button class="btn btn-sm btn-icon" onclick="deleteFile(${f.id})" title="Delete">
            <i class="fas fa-trash" style="color:var(--danger)"></i>
          </button>
        </div>
      </div>
    `).join('') || '<p style="color:var(--text-muted);text-align:center;padding:20px">No files uploaded yet.</p>';
  };

  window.deleteFile = (id) => {
    uploadedFiles = uploadedFiles.filter(f => f.id !== id);
    renderList();
    window.HI.Toast.success('File removed successfully.');
  };

  renderList();

  /* ── Drag & Drop ─────────────────────────── */
  ['dragenter','dragover'].forEach(evt =>
    zone.addEventListener(evt, (e) => { e.preventDefault(); zone.classList.add('dragover'); }));
  ['dragleave','drop'].forEach(evt =>
    zone.addEventListener(evt, (e) => { e.preventDefault(); zone.classList.remove('dragover'); }));

  zone.addEventListener('drop', (e) => {
    const files = e.dataTransfer.files;
    if (files.length) handleFile(files[0]);
  });

  fileInput.addEventListener('change', () => {
    if (fileInput.files.length) handleFile(fileInput.files[0]);
  });

  /* ── Handle file ─────────────────────────── */
  const handleFile = (file) => {
    const allowed = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg'];
    if (!allowed.includes(file.type)) {
      window.HI.Toast.error('Only PDF, JPG, and PNG files are allowed.');
      return;
    }
    if (file.size > 20 * 1024 * 1024) {
      window.HI.Toast.error('File size must be under 20 MB.');
      return;
    }

    // Show progress
    progressCard.classList.add('visible');
    fileName.textContent = file.name;
    fileSize.textContent = formatBytes(file.size);

    // Animate progress
    let pct = 0;
    progressFill.style.width = '0%';
    progressPct.textContent = '0%';

    const interval = setInterval(() => {
      pct += Math.random() * 15;
      if (pct >= 100) {
        pct = 100;
        clearInterval(interval);
        setTimeout(() => {
          progressCard.classList.remove('visible');
          // Add to list
          const newFile = {
            name: file.name,
            size: formatBytes(file.size),
            type: file.type.includes('pdf') ? 'pdf' : 'img',
            date: new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
            id: Date.now()
          };
          uploadedFiles.unshift(newFile);
          renderList();
          window.HI.Toast.success('File uploaded successfully! Click Analyze to get AI insights.');
        }, 400);
      }
      progressFill.style.width = pct + '%';
      progressPct.textContent = Math.round(pct) + '%';
    }, 150);

    // Preview
    if (file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (e) => {
        previewArea.innerHTML = `<img src="${e.target.result}" alt="Preview" style="max-height:300px;object-fit:contain">`;
      };
      reader.readAsDataURL(file);
    } else {
      previewArea.innerHTML = `
        <div style="text-align:center;padding:40px">
          <i class="fas fa-file-pdf" style="font-size:3rem;color:#EF4444;margin-bottom:12px;display:block"></i>
          <strong>${file.name}</strong>
          <p style="margin-top:6px;font-size:.85rem">${formatBytes(file.size)}</p>
          <div class="pdf-preview-mock" style="margin-top:20px">
            ${Array(8).fill('<div class="pdf-line" style="width:' + (70 + Math.random()*30).toFixed(0) + '%"></div>').join('')}
          </div>
        </div>`;
    }
  };

  const formatBytes = (b) => {
    if (b >= 1024 * 1024) return (b / (1024 * 1024)).toFixed(1) + ' MB';
    return (b / 1024).toFixed(0) + ' KB';
  };

  /* ── Upload type buttons ─────────────────── */
  document.getElementById('uploadPdfBtn').addEventListener('click', () => {
    fileInput.accept = '.pdf,application/pdf';
    fileInput.click();
  });
  document.getElementById('uploadImgBtn').addEventListener('click', () => {
    fileInput.accept = 'image/*';
    fileInput.click();
  });
});
