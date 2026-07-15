"""CuraSuite — Landing Pages Public Views"""
from django.http import Http404
from django.shortcuts import render
from .selectors import get_landing_page_by_slug, get_testimonials_for_landing_page


def landing_page_detail(request, slug: str):
    page = get_landing_page_by_slug(slug)
    if not page or not page.is_published:
        raise Http404(f"Landing page '{slug}' not found.")

    testimonials = get_testimonials_for_landing_page(page)

    return render(request, page.template_name, {
        "lp": page,
        "product": page.product,
        "pain_points": page.pain_points.all(),
        "benefits": page.benefits.all(),
        "testimonials": testimonials,
        "pricing_tiers": page.product.pricing_tiers.order_by("sort_order"),
        "product_faqs": page.product.faqs.order_by("sort_order")[:6],
        "product_features": page.product.features.order_by("sort_order"),
        "screenshots": page.product.screenshots.order_by("sort_order")[:4] if hasattr(page.product, "screenshots") else [],
    })
