"""
CuraSuite — Integrations Context Processor
Injects SiteSettings into every template so analytics IDs, WhatsApp config,
and chatbot settings are available globally without view-level queries.
Uses per-request caching to avoid hitting the DB on every template render.
"""

from django.core.cache import cache
from .models import SiteSettings

_CACHE_KEY = "curasuite:site_settings"
_CACHE_TTL = 300  # 5 minutes


def site_integrations(request):
    settings = cache.get(_CACHE_KEY)
    if settings is None:
        settings = SiteSettings.load()
        cache.set(_CACHE_KEY, settings, _CACHE_TTL)
    return {"SITE_SETTINGS": settings}
