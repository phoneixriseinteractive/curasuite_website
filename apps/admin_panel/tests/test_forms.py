"""CuraSuite — Admin Panel Auth Forms Tests"""
from django.test import TestCase

from apps.accounts.models import User
from apps.admin_panel.forms import AdminPasswordResetForm, OTPVerifyForm


class AdminPasswordResetFormTest(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            email="staff@curasuite.com", password="s3cur3-passw0rd!", first_name="Staff", is_staff=True,
        )
        self.regular_user = User.objects.create_user(
            email="regular@curasuite.com", password="s3cur3-passw0rd!", first_name="Regular", is_staff=False,
        )

    def test_get_users_includes_staff_account(self):
        form = AdminPasswordResetForm(data={"email": "staff@curasuite.com"})
        self.assertTrue(form.is_valid())
        self.assertIn(self.staff_user, list(form.get_users("staff@curasuite.com")))

    def test_get_users_excludes_non_staff_account(self):
        form = AdminPasswordResetForm(data={"email": "regular@curasuite.com"})
        self.assertTrue(form.is_valid())
        self.assertEqual(list(form.get_users("regular@curasuite.com")), [])


class OTPVerifyFormTest(TestCase):
    def test_accepts_six_digit_code(self):
        form = OTPVerifyForm(data={"code": "123456"})
        self.assertTrue(form.is_valid())

    def test_rejects_non_numeric_code(self):
        form = OTPVerifyForm(data={"code": "12a45b"})
        self.assertFalse(form.is_valid())

    def test_rejects_wrong_length_code(self):
        form = OTPVerifyForm(data={"code": "123"})
        self.assertFalse(form.is_valid())
