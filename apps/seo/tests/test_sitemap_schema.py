"""
CuraSuite — sitemap.xml, canonical tag and JSON-LD schema tests.
"""
import json
import re

from django.test import TestCase
from django.utils import timezone

from apps.accounts.models import User
from apps.blogs.models import Blog, BlogCategory, BlogTag
from apps.pages.models import Page
from apps.products.models import Product, ProductPricing
from apps.seo.models import Redirect
from apps.seo.services import upsert_seo_metadata

LD_JSON = re.compile(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', re.S)
CANONICAL = re.compile(r'<link rel="canonical" href="([^"]*)">')


def _graphs(html: str) -> list[dict]:
    return [json.loads(m) for m in LD_JSON.findall(html)]


def _types(graph: dict) -> list[str]:
    return [node["@type"] for node in graph["@graph"]]


class SeoFixturesMixin:
    @classmethod
    def setUpTestData(cls):
        now = timezone.now()
        cls.product = Product.all_objects.create(
            key="curacms", name="CuraCMS", slug="curacms",
            tagline="Professional Website Platform", short_description="CMS for doctors.",
            status="published", published_at=now, sort_order=1,
        )
        ProductPricing.objects.create(
            product=cls.product, tier_name="Starter", price=9999, billing_cycle="yearly", sort_order=1,
        )
        ProductPricing.objects.create(
            product=cls.product, tier_name="Enterprise", price=None, billing_cycle="custom", sort_order=2,
        )
        Product.all_objects.create(
            key="curalabs", name="CuraLabs", slug="curalabs", short_description="Labs.",
            status="draft", sort_order=2,
        )
        author = User.objects.create_user(
            email="writer@example.com", password="x", first_name="Safeera", last_name="Safeeq",
        )
        cls.category = BlogCategory.all_objects.create(name="Practice Management", slug="practice-management")
        cls.blog = Blog.all_objects.create(
            title='Best Clinic "Software" in India', slug="best-clinic-software",
            excerpt="Compare features </script> before choosing.", content="<p>Body</p>",
            author=author, category=cls.category, status="published", published_at=now,
        )
        cls.blog.tags.add(BlogTag.objects.create(name="Clinic Management Software", slug="cms"))
        Blog.all_objects.create(
            title="Draft post", slug="draft-post", excerpt="x", content="x", status="draft",
        )
        Page.all_objects.create(title="About", slug="about", status="published", published_at=now)
        Page.all_objects.create(title="Home", slug="home", page_type=Page.PageType.HOME,
                                status="published", published_at=now)
        Page.all_objects.create(title="Clinics", slug="solutions/clinics", status="published",
                                published_at=now)
        hidden = Page.all_objects.create(title="Hidden", slug="hidden", status="published",
                                         published_at=now)
        upsert_seo_metadata(hidden, robots="noindex, follow")
        Page.all_objects.create(title="Old", slug="old-page", status="published", published_at=now)
        Redirect.objects.create(old_path="/old-page/", new_path="/about/")


class SitemapTest(SeoFixturesMixin, TestCase):

    def setUp(self):
        self.response = self.client.get("/sitemap.xml")
        self.xml = self.response.content.decode()

    def test_served_as_xml(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertIn("xml", self.response["Content-Type"])

    def test_lists_public_urls_on_site_domain(self):
        for url in (
            "https://curasuite.app/",
            "https://curasuite.app/products/",
            "https://curasuite.app/blog/",
            "https://curasuite.app/products/curacms/",
            "https://curasuite.app/blog/best-clinic-software/",
            "https://curasuite.app/blog/category/practice-management/",
            "https://curasuite.app/about/",
        ):
            self.assertIn(f"<loc>{url}</loc>", self.xml)

    def test_excludes_drafts_noindex_redirects_and_duplicates(self):
        for path in ("/products/curalabs/", "/blog/draft-post/", "/hidden/",
                     "/solutions/clinics/", "/old-page/", "/home/"):
            self.assertNotIn(f"https://curasuite.app{path}</loc>", self.xml)
        self.assertEqual(self.xml.count("<loc>https://curasuite.app/</loc>"), 1)


class CanonicalTest(SeoFixturesMixin, TestCase):

    def test_product_page_has_self_canonical(self):
        html = self.client.get("/products/curacms/?utm_source=ads").content.decode()
        self.assertEqual(CANONICAL.findall(html), ["https://curasuite.app/products/curacms/"])

    def test_seo_canonical_override_wins(self):
        upsert_seo_metadata(self.product, canonical_url="https://curasuite.app/products/other/")
        html = self.client.get("/products/curacms/").content.decode()
        self.assertEqual(CANONICAL.findall(html), ["https://curasuite.app/products/other/"])

    def test_paginated_listing_keeps_page_param(self):
        html = self.client.get("/blog/?page=2&foo=bar").content.decode()
        self.assertEqual(CANONICAL.findall(html), ["https://curasuite.app/blog/?page=2"])


class SchemaTest(SeoFixturesMixin, TestCase):

    def test_every_page_has_one_graph_with_sitewide_nodes(self):
        for path in ("/", "/about/", "/products/", "/blog/"):
            graphs = _graphs(self.client.get(path).content.decode())
            self.assertEqual(len(graphs), 1, path)
            self.assertEqual(_types(graphs[0])[:3], ["Organization", "LocalBusiness", "WebSite"], path)

    def test_local_business_has_real_address(self):
        graph = _graphs(self.client.get("/").content.decode())[0]
        address = graph["@graph"][1]["address"]
        self.assertNotIn("ADD YOUR", json.dumps(address))
        self.assertEqual(address["addressCountry"], "IN")

    def test_product_page_schema(self):
        graph = _graphs(self.client.get("/products/curacms/").content.decode())[0]
        self.assertEqual(_types(graph)[3:], ["SoftwareApplication", "WebPage", "BreadcrumbList"])
        software = graph["@graph"][3]
        self.assertEqual(software["@id"], "https://curasuite.app/products/curacms/#software")
        self.assertIn("Gemini-Powered AI Chatbot", software["featureList"])
        # Contact-sales tier has no price, so it is not an Offer.
        self.assertEqual([o["price"] for o in software["offers"]], ["9999"])
        self.assertEqual(graph["@graph"][4]["isPartOf"]["@id"], "https://curasuite.app/#website")

    def test_blog_post_schema_is_valid_json_and_escaped(self):
        html = self.client.get("/blog/best-clinic-software/").content.decode()
        self.assertNotIn("</script> before", html.split("<body")[0])
        graph = _graphs(html)[0]
        self.assertEqual(_types(graph)[3:], ["BlogPosting", "BreadcrumbList"])
        article = graph["@graph"][3]
        self.assertEqual(article["headline"], 'Best Clinic "Software" in India')
        self.assertEqual(article["author"], {"@type": "Person", "name": "Safeera Safeeq"})
        self.assertEqual(article["articleSection"], "Practice Management")
        self.assertIn("Clinic Management Software", article["keywords"])
        self.assertEqual(article["publisher"]["@id"], "https://curasuite.app/#organization")
        crumbs = graph["@graph"][4]["itemListElement"]
        self.assertEqual([c["name"] for c in crumbs][:2], ["Home", "Blog"])
