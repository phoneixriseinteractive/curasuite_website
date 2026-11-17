"""
CuraSuite — Structured data (JSON-LD) builders.

Every public page ships exactly one ``<script type="application/ld+json">``
containing a single ``@graph``: the sitewide Organization / LocalBusiness /
WebSite nodes (see ``sitewide_nodes``) plus any page-specific nodes the view
passes in as ``schema_nodes`` (see ``product_nodes`` / ``blog_nodes``). The
graph is rendered by the ``{% schema_graph %}`` tag in ``base/base.html``.

Nodes reference each other by ``@id`` (e.g. a BlogPosting's publisher points at
``#organization``) so search engines can stitch the graph together.
"""

from __future__ import annotations

from django.conf import settings
from django.templatetags.static import static

DEFAULT_SITE_URL = "https://curasuite.app"
LANGUAGE = "en-IN"


# ── URL helpers ──────────────────────────────────────────────────────────────


def get_site_url() -> str:
    """Canonical scheme+host for the public site, without a trailing slash."""
    return getattr(settings, "SITE_URL", DEFAULT_SITE_URL).rstrip("/")


def absolute_url(path: str) -> str:
    """Turn a site-relative path (``/products/curacms/``) into an absolute URL."""
    if path.startswith(("http://", "https://")):
        return path
    if not path.startswith("/"):
        path = "/" + path
    return get_site_url() + path


def _id(path: str, fragment: str) -> str:
    return f"{absolute_url(path)}#{fragment}"


ORGANIZATION_ID = _id("/", "organization")
LOCAL_BUSINESS_ID = _id("/", "localbusiness")
WEBSITE_ID = _id("/", "website")


# ── Sitewide ─────────────────────────────────────────────────────────────────

ORG_EMAIL = "hello@curasuite.app"
ORG_PHONE = "+91 88828 14698"
ORG_ADDRESS = {
    "@type": "PostalAddress",
    "streetAddress": "D-9, Ground Floor, Sector-3",
    "addressLocality": "Noida",
    "addressRegion": "Uttar Pradesh",
    "postalCode": "201301",
    "addressCountry": "IN",
}
ORG_SAME_AS = [
    "https://www.linkedin.com/company/curasuite/",
    "https://www.facebook.com/curasuite",
    "https://www.instagram.com/curasuite_app/",
]
AREA_SERVED = {"@type": "Country", "name": "India"}


def _logo_url() -> str:
    return absolute_url(static("img/curasuite-logo-for-website.png"))


def sitewide_nodes() -> list[dict]:
    """Organization + LocalBusiness + WebSite — included on every page."""
    site_root = absolute_url("/")
    logo = _logo_url()
    return [
        {
            "@type": "Organization",
            "@id": ORGANIZATION_ID,
            "name": "CuraSuite",
            "legalName": "PhoenixRise Interactive Pvt. Ltd.",
            "url": site_root,
            "logo": {"@type": "ImageObject", "url": logo},
            "email": ORG_EMAIL,
            "telephone": ORG_PHONE,
            "description": (
                "CuraSuite is a healthcare technology platform providing digital solutions "
                "for doctors, clinics, and pathology laboratories in India."
            ),
            "address": ORG_ADDRESS,
            "areaServed": AREA_SERVED,
            "contactPoint": {
                "@type": "ContactPoint",
                "telephone": ORG_PHONE,
                "email": ORG_EMAIL,
                "contactType": "customer support",
                "areaServed": "IN",
                "availableLanguage": ["English", "Hindi"],
            },
            "sameAs": ORG_SAME_AS,
            "knowsAbout": [
                "Healthcare Management Platform",
                "Clinic Management Software",
                "Healthcare Technology",
                "Doctor Website Development",
                "Pathology Lab Management Software",
                "Healthcare Automation",
                "Digital Healthcare Solutions",
            ],
        },
        {
            "@type": "LocalBusiness",
            "@id": LOCAL_BUSINESS_ID,
            "name": "CuraSuite",
            "url": site_root,
            "image": logo,
            "telephone": ORG_PHONE,
            "email": ORG_EMAIL,
            "description": (
                "Healthcare technology solutions for doctors, clinics, and pathology laboratories."
            ),
            "parentOrganization": {"@id": ORGANIZATION_ID},
            "address": ORG_ADDRESS,
            "areaServed": AREA_SERVED,
        },
        {
            "@type": "WebSite",
            "@id": WEBSITE_ID,
            "name": "CuraSuite",
            "url": site_root,
            "publisher": {"@id": ORGANIZATION_ID},
            "inLanguage": LANGUAGE,
        },
    ]


def breadcrumb_node(path: str, crumbs: list[tuple[str, str]]) -> dict:
    """BreadcrumbList for ``path``; ``crumbs`` is ``[(name, path), ...]`` root-first."""
    return {
        "@type": "BreadcrumbList",
        "@id": _id(path, "breadcrumb"),
        "itemListElement": [
            {"@type": "ListItem", "position": i, "name": name, "item": absolute_url(crumb_path)}
            for i, (name, crumb_path) in enumerate(crumbs, start=1)
        ],
    }


# ── Products ─────────────────────────────────────────────────────────────────

# Hand-written copy for products whose schema should differ from what can be
# derived from the DB (task: "Product schema — CuraCMS product page").
PRODUCT_SCHEMA_OVERRIDES = {
    "curacms": {
        "software_description": (
            "CuraCMS is a healthcare-focused website management platform for doctors and "
            "clinics, offering appointment booking, patient CRM, blogging, SEO tools, "
            "analytics, AI chatbot, and WhatsApp integration."
        ),
        "page_name": "CuraCMS – Professional Website Platform for Doctors",
        "page_description": (
            "Build a professional doctor or clinic website with CuraCMS, featuring "
            "appointment booking, patient CRM, SEO tools, blogging, and AI chatbot."
        ),
        "feature_list": [
            "Healthcare Website CMS",
            "Drag-and-Drop Page Builder",
            "Online Appointment Booking",
            "Patient CRM",
            "Healthcare Blog Engine",
            "SEO Tools and Schema Markup",
            "Analytics Dashboard",
            "Gemini-Powered AI Chatbot",
            "WhatsApp Integration",
            "Landing Page Builder",
        ],
    },
}

_CYCLE_LABELS = {
    "monthly": "Monthly",
    "quarterly": "Quarterly",
    "yearly": "Annual",
    "one_time": "One-time",
}


def _offer_node(product, tier, url: str) -> dict | None:
    """Offer for a priced tier; 'Contact Sales' tiers have no price and are skipped."""
    if not tier.price:
        return None
    cycle = _CYCLE_LABELS.get(tier.billing_cycle)
    description = f"{tier.tier_name} {cycle.lower()} subscription" if cycle else tier.tier_name
    if tier.plus_gst:
        description += " (excl. GST)"
    offer = {
        "@type": "Offer",
        "name": f"{product.name} {tier.tier_name}",
        "price": f"{tier.price:.0f}",
        "priceCurrency": "INR",
        "description": description,
        "url": url,
        "availability": "https://schema.org/InStock",
    }
    if tier.plus_gst:
        offer["priceSpecification"] = {
            "@type": "UnitPriceSpecification",
            "price": f"{tier.price:.0f}",
            "priceCurrency": "INR",
            "valueAddedTaxIncluded": False,
        }
    return offer


def product_nodes(product, *, pricing_tiers, features, seo=None) -> list[dict]:
    """SoftwareApplication + WebPage + BreadcrumbList for a product detail page."""
    path = product.get_absolute_url()
    url = absolute_url(path)
    override = PRODUCT_SCHEMA_OVERRIDES.get(product.slug, {})

    software = {
        "@type": "SoftwareApplication",
        "@id": f"{url}#software",
        "name": product.name,
        "url": url,
        "applicationCategory": "BusinessApplication",
        "operatingSystem": "Web browser",
        "description": override.get("software_description") or product.short_description,
        "provider": {"@id": ORGANIZATION_ID},
    }
    feature_list = override.get("feature_list") or [f.title for f in features]
    if feature_list:
        software["featureList"] = feature_list
    if getattr(product, "hero_image", None):
        software["image"] = absolute_url(product.hero_image.url)
    offers = [o for o in (_offer_node(product, t, url) for t in pricing_tiers) if o]
    if offers:
        software["offers"] = offers

    page_name = override.get("page_name") or (seo.get_title() if seo else "") or (
        f"{product.name} – {product.tagline}" if product.tagline else product.name
    )
    page_description = override.get("page_description") or (
        seo.get_description(product.short_description) if seo else product.short_description
    )
    webpage = {
        "@type": "WebPage",
        "@id": f"{url}#webpage",
        "url": url,
        "name": page_name,
        "description": page_description,
        "isPartOf": {"@id": WEBSITE_ID},
        "mainEntity": {"@id": software["@id"]},
        "breadcrumb": {"@id": f"{url}#breadcrumb"},
        "inLanguage": LANGUAGE,
    }

    breadcrumb = breadcrumb_node(
        path, [("Home", "/"), ("Products", "/products/"), (product.name, path)]
    )
    return [software, webpage, breadcrumb]


# ── Blog posts ───────────────────────────────────────────────────────────────


def blog_nodes(blog, *, seo=None) -> list[dict]:
    """BlogPosting + BreadcrumbList for a blog detail page."""
    path = blog.get_absolute_url()
    url = absolute_url(path)
    tags = [t.name for t in blog.tags.all()]

    keywords = []
    if seo and seo.focus_keyword:
        keywords.append(seo.focus_keyword)
    keywords += [t for t in tags if t not in keywords]

    article = {
        "@type": "BlogPosting",
        "@id": f"{url}#article",
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
        "headline": blog.title[:110],
        "description": seo.get_description(blog.excerpt) if seo else blog.excerpt,
        "url": url,
        "publisher": {"@id": ORGANIZATION_ID},
        "isPartOf": {"@id": WEBSITE_ID},
        "inLanguage": LANGUAGE,
    }
    if blog.published_at:
        article["datePublished"] = blog.published_at.date().isoformat()
    if blog.updated_at:
        article["dateModified"] = blog.updated_at.date().isoformat()
    # byline_name never falls back to the email address (unlike User.full_name).
    author_name = blog.byline_name
    if author_name:
        person = {"@type": "Person", "name": author_name}
        profile = blog.byline
        if profile:
            if profile.designation:
                person["jobTitle"] = profile.designation
            if profile.bio:
                person["description"] = profile.bio
            if profile.photo:
                person["image"] = absolute_url(profile.photo.url)
        article["author"] = person
    else:
        article["author"] = {"@id": ORGANIZATION_ID}
    if blog.featured_image:
        article["image"] = absolute_url(blog.featured_image.url)
    if blog.category:
        article["articleSection"] = blog.category.name
    if keywords:
        article["keywords"] = keywords
    about = ([blog.category.name] if blog.category else []) + tags
    if about:
        article["about"] = [{"@type": "Thing", "name": name} for name in dict.fromkeys(about)]
    if blog.reading_time_minutes:
        article["timeRequired"] = f"PT{blog.reading_time_minutes}M"

    breadcrumb = breadcrumb_node(path, [("Home", "/"), ("Blog", "/blog/"), (blog.title, path)])
    return [article, breadcrumb]
