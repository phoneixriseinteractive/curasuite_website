"""CuraSuite — Newsletter Service Tests"""
from unittest.mock import patch
from django.test import TestCase
from apps.newsletter.models import NewsletterSubscriber, NewsletterCampaign
from apps.newsletter.services import (
    subscribe, confirm_subscription, unsubscribe_by_token, send_campaign
)


class SubscribeTest(TestCase):
    @patch("apps.newsletter.services._send_confirmation_email")
    def test_creates_pending_subscriber(self, mock_email):
        sub, created = subscribe(email="test@clinic.com", first_name="Dr. Test")
        self.assertTrue(created)
        self.assertEqual(sub.status, NewsletterSubscriber.Status.PENDING)
        mock_email.assert_called_once()

    @patch("apps.newsletter.services._send_confirmation_email")
    def test_duplicate_email_not_recreated(self, mock_email):
        subscribe(email="same@lab.com")
        _, created = subscribe(email="same@lab.com")
        self.assertFalse(created)
        self.assertEqual(NewsletterSubscriber.objects.filter(email="same@lab.com").count(), 1)

    @patch("apps.newsletter.services._send_confirmation_email")
    def test_resubscribe_after_unsubscribe(self, mock_email):
        sub, _ = subscribe(email="bounce@test.com")
        sub.unsubscribe()
        self.assertEqual(sub.status, NewsletterSubscriber.Status.UNSUBSCRIBED)
        subscribe(email="bounce@test.com")
        sub.refresh_from_db()
        self.assertEqual(sub.status, NewsletterSubscriber.Status.PENDING)


class ConfirmSubscriptionTest(TestCase):
    @patch("apps.newsletter.services._send_confirmation_email")
    @patch("apps.newsletter.services._send_welcome_email")
    def test_confirm_valid_token(self, mock_welcome, mock_confirm):
        sub, _ = subscribe(email="confirm@test.com")
        result = confirm_subscription(str(sub.confirmation_token))
        self.assertIsNotNone(result)
        result.refresh_from_db()
        self.assertEqual(result.status, NewsletterSubscriber.Status.CONFIRMED)
        self.assertIsNotNone(result.confirmed_at)
        mock_welcome.assert_called_once()

    def test_invalid_token_returns_none(self):
        import uuid
        result = confirm_subscription(str(uuid.uuid4()))
        self.assertIsNone(result)


class UnsubscribeTest(TestCase):
    @patch("apps.newsletter.services._send_confirmation_email")
    @patch("apps.newsletter.services._send_welcome_email")
    def test_unsubscribe_by_token(self, mock_welcome, mock_email):
        sub, _ = subscribe(email="unsub@test.com")
        confirm_subscription(str(sub.confirmation_token))
        result = unsubscribe_by_token(str(sub.unsubscribe_token), reason="too_frequent")
        self.assertIsNotNone(result)
        result.refresh_from_db()
        self.assertEqual(result.status, NewsletterSubscriber.Status.UNSUBSCRIBED)
        self.assertEqual(result.unsubscribe_reason, "too_frequent")

    def test_invalid_token_returns_none(self):
        import uuid
        result = unsubscribe_by_token(str(uuid.uuid4()))
        self.assertIsNone(result)


class CampaignTest(TestCase):
    @patch("apps.newsletter.services._send_confirmation_email")
    @patch("apps.newsletter.services._send_welcome_email")
    def test_send_campaign_queues_sends(self, mock_welcome, mock_email):
        # Create 3 confirmed subscribers
        for i in range(3):
            sub, _ = subscribe(email=f"user{i}@test.com")
            confirm_subscription(str(sub.confirmation_token))

        campaign = NewsletterCampaign.objects.create(
            subject="Test Campaign",
            content_html="<p>Hello!</p>",
        )
        count = send_campaign(campaign)
        self.assertEqual(count, 3)
        campaign.refresh_from_db()
        self.assertEqual(campaign.status, NewsletterCampaign.Status.SENDING)
        self.assertEqual(campaign.total_sent, 3)

    def test_send_non_draft_campaign_raises(self):
        campaign = NewsletterCampaign.objects.create(
            subject="Already Sent", content_html="<p>hi</p>",
            status=NewsletterCampaign.Status.SENT,
        )
        with self.assertRaises(ValueError):
            send_campaign(campaign)
