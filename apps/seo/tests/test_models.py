"""CuraSuite — SEO Model Tests"""
from django.test import TestCase
from apps.products.models import Product
from apps.seo.models import Redirect
from apps.seo.selectors import get_redirect_for_path, get_seo_for_object
from apps.seo.services import upsert_seo_metadata


class SEOMetadataTest(TestCase):
    def setUp(self):
        self.product = Product.all_objects.create(
            key="curacms", name="CuraCMS", tagline="Test",
            short_description="Test.", status="published",
        )

    def test_upsert_creates(self):
        seo = upsert_seo_metadata(self.product, seo_title="CuraCMS | CuraSuite")
        self.assertEqual(seo.seo_title, "CuraCMS | CuraSuite")

    def test_upsert_is_idempotent(self):
        upsert_seo_metadata(self.product, seo_title="Old")
        upsert_seo_metadata(self.product, seo_title="New")
        from apps.seo.models import SEOMetadata
        self.assertEqual(SEOMetadata.objects.count(), 1)
        self.assertEqual(SEOMetadata.objects.first().seo_title, "New")

    def test_get_seo_for_object(self):
        upsert_seo_metadata(self.product, seo_title="Test SEO")
        result = get_seo_for_object(self.product)
        self.assertIsNotNone(result)

    def test_get_title_fallback(self):
        seo = upsert_seo_metadata(self.product, seo_title="")
        self.assertEqual(seo.get_title("Fallback"), "Fallback")


class RedirectTest(TestCase):
    def test_create(self):
        r = Redirect.objects.create(old_path="/old/", new_path="/new/")
        self.assertIn("/old/", str(r))

    def test_active_redirect_found(self):
        Redirect.objects.create(old_path="/moved/", new_path="/here/", is_active=True)
        self.assertIsNotNone(get_redirect_for_path("/moved/"))

    def test_inactive_not_found(self):
        Redirect.objects.create(old_path="/gone/", new_path="/here/", is_active=False)
        self.assertIsNone(get_redirect_for_path("/gone/"))
