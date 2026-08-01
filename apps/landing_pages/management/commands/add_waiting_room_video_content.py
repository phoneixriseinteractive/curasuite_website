"""
CuraSuite — Add Waiting Room Display + Video Appointment Content

Idempotent content addition for the new CuraCMS waiting room display and Google
Meet video appointment features. seed_landing_pages skips entirely once any
LandingPage exists (see that command), and update_pain_point_content.py only
edits fields on *existing* pain points — neither can add brand-new rows to an
already-seeded database (e.g. production). This adds one new LandingPainPoint
and one new LandingBenefit to each of the 4 CuraCMS specialty landing pages,
matched/skipped by exact text so it's safe to re-run.

Usage:
    python manage.py add_waiting_room_video_content            # apply
    python manage.py add_waiting_room_video_content --dry-run   # preview only
"""

from django.core.management.base import BaseCommand

from apps.landing_pages.models import LandingBenefit, LandingPage, LandingPainPoint

# slug -> (pain point text, consequence, solution)
NEW_PAIN_POINT = {
    "general-physician": (
        "Patients waiting in your lobby with no clue when they'll be called?",
        "An uncertain, silent wait makes your clinic feel disorganised before the consultation even starts.",
        "A live waiting room display shows the patient queue, calls each patient by name and room, introduces your doctors, and plays educational health videos.",
    ),
    "dentist": (
        "Patients sitting in your waiting room with no idea when they'll be called in?",
        "An anxious, silent wait is often the worst part of a dental visit — before the appointment has even started.",
        "A live waiting room display shows the queue and estimated wait, introduces your dentists, and plays educational procedure videos to ease nerves.",
    ),
    "physiotherapist": (
        "Patients waiting for their session with no idea how long it'll be?",
        "An uncertain wait makes an already uncomfortable visit feel worse, and patients start wondering if they've been forgotten.",
        "A live waiting room display shows the session queue, calls patients by name and room, and plays educational recovery videos while they wait.",
    ),
    "ophthalmologist": (
        "Patients waiting for their consultation with no idea when they'll be seen?",
        "A long, uncertain wait undercuts the sense of precision and care your practice is built on.",
        "A live waiting room display shows the patient queue and doctor details, and plays educational videos about eye procedures while patients wait.",
    ),
}

# slug -> (icon, title, description)
NEW_BENEFIT = {
    "general-physician": (
        "🎥", "Integrated Video Appointments",
        "Patients can book and join a Google Meet video consultation with your doctor — no separate app to install.",
    ),
    "dentist": (
        "🎥", "Video Consultations",
        "Offer consultations and follow-ups over Google Meet, booked right from your website — no extra software needed.",
    ),
    "physiotherapist": (
        "🎥", "Remote Video Sessions",
        "Patients can book and join physiotherapy consultations over Google Meet, directly through your website.",
    ),
    "ophthalmologist": (
        "🎥", "Video Consultations",
        "Patients can book a Google Meet video consultation for follow-ups or preliminary eye checks — no extra software required.",
    ),
}


class Command(BaseCommand):
    help = "Add the waiting-room-display pain point and video-appointment benefit to the 4 CuraCMS landing pages (safe to re-run)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Show what would change without writing to the database.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        pain_points_added = 0
        benefits_added = 0

        slugs = set(NEW_PAIN_POINT) | set(NEW_BENEFIT)
        for slug in sorted(slugs):
            lp = LandingPage.all_objects.filter(slug=slug).first()
            if not lp:
                self.stdout.write(self.style.WARNING(f"  Skipping '{slug}' — no landing page with this slug."))
                continue

            if slug in NEW_PAIN_POINT:
                text, consequence, solution = NEW_PAIN_POINT[slug]
                if lp.pain_points.filter(text=text).exists():
                    self.stdout.write(f"  '{slug}': pain point already present — skipping.")
                else:
                    next_order = (lp.pain_points.order_by("-sort_order").values_list("sort_order", flat=True).first() or 0) + 1
                    if not dry_run:
                        LandingPainPoint.objects.create(
                            landing_page=lp, text=text, consequence_text=consequence,
                            solution_text=solution, sort_order=next_order,
                        )
                    pain_points_added += 1
                    verb = "Would add" if dry_run else "Added"
                    self.stdout.write(self.style.SUCCESS(f"  '{slug}': {verb.lower()} pain point — {text!r}"))

            if slug in NEW_BENEFIT:
                icon, title, description = NEW_BENEFIT[slug]
                if lp.benefits.filter(title=title).exists():
                    self.stdout.write(f"  '{slug}': benefit already present — skipping.")
                else:
                    next_order = (lp.benefits.order_by("-sort_order").values_list("sort_order", flat=True).first() or 0) + 1
                    if not dry_run:
                        LandingBenefit.objects.create(
                            landing_page=lp, icon=icon, title=title,
                            description=description, sort_order=next_order,
                        )
                    benefits_added += 1
                    verb = "Would add" if dry_run else "Added"
                    self.stdout.write(self.style.SUCCESS(f"  '{slug}': {verb.lower()} benefit — {title!r}"))

        summary = f"Done. {pain_points_added} pain point(s) and {benefits_added} benefit(s) {'would be ' if dry_run else ''}added."
        self.stdout.write(self.style.SUCCESS(summary))
