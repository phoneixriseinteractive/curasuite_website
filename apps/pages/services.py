"""CuraSuite — Pages Services"""
import logging
from django.db import transaction
from django.utils.text import slugify
from .models import Page, PageRevision
from apps.seo.services import upsert_seo_metadata

logger = logging.getLogger(__name__)


@transaction.atomic
def create_page(*, title: str, content: str = "", page_type: str = "custom",
                excerpt: str = "", created_by=None, seo: dict = None) -> Page:
    page = Page.all_objects.create(
        title=title, content=content, page_type=page_type,
        excerpt=excerpt, created_by=created_by,
    )
    _save_revision(page, editor=created_by)
    if seo:
        upsert_seo_metadata(page, **seo)
    logger.info("Page created: %s", title)
    return page


@transaction.atomic
def update_page(page: Page, *, title: str = None, content: str = None,
                updated_by=None, **kwargs) -> Page:
    if title:
        page.title = title
    if content is not None:
        page.content = content
    for k, v in kwargs.items():
        setattr(page, k, v)
    page.increment_version()
    page.updated_by = updated_by
    page.save()
    _save_revision(page, editor=updated_by)
    return page


def _save_revision(page: Page, editor=None):
    PageRevision.objects.create(
        page=page, title=page.title,
        content=page.content,
        revision_number=page.version,
        editor=editor,
    )
