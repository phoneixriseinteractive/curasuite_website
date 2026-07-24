"""
CuraSuite — Update Product Demo URLs

Idempotent content update for Product.demo_url on products that already exist
(seed_products skips entirely once a product with that key exists, so it can't
push this to an already-seeded database — e.g. production).

Usage:
    python manage.py update_product_demo_urls            # apply
    python manage.py update_product_demo_urls --dry-run   # preview only
"""

from django.core.management.base import BaseCommand

from apps.products.models import Product

# product key -> demo URL
DEMO_URLS = {
    "curacms": "https://cms.curasuite.app",
}


class Command(BaseCommand):
    help = "Update Product.demo_url on existing products (safe to re-run)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Show what would change without writing to the database.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        updated = 0

        for key, url in DEMO_URLS.items():
            product = Product.all_objects.filter(key=key).first()
            if not product:
                self.stdout.write(self.style.WARNING(f"  Skipping '{key}' — no product with this key."))
                continue
            if product.demo_url == url:
                self.stdout.write(f"  '{key}' already set — no change.")
                continue
            if not dry_run:
                product.demo_url = url
                product.save(update_fields=["demo_url"])
            verb = "Would set" if dry_run else "Set"
            self.stdout.write(self.style.SUCCESS(f"  {verb} demo_url for '{key}' -> {url}"))
            updated += 1

        self.stdout.write(self.style.SUCCESS(
            f"Done. {updated} product(s) {'would be ' if dry_run else ''}updated."
        ))
