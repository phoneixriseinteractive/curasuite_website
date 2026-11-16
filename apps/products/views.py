"""CuraSuite — Products Views."""

from django.http import Http404
from django.shortcuts import render

from apps.seo.schema import product_nodes
from apps.seo.selectors import get_seo_for_object
from apps.settings_app.selectors import get_product_testimonials

from .content import get_page_content
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
    features = product.features.all()
    pricing_tiers = product.pricing_tiers.all()

    return render(request, "products/product_detail.html", {
        "product": product,
        "features": features,
        "pricing_tiers": pricing_tiers,
        "faqs": product.faqs.all(),
        "screenshots": product.screenshots.all(),
        "integrations": product.integrations.all(),
        "seo": seo,
        "testimonials": get_product_testimonials(product.name),
        "schema_nodes": product_nodes(
            product, pricing_tiers=pricing_tiers, features=features, seo=seo
        ),
        **get_page_content(product.slug),
    })
