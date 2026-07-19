"""CuraSuite — Landing Pages Public Views"""
from django.http import Http404
from django.shortcuts import render
from .selectors import get_landing_page_by_slug, get_testimonials_for_landing_page

# Real CuraCMS product screenshots for the "See CuraCMS in Action" slider on
# curacms.html — (filename relative to static/img/CuraCms/, caption).
CMS_SCREENSHOTS = [
    ("Front_Pages/index-hero-section.png",   "Patient-Facing Website Homepage"),
    ("Front_Pages/profile-hero-section.png", "Doctor Profile — Public Page"),
    ("Front_Pages/dr-profile.png",           "Detailed Doctor Biography & Credentials"),
    ("Front_Pages/treatments.png",           "Treatments & Services Listing"),
    ("Front_Pages/videos.png",               "Patient Education Video Library"),
    ("Front_Pages/contact-us.png",           "Contact & Enquiry Page"),
    ("Admin_Panel/dashboard.png",            "Admin Dashboard & Analytics"),
    ("Admin_Panel/pages-module.png",         "CMS Page Manager"),
    ("Admin_Panel/treatment-module.png",     "Manage Treatments & Services"),
    ("Admin_Panel/video-module.png",         "Video Library Management"),
    ("Admin_Panel/doctor-profile.png",       "Manage Doctor Profiles"),
    ("Admin_Panel/appointment-module.png",   "Appointments & Booking Calendar"),
    ("Admin_Panel/user-module.png",          "Role-Based User Access"),
    ("Admin_Panel/seo-settings.png",         "Built-in SEO Controls"),
    ("Admin_Panel/website-settings.png",     "Site Branding & Settings"),
    ("Admin_Panel/Ai-chat-assistant-1.png",  "AI Chatbot Configuration"),
    ("Admin_Panel/social-chat-assistant.png","WhatsApp & Messenger Integration"),
    ("Admin_Panel/login-panel.png",          "Secure Admin Login"),
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
