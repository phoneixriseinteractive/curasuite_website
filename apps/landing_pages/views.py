"""CuraSuite — Landing Pages Public Views"""
from django.http import Http404
from django.shortcuts import render
from .selectors import get_landing_page_by_slug, get_testimonials_for_landing_page

# Real CuraCMS product screenshots for the "A Glimpse into CuraCMS" gallery on
# curacms.html — (filename relative to static/img/CuraCms/, caption).
GALLERY_SHOTS = [
    ("Admin_Panel/doctor-profile.webp",        "Doctor Profile Management"),
    ("Front_Pages/videos.webp",                "Patient Education Videos"),
    ("Admin_Panel/treatment-module.webp",      "Treatment & Procedure Listings"),
    ("Admin_Panel/pages-module.webp",          "Marketing CMS & Pages"),
    ("Admin_Panel/login-panel.webp",           "Secure Admin Access"),
    ("Admin_Panel/social-chat-assistant.webp", "WhatsApp & Social Integration"),
    ("Admin_Panel/Ai-chat-assistant-1.webp",   "AI Chatbot Configuration"),
    ("Admin_Panel/website-settings.webp",      "Clinic Branding & Settings"),
    ("Admin_Panel/seo-settings.webp",          "Built-in SEO Controls"),
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
