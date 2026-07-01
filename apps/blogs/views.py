"""CuraSuite — Blogs Views"""
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import render
from apps.seo.selectors import get_seo_for_object
from .selectors import (
    get_all_categories, get_all_tags, get_blog_by_slug,
    get_blogs_by_category, get_blogs_by_tag, get_featured_blogs,
    get_published_blogs, get_related_blogs, get_approved_comments,
)


def blog_list(request):
    blogs = get_published_blogs()
    paginator = Paginator(blogs, 12)
    page = paginator.get_page(request.GET.get("page", 1))
    return render(request, "blogs/blog_list.html", {
        "blogs": page, "featured": get_featured_blogs(),
        "categories": get_all_categories(), "tags": get_all_tags(),
    })


def blog_detail(request, slug: str):
    blog = get_blog_by_slug(slug)
    if not blog:
        raise Http404(f"Blog post '{slug}' not found.")
    blog.increment_view_count()
    seo = get_seo_for_object(blog)
    return render(request, "blogs/blog_detail.html", {
        "blog": blog,
        "related": get_related_blogs(blog),
        "comments": get_approved_comments(blog),
        "seo": seo,
    })


def blog_category(request, slug: str):
    from .selectors import get_all_categories
    blogs = get_blogs_by_category(slug)
    paginator = Paginator(blogs, 12)
    page = paginator.get_page(request.GET.get("page", 1))
    return render(request, "blogs/blog_list.html", {
        "blogs": page, "categories": get_all_categories(),
        "active_category_slug": slug,
    })


def blog_tag(request, slug: str):
    blogs = get_blogs_by_tag(slug)
    paginator = Paginator(blogs, 12)
    page = paginator.get_page(request.GET.get("page", 1))
    return render(request, "blogs/blog_list.html", {
        "blogs": page, "active_tag_slug": slug,
        "categories": get_all_categories(),
    })
