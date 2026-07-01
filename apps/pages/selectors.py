"""CuraSuite — Pages Selectors"""
from django.db.models import QuerySet
from .models import Page


def get_page_by_slug(slug: str) -> Page | None:
    return Page.all_objects.filter(slug=slug, deleted_at__isnull=True, is_active=True).first()

def get_home_page() -> Page | None:
    return Page.objects.filter(page_type=Page.PageType.HOME).first()

def get_all_published_pages() -> QuerySet:
    return Page.objects.order_by("slug")

def get_pages_for_sitemap() -> QuerySet:
    return Page.objects.filter(show_in_sitemap=True).order_by("slug")

def get_nav_pages() -> QuerySet:
    return Page.objects.filter(show_in_nav=True).order_by("slug")

def get_legal_pages() -> QuerySet:
    return Page.objects.filter(page_type=Page.PageType.LEGAL).order_by("title")
