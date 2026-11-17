"""CuraSuite — Blogs Services"""
import logging
from django.db import transaction
from .models import Blog, BlogComment, BlogRevision
from apps.seo.services import upsert_seo_metadata

logger = logging.getLogger(__name__)


@transaction.atomic
def create_blog(*, title: str, content: str, excerpt: str, author=None,
                category=None, created_by=None, seo: dict = None) -> Blog:
    blog = Blog.all_objects.create(
        title=title, content=content, excerpt=excerpt,
        author=author or created_by, created_by=created_by, category=category,
    )
    BlogRevision.objects.create(
        blog=blog, title=title, content=content, revision_number=1, editor=created_by,
    )
    if seo:
        upsert_seo_metadata(blog, **seo)
    logger.info("Blog created: %s", title)
    return blog


@transaction.atomic
def update_blog(blog: Blog, *, updated_by=None, **kwargs) -> Blog:
    for k, v in kwargs.items():
        setattr(blog, k, v)
    blog.increment_version()
    blog.updated_by = updated_by
    blog.save()
    BlogRevision.objects.create(
        blog=blog, title=blog.title, content=blog.content,
        revision_number=blog.version, editor=updated_by,
    )
    return blog


def set_featured_image(blog: Blog, *, image=None, alt_text: str = None, remove: bool = False) -> Blog:
    """Replace, remove, or re-caption a post's featured image.

    `image` is an UploadedFile (validated here; raises ValueError if invalid).
    `alt_text=None` leaves the existing alt text untouched. The previous image file is
    deleted from storage when replaced or removed — revisions don't reference it.
    """
    from apps.media.validators import validate_image_upload

    fields = []
    if image is not None:
        validate_image_upload(image)
        if blog.featured_image:
            blog.featured_image.delete(save=False)
        blog.featured_image = image
        fields.append("featured_image")
    elif remove and blog.featured_image:
        blog.featured_image.delete(save=False)
        blog.featured_image = None
        fields.append("featured_image")
    if alt_text is not None and alt_text != blog.featured_image_alt:
        blog.featured_image_alt = alt_text
        fields.append("featured_image_alt")
    if fields:
        blog.save(update_fields=fields + ["updated_at"])
    return blog


def submit_comment(*, blog: Blog, author_name: str, author_email: str,
                   content: str, ip_address: str = None) -> BlogComment:
    return BlogComment.objects.create(
        blog=blog, author_name=author_name, author_email=author_email,
        content=content, ip_address=ip_address,
        status=BlogComment.Status.PENDING,
    )
