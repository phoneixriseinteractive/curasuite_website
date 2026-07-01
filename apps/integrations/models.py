"""
CuraSuite — Integrations Models

Stores configuration for all third-party integrations.
Each integration record holds credentials, status, and config JSON.
The admin panel can enable/disable and test connections without code changes.

Also stores the site-wide settings used by template tags (GA4, GTM, WhatsApp, etc.)
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel


class Integration(TimeStampedModel):
    """
    A single third-party integration configuration.
    Credentials are stored encrypted at the application level via environment
    variables for sensitive fields; this model stores only non-secret config.
    """

    class Provider(models.TextChoices):
        GOOGLE_ANALYTICS  = "google_analytics",  _("Google Analytics 4")
        GOOGLE_TAG_MANAGER= "google_tag_manager", _("Google Tag Manager")
        GOOGLE_ADS        = "google_ads",         _("Google Ads")
        META_PIXEL        = "meta_pixel",         _("Meta Pixel")
        MICROSOFT_CLARITY = "microsoft_clarity",  _("Microsoft Clarity")
        WHATSAPP          = "whatsapp",           _("WhatsApp Business")
        SMTP              = "smtp",               _("SMTP Email")
        RECAPTCHA         = "recaptcha",          _("reCAPTCHA / Turnstile")
        GEMINI            = "gemini",             _("Google Gemini AI")
        OPENAI            = "openai",             _("OpenAI")
        ANTHROPIC         = "anthropic",          _("Anthropic Claude")
        BREVO             = "brevo",              _("Brevo (Email)")
        MAILCHIMP         = "mailchimp",          _("Mailchimp")

    provider    = models.CharField(
        max_length=30, choices=Provider.choices,
        unique=True, db_index=True,
    )
    is_enabled  = models.BooleanField(default=False, verbose_name=_("Enabled"), db_index=True)
    config      = models.JSONField(
        default=dict, blank=True,
        verbose_name=_("Configuration"),
        help_text=_("Non-secret configuration JSON. Store secrets in environment variables."),
    )
    last_tested_at     = models.DateTimeField(null=True, blank=True)
    last_test_status   = models.CharField(max_length=10, blank=True,
                                          choices=[("ok", "OK"), ("error", "Error"), ("", "Not tested")])
    last_test_message  = models.TextField(blank=True)

    class Meta:
        db_table     = "integrations"
        verbose_name = _("Integration")
        verbose_name_plural = _("Integrations")
        ordering     = ["provider"]

    def __str__(self):
        status = "✓" if self.is_enabled else "✗"
        return f"{status} {self.get_provider_display()}"

    def get_config(self, key: str, default=None):
        return self.config.get(key, default)


class SiteSettings(models.Model):
    """
    Singleton model for site-wide settings surfaced in templates.
    Only one record exists (pk=1). Use SiteSettings.load() to access.

    Covers: analytics IDs, WhatsApp number, chatbot toggle, CAPTCHA keys.
    Actual API secrets live in environment variables.
    """

    # ── Analytics ─────────────────────────────────────────────────────────────
    ga4_measurement_id  = models.CharField(max_length=20, blank=True, verbose_name=_("GA4 Measurement ID"), help_text=_("e.g. G-XXXXXXXXXX"))
    gtm_container_id    = models.CharField(max_length=20, blank=True, verbose_name=_("GTM Container ID"), help_text=_("e.g. GTM-XXXXXXX"))
    meta_pixel_id       = models.CharField(max_length=30, blank=True, verbose_name=_("Meta Pixel ID"))
    clarity_project_id  = models.CharField(max_length=20, blank=True, verbose_name=_("Microsoft Clarity ID"))

    # ── WhatsApp ──────────────────────────────────────────────────────────────
    whatsapp_enabled      = models.BooleanField(default=False, verbose_name=_("Enable WhatsApp widget"))
    whatsapp_phone        = models.CharField(max_length=20, blank=True, verbose_name=_("WhatsApp phone number"), help_text=_("International format without +: e.g. 919876543210"))
    whatsapp_message      = models.CharField(max_length=200, blank=True, default="Hi! I'd like to know more about CuraSuite.", verbose_name=_("Pre-filled message"))
    whatsapp_tooltip      = models.CharField(max_length=100, blank=True, default="Chat with us", verbose_name=_("Tooltip text"))

    # ── AI Chatbot ────────────────────────────────────────────────────────────
    chatbot_enabled       = models.BooleanField(default=False, verbose_name=_("Enable AI chatbot"))
    chatbot_name          = models.CharField(max_length=50, default="CuraSuite Assistant", verbose_name=_("Chatbot name"))
    chatbot_greeting      = models.CharField(max_length=300, default="Hi! I'm the CuraSuite Assistant. How can I help you today?", verbose_name=_("Greeting message"))
    chatbot_system_prompt = models.TextField(
        blank=True,
        verbose_name=_("System prompt"),
        help_text=_("Instructions for the AI. Keep focused on CuraSuite products and healthcare technology."),
        default=(
            "You are the CuraSuite Assistant, a helpful AI for CuraSuite — "
            "India's healthcare technology platform. Help visitors understand "
            "our products (CuraCMS, CuraLabs, CuraSuite), answer questions about "
            "features and pricing, and guide them to book a demo. "
            "Be friendly, professional, and concise. "
            "For medical advice, always direct users to qualified healthcare professionals."
        ),
    )

    # ── reCAPTCHA / Turnstile ────────────────────────────────────────────────
    captcha_enabled     = models.BooleanField(default=False, verbose_name=_("Enable CAPTCHA on forms"))
    captcha_provider    = models.CharField(
        max_length=15,
        choices=[("recaptcha_v3", "reCAPTCHA v3"), ("turnstile", "Cloudflare Turnstile")],
        default="turnstile",
        verbose_name=_("CAPTCHA provider"),
    )
    captcha_site_key    = models.CharField(max_length=200, blank=True, verbose_name=_("Site key (public)"))

    # ── Timestamps ────────────────────────────────────────────────────────────
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table     = "site_settings"
        verbose_name = _("Site Settings")
        verbose_name_plural = _("Site Settings")

    def __str__(self):
        return "Site Settings"

    @classmethod
    def load(cls) -> "SiteSettings":
        """Return the singleton settings record, creating it if absent."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
