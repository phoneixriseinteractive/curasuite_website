"""CuraSuite — CRM Forms"""
from django import forms
from .models import Lead


class ContactForm(forms.Form):
    full_name        = forms.CharField(max_length=200, label="Full Name")
    email            = forms.EmailField(label="Email Address")
    phone            = forms.CharField(max_length=20, required=False, label="Phone Number")
    organization     = forms.CharField(max_length=200, required=False, label="Clinic / Organisation")
    city             = forms.CharField(max_length=100, required=False, label="City")
    product_interest = forms.ChoiceField(
        required=False,
        choices=[("", "Select a product")] + [
            ("CuraCMS", "CuraCMS — Website for Doctors"),
            ("CuraLabs", "CuraLabs — Platform for Labs"),
            ("CuraSuite", "CuraSuite — Clinic Management"),
            ("Not sure", "Not sure yet"),
        ],
        label="Product Interest",
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 4}),
        max_length=2000,
        required=False,
        label="Message",
    )

    def clean_email(self):
        return self.cleaned_data["email"].lower().strip()

    def clean_full_name(self):
        name = self.cleaned_data["full_name"].strip()
        if len(name) < 2:
            raise forms.ValidationError("Please enter your full name.")
        return name


class DemoRequestForm(ContactForm):
    business_type = forms.ChoiceField(
        choices=[("", "Select business type")] + list(Lead.BusinessType.choices),
        required=False,
        label="Business Type",
    )
    preferred_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
        label="Preferred Demo Date",
    )
    preferred_time = forms.ChoiceField(
        required=False,
        choices=[
            ("", "Select time slot"),
            ("10:00 AM", "10:00 AM"),
            ("11:00 AM", "11:00 AM"),
            ("12:00 PM", "12:00 PM"),
            ("2:00 PM",  "2:00 PM"),
            ("3:00 PM",  "3:00 PM"),
            ("4:00 PM",  "4:00 PM"),
            ("5:00 PM",  "5:00 PM"),
        ],
        label="Preferred Time",
    )
