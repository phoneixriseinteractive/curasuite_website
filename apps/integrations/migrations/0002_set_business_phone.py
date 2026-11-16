"""
Set the business phone / WhatsApp number to +91 88828 14698.

SiteSettings.whatsapp_phone drives every number shown on the site (contact page, footer,
WhatsApp button, landing-page call links); SocialLinks.whatsapp_link is the footer/social
WhatsApp URL. The old placeholder number is also replaced in page body text.

Reversing is a no-op: the previous values were placeholders.
"""

from django.db import migrations

PHONE = "918882814698"  # international format without "+", as the field expects
OLD_TEXT_NUMBERS = ["+91 98765 43210", "+91-98765-43210", "+919876543210"]
NEW_TEXT_NUMBER = "+91 88828 14698"


def forwards(apps, schema_editor):
    SiteSettings = apps.get_model("integrations", "SiteSettings")
    Integration = apps.get_model("integrations", "Integration")
    SocialLinks = apps.get_model("settings_app", "SocialLinks")
    Page = apps.get_model("pages", "Page")

    # Both are pk=1 singletons (see their .load()); create the row if it doesn't exist yet.
    SiteSettings._base_manager.update_or_create(pk=1, defaults={"whatsapp_phone": PHONE})
    SocialLinks._base_manager.update_or_create(pk=1, defaults={"whatsapp_link": f"https://wa.me/{PHONE}"})

    # The WhatsApp Business integration also keeps a copy of the number in its config.
    for integration in Integration._base_manager.filter(provider="whatsapp"):
        if (integration.config or {}).get("phone") != PHONE:
            integration.config = {**(integration.config or {}), "phone": PHONE}
            integration.save(update_fields=["config"])

    for page in Page._base_manager.filter(content__contains="98765"):
        content = page.content
        for old in OLD_TEXT_NUMBERS:
            content = content.replace(old, NEW_TEXT_NUMBER)
        if content != page.content:
            page.content = content
            page.save(update_fields=["content"])


class Migration(migrations.Migration):

    dependencies = [
        ("integrations", "0001_initial"),
        ("settings_app", "0002_testimonial_specialty"),
        ("pages", "0002_alter_page_template"),
    ]

    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]
