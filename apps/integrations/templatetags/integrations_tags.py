"""
CuraSuite — Integrations Template Tags

Usage in templates:
  {% load integrations_tags %}
  {% gtm_head %}         — GTM <script> in <head>
  {% gtm_body %}         — GTM <noscript> immediately after <body>
  {% ga4_tag %}          — GA4 gtag.js snippet (if GTM not used)
  {% meta_pixel_tag %}   — Meta Pixel base code
  {% clarity_tag %}      — Microsoft Clarity snippet
  {% whatsapp_widget %}  — Floating WhatsApp button
  {% chatbot_widget %}   — AI chatbot widget shell
  {% captcha_scripts %}  — reCAPTCHA / Turnstile script tags
"""

from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe

register = template.Library()


def _get_settings(context):
    return context.get("SITE_SETTINGS")


@register.simple_tag(takes_context=True)
def gtm_head(context):
    s = _get_settings(context)
    if not s or not s.gtm_container_id:
        return ""
    cid = s.gtm_container_id
    return mark_safe(f"""<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':
new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
}})(window,document,'script','dataLayer','{cid}');</script>
<!-- End Google Tag Manager -->""")


@register.simple_tag(takes_context=True)
def gtm_body(context):
    s = _get_settings(context)
    if not s or not s.gtm_container_id:
        return ""
    cid = s.gtm_container_id
    return mark_safe(f"""<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id={cid}"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->""")


@register.simple_tag(takes_context=True)
def ga4_tag(context):
    """Standalone GA4 tag — only use if GTM is NOT configured."""
    s = _get_settings(context)
    if not s or not s.ga4_measurement_id or s.gtm_container_id:
        return ""
    mid = s.ga4_measurement_id
    return mark_safe(f"""<!-- Google Analytics 4 -->
<script async src="https://www.googletagmanager.com/gtag/js?id={mid}"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}
gtag('js',new Date());gtag('config','{mid}');</script>""")


@register.simple_tag(takes_context=True)
def meta_pixel_tag(context):
    s = _get_settings(context)
    if not s or not s.meta_pixel_id:
        return ""
    pid = s.meta_pixel_id
    return mark_safe(f"""<!-- Meta Pixel Code -->
<script>!function(f,b,e,v,n,t,s){{if(f.fbq)return;n=f.fbq=function(){{n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)}};if(!f._fbq)f._fbq=n;
n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}}(window,
document,'script','https://connect.facebook.net/en_US/fbevents.js');
fbq('init','{pid}');fbq('track','PageView');</script>
<noscript><img height="1" width="1" style="display:none"
src="https://www.facebook.com/tr?id={pid}&ev=PageView&noscript=1"/></noscript>
<!-- End Meta Pixel Code -->""")


@register.simple_tag(takes_context=True)
def clarity_tag(context):
    s = _get_settings(context)
    if not s or not s.clarity_project_id:
        return ""
    pid = s.clarity_project_id
    return mark_safe(f"""<!-- Microsoft Clarity -->
<script type="text/javascript">(function(c,l,a,r,i,t,y){{
c[a]=c[a]||function(){{(c[a].q=c[a].q||[]).push(arguments)}};
t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
}})(window,document,"clarity","script","{pid}");</script>""")


@register.simple_tag(takes_context=True)
def whatsapp_widget(context):
    s = _get_settings(context)
    if not s or not s.whatsapp_enabled or not s.whatsapp_phone:
        return ""
    import urllib.parse
    phone   = s.whatsapp_phone.replace("+", "").replace(" ", "")
    message = urllib.parse.quote(s.whatsapp_message or "")
    tooltip = s.whatsapp_tooltip or "Chat with us"
    wa_url  = f"https://wa.me/{phone}?text={message}"
    return mark_safe(f"""<!-- CuraSuite WhatsApp Widget -->
<div id="cs-whatsapp" style="position:fixed;bottom:24px;right:90px;z-index:999;display:flex;flex-direction:column;align-items:flex-end;gap:8px;">
  <div id="cs-wa-tooltip" style="background:#1F2937;color:white;padding:6px 12px;border-radius:8px;font-size:13px;white-space:nowrap;opacity:0;transition:opacity .2s;pointer-events:none;">{tooltip}</div>
  <a href="{wa_url}" target="_blank" rel="noopener noreferrer" aria-label="{tooltip}" data-wa-placement="floating_widget"
     onmouseenter="document.getElementById('cs-wa-tooltip').style.opacity='1'"
     onmouseleave="document.getElementById('cs-wa-tooltip').style.opacity='0'"
     style="width:56px;height:56px;background:#25D366;border-radius:50%;display:flex;align-items:center;justify-content:center;box-shadow:0 4px 12px rgba(0,0,0,.2);transition:transform .2s;"
     onmouseenter="this.style.transform='scale(1.1)'" onmouseleave="this.style.transform='scale(1)'">
    <svg width="28" height="28" viewBox="0 0 24 24" fill="white" aria-hidden="true">
      <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/>
    </svg>
  </a>
</div>""")


@register.simple_tag(takes_context=True)
def chatbot_widget(context):
    s = _get_settings(context)
    if not s or not s.chatbot_enabled:
        return ""
    name     = s.chatbot_name
    greeting = s.chatbot_greeting
    return mark_safe(f"""<!-- CuraSuite AI Chatbot Widget -->
<div id="cs-chatbot" x-data="chatbot()" style="position:fixed;bottom:24px;left:24px;z-index:998;">
  <!-- Toggle button -->
  <button @click="open=!open" aria-label="Open chat assistant"
    style="width:56px;height:56px;background:var(--color-primary-600);color:white;border:none;border-radius:50%;cursor:pointer;box-shadow:0 4px 12px rgba(0,0,0,.2);display:flex;align-items:center;justify-content:center;font-size:24px;">
    <span x-show="!open">💬</span><span x-show="open" x-cloak>✕</span>
  </button>
  <!-- Chat window -->
  <div x-show="open" x-cloak x-transition
    style="position:absolute;bottom:68px;left:0;width:340px;max-width:calc(100vw - 48px);height:min(480px, calc(100vh - 140px));background:white;border-radius:16px;box-shadow:0 8px 32px rgba(0,0,0,.15);display:flex;flex-direction:column;overflow:hidden;border:1px solid var(--border-default);">
    <!-- Header -->
    <div style="flex-shrink:0;background:var(--color-primary-600);color:white;padding:14px 16px;display:flex;align-items:center;gap:10px;">
      <div style="width:36px;height:36px;background:white;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:18px;">🤖</div>
      <div><div style="font-weight:600;font-size:14px;">{name}</div><div style="font-size:11px;opacity:.8;">Online</div></div>
    </div>
    <!-- Messages -->
    <div id="cs-chat-messages" style="flex:1;min-height:0;overflow-y:auto;overscroll-behavior:contain;padding:16px;display:flex;flex-direction:column;gap:10px;">
      <div style="background:var(--color-primary-50);border-radius:12px 12px 12px 0;padding:10px 14px;font-size:13px;max-width:85%;color:var(--text-primary);">{greeting}</div>
      <template x-for="msg in messages" :key="msg.id">
        <div :style="msg.role==='user' ? 'align-self:flex-end;' : 'align-self:flex-start;'">
          <div :style="msg.role==='user'
            ? 'background:var(--color-primary-600);color:white;border-radius:12px 12px 0 12px;padding:10px 14px;font-size:13px;max-width:260px;'
            : 'background:var(--color-gray-100);color:var(--text-primary);border-radius:12px 12px 12px 0;padding:10px 14px;font-size:13px;max-width:260px;'"
            x-text="msg.content"></div>
        </div>
      </template>
      <div x-show="loading" style="align-self:flex-start;">
        <div style="background:var(--color-gray-100);border-radius:12px;padding:10px 14px;font-size:13px;">Thinking…</div>
      </div>
    </div>
    <!-- Input -->
    <div style="flex-shrink:0;padding:12px;border-top:1px solid var(--border-default);display:flex;gap:8px;">
      <input x-model="inputText" @keydown.enter.prevent="sendMessage()"
        type="text" placeholder="Type a message…"
        style="flex:1;border:1px solid var(--border-strong);border-radius:8px;padding:8px 12px;font-size:13px;outline:none;"
        :disabled="loading">
      <button @click="sendMessage()" :disabled="loading || !inputText.trim()"
        style="background:var(--color-primary-600);color:white;border:none;border-radius:8px;padding:8px 14px;font-size:13px;cursor:pointer;white-space:nowrap;"
        :style="(loading || !inputText.trim()) && 'opacity:.5;cursor:not-allowed;'">Send</button>
    </div>
  </div>
</div>
<script>
function chatbot() {{
  return {{
    open: false,
    loading: false,
    inputText: '',
    messages: [],
    msgId: 0,
    async sendMessage() {{
      const text = this.inputText.trim();
      if (!text || this.loading) return;
      this.messages.push({{ id: ++this.msgId, role: 'user', content: text }});
      this.inputText = '';
      this.loading = true;
      this.$nextTick(() => {{ const el = document.getElementById('cs-chat-messages'); if(el) el.scrollTop = el.scrollHeight; }});
      try {{
        const res = await fetch('/api/v1/chatbot/message/', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') }},
          body: JSON.stringify({{ message: text, history: this.messages.slice(-6) }})
        }});
        const data = await res.json();
        this.messages.push({{ id: ++this.msgId, role: 'assistant', content: data.reply || 'Sorry, I had trouble with that. Please try again.' }});
      }} catch(e) {{
        this.messages.push({{ id: ++this.msgId, role: 'assistant', content: 'Something went wrong. Please try again.' }});
      }}
      this.loading = false;
      this.$nextTick(() => {{ const el = document.getElementById('cs-chat-messages'); if(el) el.scrollTop = el.scrollHeight; }});
    }}
  }};
}}
function getCookie(name) {{
  const v = document.cookie.match('(^|;) ?' + name + '=([^;]*)(;|$)');
  return v ? v[2] : null;
}}
</script>""")


@register.simple_tag(takes_context=True)
def captcha_scripts(context):
    s = _get_settings(context)
    if not s or not s.captcha_enabled or not s.captcha_site_key:
        return ""
    if s.captcha_provider == "turnstile":
        return mark_safe('<script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async defer></script>')
    return mark_safe(f'<script src="https://www.google.com/recaptcha/api.js?render={s.captcha_site_key}" async defer></script>')
