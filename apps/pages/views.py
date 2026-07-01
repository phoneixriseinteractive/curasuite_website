"""CuraSuite — Pages Views"""
from django.http import Http404
from django.shortcuts import render
from apps.seo.selectors import get_seo_for_object
from .selectors import get_home_page, get_page_by_slug


def home(request):
    from apps.products.selectors import get_products_for_homepage
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
        products     = get_products_for_homepage()
        testimonials = Testimonial.objects.filter(status="approved", is_featured=True).order_by("sort_order")[:6]
        recent_blogs = get_published_blogs(limit=3)
    except Exception:
        products     = []
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

    # Solutions pages get extra context
    if page.template == "solutions" or slug.startswith("solutions/"):
        try:
            from apps.settings_app.models import Testimonial
            product_name = ""
            if "doctors" in slug: product_name = "CuraCMS"
            elif "labs" in slug:  product_name = "CuraLabs"
            elif "clinics" in slug: product_name = "CuraSuite"
            context["testimonials"] = Testimonial.objects.filter(
                status="approved", is_featured=True,
                **({} if not product_name else {"product__in": [product_name, ""]})
            ).order_by("sort_order")[:4]
            context["demo_form_action"] = "/contact/demo/"
        except Exception:
            pass

    # About page gets extra context
    if page.template == "about" or slug == "about":
        try:
            from apps.settings_app.models import Testimonial
            context["testimonials"] = Testimonial.objects.filter(
                status="approved", is_featured=True
            ).order_by("sort_order")[:6]
        except Exception:
            pass

    # Pricing page gets extra context
    if page.page_type == "pricing" or slug == "pricing":
        try:
            from apps.products.selectors import get_products_for_homepage
            from apps.settings_app.models import GlobalFAQ
            context["products"] = get_products_for_homepage()
            context["pricing_faqs"] = GlobalFAQ.objects.filter(
                category="pricing", is_active=True
            ).order_by("sort_order")
            context["included_items"] = [
                {"icon": "🚀", "title": "Free Setup",          "description": "Our team sets up everything within 48 hours of signup."},
                {"icon": "🎓", "title": "Training Included",   "description": "Live training session for you and your staff."},
                {"icon": "🔒", "title": "SSL Certificate",     "description": "HTTPS encryption on all plans at no extra cost."},
                {"icon": "💾", "title": "Daily Backups",       "description": "Your data is automatically backed up every day."},
                {"icon": "📧", "title": "Email Support",       "description": "Responsive email support during business hours."},
                {"icon": "📱", "title": "Mobile-Ready",        "description": "Works perfectly on all devices from day one."},
                {"icon": "🔄", "title": "Free Updates",        "description": "All product updates and new features at no charge."},
                {"icon": "📊", "title": "Analytics Ready",     "description": "GA4, GTM, Meta Pixel integrations pre-configured."},
            ]
        except Exception:
            pass

    return render(request, f"pages/{page.template}.html", context)
