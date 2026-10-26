from unittest import mock

from django.core.mail import EmailMultiAlternatives, get_connection
from django.test import SimpleTestCase, override_settings

from apps.core.email_backends import RESEND_API_URL

BACKEND = "apps.core.email_backends.ResendEmailBackend"


@override_settings(EMAIL_BACKEND=BACKEND, RESEND_API_KEY="re_test_key", DEFAULT_FROM_EMAIL="CuraSuite <hello@curasuite.com>")
class ResendEmailBackendTest(SimpleTestCase):
    def _message(self, connection):
        msg = EmailMultiAlternatives(
            subject="Your code", body="Code is: 123456", to=["admin@example.com"],
            reply_to=["support@curasuite.com"], connection=connection,
        )
        msg.attach_alternative("<p>123456</p>", "text/html")
        return msg

    @mock.patch("apps.core.email_backends.requests.Session.post")
    def test_posts_message_to_resend_api(self, post):
        post.return_value = mock.Mock(status_code=200, text='{"id":"abc"}')
        sent = self._message(get_connection()).send()

        self.assertEqual(sent, 1)
        url = post.call_args.args[0]
        payload = post.call_args.kwargs["json"]
        self.assertEqual(url, RESEND_API_URL)
        self.assertEqual(payload["from"], "CuraSuite <hello@curasuite.com>")
        self.assertEqual(payload["to"], ["admin@example.com"])
        self.assertEqual(payload["subject"], "Your code")
        self.assertEqual(payload["text"], "Code is: 123456")
        self.assertEqual(payload["html"], "<p>123456</p>")
        self.assertEqual(payload["reply_to"], ["support@curasuite.com"])

    @mock.patch("apps.core.email_backends.requests.Session.post")
    def test_sends_bearer_auth_header(self, post):
        post.return_value = mock.Mock(status_code=200, text="{}")
        connection = get_connection()
        connection.open()
        self.assertEqual(connection.session.headers["Authorization"], "Bearer re_test_key")
        connection.close()

    @mock.patch("apps.core.email_backends.requests.Session.post")
    def test_api_error_raises_when_not_silent(self, post):
        post.return_value = mock.Mock(status_code=422, text='{"message":"domain not verified"}')
        with self.assertRaises(RuntimeError):
            self._message(get_connection()).send()

    @mock.patch("apps.core.email_backends.requests.Session.post")
    def test_api_error_swallowed_when_silent(self, post):
        post.return_value = mock.Mock(status_code=500, text="oops")
        sent = self._message(get_connection(fail_silently=True)).send()
        self.assertEqual(sent, 0)

    @override_settings(RESEND_API_KEY="")
    def test_missing_api_key_raises(self):
        with self.assertRaises(ValueError):
            self._message(get_connection()).send()
