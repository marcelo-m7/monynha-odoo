import json

from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestMonynhaDiscoveryHttp(HttpCase):
    def test_start_page_renders(self):
        response = self.url_open("/start")
        self.assertEqual(response.status_code, 200)
        self.assertIn("PROJECT DISCOVERY", response.text)

    def test_public_submission_creates_lead_before_report(self):
        email = "public-discovery@example.com"
        response = self.url_open("/monynha/discovery/submit", data=json.dumps({"jsonrpc": "2.0", "method": "call", "params": {"email": email, "brand_name": "Public Fixture", "no_brand": False, "revenue_model": "service", "decision_profile": "solo", "struggle": "We manually repeat spreadsheet work and need one operational system.", "website_url": "https://example.com", "instagram_url": "", "linkedin_url": "", "website_company": ""}, "id": 1}), headers={"Content-Type": "application/json"})
        payload = response.json()["result"]
        self.assertTrue(payload["ok"])
        self.assertIn("/diagnosis/", payload["report_url"])
        lead = self.env["crm.lead"].search([("email_from", "=", email)], limit=1)
        self.assertTrue(lead)
        self.assertEqual(lead.monynha_diagnosis_ids.state, "completed")
