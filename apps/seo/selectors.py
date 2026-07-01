"""
CuraSuite — SEO Selectors
Read-only query logic for SEO data.
"""

from django.contrib.contenttypes.models import ContentType

from .models import Redirect, SEOMetadata


def get_seo_for_object(obj) -> SEOMetadata | None:
    """Return the SEOMetadata for any model instance, or None if not set."""
    ct = ContentType.objects.get_for_model(obj)
    return SEOMetadata.objects.filter(content_type=ct, object_id=obj.pk).first()


def get_redirect_for_path(path: str) -> Redirect | None:
    """Return an active Redirect for the given path, or None."""
    return Redirect.objects.filter(old_path=path, is_active=True).first()


def get_all_redirects():
    """Return all active redirects ordered by old_path."""
    return Redirect.objects.filter(is_active=True).order_by("old_path")
