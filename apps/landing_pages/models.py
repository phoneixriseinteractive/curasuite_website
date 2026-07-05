"""
CuraSuite — Landing Pages Models

Conversion-focused, ad-only pages — separate from the general `pages` app.
Each LandingPage renders through one of two shared templates
(landing_pages/curacms.html or landing_pages/curalabs.html) based on product,
so content is fully data-driven and editable from the admin panel without
touching HTML.

Models:
  LandingPage       — one ad landing page (headline, copy blocks, WhatsApp msg)
  LandingPainPoint  — bullet problem statements shown on the page
  LandingBenefit    — icon + title + description cards
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import PublishableModel, UUIDModel


class LandingPage(PublishableModel):
    """A single ad-traffic landing page, e.g. /lp/dentist/."""

    slug = models.SlugField(
        max_length=100, unique=True, db_index=True,
        verbose_name=_("URL slug"),
        help_text=_("Used as /lp/<slug>/ — e.g. 'dentist', 'pathology-digital-platform'."),
    )
    product = models.ForeignKey(
        "products.Product", on_delete=models.CASCADE,
        related_name="landing_pages", verbose_name=_("Product"),
        help_text=_("Which product this page advertises. Controls color, icon, and template family."),
    )

    # ── Hero ──────────────────────────────────────────────────────────────────
    headline    = models.CharField(max_length=200, verbose_name=_("Headline"))
    subheadline = models.CharField(max_length=300, blank=True, verbose_name=_("Subheadline"))
    hero_image  = models.ImageField(upload_to="landing_pages/", null=True, blank=True, verbose_name=_("Hero image"))

    # ── Targeting / copy context ─────────────────────────────────────────────
    target_audience_label = models.CharField(
        max_length=100, blank=True, verbose_name=_("Audience label"),
        help_text=_("Shown as a pill badge, e.g. 'For Dentists', 'For Pathology Labs'."),
    )
    specialty = models.CharField(
        max_length=30, blank=True, verbose_name=_("Specialty (auto-fill)"),
        help_text=_("Pre-fills the specialty field on the form so visitors aren't asked again — "
                    "e.g. 'dentist' for the dentist landing page. Matches Lead.Specialty choices."),
    )
    social_proof_note = models.CharField(
        max_length=200, blank=True, verbose_name=_("Social proof note"),
        help_text=_("e.g. 'Trusted by 120+ dental clinics across India'."),
    )

    # ── WhatsApp ──────────────────────────────────────────────────────────────
    whatsapp_message_template = models.TextField(
        blank=True, verbose_name=_("WhatsApp message template"),
        help_text=_("Pre-filled message when a visitor clicks the WhatsApp CTA."),
    )

    # ── Attribution defaults ─────────────────────────────────────────────────
    default_utm_campaign = models.CharField(
        max_length=100, blank=True, verbose_name=_("Default UTM campaign"),
        help_text=_("Used if the incoming ad URL doesn't carry its own utm_campaign."),
    )

    # ── SEO / indexing ────────────────────────────────────────────────────────
    noindex = models.BooleanField(
        default=True, verbose_name=_("No-index this page"),
        help_text=_("Landing pages are usually excluded from search results and the sitemap."),
    )

    class Meta:
        db_table = "landing_pages"
        verbose_name = _("Landing Page")
        verbose_name_plural = _("Landing Pages")
        ordering = ["product__sort_order", "slug"]

    def __str__(self):
        return f"{self.headline} (/lp/{self.slug}/)"

    def get_absolute_url(self):
        return f"/lp/{self.slug}/"

    @property
    def template_name(self):
        """Two shared templates only — grouped by product key."""
        if self.product.key == "curalabs":
            return "landing_pages/curalabs.html"
        return "landing_pages/curacms.html"


class LandingPainPoint(models.Model):
    """A problem/pain bullet shown on the landing page — 'Struggling with X?'"""

    landing_page = models.ForeignKey(LandingPage, on_delete=models.CASCADE, related_name="pain_points")
    text         = models.CharField(max_length=200, verbose_name=_("Pain point"))
    sort_order   = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "landing_pain_points"
        ordering = ["sort_order"]
        verbose_name = _("Pain Point")
        verbose_name_plural = _("Pain Points")

    def __str__(self):
        return self.text


class LandingBenefit(models.Model):
    """An icon + title + description benefit card shown on the landing page."""

    landing_page = models.ForeignKey(LandingPage, on_delete=models.CASCADE, related_name="benefits")
    icon         = models.CharField(max_length=10, default="✓", verbose_name=_("Icon (emoji)"))
    title        = models.CharField(max_length=100, verbose_name=_("Title"))
    description  = models.TextField(verbose_name=_("Description"))
    sort_order   = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "landing_benefits"
        ordering = ["sort_order"]
        verbose_name = _("Benefit")
        verbose_name_plural = _("Benefits")

    def __str__(self):
        return self.title
