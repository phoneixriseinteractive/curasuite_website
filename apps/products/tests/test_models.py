"""CuraSuite — Products Model Tests"""
from django.test import TestCase
from apps.products.models import Product, ProductPricing


class ProductModelTest(TestCase):
    def setUp(self):
        self.product = Product.all_objects.create(
            key="curacms", name="CuraCMS", tagline="For doctors",
            short_description="Great CMS.", status="published", sort_order=1,
        )

    def test_slug_auto_generated(self):
        self.assertEqual(self.product.slug, "curacms")

    def test_str(self):
        self.assertEqual(str(self.product), "CuraCMS")

    def test_is_published(self):
        self.assertTrue(self.product.is_published)

    def test_soft_delete(self):
        self.product.soft_delete()
        self.assertFalse(Product.objects.filter(pk=self.product.pk).exists())
        self.assertTrue(Product.all_objects.filter(pk=self.product.pk).exists())

    def test_audience_list(self):
        self.product.target_audience = "Doctors, Clinics"
        self.assertEqual(self.product.audience_list, ["Doctors", "Clinics"])


class ProductPricingTest(TestCase):
    def setUp(self):
        self.product = Product.all_objects.create(
            key="curalabs", name="CuraLabs", tagline="Labs",
            short_description="Lab platform.", status="published",
        )

    def test_formatted_price(self):
        tier = ProductPricing.objects.create(
            product=self.product, tier_name="Starter", price=9999, billing_cycle="yearly",
        )
        self.assertEqual(tier.formatted_price, "₹9,999")

    def test_no_price_contact_sales(self):
        tier = ProductPricing.objects.create(
            product=self.product, tier_name="Enterprise", billing_cycle="custom",
        )
        self.assertEqual(tier.formatted_price, "Contact Sales")
