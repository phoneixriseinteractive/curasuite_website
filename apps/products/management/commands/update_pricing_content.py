"""
CuraSuite — Update Pricing Content

Idempotent content update for ProductPricing.original_price / features_included
on tiers that already exist (seed_products skips entirely once a product with
that key exists, so it can't push this to an already-seeded database — e.g.
production).

Usage:
    python manage.py update_pricing_content            # apply
    python manage.py update_pricing_content --dry-run   # preview only
"""

from decimal import Decimal

from django.core.management.base import BaseCommand

from apps.products.models import Product, ProductPricing

# product key -> {tier_name: (original_price or None, features_included)}
PRICING_CONTENT = {
    "curacms": {
        "Starter": (
            Decimal("14999"),
            "Marketing CMS\nDoctor Profiles\nSocial Integration\nPatient Education Videos\n"
            "Role-Based Access\nBuilt-in SEO\nBlog & Content\nSite Settings",
        ),
        "Professional": (
            Decimal("29999"),
            "Everything in the Starter plan, plus\nTreatment Listings\nPatient CRM\n"
            "Online Appointment Booking\nAI Chat Assistant",
        ),
    },
}


class Command(BaseCommand):
    help = "Update original_price/features_included on existing pricing tiers (safe to re-run)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Show what would change without writing to the database.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        total_updated = 0

        for product_key, tiers in PRICING_CONTENT.items():
            product = Product.all_objects.filter(key=product_key).first()
            if not product:
                self.stdout.write(self.style.WARNING(f"  Skipping '{product_key}' — no product with this key."))
                continue

            existing = {t.tier_name: t for t in ProductPricing.objects.filter(product=product)}

            for tier_name, (original_price, features_included) in tiers.items():
                tier = existing.get(tier_name)
                if not tier:
                    self.stdout.write(self.style.WARNING(
                        f"    No matching tier on '{product_key}': {tier_name!r}"
                    ))
                    continue
                if tier.original_price == original_price and tier.features_included == features_included:
                    self.stdout.write(f"  '{product_key}/{tier_name}' already up to date — no change.")
                    continue
                if not dry_run:
                    tier.original_price = original_price
                    tier.features_included = features_included
                    tier.save(update_fields=["original_price", "features_included"])
                verb = "Would update" if dry_run else "Updated"
                self.stdout.write(self.style.SUCCESS(f"  {verb} '{product_key}/{tier_name}'"))
                total_updated += 1

        self.stdout.write(self.style.SUCCESS(
            f"Done. {total_updated} tier(s) {'would be ' if dry_run else ''}updated."
        ))
