"""CuraSuite — Media Validators"""
from django.core.files.uploadedfile import UploadedFile

# Raster formats only. SVG is deliberately excluded: it can carry script and these
# images are embedded straight into public page HTML.
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_IMAGE_SIZE_MB = 10


def validate_image_upload(file: UploadedFile) -> None:
    """Raise ValueError unless `file` is a real raster image within the size limit.

    The browser-supplied content type is checked first, then Pillow verifies the bytes
    actually decode as an image (so a renamed non-image file is rejected).
    """
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise ValueError("Only JPEG, PNG, WebP or GIF images are allowed.")
    if file.size > MAX_IMAGE_SIZE_MB * 1024 * 1024:
        raise ValueError(f"Image exceeds the maximum size of {MAX_IMAGE_SIZE_MB}MB.")
    try:
        from PIL import Image
        file.seek(0)
        Image.open(file).verify()
    except Exception:
        raise ValueError("The uploaded file is not a valid image.")
    finally:
        file.seek(0)
