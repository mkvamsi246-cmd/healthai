/* ============================================================
   main.js — Shared utilities for HealthInsight AI
   ============================================================ */

'use strict';

/* ── Theme ──────────────────────────────────────────────────── */
const ThemeManager = (() => {
  const KEY = 'hi-theme';
  const html = document.documentElement;

  const get   = () => localStorage.getItem(KEY) || 'light';
  const apply = (t) => { html.setAttribute('data-theme', t); localStorage.setItem(KEY, t); };
  const init  = () => apply(get());
  const toggle = () => apply(get() === 'dark' ? 'light' : 'dark');

  document.addEventListener('DOMContentLoaded', () => {
    init();
    document.querySelectorAll('[data-theme-toggle]').forEach(btn => {
      btn.addEventListener('click', () => {
        toggle();
        const isDark = get() === 'dark';
        btn.querySelector('i').className = isDark ? 'fas fa-sun' : 'fas fa-moon';
      });
      // Set initial icon
      const isDark = get() === 'dark';
      btn.querySelector('i').className = isDark ? 'fas fa-sun' : 'fas fa-moon';
    });
  });

  return { get, apply, toggle };
})();

/* ── Toast Notifications ────────────────────────────────────── */
const Toast = (() => {
  let container;

  const getContainer = () => {
    if (!container) {
      container = document.createElement('div');
      container.className = 'toast-container';
      document.body.appendChild(container);
    }
    return container;
  };

  const iconMap = {
    success: 'fa-circle-check',
    warning: 'fa-triangle-exclamation',
    error:   'fa-circle-xmark',
    info:    'fa-circle-info',
  };

  const show = (message, type = 'info', duration = 3500) => {
    const c   = getContainer();
    const div = document.createElement('div');
    div.className = `toast ${type}`;
    div.innerHTML = `<i class="fas ${iconMap[type] || iconMap.info}"></i><span>${message}</span>`;
    c.appendChild(div);

    setTimeout(() => {
      div.classList.add('fade-out');
      div.addEventListener('animationend', () => div.remove(), { once: true });
    }, duration);
  };

  return {
    success: (m, d) => show(m, 'success', d),
    warning: (m, d) => show(m, 'warning', d),
    error:   (m, d) => show(m, 'error',   d),
    info:    (m, d) => show(m, 'info',    d),
  };
})();

/* ── Modal ──────────────────────────────────────────────────── */
const Modal = (() => {
  let overlay = null;

  const open = (html, opts = {}) => {
    close();
    overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.innerHTML = `
      <div class="modal" role="dialog" aria-modal="true">
        <button class="modal-close" aria-label="Close">&times;</button>
        ${html}
      </div>`;
    document.body.appendChild(overlay);
    document.body.style.overflow = 'hidden';

    overlay.querySelector('.modal-close').addEventListener('click', close);
    if (!opts.noBackdrop) overlay.addEventListener('click', e => { if (e.target === overlay) close(); });
    document.addEventListener('keydown', escClose);
    if (opts.onOpen) opts.onOpen(overlay.querySelector('.modal'));
  };

  const escClose = (e) => { if (e.key === 'Escape') close(); };
  const close = () => {
    if (!overlay) return;
    overlay.remove();
    overlay = null;
    document.body.style.overflow = '';
    document.removeEventListener('keydown', escClose);
  };

  return { open, close };
})();

/* ── Animated Counter ────────────────────────────────────────── */
const animateCounter = (el, target, duration = 1800, suffix = '') => {
  const start = performance.now();
  const startVal = 0;
  const update = (now) => {
    const progress = Math.min((now - start) / duration, 1);
    const ease = 1 - Math.pow(1 - progress, 4);
    el.textContent = Math.round(startVal + ease * (target - startVal)) + suffix;
    if (progress < 1) requestAnimationFrame(update);
  };
  requestAnimationFrame(update);
};

/* ── Scroll Reveal ───────────────────────────────────────────── */
const initScrollReveal = () => {
  const els = document.querySelectorAll('.reveal');
  if (!els.length) return;

  const obs = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add('visible');
        obs.unobserve(e.target);
      }
    });
  }, { threshold: 0.15 });

  els.forEach(el => obs.observe(el));
};

/* ── Sticky Navbar ───────────────────────────────────────────── */
const initStickyNavbar = () => {
  const nav = document.querySelector('.navbar');
  if (!nav) return;
  window.addEventListener('scroll', () => {
    nav.classList.toggle('scrolled', window.scrollY > 20);
  }, { passive: true });
};

/* ── Hamburger Menu ──────────────────────────────────────────── */
const initMobileMenu = () => {
  const btn  = document.querySelector('.hamburger');
  const menu = document.querySelector('.mobile-menu');
  if (!btn || !menu) return;

  btn.addEventListener('click', () => {
    btn.classList.toggle('active');
    menu.classList.toggle('open');
  });
};

/* ── Smooth Scroll for anchor links ──────────────────────────── */
const initSmoothScroll = () => {
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
      const target = document.querySelector(a.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });
};

/* ── FAQ Accordion ───────────────────────────────────────────── */
const initFAQ = () => {
  document.querySelectorAll('.faq-question').forEach(q => {
    q.addEventListener('click', () => {
      const item = q.closest('.faq-item');
      const isOpen = item.classList.contains('open');
      document.querySelectorAll('.faq-item.open').forEach(el => el.classList.remove('open'));
      if (!isOpen) item.classList.add('open');
    });
  });
};

/* ── Loading Overlay ─────────────────────────────────────────── */
const showLoader = (msg = 'Loading…') => {
  const el = document.createElement('div');
  el.className = 'loading-overlay';
  el.id = '__loader__';
  el.innerHTML = `<div class="spinner"></div><p>${msg}</p>`;
  document.body.appendChild(el);
  return el;
};

const hideLoader = () => {
  const el = document.getElementById('__loader__');
  if (el) el.remove();
};

/* ── Sidebar (dashboard pages) ───────────────────────────────── */
const initSidebar = () => {
  const sidebar  = document.querySelector('.sidebar');
  const overlay  = document.querySelector('.sidebar-overlay');
  const toggleBtn = document.querySelector('.sidebar-toggle');
  const mobileBtn = document.querySelector('.mobile-menu-btn');
  if (!sidebar) return;

  // Desktop collapse
  toggleBtn && toggleBtn.addEventListener('click', () => {
    sidebar.classList.toggle('collapsed');
    const icon = toggleBtn.querySelector('i');
    if (icon) icon.className = sidebar.classList.contains('collapsed') ? 'fas fa-chevron-right' : 'fas fa-chevron-left';
  });

  // Mobile open/close
  mobileBtn && mobileBtn.addEventListener('click', () => {
    sidebar.classList.toggle('mobile-open');
    overlay && overlay.classList.toggle('active');
  });
  overlay && overlay.addEventListener('click', () => {
    sidebar.classList.remove('mobile-open');
    overlay.classList.remove('active');
  });

  // Mark active link
  const current = window.location.pathname.split('/').pop() || 'index.html';
  sidebar.querySelectorAll('.nav-item[href]').forEach(a => {
    if (a.getAttribute('href') === current) a.classList.add('active');
  });
};

/* ── Init all shared features ────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  initScrollReveal();
  initStickyNavbar();
  initMobileMenu();
  initSmoothScroll();
  initFAQ();
  initSidebar();

  // Counter animation (triggered on visibility)
  const counters = document.querySelectorAll('[data-count]');
  if (counters.length) {
    const obs = new IntersectionObserver(entries => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          const el     = e.target;
          const target = parseFloat(el.dataset.count);
          const suffix = el.dataset.suffix || '';
          animateCounter(el, target, 1800, suffix);
          obs.unobserve(el);
        }
      });
    }, { threshold: 0.5 });
    counters.forEach(c => obs.observe(c));
  }
});

/* ── Export for modules ───────────────────────────────────────── */
window.HI = { Toast, Modal, animateCounter, showLoader, hideLoader };
