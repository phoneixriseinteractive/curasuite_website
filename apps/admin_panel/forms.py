"""CuraSuite — Admin Panel Auth Forms"""
from django import forms
from django.contrib.auth.forms import PasswordResetForm


class AdminLoginForm(forms.Form):
    email    = forms.EmailField(
        label="Email address",
        widget=forms.EmailInput(attrs={"placeholder": "admin@curasuite.com", "autocomplete": "email", "autofocus": True}),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"placeholder": "••••••••••••", "autocomplete": "current-password"}),
    )
    remember_me = forms.BooleanField(required=False, label="Keep me signed in")


class OTPVerifyForm(forms.Form):
    code = forms.CharField(
        label="Verification code",
        min_length=6,
        max_length=6,
        widget=forms.TextInput(attrs={
            "placeholder": "••••••",
            "inputmode": "numeric",
            "autocomplete": "one-time-code",
            "pattern": "[0-9]*",
            "autofocus": True,
        }),
    )
    trust_device = forms.BooleanField(required=False, label="Trust this device for 30 days")

    def clean_code(self):
        code = self.cleaned_data["code"].strip()
        if not code.isdigit() or len(code) != 6:
            raise forms.ValidationError("Enter the 6-digit code from your email.")
        return code


class AdminPasswordResetForm(PasswordResetForm):
    """Only sends a reset email for staff accounts (non-staff have no /manage/ access)."""

    def get_users(self, email):
        return (u for u in super().get_users(email) if u.is_staff)
