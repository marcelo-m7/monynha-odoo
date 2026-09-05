from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestMonynhaDiagnosis(TransactionCase):
    def test_local_rules_create_append_only_completed_diagnosis(self):
        lead = self.env["crm.lead"].create({
            "name": "Discovery fixture",
            "email_from": "fixture@example.com",
            "monynha_revenue_model": "service",
            "monynha_decision_profile": "solo",
            "monynha_struggle": "We manually repeat spreadsheet work across sales and operations every day.",
        })
        first = lead._monynha_create_diagnosis()
        second = lead._monynha_create_diagnosis()
        self.assertEqual(first.state, "completed")
        self.assertEqual(second.state, "completed")
        self.assertNotEqual(first, second)
        self.assertGreaterEqual(first.automation_potential, 70)
        self.assertTrue(first.opportunities)
        self.assertEqual(first.recommended_action, "automate")
        self.assertEqual(lead.monynha_diagnosis_count, 2)
        self.assertEqual(lead.monynha_recommended_action, "automate")
        self.assertTrue(lead.monynha_opportunities)

    def test_latest_completed_diagnosis_drives_computed_signal_fields(self):
        lead = self.env["crm.lead"].create({
            "name": "Latest signal fixture",
            "monynha_revenue_model": "other",
            "monynha_decision_profile": "unclear",
            "monynha_struggle": "We need clarity on ownership and operating boundaries before building more tools.",
        })
        first = lead._monynha_create_diagnosis()
        self.assertEqual(first.recommended_action, "clarify")
        lead.write({
            "monynha_revenue_model": "service",
            "monynha_decision_profile": "solo",
            "monynha_struggle": "Manual spreadsheet duplication and repetitive work blocks delivery every day.",
        })
        second = lead._monynha_create_diagnosis()
        self.assertEqual(second.recommended_action, "automate")
        self.assertEqual(lead.monynha_recommended_action, "automate")
        self.assertEqual(lead.monynha_diagnosis_score, second.score)

    def test_followup_request_records_once_and_schedules_standard_activity(self):
        admin = self.env.ref("base.user_admin")
        lead = self.env["crm.lead"].create({
            "name": "Follow-up fixture",
            "email_from": "followup@example.com",
            "user_id": admin.id,
            "monynha_struggle": "Manual work needs a better operating flow.",
        })
        diagnosis = lead._monynha_create_diagnosis()
        self.assertFalse(lead.monynha_followup_requested_at)

        created = diagnosis.action_request_followup()
        self.assertTrue(created)
        self.assertTrue(lead.monynha_followup_requested_at)
        first_timestamp = lead.monynha_followup_requested_at
        activities = lead.activity_ids.filtered(
            lambda activity: activity.summary == "Monynha Project Signal follow-up"
        )
        self.assertEqual(len(activities), 1)
        self.assertEqual(activities.user_id, admin)
        messages = lead.message_ids.filtered(
            lambda message: "Project Signal follow-up requested" in (message.body or "")
        )
        self.assertTrue(messages)

        created_again = diagnosis.action_request_followup()
        self.assertFalse(created_again)
        self.assertEqual(lead.monynha_followup_requested_at, first_timestamp)
        self.assertEqual(
            len(lead.activity_ids.filtered(lambda activity: activity.summary == "Monynha Project Signal follow-up")),
            1,
        )

    def test_followup_without_responsible_user_is_recorded_without_arbitrary_activity(self):
        lead = self.env["crm.lead"].create({
            "name": "Unassigned follow-up fixture",
            "email_from": "unassigned@example.com",
            "user_id": False,
            "team_id": False,
        })
        diagnosis = lead._monynha_create_diagnosis()
        self.assertTrue(diagnosis.action_request_followup())
        self.assertTrue(lead.monynha_followup_requested_at)
        self.assertFalse(
            lead.activity_ids.filtered(lambda activity: activity.summary == "Monynha Project Signal follow-up")
        )

    def test_unknown_provider_fails_without_modifying_lead(self):
        lead = self.env["crm.lead"].create({"name": "Provider fixture"})
        diagnosis = lead._monynha_create_diagnosis(provider="missing-provider")
        self.assertEqual(diagnosis.state, "failed")
        self.assertTrue(lead.exists())
