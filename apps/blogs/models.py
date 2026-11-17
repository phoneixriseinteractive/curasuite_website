"""
CuraSuite — Blogs Models

Full blog engine with categories, tags, authors, comments, and SEO.
Blog posts use VersionedModel for draft/review/published workflow + revision history.

Models:
  BlogCategory  — hierarchical content categories
  BlogTag       — flat tagging system
  BlogAuthor    — public author profile (name, designation, bio, photo) shown on posts
  Blog          — the article itself
  BlogRevision  — version snapshot per save
  BlogComment   — moderated reader comments
"""

from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from apps.core.models import AuditedModel, TimeStampedModel, UUIDModel, VersionedModel


class BlogCategory(AuditedModel):
    """Hierarchical blog category. Supports parent/child nesting (one level deep)."""

    name        = models.CharField(max_length=100, verbose_name=_("Name"))
    slug        = models.SlugField(max_length=120, unique=True, db_index=True)
    description = models.TextField(max_length=300, blank=True)
    parent      = models.ForeignKey(
        "self", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="children",
    )
    sort_order = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        db_table = "blog_categories"
        verbose_name = _("Blog Category")
        verbose_name_plural = _("Blog Categories")
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("blogs:category", kwargs={"slug": self.slug})


class BlogTag(UUIDModel):
    """Flat tag for cross-cutting blog topics."""

    name = models.CharField(max_length=50, unique=True, verbose_name=_("Name"))
    slug = models.SlugField(max_length=60, unique=True, db_index=True)

    class Meta:
        db_table = "blog_tags"
        verbose_name = _("Blog Tag")
        verbose_name_plural = _("Blog Tags")
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("blogs:tag", kwargs={"slug": self.slug})


class BlogAuthor(AuditedModel):
    """
    Public-facing author profile shown in the byline and the author box on each post.

    Deliberately separate from the User account (Blog.author): bylines can credit people
    who never log in to /manage/ (guest writers, doctors), and a profile holds public
    bio/photo data that doesn't belong on a login account.
    """

    name        = models.CharField(max_length=120, verbose_name=_("Name"))
    slug        = models.SlugField(max_length=140, unique=True, db_index=True)
    designation = models.CharField(
        max_length=150, blank=True, verbose_name=_("Designation"),
        help_text=_("e.g. 'Head of Product, CuraSuite' or 'MBBS, MD — Cardiologist'."),
    )
    bio         = models.TextField(max_length=600, blank=True, verbose_name=_("Short bio"))
    photo       = models.ImageField(upload_to="blog_authors/", null=True, blank=True, verbose_name=_("Photo"))
    sort_order  = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        db_table = "blog_authors"
        verbose_name = _("Blog Author")
        verbose_name_plural = _("Blog Authors")
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name) or "author"
            slug, n = base, 2
            while BlogAuthor.all_objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug, n = f"{base}-{n}", n + 1
            self.slug = slug
        super().save(*args, **kwargs)


class Blog(VersionedModel):
    """
    A blog article. Inherits VersionedModel for full publishing workflow.
    Default manager (objects) returns only published, active posts.
    Use Blog.all_objects for admin/draft views.
    """

    # ── Identity ──────────────────────────────────────────────────────────────
    title         = models.CharField(max_length=200, verbose_name=_("Title"))
    slug          = models.SlugField(max_length=220, unique=True, db_index=True)
    author        = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="blog_posts",
        verbose_name=_("Author"),
        help_text=_("Account that created the post. The public byline uses author_profile."),
    )
    author_profile = models.ForeignKey(
        "BlogAuthor", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="posts",
        verbose_name=_("Author profile"),
        help_text=_("Public author shown in the byline and author box."),
    )

    # ── Content ───────────────────────────────────────────────────────────────
    excerpt       = models.TextField(
        max_length=500, verbose_name=_("Excerpt"),
        help_text=_("Displayed in listings, OG cards, and as meta description fallback."),
    )
    content       = models.TextField(verbose_name=_("Content"), help_text=_("Full article HTML/Markdown."))
    featured_image = models.ImageField(
        upload_to="blogs/", null=True, blank=True,
        verbose_name=_("Featured image"),
    )
    featured_image_alt = models.CharField(max_length=200, blank=True, verbose_name=_("Image alt text"))

    # ── Taxonomy ──────────────────────────────────────────────────────────────
    category = models.ForeignKey(
        BlogCategory, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="posts",
        verbose_name=_("Category"),
    )
    tags = models.ManyToManyField(BlogTag, blank=True, related_name="posts", verbose_name=_("Tags"))

    # ── Metadata ──────────────────────────────────────────────────────────────
    reading_time_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Reading time (minutes)"),
        help_text=_("Auto-calculated on save. Override if needed."),
    )
    is_featured = models.BooleanField(
        default=False, db_index=True,
        verbose_name=_("Featured post"),
        help_text=_("Featured posts appear in the hero section of the blog listing."),
    )
    allow_comments = models.BooleanField(default=True, verbose_name=_("Allow comments"))
    view_count     = models.PositiveIntegerField(default=0, verbose_name=_("View count"))

    class Meta:
        db_table = "blogs"
        verbose_name = _("Blog Post")
        verbose_name_plural = _("Blog Posts")
        ordering = ["-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["status", "published_at"]),
            models.Index(fields=["category", "status"]),
            models.Index(fields=["is_featured", "status"]),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.reading_time_minutes and self.content:
            word_count = len(self.content.split())
            self.reading_time_minutes = max(1, round(word_count / 200))
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("blogs:detail", kwargs={"slug": self.slug})

    @property
    def byline(self):
        """The public author profile, or None if unset or the profile was deleted."""
        p = self.author_profile
        return p if p is not None and p.is_active and p.deleted_at is None else None

    @property
    def byline_name(self) -> str:
        """Public author name: the profile, else the account's real name. Never the
        email address (User.full_name falls back to it, which must not be published)."""
        if self.byline:
            return self.byline.name
        if self.author:
            return f"{self.author.first_name} {self.author.last_name}".strip()
        return ""

    def increment_view_count(self):
        Blog.all_objects.filter(pk=self.pk).update(view_count=models.F("view_count") + 1)


class BlogRevision(UUIDModel):
    """Immutable snapshot of a blog post's content on each save."""

    blog            = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="revisions")
    title           = models.CharField(max_length=200)
    content         = models.TextField()
    revision_number = models.PositiveIntegerField()
    editor          = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="blog_revisions",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "blog_revisions"
        verbose_name = _("Blog Revision")
        ordering = ["-revision_number"]
        unique_together = [("blog", "revision_number")]

    def __str__(self):
        return f"{self.blog.title} — v{self.revision_number}"


class BlogComment(TimeStampedModel):
    """Reader comment on a blog post. Requires moderation before display."""

    class Status(models.TextChoices):
        PENDING  = "pending",  _("Pending Moderation")
        APPROVED = "approved", _("Approved")
        SPAM     = "spam",     _("Spam")

    blog        = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="comments")
    author_name = models.CharField(max_length=100, verbose_name=_("Name"))
    author_email= models.EmailField(verbose_name=_("Email"))
    content     = models.TextField(max_length=2000, verbose_name=_("Comment"))
    status      = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING, db_index=True)
    ip_address  = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        db_table = "blog_comments"
        verbose_name = _("Blog Comment")
        verbose_name_plural = _("Blog Comments")
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.author_name} on '{self.blog.title}'"
