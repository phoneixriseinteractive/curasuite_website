"""
CuraSuite — Pages / CMS Models

Handles all static and dynamic public pages: Home, About, Products, Solutions,
Pricing, Contact, Privacy, Terms, and any custom pages created via the CMS.

Models:
  Page         — a single CMS-managed page with full publishing workflow
  PageRevision — version history for every saved page
  PageBlock    — structured content blocks within a page (for block-based editing)
"""

from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from apps.core.models import AuditedModel, VersionedModel, UUIDModel


class Page(VersionedModel):
    """
    A CMS-managed page. Inherits VersionedModel for full publishing workflow
    + revision history tracking.
    """

    class PageType(models.TextChoices):
        HOME       = "home",       _("Home")
        ABOUT      = "about",      _("About")
        PRODUCT    = "product",    _("Product Landing")
        SOLUTION   = "solution",   _("Solution")
        FEATURE    = "feature",    _("Feature")
        PRICING    = "pricing",    _("Pricing")
        CONTACT    = "contact",    _("Contact")
        BLOG_INDEX = "blog_index", _("Blog Index")
        LEGAL      = "legal",      _("Legal")
        CUSTOM     = "custom",     _("Custom")

    class Template(models.TextChoices):
        DEFAULT     = "default",      _("Default")
        FULL_WIDTH  = "full_width",   _("Full Width")
        LANDING     = "landing",      _("Landing Page")
        MINIMAL     = "minimal",      _("Minimal (no header/footer)")
        ABOUT       = "about",        _("About Page")
        SOLUTIONS   = "solutions",    _("Solutions Page")
        PRICING     = "pricing",      _("Pricing Page")

    # ── Identity ──────────────────────────────────────────────────────────────
    title     = models.CharField(max_length=200, verbose_name=_("Title"))
    slug      = models.SlugField(max_length=220, unique=True, db_index=True)
    page_type = models.CharField(max_length=20, choices=PageType.choices, default=PageType.CUSTOM)
    template  = models.CharField(max_length=20, choices=Template.choices, default=Template.DEFAULT)
    parent    = models.ForeignKey(
        "self", null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="children",
        verbose_name=_("Parent page"),
    )

    # ── Content ───────────────────────────────────────────────────────────────
    excerpt = models.TextField(
        max_length=500, blank=True,
        verbose_name=_("Excerpt"),
        help_text=_("Short summary used in listings and SEO fallback."),
    )
    content = models.TextField(
        blank=True,
        verbose_name=_("Content"),
        help_text=_("Main page content (HTML or Markdown)."),
    )
    featured_image = models.ImageField(
        upload_to="pages/", null=True, blank=True,
        verbose_name=_("Featured image"),
    )

    # ── Display ───────────────────────────────────────────────────────────────
    show_in_sitemap = models.BooleanField(default=True, verbose_name=_("Show in sitemap"))
    show_in_nav     = models.BooleanField(default=False, verbose_name=_("Show in navigation"))

    class Meta:
        db_table = "pages"
        verbose_name = _("Page")
        verbose_name_plural = _("Pages")
        ordering = ["slug"]
        indexes = [
            models.Index(fields=["status", "slug"]),
            models.Index(fields=["page_type", "status"]),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse, NoReverseMatch
        if self.page_type == self.PageType.HOME:
            return "/"
        try:
            return reverse("pages:detail", kwargs={"slug": self.slug})
        except NoReverseMatch:
            # Slug contains characters not matched by <slug:> (e.g. forward slashes)
            # Return the URL directly
            return f"/{self.slug}/"

    @property
    def breadcrumbs(self) -> list[dict]:
        """Build breadcrumb chain by walking up the parent tree."""
        crumbs = [{"title": self.title, "url": self.get_absolute_url()}]
        node = self.parent
        while node:
            crumbs.insert(0, {"title": node.title, "url": node.get_absolute_url()})
            node = node.parent
        crumbs.insert(0, {"title": "Home", "url": "/"})
        return crumbs


class PageRevision(UUIDModel):
    """
    Immutable snapshot of a Page's content at a point in time.
    Created automatically on every save via the Page service.
    """

    page            = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="revisions")
    content         = models.TextField()
    title           = models.CharField(max_length=200)
    revision_number = models.PositiveIntegerField()
    editor          = models.ForeignKey(
        "accounts.User", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="page_revisions",
    )
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "page_revisions"
        verbose_name = _("Page Revision")
        verbose_name_plural = _("Page Revisions")
        ordering = ["-revision_number"]
        unique_together = [("page", "revision_number")]

    def __str__(self):
        return f"{self.page.title} — v{self.revision_number}"
