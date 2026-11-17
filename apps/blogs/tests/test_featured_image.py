"""CuraSuite — Blog featured image + rich text editor upload tests"""
import io
import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from apps.blogs.models import Blog
from apps.blogs.services import create_blog, set_featured_image

TMP_MEDIA = tempfile.mkdtemp()


def make_png(name="photo.png"):
    buf = io.BytesIO()
    Image.new("RGB", (20, 10), "blue").save(buf, format="PNG")
    return SimpleUploadedFile(name, buf.getvalue(), content_type="image/png")


@override_settings(MEDIA_ROOT=TMP_MEDIA)
class FeaturedImageServiceTest(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TMP_MEDIA, ignore_errors=True)

    def setUp(self):
        self.blog = create_blog(title="Hello", content="<p>Body</p>", excerpt="Ex.")

    def test_sets_image_and_alt(self):
        set_featured_image(self.blog, image=make_png(), alt_text="A blue box")
        self.blog.refresh_from_db()
        self.assertTrue(self.blog.featured_image.name.startswith("blogs/"))
        self.assertEqual(self.blog.featured_image_alt, "A blue box")

    def test_remove_image(self):
        set_featured_image(self.blog, image=make_png())
        set_featured_image(self.blog, remove=True)
        self.blog.refresh_from_db()
        self.assertFalse(self.blog.featured_image)

    def test_rejects_non_image_bytes(self):
        fake = SimpleUploadedFile("x.png", b"not an image", content_type="image/png")
        with self.assertRaises(ValueError):
            set_featured_image(self.blog, image=fake)

    def test_rejects_svg(self):
        svg = SimpleUploadedFile("x.svg", b"<svg onload='alert(1)'/>", content_type="image/svg+xml")
        with self.assertRaises(ValueError):
            set_featured_image(self.blog, image=svg)


@override_settings(MEDIA_ROOT=TMP_MEDIA)
class AdminBlogImageViewsTest(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TMP_MEDIA, ignore_errors=True)

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="staff@example.com", password="pw-12345678", is_staff=True,
        )
        self.client.force_login(self.user)

    def test_create_post_with_featured_image(self):
        resp = self.client.post(reverse("admin_panel:blog_create"), {
            "title": "With image", "excerpt": "Ex.", "content": "<ul><li>a<ul><li>b</li></ul></li></ul>",
            "featured_image": make_png(), "featured_image_alt": "Alt",
        })
        self.assertEqual(resp.status_code, 302)
        blog = Blog.all_objects.get(title="With image")
        self.assertTrue(blog.featured_image)
        self.assertEqual(blog.featured_image_alt, "Alt")
        self.assertIn("<ul><li>b</li></ul>", blog.content)

    def test_edit_form_renders_editor_and_image_field(self):
        blog = create_blog(title="Edit me", content="<p>x</p>", excerpt="Ex.")
        resp = self.client.get(reverse("admin_panel:blog_edit", args=[blog.pk]))
        self.assertContains(resp, 'enctype="multipart/form-data"')
        self.assertContains(resp, 'name="featured_image"')
        self.assertContains(resp, "tinymce")

    def test_editor_upload_returns_location(self):
        resp = self.client.post(reverse("admin_panel:editor_image_upload"), {"file": make_png()})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()["location"].startswith("/media/"))

    def test_editor_upload_rejects_bad_file(self):
        bad = SimpleUploadedFile("x.png", b"nope", content_type="image/png")
        resp = self.client.post(reverse("admin_panel:editor_image_upload"), {"file": bad})
        self.assertEqual(resp.status_code, 400)
        self.assertIn("error", resp.json())

    def test_editor_upload_requires_staff(self):
        self.client.logout()
        resp = self.client.post(reverse("admin_panel:editor_image_upload"), {"file": make_png()})
        self.assertEqual(resp.status_code, 302)
