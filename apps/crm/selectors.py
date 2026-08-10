"""CuraSuite — CRM Selectors"""
from django.db.models import QuerySet
from .models import DemoRequest, Lead


def get_lead_by_email(email: str) -> Lead | None:
    return Lead.objects.filter(email__iexact=email).first()

def get_all_leads(status: str = None) -> QuerySet:
    qs = Lead.objects.select_related("assigned_to")
    if status:
        qs = qs.filter(status=status)
    return qs

def get_recent_leads(limit: int = 20) -> QuerySet:
    # -updated_at, not -created_at: capture_lead() merges a resubmission (same
    # phone/email) into the existing Lead rather than creating a new row, so
    # sorting by created_at alone would leave a just-resubmitted lead stuck
    # wherever it was first created instead of surfacing it as "recent".
    return Lead.objects.select_related("assigned_to").order_by("-updated_at")[:limit]

def get_pending_demos() -> QuerySet:
    return DemoRequest.objects.filter(
        status=DemoRequest.Status.PENDING
    ).select_related("lead").order_by("preferred_date")

def get_lead_with_history(pk) -> Lead | None:
    return (
        Lead.objects.filter(pk=pk)
        .prefetch_related("notes", "activities", "demo_requests")
        .first()
    )
