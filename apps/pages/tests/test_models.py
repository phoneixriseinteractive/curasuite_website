"""CuraSuite — Pages Model Tests"""
from django.test import TestCase
from apps.pages.models import Page
from apps.pages.services import create_page, update_page
from apps.pages.selectors import get_page_by_slug, get_home_page


class PageModelTest(TestCase):
    def test_create_page(self):
        page = create_page(title="About Us", content="<p>About.</p>", page_type="about")
        self.assertEqual(page.version, 1)
        self.assertEqual(page.slug, "about-us")
        self.assertEqual(page.status, "draft")

    def test_revision_created_on_create(self):
        page = create_page(title="Privacy Policy", page_type="legal")
        self.assertEqual(page.revisions.count(), 1)

    def test_revision_incremented_on_update(self):
        page = create_page(title="Contact", page_type="contact")
        update_page(page, title="Contact Us", content="Updated content")
        self.assertEqual(page.version, 2)
        self.assertEqual(page.revisions.count(), 2)

    def test_get_page_by_slug(self):
        create_page(title="Pricing", page_type="pricing")
        page = get_page_by_slug("pricing")
        self.assertIsNotNone(page)

    def test_soft_delete(self):
        page = create_page(title="Draft Page")
        page.soft_delete()
        self.assertFalse(Page.objects.filter(slug="draft-page").exists())
        self.assertTrue(Page.all_objects.filter(slug="draft-page").exists())

    def test_breadcrumbs_single_page(self):
        page = create_page(title="About")
        page.status = "published"
        page.save()
        crumbs = page.breadcrumbs
        self.assertEqual(crumbs[0]["title"], "Home")
        self.assertEqual(crumbs[-1]["title"], "About")
