"""CuraSuite — Settings App Selectors"""
from django.db.models import QuerySet

from .models import Testimonial


def get_product_testimonials(product_name: str, limit: int = 3) -> QuerySet:
    """Approved testimonials tagged with this product (Testimonial.product holds the product name)."""
    return Testimonial.objects.filter(
        status=Testimonial.Status.APPROVED, product__iexact=product_name
    ).order_by("-is_featured", "sort_order")[:limit]
