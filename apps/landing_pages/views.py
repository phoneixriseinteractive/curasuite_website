"""CuraSuite — Landing Pages Public Views"""
from django.http import Http404
from django.shortcuts import render
from .selectors import get_landing_page_by_slug, get_testimonials_for_landing_page

# Real CuraCMS product screenshots for the "A Glimpse into CuraCMS" gallery on
# curacms.html — (filename relative to static/img/CuraCms/, caption).
GALLERY_SHOTS = [
    ("Admin_Panel/doctor-profile.png",        "Doctor Profile Management"),
    ("Front_Pages/videos.png",                "Patient Education Videos"),
    ("Admin_Panel/treatment-module.png",      "Treatment & Procedure Listings"),
    ("Admin_Panel/pages-module.png",          "Marketing CMS & Pages"),
    ("Admin_Panel/login-panel.png",           "Secure Admin Access"),
    ("Admin_Panel/social-chat-assistant.png", "WhatsApp & Social Integration"),
    ("Admin_Panel/Ai-chat-assistant-1.png",   "AI Chatbot Configuration"),
    ("Admin_Panel/website-settings.png",      "Clinic Branding & Settings"),
    ("Admin_Panel/seo-settings.png",          "Built-in SEO Controls"),
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
        "gallery_shots": GALLERY_SHOTS,
    })
