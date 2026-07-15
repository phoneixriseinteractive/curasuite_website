"""CuraSuite — Landing Pages Public Views"""
from django.http import Http404
from django.shortcuts import render
from .selectors import get_landing_page_by_slug, get_testimonials_for_landing_page

# Real CuraCMS product screenshots for the "See CuraCMS in Action" slider on
# curacms.html — (filename in static/img/cms-screen-shots/, caption).
CMS_SCREENSHOTS = [
    ("homepage-section-1.png",    "Patient-Facing Website Homepage"),
    ("homepage-doctor-profile.png","Doctor Bio Shown on the Homepage"),
    ("doctor-profile.png",         "Manage Doctor Profiles"),
    ("doctor-profile-page-2.png",  "Doctor Profile — Public Page"),
    ("treatments.png",             "Treatment & Services Management"),
    ("homepage-treatment.png",     "Treatments Showcased to Patients"),
    ("book-appointment-widget.png","Patient Appointment Booking Widget"),
    ("appointment-time-slots.png", "Weekly Slot Management"),
    ("booked-appointments.png",    "Appointments Dashboard"),
    ("contact-page.png",           "Contact & Location Page"),
    ("contact-page-2.png",         "Contact Page — Alternate Layout"),
    ("homepage-how-it-works.png",  "How It Works — Patient Journey"),
    ("ai-chatbot.png",             "AI Chatbot Configuration"),
    ("pages.png",                  "CMS Page Manager"),
    ("user-management.png",        "Role-Based User Access"),
    ("site-settings.png",          "Site Settings Panel"),
    ("site-settings-2.png",        "Site Settings — Advanced Options"),
]


def landing_page_detail(request, slug: str):
    page = get_landing_page_by_slug(slug)
    if not page or not page.is_published:
        raise Http404(f"Landing page '{slug}' not found.")

    testimonials = get_testimonials_for_landing_page(page)

    return render(request, page.template_name, {
        "lp": page,
        "product": page.product,
        "pain_points": page.pain_points.all(),
        "benefits": page.benefits.all(),
        "testimonials": testimonials,
        "pricing_tiers": page.product.pricing_tiers.order_by("sort_order"),
        "product_faqs": page.product.faqs.order_by("sort_order")[:6],
        "product_features": page.product.features.order_by("sort_order"),
        "screenshots": page.product.screenshots.order_by("sort_order")[:4] if hasattr(page.product, "screenshots") else [],
        "cms_screenshots": CMS_SCREENSHOTS,
    })
