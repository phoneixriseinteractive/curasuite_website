"""CuraSuite — CRM Views"""
import logging
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages

from .forms import ContactForm, DemoRequestForm, AppointmentForm
from .services import capture_lead, create_demo_request
from .models import Lead
from apps.integrations.services import verify_captcha

CAPTCHA_ERROR = "We couldn't verify you're human. Please try again."

logger = logging.getLogger(__name__)


def contact_page(request):
    form = DemoRequestForm(request.POST or None)
    if request.method == "POST" and form.is_valid() and not verify_captcha(request):
        form.add_error(None, CAPTCHA_ERROR)
    if request.method == "POST" and form.is_valid():
        d = form.cleaned_data
        lead, created = capture_lead(
            full_name=d["full_name"], email=d["email"],
            phone=d.get("phone", ""), organization=d.get("organization", ""),
            city=d.get("city", ""), message=d.get("message", ""),
            business_type=d.get("business_type", ""),
            product_interest=d.get("product_interest", ""),
            source="contact_form",
            referrer_url=request.META.get("HTTP_REFERER", ""),
        )
        if d.get("preferred_date") or d.get("product_interest"):
            create_demo_request(
                lead=lead,
                product_interest=d.get("product_interest", ""),
                preferred_date=d.get("preferred_date"),
                preferred_time=d.get("preferred_time", ""),
            )

        # HTMX response
        if request.headers.get("HX-Request"):
            return render(request, "crm/partials/contact_success.html", {"lead": lead})

        return redirect("crm:contact_success")

    return render(request, "crm/contact.html", {"form": form})


def contact_success(request):
    return render(request, "crm/contact_success.html")


@require_POST
def demo_request_htmx(request):
    """HTMX endpoint — demo form submitted inline from any page."""
    form = DemoRequestForm(request.POST)
    if form.is_valid() and not verify_captcha(request):
        form.add_error(None, CAPTCHA_ERROR)
    if form.is_valid():
        d = form.cleaned_data
        lead, _ = capture_lead(
            full_name=d["full_name"], email=d["email"],
            phone=d.get("phone", ""), organization=d.get("organization", ""),
            city=d.get("city", ""), product_interest=d.get("product_interest", ""),
            source="demo_form",
            referrer_url=request.META.get("HTTP_REFERER", ""),
        )
        create_demo_request(
            lead=lead,
            product_interest=d.get("product_interest", ""),
            preferred_date=d.get("preferred_date"),
            preferred_time=d.get("preferred_time", ""),
        )
        return render(request, "crm/partials/contact_success.html", {"lead": lead})

    return render(request, "crm/partials/demo_form.html", {"form": form})

def _resolve_source(utm_source: str, explicit_source: str = "") -> str:
    """Map a UTM source string (or explicit override) to a Lead.Source choice."""
    if explicit_source:
        return explicit_source
    if not utm_source:
        return Lead.Source.DIRECT
    s = utm_source.lower()
    if "google" in s:
        return Lead.Source.GOOGLE_ADS
    if "facebook" in s or "meta" in s or "instagram" in s or "fb" in s:
        return Lead.Source.META_ADS
    return Lead.Source.OTHER


@require_POST
def appointment_widget_submit(request):
    """
    Global 'Book Demo / Appointment' widget — Step 2 submission.
    Always returns an HTMX partial (widget is HTMX-only, no full-page fallback).
    """
    form = AppointmentForm(request.POST)
    if form.is_valid() and not verify_captcha(request):
        form.add_error(None, CAPTCHA_ERROR)
    if form.is_valid():
        d = form.cleaned_data
        source = _resolve_source(d.get("utm_source", ""), d.get("source", ""))

        lead, created = capture_lead(
            full_name=d["full_name"],
            email=d.get("email", ""),
            phone=d["phone"],
            organization=d["organization"],
            city=d["city"],
            business_type="",
            specialty=d["specialty"],
            product_interest=d["product"],
            source=source,
            utm_source=d.get("utm_source", ""),
            utm_medium=d.get("utm_medium", ""),
            utm_campaign=d.get("utm_campaign", ""),
            utm_content=d.get("utm_content", ""),
            referrer_url=request.META.get("HTTP_REFERER", ""),
        )
        create_demo_request(lead=lead, product_interest=d["product"])

        return render(request, "crm/partials/appointment_success.html", {
            "lead": lead, "product": d["product"], "lp_slug": request.POST.get("lp_slug", ""),
        })

    return render(request, "crm/partials/appointment_form.html", {
        "form": form, "product": request.POST.get("product", ""),
    })
