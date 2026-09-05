import json

from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestMonynhaDiscoveryHttp(HttpCase):
    def _json_call(self, route, params, request_id=1):
        return self.url_open(
            route,
            data=json.dumps({"jsonrpc": "2.0", "method": "call", "params": params, "id": request_id}),
            headers={"Content-Type": "application/json"},
        ).json()["result"]

    def _submit_discovery(self, **overrides):
        params = {
            "email": "public-discovery@example.com",
            "brand_name": "Public Fixture",
            "no_brand": False,
            "revenue_model": "service",
            "decision_profile": "solo",
            "struggle": "We manually repeat spreadsheet work and need one operational system.",
            "website_url": "https://example.com",
            "instagram_url": "",
            "linkedin_url": "",
            "website_company": "",
        }
        params.update(overrides)
        return self._json_call("/monynha/discovery/submit", params)

    def test_start_page_renders(self):
        response = self.url_open("/start")
        self.assertEqual(response.status_code, 200)
        self.assertIn("PROJECT DISCOVERY", response.text)

    def test_public_submission_creates_lead_before_report(self):
        email = "public-discovery@example.com"
        payload = self._submit_discovery(email=email)
        self.assertTrue(payload["ok"])
        self.assertIn("/diagnosis/", payload["report_url"])
        lead = self.env["crm.lead"].search([("email_from", "=", email)], limit=1)
        self.assertTrue(lead)
        self.assertEqual(lead.monynha_diagnosis_ids.state, "completed")

    def test_public_report_shows_actionable_output_without_internal_payload(self):
        email = "public-report@example.com"
        payload = self._submit_discovery(email=email)
        response = self.url_open(payload["report_url"])
        self.assertEqual(response.status_code, 200)
        self.assertIn("Project Signal", response.text)
        self.assertIn("Opportunities", response.text)
        self.assertIn("Automate repetitive", response.text)
        self.assertIn("Recommended next move", response.text)
        self.assertNotIn("raw_payload", response.text)
        self.assertNotIn("error_message", response.text)
        self.assertNotIn(email, response.text)

    def test_public_followup_is_tokenized_and_idempotent(self):
        email = "public-followup@example.com"
        self._submit_discovery(email=email)
        lead = self.env["crm.lead"].search([("email_from", "=", email)], limit=1)
        diagnosis = lead.monynha_diagnosis_ids[:1]
        self.assertFalse(lead.monynha_followup_requested_at)

        first = self._json_call("/monynha/diagnosis/followup", {"token": diagnosis.public_token})
        self.assertTrue(first["ok"])
        self.assertFalse(first["already_requested"])
        self.assertTrue(lead.monynha_followup_requested_at)
        timestamp = lead.monynha_followup_requested_at

        second = self._json_call(
            "/monynha/diagnosis/followup",
            {"token": diagnosis.public_token},
            request_id=2,
        )
        self.assertTrue(second["ok"])
        self.assertTrue(second["already_requested"])
        self.assertEqual(lead.monynha_followup_requested_at, timestamp)

    def test_unknown_followup_token_does_not_mutate_leads(self):
        before = self.env["crm.lead"].search_count([("monynha_followup_requested_at", "!=", False)])
        payload = self._json_call("/monynha/diagnosis/followup", {"token": "not-a-real-token"})
        after = self.env["crm.lead"].search_count([("monynha_followup_requested_at", "!=", False)])
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error"], "not_found")
        self.assertEqual(after, before)

    def test_unknown_report_token_returns_not_found(self):
        response = self.url_open("/diagnosis/not-a-real-monynha-token")
        self.assertEqual(response.status_code, 404)
