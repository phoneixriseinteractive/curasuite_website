"""
CuraSuite — Seed Products Command

Usage:
    python manage.py seed_products
    python manage.py seed_products --clear   # clears existing and re-seeds

Seeds the three CuraSuite products with full features, pricing, and FAQs.
Also creates SEO metadata for each product.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.products.models import Product
from apps.products.services import add_faq, add_feature, add_pricing_tier, create_product
from apps.seo.services import upsert_seo_metadata


PRODUCTS = [
    {
        "key": "curacms",
        "name": "CuraCMS",
        "sort_order": 1,
        "color": "#2563EB",
        "tagline": "Professional Website Platform Built for Doctors & Clinics",
        "short_description": (
            "A healthcare-focused website CMS that enables doctors and clinics to establish "
            "a professional digital presence with appointment booking, blogging, SEO, CRM, "
            "analytics, and patient engagement features."
        ),
        "long_description": (
            "CuraCMS is the easiest way for healthcare professionals to build a world-class "
            "digital presence. Designed specifically for Indian doctors, dental clinics, "
            "physiotherapists, and specialty clinics, it combines a powerful CMS with patient "
            "engagement tools that actually work.\n\n"
            "No technical knowledge required. Go live in days, not months."
        ),
        "target_audience": "Doctors, Dental Clinics, Physiotherapists, Ayurvedic Clinics, Specialty Clinics",
        "seo": {
            "seo_title": "CuraCMS — Professional Website Platform for Doctors | CuraSuite",
            "meta_description": (
                "Build a professional medical website with CuraCMS. Appointment booking, "
                "SEO, CRM, and AI chatbot — designed exclusively for Indian healthcare providers."
            ),
            "schema_type": "SoftwareApplication",
            "focus_keyword": "doctor website CMS India",
            "og_title": "CuraCMS — Website Platform for Doctors & Clinics",
            "og_description": "Professional medical websites with appointment booking, SEO & CRM.",
        },
        "features": [
            {"title": "Website CMS", "description": "Drag-and-drop page builder with healthcare-specific templates. No developer needed.", "icon_name": "layout", "is_highlighted": True, "sort_order": 1},
            {"title": "Online Appointment Booking", "description": "Let patients book appointments 24/7. Reduce phone calls and missed appointments.", "icon_name": "calendar", "is_highlighted": True, "sort_order": 2},
            {"title": "Patient CRM", "description": "Capture leads, manage patient enquiries, and track follow-ups from one dashboard.", "icon_name": "users", "sort_order": 3},
            {"title": "Blog Engine", "description": "Publish healthcare articles that rank on Google and build patient trust.", "icon_name": "file-text", "sort_order": 4},
            {"title": "SEO Tools", "description": "Built-in metadata editor, schema markup, sitemap, and keyword tracking.", "icon_name": "search", "sort_order": 5},
            {"title": "Analytics Dashboard", "description": "Track visitors, appointment requests, and conversion rates in real-time.", "icon_name": "bar-chart", "sort_order": 6},
            {"title": "AI Chatbot", "description": "Answer patient queries 24/7 with a Gemini-powered AI assistant on your website.", "icon_name": "message-circle", "is_highlighted": True, "sort_order": 7},
            {"title": "WhatsApp Integration", "description": "Floating WhatsApp button lets patients contact you instantly from your website.", "icon_name": "phone", "sort_order": 8},
            {"title": "Landing Page Builder", "description": "Create high-converting campaign pages for Google Ads and Meta Ads.", "icon_name": "layers", "sort_order": 9},
        ],
        "pricing": [
            {
                "tier_name": "Starter",
                "price": "9999",
                "billing_cycle": "yearly",
                "description": "Perfect for individual doctors starting their digital journey.",
                "features_included": "5 Pages\nAppointment Booking\nContact Form\nBasic SEO\nWhatsApp Button\nSSL Certificate\nFree Domain (1 Year)",
                "is_featured": False,
                "cta_text": "Get Started",
                "sort_order": 1,
            },
            {
                "tier_name": "Professional",
                "price": "19999",
                "billing_cycle": "yearly",
                "description": "For growing clinics that need more power.",
                "features_included": "Unlimited Pages\nAppointment Booking\nBlog Engine (Unlimited Posts)\nPatient CRM\nAdvanced SEO Tools\nAI Chatbot\nAnalytics Dashboard\nWhatsApp Integration\nEmail Notifications\nPriority Support",
                "is_featured": True,
                "cta_text": "Most Popular",
                "sort_order": 2,
            },
            {
                "tier_name": "Enterprise",
                "price": None,
                "billing_cycle": "custom",
                "description": "For hospital groups and multi-location clinics.",
                "features_included": "Everything in Professional\nMultiple Locations\nCustom Integrations\nDedicated Account Manager\nSLA Support\nCustom Development",
                "is_featured": False,
                "cta_text": "Contact Sales",
                "cta_url": "/contact/",
                "sort_order": 3,
            },
        ],
        "faqs": [
            {"question": "Do I need a developer to build my website with CuraCMS?", "answer": "No. CuraCMS is designed for non-technical users. Our team sets up your website and trains you to manage content. Most doctors are comfortable updating their site within the first day.", "sort_order": 1},
            {"question": "How long does it take to launch my website?", "answer": "A standard CuraCMS website goes live within 7–14 working days. This includes design setup, content upload, and quality review.", "sort_order": 2},
            {"question": "Can I migrate my existing website to CuraCMS?", "answer": "Yes. Our implementation team handles content migration from your existing website at no extra charge for Professional and Enterprise plans.", "sort_order": 3},
            {"question": "Is my patient data secure?", "answer": "Yes. CuraCMS uses HTTPS encryption, secure data storage, and follows industry best practices. We never share your data with third parties.", "sort_order": 4},
            {"question": "Can I add multiple doctors to my clinic website?", "answer": "Yes. You can add doctor profiles with qualifications, specializations, and individual booking calendars for each doctor.", "sort_order": 5},
        ],
    },
    {
        "key": "curalabs",
        "name": "CuraLabs",
        "sort_order": 2,
        "color": "#16A34A",
        "tagline": "Digital Experience Platform for Pathology Laboratories",
        "short_description": (
            "A digital platform designed for pathology laboratories to manage online test "
            "bookings, home collection requests, report downloads, and patient communication — "
            "all in one place."
        ),
        "long_description": (
            "CuraLabs transforms how pathology labs interact with patients and referring doctors. "
            "From online test booking to instant report delivery, CuraLabs delivers the modern "
            "digital experience your patients expect.\n\n"
            "Built specifically for Indian pathology labs, diagnostic centres, and imaging centres."
        ),
        "target_audience": "Pathology Labs, Diagnostic Centers, Imaging Centers",
        "seo": {
            "seo_title": "CuraLabs — Digital Platform for Pathology Labs | CuraSuite",
            "meta_description": (
                "Modernise your pathology lab with CuraLabs. Online test booking, "
                "home collection, report download & patient CRM — built for Indian diagnostic labs."
            ),
            "schema_type": "SoftwareApplication",
            "focus_keyword": "pathology lab software India",
            "og_title": "CuraLabs — Digital Platform for Diagnostic Labs",
            "og_description": "Online test booking, home collection & report download for pathology labs.",
        },
        "features": [
            {"title": "Test Catalogue", "description": "Digital catalogue of all your tests with prices, preparation instructions, and turnaround times.", "icon_name": "list", "is_highlighted": True, "sort_order": 1},
            {"title": "Online Test Booking", "description": "Patients book tests directly from your website 24/7. Reduce call volume significantly.", "icon_name": "calendar", "is_highlighted": True, "sort_order": 2},
            {"title": "Home Collection", "description": "Patients request home collection with their preferred slot and address.", "icon_name": "home", "sort_order": 3},
            {"title": "Report Download", "description": "Patients download their reports securely with an OTP or booking ID — no more phone calls.", "icon_name": "download", "is_highlighted": True, "sort_order": 4},
            {"title": "Patient Notifications", "description": "Automated SMS and WhatsApp notifications for booking confirmation and report readiness.", "icon_name": "bell", "sort_order": 5},
            {"title": "Patient CRM", "description": "Manage patient records, test history, and communication from a single dashboard.", "icon_name": "users", "sort_order": 6},
            {"title": "Blog Platform", "description": "Publish health awareness content to attract organic traffic and educate patients.", "icon_name": "file-text", "sort_order": 7},
            {"title": "SEO & Analytics", "description": "Built-in SEO tools and analytics so your lab ranks higher and tracks performance.", "icon_name": "bar-chart", "sort_order": 8},
        ],
        "pricing": [
            {
                "tier_name": "Basic",
                "price": "14999",
                "billing_cycle": "yearly",
                "description": "For small labs getting started with digital.",
                "features_included": "Test Catalogue (up to 100 tests)\nOnline Booking\nReport Download\nContact Form\nBasic SEO\nSSL Certificate",
                "is_featured": False,
                "cta_text": "Get Started",
                "sort_order": 1,
            },
            {
                "tier_name": "Growth",
                "price": "29999",
                "billing_cycle": "yearly",
                "description": "For established labs ready to scale digitally.",
                "features_included": "Unlimited Tests\nOnline Booking\nHome Collection Requests\nReport Download with OTP\nPatient Notifications (SMS + WhatsApp)\nPatient CRM\nBlog Platform\nSEO Tools\nAnalytics Dashboard",
                "is_featured": True,
                "cta_text": "Most Popular",
                "sort_order": 2,
            },
            {
                "tier_name": "Enterprise",
                "price": None,
                "billing_cycle": "custom",
                "description": "For diagnostic chains and multi-branch labs.",
                "features_included": "Everything in Growth\nMultiple Branches\nBranded Mobile App\nLIS Integration\nCustom Reporting\nDedicated Support",
                "is_featured": False,
                "cta_text": "Contact Sales",
                "cta_url": "/contact/",
                "sort_order": 3,
            },
        ],
        "faqs": [
            {"question": "Can patients download reports without creating an account?", "answer": "Yes. Patients can download reports using their booking ID and mobile OTP — no account creation needed. This removes friction and improves patient experience.", "sort_order": 1},
            {"question": "Does CuraLabs integrate with Lab Information Systems (LIS)?", "answer": "LIS integration is available in the Enterprise plan. We support custom integrations with major LIS providers used in India.", "sort_order": 2},
            {"question": "How are home collection slots managed?", "answer": "Home collection requests are received in the admin panel with patient details and preferred time slots. Your team confirms and assigns a phlebotomist. Future versions will include automated slot management.", "sort_order": 3},
            {"question": "Can I list all my tests with NABL accreditation badges?", "answer": "Yes. The test catalogue supports custom badges, accreditation details, preparation instructions, and sample type information for each test.", "sort_order": 4},
        ],
    },
    {
        "key": "curasuite",
        "name": "CuraSuite CMS",
        "sort_order": 3,
        "color": "#7C3AED",
        "tagline": "Complete Clinic Management Software for Modern Healthcare",
        "short_description": (
            "A comprehensive clinic management system for healthcare providers to manage "
            "appointments, patient records, billing, staff, inventory, and daily clinic "
            "operations from a single platform."
        ),
        "long_description": (
            "CuraSuite CMS is the operating system for your clinic. Designed for single-doctor "
            "practices, multi-specialty clinics, and polyclinics, it brings every part of your "
            "clinic onto one platform — from reception to billing to the doctor's dashboard.\n\n"
            "Reduce administrative burden, improve patient flow, and grow your practice."
        ),
        "target_audience": "Single Doctor Clinics, Multi-specialty Clinics, Polyclinics, Small Hospitals",
        "seo": {
            "seo_title": "CuraSuite — Clinic Management Software for Doctors | CuraSuite",
            "meta_description": (
                "Manage your clinic operations with CuraSuite. Appointments, patient records, "
                "billing, prescriptions & reports — all in one clinic management software."
            ),
            "schema_type": "SoftwareApplication",
            "focus_keyword": "clinic management software India",
            "og_title": "CuraSuite — Complete Clinic Management System",
            "og_description": "Appointments, billing, patient records & more — one platform for your clinic.",
        },
        "features": [
            {"title": "Appointment Management", "description": "Smart scheduling with doctor-wise calendars, slot management, and automated reminders.", "icon_name": "calendar", "is_highlighted": True, "sort_order": 1},
            {"title": "Reception Dashboard", "description": "Front desk staff manage patient check-ins, token system, and waiting queue in real time.", "icon_name": "monitor", "sort_order": 2},
            {"title": "Doctor Dashboard", "description": "Patient queue, consultation history, and prescription tools in one focused view.", "icon_name": "user", "is_highlighted": True, "sort_order": 3},
            {"title": "Patient Records", "description": "Comprehensive patient history with visits, prescriptions, reports, and notes.", "icon_name": "folder", "sort_order": 4},
            {"title": "Billing & Invoicing", "description": "Generate invoices, track payments, and manage outstanding balances.", "icon_name": "credit-card", "is_highlighted": True, "sort_order": 5},
            {"title": "Prescription Management", "description": "Digital prescriptions with medicine database, dosage templates, and print support.", "icon_name": "file-text", "sort_order": 6},
            {"title": "Inventory Management", "description": "Track medicines, consumables, and equipment with low-stock alerts.", "icon_name": "package", "sort_order": 7},
            {"title": "Reports & Analytics", "description": "Revenue reports, patient statistics, doctor productivity, and business insights.", "icon_name": "bar-chart", "sort_order": 8},
        ],
        "pricing": [
            {
                "tier_name": "Clinic Starter",
                "price": None,
                "billing_cycle": "custom",
                "description": "For single-doctor clinics getting started with digital operations.",
                "features_included": "Appointment Management\nReception Dashboard\nPatient Records\nBasic Billing\nDoctor Dashboard\nPrescription Management",
                "is_featured": False,
                "cta_text": "Request Pricing",
                "cta_url": "/contact/",
                "sort_order": 1,
            },
            {
                "tier_name": "Clinic Pro",
                "price": None,
                "billing_cycle": "custom",
                "description": "For multi-doctor clinics needing full operational control.",
                "features_included": "Everything in Starter\nMultiple Doctors\nInventory Management\nAdvanced Billing\nPatient Notifications\nReports & Analytics\nCRM Integration",
                "is_featured": True,
                "cta_text": "Contact Sales",
                "cta_url": "/contact/",
                "sort_order": 2,
            },
        ],
        "faqs": [
            {"question": "Can multiple doctors share the same CuraSuite installation?", "answer": "Yes. CuraSuite supports multiple doctors on a single installation, each with their own calendar, patient queue, and dashboard. Roles and permissions control what each staff member can access.", "sort_order": 1},
            {"question": "Does CuraSuite work on tablets and mobile devices?", "answer": "Yes. The web application is fully responsive and works on tablets and desktops. A dedicated mobile application is on the product roadmap.", "sort_order": 2},
            {"question": "Can I print prescriptions from CuraSuite?", "answer": "Yes. Prescriptions can be printed on your clinic letterhead or saved as PDFs. The system includes a medicine database and dosage templates to speed up prescription writing.", "sort_order": 3},
            {"question": "Is there a free trial available?", "answer": "Yes. We offer a 30-day free trial for qualified clinics. Book a demo and our team will set up a trial account tailored to your specialty.", "sort_order": 4},
        ],
    },
]


class Command(BaseCommand):
    help = "Seed the three CuraSuite products with features, pricing, and FAQs."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing products before seeding.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["clear"]:
            Product.all_objects.all().delete()
            self.stdout.write(self.style.WARNING("Existing products cleared."))

        for product_data in PRODUCTS:
            key = product_data["key"]

            if Product.all_objects.filter(key=key).exists():
                self.stdout.write(f"  Skipping {key} (already exists). Use --clear to re-seed.")
                continue

            self.stdout.write(f"  Seeding {product_data['name']}...")

            product = create_product(
                key=key,
                name=product_data["name"],
                tagline=product_data["tagline"],
                short_description=product_data["short_description"],
                long_description=product_data["long_description"],
                target_audience=product_data["target_audience"],
                color=product_data["color"],
                sort_order=product_data["sort_order"],
            )

            # SEO
            upsert_seo_metadata(product, **product_data["seo"])

            # Features
            for f in product_data["features"]:
                add_feature(product, **f)

            # Pricing
            for p in product_data["pricing"]:
                add_pricing_tier(product, **p)

            # FAQs
            for q in product_data["faqs"]:
                add_faq(product, **q)

            # Fix slug for curasuite (name is 'CuraSuite CMS' but slug should be 'curasuite')
            if product.key == 'curasuite' and product.slug != 'curasuite':
                product.slug = 'curasuite'
                product.save(update_fields=['slug'])

            # Publish the product
            product.publish()

            self.stdout.write(self.style.SUCCESS(f"  ✓ {product.name} seeded and published."))

        self.stdout.write(self.style.SUCCESS("\nProduct seeding complete."))
