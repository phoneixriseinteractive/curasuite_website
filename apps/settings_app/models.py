"""
CuraSuite — Settings App Models

Global site configuration models that don't belong in individual domain apps:
  GlobalFAQ       — site-wide FAQ entries (not product-specific)
  Testimonial     — customer testimonials with moderation
  AnnouncementBar — the dismissible top banner
  SocialLinks     — social media profile URLs
  SMTPSettings    — outgoing email configuration
  RobotsTxt       — robots.txt content editor
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel, UUIDModel


class GlobalFAQ(UUIDModel):
    """Site-wide FAQ not tied to a specific product."""

    class FAQCategory(models.TextChoices):
        GENERAL   = "general",   _("General")
        PRICING   = "pricing",   _("Pricing")
        TECHNICAL = "technical", _("Technical")
        SUPPORT   = "support",   _("Support")
        SECURITY  = "security",  _("Security")

    question    = models.CharField(max_length=300, verbose_name=_("Question"))
    answer      = models.TextField(verbose_name=_("Answer"))
    category    = models.CharField(max_length=20, choices=FAQCategory.choices, default=FAQCategory.GENERAL)
    is_active   = models.BooleanField(default=True, db_index=True)
    sort_order  = models.PositiveIntegerField(default=0, db_index=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "global_faqs"
        verbose_name = _("Global FAQ")
        verbose_name_plural = _("Global FAQs")
        ordering = ["category", "sort_order"]

    def __str__(self):
        return f"[{self.category}] {self.question[:60]}"


class Testimonial(TimeStampedModel):
    """Customer testimonial with photo and rating."""

    class Status(models.TextChoices):
        PENDING  = "pending",  _("Pending Review")
        APPROVED = "approved", _("Approved")
        REJECTED = "rejected", _("Rejected")

    customer_name = models.CharField(max_length=200, verbose_name=_("Customer name"))
    designation   = models.CharField(max_length=200, blank=True, verbose_name=_("Designation / Role"))
    clinic_name   = models.CharField(max_length=200, blank=True, verbose_name=_("Clinic / Organisation"))
    location      = models.CharField(max_length=100, blank=True, verbose_name=_("City / Location"))
    photo         = models.ImageField(upload_to="testimonials/", null=True, blank=True)
    rating        = models.PositiveIntegerField(default=5, choices=[(i, f"{i} Star{'s' if i>1 else ''}") for i in range(1, 6)])
    feedback      = models.TextField(verbose_name=_("Testimonial text"))
    product       = models.CharField(max_length=50, blank=True, verbose_name=_("Product"), help_text=_("CuraCMS, CuraLabs, CuraSuite, or blank for general"))
    status        = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING, db_index=True)
    is_featured   = models.BooleanField(default=False, verbose_name=_("Featured on homepage"))
    sort_order    = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        db_table = "testimonials"
        verbose_name = _("Testimonial")
        verbose_name_plural = _("Testimonials")
        ordering = ["sort_order", "-created_at"]

    def __str__(self):
        return f"{self.customer_name} — {self.clinic_name or 'General'}"

    @property
    def star_display(self):
        return "★" * self.rating + "☆" * (5 - self.rating)


class AnnouncementBar(UUIDModel):
    """The dismissible announcement banner shown at the top of the public site."""

    class BarStyle(models.TextChoices):
        INFO    = "info",    _("Info (Blue)")
        SUCCESS = "success", _("Success (Green)")
        WARNING = "warning", _("Warning (Amber)")
        PROMO   = "promo",   _("Promo (Black)")

    text        = models.CharField(max_length=300, verbose_name=_("Announcement text"))
    link_text   = models.CharField(max_length=50, blank=True, verbose_name=_("Link text"))
    link_url    = models.CharField(max_length=200, blank=True, verbose_name=_("Link URL"))
    style       = models.CharField(max_length=10, choices=BarStyle.choices, default=BarStyle.INFO)
    is_active   = models.BooleanField(default=False, db_index=True, verbose_name=_("Active"))
    is_dismissible = models.BooleanField(default=True, verbose_name=_("Dismissible by user"))
    starts_at   = models.DateTimeField(null=True, blank=True, verbose_name=_("Show from"))
    ends_at     = models.DateTimeField(null=True, blank=True, verbose_name=_("Hide after"))
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "announcement_bars"
        verbose_name = _("Announcement Bar")
        verbose_name_plural = _("Announcement Bars")
        ordering = ["-created_at"]

    def __str__(self):
        status = "Active" if self.is_active else "Inactive"
        return f"[{status}] {self.text[:60]}"


class SocialLinks(models.Model):
    """Singleton — social media profile URLs for the site footer and schema."""

    facebook    = models.URLField(blank=True, verbose_name=_("Facebook"))
    instagram   = models.URLField(blank=True, verbose_name=_("Instagram"))
    linkedin    = models.URLField(blank=True, verbose_name=_("LinkedIn"))
    twitter_x   = models.URLField(blank=True, verbose_name=_("X / Twitter"))
    youtube     = models.URLField(blank=True, verbose_name=_("YouTube"))
    whatsapp_link = models.URLField(blank=True, verbose_name=_("WhatsApp Business Link"))
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "social_links"
        verbose_name = _("Social Links")

    def __str__(self):
        return "Social Links"

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)


class SMTPSettings(models.Model):
    """
    Singleton — outgoing email server configuration.
    Passwords are stored encrypted via environment variable references.
    The actual password should be in the .env file, not here.
    """

    host        = models.CharField(max_length=200, default="smtp.gmail.com", verbose_name=_("SMTP Host"))
    port        = models.PositiveIntegerField(default=587, verbose_name=_("Port"))
    username    = models.CharField(max_length=200, blank=True, verbose_name=_("Username / Email"))
    use_tls     = models.BooleanField(default=True, verbose_name=_("Use TLS"))
    use_ssl     = models.BooleanField(default=False, verbose_name=_("Use SSL"))
    from_email  = models.EmailField(default="hello@curasuite.com", verbose_name=_("From email"))
    from_name   = models.CharField(max_length=100, default="CuraSuite", verbose_name=_("From name"))
    # Note: password stored in .env as EMAIL_HOST_PASSWORD — never in DB
    is_verified = models.BooleanField(default=False, verbose_name=_("Connection verified"))
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "smtp_settings"
        verbose_name = _("SMTP Settings")

    def __str__(self):
        return f"SMTP: {self.host}:{self.port}"

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @property
    def display_from(self):
        return f"{self.from_name} <{self.from_email}>"


class RobotsTxt(models.Model):
    """Singleton — editable robots.txt content."""

    content = models.TextField(
        default=(
            "User-agent: *\n"
            "Allow: /\n"
            "Disallow: /manage/\n"
            "Disallow: /admin/\n"
            "\n"
            "Sitemap: https://curasuite.com/sitemap.xml\n"
        ),
        verbose_name=_("robots.txt content"),
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "robots_txt"
        verbose_name = _("Robots.txt")

    def __str__(self):
        return "robots.txt"

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
