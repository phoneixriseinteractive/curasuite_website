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


class AppointmentForm(forms.Form):
    """
    Global appointment/demo booking widget form.
    Used by the 2-step modal: product selection → this form, and by the ad landing pages
    (apps/landing_pages), which intentionally show only 3 fields (name, phone, clinic) to
    minimize lead-form friction. Email and city are optional — collected on the follow-up
    call instead — since name, phone, clinic name, and specialty are the only fields that
    matter for a callback.
    """
    product      = forms.CharField(max_length=50, widget=forms.HiddenInput())  # CuraCMS / CuraLabs / CuraSuite
    full_name    = forms.CharField(max_length=200, label="Full Name")
    phone        = forms.CharField(max_length=20, label="Phone Number")
    email        = forms.EmailField(required=False, label="Email Address")
    city         = forms.CharField(max_length=100, required=False, label="City")
    organization = forms.CharField(max_length=200, label="Clinic Name")
    specialty    = forms.ChoiceField(choices=Lead.Specialty.choices, label="Specialty")

    # Attribution — hidden, filled by JS from URL params
    source       = forms.CharField(max_length=20, required=False, widget=forms.HiddenInput())
    utm_source   = forms.CharField(max_length=100, required=False, widget=forms.HiddenInput())
    utm_medium   = forms.CharField(max_length=100, required=False, widget=forms.HiddenInput())
    utm_campaign = forms.CharField(max_length=100, required=False, widget=forms.HiddenInput())
    utm_content  = forms.CharField(max_length=100, required=False, widget=forms.HiddenInput())

    def clean_full_name(self):
        name = self.cleaned_data["full_name"].strip()
        if len(name) < 2:
            raise forms.ValidationError("Please enter your full name.")
        return name

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        digits = "".join(c for c in phone if c.isdigit())
        if len(digits) < 10:
            raise forms.ValidationError("Please enter a valid phone number.")
        return phone

    def clean_email(self):
        email = self.cleaned_data.get("email", "")
        return email.lower().strip() if email else ""
