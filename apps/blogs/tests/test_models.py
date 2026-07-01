"""CuraSuite — Blogs Model Tests"""
from django.test import TestCase
from apps.blogs.models import Blog, BlogCategory, BlogTag
from apps.blogs.services import create_blog, submit_comment
from apps.blogs.selectors import get_blog_by_slug, get_published_blogs


class BlogModelTest(TestCase):
    def setUp(self):
        self.category = BlogCategory.all_objects.create(name="Clinic Growth")

    def test_create_blog(self):
        blog = create_blog(
            title="Why Every Doctor Needs a Website",
            content="Long content here " * 50,
            excerpt="Short excerpt.",
            category=self.category,
        )
        self.assertEqual(blog.status, "draft")
        self.assertGreater(blog.reading_time_minutes, 0)

    def test_slug_auto_generated(self):
        blog = create_blog(title="SEO for Clinics", content="Content.", excerpt="Excerpt.")
        self.assertEqual(blog.slug, "seo-for-clinics")

    def test_revision_on_create(self):
        blog = create_blog(title="Test Post", content="Body.", excerpt="Excerpt.")
        self.assertEqual(blog.revisions.count(), 1)

    def test_publish_and_selector(self):
        blog = create_blog(title="Published Post", content="Body.", excerpt="Excerpt.")
        blog.publish()
        results = get_published_blogs()
        self.assertEqual(results.count(), 1)

    def test_draft_not_in_published(self):
        create_blog(title="Draft Post", content="Body.", excerpt="Excerpt.")
        self.assertEqual(get_published_blogs().count(), 0)

    def test_reading_time_calculated(self):
        long_content = "word " * 400
        blog = create_blog(title="Long Post", content=long_content, excerpt="Short.")
        self.assertEqual(blog.reading_time_minutes, 2)

    def test_comment_submitted_pending(self):
        blog = create_blog(title="Commented Post", content="Body.", excerpt="Excerpt.")
        comment = submit_comment(
            blog=blog, author_name="John", author_email="j@test.com", content="Great article!"
        )
        self.assertEqual(comment.status, "pending")
