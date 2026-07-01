"""CuraSuite — Blogs Selectors"""
from django.db.models import Prefetch, QuerySet
from .models import Blog, BlogCategory, BlogComment, BlogTag


def get_published_blogs(limit: int = None) -> QuerySet:
    qs = Blog.objects.select_related("author", "category").prefetch_related("tags").order_by("-published_at")
    return qs[:limit] if limit else qs

def get_blog_by_slug(slug: str) -> Blog | None:
    return Blog.objects.select_related("author", "category").prefetch_related("tags").filter(slug=slug).first()

def get_featured_blogs(limit: int = 3) -> QuerySet:
    return Blog.objects.filter(is_featured=True).select_related("author", "category")[:limit]

def get_blogs_by_category(category_slug: str) -> QuerySet:
    return Blog.objects.filter(category__slug=category_slug).select_related("author", "category").order_by("-published_at")

def get_blogs_by_tag(tag_slug: str) -> QuerySet:
    return Blog.objects.filter(tags__slug=tag_slug).select_related("author", "category").order_by("-published_at")

def get_related_blogs(blog: Blog, limit: int = 3) -> QuerySet:
    qs = Blog.objects.exclude(pk=blog.pk)
    if blog.category:
        qs = qs.filter(category=blog.category)
    return qs.order_by("-published_at")[:limit]

def get_all_categories() -> QuerySet:
    return BlogCategory.objects.filter(is_active=True).order_by("sort_order")

def get_all_tags() -> QuerySet:
    return BlogTag.objects.order_by("name")

def get_approved_comments(blog: Blog) -> QuerySet:
    return BlogComment.objects.filter(blog=blog, status=BlogComment.Status.APPROVED).order_by("created_at")
