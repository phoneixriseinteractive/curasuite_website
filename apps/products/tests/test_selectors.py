"""
CuraSuite — Products Selector Tests
"""
from django.test import TestCase

from apps.products.models import Product
from apps.products.selectors import (
    get_all_products,
    get_product_by_key,
    get_product_by_slug,
    get_product_with_full_detail,
)


class ProductSelectorsTest(TestCase):

    def setUp(self):
        self.product = Product.all_objects.create(
            key="curacms", name="CuraCMS",
            tagline="For doctors", short_description="Great CMS.",
            status="published", sort_order=1,
        )
        # Unpublished product should not appear in default queries
        Product.all_objects.create(
            key="curalabs", name="CuraLabs",
            tagline="For labs", short_description="Lab platform.",
            status="draft", sort_order=2,
        )

    def test_get_all_products_returns_only_published(self):
        products = get_all_products()
        self.assertEqual(products.count(), 1)
        self.assertEqual(products.first().key, "curacms")

    def test_get_product_by_slug(self):
        result = get_product_by_slug("curacms")
        self.assertIsNotNone(result)
        self.assertEqual(result.name, "CuraCMS")

    def test_get_product_by_slug_not_found(self):
        result = get_product_by_slug("nonexistent")
        self.assertIsNone(result)

    def test_get_product_by_key(self):
        result = get_product_by_key("curacms")
        self.assertIsNotNone(result)

    def test_get_product_with_full_detail(self):
        result = get_product_with_full_detail("curacms")
        self.assertIsNotNone(result)
        # Prefetched relations should be accessible without extra queries
        _ = list(result.features.all())
        _ = list(result.faqs.all())
        _ = list(result.pricing_tiers.all())
