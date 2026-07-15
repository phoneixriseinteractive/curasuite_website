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


def get_testimonials_for_landing_page(page: LandingPage, limit: int = 3):
    """
    Testimonials for one ad landing page — restricted to the same product AND the same
    specialty/vertical as the page. A visitor who clicked a dentist ad and lands on a page
    quoting a physiotherapist reads it as a generic template — it kills message-match trust,
    so this deliberately never falls back to a different vertical or an unrelated
    'is_featured' testimonial just to fill the slot.
    """
    from apps.settings_app.models import Testimonial

    testimonials = Testimonial.objects.filter(
        status="approved", product=page.product.name, specialty=page.specialty,
    ).order_by("sort_order")[:limit]

    if not testimonials and page.specialty:
        # No specialty-tagged testimonial yet for this vertical — fall back to an untagged,
        # general testimonial for the same product only (never a different vertical).
        testimonials = Testimonial.objects.filter(
            status="approved", product=page.product.name, specialty="",
        ).order_by("sort_order")[:limit]

    return testimonials
