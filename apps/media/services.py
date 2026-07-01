"""CuraSuite — Media Services"""
import logging
import os
from django.core.files.uploadedfile import UploadedFile
from .models import MediaFile, MediaFolder

logger = logging.getLogger(__name__)

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/avif", "image/gif"}
ALLOWED_DOC_TYPES   = {"application/pdf", "application/msword",
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
ALLOWED_SVG_TYPES   = {"image/svg+xml"}
MAX_FILE_SIZE_MB    = 10


def get_file_type(mime_type: str) -> str:
    if mime_type in ALLOWED_IMAGE_TYPES: return MediaFile.FileType.IMAGE
    if mime_type in ALLOWED_DOC_TYPES:   return MediaFile.FileType.DOCUMENT
    if mime_type in ALLOWED_SVG_TYPES:   return MediaFile.FileType.SVG
    if mime_type.startswith("video/"):   return MediaFile.FileType.VIDEO
    return MediaFile.FileType.OTHER


def validate_upload(file: UploadedFile) -> None:
    """Raise ValueError for invalid uploads."""
    all_allowed = ALLOWED_IMAGE_TYPES | ALLOWED_DOC_TYPES | ALLOWED_SVG_TYPES | {"video/mp4"}
    if file.content_type not in all_allowed:
        raise ValueError(f"File type '{file.content_type}' is not allowed.")
    max_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
    if file.size > max_bytes:
        raise ValueError(f"File exceeds maximum size of {MAX_FILE_SIZE_MB}MB.")


def upload_file(file: UploadedFile, *, folder=None, alt_text: str = "",
                title: str = "", uploaded_by=None) -> MediaFile:
    """Validate and save an uploaded file to the media library."""
    validate_upload(file)
    file_type = get_file_type(file.content_type)

    media = MediaFile.objects.create(
        file=file,
        original_name=file.name,
        mime_type=file.content_type,
        file_type=file_type,
        file_size=file.size,
        alt_text=alt_text,
        title=title or os.path.splitext(file.name)[0].replace("-", " ").replace("_", " ").title(),
        folder=folder,
        uploaded_by=uploaded_by,
    )

    # Extract image dimensions if PIL is available
    if file_type == MediaFile.FileType.IMAGE:
        try:
            from PIL import Image
            file.seek(0)
            img = Image.open(file)
            media.width, media.height = img.size
            media.save(update_fields=["width", "height"])
        except Exception:
            pass

    logger.info("Media uploaded: %s (%s)", media.original_name, media.file_size_display)
    return media
