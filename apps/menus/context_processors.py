"""CuraSuite — Menus Context Processor."""


def navigation(request):
    try:
        from apps.settings_app.models import SocialLinks
        social_links = SocialLinks.load()
    except Exception:
        social_links = None

    try:
        from apps.products.models import Product
        all_products = list(Product.objects.order_by("sort_order"))
    except Exception:
        all_products = []

    return {
        "SOCIAL_LINKS": social_links,
        "ALL_PRODUCTS": all_products,
        "PRIMARY_NAV": [
            {
                "label": "Products",
                "url": "/products/",
                "has_dropdown": True,
                "children": [
                    {"label": "CuraCMS",   "url": "/products/curacms/",   "description": "Website CMS for doctors & clinics"},
                    {"label": "CuraLabs",  "url": "/products/curalabs/",  "description": "Digital platform for pathology labs"},
                    {"label": "CuraSuite", "url": "/products/curasuite/", "description": "Complete clinic management software"},
                ],
            },
            {
                "label": "Solutions",
                "url": "/solutions/doctors/",
                "has_dropdown": True,
                "children": [
                    {"label": "For Doctors",        "url": "/solutions/doctors/",        "description": "Grow your private practice online"},
                    {"label": "For Clinics",        "url": "/solutions/clinics/",        "description": "Digitise your clinic operations"},
                    {"label": "For Pathology Labs", "url": "/solutions/pathology-labs/", "description": "Modern digital lab experience"},
                ],
            },
            {"label": "Pricing", "url": "/pricing/",  "has_dropdown": False, "children": []},
            {"label": "Company", "url": "/about/",    "has_dropdown": False, "children": []},
            {"label": "Blog",    "url": "/blog/",     "has_dropdown": False, "children": []},
            {"label": "Contact", "url": "/contact/",  "has_dropdown": False, "children": []},
        ],
    }
