"""CuraSuite — Root URL Configuration"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse


def robots_txt(request):
    from apps.settings_app.models import RobotsTxt
    return HttpResponse(RobotsTxt.load().content, content_type="text/plain")


urlpatterns = [
    # ── System ──────────────────────────────────────────────────────────────
    path("admin/",       admin.site.urls),
    path("manage/",      include("apps.admin_panel.urls", namespace="admin_panel")),
    path("robots.txt",   robots_txt, name="robots_txt"),

    # ── Specific app routes (registered BEFORE the pages catch-all) ─────────
    path("blog/",        include("apps.blogs.urls",      namespace="blogs")),
    path("products/",    include("apps.products.urls",   namespace="products")),
    path("contact/",     include("apps.crm.urls",        namespace="crm")),
    path("newsletter/",  include("apps.newsletter.urls", namespace="newsletter")),
    path("search/",      include("apps.core.urls",       namespace="core")),
    path("api/v1/",      include("apps.api.urls",        namespace="api_v1")),

    # ── Pages app LAST — catches / (home) and all other slugs ──────────────
    # Must be last because <path:slug> matches anything not caught above.
    path("",             include("apps.pages.urls",      namespace="pages")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
