"""CuraSuite — Pages Views"""
from django.http import Http404
from django.shortcuts import render
from apps.seo.selectors import get_seo_for_object
from .selectors import get_home_page, get_page_by_slug


def home(request):
    from apps.products.selectors import get_products_with_pricing
    from apps.settings_app.models import Testimonial
    from apps.blogs.selectors import get_published_blogs

    page = get_home_page()

    steps = [
        {"title": "Book a Demo",             "description": "Schedule a free consultation with our team to understand your requirements."},
        {"title": "Configure Your Product",  "description": "We set up and customise the platform for your specialty and workflow."},
        {"title": "Go Live",                 "description": "Your website or system goes live within 7–14 days — fully ready for patients."},
        {"title": "Ongoing Support",         "description": "Our team supports you every step of the way with training and updates."},
    ]

    trust_badges = [
        "Healthcare-focused",
        "Secure infrastructure",
        "Fast implementation",
        "Responsive support",
        "Scalable architecture",
    ]

    try:
        products     = get_products_with_pricing(["curaos", "curacms", "curalabs"])
        testimonials = Testimonial.objects.filter(status="approved", is_featured=True).order_by("sort_order")[:6]
        recent_blogs = get_published_blogs(limit=3)
    except Exception:
        products     = {}
        testimonials = []
        recent_blogs = []

    return render(request, "pages/home.html", {
        "page":         page,
        "products":     products,
        "steps":        steps,
        "trust_badges": trust_badges,
        "testimonials": testimonials,
        "recent_blogs": recent_blogs,
    })


def page_detail(request, slug: str):
    page = get_page_by_slug(slug)
    if not page or not page.is_published:
        raise Http404(f"Page '{slug}' not found.")
    seo = get_seo_for_object(page)

    context = {
        "page":        page,
        "breadcrumbs": page.breadcrumbs,
        "seo":         seo,
    }

    # Solutions pages are sales pages per audience: doctors/clinics (CuraOS + CuraCMS)
    # or pathology labs (CuraLabs). Each renders its own template on top of solutions.html.
    if page.template == "solutions" or slug.startswith("solutions/"):
        if "labs" in slug:
            audience, product_slugs, testimonial_products = "labs", ["curalabs"], ["CuraLabs"]
        else:
            audience, product_slugs, testimonial_products = "doctors", ["curaos", "curacms"], ["CuraOS", "CuraCMS"]
        try:
            from apps.products.selectors import get_products_with_pricing
            from apps.settings_app.models import Testimonial
            context["solution_products"] = get_products_with_pricing(product_slugs)
            context["testimonials"] = Testimonial.objects.filter(
                status="approved", is_featured=True, product__in=testimonial_products + [""]
            ).order_by("sort_order")[:4]
        except Exception:
            pass
        return render(request, f"pages/solutions_{audience}.html", context)

    # About page gets extra context
    if page.template == "about" or slug == "about":
        try:
            from apps.products.selectors import get_products_with_pricing
            from apps.settings_app.models import Testimonial
            context["about_products"] = get_products_with_pricing(["curaos", "curacms", "curalabs"])
            context["testimonials"] = Testimonial.objects.filter(
                status="approved", is_featured=True
            ).order_by("sort_order")[:6]
        except Exception:
            pass

    # Pricing page gets extra context
    if page.page_type == "pricing" or slug == "pricing":
        try:
            from apps.products.selectors import get_products_with_pricing
            from apps.settings_app.models import GlobalFAQ
            # Grouped the same way as the Solutions menu.
            products = get_products_with_pricing(["curaos", "curacms", "curalabs"])
            context["product_groups"] = [
                {"id": "doctors", "title": "For Doctors & Clinics",
                 "products": [products[s] for s in ("curaos", "curacms") if s in products]},
                {"id": "labs", "title": "For Pathology Labs",
                 "products": [products[s] for s in ("curalabs",) if s in products]},
            ]
            context["pricing_faqs"] = GlobalFAQ.objects.filter(
                category="pricing", is_active=True
            ).order_by("sort_order")
            context["included_items"] = [
                {"icon": "rocket", "title": "Free Setup",          "description": "Our team sets up everything within 48 hours of signup."},
                {"icon": "graduation-cap", "title": "Training Included",   "description": "Live training session for you and your staff."},
                {"icon": "lock", "title": "SSL Certificate",     "description": "HTTPS encryption on all plans at no extra cost."},
                {"icon": "database", "title": "Daily Backups",       "description": "Your data is automatically backed up every day."},
                {"icon": "mail", "title": "Email Support",       "description": "Responsive email support during business hours."},
                {"icon": "smartphone", "title": "Mobile-Ready",        "description": "Works perfectly on all devices from day one."},
                {"icon": "refresh-cw", "title": "Free Updates",        "description": "All product updates and new features at no charge."},
                {"icon": "bar-chart", "title": "Analytics Ready",     "description": "GA4, GTM, Meta Pixel integrations pre-configured."},
            ]
        except Exception:
            pass

    return render(request, f"pages/{page.template}.html", context)
