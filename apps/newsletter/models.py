"""
CuraSuite — Newsletter Models

Double opt-in subscriber management with campaign tracking.

Models:
  NewsletterSubscriber  — a confirmed or pending email subscriber
  NewsletterCampaign    — a broadcast email campaign
  NewsletterSend        — per-subscriber delivery record (open/click tracking)
"""

import uuid
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel, UUIDModel


class NewsletterSubscriber(TimeStampedModel):
    """
    An email subscriber. Follows double opt-in:
      submitted → confirmation email sent → confirmed (active)
    Unsubscribe sets status to unsubscribed without deleting the record.
    """

    class Status(models.TextChoices):
        PENDING       = "pending",       _("Pending Confirmation")
        CONFIRMED     = "confirmed",     _("Confirmed")
        UNSUBSCRIBED  = "unsubscribed",  _("Unsubscribed")
        BOUNCED       = "bounced",       _("Bounced")
        COMPLAINED    = "complained",    _("Complained (Spam)")

    email      = models.EmailField(unique=True, db_index=True, verbose_name=_("Email"))
    first_name = models.CharField(max_length=100, blank=True, verbose_name=_("First name"))
    status     = models.CharField(
        max_length=15, choices=Status.choices,
        default=Status.PENDING, db_index=True,
    )

    # ── Double opt-in tokens ─────────────────────────────────────────────────
    confirmation_token    = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    confirmation_sent_at  = models.DateTimeField(null=True, blank=True)
    confirmed_at          = models.DateTimeField(null=True, blank=True)

    # ── Unsubscribe ───────────────────────────────────────────────────────────
    unsubscribe_token    = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    unsubscribed_at      = models.DateTimeField(null=True, blank=True)
    unsubscribe_reason   = models.CharField(max_length=200, blank=True)

    # ── Source tracking ───────────────────────────────────────────────────────
    source      = models.CharField(max_length=100, blank=True, verbose_name=_("Source"))
    ip_address  = models.GenericIPAddressField(null=True, blank=True)
    referrer    = models.URLField(blank=True)

    class Meta:
        db_table     = "newsletter_subscribers"
        verbose_name = _("Subscriber")
        verbose_name_plural = _("Subscribers")
        ordering     = ["-created_at"]

    def __str__(self):
        return f"{self.email} ({self.status})"

    @property
    def is_active(self):
        return self.status == self.Status.CONFIRMED

    def confirm(self):
        self.status       = self.Status.CONFIRMED
        self.confirmed_at = timezone.now()
        self.save(update_fields=["status", "confirmed_at", "updated_at"])

    def unsubscribe(self, reason: str = ""):
        self.status            = self.Status.UNSUBSCRIBED
        self.unsubscribed_at   = timezone.now()
        self.unsubscribe_reason = reason
        self.save(update_fields=["status", "unsubscribed_at", "unsubscribe_reason", "updated_at"])


class NewsletterCampaign(TimeStampedModel):
    """A broadcast email campaign sent to confirmed subscribers."""

    class Status(models.TextChoices):
        DRAFT     = "draft",     _("Draft")
        SCHEDULED = "scheduled", _("Scheduled")
        SENDING   = "sending",   _("Sending")
        SENT      = "sent",      _("Sent")
        CANCELLED = "cancelled", _("Cancelled")

    subject      = models.CharField(max_length=200, verbose_name=_("Subject line"))
    preview_text = models.CharField(
        max_length=200, blank=True,
        verbose_name=_("Preview text"),
        help_text=_("Shown in email clients before opening. 85–100 chars ideal."),
    )
    content_html = models.TextField(verbose_name=_("HTML content"))
    content_text = models.TextField(blank=True, verbose_name=_("Plain text fallback"))

    status       = models.CharField(
        max_length=10, choices=Status.choices,
        default=Status.DRAFT, db_index=True,
    )
    scheduled_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Scheduled send time"))
    sent_at      = models.DateTimeField(null=True, blank=True)

    # ── Stats (denormalised for performance) ──────────────────────────────────
    total_sent   = models.PositiveIntegerField(default=0)
    total_opens  = models.PositiveIntegerField(default=0)
    total_clicks = models.PositiveIntegerField(default=0)
    total_bounces= models.PositiveIntegerField(default=0)
    total_unsubs = models.PositiveIntegerField(default=0)

    created_by   = models.ForeignKey(
        "accounts.User", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="campaigns",
    )

    class Meta:
        db_table     = "newsletter_campaigns"
        verbose_name = _("Campaign")
        verbose_name_plural = _("Campaigns")
        ordering     = ["-created_at"]

    def __str__(self):
        return self.subject

    @property
    def open_rate(self) -> str:
        if not self.total_sent:
            return "—"
        return f"{(self.total_opens / self.total_sent) * 100:.1f}%"

    @property
    def click_rate(self) -> str:
        if not self.total_sent:
            return "—"
        return f"{(self.total_clicks / self.total_sent) * 100:.1f}%"


class NewsletterSend(UUIDModel):
    """
    One record per subscriber per campaign.
    Tracks delivery status, opens, and clicks for each recipient.
    """

    class DeliveryStatus(models.TextChoices):
        QUEUED    = "queued",    _("Queued")
        SENT      = "sent",      _("Sent")
        OPENED    = "opened",    _("Opened")
        CLICKED   = "clicked",   _("Clicked")
        BOUNCED   = "bounced",   _("Bounced")
        FAILED    = "failed",    _("Failed")

    campaign   = models.ForeignKey(NewsletterCampaign, on_delete=models.CASCADE, related_name="sends")
    subscriber = models.ForeignKey(NewsletterSubscriber, on_delete=models.CASCADE, related_name="sends")

    status     = models.CharField(
        max_length=10, choices=DeliveryStatus.choices,
        default=DeliveryStatus.QUEUED, db_index=True,
    )
    sent_at    = models.DateTimeField(null=True, blank=True)
    opened_at  = models.DateTimeField(null=True, blank=True)
    clicked_at = models.DateTimeField(null=True, blank=True)
    error_msg  = models.TextField(blank=True)

    # Unique open tracking pixel token per send
    tracking_token = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)

    class Meta:
        db_table      = "newsletter_sends"
        verbose_name  = _("Newsletter Send")
        unique_together = [("campaign", "subscriber")]
        ordering      = ["-sent_at"]

    def __str__(self):
        return f"{self.campaign.subject} → {self.subscriber.email}"

    def mark_opened(self):
        if self.status not in (self.DeliveryStatus.OPENED, self.DeliveryStatus.CLICKED):
            self.status    = self.DeliveryStatus.OPENED
            self.opened_at = timezone.now()
            self.save(update_fields=["status", "opened_at"])
            NewsletterCampaign.objects.filter(pk=self.campaign_id).update(
                total_opens=models.F("total_opens") + 1
            )

    def mark_clicked(self):
        if self.status != self.DeliveryStatus.CLICKED:
            self.status     = self.DeliveryStatus.CLICKED
            self.clicked_at = timezone.now()
            if not self.opened_at:
                self.opened_at = self.clicked_at
            self.save(update_fields=["status", "clicked_at", "opened_at"])
            NewsletterCampaign.objects.filter(pk=self.campaign_id).update(
                total_clicks=models.F("total_clicks") + 1
            )
