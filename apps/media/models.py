"""
CuraSuite — Media Library Models

Centralised file management for all CuraSuite products.
Every uploaded image, document, or video is stored here with metadata.

Models:
  MediaFolder — hierarchical folder organisation
  MediaFile   — the file record itself (metadata + path)
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel, UUIDModel


class MediaFolder(UUIDModel):
    """Hierarchical folder for organising media files."""

    name   = models.CharField(max_length=100, verbose_name=_("Folder name"))
    parent = models.ForeignKey(
        "self", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="children",
        verbose_name=_("Parent folder"),
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="created_folders",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "media_folders"
        verbose_name = _("Media Folder")
        verbose_name_plural = _("Media Folders")
        ordering = ["name"]
        unique_together = [("name", "parent")]

    def __str__(self):
        return self.full_path

    @property
    def full_path(self) -> str:
        parts = [self.name]
        node  = self.parent
        while node:
            parts.insert(0, node.name)
            node = node.parent
        return " / ".join(parts)


class MediaFile(TimeStampedModel):
    """
    A single media asset. Supports images, PDFs, documents, videos, and SVGs.
    Alt text is required for accessibility and SEO compliance.
    """

    class FileType(models.TextChoices):
        IMAGE    = "image",    _("Image")
        DOCUMENT = "document", _("Document / PDF")
        VIDEO    = "video",    _("Video")
        SVG      = "svg",      _("SVG")
        OTHER    = "other",    _("Other")

    # ── Storage ───────────────────────────────────────────────────────────────
    file          = models.FileField(upload_to="media-library/%Y/%m/", verbose_name=_("File"))
    original_name = models.CharField(max_length=255, verbose_name=_("Original filename"))
    mime_type     = models.CharField(max_length=100, verbose_name=_("MIME type"))
    file_type     = models.CharField(max_length=10, choices=FileType.choices, default=FileType.OTHER, db_index=True)
    file_size     = models.PositiveIntegerField(verbose_name=_("File size (bytes)"), default=0)

    # ── Image-specific ────────────────────────────────────────────────────────
    width  = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Width (px)"))
    height = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Height (px)"))

    # ── Metadata ──────────────────────────────────────────────────────────────
    alt_text = models.CharField(
        max_length=200, blank=True,
        verbose_name=_("Alt text"),
        help_text=_("Required for images — describes the image for accessibility and SEO."),
    )
    title   = models.CharField(max_length=200, blank=True, verbose_name=_("Title"))
    caption = models.TextField(max_length=500, blank=True, verbose_name=_("Caption"))
    tags    = models.CharField(max_length=500, blank=True, verbose_name=_("Tags"), help_text=_("Comma-separated."))

    # ── Organisation ──────────────────────────────────────────────────────────
    folder = models.ForeignKey(
        MediaFolder, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="files",
        verbose_name=_("Folder"),
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="uploaded_files",
    )

    class Meta:
        db_table = "media_files"
        verbose_name = _("Media File")
        verbose_name_plural = _("Media Files")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["file_type", "created_at"]),
            models.Index(fields=["folder", "file_type"]),
        ]

    def __str__(self):
        return self.title or self.original_name

    @property
    def file_size_display(self) -> str:
        size = self.file_size
        if size < 1024:
            return f"{size} B"
        if size < 1024 ** 2:
            return f"{size / 1024:.1f} KB"
        return f"{size / (1024 ** 2):.1f} MB"

    @property
    def is_image(self) -> bool:
        return self.file_type == self.FileType.IMAGE

    @property
    def dimensions(self) -> str | None:
        if self.width and self.height:
            return f"{self.width}×{self.height}"
        return None

    @property
    def tag_list(self) -> list[str]:
        return [t.strip() for t in self.tags.split(",") if t.strip()]
