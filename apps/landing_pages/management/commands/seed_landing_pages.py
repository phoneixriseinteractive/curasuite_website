"""
CuraSuite — Seed the 5 ad landing pages.
Usage: python manage.py seed_landing_pages
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Seed the 5 ad landing pages (4 CuraCMS specialty pages + 1 CuraLabs pathology page)."

    def handle(self, *args, **options):
        from apps.landing_pages.models import LandingPage, LandingPainPoint, LandingBenefit
        from apps.products.models import Product

        if LandingPage.all_objects.exists():
            self.stdout.write(self.style.WARNING("Landing pages already exist — skipping."))
            return

        curacms  = Product.objects.filter(key="curacms").first()
        curalabs = Product.objects.filter(key="curalabs").first()

        if not curacms or not curalabs:
            self.stdout.write(self.style.ERROR("Run seed_products first — CuraCMS/CuraLabs not found."))
            return

        pages_data = [
            {
                "slug": "general-physician",
                "product": curacms,
                "specialty": "general_physician",
                "headline": "Grow Your Clinic Online — Free Website Demo for General Physicians",
                "subheadline": "Professional website, online appointment booking, and AI chatbot — built specifically for general physicians across India.",
                "target_audience_label": "For General Physicians",
                "social_proof_note": "Trusted by 150+ general physicians across India",
                "whatsapp_message_template": "Hi! I saw your ad and I'm interested in CuraCMS for my clinic.",
                "default_utm_campaign": "gp-website-demo",
                "pain_points": [
                    "Losing patients to clinics with a stronger online presence?",
                    "Spending hours on the phone booking appointments manually?",
                    "No way for patients to find you when they search on Google?",
                    "Website looks outdated or doesn't work on mobile?",
                ],
                "benefits": [
                    ("📅", "24/7 Online Booking", "Patients book appointments anytime — no phone calls needed, even outside clinic hours."),
                    ("🤖", "AI Chatbot Support", "Answers patient questions about timings, services, and directions automatically."),
                    ("📈", "Rank Higher on Google", "SEO-optimised pages help new patients find you before your competitors."),
                    ("✍️", "Health Blog Included", "Publish health tips easily to build authority and improve search rankings."),
                    ("📱", "Mobile-First Design", "Looks perfect on every device — most patients search from their phones."),
                    ("⚡", "Live in 7–14 Days", "Our team handles setup, content, and training. You just approve and go live."),
                ],
            },
            {
                "slug": "dentist",
                "product": curacms,
                "specialty": "dentist",
                "headline": "Fill Your Appointment Book — Free Website Demo for Dentists",
                "subheadline": "A professional dental website with online booking and patient reviews — built to bring more patients to your chair.",
                "target_audience_label": "For Dentists",
                "social_proof_note": "Trusted by 120+ dental clinics across India",
                "whatsapp_message_template": "Hi! I saw your ad and I'm interested in CuraCMS for my dental clinic.",
                "default_utm_campaign": "dentist-website-demo",
                "pain_points": [
                    "Potential patients choosing a competitor with a better website?",
                    "Struggling to showcase before/after smile transformations online?",
                    "No easy way for patients to book a consultation online?",
                    "Not appearing when people search 'dentist near me'?",
                ],
                "benefits": [
                    ("🦷", "Showcase Your Work", "Display smile transformations and treatment galleries that build instant trust."),
                    ("📅", "Online Consultation Booking", "Patients pick a slot and book instantly — no back-and-forth calls."),
                    ("⭐", "Patient Reviews Display", "Show your best reviews prominently to convert hesitant visitors."),
                    ("🤖", "AI Chatbot 24/7", "Answers questions about procedures, pricing ranges, and appointment slots."),
                    ("📍", "Local SEO Built In", "Appear in Google Maps and local search when patients search nearby."),
                    ("⚡", "Live in 7–14 Days", "No technical skill needed — our team builds and launches it for you."),
                ],
            },
            {
                "slug": "physiotherapist",
                "product": curacms,
                "specialty": "physiotherapist",
                "headline": "More Patients, Less Admin — Free Website Demo for Physiotherapists",
                "subheadline": "A conversion-focused website that books sessions automatically and showcases your treatment expertise.",
                "target_audience_label": "For Physiotherapists",
                "social_proof_note": "Trusted by 90+ physiotherapy clinics across India",
                "whatsapp_message_template": "Hi! I saw your ad and I'm interested in CuraCMS for my physiotherapy clinic.",
                "default_utm_campaign": "physio-website-demo",
                "pain_points": [
                    "Patients unsure what conditions you treat before calling?",
                    "Manually managing session bookings on WhatsApp or calls?",
                    "No content to explain your specialisations online?",
                    "Losing potential patients who search online and find nothing?",
                ],
                "benefits": [
                    ("🏃", "List Your Specialisations", "Clearly showcase sports injury, post-surgery, and chronic pain treatments."),
                    ("📅", "Automated Session Booking", "Patients book physiotherapy sessions online without calling your clinic."),
                    ("✍️", "Recovery Tips Blog", "Publish helpful content that builds trust and improves Google rankings."),
                    ("🤖", "AI Chatbot Support", "Handles common questions about session duration, pricing, and availability."),
                    ("📱", "Mobile-Optimised", "Most patients research on mobile — your site works perfectly everywhere."),
                    ("⚡", "Live in 7–14 Days", "Fast, guided setup with zero technical work on your end."),
                ],
            },
            {
                "slug": "ophthalmologist",
                "product": curacms,
                "specialty": "ophthalmologist",
                "headline": "Modern Website for Modern Eye Care — Free Demo for Ophthalmologists",
                "subheadline": "Build patient trust with a professional website, online booking, and easy-to-understand treatment information.",
                "target_audience_label": "For Ophthalmologists",
                "social_proof_note": "Trusted by 60+ eye care specialists across India",
                "whatsapp_message_template": "Hi! I saw your ad and I'm interested in CuraCMS for my eye care practice.",
                "default_utm_campaign": "ophthalmology-website-demo",
                "pain_points": [
                    "Patients confused about which eye procedures you offer?",
                    "No online way to book cataract or LASIK consultations?",
                    "Website doesn't reflect the precision and trust your practice requires?",
                    "Missing out on patients who research online before choosing a specialist?",
                ],
                "benefits": [
                    ("👁️", "Procedure Explainers", "Clear, patient-friendly descriptions of cataract, LASIK, and other procedures."),
                    ("📅", "Consultation Booking", "Patients book eye check-ups and procedure consultations online, 24/7."),
                    ("⭐", "Before/After Trust Signals", "Testimonials and results build confidence before the first visit."),
                    ("🤖", "AI Chatbot Support", "Answers common questions about procedures, cost ranges, and recovery."),
                    ("📈", "SEO for Eye Specialists", "Rank higher when patients search for eye specialists in your city."),
                    ("⚡", "Live in 7–14 Days", "Fully managed setup — no technical effort required from your team."),
                ],
            },
            {
                "slug": "pathology-digital-platform",
                "product": curalabs,
                "specialty": "pathology_lab",
                "headline": "Take Your Pathology Lab Digital — Free CuraLabs Demo",
                "subheadline": "Online test booking, home collection management, and secure report downloads — built specifically for Indian pathology labs.",
                "target_audience_label": "Digital Platform for Pathology Labs",
                "social_proof_note": "Trusted by 80+ pathology labs across India",
                "whatsapp_message_template": "Hi! I saw your ad and I'm interested in CuraLabs for my pathology lab.",
                "default_utm_campaign": "curalabs-digital-demo",
                "pain_points": [
                    "Phone lines constantly busy with report status calls?",
                    "Manually coordinating home sample collection over calls?",
                    "Patients frustrated waiting to collect printed reports?",
                    "No digital presence while competitor labs go online?",
                ],
                "benefits": [
                    ("🔬", "Digital Test Catalogue", "Show all your tests with prices, prep instructions, and turnaround times."),
                    ("🏠", "Home Collection Booking", "Patients request home sample collection online with preferred time slots."),
                    ("📄", "Secure Report Download", "OTP-verified, paperless report access — no more waiting or phone calls."),
                    ("💬", "Automated Notifications", "WhatsApp/SMS alerts for booking confirmation and report availability."),
                    ("📊", "Multi-Branch Ready", "Manage multiple collection centres from a single dashboard."),
                    ("⚡", "Live in 7–14 Days", "Our team sets up your full test catalogue and launches it for you."),
                ],
            },
        ]

        for data in pages_data:
            pain_points = data.pop("pain_points")
            benefits = data.pop("benefits")
            product = data.pop("product")

            lp = LandingPage.objects.create(product=product, **data)
            lp.publish()

            for i, text in enumerate(pain_points):
                LandingPainPoint.objects.create(landing_page=lp, text=text, sort_order=i)

            for i, (icon, title, desc) in enumerate(benefits):
                LandingBenefit.objects.create(
                    landing_page=lp, icon=icon, title=title, description=desc, sort_order=i,
                )

            self.stdout.write(self.style.SUCCESS(f"  ✓ /lp/{lp.slug}/ — {lp.headline[:50]}"))

        self.stdout.write(self.style.SUCCESS(f"\n✅ {len(pages_data)} landing pages created and published."))
