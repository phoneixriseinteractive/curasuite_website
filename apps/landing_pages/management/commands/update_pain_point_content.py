"""
CuraSuite — Update Pain Point Content

Idempotent content update for LandingPainPoint.consequence_text / solution_text
on landing pages that already exist (seed_landing_pages skips entirely once any
LandingPage exists, so it can't push copy updates to an already-seeded database
— e.g. production). Matches existing rows by landing_page slug + exact pain
point text and fills in consequence_text/solution_text; does not create, delete,
or reorder pain points.

Usage:
    python manage.py update_pain_point_content            # apply
    python manage.py update_pain_point_content --dry-run   # preview only
"""

from django.core.management.base import BaseCommand

from apps.landing_pages.models import LandingPage, LandingPainPoint

# slug -> [(pain point text, consequence, solution), ...]
PAIN_POINT_CONTENT = {
    "general-physician": [
        ("Losing patients to clinics with a stronger online presence?",
         "Your expertise stays hidden while competitors capture the local market.",
         "A modern, professional website gives your practice the same digital presence as bigger clinics — without the agency price tag."),
        ("Spending hours on the phone booking appointments manually?",
         "Manual coordination means double-bookings, missed calls, and a reception desk that never gets a break.",
         "Online booking lets patients schedule themselves 24/7, freeing up your reception desk."),
        ("No way for patients to find you when they search on Google?",
         "If you aren't on the first page, you're invisible to patients actively looking for care.",
         "Every page ships with built-in SEO, so you show up when patients search for a doctor nearby."),
        ("Website looks outdated or doesn't work on mobile?",
         "Most patients browse on their phones — a clunky site quietly sends them elsewhere.",
         "Every CuraCMS site is fully responsive and loads in under a second, on any device."),
    ],
    "dentist": [
        ("Potential patients choosing a competitor with a better website?",
         "First impressions happen online now — a dated site loses patients before they ever call.",
         "A professional, mobile-ready website built specifically for dental practices — so you make the first impression, not your competitor."),
        ("Struggling to showcase before/after smile transformations online?",
         "Your best work stays buried in your camera roll instead of winning new patients.",
         "Dedicated treatment and gallery pages built into the CMS make it easy to showcase your best work — no coding needed."),
        ("No easy way for patients to book a consultation online?",
         "Every missed call after hours is a consultation booked with someone else.",
         "24/7 online appointment booking — patients pick a slot themselves, no back-and-forth calls."),
        ("Not appearing when people search 'dentist near me'?",
         "Nearby patients are searching right now — and finding your competitors instead.",
         "Built-in SEO tools and schema markup on every page help you rank for local searches that actually convert."),
    ],
    "physiotherapist": [
        ("Patients unsure what conditions you treat before calling?",
         "Uncertainty makes people hesitate to call at all — and hesitation costs you patients.",
         "Treatment listing pages spell out every condition and service you treat — before they even pick up the phone."),
        ("Manually managing session bookings on WhatsApp or calls?",
         "Chasing confirmations across chats and calls eats into time you could spend treating patients.",
         "Online booking handles scheduling automatically, while WhatsApp integration stays there for quick questions."),
        ("No content to explain your specialisations online?",
         "Patients can't tell what makes you different, so they default to whoever ranks first on Google.",
         "Publish blog articles and service pages that explain your specialisations and build patient trust."),
        ("Losing potential patients who search online and find nothing?",
         "No online presence reads as no practice at all to patients researching their options.",
         "A findable, SEO-ready website means patients searching for physiotherapy nearby actually find you."),
    ],
    "ophthalmologist": [
        ("Patients confused about which eye procedures you offer?",
         "Confusion about your services sends patients looking for clearer answers elsewhere.",
         "Dedicated treatment listing pages clearly explain every procedure you offer, in patient-friendly language."),
        ("No online way to book cataract or LASIK consultations?",
         "High-value consultations get lost to clinics that make booking effortless.",
         "Patients book cataract, LASIK, or any consultation online, 24/7 — no phone tag required."),
        ("Website doesn't reflect the precision and trust your practice requires?",
         "A dated or generic site undersells the expertise patients are trusting you with their eyesight for.",
         "A polished, professional design built for specialty clinics — reflecting the same precision you bring to your practice."),
        ("Missing out on patients who research online before choosing a specialist?",
         "Most patients compare specialists online before ever calling — and you're not in the running.",
         "SEO-optimised pages and doctor profiles help you get found by patients actively researching specialists."),
    ],
    "pathology-digital-platform": [
        ("Phone lines constantly busy with report status calls?",
         "Every busy signal is a patient who gives up and calls a competitor lab instead.",
         "Patients check report status themselves through secure online access — no more hold music."),
        ("Manually coordinating home sample collection over calls?",
         "Phone-based scheduling doesn't scale, and double-bookings slip through the cracks.",
         "Home collection requests are booked online with a preferred time slot — no phone coordination needed."),
        ("Patients frustrated waiting to collect printed reports?",
         "A frustrating pickup experience is the last impression patients remember, not the accurate results.",
         "OTP-verified digital report downloads mean patients get results the moment they're ready."),
        ("No digital presence while competitor labs go online?",
         "Labs that stay offline lose patients to the ones that make testing feel effortless.",
         "A modern, professional digital platform puts your lab on equal footing with labs that have already gone digital."),
    ],
}


class Command(BaseCommand):
    help = "Update consequence_text/solution_text on existing landing page pain points (safe to re-run)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Show what would change without writing to the database.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        total_updated = 0
        total_missing_page = 0
        total_missing_point = 0

        for slug, rows in PAIN_POINT_CONTENT.items():
            lp = LandingPage.all_objects.filter(slug=slug).first()
            if not lp:
                self.stdout.write(self.style.WARNING(f"  Skipping '{slug}' — no landing page with this slug."))
                total_missing_page += 1
                continue

            lookup = {text: (consequence, solution) for text, consequence, solution in rows}
            existing = {pp.text: pp for pp in lp.pain_points.all()}

            updated_here = 0
            for text, (consequence, solution) in lookup.items():
                pp = existing.get(text)
                if not pp:
                    self.stdout.write(self.style.WARNING(f"    No matching pain point on '{slug}': {text!r}"))
                    total_missing_point += 1
                    continue
                if pp.consequence_text == consequence and pp.solution_text == solution:
                    continue
                if not dry_run:
                    pp.consequence_text = consequence
                    pp.solution_text = solution
                    pp.save(update_fields=["consequence_text", "solution_text"])
                updated_here += 1

            total_updated += updated_here
            verb = "Would update" if dry_run else "Updated"
            self.stdout.write(self.style.SUCCESS(f"  {verb} {updated_here} pain point(s) on '{slug}'"))

        summary = f"Done. {total_updated} pain point(s) {'would be ' if dry_run else ''}updated."
        if total_missing_page or total_missing_point:
            summary += f" ({total_missing_page} page(s) not found, {total_missing_point} text mismatch(es) skipped.)"
        self.stdout.write(self.style.SUCCESS(summary))
