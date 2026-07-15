"""
CuraSuite — Master Seed Command
Usage:
    python manage.py seed_all
    python manage.py seed_all --clear    # wipe everything first

Seeds every module with realistic, production-quality data so every
admin panel feature has something to display and interact with.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
import random


class Command(BaseCommand):
    help = "Seed all CuraSuite modules with realistic demo data."

    def add_arguments(self, parser):
        parser.add_argument("--clear", action="store_true",
                            help="Clear existing data before seeding.")

    def handle(self, *args, **options):
        if options["clear"]:
            self._clear_all()

        self.stdout.write(self.style.MIGRATE_HEADING("\n🌱 CuraSuite Master Seed\n"))

        admin = self._seed_users()
        self._seed_site_settings()
        self._seed_social_links()
        self._seed_smtp()
        self._seed_robots()
        self._seed_announcement()
        self._seed_integrations()
        products = self._seed_products(admin)
        self._seed_global_faqs()
        self._seed_testimonials()
        self._seed_pages(admin)
        self._seed_blogs(admin)
        self._seed_redirects()
        self._seed_crm(admin)
        self._seed_newsletter()

        self.stdout.write(self.style.SUCCESS(
            "\n✅ Seed complete — visit http://localhost:8000/manage/ to explore.\n"
            "   Admin login: admin@curasuite.com / Admin@123456\n"
        ))

    # ──────────────────────────────────────────────────────────────────────────
    def _clear_all(self):
        self.stdout.write(self.style.WARNING("  Clearing existing data…"))
        from apps.products.models import Product, ProductFeature, ProductPricing, ProductFAQ, ProductScreenshot
        from apps.pages.models import Page, PageRevision
        from apps.blogs.models import Blog, BlogCategory, BlogTag, BlogComment
        from apps.crm.models import Lead, DemoRequest, LeadNote, LeadActivity
        from apps.newsletter.models import NewsletterSubscriber, NewsletterCampaign, NewsletterSend
        from apps.seo.models import SEOMetadata, Redirect
        from apps.settings_app.models import GlobalFAQ, Testimonial, AnnouncementBar
        from apps.integrations.models import Integration
        from apps.accounts.models import User

        for M in [NewsletterSend, NewsletterCampaign, NewsletterSubscriber,
                  LeadActivity, LeadNote, DemoRequest, Lead,
                  BlogComment, Blog, BlogTag, BlogCategory,
                  PageRevision, Page,
                  ProductFAQ, ProductPricing, ProductFeature, ProductScreenshot, Product,
                  SEOMetadata, Redirect,
                  GlobalFAQ, Testimonial, AnnouncementBar, Integration]:
            M.objects.all().delete()

        User.objects.filter(is_superuser=False).delete()
        self.stdout.write(self.style.SUCCESS("  ✓ Cleared"))

    # ── USERS ─────────────────────────────────────────────────────────────────
    def _seed_users(self):
        from apps.accounts.models import User
        self.stdout.write("  → Users…")

        admin, _ = User.objects.get_or_create(
            email="admin@curasuite.com",
            defaults=dict(first_name="Akash", last_name="Mehta",
                          is_staff=True, is_superuser=True, is_active=True),
        )
        if not admin.has_usable_password():
            admin.set_password("Admin@123456")
            admin.save()

        staff_data = [
            ("priya@curasuite.com", "Priya", "Sharma", True, False),
            ("raj@curasuite.com",   "Raj",   "Verma",  True, False),
            ("neha@curasuite.com",  "Neha",  "Singh",  True, False),
        ]
        for email, fn, ln, staff, su in staff_data:
            u, created = User.objects.get_or_create(
                email=email,
                defaults=dict(first_name=fn, last_name=ln,
                              is_staff=staff, is_superuser=su, is_active=True),
            )
            if created:
                u.set_password("Staff@123456")
                u.save()

        self.stdout.write(self.style.SUCCESS(f"    ✓ 4 users (admin + 3 staff)"))
        return admin

    # ── SITE SETTINGS ─────────────────────────────────────────────────────────
    def _seed_site_settings(self):
        from apps.integrations.models import SiteSettings
        self.stdout.write("  → Site Settings…")
        s = SiteSettings.load()
        s.ga4_measurement_id   = "G-XXXXXXXXXX"
        s.gtm_container_id     = "GTM-XXXXXXX"
        s.meta_pixel_id        = "123456789012345"
        s.clarity_project_id   = "abcdefghij"
        s.whatsapp_enabled     = True
        s.whatsapp_phone       = "919876543210"
        s.whatsapp_message     = "Hi! I'd like to know more about CuraSuite."
        s.whatsapp_tooltip     = "Chat with us on WhatsApp"
        s.chatbot_enabled      = True
        s.chatbot_name         = "CuraSuite Assistant"
        s.chatbot_greeting     = "Hi! I'm the CuraSuite Assistant. How can I help you today? 😊"
        s.chatbot_system_prompt = (
            "You are the CuraSuite Assistant, a helpful AI for CuraSuite — "
            "India's healthcare technology platform built by PhoenixRise Interactive. "
            "Help visitors understand our three products:\n"
            "• CuraCMS — Professional website CMS for doctors and clinics\n"
            "• CuraLabs — Digital experience platform for pathology laboratories\n"
            "• CuraSuite CMS — Complete clinic management software\n"
            "Answer questions about features, pricing (starting ₹9,999/year), "
            "and guide visitors to book a free demo. "
            "Be warm, professional, and concise. "
            "For medical advice, always direct users to qualified healthcare professionals."
        )
        s.captcha_enabled   = False
        s.captcha_provider  = "turnstile"
        s.save()
        self.stdout.write(self.style.SUCCESS("    ✓ Site settings configured"))

    # ── SMTP ──────────────────────────────────────────────────────────────────
    def _seed_smtp(self):
        from apps.settings_app.models import SMTPSettings
        self.stdout.write("  → SMTP Settings…")
        smtp = SMTPSettings.load()
        smtp.host        = "smtp.gmail.com"
        smtp.port        = 587
        smtp.username    = "hello@curasuite.com"
        smtp.from_email  = "hello@curasuite.com"
        smtp.from_name   = "CuraSuite"
        smtp.use_tls     = True
        smtp.use_ssl     = False
        smtp.is_verified = False
        smtp.save()
        self.stdout.write(self.style.SUCCESS("    ✓ SMTP settings saved (add real password in .env)"))

    # ── SOCIAL LINKS ──────────────────────────────────────────────────────────
    def _seed_social_links(self):
        from apps.settings_app.models import SocialLinks
        self.stdout.write("  → Social Links…")
        s = SocialLinks.load()
        s.facebook     = "https://www.facebook.com/curasuite"
        s.instagram    = "https://www.instagram.com/curasuite"
        s.linkedin     = "https://www.linkedin.com/company/curasuite"
        s.twitter_x    = "https://x.com/curasuite"
        s.youtube      = "https://www.youtube.com/@curasuite"
        s.whatsapp_link= "https://wa.me/919876543210"
        s.save()
        self.stdout.write(self.style.SUCCESS("    ✓ Social links saved"))

    # ── ROBOTS.TXT ────────────────────────────────────────────────────────────
    def _seed_robots(self):
        from apps.settings_app.models import RobotsTxt
        self.stdout.write("  → Robots.txt…")
        r = RobotsTxt.load()
        r.content = (
            "User-agent: *\n"
            "Allow: /\n"
            "Disallow: /manage/\n"
            "Disallow: /admin/\n"
            "Disallow: /api/\n"
            "\n"
            "Sitemap: https://curasuite.com/sitemap.xml\n"
        )
        r.save()
        self.stdout.write(self.style.SUCCESS("    ✓ robots.txt saved"))

    # ── ANNOUNCEMENT BAR ──────────────────────────────────────────────────────
    def _seed_announcement(self):
        from apps.settings_app.models import AnnouncementBar
        self.stdout.write("  → Announcement Bar…")
        if not AnnouncementBar.objects.exists():
            AnnouncementBar.objects.create(
                text="🎉 CuraLabs is now live — Digital platform for pathology labs.",
                link_text="Explore CuraLabs",
                link_url="/products/curalabs/",
                style="promo",
                is_active=True,
                is_dismissible=True,
            )
            AnnouncementBar.objects.create(
                text="🚀 Limited time offer — CuraCMS Starter plan at ₹7,999/year. Save ₹2,000!",
                link_text="Claim Offer",
                link_url="/pricing/",
                style="success",
                is_active=False,
                is_dismissible=True,
            )
        self.stdout.write(self.style.SUCCESS("    ✓ 2 announcement bars"))

    # ── INTEGRATIONS ──────────────────────────────────────────────────────────
    def _seed_integrations(self):
        from apps.integrations.models import Integration
        self.stdout.write("  → Integrations…")
        integrations = [
            (Integration.Provider.GOOGLE_ANALYTICS,   True,  {"measurement_id": "G-XXXXXXXXXX"}),
            (Integration.Provider.GOOGLE_TAG_MANAGER, True,  {"container_id": "GTM-XXXXXXX"}),
            (Integration.Provider.META_PIXEL,         True,  {"pixel_id": "123456789012345"}),
            (Integration.Provider.MICROSOFT_CLARITY,  True,  {"project_id": "abcdefghij"}),
            (Integration.Provider.WHATSAPP,           True,  {"phone": "919876543210"}),
            (Integration.Provider.GEMINI,             True,  {"model_chain": "gemini-2.0-flash-lite,gemini-2.0-flash"}),
            (Integration.Provider.SMTP,               True,  {"host": "smtp.gmail.com", "port": 587}),
            (Integration.Provider.RECAPTCHA,          False, {"provider": "turnstile"}),
        ]
        for provider, enabled, config in integrations:
            Integration.objects.get_or_create(
                provider=provider,
                defaults={"is_enabled": enabled, "config": config},
            )
        self.stdout.write(self.style.SUCCESS(f"    ✓ {len(integrations)} integrations configured"))

    # ── PRODUCTS ──────────────────────────────────────────────────────────────
    def _seed_products(self, admin):
        from apps.products.models import Product
        self.stdout.write("  → Products (running existing seed command)…")
        from django.core.management import call_command
        import io
        out = io.StringIO()
        call_command("seed_products", stdout=out)
        lines = [l for l in out.getvalue().strip().split('\n') if l.strip()]
        for line in lines:
            self.stdout.write(f"    {line}")
        # Fix slug for CuraSuite product (slugify makes 'curasuite-cms', should be 'curasuite')
        try:
            cs = Product.all_objects.filter(key='curasuite').first()
            if cs and cs.slug != 'curasuite':
                cs.slug = 'curasuite'
                cs.save(update_fields=['slug'])
        except Exception:
            pass

        products = list(Product.objects.order_by("sort_order"))
        self.stdout.write(self.style.SUCCESS(f"    ✓ {len(products)} products seeded"))
        return products

    # ── GLOBAL FAQS ───────────────────────────────────────────────────────────
    def _seed_global_faqs(self):
        from apps.settings_app.models import GlobalFAQ
        self.stdout.write("  → Global FAQs…")
        if GlobalFAQ.objects.exists():
            self.stdout.write("    (already seeded, skipping)")
            return

        faqs = [
            ("general",   "What is CuraSuite?",
             "CuraSuite is a unified healthcare technology ecosystem built by PhoenixRise Interactive. It includes CuraCMS (website platform for doctors), CuraLabs (digital platform for pathology labs), and CuraSuite CMS (clinic management software)."),
            ("general",   "Who can use CuraSuite?",
             "CuraSuite is designed for individual doctors, dental clinics, physiotherapists, pathology labs, diagnostic centres, and multi-specialty clinics across India."),
            ("general",   "Is there a free trial available?",
             "Yes. We offer a 30-day free trial for all products. Book a demo and our team will configure a trial account tailored to your specialty within 24 hours."),
            ("general",   "How long does implementation take?",
             "CuraCMS and CuraLabs websites go live within 7–14 working days. CuraSuite CMS implementations typically take 14–21 days including staff training."),
            ("general",   "Do you provide training and support?",
             "Yes. Every plan includes onboarding training, video guides, and email support. Professional and Enterprise plans include priority support with dedicated account managers."),
            ("pricing",   "What does CuraCMS cost?",
             "CuraCMS starts from ₹9,999 per year for the Starter plan. The Professional plan is ₹19,999 per year. Custom Enterprise pricing is available for hospital groups and multi-location clinics."),
            ("pricing",   "What does CuraLabs cost?",
             "CuraLabs starts from ₹14,999 per year for the Basic plan. The Growth plan is ₹29,999 per year. Enterprise pricing is available for diagnostic chains."),
            ("pricing",   "Are there any setup fees?",
             "There are no hidden setup fees. The annual plan includes initial setup, content upload assistance, and training. Domain registration (first year) is included in Starter plans."),
            ("pricing",   "Can I upgrade my plan later?",
             "Yes. You can upgrade your plan at any time. The price difference is prorated for the remaining subscription period."),
            ("technical", "Is my patient data secure?",
             "Yes. CuraSuite uses HTTPS encryption, secure data centres, regular backups, and follows industry security best practices. We never share your data with third parties."),
            ("technical", "Can I migrate my existing website?",
             "Yes. Our implementation team handles content migration from your existing website at no extra charge for Professional and Enterprise plans."),
            ("technical", "Does CuraSuite work on mobile devices?",
             "Yes. All CuraSuite products are fully responsive and work on smartphones, tablets, and desktops. A dedicated patient mobile app is on our roadmap."),
            ("technical", "Can I use my own domain name?",
             "Yes. You can connect your existing domain or purchase a new one. We handle the technical DNS configuration as part of the setup process."),
            ("support",   "What support channels are available?",
             "We offer email support, WhatsApp support, and scheduled video calls. Enterprise clients have access to a dedicated account manager and phone support."),
            ("support",   "What are your support hours?",
             "Email and WhatsApp support is available Monday to Saturday, 9 AM to 7 PM IST. Critical issues for Enterprise clients are handled 24/7."),
            ("security",  "Is CuraSuite HIPAA compliant?",
             "CuraSuite follows strong data security practices including encryption, access controls, and audit logs. For specific compliance requirements, please contact our team for a detailed assessment."),
            ("security",  "How often is my data backed up?",
             "Data is backed up daily with incremental backups and weekly full backups. Backups are encrypted and stored in secure, geographically separate locations."),
        ]

        for i, (cat, q, a) in enumerate(faqs):
            GlobalFAQ.objects.create(
                question=q, answer=a, category=cat,
                sort_order=i, is_active=True,
            )
        self.stdout.write(self.style.SUCCESS(f"    ✓ {len(faqs)} global FAQs"))

    # ── TESTIMONIALS ──────────────────────────────────────────────────────────
    def _seed_testimonials(self):
        from apps.settings_app.models import Testimonial
        self.stdout.write("  → Testimonials…")
        if Testimonial.objects.exists():
            self.stdout.write("    (already seeded, skipping)")
            return

        # specialty values match apps.crm.models.Lead.Specialty / apps.landing_pages LandingPage.specialty —
        # keeps each landing page's testimonial pool restricted to its own vertical (see get_testimonials_for_landing_page).
        testimonials = [
            ("Dr. Priya Nair",    "General Physician",      "Nair Family Clinic",           "Kochi",       5, "CuraCMS",  "general_physician",
             "CuraCMS transformed how patients find us. Our online appointment bookings increased by 300% in the first month. The setup was fast and the support team was exceptional."),
            ("Dr. Rajesh Sharma", "Dental Surgeon",         "Sharma Dental Care",           "Jaipur",      5, "CuraCMS",  "dentist",
             "We moved from a poorly designed website to CuraCMS and saw immediate results. Patient enquiries doubled and our Google ranking improved significantly within 60 days."),
            ("Dr. Meera Pillai",  "Physiotherapist",        "Pillai Physiotherapy Centre",  "Bangalore",   5, "CuraCMS",  "physiotherapist",
             "The blog feature helped us publish health content regularly. We now rank on page 1 for physiotherapy Bangalore. The AI chatbot handles patient queries even at night."),
            ("Mr. Suresh Kumar",  "Lab Director",           "Kumar Diagnostics",            "Hyderabad",   5, "CuraLabs", "pathology_lab",
             "CuraLabs gave our pathology lab a professional digital presence. Patients can now book tests online and download reports without calling us. Our call volume dropped by 60%."),
            ("Dr. Anjali Mehta",  "Managing Director",      "Mehta Diagnostic Centre",      "Ahmedabad",   5, "CuraLabs", "pathology_lab",
             "The home collection booking feature was a game-changer. We now manage home collection requests efficiently and send automated WhatsApp confirmations. Highly recommended."),
            ("Dr. Vikram Singh",  "Medical Director",       "Singh Multi-Specialty Clinic", "Lucknow",     5, "CuraSuite", "",
             "CuraSuite CMS streamlined our entire clinic operations. Reception, billing, and doctor workflows are now on one platform. We save 3 hours of administrative work every day."),
            ("Dr. Sunita Reddy",  "Gynecologist",           "Reddy Women's Clinic",         "Pune",        4, "CuraCMS",  "other",
             "Professional website, easy to manage, and excellent SEO performance. Our clinic now gets 15-20 new patient enquiries every week through the website alone."),
            ("Mr. Arun Patel",    "Operations Manager",     "Patel Lab Network",            "Surat",       5, "CuraLabs", "pathology_lab",
             "We have 3 lab branches and CuraLabs manages all of them. Patient data, test catalogues, and report downloads work seamlessly across all locations."),
            ("Dr. Kavitha Iyer",  "Ayurvedic Practitioner", "Iyer Ayurveda Clinic",        "Chennai",     5, "CuraCMS",  "other",
             "I was skeptical about going digital, but CuraCMS made it easy. My patients love booking appointments online and the website looks beautiful on all devices."),
            ("Dr. Ravi Malhotra", "Orthopedic Surgeon",     "Malhotra Orthopedic Centre",   "Delhi",       5, "CuraSuite", "",
             "From patient registration to billing — everything is digitized. The prescription module with our medicine templates saves 20 minutes per patient consultation."),
        ]

        for i, (name, designation, clinic, loc, rating, product, specialty, feedback) in enumerate(testimonials):
            Testimonial.objects.create(
                customer_name=name, designation=designation,
                clinic_name=clinic, location=loc,
                rating=rating, product=product, specialty=specialty, feedback=feedback,
                status="approved",
                is_featured=(i < 6),
                sort_order=i,
            )
        self.stdout.write(self.style.SUCCESS(f"    ✓ {len(testimonials)} testimonials (6 featured)"))

    # ── PAGES ─────────────────────────────────────────────────────────────────
    def _seed_pages(self, admin):
        from apps.pages.services import create_page
        from apps.seo.services import upsert_seo_metadata
        self.stdout.write("  → Pages…")
        if __import__('apps.pages.models', fromlist=['Page']).Page.objects.exists():
            self.stdout.write("    (already seeded, skipping)")
            return

        pages_data = [
            {
                "title": "Home",
                "slug": "home",
                "page_type": "home",
                "excerpt": "CuraSuite — Healthcare Technology That Helps Your Practice Grow.",
                "content": "<p>Welcome to CuraSuite. India's most trusted healthcare technology platform for clinics, doctors, and diagnostic labs.</p>",
                "seo": {
                    "seo_title": "CuraSuite — Healthcare Technology That Helps Your Practice Grow",
                    "meta_description": "CuraSuite delivers professional website CMS, pathology lab platforms, and clinic management software built exclusively for Indian healthcare providers.",
                    "schema_type": "WebSite",
                    "focus_keyword": "healthcare technology platform India",
                },
            },
            {
                "title": "About CuraSuite",
                "slug": "about",
                "page_type": "about",
                "template": "about",
                "excerpt": "PhoenixRise Interactive — Building India's most trusted healthcare technology ecosystem.",
                "content": "<h2>Our Mission</h2><p>To simplify healthcare technology by delivering practical, secure, and scalable digital solutions that help healthcare providers focus on patient care.</p><h2>Our Vision</h2><p>Become India's most trusted healthcare technology ecosystem for clinics, diagnostic centres, and healthcare professionals.</p><h2>Why Healthcare?</h2><p>Healthcare in India is undergoing rapid digital transformation. Yet most clinics and labs use fragmented, outdated software that doesn't talk to each other. CuraSuite was built to change that.</p>",
                "seo": {
                    "seo_title": "About CuraSuite — Healthcare Technology by PhoenixRise Interactive",
                    "meta_description": "Learn about CuraSuite and PhoenixRise Interactive — our mission to digitise Indian healthcare for clinics, doctors, and diagnostic labs.",
                    "schema_type": "Organization",
                    "focus_keyword": "about curasuite healthcare technology",
                },
            },
            {
                "title": "Pricing",
                "slug": "pricing",
                "page_type": "pricing",
                "template": "pricing",
                "excerpt": "Simple, transparent pricing for CuraCMS, CuraLabs, and CuraSuite.",
                "content": "<p>All plans include free setup, training, and support. No hidden fees.</p><p>Starting from ₹9,999/year for CuraCMS, ₹14,999/year for CuraLabs. CuraSuite pricing on request.</p>",
                "seo": {
                    "seo_title": "Pricing — CuraSuite Healthcare Technology Plans",
                    "meta_description": "CuraCMS from ₹9,999/year. CuraLabs from ₹14,999/year. Transparent pricing with no hidden fees. 30-day free trial available.",
                    "schema_type": "WebPage",
                    "focus_keyword": "curasuite pricing healthcare software cost",
                },
            },
            {
                "title": "Contact Us",
                "slug": "contact",
                "page_type": "contact",
                "excerpt": "Get in touch with the CuraSuite team. Book a free demo today.",
                "content": "<p>We'd love to hear from you. Book a free demo, request pricing, or just say hello.</p><p><strong>Email:</strong> hello@curasuite.com</p><p><strong>WhatsApp:</strong> +91 98765 43210</p><p><strong>Business Hours:</strong> Monday–Saturday, 9 AM–7 PM IST</p>",
                "seo": {
                    "seo_title": "Contact CuraSuite — Book a Free Demo",
                    "meta_description": "Contact CuraSuite to book a free product demo, request pricing, or get support. Available Monday–Saturday, 9 AM–7 PM IST.",
                    "schema_type": "ContactPage",
                    "focus_keyword": "contact curasuite book demo",
                },
            },
            {
                "title": "Privacy Policy",
                "slug": "privacy-policy",
                "page_type": "legal",
                "excerpt": "How CuraSuite collects, uses, and protects your data.",
                "content": "<h2>Privacy Policy</h2><p><em>Last updated: June 2025</em></p><h3>Information We Collect</h3><p>We collect information you provide when booking demos, subscribing to our newsletter, or contacting us — including name, email, phone, and organisation.</p><h3>How We Use It</h3><p>We use your information to provide our services, respond to enquiries, send relevant updates, and improve CuraSuite products. We never sell your data.</p><h3>Data Security</h3><p>All data is encrypted in transit (HTTPS) and at rest. We use industry-standard security practices and conduct regular security reviews.</p><h3>Contact</h3><p>For privacy concerns, email privacy@curasuite.com.</p>",
                "seo": {
                    "seo_title": "Privacy Policy | CuraSuite",
                    "meta_description": "Read CuraSuite's privacy policy to understand how we collect, use, and protect your personal information.",
                    "robots": "noindex, follow",
                },
            },
            {
                "title": "Terms & Conditions",
                "slug": "terms",
                "page_type": "legal",
                "excerpt": "Terms and conditions for using CuraSuite products and services.",
                "content": "<h2>Terms &amp; Conditions</h2><p><em>Last updated: June 2025</em></p><h3>Acceptance</h3><p>By using CuraSuite products, you agree to these terms. If you do not agree, please do not use our services.</p><h3>Service Description</h3><p>CuraSuite provides healthcare technology software including website CMS, lab management platforms, and clinic management systems.</p><h3>Payment</h3><p>All plans are billed annually. Refunds are available within 30 days of purchase if you are not satisfied.</p><h3>Support</h3><p>We provide email and WhatsApp support during business hours. Response times depend on your plan tier.</p>",
                "seo": {
                    "seo_title": "Terms & Conditions | CuraSuite",
                    "meta_description": "Read the terms and conditions for using CuraSuite healthcare technology products and services.",
                    "robots": "noindex, follow",
                },
            },
            {
                "title": "Refund Policy",
                "slug": "refund-policy",
                "page_type": "legal",
                "excerpt": "CuraSuite's 30-day money-back guarantee and refund process.",
                "content": "<h2>Refund Policy</h2><p>We offer a 30-day money-back guarantee on all annual plans. If you are not completely satisfied within the first 30 days, contact us for a full refund — no questions asked.</p><p>To request a refund, email billing@curasuite.com with your order details.</p>",
                "seo": {
                    "seo_title": "Refund Policy — 30-Day Money Back Guarantee | CuraSuite",
                    "meta_description": "CuraSuite offers a 30-day money-back guarantee on all annual plans. Full refund, no questions asked.",
                    "robots": "noindex, follow",
                },
            },
            {
                "title": "Solutions for Doctors",
                "slug": "solutions/doctors",
                "page_type": "custom",
                "template": "solutions",
                "excerpt": "Helping independent doctors build a strong digital presence and streamline patient interactions.",
                "content": "<h2>Digital Solutions for Doctors</h2><p>Whether you're an independent practitioner or part of a multi-doctor clinic, CuraSuite has the right tools to grow your practice online.</p><h3>What Doctors Get</h3><ul><li>Professional website that builds patient trust</li><li>Online appointment booking available 24/7</li><li>Blog to publish health content and rank on Google</li><li>AI chatbot to answer patient queries automatically</li><li>Patient CRM to manage enquiries and follow-ups</li></ul>",
                "seo": {
                    "seo_title": "Digital Solutions for Doctors — CuraSuite",
                    "meta_description": "CuraSuite helps Indian doctors build professional websites, accept online bookings, and grow their practice digitally.",
                    "focus_keyword": "digital solutions for doctors India",
                    "schema_type": "WebPage",
                },
            },
            {
                "title": "Solutions for Clinics",
                "slug": "solutions/clinics",
                "page_type": "custom",
                "template": "solutions",
                "excerpt": "Helping clinics improve operational efficiency while delivering a better patient experience.",
                "content": "<h2>Digital Solutions for Clinics</h2><p>From reception management to patient billing, CuraSuite helps clinics digitize their operations and deliver a world-class patient experience.</p><h3>Key Benefits</h3><ul><li>Digital reception and patient queue management</li><li>Appointment scheduling for multiple doctors</li><li>Digital prescriptions with medicine templates</li><li>Billing and invoice management</li><li>Inventory tracking with low-stock alerts</li></ul>",
                "seo": {
                    "seo_title": "Digital Solutions for Clinics — CuraSuite",
                    "meta_description": "Digitize your clinic with CuraSuite. Appointment management, digital prescriptions, billing, and patient records on one platform.",
                    "focus_keyword": "clinic management software India",
                    "schema_type": "WebPage",
                },
            },
            {
                "title": "Solutions for Pathology Labs",
                "slug": "solutions/pathology-labs",
                "page_type": "custom",
                "template": "solutions",
                "excerpt": "Helping diagnostic centres digitize patient engagement and online services.",
                "content": "<h2>Digital Solutions for Pathology Labs</h2><p>CuraLabs gives your pathology lab a modern digital presence that patients expect. From online test booking to instant report delivery.</p><h3>Features Built for Labs</h3><ul><li>Digital test catalogue with preparation instructions</li><li>Online booking and home collection requests</li><li>Secure report download with OTP verification</li><li>Automated SMS and WhatsApp notifications</li><li>Patient CRM and communication tools</li></ul>",
                "seo": {
                    "seo_title": "Digital Solutions for Pathology Labs — CuraLabs",
                    "meta_description": "CuraLabs helps pathology labs and diagnostic centres digitize with online test booking, report download, and patient notifications.",
                    "focus_keyword": "pathology lab software digital platform India",
                    "schema_type": "WebPage",
                },
            },
        ]

        count = 0
        for data in pages_data:
            seo_data  = data.pop("seo", {})
            slug      = data.pop("slug")
            template  = data.pop("template", "default")
            page = create_page(created_by=admin, **data)
            page.slug     = slug
            page.template = template
            page.show_in_sitemap = True
            page.show_in_nav = data.get("page_type") in ("home", "about", "pricing", "contact")
            page.save()
            page.publish(published_by=admin)
            if seo_data:
                upsert_seo_metadata(page, **seo_data)
            count += 1

        self.stdout.write(self.style.SUCCESS(f"    ✓ {count} pages created and published"))

    # ── BLOG CATEGORIES, TAGS, POSTS ──────────────────────────────────────────
    def _seed_blogs(self, admin):
        from apps.blogs.models import Blog, BlogCategory, BlogTag
        from apps.blogs.services import create_blog
        from apps.seo.services import upsert_seo_metadata
        self.stdout.write("  → Blog categories, tags, and posts…")
        if Blog.all_objects.exists():
            self.stdout.write("    (already seeded, skipping)")
            return

        categories = {}
        for name in ["Clinic Growth", "Healthcare Marketing", "Digital Transformation",
                     "Patient Experience", "SEO for Doctors", "Product Updates",
                     "Practice Management", "Company News"]:
            cat = BlogCategory.all_objects.create(name=name, created_by=admin)
            categories[name] = cat

        tags = {}
        for name in ["CuraCMS", "CuraLabs", "CuraSuite", "Appointment Booking",
                     "SEO", "Digital Marketing", "Patient Engagement",
                     "Clinic Management", "Pathology", "Telemedicine",
                     "India Healthcare", "Online Presence"]:
            tag = BlogTag.objects.create(name=name)
            tags[name] = tag

        blog_posts = [
            {
                "title": "Why Every Doctor Needs a Professional Website in 2025",
                "category": "Clinic Growth",
                "tags": ["CuraCMS", "SEO", "Online Presence"],
                "excerpt": "In a world where patients search online before booking, a professional website isn't optional for doctors — it's essential for practice growth.",
                "content": """<h2>The New Patient Journey</h2>
<p>Before a patient calls your clinic, they've already Googled you. They've checked your reviews, scanned your website, and formed an opinion about your practice — all before you've had a chance to speak with them.</p>
<p>Studies show that <strong>over 70% of patients</strong> research doctors online before making an appointment. If your digital presence is weak, you're losing patients to competitors who invested in their online presence.</p>
<h2>What Patients Look for Online</h2>
<ul>
<li>Your qualifications and specialisation</li>
<li>Clinic location, timings, and contact details</li>
<li>Patient reviews and testimonials</li>
<li>Ability to book appointments online</li>
<li>Health content that demonstrates your expertise</li>
</ul>
<h2>What a Professional Website Does for Your Practice</h2>
<p>A well-designed medical website isn't just an online brochure. It's a patient acquisition and trust-building engine that works 24/7.</p>
<h3>1. First Impressions Matter</h3>
<p>Your website is often the first interaction a patient has with your brand. A professional, fast, and mobile-friendly site immediately builds trust.</p>
<h3>2. Online Appointment Booking</h3>
<p>Allowing patients to book appointments directly from your website reduces phone call volume and fills your schedule automatically — even outside working hours.</p>
<h3>3. Ranking on Google</h3>
<p>A properly optimised website helps you appear in local search results when patients search for a doctor in your specialty and city.</p>
<h2>Getting Started with CuraCMS</h2>
<p>CuraCMS is a healthcare-specific website platform designed for doctors and clinics. It includes everything — appointment booking, patient CRM, blog engine, SEO tools, and AI chatbot — in one easy-to-use platform.</p>
<p>Most CuraCMS websites go live within 7–14 days. No technical knowledge required.</p>""",
                "is_featured": True,
                "seo": {
                    "seo_title": "Why Every Doctor Needs a Professional Website in 2025 | CuraSuite Blog",
                    "meta_description": "70% of patients research doctors online before booking. Learn why a professional website is essential for practice growth in 2025.",
                    "focus_keyword": "doctor website professional online presence India",
                    "schema_type": "BlogPosting",
                },
            },
            {
                "title": "How Online Appointment Booking Increases Patient Satisfaction",
                "category": "Patient Experience",
                "tags": ["Appointment Booking", "Patient Engagement", "CuraCMS"],
                "excerpt": "Discover how letting patients book appointments online reduces no-shows, increases bookings, and dramatically improves patient satisfaction scores.",
                "content": """<h2>The Problem with Phone-Only Booking</h2>
<p>If your clinic only accepts appointments by phone, you're creating friction for patients. People are busy. They want to book when it's convenient for them — often outside your clinic's working hours.</p>
<p>Research shows that <strong>40% of appointments</strong> are booked outside working hours. Without an online booking system, you're missing nearly half your potential patients.</p>
<h2>Benefits of Online Appointment Booking</h2>
<h3>For Patients</h3>
<ul>
<li>Book anytime, 24/7 — no waiting on hold</li>
<li>Choose their preferred doctor and time slot</li>
<li>Receive automatic confirmation and reminders</li>
<li>Reschedule or cancel easily without calling</li>
</ul>
<h3>For Your Practice</h3>
<ul>
<li>Reduced call volume — staff can focus on in-clinic care</li>
<li>Fewer no-shows with automated reminders</li>
<li>Better schedule management and visibility</li>
<li>Increased bookings from digital-first patients</li>
</ul>
<h2>Measuring the Impact</h2>
<p>CuraCMS clients who enabled online booking reported an average 45% increase in appointment volume within 90 days. Phone call volume dropped by 60%, freeing reception staff for higher-value tasks.</p>
<h2>Getting Started</h2>
<p>CuraCMS includes a fully integrated appointment booking system that works directly from your website. Patients see your available slots in real time and confirm with a click.</p>""",
                "is_featured": True,
                "seo": {
                    "seo_title": "Online Appointment Booking & Patient Satisfaction | CuraSuite",
                    "meta_description": "Online appointment booking increases bookings by 45% and reduces no-shows. Learn how CuraCMS makes it easy for clinics and doctors.",
                    "focus_keyword": "online appointment booking clinic India",
                    "schema_type": "BlogPosting",
                },
            },
            {
                "title": "Digital Transformation for Pathology Labs: A Complete Guide",
                "category": "Digital Transformation",
                "tags": ["CuraLabs", "Pathology", "Digital Transformation"],
                "excerpt": "A step-by-step guide to digitizing your pathology lab — from online test booking to automated report delivery and patient communication.",
                "content": """<h2>The State of Pathology Labs in India</h2>
<p>India's diagnostic industry is growing rapidly, but many pathology labs still operate with outdated, paper-heavy processes. Patients call to ask for results. Staff spend hours on the phone. Reports are emailed as PDFs from Gmail.</p>
<p>There's a better way.</p>
<h2>What Digital Transformation Looks Like for a Lab</h2>
<h3>Phase 1: Digital Presence</h3>
<p>Start with a professional website that showcases your test catalogue, accreditations, and contact information. Patients need to find you online before they can choose you.</p>
<h3>Phase 2: Online Booking</h3>
<p>Allow patients to book test appointments and home collection slots directly from your website. No phone calls required.</p>
<h3>Phase 3: Digital Reports</h3>
<p>Enable secure, OTP-verified report downloads from your website. Patients get their results the moment they're ready — without calling.</p>
<h3>Phase 4: Patient Communication</h3>
<p>Automated WhatsApp and SMS notifications for booking confirmations, sample collection reminders, and report availability alerts.</p>
<h2>The CuraLabs Advantage</h2>
<p>CuraLabs is built specifically for Indian pathology labs. It covers all four phases in one integrated platform, with an implementation timeline of 7–14 days.</p>""",
                "is_featured": True,
                "seo": {
                    "seo_title": "Digital Transformation for Pathology Labs: Complete Guide | CuraSuite",
                    "meta_description": "Step-by-step guide to digitizing your pathology lab with online booking, report downloads, and patient notifications using CuraLabs.",
                    "focus_keyword": "pathology lab digital transformation India",
                    "schema_type": "BlogPosting",
                },
            },
            {
                "title": "SEO for Doctors: How to Rank on Google in Your City",
                "category": "SEO for Doctors",
                "tags": ["SEO", "Digital Marketing", "Online Presence", "India Healthcare"],
                "excerpt": "A practical SEO guide for doctors and clinics — learn how to appear on page 1 of Google when patients search for a doctor in your specialty.",
                "content": """<h2>Why SEO Matters for Doctors</h2>
<p>When someone in your city searches "best cardiologist in Pune" or "dental clinic near me," are you appearing in the results? If not, you're invisible to a huge segment of potential patients.</p>
<p>Search Engine Optimisation (SEO) is the process of improving your website so it appears higher in Google results for relevant searches.</p>
<h2>The Basics of Local SEO for Clinics</h2>
<h3>1. Google Business Profile</h3>
<p>Claim and optimise your Google Business Profile. This is the listing that appears in Google Maps and the local pack. Include your clinic address, hours, phone number, and photos.</p>
<h3>2. Location-Specific Keywords</h3>
<p>Include your city and specialty in your website content. "Orthopedic surgeon Dehradun" is more valuable than just "orthopedic surgeon."</p>
<h3>3. Patient Reviews</h3>
<p>Google rewards businesses with more and better reviews. Encourage satisfied patients to leave a Google review.</p>
<h3>4. Fast, Mobile-Friendly Website</h3>
<p>Google penalises slow websites and websites that aren't mobile-friendly. CuraCMS is optimised for speed and works perfectly on all devices.</p>
<h3>5. Healthcare Content</h3>
<p>Publishing helpful health articles on your website blog helps Google understand what you specialise in and improves your rankings over time.</p>
<h2>How CuraCMS Helps with SEO</h2>
<p>CuraCMS includes built-in SEO tools — meta tags, schema markup, sitemap generation, Google Search Console integration, and a blog engine. You don't need a separate SEO plugin or developer.</p>""",
                "is_featured": False,
                "seo": {
                    "seo_title": "SEO for Doctors: How to Rank on Google in Your City | CuraSuite Blog",
                    "meta_description": "Practical SEO tips for doctors and clinics in India. Learn how to appear on page 1 of Google when patients search for your specialty.",
                    "focus_keyword": "SEO for doctors India rank Google",
                    "schema_type": "BlogPosting",
                },
            },
            {
                "title": "Clinic Management Software Buying Guide for Indian Clinics",
                "category": "Practice Management",
                "tags": ["CuraSuite", "Clinic Management", "India Healthcare"],
                "excerpt": "Everything you need to know before buying clinic management software — features to look for, questions to ask, and red flags to avoid.",
                "content": """<h2>Do You Really Need Clinic Management Software?</h2>
<p>If your clinic uses paper registers, WhatsApp for appointments, and Excel for billing — you're losing time, money, and patients. Clinic management software digitizes these workflows and gives you real-time visibility into your practice.</p>
<h2>Key Features to Look For</h2>
<h3>Patient Registration</h3>
<p>Digital patient records with complete visit history, contact details, and medical notes.</p>
<h3>Appointment Management</h3>
<p>Doctor-wise calendars, slot configuration, and appointment reminders.</p>
<h3>Billing and Invoicing</h3>
<p>Generate invoices, track payments, and manage outstanding balances with ease.</p>
<h3>Prescription Management</h3>
<p>Digital prescriptions with a medicine database and printable letterhead templates.</p>
<h3>Reports and Analytics</h3>
<p>Revenue reports, patient statistics, and doctor productivity insights.</p>
<h2>Questions to Ask the Vendor</h2>
<ul>
<li>How long does implementation take?</li>
<li>Is training included in the price?</li>
<li>Can we try it before committing?</li>
<li>What happens to our data if we cancel?</li>
<li>Is the software cloud-based or installed locally?</li>
</ul>
<h2>Why CuraSuite CMS Stands Out</h2>
<p>CuraSuite CMS is designed for Indian clinics — it understands the workflow, the compliance requirements, and the patient expectations of the Indian market. Implementation takes 14–21 days and includes full staff training.</p>""",
                "is_featured": False,
                "seo": {
                    "seo_title": "Clinic Management Software Buying Guide | CuraSuite Blog",
                    "meta_description": "Complete buying guide for clinic management software in India. Features to look for, questions to ask vendors, and how CuraSuite CMS compares.",
                    "focus_keyword": "clinic management software buying guide India",
                    "schema_type": "BlogPosting",
                },
            },
            {
                "title": "How AI Is Transforming Healthcare in India",
                "category": "Digital Transformation",
                "tags": ["Digital Transformation", "India Healthcare", "Patient Engagement"],
                "excerpt": "AI is no longer science fiction in Indian healthcare. From diagnostic assistance to patient chatbots, here's how AI is reshaping the industry.",
                "content": """<h2>The AI Revolution in Indian Healthcare</h2>
<p>Artificial intelligence is transforming every industry, and healthcare is no exception. In India, where the doctor-to-patient ratio remains a challenge, AI tools are helping bridge the gap.</p>
<h2>Key AI Applications in Healthcare</h2>
<h3>AI-Powered Chatbots</h3>
<p>Healthcare chatbots can answer patient queries 24/7 — clinic timings, appointment availability, test preparation instructions, and general health information. CuraSuite's AI chatbot is powered by Google Gemini and can be customised with your clinic's specific information.</p>
<h3>Diagnostic Assistance</h3>
<p>AI tools are helping pathologists analyse slides faster and with greater accuracy. Early detection of conditions like diabetic retinopathy and certain cancers is improving outcomes.</p>
<h3>Predictive Analytics</h3>
<p>Clinic management systems with AI can predict appointment no-shows, identify at-risk patients, and suggest optimal scheduling to maximise revenue.</p>
<h3>Content Generation</h3>
<p>AI tools are helping doctors create patient education content — blogs, health tips, and social media posts — in a fraction of the time.</p>
<h2>How CuraSuite Uses AI</h2>
<p>CuraSuite integrates AI thoughtfully — our chatbot uses a 4-model Gemini fallback chain to ensure reliability, and our admin panel includes AI-assisted SEO suggestions for meta descriptions and content improvement.</p>""",
                "is_featured": False,
                "seo": {
                    "seo_title": "How AI Is Transforming Healthcare in India | CuraSuite Blog",
                    "meta_description": "From diagnostic AI to patient chatbots — explore how artificial intelligence is reshaping healthcare delivery in India.",
                    "focus_keyword": "AI healthcare India transformation",
                    "schema_type": "BlogPosting",
                },
            },
            {
                "title": "CuraLabs Launch — Digital Platform for Pathology Labs is Here",
                "category": "Product Updates",
                "tags": ["CuraLabs", "Pathology"],
                "excerpt": "We're excited to announce the official launch of CuraLabs — our digital experience platform built exclusively for pathology laboratories and diagnostic centres in India.",
                "content": """<h2>Introducing CuraLabs</h2>
<p>Today, PhoenixRise Interactive is proud to announce the official launch of <strong>CuraLabs</strong> — a digital experience platform built exclusively for pathology laboratories and diagnostic centres across India.</p>
<h2>What CuraLabs Offers</h2>
<p>CuraLabs gives pathology labs everything they need to create a modern digital presence:</p>
<ul>
<li><strong>Digital Test Catalogue</strong> — Showcase all your tests with prices, preparation instructions, and turnaround times</li>
<li><strong>Online Test Booking</strong> — Let patients book tests directly from your website, 24/7</li>
<li><strong>Home Collection Management</strong> — Accept home collection requests with preferred slots and addresses</li>
<li><strong>Secure Report Download</strong> — OTP-verified report access for patients</li>
<li><strong>Patient Notifications</strong> — Automated WhatsApp and SMS for confirmations and report alerts</li>
<li><strong>Patient CRM</strong> — Manage patient records and communication history</li>
</ul>
<h2>Pricing</h2>
<p>CuraLabs Basic starts at ₹14,999/year. The Growth plan with full features is ₹29,999/year. Enterprise pricing is available for diagnostic chains with multiple branches.</p>
<h2>Get Started</h2>
<p>Book a free demo today and see CuraLabs in action. Most labs are live within 7–14 days of signup.</p>""",
                "is_featured": True,
                "seo": {
                    "seo_title": "CuraLabs Launch — Digital Platform for Pathology Labs | CuraSuite",
                    "meta_description": "Announcing CuraLabs — online test booking, report download, home collection management, and patient notifications for pathology labs in India.",
                    "focus_keyword": "CuraLabs pathology lab digital platform launch",
                    "schema_type": "BlogPosting",
                },
            },
            {
                "title": "10 Website Mistakes Healthcare Providers Make (And How to Fix Them)",
                "category": "Healthcare Marketing",
                "tags": ["CuraCMS", "Online Presence", "Digital Marketing"],
                "excerpt": "Is your clinic website costing you patients? Here are the 10 most common website mistakes healthcare providers make and how to fix each one.",
                "content": """<h2>Your Website Is Either Winning or Losing Patients</h2>
<p>Most clinic websites make the same critical mistakes. These errors cost clinics real patients every single day. Here are the top 10.</p>
<h3>1. No Mobile Optimisation</h3>
<p>Over 80% of healthcare searches happen on mobile phones. If your website doesn't work well on mobile, you're losing 8 out of 10 visitors immediately.</p>
<h3>2. Slow Loading Speed</h3>
<p>Google research shows that 53% of mobile users abandon a website that takes more than 3 seconds to load. Every second of delay costs you patients.</p>
<h3>3. No Online Appointment Booking</h3>
<p>If patients can't book online, they'll find a clinic that allows it. Frictionless booking is now a baseline expectation.</p>
<h3>4. Missing Contact Information</h3>
<p>Your phone number, address, and business hours should be visible on every page — not just on the contact page.</p>
<h3>5. No Patient Reviews</h3>
<p>Patients trust other patients. A website without testimonials feels unverified. Display reviews prominently.</p>
<h3>6. No SSL Certificate</h3>
<p>An unsecured website (http:// instead of https://) triggers browser warnings and signals untrustworthiness to both patients and Google.</p>
<h3>7. Generic Stock Photos</h3>
<p>Photos of your actual clinic and team build far more trust than generic stock images of doctors and stethoscopes.</p>
<h3>8. No Blog or Health Content</h3>
<p>Without fresh content, your website has nothing new to tell Google. Regular blog posts improve rankings and demonstrate expertise.</p>
<h3>9. Poor Navigation</h3>
<p>If patients can't find your services, timings, or contact details within 5 seconds, they'll leave.</p>
<h3>10. No Clear Call to Action</h3>
<p>Every page should tell visitors exactly what to do next — Book an Appointment, Call Us, or Learn More.</p>
<h2>The CuraCMS Fix</h2>
<p>CuraCMS addresses all 10 of these issues out of the box — fast loading, mobile-first, appointment booking, SEO, reviews display, SSL, and clear CTAs on every page.</p>""",
                "is_featured": False,
                "seo": {
                    "seo_title": "10 Website Mistakes Healthcare Providers Make | CuraSuite Blog",
                    "meta_description": "Is your clinic website losing patients? Discover the 10 most common healthcare website mistakes and how to fix them with CuraCMS.",
                    "focus_keyword": "healthcare website mistakes clinics India",
                    "schema_type": "BlogPosting",
                },
            },
        ]

        count = 0
        for data in blog_posts:
            seo_data = data.pop("seo", {})
            tag_names = data.pop("tags", [])
            cat_name = data.pop("category")
            is_featured = data.pop("is_featured", False)
            category = categories.get(cat_name)
            blog = create_blog(category=category, created_by=admin, **data)
            blog.is_featured = is_featured
            tag_objs = [tags[t] for t in tag_names if t in tags]
            if tag_objs:
                blog.tags.set(tag_objs)
            blog.save()
            blog.publish(published_by=admin)
            if seo_data:
                upsert_seo_metadata(blog, **seo_data)
            count += 1

        self.stdout.write(self.style.SUCCESS(
            f"    ✓ {len(categories)} categories, {len(tags)} tags, {count} blog posts (4 featured)"))

    # ── REDIRECTS ─────────────────────────────────────────────────────────────
    def _seed_redirects(self):
        from apps.seo.models import Redirect
        self.stdout.write("  → Redirects…")
        if Redirect.objects.exists():
            self.stdout.write("    (already seeded, skipping)")
            return
        redirects = [
            ("/old-website/",         "/",                     "301", "Root redirect from old site"),
            ("/services/",            "/products/",            "301", "Old services page → products"),
            ("/appointment/",         "/contact/",             "301", "Old appointment page → contact"),
            ("/lab/",                 "/products/curalabs/",   "301", "Short lab URL"),
            ("/cms/",                 "/products/curacms/",    "301", "Short CMS URL"),
            ("/clinic/",              "/products/curasuite/",  "301", "Short clinic URL"),
            ("/blog/category/news/",  "/blog/",                "302", "Temporary news redirect"),
        ]
        for old, new, rtype, note in redirects:
            Redirect.objects.create(old_path=old, new_path=new, redirect_type=rtype, note=note)
        self.stdout.write(self.style.SUCCESS(f"    ✓ {len(redirects)} URL redirects"))

    # ── CRM ───────────────────────────────────────────────────────────────────
    def _seed_crm(self, admin):
        from apps.crm.services import capture_lead, create_demo_request, update_lead_status
        from apps.crm.models import Lead, LeadNote
        self.stdout.write("  → CRM leads, notes, demo requests…")
        if Lead.objects.exists():
            self.stdout.write("    (already seeded, skipping)")
            return

        now = timezone.now()
        leads_data = [
            # (name, email, phone, org, city, product, source, business_type, status, days_ago, add_demo, add_note)
            ("Dr. Anjali Kapoor",   "anjali.kapoor@gmail.com",   "9876543210", "Kapoor Clinic",          "Dehradun",   "CuraCMS",   "organic",      "single_doctor",   "qualified",       5, True,  "Very interested in the blog feature. Send pricing PDF."),
            ("Dr. Rohit Sharma",    "rohit.sharma@example.com",  "9812345678", "Sharma Dental",          "Jaipur",     "CuraCMS",   "google_ads",   "dental",          "demo_scheduled",  3, True,  "Demo scheduled for next Tuesday. Send prep guide."),
            ("Mr. Suresh Patel",    "suresh.patel@mehtadiag.in", "9923456789", "Mehta Diagnostics",      "Ahmedabad",  "CuraLabs",  "demo_form",    "diagnostic",      "won",             20, True, "Signed up for Growth plan. Onboarding in progress."),
            ("Dr. Priya Nair",      "priya.nair@example.com",    "8834567890", "Nair Ortho Centre",      "Kochi",      "CuraSuite", "referral",     "multi_specialty", "proposal_sent",   7, True,  "Proposal sent. Follow up end of week."),
            ("Dr. Vikram Singh",    "vikram.singh@example.com",  "9745678901", "Singh Multispecialty",   "Lucknow",    "CuraCMS",   "meta_ads",     "multi_specialty", "contacted",       2, False, "Called — interested but budget decision in Q3."),
            ("Ms. Kavitha Reddy",   "kavitha.reddy@example.com", "8856789012", "Reddy Lab Network",      "Hyderabad",  "CuraLabs",  "organic",      "pathology_lab",   "new",             1, False, ""),
            ("Dr. Arun Kumar",      "arun.kumar@example.com",    "9767890123", "Kumar Physiotherapy",    "Chennai",    "CuraCMS",   "contact_form", "single_doctor",   "new",             0, False, ""),
            ("Dr. Meera Joshi",     "meera.joshi@example.com",   "9778901234", "Joshi Womens Clinic",    "Pune",       "CuraCMS",   "organic",      "single_doctor",   "contacted",       4, False, "Called. Wants demo with team lead present."),
            ("Mr. Deepak Malhotra", "deepak.malhotra@labs.com",  "9889012345", "Malhotra Diagnostic Lab","Delhi",      "CuraLabs",  "google_ads",   "diagnostic",      "qualified",       6, True,  "NABL accredited lab, wants full test catalogue."),
            ("Dr. Sunita Verma",    "sunita.verma@example.com",  "9890123456", "Verma Dental Studio",    "Bangalore",  "CuraCMS",   "referral",     "dental",          "negotiation",     10, True, "Negotiating on pricing. Offered 2-month free trial extension."),
            ("Dr. Ravi Tiwari",     "ravi.tiwari@example.com",   "9901234567", "Tiwari Eye Care",        "Varanasi",   "CuraCMS",   "organic",      "single_doctor",   "lost",            15, False,"Went with competitor. Price was deciding factor."),
            ("Ms. Lalita Singh",    "lalita.singh@radiant.com",  "9912345678", "Radiant Diagnostics",    "Indore",     "CuraLabs",  "meta_ads",     "pathology_lab",   "new",             0, False, ""),
            ("Dr. Kiran Rao",       "kiran.rao@example.com",     "9823456781", "Rao Physiotherapy Hub",  "Mysore",     "CuraCMS",   "organic",      "single_doctor",   "new",             0, False, ""),
            ("Dr. Faraz Ahmed",     "faraz.ahmed@example.com",   "9934567892", "Ahmed ENT Clinic",       "Lucknow",    "CuraSuite", "demo_form",    "single_doctor",   "demo_scheduled",  2, True, "Interested in prescription management specifically."),
            ("Dr. Nisha Gupta",     "nisha.gupta@example.com",   "9845678903", "Gupta Fertility Centre", "Chandigarh", "CuraCMS",   "referral",     "multi_specialty", "qualified",       8, True, "Referred by Dr. Anjali Kapoor. Ready to proceed."),
        ]

        from apps.accounts.models import User
        staff = list(User.objects.filter(is_staff=True, is_superuser=False))

        created_count = 0
        demo_count = 0
        for row in leads_data:
            name, email, phone, org, city, product, source, biz_type, status, days_ago, add_demo, note_text = row
            lead, created = capture_lead(
                full_name=name, email=email, phone=phone,
                organization=org, city=city, product_interest=product,
                source=source, business_type=biz_type,
            )
            if created:
                # Backdate created_at
                Lead.objects.filter(pk=lead.pk).update(
                    created_at=now - timedelta(days=days_ago),
                    updated_at=now - timedelta(days=max(0, days_ago - 1)),
                )
                if staff:
                    lead.assigned_to = random.choice(staff)
                    lead.save(update_fields=["assigned_to"])

                if status != "new":
                    update_lead_status(lead, status)

                if note_text:
                    LeadNote.objects.create(
                        lead=lead, content=note_text, author=admin,
                    )

                if add_demo:
                    create_demo_request(
                        lead=lead, product_interest=product,
                        preferred_date=(timezone.now() + timedelta(days=random.randint(2, 10))).date(),
                        preferred_time=random.choice(["10:00 AM", "11:00 AM", "2:00 PM", "4:00 PM"]),
                    )
                    demo_count += 1

                created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"    ✓ {created_count} leads ({demo_count} with demo requests, "
            f"various pipeline stages)"))

    # ── NEWSLETTER ────────────────────────────────────────────────────────────
    def _seed_newsletter(self):
        from apps.newsletter.models import NewsletterSubscriber, NewsletterCampaign, NewsletterSend
        self.stdout.write("  → Newsletter subscribers and campaigns…")
        if NewsletterSubscriber.objects.exists():
            self.stdout.write("    (already seeded, skipping)")
            return

        now = timezone.now()

        # Subscribers
        subscribers_data = [
            ("dr.anjali@clinic.com",   "Anjali",   "confirmed",    "website_footer", 30),
            ("suresh.lab@diag.in",     "Suresh",   "confirmed",    "website_footer", 25),
            ("priya.sharma@gmail.com", "Priya",    "confirmed",    "blog",           20),
            ("rohit.dental@example.com","Rohit",   "confirmed",    "website_footer", 18),
            ("meera.clinic@yahoo.com", "Meera",    "confirmed",    "google_ads",     15),
            ("vikram.doc@gmail.com",   "Vikram",   "confirmed",    "website_footer", 12),
            ("kavitha.lab@example.com","Kavitha",  "confirmed",    "blog",           10),
            ("arun.physio@gmail.com",  "Arun",     "confirmed",    "website_footer",  8),
            ("sunita.dental@mail.com", "Sunita",   "confirmed",    "referral",        7),
            ("deepak.diag@labs.com",   "Deepak",   "confirmed",    "google_ads",      5),
            ("ravi.eye@example.com",   "Ravi",     "confirmed",    "website_footer",  4),
            ("nisha.fertility@dr.com", "Nisha",    "confirmed",    "website_footer",  3),
            ("faraz.ent@example.com",  "Faraz",    "confirmed",    "blog",            2),
            ("lalita.radiant@labs.in", "Lalita",   "pending",      "website_footer",  1),
            ("kiran.physio@example.com","Kiran",   "pending",      "website_footer",  0),
            ("test.unsub@example.com", "Test",     "unsubscribed", "website_footer", 25),
        ]

        subs = []
        for email, fname, status, source, days_ago in subscribers_data:
            sub = NewsletterSubscriber(
                email=email, first_name=fname,
                status=status, source=source,
            )
            if status == "confirmed":
                sub.confirmed_at = now - timedelta(days=days_ago)
            sub.save()
            subs.append(sub)

        # Campaign 1 — sent
        campaign1 = NewsletterCampaign.objects.create(
            subject="Welcome to CuraSuite Insights — Healthcare Technology for Your Practice",
            preview_text="Your guide to growing your practice digitally starts here.",
            content_html="""<h1 style="color:#111827;">Welcome to CuraSuite Insights 👋</h1>
<p>Thank you for subscribing! You're now part of a community of healthcare professionals across India who are embracing digital transformation.</p>
<p>In this newsletter, you'll receive:</p>
<ul>
<li>📈 Clinic growth strategies that work</li>
<li>💡 Healthcare marketing tips and SEO guides</li>
<li>🚀 CuraSuite product updates and new features</li>
<li>📖 Case studies from Indian clinics and labs</li>
</ul>
<p>We publish twice a month — no spam, ever.</p>
<p style="margin-top:32px;"><a href="https://curasuite.com/products/" style="background:#111827;color:white;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600;">Explore Our Products →</a></p>
<p style="color:#9CA3AF;font-size:12px;margin-top:48px;">PhoenixRise Interactive Pvt. Ltd. | hello@curasuite.com</p>""",
            content_text="Welcome to CuraSuite Insights! Thank you for subscribing. Visit curasuite.com to explore our products.",
            status="sent",
            sent_at=now - timedelta(days=20),
            total_sent=12,
            total_opens=9,
            total_clicks=4,
        )

        # Campaign 2 — draft
        NewsletterCampaign.objects.create(
            subject="How CuraLabs Is Helping Pathology Labs Across India Go Digital",
            preview_text="Real results from 3 labs that transformed with CuraLabs.",
            content_html="""<h1 style="color:#111827;">CuraLabs — Real Results from Real Labs</h1>
<p>Over the past quarter, we've helped pathology labs across India transform their patient experience. Here are three stories.</p>
<h2>Kumar Diagnostics, Hyderabad</h2>
<p>"Our phone call volume dropped by 60% after enabling online booking. Patients now book and receive reports without ever calling us." — Mr. Suresh Kumar, Lab Director</p>
<h2>Mehta Diagnostic Centre, Ahmedabad</h2>
<p>"The home collection feature was a game-changer. We manage collection slots efficiently and confirmation WhatsApps go out automatically." — Dr. Anjali Mehta</p>
<h2>Ready to Transform Your Lab?</h2>
<p><a href="https://curasuite.com/products/curalabs/" style="background:#16A34A;color:white;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600;">Explore CuraLabs →</a></p>""",
            content_text="CuraLabs is helping pathology labs across India. Read real results at curasuite.com/products/curalabs/",
            status="draft",
        )

        self.stdout.write(self.style.SUCCESS(
            f"    ✓ {len(subscribers_data)} subscribers, 2 campaigns (1 sent, 1 draft)"))
