"""CuraSuite — Admin Panel Auth Forms"""
from django import forms


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
