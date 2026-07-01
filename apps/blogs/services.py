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


def submit_comment(*, blog: Blog, author_name: str, author_email: str,
                   content: str, ip_address: str = None) -> BlogComment:
    return BlogComment.objects.create(
        blog=blog, author_name=author_name, author_email=author_email,
        content=content, ip_address=ip_address,
        status=BlogComment.Status.PENDING,
    )
