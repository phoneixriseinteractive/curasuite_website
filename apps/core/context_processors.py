"""
CuraSuite — Core Context Processors
Injects globally-needed context into every template.
"""

from django.conf import settings


def site_settings(request):
    """Inject CuraSuite site settings into all templates."""
    return {
        "SITE_NAME": getattr(settings, "CURASUITE_SITE_NAME", "CuraSuite"),
        "SITE_TAGLINE": getattr(settings, "CURASUITE_SITE_TAGLINE", ""),
        "SUPPORT_EMAIL": getattr(settings, "CURASUITE_SUPPORT_EMAIL", ""),
        "DEMO_EMAIL": getattr(settings, "CURASUITE_DEMO_EMAIL", ""),
        "DEBUG": settings.DEBUG,
    }
