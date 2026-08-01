"""
CuraSuite — Reposition the Video Appointment Benefit

The bento-benefits layout on curacms.html pairs the 2nd and 3rd benefit
(index 1 and 2) together in a stacked right-hand column next to the 1st
benefit's image card — see the "Right column" comment in curacms.html. The
video-appointment benefit added by add_waiting_room_video_content.py was
appended at the end of each landing page's benefit list, so it needs to be
moved into slot index 2 (3rd position) for that layout to place it correctly.
Safe to re-run — it's a no-op once the benefit is already in position.

Usage:
    python manage.py reposition_video_benefit            # apply
    python manage.py reposition_video_benefit --dry-run   # preview only
"""

from django.core.management.base import BaseCommand

from apps.landing_pages.models import LandingPage

# slug -> title of the benefit that must land at index 2 (3rd position)
VIDEO_BENEFIT_TITLE = {
    "general-physician": "Integrated Video Appointments",
    "dentist": "Video Consultations",
    "physiotherapist": "Remote Video Sessions",
    "ophthalmologist": "Video Consultations",
}

TARGET_INDEX = 2


class Command(BaseCommand):
    help = "Move each CuraCMS landing page's video-appointment benefit to index 2 (safe to re-run)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Show what would change without writing to the database.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        moved = 0

        for slug, title in VIDEO_BENEFIT_TITLE.items():
            lp = LandingPage.all_objects.filter(slug=slug).first()
            if not lp:
                self.stdout.write(self.style.WARNING(f"  Skipping '{slug}' — no landing page with this slug."))
                continue

            ordered = list(lp.benefits.order_by("sort_order"))
            current_index = next((i for i, b in enumerate(ordered) if b.title == title), None)
            if current_index is None:
                self.stdout.write(self.style.WARNING(f"  '{slug}': no benefit titled {title!r} — skipping."))
                continue

            if current_index == TARGET_INDEX:
                self.stdout.write(f"  '{slug}': {title!r} already at index {TARGET_INDEX} — skipping.")
                continue

            target = ordered.pop(current_index)
            ordered.insert(TARGET_INDEX, target)

            changed_here = 0
            for i, b in enumerate(ordered):
                if b.sort_order != i:
                    changed_here += 1
                    if not dry_run:
                        b.sort_order = i
                        b.save(update_fields=["sort_order"])

            moved += 1
            verb = "Would move" if dry_run else "Moved"
            self.stdout.write(self.style.SUCCESS(
                f"  '{slug}': {verb.lower()} {title!r} to index {TARGET_INDEX} ({changed_here} row(s) resequenced)."
            ))

        summary = f"Done. {moved} landing page(s) {'would be ' if dry_run else ''}updated."
        self.stdout.write(self.style.SUCCESS(summary))
