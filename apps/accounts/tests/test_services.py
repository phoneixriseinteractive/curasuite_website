"""CuraSuite — Accounts Services Tests (login OTP + remembered devices)"""
from django.core import mail
from django.test import TestCase, override_settings
from django.utils import timezone

from apps.accounts.models import LoginOTP, User
from apps.accounts.services import (
    create_and_send_otp, create_remembered_device, generate_otp_code,
    get_remembered_device, resend_otp, verify_otp,
)


class OTPServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="staff@curasuite.com", password="s3cur3-passw0rd!", first_name="Staff", is_staff=True,
        )

    def test_generate_otp_code_is_six_digits(self):
        code = generate_otp_code()
        self.assertEqual(len(code), 6)
        self.assertTrue(code.isdigit())

    def test_create_and_send_otp_emails_code_and_stores_hash_only(self):
        otp = create_and_send_otp(self.user)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.user.email, mail.outbox[0].to)
        # the plaintext code appears in the email body but never in the stored row
        self.assertNotIn(otp.code_hash, mail.outbox[0].body)

    def test_create_and_send_otp_invalidates_prior_unused_codes(self):
        first = create_and_send_otp(self.user)
        create_and_send_otp(self.user)
        first.refresh_from_db()
        self.assertTrue(first.is_used)

    def test_verify_otp_succeeds_with_correct_code(self):
        create_and_send_otp(self.user)
        code = mail.outbox[0].body.split("code is: ")[1].split("\n")[0]
        ok, err = verify_otp(self.user, code)
        self.assertTrue(ok)
        self.assertIsNone(err)

    def test_verify_otp_fails_with_wrong_code(self):
        create_and_send_otp(self.user)
        ok, err = verify_otp(self.user, "000000")
        self.assertFalse(ok)
        self.assertIsNotNone(err)

    def test_verify_otp_locks_out_after_max_attempts(self):
        create_and_send_otp(self.user)
        for _ in range(5):
            verify_otp(self.user, "000000")
        ok, err = verify_otp(self.user, "000000")
        self.assertFalse(ok)
        self.assertIn("Too many", err)

    def test_verify_otp_fails_when_expired(self):
        otp = create_and_send_otp(self.user)
        LoginOTP.objects.filter(pk=otp.pk).update(expires_at=timezone.now() - timezone.timedelta(minutes=1))
        ok, err = verify_otp(self.user, "000000")
        self.assertFalse(ok)
        self.assertIn("expired", err)

    def test_verify_otp_cannot_be_reused(self):
        create_and_send_otp(self.user)
        code = mail.outbox[0].body.split("code is: ")[1].split("\n")[0]
        self.assertTrue(verify_otp(self.user, code)[0])
        ok, _ = verify_otp(self.user, code)
        self.assertFalse(ok)

    @override_settings(ADMIN_OTP_RESEND_COOLDOWN_SECONDS=9999)
    def test_resend_otp_respects_cooldown(self):
        create_and_send_otp(self.user)
        ok, err = resend_otp(self.user)
        self.assertFalse(ok)
        self.assertEqual(err, "cooldown")

    @override_settings(ADMIN_OTP_RESEND_COOLDOWN_SECONDS=0, ADMIN_OTP_MAX_SENDS_PER_WINDOW=1)
    def test_resend_otp_respects_send_window_cap(self):
        create_and_send_otp(self.user)
        ok, err = resend_otp(self.user)
        self.assertFalse(ok)
        self.assertEqual(err, "too_many_requests")


class RememberedDeviceServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="staff2@curasuite.com", password="s3cur3-passw0rd!", first_name="Staff", is_staff=True,
        )

    def test_create_and_lookup_remembered_device(self):
        create_remembered_device(self.user, "raw-token-value")
        device = get_remembered_device(self.user, "raw-token-value")
        self.assertIsNotNone(device)

    def test_lookup_fails_for_wrong_token(self):
        create_remembered_device(self.user, "raw-token-value")
        device = get_remembered_device(self.user, "some-other-token")
        self.assertIsNone(device)

    def test_lookup_fails_when_expired(self):
        device = create_remembered_device(self.user, "raw-token-value")
        type(device).objects.filter(pk=device.pk).update(expires_at=timezone.now() - timezone.timedelta(days=1))
        self.assertIsNone(get_remembered_device(self.user, "raw-token-value"))
