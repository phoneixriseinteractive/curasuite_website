"""CuraSuite — Integrations Model Tests"""
from django.test import TestCase
from apps.integrations.models import Integration, SiteSettings


class SiteSettingsTest(TestCase):
    def test_singleton_load(self):
        s1 = SiteSettings.load()
        s2 = SiteSettings.load()
        self.assertEqual(s1.pk, s2.pk)
        self.assertEqual(SiteSettings.objects.count(), 1)

    def test_singleton_save(self):
        s = SiteSettings.load()
        s.whatsapp_phone = "919876543210"
        s.save()
        reloaded = SiteSettings.load()
        self.assertEqual(reloaded.whatsapp_phone, "919876543210")

    def test_defaults(self):
        s = SiteSettings.load()
        self.assertFalse(s.whatsapp_enabled)
        self.assertFalse(s.chatbot_enabled)
        self.assertFalse(s.captcha_enabled)


class IntegrationModelTest(TestCase):
    def test_create_integration(self):
        i = Integration.objects.create(
            provider=Integration.Provider.GOOGLE_ANALYTICS,
            is_enabled=True,
            config={"measurement_id": "G-XXXXXXX"},
        )
        self.assertIn("Google Analytics", str(i))

    def test_get_config(self):
        i = Integration.objects.create(
            provider=Integration.Provider.WHATSAPP,
            config={"phone": "919876543210"},
        )
        self.assertEqual(i.get_config("phone"), "919876543210")
        self.assertIsNone(i.get_config("missing_key"))
