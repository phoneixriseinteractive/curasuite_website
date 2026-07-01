/**
 * CuraSuite Admin Panel — Core JS
 * Toast notifications, Quill editor init, delete confirms, HTMX hooks
 */

'use strict';

/* ── Toast system ─────────────────────────────────────────────────────────── */
window.adminToast = function(message, type = 'success', duration = 3500) {
  let container = document.getElementById('adm-toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'adm-toast-container';
    container.className = 'adm-toast-container';
    document.body.appendChild(container);
  }
  const toast = document.createElement('div');
  toast.className = `adm-toast adm-toast-${type}`;
  const icon = type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ';
  toast.innerHTML = `<span>${icon}</span> ${message}`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    toast.style.transition = 'all .3s ease';
    setTimeout(() => toast.remove(), 300);
  }, duration);
};

/* ── Quill editor factory ─────────────────────────────────────────────────── */
window.initQuill = function(containerId, hiddenInputId, options = {}) {
  const container = document.getElementById(containerId);
  if (!container) return null;

  const toolbarOptions = options.toolbar || [
    [{ 'header': [1, 2, 3, false] }],
    ['bold', 'italic', 'underline', 'strike'],
    [{ 'list': 'ordered'}, { 'list': 'bullet' }],
    ['blockquote', 'code-block'],
    ['link'],
    [{ 'align': [] }],
    ['clean']
  ];

  const quill = new Quill(container, {
    theme: 'snow',
    modules: { toolbar: toolbarOptions },
    placeholder: options.placeholder || 'Start writing…',
  });

  // Sync to hidden input on change
  const hiddenInput = document.getElementById(hiddenInputId);
  if (hiddenInput) {
    // Pre-populate
    if (hiddenInput.value) {
      quill.root.innerHTML = hiddenInput.value;
    }
    quill.on('text-change', () => {
      hiddenInput.value = quill.root.innerHTML;
    });
  }

  return quill;
};

/* ── Delete confirm ───────────────────────────────────────────────────────── */
window.confirmDelete = function(message, formId) {
  if (confirm(message || 'Are you sure you want to delete this? This cannot be undone.')) {
    const form = document.getElementById(formId);
    if (form) form.submit();
    return true;
  }
  return false;
};

/* ── HTMX hooks ───────────────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  // Show toast on HTMX success if response includes data-toast attribute
  document.body.addEventListener('htmx:afterSwap', (e) => {
    const toastEl = e.detail.elt.querySelector('[data-toast]');
    if (toastEl) {
      adminToast(toastEl.dataset.toast, toastEl.dataset.toastType || 'success');
    }
  });

  // Close modal on ESC
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      const modal = document.querySelector('[x-data]')?.__x?.$data;
      if (modal && typeof modal.showModal !== 'undefined') modal.showModal = false;
    }
  });
});

/* ── Upload zone drag-and-drop ────────────────────────────────────────────── */
window.initUploadZone = function(zoneId, inputId) {
  const zone  = document.getElementById(zoneId);
  const input = document.getElementById(inputId);
  if (!zone || !input) return;

  zone.addEventListener('click', () => input.click());
  zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('drag-over'); });
  zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'));
  zone.addEventListener('drop', e => {
    e.preventDefault();
    zone.classList.remove('drag-over');
    input.files = e.dataTransfer.files;
    input.dispatchEvent(new Event('change'));
  });
};
