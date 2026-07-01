"""
CuraSuite — Products Services
Business logic for product management.
Views should call these — never put business logic in views.
"""

import logging

from django.db import transaction

from apps.seo.services import upsert_seo_metadata

from .models import Product, ProductFAQ, ProductFeature, ProductPricing, ProductScreenshot

logger = logging.getLogger(__name__)


@transaction.atomic
def publish_product(product: Product, published_by=None) -> Product:
    """Publish a product and log the action."""
    product.publish(published_by=published_by)
    logger.info("Product published: %s (by %s)", product.name, published_by)
    return product


@transaction.atomic
def create_product(
    *,
    key: str,
    name: str,
    tagline: str,
    short_description: str,
    long_description: str = "",
    target_audience: str = "",
    color: str = "#2563EB",
    sort_order: int = 0,
    created_by=None,
    seo: dict | None = None,
) -> Product:
    """
    Create a new product with optional SEO metadata.

    Args:
        key: Unique product key (curacms, curalabs, curasuite)
        name: Display name
        tagline: One-line value proposition
        short_description: Used in cards and metadata fallback
        long_description: Full description for landing page
        target_audience: Comma-separated audience list
        color: Brand hex color
        sort_order: Display order
        created_by: User instance
        seo: Dict of SEOMetadata fields to create alongside the product

    Returns:
        Created Product instance
    """
    product = Product.all_objects.create(
        key=key,
        name=name,
        tagline=tagline,
        short_description=short_description,
        long_description=long_description,
        target_audience=target_audience,
        color=color,
        sort_order=sort_order,
        created_by=created_by,
    )

    if seo:
        upsert_seo_metadata(product, **seo)

    logger.info("Product created: %s", product.name)
    return product


def add_feature(
    product: Product,
    *,
    title: str,
    description: str,
    icon_name: str = "",
    is_highlighted: bool = False,
    sort_order: int = 0,
) -> ProductFeature:
    """Add a feature to a product."""
    return ProductFeature.objects.create(
        product=product,
        title=title,
        description=description,
        icon_name=icon_name,
        is_highlighted=is_highlighted,
        sort_order=sort_order,
    )


def add_pricing_tier(
    product: Product,
    *,
    tier_name: str,
    price=None,
    billing_cycle: str = "monthly",
    description: str = "",
    features_included: str = "",
    is_featured: bool = False,
    cta_text: str = "Get Started",
    cta_url: str = "",
    sort_order: int = 0,
) -> ProductPricing:
    """Add a pricing tier to a product."""
    return ProductPricing.objects.create(
        product=product,
        tier_name=tier_name,
        price=price,
        billing_cycle=billing_cycle,
        description=description,
        features_included=features_included,
        is_featured=is_featured,
        cta_text=cta_text,
        cta_url=cta_url,
        sort_order=sort_order,
    )


def add_faq(
    product: Product,
    *,
    question: str,
    answer: str,
    sort_order: int = 0,
) -> ProductFAQ:
    """Add a FAQ to a product."""
    return ProductFAQ.objects.create(
        product=product,
        question=question,
        answer=answer,
        sort_order=sort_order,
    )
