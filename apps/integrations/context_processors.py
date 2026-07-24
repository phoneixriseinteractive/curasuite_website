"""
CuraSuite — Integrations Context Processor
Injects SiteSettings into every template so analytics IDs, WhatsApp config,
and chatbot settings are available globally without view-level queries.

Queries directly on every request rather than caching: SiteSettings.load() is
a single indexed PK lookup, and the app runs behind multiple gunicorn worker
processes with no shared cache (no Redis in this deployment — see CLAUDE.md),
so a process-local cache made admin toggles (e.g. chatbot on/off) appear
stuck until the change happened to hit the same worker or the entry expired.
"""

from .models import SiteSettings


def site_integrations(request):
    return {"SITE_SETTINGS": SiteSettings.load()}
