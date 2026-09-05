from odoo import api, fields, models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    monynha_brand_name = fields.Char(string="Discovery Brand / Project")
    monynha_revenue_model = fields.Selection([("service", "Service"), ("product", "Product"), ("subscription", "Subscription / Recurring"), ("other", "Other")], string="Revenue Model")
    monynha_decision_profile = fields.Selection([("solo", "I do most things myself"), ("delegate", "I prefer to delegate execution"), ("sales_focus", "I am focused on selling"), ("unclear", "I am still figuring it out")], string="Operating Style")
    monynha_struggle = fields.Text(string="Primary Struggle")
    monynha_instagram_url = fields.Char(string="Instagram")
    monynha_linkedin_url = fields.Char(string="LinkedIn")
    monynha_discovery_version = fields.Char(default="1", readonly=True)
    monynha_discovery_completed_at = fields.Datetime(string="Discovery Completed At", readonly=True)
    monynha_diagnosis_ids = fields.One2many("monynha.lead.diagnosis", "lead_id", string="Monynha Diagnoses")
    monynha_diagnosis_count = fields.Integer(compute="_compute_monynha_diagnosis_count")
    monynha_diagnosis_score = fields.Integer(compute="_compute_monynha_latest_diagnosis")
    monynha_diagnosis_summary = fields.Text(compute="_compute_monynha_latest_diagnosis")

    @api.depends("monynha_diagnosis_ids")
    def _compute_monynha_diagnosis_count(self):
        for lead in self:
            lead.monynha_diagnosis_count = len(lead.monynha_diagnosis_ids)

    @api.depends("monynha_diagnosis_ids.state", "monynha_diagnosis_ids.score", "monynha_diagnosis_ids.summary", "monynha_diagnosis_ids.completed_at")
    def _compute_monynha_latest_diagnosis(self):
        for lead in self:
            completed = lead.monynha_diagnosis_ids.filtered(lambda diagnosis: diagnosis.state == "completed")
            latest = completed.sorted(key=lambda diagnosis: diagnosis.completed_at or diagnosis.create_date, reverse=True)[:1]
            lead.monynha_diagnosis_score = latest.score if latest else 0
            lead.monynha_diagnosis_summary = latest.summary if latest else False

    def _monynha_discovery_answers(self):
        self.ensure_one()
        return {"revenue_model": self.monynha_revenue_model or "", "decision_profile": self.monynha_decision_profile or "", "struggle": self.monynha_struggle or "", "website_url": self.website or "", "instagram_url": self.monynha_instagram_url or "", "linkedin_url": self.monynha_linkedin_url or ""}

    def _monynha_create_diagnosis(self, provider="local_rules"):
        self.ensure_one()
        diagnosis = self.env["monynha.lead.diagnosis"].create({"lead_id": self.id, "provider": provider})
        diagnosis.action_process()
        return diagnosis

    def action_monynha_generate_diagnosis(self):
        self.ensure_one()
        diagnosis = self._monynha_create_diagnosis()
        return {"type": "ir.actions.act_window", "res_model": "monynha.lead.diagnosis", "res_id": diagnosis.id, "view_mode": "form", "target": "current"}

    def action_monynha_view_diagnoses(self):
        self.ensure_one()
        return {"type": "ir.actions.act_window", "name": "Monynha Diagnoses", "res_model": "monynha.lead.diagnosis", "view_mode": "list,form", "domain": [("lead_id", "=", self.id)], "context": {"default_lead_id": self.id}}
