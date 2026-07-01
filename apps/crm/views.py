"""CuraSuite — CRM Views"""
import logging
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages

from .forms import ContactForm, DemoRequestForm
from .services import capture_lead, create_demo_request

logger = logging.getLogger(__name__)


def contact_page(request):
    form = DemoRequestForm(request.POST or None)
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
