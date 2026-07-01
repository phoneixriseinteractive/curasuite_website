"""CuraSuite — Admin Panel Selectors
Aggregated queries that power the dashboard KPI cards and widgets.
"""
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta


def get_dashboard_stats() -> dict:
    """Return all KPI values needed for the dashboard in a single pass."""
    from apps.crm.models import Lead, DemoRequest
    from apps.blogs.models import Blog
    from apps.newsletter.models import NewsletterSubscriber
    from apps.pages.models import Page

    now   = timezone.now()
    today = now.date()
    week_ago  = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    total_leads       = Lead.objects.count()
    leads_this_week   = Lead.objects.filter(created_at__gte=week_ago).count()
    leads_this_month  = Lead.objects.filter(created_at__gte=month_ago).count()

    pending_demos     = DemoRequest.objects.filter(status="pending").count()
    confirmed_demos   = DemoRequest.objects.filter(status="confirmed").count()

    total_subscribers = NewsletterSubscriber.objects.filter(status="confirmed").count()
    new_subscribers   = NewsletterSubscriber.objects.filter(
        status="confirmed", confirmed_at__gte=week_ago
    ).count()

    published_blogs   = Blog.objects.filter(status="published").count()
    draft_blogs       = Blog.all_objects.filter(status="draft").count()

    published_pages   = Page.objects.filter(status="published").count()

    won_leads  = Lead.objects.filter(status="won").count()
    lost_leads = Lead.objects.filter(status="lost").count()

    return {
        "total_leads":       total_leads,
        "leads_this_week":   leads_this_week,
        "leads_this_month":  leads_this_month,
        "pending_demos":     pending_demos,
        "confirmed_demos":   confirmed_demos,
        "total_subscribers": total_subscribers,
        "new_subscribers":   new_subscribers,
        "published_blogs":   published_blogs,
        "draft_blogs":       draft_blogs,
        "published_pages":   published_pages,
        "won_leads":         won_leads,
        "lost_leads":        lost_leads,
    }


def get_recent_leads(limit: int = 8):
    from apps.crm.models import Lead
    return Lead.objects.select_related("assigned_to").order_by("-created_at")[:limit]


def get_recent_demo_requests(limit: int = 5):
    from apps.crm.models import DemoRequest
    return DemoRequest.objects.filter(
        status="pending"
    ).select_related("lead").order_by("-created_at")[:limit]


def get_leads_by_status() -> list[dict]:
    from apps.crm.models import Lead
    return list(
        Lead.objects.values("status")
        .annotate(count=Count("id"))
        .order_by("-count")
    )


def get_leads_by_source() -> list[dict]:
    from apps.crm.models import Lead
    return list(
        Lead.objects.values("source")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
