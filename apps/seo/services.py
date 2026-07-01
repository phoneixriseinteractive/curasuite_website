"""
CuraSuite — SEO Services
Business logic for creating and updating SEO metadata.
"""

from django.contrib.contenttypes.models import ContentType

from .models import SEOMetadata


def upsert_seo_metadata(obj, **kwargs) -> SEOMetadata:
    """
    Create or update SEO metadata for any model instance.

    Usage:
        upsert_seo_metadata(
            product,
            seo_title="CuraCMS — Website Platform for Doctors | CuraSuite",
            meta_description="...",
            schema_type="SoftwareApplication",
        )
    """
    ct = ContentType.objects.get_for_model(obj)
    seo, _ = SEOMetadata.objects.update_or_create(
        content_type=ct,
        object_id=obj.pk,
        defaults=kwargs,
    )
    return seo


def create_redirect(old_path: str, new_path: str, redirect_type: str = "301", note: str = "") -> "Redirect":
    """Create a new URL redirect."""
    from .models import Redirect
    return Redirect.objects.create(
        old_path=old_path,
        new_path=new_path,
        redirect_type=redirect_type,
        note=note,
    )
