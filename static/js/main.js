/**
 * CuraSuite — Main JavaScript
 * Minimal vanilla JS for core interactions.
 * HTMX handles dynamic updates; Alpine.js handles UI components.
 */

'use strict';

// ── HTMX Configuration ────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  // Configure HTMX
  if (typeof htmx !== 'undefined') {
    htmx.config.defaultSwapStyle = 'innerHTML';
    htmx.config.historyCacheSize = 10;
    htmx.config.refreshOnHistoryMiss = true;
  }
});

// ── Toast Notifications ────────────────────────────────────────────────────────
function showToast(message, type = 'info', duration = 4000) {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.setAttribute('role', 'alert');
  toast.textContent = message;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// ── HTMX After Swap ───────────────────────────────────────────────────────────
document.addEventListener('htmx:afterSwap', (event) => {
  const messages = event.detail.elt.querySelectorAll('[data-message]');
  messages.forEach(el => {
    showToast(el.dataset.message, el.dataset.messageType || 'info');
    el.remove();
  });
});
