"""
CuraSuite — SEO Models

SEOMetadata uses a GenericForeignKey so it can be attached to any content type:
  Page, Blog, Product, Landing Page, etc.

Redirect handles 301/302 URL redirects managed from the admin panel.
"""

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel, UUIDModel


class SEOMetadata(TimeStampedModel):
    """
    Reusable SEO metadata block that can be attached to any content object.
    One SEOMetadata record per content object (enforced via unique_together).
    """

    # ── Generic relation — links to any model ─────────────────────────────────
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name=_("Content type"),
    )
    object_id = models.UUIDField(verbose_name=_("Object ID"))
    content_object = GenericForeignKey("content_type", "object_id")

    # ── Core metadata ─────────────────────────────────────────────────────────
    seo_title = models.CharField(
        max_length=70,
        blank=True,
        verbose_name=_("SEO title"),
        help_text=_("Recommended 50–60 characters. Defaults to content title if blank."),
    )
    meta_description = models.CharField(
        max_length=165,
        blank=True,
        verbose_name=_("Meta description"),
        help_text=_("Recommended 140–160 characters."),
    )
    canonical_url = models.URLField(
        blank=True,
        verbose_name=_("Canonical URL"),
        help_text=_("Leave blank to use the page's default URL."),
    )

    # ── Robots ────────────────────────────────────────────────────────────────
    class RobotsDirective(models.TextChoices):
        INDEX_FOLLOW     = "index, follow",     _("Index, Follow (default)")
        NOINDEX_FOLLOW   = "noindex, follow",   _("No Index, Follow")
        INDEX_NOFOLLOW   = "index, nofollow",   _("Index, No Follow")
        NOINDEX_NOFOLLOW = "noindex, nofollow", _("No Index, No Follow")

    robots = models.CharField(
        max_length=30,
        choices=RobotsDirective.choices,
        default=RobotsDirective.INDEX_FOLLOW,
        verbose_name=_("Robots directive"),
    )

    # ── Open Graph ────────────────────────────────────────────────────────────
    og_title = models.CharField(max_length=100, blank=True, verbose_name=_("OG title"))
    og_description = models.TextField(max_length=300, blank=True, verbose_name=_("OG description"))
    og_image = models.ImageField(
        upload_to="seo/og/",
        null=True,
        blank=True,
        verbose_name=_("OG image"),
        help_text=_("Recommended 1200×630px."),
    )

    # ── Twitter Card ──────────────────────────────────────────────────────────
    twitter_title = models.CharField(max_length=100, blank=True, verbose_name=_("Twitter title"))
    twitter_description = models.CharField(max_length=200, blank=True, verbose_name=_("Twitter description"))

    # ── Schema ────────────────────────────────────────────────────────────────
    class SchemaType(models.TextChoices):
        NONE              = "",                    _("None")
        ORGANIZATION      = "Organization",        _("Organization")
        WEBSITE           = "WebSite",             _("Website")
        SOFTWARE_APP      = "SoftwareApplication", _("Software Application")
        PRODUCT           = "Product",             _("Product")
        ARTICLE           = "Article",             _("Article")
        BLOG_POSTING      = "BlogPosting",         _("Blog Posting")
        FAQ_PAGE          = "FAQPage",             _("FAQ Page")
        HOW_TO            = "HowTo",               _("How To")
        LOCAL_BUSINESS    = "LocalBusiness",       _("Local Business")
        BREADCRUMB_LIST   = "BreadcrumbList",      _("Breadcrumb List")

    schema_type = models.CharField(
        max_length=30,
        choices=SchemaType.choices,
        default=SchemaType.NONE,
        blank=True,
        verbose_name=_("Schema type"),
    )

    # ── Focus keyword (for editorial guidance) ────────────────────────────────
    focus_keyword = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Focus keyword"),
        help_text=_("Primary keyword this page targets."),
    )

    class Meta:
        db_table = "seo_metadata"
        verbose_name = _("SEO Metadata")
        verbose_name_plural = _("SEO Metadata")
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]
        unique_together = [("content_type", "object_id")]

    def __str__(self):
        return f"SEO: {self.seo_title or self.object_id}"

    def get_title(self, fallback: str = "") -> str:
        return self.seo_title or fallback

    def get_description(self, fallback: str = "") -> str:
        return self.meta_description or fallback

    def get_og_title(self, fallback: str = "") -> str:
        return self.og_title or self.seo_title or fallback

    def get_og_description(self, fallback: str = "") -> str:
        return self.og_description or self.meta_description or fallback


class Redirect(UUIDModel):
    """
    URL redirect manager — handles 301 and 302 redirects.
    Managed from the admin panel by the SEO specialist role.
    """

    class RedirectType(models.TextChoices):
        PERMANENT = "301", _("301 — Permanent")
        TEMPORARY = "302", _("302 — Temporary")

    old_path = models.CharField(
        max_length=500,
        unique=True,
        db_index=True,
        verbose_name=_("Old path"),
        help_text=_("The URL path being redirected FROM. Must start with /"),
    )
    new_path = models.CharField(
        max_length=500,
        verbose_name=_("New path"),
        help_text=_("The URL path redirecting TO. Can be absolute or relative."),
    )
    redirect_type = models.CharField(
        max_length=3,
        choices=RedirectType.choices,
        default=RedirectType.PERMANENT,
        verbose_name=_("Redirect type"),
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Active"), db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    note = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Note"),
        help_text=_("Internal note about why this redirect exists."),
    )

    class Meta:
        db_table = "seo_redirects"
        verbose_name = _("Redirect")
        verbose_name_plural = _("Redirects")
        ordering = ["old_path"]

    def __str__(self):
        return f"{self.old_path} → {self.new_path} ({self.redirect_type})"
