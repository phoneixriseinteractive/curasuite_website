"""CuraSuite — CRM Services"""
import logging
from django.db import transaction
from django.utils import timezone
from .models import DemoRequest, Lead, LeadActivity
from .selectors import get_lead_by_email

logger = logging.getLogger(__name__)


def _log_activity(lead: Lead, activity_type: str, description: str = "", performed_by=None):
    LeadActivity.objects.create(
        lead=lead, activity_type=activity_type,
        description=description, performed_by=performed_by,
    )


@transaction.atomic
def capture_lead(
    *,
    full_name: str,
    email: str,
    phone: str = "",
    organization: str = "",
    city: str = "",
    message: str = "",
    business_type: str = "",
    product_interest: str = "",
    source: str = Lead.Source.OTHER,
    utm_source: str = "",
    utm_medium: str = "",
    utm_campaign: str = "",
    utm_content: str = "",
    referrer_url: str = "",
) -> tuple[Lead, bool]:
    """
    Create or update a lead from a form submission.
    Returns (lead, created) tuple.
    If email already exists, updates contact details and logs the re-submission.
    """
    existing = get_lead_by_email(email)

    if existing:
        # Update fields that may have changed
        existing.phone        = phone or existing.phone
        existing.organization = organization or existing.organization
        existing.city         = city or existing.city
        if message:
            existing.message  = message
        existing.save(update_fields=["phone", "organization", "city", "message", "updated_at"])
        _log_activity(existing, LeadActivity.ActivityType.NOTE_ADDED,
                      f"Re-submitted form from source: {source}")
        logger.info("Lead updated: %s", email)
        return existing, False

    lead = Lead.objects.create(
        full_name=full_name, email=email, phone=phone,
        organization=organization, city=city, message=message,
        business_type=business_type, product_interest=product_interest,
        source=source, utm_source=utm_source, utm_medium=utm_medium,
        utm_campaign=utm_campaign, utm_content=utm_content,
        referrer_url=referrer_url,
    )
    _log_activity(lead, LeadActivity.ActivityType.CREATED, f"Lead captured via {source}")
    logger.info("Lead created: %s", email)
    return lead, True


@transaction.atomic
def create_demo_request(
    *,
    lead: Lead,
    product_interest: str = "",
    preferred_date=None,
    preferred_time: str = "",
) -> DemoRequest:
    """Create a demo request linked to an existing lead."""
    demo = DemoRequest.objects.create(
        lead=lead,
        product_interest=product_interest,
        preferred_date=preferred_date,
        preferred_time=preferred_time,
    )
    _log_activity(lead, LeadActivity.ActivityType.DEMO_BOOKED,
                  f"Demo requested for: {product_interest}")
    lead.status = Lead.Status.DEMO_SCHEDULED
    lead.save(update_fields=["status", "updated_at"])
    return demo


@transaction.atomic
def update_lead_status(lead: Lead, new_status: str, performed_by=None) -> Lead:
    """Update a lead's pipeline status and log the change."""
    old_status = lead.status
    lead.status = new_status
    lead.save(update_fields=["status", "updated_at"])
    _log_activity(
        lead, LeadActivity.ActivityType.STATUS_CHANGED,
        f"Status: {old_status} → {new_status}",
        performed_by=performed_by,
    )
    return lead
