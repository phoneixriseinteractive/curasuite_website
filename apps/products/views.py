"""CuraSuite — Products Views."""

from django.http import Http404
from django.shortcuts import render

from apps.seo.selectors import get_seo_for_object

from .selectors import get_all_products, get_product_with_full_detail


def product_list(request):
    """All products listing page."""
    products = get_all_products()
    return render(request, "products/product_list.html", {"products": products})


def product_detail(request, slug: str):
    """
    Product landing page.
    Fetches full product detail with all related data in a single query set.
    """
    product = get_product_with_full_detail(slug)
    if not product:
        raise Http404(f"Product '{slug}' not found.")

    seo = get_seo_for_object(product)

    return render(request, "products/product_detail.html", {
        "product": product,
        "features": product.features.all(),
        "pricing_tiers": product.pricing_tiers.all(),
        "faqs": product.faqs.all(),
        "screenshots": product.screenshots.all(),
        "integrations": product.integrations.all(),
        "seo": seo,
    })
