"""
CuraSuite — Core Context Processors
Injects globally-needed context into every template.
"""

from django.conf import settings

from apps.seo.schema import absolute_url, get_site_url


def canonical_url(request) -> str:
    """
    Absolute canonical URL for the current request, always on the configured
    public host (settings.SITE_URL, default https://curasuite.app) so http/www/
    staging-host variants never self-canonicalise. Query strings are dropped,
    except ``?page=N`` on paginated listings.
    """
    url = absolute_url(request.path)
    page = request.GET.get("page", "")
    if page.isdigit() and int(page) > 1:
        url += f"?page={int(page)}"
    return url


def site_settings(request):
    """Inject CuraSuite site settings into all templates."""
    return {
        "SITE_URL": get_site_url(),
        "CANONICAL_URL": canonical_url(request),
        "SITE_NAME": getattr(settings, "CURASUITE_SITE_NAME", "CuraSuite"),
        "SITE_TAGLINE": getattr(settings, "CURASUITE_SITE_TAGLINE", ""),
        "SUPPORT_EMAIL": getattr(settings, "CURASUITE_SUPPORT_EMAIL", ""),
        "DEMO_EMAIL": getattr(settings, "CURASUITE_DEMO_EMAIL", ""),
        "DEBUG": settings.DEBUG,
    }
