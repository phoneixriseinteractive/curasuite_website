/**
 * CuraSuite Admin Panel — Core JS
 * Toast notifications, rich text editor (TinyMCE) init, delete confirms, HTMX hooks
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

/* ── Legacy Quill content → semantic HTML ─────────────────────────────────── */
/*
 * Quill 2 (the previous editor) stored every list as a flat <ol> whose items carry
 * data-list="bullet|ordered" and ql-indent-N classes. Rebuild those into real nested
 * <ul>/<ol> so older posts open correctly and render as proper bullets once re-saved.
 */
function upgradeQuillHtml(html) {
  if (!html || html.indexOf('data-list') === -1) return html;
  const doc = new DOMParser().parseFromString(`<div id="root">${html}</div>`, 'text/html');
  const root = doc.getElementById('root');

  root.querySelectorAll('ol').forEach(ol => {
    const items = Array.from(ol.children).filter(li => li.tagName === 'LI' && li.dataset.list);
    if (!items.length) return;

    const frag = doc.createDocumentFragment();
    const stack = []; // [{list, depth}]
    items.forEach(li => {
      const m = (li.className || '').match(/ql-indent-(\d+)/);
      const depth = m ? parseInt(m[1], 10) : 0;
      const tag = li.dataset.list === 'ordered' ? 'ol' : 'ul';

      while (stack.length && stack[stack.length - 1].depth > depth) stack.pop();
      let top = stack[stack.length - 1];
      if (top && top.depth === depth && top.list.tagName.toLowerCase() !== tag) {
        stack.pop();
        top = stack[stack.length - 1];
      }
      if (!top || top.depth < depth) {
        const list = doc.createElement(tag);
        if (top && top.list.lastElementChild) top.list.lastElementChild.appendChild(list);
        else frag.appendChild(list);
        stack.push({ list, depth });
        top = stack[stack.length - 1];
      }

      li.removeAttribute('data-list');
      li.className = li.className.replace(/ql-indent-\d+/g, '').trim();
      if (!li.className) li.removeAttribute('class');
      li.querySelectorAll('.ql-ui').forEach(el => el.remove());
      top.list.appendChild(li);
    });
    ol.replaceWith(frag);
  });

  // Quill alignment classes → inline styles TinyMCE understands
  ['center', 'right', 'justify'].forEach(a => {
    root.querySelectorAll(`.ql-align-${a}`).forEach(el => {
      el.classList.remove(`ql-align-${a}`);
      el.style.textAlign = a;
      if (!el.className) el.removeAttribute('class');
    });
  });
  return root.innerHTML;
}

function csrfToken() {
  const input = document.querySelector('[name=csrfmiddlewaretoken]');
  if (input) return input.value;
  const m = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
  return m ? decodeURIComponent(m[1]) : '';
}

/* ── Rich text editor factory (TinyMCE) ───────────────────────────────────── */
window.initRichEditor = function(textareaId, options = {}) {
  const textarea = document.getElementById(textareaId);
  if (!textarea || typeof tinymce === 'undefined') return null;

  textarea.value = upgradeQuillHtml(textarea.value);

  const uploadUrl = textarea.dataset.uploadUrl;
  const absoluteUrls = textarea.dataset.absoluteUrls === '1';
  const headerH = parseInt(
    getComputedStyle(document.documentElement).getPropertyValue('--adm-header-h'), 10
  ) || 60;

  const uploadHandler = (blobInfo, progress) => new Promise((resolve, reject) => {
    const fd = new FormData();
    fd.append('file', blobInfo.blob(), blobInfo.filename());
    fetch(uploadUrl, {
      method: 'POST',
      body: fd,
      credentials: 'same-origin',
      headers: { 'X-CSRFToken': csrfToken() },
    })
      .then(r => r.json().then(data => ({ ok: r.ok, data })))
      .then(({ ok, data }) => {
        if (ok && data.location) resolve(data.location);
        else reject({ message: data.error || 'Image upload failed.', remove: true });
      })
      .catch(() => reject({ message: 'Image upload failed (network error).', remove: true }));
  });

  tinymce.init(Object.assign({
    target: textarea,
    license_key: 'gpl',
    promotion: false,
    branding: false,
    menubar: 'edit view insert format table tools',
    plugins: 'advlist autolink lists link image media table code fullscreen ' +
             'searchreplace visualblocks wordcount charmap anchor autoresize preview',
    toolbar: 'undo redo | blocks | bold italic underline strikethrough | forecolor backcolor | ' +
             'alignleft aligncenter alignright alignjustify | ' +
             'bullist numlist outdent indent | link image media table | ' +
             'blockquote hr | removeformat | code fullscreen',
    toolbar_mode: 'wrap',
    // Keep the toolbar pinned below the fixed admin header while the content scrolls.
    toolbar_sticky: true,
    toolbar_sticky_offset: headerH,
    min_height: 420,
    autoresize_bottom_margin: 40,
    block_formats: 'Paragraph=p; Heading 2=h2; Heading 3=h3; Heading 4=h4; Preformatted=pre',
    // Nested lists: Tab / Shift+Tab (or the indent buttons) create multi-level bullets.
    advlist_bullet_styles: 'default,circle,square',
    advlist_number_styles: 'default,lower-alpha,lower-roman,upper-alpha,upper-roman',
    lists_indent_on_tab: true,
    // Images: upload tab in the image dialog, plus paste / drag-and-drop uploads.
    images_upload_handler: uploadHandler,
    automatic_uploads: true,
    images_file_types: 'jpeg,jpg,png,gif,webp',
    image_caption: true,
    image_advtab: true,
    image_title: true,
    paste_data_images: true,
    // URLs: root-relative (/media/...) for the site; absolute for email content.
    relative_urls: false,
    remove_script_host: !absoluteUrls,
    convert_urls: true,
    // Source code editing: don't strip markup editors add by hand in the code view.
    extended_valid_elements: '*[*]',
    valid_children: '+body[style],+div[style]',
    content_style:
      'body{font-family:system-ui,-apple-system,"Segoe UI",sans-serif;font-size:15px;line-height:1.7;max-width:820px;margin:16px auto;padding:0 12px;}' +
      'img{max-width:100%;height:auto;} figure.image{display:table;margin:1em auto;} figure.image figcaption{text-align:center;font-size:13px;color:#666;}' +
      'ul,ol{padding-left:1.6em;} ul ul{list-style-type:circle;} ul ul ul{list-style-type:square;}' +
      'blockquote{border-left:3px solid #ccc;margin-left:0;padding-left:1em;color:#555;}',
    setup(editor) {
      // Keep the textarea in sync on every change so programmatic form.submit()
      // (e.g. the Publish button) never posts stale content.
      editor.on('input change undo redo SetContent ExecCommand', () => editor.save());
    },
  }, options));
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
