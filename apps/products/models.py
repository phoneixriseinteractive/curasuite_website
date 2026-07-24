"""
CuraSuite — Products Models

Three products in the CuraSuite ecosystem:
  - CuraCMS    : Website CMS for doctors and clinics
  - CuraLabs   : Digital platform for pathology labs
  - CuraSuite  : Clinic management system

Model hierarchy:
  Product
    ├── ProductFeature      (ordered list of features)
    ├── ProductPricing      (pricing tiers)
    ├── ProductFAQ          (per-product FAQs)
    ├── ProductScreenshot   (ordered screenshots)
    └── ProductIntegration  (integration badges)

Each Product links to an SEOMetadata via GenericFK (in seo app).
"""

from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from apps.core.models import AuditedModel, PublishableModel, UUIDModel


class Product(PublishableModel):
    """
    A CuraSuite product (CuraCMS, CuraLabs, CuraSuite).
    Uses PublishableModel for draft → published workflow.
    """

    class ProductKey(models.TextChoices):
        CURACMS   = "curacms",   _("CuraCMS")
        CURALABS  = "curalabs",  _("CuraLabs")
        CURASUITE = "curasuite", _("CuraSuite")

    # ── Identity ──────────────────────────────────────────────────────────────
    key = models.CharField(
        max_length=20,
        choices=ProductKey.choices,
        unique=True,
        db_index=True,
        verbose_name=_("Product key"),
        help_text=_("Unique identifier used internally and in URLs."),
    )
    name = models.CharField(max_length=100, verbose_name=_("Product name"))
    slug = models.SlugField(
        max_length=120,
        unique=True,
        db_index=True,
        verbose_name=_("Slug"),
        help_text=_("Used in the URL: /products/<slug>/"),
    )
    tagline = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Tagline"),
        help_text=_("One-line value proposition shown on cards."),
    )

    # ── Descriptions ─────────────────────────────────────────────────────────
    short_description = models.TextField(
        max_length=500,
        verbose_name=_("Short description"),
        help_text=_("Used in product cards, search results, and metadata fallback."),
    )
    long_description = models.TextField(
        blank=True,
        verbose_name=_("Long description"),
        help_text=_("Full product description rendered on the product landing page."),
    )

    # ── Visuals ───────────────────────────────────────────────────────────────
    icon = models.ImageField(
        upload_to="products/icons/",
        null=True,
        blank=True,
        verbose_name=_("Icon"),
        help_text=_("Product icon — square, min 256×256px."),
    )
    hero_image = models.ImageField(
        upload_to="products/heroes/",
        null=True,
        blank=True,
        verbose_name=_("Hero image"),
        help_text=_("Used in the product landing page hero section."),
    )
    color = models.CharField(
        max_length=7,
        default="#2563EB",
        verbose_name=_("Brand color"),
        help_text=_("Hex color used for product accents. e.g. #2563EB"),
    )

    # ── Target audience ───────────────────────────────────────────────────────
    target_audience = models.TextField(
        blank=True,
        verbose_name=_("Target audience"),
        help_text=_("Comma-separated list: Doctors, Clinics, Pathology Labs"),
    )

    # ── Display order ─────────────────────────────────────────────────────────
    sort_order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Sort order"),
        db_index=True,
    )

    class Meta:
        db_table = "products"
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("products:detail", kwargs={"slug": self.slug})

    @property
    def audience_list(self) -> list[str]:
        return [a.strip() for a in self.target_audience.split(",") if a.strip()]


class ProductFeature(UUIDModel):
    """
    A single feature belonging to a product.
    Displayed in the features grid on the product landing page.
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="features",
        verbose_name=_("Product"),
    )
    title = models.CharField(max_length=100, verbose_name=_("Title"))
    description = models.TextField(max_length=500, verbose_name=_("Description"))
    icon_name = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Icon name"),
        help_text=_("Lucide icon name e.g. 'calendar', 'bar-chart', 'users'"),
    )
    is_highlighted = models.BooleanField(
        default=False,
        verbose_name=_("Highlighted"),
        help_text=_("Highlighted features are shown prominently."),
    )
    sort_order = models.PositiveIntegerField(default=0, verbose_name=_("Sort order"), db_index=True)

    class Meta:
        db_table = "product_features"
        verbose_name = _("Product Feature")
        verbose_name_plural = _("Product Features")
        ordering = ["sort_order"]

    def __str__(self):
        return f"{self.product.name} — {self.title}"


class ProductPricing(UUIDModel):
    """
    A pricing tier for a product.
    Products can have multiple tiers (Starter, Professional, Enterprise).
    """

    class BillingCycle(models.TextChoices):
        MONTHLY  = "monthly",  _("Monthly")
        YEARLY   = "yearly",   _("Yearly")
        ONE_TIME = "one_time", _("One Time")
        CUSTOM   = "custom",   _("Custom / Contact Sales")

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="pricing_tiers",
        verbose_name=_("Product"),
    )
    tier_name = models.CharField(max_length=50, verbose_name=_("Tier name"))
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Price (₹)"),
        help_text=_("Leave blank for 'Contact Sales' pricing."),
    )
    original_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Original price (₹)"),
        help_text=_("Optional. If set and higher than Price, shown struck-through with a savings badge."),
    )
    billing_cycle = models.CharField(
        max_length=20,
        choices=BillingCycle.choices,
        default=BillingCycle.MONTHLY,
        verbose_name=_("Billing cycle"),
    )
    description = models.TextField(blank=True, verbose_name=_("Description"))
    features_included = models.TextField(
        blank=True,
        verbose_name=_("Features included"),
        help_text=_("One feature per line."),
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name=_("Featured tier"),
        help_text=_("The featured tier is highlighted on the pricing page."),
    )
    cta_text = models.CharField(
        max_length=50,
        default="Get Started",
        verbose_name=_("CTA button text"),
    )
    cta_url = models.CharField(max_length=200, blank=True, verbose_name=_("CTA URL"))
    sort_order = models.PositiveIntegerField(default=0, verbose_name=_("Sort order"), db_index=True)

    class Meta:
        db_table = "product_pricing"
        verbose_name = _("Product Pricing")
        verbose_name_plural = _("Product Pricing")
        ordering = ["sort_order"]

    def __str__(self):
        price_str = f"₹{self.price}" if self.price else "Contact Sales"
        return f"{self.product.name} — {self.tier_name} ({price_str})"

    @property
    def formatted_price(self) -> str:
        if not self.price:
            return "Contact Sales"
        return f"₹{self.price:,.0f}"

    @property
    def formatted_original_price(self) -> str:
        return f"₹{self.original_price:,.0f}" if self.original_price else ""

    @property
    def has_discount(self) -> bool:
        return bool(self.price and self.original_price and self.original_price > self.price)

    @property
    def savings_amount(self):
        return (self.original_price - self.price) if self.has_discount else None

    @property
    def formatted_savings_amount(self) -> str:
        return f"₹{self.savings_amount:,.0f}" if self.has_discount else ""

    @property
    def savings_percent(self) -> int:
        if not self.has_discount:
            return 0
        return round((self.original_price - self.price) / self.original_price * 100)

    @property
    def features_list(self) -> list[str]:
        return [f.strip() for f in self.features_included.splitlines() if f.strip()]


class ProductFAQ(UUIDModel):
    """
    A frequently asked question specific to a product.
    Rendered as an accordion on the product landing page.
    Includes FAQPage schema markup support.
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="faqs",
        verbose_name=_("Product"),
    )
    question = models.CharField(max_length=300, verbose_name=_("Question"))
    answer = models.TextField(verbose_name=_("Answer"))
    sort_order = models.PositiveIntegerField(default=0, verbose_name=_("Sort order"), db_index=True)

    class Meta:
        db_table = "product_faqs"
        verbose_name = _("Product FAQ")
        verbose_name_plural = _("Product FAQs")
        ordering = ["sort_order"]

    def __str__(self):
        return f"{self.product.name} — {self.question[:60]}"


class ProductScreenshot(UUIDModel):
    """
    A screenshot or demo image for a product.
    Displayed in a carousel on the product landing page.
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="screenshots",
        verbose_name=_("Product"),
    )
    title = models.CharField(max_length=100, verbose_name=_("Title"))
    caption = models.CharField(max_length=200, blank=True, verbose_name=_("Caption"))
    image = models.ImageField(
        upload_to="products/screenshots/",
        verbose_name=_("Screenshot"),
    )
    alt_text = models.CharField(
        max_length=200,
        verbose_name=_("Alt text"),
        help_text=_("Describe the screenshot for accessibility and SEO."),
    )
    sort_order = models.PositiveIntegerField(default=0, verbose_name=_("Sort order"), db_index=True)

    class Meta:
        db_table = "product_screenshots"
        verbose_name = _("Product Screenshot")
        verbose_name_plural = _("Product Screenshots")
        ordering = ["sort_order"]

    def __str__(self):
        return f"{self.product.name} — {self.title}"


class ProductIntegration(UUIDModel):
    """
    An integration badge shown on the product landing page.
    e.g. "Works with Google Calendar", "WhatsApp Integration"
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="integrations",
        verbose_name=_("Product"),
    )
    name = models.CharField(max_length=100, verbose_name=_("Integration name"))
    logo = models.ImageField(
        upload_to="products/integrations/",
        null=True,
        blank=True,
        verbose_name=_("Logo"),
    )
    url = models.URLField(blank=True, verbose_name=_("URL"))
    sort_order = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        db_table = "product_integrations"
        verbose_name = _("Product Integration")
        verbose_name_plural = _("Product Integrations")
        ordering = ["sort_order"]

    def __str__(self):
        return f"{self.product.name} — {self.name}"
