"""
CuraSuite — Products Selectors
All read/query logic for products. Views and services call these — never raw ORM.
"""

from django.db.models import Prefetch, QuerySet

from .models import Product, ProductFAQ, ProductFeature, ProductPricing, ProductScreenshot


def get_all_products() -> QuerySet:
    """Return all published products ordered by sort_order."""
    return Product.objects.order_by("sort_order", "name")


def get_product_by_slug(slug: str) -> Product | None:
    """Return a single published product by slug, or None."""
    return Product.objects.filter(slug=slug).first()


def get_product_by_key(key: str) -> Product | None:
    """Return a single published product by its key (curacms, curalabs, curasuite)."""
    return Product.objects.filter(key=key).first()


def get_product_with_full_detail(slug: str) -> Product | None:
    """
    Return a product with all related data prefetched.
    Use this for the product landing page to avoid N+1 queries.
    """
    return (
        Product.objects.filter(slug=slug)
        .prefetch_related(
            Prefetch("features", queryset=ProductFeature.objects.order_by("sort_order")),
            Prefetch("pricing_tiers", queryset=ProductPricing.objects.order_by("sort_order")),
            Prefetch("faqs", queryset=ProductFAQ.objects.order_by("sort_order")),
            Prefetch("screenshots", queryset=ProductScreenshot.objects.order_by("sort_order")),
            "integrations",
        )
        .first()
    )


def get_products_for_homepage() -> QuerySet:
    """
    Return published products with only the fields needed for the homepage cards.
    Avoids fetching heavy fields like long_description.
    """
    return Product.objects.only(
        "id", "key", "name", "slug", "tagline", "short_description", "icon", "color", "sort_order"
    ).order_by("sort_order")


def get_featured_pricing_tier(product: Product) -> ProductPricing | None:
    """Return the featured pricing tier for a product (for homepage pricing preview)."""
    return product.pricing_tiers.filter(is_featured=True).first()
