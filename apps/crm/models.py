"""
CuraSuite — CRM Models

Lead capture and pipeline management for the CuraSuite marketing website.
Every form submission (demo request, contact, newsletter) flows into this module.

Models:
  Lead            — a captured prospect from any source
  LeadNote        — internal notes added by sales team
  LeadActivity    — audit trail of all lead interactions
  DemoRequest     — structured demo booking linked to a lead
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import AuditedModel, TimeStampedModel, UUIDModel


class Lead(AuditedModel):
    """
    A prospect captured from any channel on the CuraSuite website.
    One Lead per email address. Duplicate submissions update the existing record.
    """

    class Status(models.TextChoices):
        NEW           = "new",            _("New")
        CONTACTED     = "contacted",      _("Contacted")
        QUALIFIED     = "qualified",      _("Qualified")
        DEMO_SCHEDULED= "demo_scheduled", _("Demo Scheduled")
        PROPOSAL_SENT = "proposal_sent",  _("Proposal Sent")
        NEGOTIATION   = "negotiation",    _("Negotiation")
        WON           = "won",            _("Won")
        LOST          = "lost",           _("Lost")
        UNQUALIFIED   = "unqualified",    _("Unqualified")

    class Source(models.TextChoices):
        CONTACT_FORM  = "contact_form",  _("Contact Form")
        DEMO_FORM     = "demo_form",     _("Demo Request Form")
        NEWSLETTER    = "newsletter",    _("Newsletter Signup")
        GOOGLE_ADS    = "google_ads",    _("Google Ads")
        META_ADS      = "meta_ads",      _("Meta Ads")
        ORGANIC       = "organic",       _("Organic Search")
        REFERRAL      = "referral",      _("Referral")
        CHATBOT       = "chatbot",       _("AI Chatbot")
        DIRECT        = "direct",        _("Direct")
        OTHER         = "other",         _("Other")

    class BusinessType(models.TextChoices):
        SINGLE_DOCTOR    = "single_doctor",    _("Single Doctor")
        MULTI_SPECIALTY  = "multi_specialty",  _("Multi-Specialty Clinic")
        DENTAL           = "dental",           _("Dental Clinic")
        PHYSIOTHERAPY    = "physiotherapy",    _("Physiotherapy Clinic")
        PATHOLOGY_LAB    = "pathology_lab",    _("Pathology Lab")
        DIAGNOSTIC       = "diagnostic",       _("Diagnostic Center")
        HOSPITAL         = "hospital",         _("Hospital")
        OTHER            = "other",            _("Other")

    # ── Contact details ───────────────────────────────────────────────────────
    full_name    = models.CharField(max_length=200, verbose_name=_("Full name"))
    email        = models.EmailField(db_index=True, verbose_name=_("Email"))
    phone        = models.CharField(max_length=20, blank=True, verbose_name=_("Phone"))
    organization = models.CharField(max_length=200, blank=True, verbose_name=_("Organization"))
    city         = models.CharField(max_length=100, blank=True, verbose_name=_("City"))
    message      = models.TextField(blank=True, verbose_name=_("Message"))

    # ── Classification ────────────────────────────────────────────────────────
    business_type = models.CharField(
        max_length=30, choices=BusinessType.choices,
        blank=True, verbose_name=_("Business type"),
    )
    product_interest = models.CharField(
        max_length=100, blank=True,
        verbose_name=_("Product interest"),
        help_text=_("Which CuraSuite product are they interested in?"),
    )

    # ── Pipeline ──────────────────────────────────────────────────────────────
    status = models.CharField(
        max_length=20, choices=Status.choices,
        default=Status.NEW, db_index=True,
        verbose_name=_("Status"),
    )
    score = models.PositiveIntegerField(
        default=0, verbose_name=_("Lead score"),
        help_text=_("Higher score = higher priority. Set manually or via automation."),
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_leads",
        verbose_name=_("Assigned to"),
    )

    # ── Attribution ───────────────────────────────────────────────────────────
    source       = models.CharField(max_length=20, choices=Source.choices, default=Source.OTHER, verbose_name=_("Source"))
    utm_source   = models.CharField(max_length=100, blank=True, verbose_name=_("UTM source"))
    utm_medium   = models.CharField(max_length=100, blank=True, verbose_name=_("UTM medium"))
    utm_campaign = models.CharField(max_length=100, blank=True, verbose_name=_("UTM campaign"))
    utm_content  = models.CharField(max_length=100, blank=True, verbose_name=_("UTM content"))
    referrer_url = models.URLField(blank=True, verbose_name=_("Referrer URL"))

    class Meta:
        db_table  = "crm_leads"
        verbose_name = _("Lead")
        verbose_name_plural = _("Leads")
        ordering  = ["-created_at"]
        indexes   = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["source", "created_at"]),
        ]

    def __str__(self):
        return f"{self.full_name} <{self.email}>"

    @property
    def is_won(self):
        return self.status == self.Status.WON

    @property
    def display_name(self):
        return self.organization or self.full_name


class LeadNote(UUIDModel):
    """Internal note added by a sales team member on a lead."""

    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="notes")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="lead_notes",
    )
    content   = models.TextField(verbose_name=_("Note"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "crm_lead_notes"
        verbose_name = _("Lead Note")
        verbose_name_plural = _("Lead Notes")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Note on {self.lead} — {self.created_at:%Y-%m-%d}"


class LeadActivity(UUIDModel):
    """Audit trail entry for a lead — every status change and interaction is logged."""

    class ActivityType(models.TextChoices):
        CREATED        = "created",        _("Lead Created")
        STATUS_CHANGED = "status_changed", _("Status Changed")
        NOTE_ADDED     = "note_added",     _("Note Added")
        EMAIL_SENT     = "email_sent",     _("Email Sent")
        CALL_LOGGED    = "call_logged",    _("Call Logged")
        DEMO_BOOKED    = "demo_booked",    _("Demo Booked")
        ASSIGNED       = "assigned",       _("Lead Assigned")

    lead          = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="activities")
    activity_type = models.CharField(max_length=20, choices=ActivityType.choices)
    description   = models.TextField(blank=True)
    performed_by  = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="lead_activities",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "crm_lead_activities"
        verbose_name = _("Lead Activity")
        verbose_name_plural = _("Lead Activities")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.activity_type} — {self.lead}"


class DemoRequest(TimeStampedModel):
    """
    A structured demo booking.
    Always linked to a Lead record.
    Created automatically when the demo form is submitted.
    """

    class Status(models.TextChoices):
        PENDING   = "pending",   _("Pending")
        CONFIRMED = "confirmed", _("Confirmed")
        COMPLETED = "completed", _("Completed")
        CANCELLED = "cancelled", _("Cancelled")
        NO_SHOW   = "no_show",   _("No Show")

    lead             = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="demo_requests")
    preferred_date   = models.DateField(null=True, blank=True, verbose_name=_("Preferred date"))
    preferred_time   = models.CharField(max_length=50, blank=True, verbose_name=_("Preferred time"))
    product_interest = models.CharField(max_length=100, blank=True, verbose_name=_("Product of interest"))
    status           = models.CharField(
        max_length=15, choices=Status.choices,
        default=Status.PENDING, db_index=True,
    )
    notes            = models.TextField(blank=True, verbose_name=_("Internal notes"))
    confirmed_at     = models.DateTimeField(null=True, blank=True)
    handled_by       = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="handled_demos",
    )

    class Meta:
        db_table = "crm_demo_requests"
        verbose_name = _("Demo Request")
        verbose_name_plural = _("Demo Requests")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Demo — {self.lead.full_name} ({self.status})"
