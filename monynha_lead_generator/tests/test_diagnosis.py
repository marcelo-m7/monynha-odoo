from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestMonynhaDiagnosis(TransactionCase):
    def test_local_rules_create_append_only_completed_diagnosis(self):
        lead = self.env["crm.lead"].create({"name": "Discovery fixture", "email_from": "fixture@example.com", "monynha_revenue_model": "service", "monynha_decision_profile": "solo", "monynha_struggle": "We manually repeat spreadsheet work across sales and operations every day."})
        first = lead._monynha_create_diagnosis()
        second = lead._monynha_create_diagnosis()
        self.assertEqual(first.state, "completed")
        self.assertEqual(second.state, "completed")
        self.assertNotEqual(first, second)
        self.assertGreaterEqual(first.automation_potential, 70)
        self.assertEqual(lead.monynha_diagnosis_count, 2)

    def test_unknown_provider_fails_without_modifying_lead(self):
        lead = self.env["crm.lead"].create({"name": "Provider fixture"})
        diagnosis = lead._monynha_create_diagnosis(provider="missing-provider")
        self.assertEqual(diagnosis.state, "failed")
        self.assertTrue(lead.exists())
