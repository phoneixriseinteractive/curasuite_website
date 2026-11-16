"""
CuraSuite — XML sitemap (served at /sitemap.xml, see config/urls.py).

One flat sitemap built from:
  - fixed public routes (home, product/blog listings, contact)
  - CMS pages with ``show_in_sitemap`` (excluding the home page, served at /)
  - published products, published blog posts, active blog categories

URLs are always emitted on settings.SITE_URL (https://curasuite.app), never the
request host. Anything marked ``noindex`` via SEO metadata, or whose path is a
redirect source (admin-managed Redirects or code-level RedirectViews), is
left out so the sitemap only lists canonical, indexable URLs. Landing pages
(/lp/) are intentionally excluded.
"""

from __future__ import annotations

from urllib.parse import urlsplit

from django.contrib.contenttypes.models import ContentType
from django.contrib.sitemaps import Sitemap

from apps.seo.models import Redirect, SEOMetadata
from apps.seo.schema import get_site_url

# Paths that 301 elsewhere via RedirectView in apps/*/urls.py.
CODE_REDIRECT_PATHS = {"/solutions/clinics/", "/products/curasuite/"}

STATIC_ENTRIES = [
    # (path, changefreq, priority)
    ("/", "weekly", 1.0),
    ("/products/", "monthly", 0.9),
    ("/blog/", "daily", 0.8),
    ("/contact/", "yearly", 0.6),
]


def _noindex_ids(model) -> set:
    ct = ContentType.objects.get_for_model(model)
    return set(
        SEOMetadata.objects.filter(content_type=ct, robots__startswith="noindex").values_list(
            "object_id", flat=True
        )
    )


class SiteSitemap(Sitemap):
    protocol = urlsplit(get_site_url()).scheme or "https"

    def get_domain(self, site=None):
        return urlsplit(get_site_url()).netloc

    def items(self) -> list[dict]:
        from apps.blogs.models import Blog, BlogCategory
        from apps.pages.models import Page
        from apps.pages.selectors import get_pages_for_sitemap
        from apps.products.models import Product
        from apps.products.selectors import get_all_products

        entries: list[dict] = [
            {"path": path, "lastmod": None, "changefreq": freq, "priority": prio}
            for path, freq, prio in STATIC_ENTRIES
        ]

        hidden = _noindex_ids(Page)
        for page in get_pages_for_sitemap().exclude(page_type=Page.PageType.HOME):
            if page.pk in hidden:
                continue
            priority = 0.8 if page.slug.startswith("solutions/") or page.slug == "pricing" else 0.5
            if page.page_type == Page.PageType.LEGAL:
                priority = 0.3
            entries.append({
                "path": page.get_absolute_url(), "lastmod": page.updated_at,
                "changefreq": "monthly", "priority": priority,
            })

        hidden = _noindex_ids(Product)
        for product in get_all_products():
            if product.pk in hidden:
                continue
            entries.append({
                "path": product.get_absolute_url(), "lastmod": product.updated_at,
                "changefreq": "weekly", "priority": 0.9,
            })

        hidden = _noindex_ids(Blog)
        for blog in Blog.objects.only("id", "slug", "updated_at").order_by("-published_at"):
            if blog.pk in hidden:
                continue
            entries.append({
                "path": blog.get_absolute_url(), "lastmod": blog.updated_at,
                "changefreq": "monthly", "priority": 0.7,
            })

        for category in BlogCategory.objects.filter(posts__in=Blog.objects.all()).distinct():
            entries.append({
                "path": category.get_absolute_url(), "lastmod": category.updated_at,
                "changefreq": "weekly", "priority": 0.4,
            })

        excluded = CODE_REDIRECT_PATHS | set(
            Redirect.objects.filter(is_active=True).values_list("old_path", flat=True)
        )
        seen: set[str] = set()
        unique = []
        for entry in entries:
            path = entry["path"]
            if path in seen or path in excluded:
                continue
            seen.add(path)
            unique.append(entry)
        return unique

    def location(self, item):
        return item["path"]

    def lastmod(self, item):
        return item["lastmod"]

    def changefreq(self, item):
        return item["changefreq"]

    def priority(self, item):
        return item["priority"]


SITEMAPS = {"site": SiteSitemap}
