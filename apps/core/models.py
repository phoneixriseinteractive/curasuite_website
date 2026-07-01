"""
CuraSuite — Core Base Models
Every domain model in the CuraSuite ecosystem inherits from one of these base classes.
"""

import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


# ── Managers ───────────────────────────────────────────────────────────────────

class ActiveManager(models.Manager):
    """Default manager — returns only active (non-deleted) records."""
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True, deleted_at__isnull=True)


class SoftDeleteManager(models.Manager):
    """Manager that includes soft-deleted records."""
    def get_queryset(self):
        return super().get_queryset()

    def active(self):
        return self.get_queryset().filter(is_active=True, deleted_at__isnull=True)

    def deleted(self):
        return self.get_queryset().filter(deleted_at__isnull=False)


class PublishedManager(models.Manager):
    """Returns only published, active records."""
    def get_queryset(self):
        return super().get_queryset().filter(
            status="published",
            is_active=True,
            deleted_at__isnull=True,
        )


# ── Base Models ────────────────────────────────────────────────────────────────

class UUIDModel(models.Model):
    """Abstract base: UUID primary key."""
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("ID"),
    )

    class Meta:
        abstract = True


class TimeStampedModel(UUIDModel):
    """Abstract base: UUID + timestamps."""
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"), db_index=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"), db_index=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class SoftDeleteModel(TimeStampedModel):
    """
    Abstract base: soft delete support.
    objects = active records only.
    all_objects = all records including deleted.
    """
    is_active = models.BooleanField(default=True, verbose_name=_("Active"), db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Deleted at"), db_index=True)

    objects = ActiveManager()
    all_objects = SoftDeleteManager()

    class Meta:
        abstract = True

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save(update_fields=["deleted_at", "is_active", "updated_at"])

    def restore(self):
        self.deleted_at = None
        self.is_active = True
        self.save(update_fields=["deleted_at", "is_active", "updated_at"])

    @property
    def is_deleted(self):
        return self.deleted_at is not None


class AuditedModel(SoftDeleteModel):
    """Abstract base: full audit trail (created_by, updated_by)."""
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_created",
        verbose_name=_("Created by"),
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_updated",
        verbose_name=_("Updated by"),
    )

    class Meta:
        abstract = True


class PublishableModel(AuditedModel):
    """Abstract base: publishing workflow (draft → review → published → archived)."""

    class Status(models.TextChoices):
        DRAFT = "draft", _("Draft")
        REVIEW = "review", _("In Review")
        APPROVED = "approved", _("Approved")
        SCHEDULED = "scheduled", _("Scheduled")
        PUBLISHED = "published", _("Published")
        ARCHIVED = "archived", _("Archived")

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT,
        verbose_name=_("Status"), db_index=True,
    )
    published_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Published at"), db_index=True)
    scheduled_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Scheduled for"))
    published_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_published",
        verbose_name=_("Published by"),
    )

    objects = PublishedManager()
    all_objects = SoftDeleteManager()

    class Meta:
        abstract = True

    def publish(self, published_by=None):
        self.status = self.Status.PUBLISHED
        self.published_at = timezone.now()
        if published_by:
            self.published_by = published_by
        self.save(update_fields=["status", "published_at", "published_by", "updated_at"])

    def unpublish(self):
        self.status = self.Status.DRAFT
        self.published_at = None
        self.save(update_fields=["status", "published_at", "updated_at"])

    def archive(self):
        self.status = self.Status.ARCHIVED
        self.save(update_fields=["status", "updated_at"])

    @property
    def is_published(self):
        return self.status == self.Status.PUBLISHED

    @property
    def is_draft(self):
        return self.status == self.Status.DRAFT


class VersionedModel(PublishableModel):
    """Abstract base: version history tracking. Each implementing app needs a Revision model."""
    version = models.PositiveIntegerField(default=1, verbose_name=_("Version"))

    class Meta:
        abstract = True

    def increment_version(self):
        self.version += 1
