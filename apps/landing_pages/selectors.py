"""CuraSuite — Landing Pages Selectors"""
from .models import LandingPage


def get_landing_page_by_slug(slug: str) -> LandingPage | None:
    return (
        LandingPage.objects
        .select_related("product")
        .prefetch_related("pain_points", "benefits")
        .filter(slug=slug)
        .first()
    )


def get_all_landing_pages():
    return LandingPage.all_objects.select_related("product").order_by("product__sort_order", "slug")
