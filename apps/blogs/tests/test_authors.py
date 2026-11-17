"""CuraSuite — Blog author profile tests"""
import io
import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from apps.blogs.models import Blog, BlogAuthor
from apps.blogs.services import create_blog, delete_author, save_author
from apps.seo.schema import blog_nodes

TMP_MEDIA = tempfile.mkdtemp()


def make_png(name="me.png"):
    buf = io.BytesIO()
    Image.new("RGB", (10, 10), "red").save(buf, format="PNG")
    return SimpleUploadedFile(name, buf.getvalue(), content_type="image/png")


@override_settings(MEDIA_ROOT=TMP_MEDIA)
class BlogAuthorServiceTest(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TMP_MEDIA, ignore_errors=True)

    def test_create_with_photo_and_unique_slug(self):
        a1 = save_author(name="Priya Sharma", designation="Cardiologist", bio="Bio.", photo=make_png())
        a2 = save_author(name="Priya Sharma")
        self.assertTrue(a1.photo.name.startswith("blog_authors/"))
        self.assertEqual(a1.slug, "priya-sharma")
        self.assertEqual(a2.slug, "priya-sharma-2")

    def test_name_required(self):
        with self.assertRaises(ValueError):
            save_author(name="   ")

    def test_invalid_photo_rejected_before_save(self):
        bad = SimpleUploadedFile("x.png", b"nope", content_type="image/png")
        with self.assertRaises(ValueError):
            save_author(name="X", photo=bad)
        self.assertFalse(BlogAuthor.all_objects.exists())

    def test_deleted_author_hidden_from_byline(self):
        author = save_author(name="Ravi")
        blog = create_blog(title="T", content="c", excerpt="e", author_profile=author)
        self.assertEqual(blog.byline, author)
        delete_author(author)
        blog = Blog.all_objects.get(pk=blog.pk)
        self.assertIsNone(blog.byline)

    def test_byline_name_never_uses_email(self):
        user = get_user_model().objects.create_user(email="secret@example.com", password="x")
        blog = create_blog(title="T", content="c", excerpt="e", created_by=user)
        self.assertEqual(blog.byline_name, "")

    def test_schema_uses_author_profile(self):
        author = save_author(name="Asha Rao", designation="Head of Product", bio="Writes about clinics.")
        blog = create_blog(title="Schema", content="c", excerpt="e", author_profile=author)
        nodes = blog_nodes(blog)
        persons = [n.get("author") for n in nodes if isinstance(n, dict) and n.get("author")]
        self.assertIn({"@type": "Person", "name": "Asha Rao", "jobTitle": "Head of Product",
                       "description": "Writes about clinics."}, persons)


@override_settings(MEDIA_ROOT=TMP_MEDIA)
class BlogAuthorAdminAndPublicTest(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TMP_MEDIA, ignore_errors=True)

    def setUp(self):
        self.staff = get_user_model().objects.create_user(
            email="staff@example.com", password="pw-12345678", is_staff=True,
        )
        self.client.force_login(self.staff)

    def test_admin_author_crud(self):
        resp = self.client.post(reverse("admin_panel:blog_author_create"), {
            "name": "Dr. Meera", "designation": "Dermatologist", "bio": "Short bio.", "photo": make_png(),
        })
        self.assertRedirects(resp, reverse("admin_panel:blog_authors"))
        author = BlogAuthor.objects.get(name="Dr. Meera")

        self.assertContains(self.client.get(reverse("admin_panel:blog_authors")), "Dr. Meera")

        self.client.post(reverse("admin_panel:blog_author_edit", args=[author.pk]), {
            "name": "Dr. Meera K", "designation": "Dermatologist", "bio": "", "remove_photo": "on",
        })
        author.refresh_from_db()
        self.assertEqual(author.name, "Dr. Meera K")
        self.assertFalse(author.photo)

        self.client.post(reverse("admin_panel:blog_author_delete", args=[author.pk]))
        self.assertFalse(BlogAuthor.objects.filter(pk=author.pk).exists())

    def test_admin_create_rejects_missing_name(self):
        resp = self.client.post(reverse("admin_panel:blog_author_create"), {"name": ""})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Author name is required.")

    def test_choose_author_on_blog_and_render_box(self):
        author = save_author(name="Kavya Iyer", designation="Clinic Growth Lead", bio="Helps clinics grow.")
        resp = self.client.get(reverse("admin_panel:blog_create"))
        self.assertContains(resp, 'name="author_profile"')
        self.assertContains(resp, "Kavya Iyer")

        self.client.post(reverse("admin_panel:blog_create"), {
            "title": "Author post", "excerpt": "Ex.", "content": "<p>Body</p>",
            "author_profile": str(author.pk),
        })
        blog = Blog.all_objects.get(title="Author post")
        self.assertEqual(blog.author_profile, author)

        # Edit: clear the author
        self.client.post(reverse("admin_panel:blog_edit", args=[blog.pk]), {
            "title": blog.title, "excerpt": blog.excerpt, "content": blog.content, "author_profile": "",
        })
        blog.refresh_from_db()
        self.assertIsNone(blog.author_profile)

        # Re-assign, publish, check the public page
        self.client.post(reverse("admin_panel:blog_edit", args=[blog.pk]), {
            "title": blog.title, "excerpt": blog.excerpt, "content": blog.content,
            "author_profile": str(author.pk), "action": "publish",
        })
        page = self.client.get(blog.get_absolute_url())
        self.assertContains(page, 'id="about-author"')
        self.assertContains(page, "Clinic Growth Lead")
        self.assertContains(page, "Helps clinics grow.")

    def test_garbage_author_id_is_ignored(self):
        self.client.post(reverse("admin_panel:blog_create"), {
            "title": "Junk", "excerpt": "Ex.", "content": "x", "author_profile": "not-a-uuid",
        })
        self.assertIsNone(Blog.all_objects.get(title="Junk").author_profile)
