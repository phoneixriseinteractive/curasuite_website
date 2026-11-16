"""
CuraSuite — Static marketing copy for product detail pages.

Product-specific sections that aren't (yet) editable in /manage/ live here so
the template stays markup-only. ``get_page_content(slug)`` returns extra
template context for products/product_detail.html; products without an entry
get ``{}`` and render the generic layout.
"""

CURACMS = {
    "cms_templates": [
        {"name": "General Physician", "icon": "stethoscope",
         "description": "Consultation hours, conditions treated, doctor credentials and one-tap booking."},
        {"name": "Dental Clinic", "icon": "sparkles",
         "description": "Treatment pages for implants, aligners and root canals, with before/after galleries."},
        {"name": "Physiotherapy & Rehab", "icon": "users",
         "description": "Condition-based service pages, home-visit enquiries and session packages."},
        {"name": "Skin & Hair Clinic", "icon": "eye",
         "description": "Procedure showcases, FAQs and consultation booking for dermatology practices."},
        {"name": "Ayurveda & Wellness", "icon": "lightbulb",
         "description": "Therapy listings, wellness programmes and patient education articles."},
        {"name": "Multi-Speciality Clinic", "icon": "layers",
         "description": "Department pages, multiple doctor profiles and per-doctor booking calendars."},
    ],
    "cms_appointment_steps": [
        {"title": "Patient books online",
         "description": "From any page of your website, 24/7 — choosing the doctor, date and preferred time."},
        {"title": "Request lands in your dashboard",
         "description": "Every booking appears instantly in the admin panel with the patient’s details and concern."},
        {"title": "Your team confirms",
         "description": "Call or WhatsApp the patient in one click and update the status as confirmed."},
        {"title": "Follow up and track",
         "description": "The patient CRM keeps the history, so follow-ups and repeat visits never slip."},
    ],
    "cms_integrations": [
        {"name": "WhatsApp", "icon": "message-circle",
         "description": "Floating WhatsApp button with a pre-filled message so patients reach you instantly."},
        {"name": "Gemini AI Chatbot", "icon": "sparkles",
         "description": "Answers common patient questions on your website around the clock."},
        {"name": "Google Analytics 4 & Tag Manager", "icon": "bar-chart",
         "description": "Track visitors, booking requests and campaign performance."},
        {"name": "Google Search Console", "icon": "search",
         "description": "Verify your site and submit your sitemap so Google indexes new pages quickly."},
        {"name": "Meta Pixel & Microsoft Clarity", "icon": "target",
         "description": "Measure Facebook and Instagram ads and see how visitors use your pages."},
        {"name": "reCAPTCHA & Cloudflare Turnstile", "icon": "shield-check",
         "description": "Keep spam out of your contact and appointment forms."},
    ],
    "cms_migration_steps": [
        {"title": "Audit your current website",
         "description": "We list every page, article and image, and note which URLs already bring in traffic."},
        {"title": "Move your content",
         "description": "Pages, blog posts, doctor profiles and images are rebuilt on CuraCMS and checked for accuracy."},
        {"title": "Preserve your rankings",
         "description": "Old URLs are 301-redirected to their new pages and SEO titles and descriptions carried over."},
        {"title": "Switch over with no downtime",
         "description": "We point your domain to CuraCMS once you approve the new site, and submit the new sitemap to Google."},
    ],
    "cms_security": [
        {"title": "HTTPS everywhere", "icon": "lock",
         "description": "Every CuraCMS website is served over SSL, so form submissions are encrypted in transit."},
        {"title": "Role-based access", "icon": "users",
         "description": "Give doctors, front-desk staff and marketers only the permissions they need."},
        {"title": "Verified admin logins", "icon": "shield-check",
         "description": "Admin sign-in is protected with strong password hashing and emailed verification codes."},
        {"title": "Spam-protected forms", "icon": "alert-circle",
         "description": "CAPTCHA on appointment and contact forms keeps fake enquiries out of your CRM."},
        {"title": "Your data stays yours", "icon": "database",
         "description": "Patient enquiries are stored securely and never shared with third parties."},
        {"title": "Managed updates", "icon": "refresh-cw",
         "description": "We maintain and update the platform — no plugins to patch, no outdated themes."},
    ],
}

PAGE_CONTENT = {"curacms": CURACMS}


def get_page_content(slug: str) -> dict:
    return PAGE_CONTENT.get(slug, {})
