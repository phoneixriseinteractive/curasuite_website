"""CuraSuite — CRM Service Tests"""
from django.test import TestCase
from apps.crm.models import Lead, DemoRequest
from apps.crm.services import capture_lead, create_demo_request, update_lead_status


class CaptureLeadTest(TestCase):
    def test_creates_new_lead(self):
        lead, created = capture_lead(
            full_name="Dr. Anita Sharma", email="anita@clinic.com",
            phone="9876543210", organization="Sharma Clinic",
            city="Dehradun", source="contact_form",
        )
        self.assertTrue(created)
        self.assertEqual(lead.full_name, "Dr. Anita Sharma")
        self.assertEqual(lead.status, Lead.Status.NEW)

    def test_returns_existing_on_duplicate_email(self):
        capture_lead(full_name="Dr. A", email="same@clinic.com", source="contact_form")
        _, created = capture_lead(full_name="Dr. A Again", email="same@clinic.com", source="demo_form")
        self.assertFalse(created)
        self.assertEqual(Lead.objects.filter(email="same@clinic.com").count(), 1)

    def test_lead_activity_logged_on_create(self):
        lead, _ = capture_lead(full_name="Test", email="log@test.com", source="organic")
        self.assertEqual(lead.activities.count(), 1)
        self.assertEqual(lead.activities.first().activity_type, "created")


class DemoRequestTest(TestCase):
    def setUp(self):
        self.lead, _ = capture_lead(
            full_name="Dr. Raj", email="raj@lab.com", source="demo_form"
        )

    def test_creates_demo_request(self):
        demo = create_demo_request(lead=self.lead, product_interest="CuraLabs")
        self.assertEqual(demo.status, DemoRequest.Status.PENDING)
        self.assertEqual(demo.product_interest, "CuraLabs")

    def test_lead_status_updated_on_demo(self):
        create_demo_request(lead=self.lead, product_interest="CuraCMS")
        self.lead.refresh_from_db()
        self.assertEqual(self.lead.status, Lead.Status.DEMO_SCHEDULED)

    def test_activity_logged_on_demo(self):
        create_demo_request(lead=self.lead, product_interest="CuraSuite")
        self.assertGreater(self.lead.activities.count(), 1)


class UpdateLeadStatusTest(TestCase):
    def test_status_change_logged(self):
        lead, _ = capture_lead(full_name="Test", email="status@test.com", source="direct")
        update_lead_status(lead, Lead.Status.QUALIFIED)
        lead.refresh_from_db()
        self.assertEqual(lead.status, Lead.Status.QUALIFIED)
