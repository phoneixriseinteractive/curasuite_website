"""CuraSuite — Newsletter Forms"""
from django import forms


class NewsletterSubscribeForm(forms.Form):
    email      = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={"placeholder": "your@email.com", "autocomplete": "email"}),
    )
    first_name = forms.CharField(
        max_length=100, required=False, label="First Name",
        widget=forms.TextInput(attrs={"placeholder": "First name (optional)"}),
    )

    def clean_email(self):
        return self.cleaned_data["email"].lower().strip()
