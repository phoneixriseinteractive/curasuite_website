"""CuraSuite — Newsletter Selectors"""
from django.db.models import QuerySet
from .models import NewsletterCampaign, NewsletterSubscriber


def get_active_subscribers() -> QuerySet:
    return NewsletterSubscriber.objects.filter(status=NewsletterSubscriber.Status.CONFIRMED)

def get_subscriber_by_email(email: str) -> NewsletterSubscriber | None:
    return NewsletterSubscriber.objects.filter(email__iexact=email).first()

def get_subscriber_by_confirmation_token(token) -> NewsletterSubscriber | None:
    return NewsletterSubscriber.objects.filter(confirmation_token=token).first()

def get_subscriber_by_unsubscribe_token(token) -> NewsletterSubscriber | None:
    return NewsletterSubscriber.objects.filter(unsubscribe_token=token).first()

def get_all_campaigns() -> QuerySet:
    return NewsletterCampaign.objects.order_by("-created_at")

def get_sent_campaigns() -> QuerySet:
    return NewsletterCampaign.objects.filter(status=NewsletterCampaign.Status.SENT)
