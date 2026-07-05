"""CuraSuite — Newsletter Services"""
import logging
from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.template.loader import render_to_string
from django.utils import timezone

from .models import NewsletterCampaign, NewsletterSend, NewsletterSubscriber

logger = logging.getLogger(__name__)


def subscribe(
    *,
    email: str,
    first_name: str = "",
    source: str = "",
    ip_address: str = None,
    referrer: str = "",
) -> tuple[NewsletterSubscriber, bool]:
    """
    Subscribe an email address. Returns (subscriber, created).
    If already confirmed, returns existing record without re-sending.
    If pending, resends confirmation email.
    """
    email = email.lower().strip()
    subscriber, created = NewsletterSubscriber.objects.get_or_create(
        email=email,
        defaults=dict(
            first_name=first_name, source=source,
            ip_address=ip_address, referrer=referrer,
        ),
    )

    if not created and subscriber.status == NewsletterSubscriber.Status.CONFIRMED:
        return subscriber, False

    if not created and subscriber.status == NewsletterSubscriber.Status.UNSUBSCRIBED:
        # Allow re-subscription by resetting to pending
        subscriber.status = NewsletterSubscriber.Status.PENDING
        subscriber.unsubscribed_at = None
        subscriber.save(update_fields=["status", "unsubscribed_at", "updated_at"])

    # Send confirmation email
    _send_confirmation_email(subscriber)
    subscriber.confirmation_sent_at = timezone.now()
    subscriber.save(update_fields=["confirmation_sent_at", "updated_at"])

    logger.info("Newsletter subscription initiated: %s", email)
    return subscriber, created


def confirm_subscription(token: str) -> NewsletterSubscriber | None:
    """Confirm a subscription via the token from the confirmation email."""
    try:
        subscriber = NewsletterSubscriber.objects.get(confirmation_token=token)
    except NewsletterSubscriber.DoesNotExist:
        return None

    if subscriber.status != NewsletterSubscriber.Status.CONFIRMED:
        subscriber.confirm()
        _send_welcome_email(subscriber)
        logger.info("Newsletter subscription confirmed: %s", subscriber.email)

    return subscriber


def unsubscribe_by_token(token: str, reason: str = "") -> NewsletterSubscriber | None:
    """Unsubscribe via the one-click token from any campaign email."""
    try:
        subscriber = NewsletterSubscriber.objects.get(unsubscribe_token=token)
    except NewsletterSubscriber.DoesNotExist:
        return None

    if subscriber.status != NewsletterSubscriber.Status.UNSUBSCRIBED:
        subscriber.unsubscribe(reason=reason)
        logger.info("Newsletter unsubscribe: %s", subscriber.email)

    return subscriber


def _send_confirmation_email(subscriber: NewsletterSubscriber) -> None:
    """Send the double opt-in confirmation email."""
    site_name = getattr(settings, "CURASUITE_SITE_NAME", "CuraSuite")
    confirm_url = f"{_get_base_url()}/newsletter/confirm/{subscriber.confirmation_token}/"

    try:
        send_mail(
            subject=f"Confirm your subscription to {site_name} Insights",
            message=(
                f"Hi {subscriber.first_name or 'there'},\n\n"
                f"Please confirm your subscription by visiting:\n{confirm_url}\n\n"
                f"If you didn't subscribe, you can ignore this email.\n\n"
                f"— The {site_name} Team"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[subscriber.email],
            fail_silently=True,
        )
    except Exception as e:
        logger.warning("Failed to send confirmation email to %s: %s", subscriber.email, e)


def _send_welcome_email(subscriber: NewsletterSubscriber) -> None:
    """Send the welcome email after confirmation."""
    site_name = getattr(settings, "CURASUITE_SITE_NAME", "CuraSuite")
    unsub_url = f"{_get_base_url()}/newsletter/unsubscribe/{subscriber.unsubscribe_token}/"

    try:
        send_mail(
            subject=f"Welcome to {site_name} Insights!",
            message=(
                f"Hi {subscriber.first_name or 'there'},\n\n"
                f"You're now subscribed to {site_name} Insights — practical healthcare "
                f"technology guides, product updates, and clinic growth strategies.\n\n"
                f"To unsubscribe: {unsub_url}\n\n"
                f"— The {site_name} Team"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[subscriber.email],
            fail_silently=True,
        )
    except Exception as e:
        logger.warning("Failed to send welcome email to %s: %s", subscriber.email, e)


def _get_base_url() -> str:
    return getattr(settings, "CURASUITE_BASE_URL", "https://curasuite.com")


@transaction.atomic
def send_campaign(campaign: NewsletterCampaign) -> int:
    """
    Queue delivery records for all confirmed subscribers.
    NOTE: This only creates NewsletterSend records — actual sending is not
    yet wired up (no Celery/async pipeline on this deployment). Implement a
    synchronous sender before using this in production.
    Returns the number of queued sends.
    """
    if campaign.status != NewsletterCampaign.Status.DRAFT:
        raise ValueError(f"Campaign '{campaign.subject}' is not in draft status.")

    subscribers = NewsletterSubscriber.objects.filter(
        status=NewsletterSubscriber.Status.CONFIRMED
    )

    sends = [
        NewsletterSend(campaign=campaign, subscriber=sub)
        for sub in subscribers
        if not NewsletterSend.objects.filter(campaign=campaign, subscriber=sub).exists()
    ]
    NewsletterSend.objects.bulk_create(sends, ignore_conflicts=True)

    campaign.status   = NewsletterCampaign.Status.SENDING
    campaign.sent_at  = timezone.now()
    campaign.total_sent = subscribers.count()
    campaign.save(update_fields=["status", "sent_at", "total_sent", "updated_at"])

    logger.info("Campaign '%s' queued for %d subscribers", campaign.subject, len(sends))
    return len(sends)
