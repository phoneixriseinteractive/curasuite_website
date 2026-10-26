"""CuraSuite — Resend email backend (HTTP API, no SDK dependency)"""
import logging

import requests
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend

logger = logging.getLogger(__name__)

RESEND_API_URL = "https://api.resend.com/emails"


class ResendEmailBackend(BaseEmailBackend):
    """Sends Django EmailMessage objects through Resend's /emails endpoint."""

    def __init__(self, api_key=None, timeout=None, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.api_key = api_key or getattr(settings, "RESEND_API_KEY", "")
        self.timeout = timeout or getattr(settings, "RESEND_TIMEOUT_SECONDS", 10)
        self.session = None

    def open(self):
        if self.session is not None:
            return False
        if not self.api_key:
            if self.fail_silently:
                return False
            raise ValueError("RESEND_API_KEY is not configured.")
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        })
        return True

    def close(self):
        if self.session is not None:
            self.session.close()
            self.session = None

    def send_messages(self, email_messages):
        if not email_messages:
            return 0
        new_session = self.open()
        if self.session is None:
            return 0
        sent = 0
        try:
            for message in email_messages:
                if self._send(message):
                    sent += 1
        finally:
            if new_session:
                self.close()
        return sent

    def _payload(self, message):
        payload = {
            "from": message.from_email or settings.DEFAULT_FROM_EMAIL,
            "to": message.to,
            "subject": message.subject,
            "text": message.body,
        }
        if message.cc:
            payload["cc"] = message.cc
        if message.bcc:
            payload["bcc"] = message.bcc
        if message.reply_to:
            payload["reply_to"] = message.reply_to
        if message.extra_headers:
            payload["headers"] = message.extra_headers
        for content, mimetype in getattr(message, "alternatives", []) or []:
            if mimetype == "text/html":
                payload["html"] = content
        return payload

    def _send(self, message):
        if not message.recipients():
            return False
        try:
            response = self.session.post(RESEND_API_URL, json=self._payload(message), timeout=self.timeout)
            if response.status_code >= 400:
                raise RuntimeError(f"Resend API error {response.status_code}: {response.text[:500]}")
        except Exception:
            logger.exception("Resend failed to send email to %s", message.to)
            if not self.fail_silently:
                raise
            return False
        return True
