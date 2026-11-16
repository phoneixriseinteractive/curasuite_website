"""
Production content updates that were first made by hand in development:

- CuraOS pricing: 3 Months ₹4,500 + GST, 1 Year ₹12,000 + GST (featured), Enterprise (contact).
  Any other CuraOS tiers (the old "Clinic Starter" / "Clinic Pro") are removed.
- CuraLabs theme colour green → red (only if it is still the old green, so a later
  manual change in /manage/ is not overwritten).
- Pricing-page FAQ "What does CuraOS cost?".

Idempotent, so databases that already have these values are left unchanged. Reversing
only removes the added FAQ and restores the CuraLabs colour; the old CuraOS tiers are
not recreated.
"""

from django.db import migrations

CURAOS_KEY = "curasuite"  # internal key of the CuraOS product (unchanged by the rename)
OLD_GREEN, RED = "#16A34A", "#DC2626"
FAQ_QUESTION = "What does CuraOS cost?"

CORE_FEATURES = "\n".join([
    "Appointment & Queue Management",
    "Patient Records (EHR)",
    "OPD Billing & Invoicing",
    "Doctor & Reception Dashboards",
    "Prescription Management",
    "Inventory Management",
    "Patient Notifications",
    "Reports & Analytics",
])

CURAOS_TIERS = [
    {
        "tier_name": "3 Months", "price": 4500, "original_price": None, "billing_cycle": "quarterly",
        "plus_gst": True, "is_featured": False, "sort_order": 1,
        "description": "Get your clinic running digitally with a short-term plan.",
        "features_included": CORE_FEATURES, "cta_text": "Get Started", "cta_url": "/contact/",
    },
    {
        "tier_name": "1 Year", "price": 12000, "original_price": None, "billing_cycle": "yearly",
        "plus_gst": True, "is_featured": True, "sort_order": 2,
        "description": "Best value — save ₹6,000 compared with paying every 3 months.",
        "features_included": CORE_FEATURES, "cta_text": "Get Started", "cta_url": "/contact/",
    },
    {
        "tier_name": "Enterprise", "price": None, "original_price": None, "billing_cycle": "custom",
        "plus_gst": False, "is_featured": False, "sort_order": 3,
        "description": "For hospitals and multi-branch clinic groups with custom requirements.",
        "features_included": "\n".join([
            "Everything in the 1 Year plan",
            "Multiple branches / locations",
            "Custom integrations",
            "Dedicated onboarding & priority support",
        ]),
        "cta_text": "Contact Sales", "cta_url": "/contact/",
    },
]


def forwards(apps, schema_editor):
    Product = apps.get_model("products", "Product")
    ProductPricing = apps.get_model("products", "ProductPricing")
    GlobalFAQ = apps.get_model("settings_app", "GlobalFAQ")

    curaos = Product._base_manager.filter(key=CURAOS_KEY).first()
    if curaos:
        keep = []
        for tier in CURAOS_TIERS:
            obj, _ = ProductPricing._base_manager.update_or_create(
                product=curaos, tier_name=tier["tier_name"],
                defaults={k: v for k, v in tier.items() if k != "tier_name"},
            )
            keep.append(obj.pk)
        ProductPricing._base_manager.filter(product=curaos).exclude(pk__in=keep).delete()

    Product._base_manager.filter(key="curalabs", color__iexact=OLD_GREEN).update(color=RED)

    GlobalFAQ._base_manager.get_or_create(
        category="pricing", question=FAQ_QUESTION,
        defaults={
            "answer": (
                "CuraOS is ₹4,500 + GST for 3 months, or ₹12,000 + GST per year — saving ₹6,000 "
                "compared with paying every 3 months. Enterprise pricing is available for hospitals "
                "and multi-branch clinic groups."
            ),
            "sort_order": 4,
            "is_active": True,
        },
    )


def backwards(apps, schema_editor):
    Product = apps.get_model("products", "Product")
    GlobalFAQ = apps.get_model("settings_app", "GlobalFAQ")
    GlobalFAQ._base_manager.filter(category="pricing", question=FAQ_QUESTION).delete()
    Product._base_manager.filter(key="curalabs", color__iexact=RED).update(color=OLD_GREEN)


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0005_rename_curasuite_cms_to_curaos"),
        ("settings_app", "0002_testimonial_specialty"),
    ]

    operations = [migrations.RunPython(forwards, backwards)]
