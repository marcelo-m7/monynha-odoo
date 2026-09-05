import logging
import secrets

from odoo import api, fields, models

from ..services.scoring import score_discovery

_logger = logging.getLogger(__name__)

RECOMMENDED_ACTION_SELECTION = [
    ("clarify", "Clarify the operating model"),
    ("automate", "Automate repetitive work"),
    ("centralize", "Centralize operational context"),
    ("integrate", "Integrate system boundaries"),
    ("architecture", "Define the target architecture"),
]


class MonynhaLeadDiagnosis(models.Model):
    _name = "monynha.lead.diagnosis"
    _description = "Monynha Lead Diagnosis"
    _order = "create_date desc, id desc"

    lead_id = fields.Many2one("crm.lead", required=True, ondelete="cascade", index=True)
    state = fields.Selection(
        [
            ("pending", "Pending"),
            ("processing", "Processing"),
            ("completed", "Completed"),
            ("failed", "Failed"),
        ],
        default="pending",
        required=True,
        index=True,
    )
    provider = fields.Char(default="local_rules", required=True, index=True)
    model_name = fields.Char(readonly=True)
    requested_at = fields.Datetime(default=fields.Datetime.now, required=True, readonly=True)
    started_at = fields.Datetime(readonly=True)
    completed_at = fields.Datetime(readonly=True)
    score = fields.Integer(readonly=True)
    digital_maturity = fields.Integer(readonly=True)
    automation_potential = fields.Integer(readonly=True)
    process_clarity = fields.Integer(readonly=True)
    odoo_fit = fields.Integer(readonly=True)
    summary = fields.Text(readonly=True)
    signals = fields.Json(readonly=True)
    opportunities = fields.Json(readonly=True)
    recommended_action = fields.Selection(RECOMMENDED_ACTION_SELECTION, readonly=True)
    raw_payload = fields.Json(readonly=True, groups="base.group_system")
    error_message = fields.Text(readonly=True, groups="base.group_system")
    public_token = fields.Char(
        default=lambda self: secrets.token_urlsafe(32),
        copy=False,
        readonly=True,
        index=True,
    )
    public_url = fields.Char(compute="_compute_public_url")

    _public_token_unique = models.Constraint(
        "unique(public_token)",
        "The public diagnosis token must be unique.",
    )

    @api.depends("public_token")
    def _compute_public_url(self):
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        for diagnosis in self:
            diagnosis.public_url = (
                f"{base_url}/diagnosis/{diagnosis.public_token}"
                if diagnosis.public_token
                else False
            )

    def _get_provider_registry(self):
        self.ensure_one()
        return {"local_rules": self._run_local_rules}

    def _run_local_rules(self):
        self.ensure_one()
        return score_discovery(self.lead_id._monynha_discovery_answers())

    def _build_summary(self, result):
        self.ensure_one()
        strongest = max(
            (
                ("digital maturity", result["digital_maturity"]),
                ("automation potential", result["automation_potential"]),
                ("process clarity", result["process_clarity"]),
                ("Odoo fit", result["odoo_fit"]),
            ),
            key=lambda item: item[1],
        )[0]
        action_labels = dict(RECOMMENDED_ACTION_SELECTION)
        action = action_labels.get(
            result.get("recommended_action"),
            "Define the next architecture step",
        )
        return (
            f"The discovery shows {strongest} as the strongest current signal. "
            f"Suggested next move: {action}. "
            "Use the dimensions and opportunities as a conversation starter, not as an automatic sales decision."
        )

    def action_process(self):
        for diagnosis in self:
            if diagnosis.state == "completed":
                continue
            diagnosis.write(
                {
                    "state": "processing",
                    "started_at": fields.Datetime.now(),
                    "error_message": False,
                }
            )
            provider = diagnosis._get_provider_registry().get(diagnosis.provider)
            if not provider:
                diagnosis.write(
                    {
                        "state": "failed",
                        "completed_at": fields.Datetime.now(),
                        "error_message": f"Unknown diagnosis provider: {diagnosis.provider}",
                    }
                )
                continue
            try:
                result = provider()
            except Exception as error:  # keep the lead and diagnosis history intact
                _logger.exception("Monynha diagnosis failed for lead %s", diagnosis.lead_id.id)
                diagnosis.write(
                    {
                        "state": "failed",
                        "completed_at": fields.Datetime.now(),
                        "error_message": str(error),
                    }
                )
                continue
            diagnosis.write(
                {
                    "state": "completed",
                    "completed_at": fields.Datetime.now(),
                    "model_name": "monynha-local-rules-v2",
                    "score": result["overall"],
                    "digital_maturity": result["digital_maturity"],
                    "automation_potential": result["automation_potential"],
                    "process_clarity": result["process_clarity"],
                    "odoo_fit": result["odoo_fit"],
                    "summary": diagnosis._build_summary(result),
                    "signals": result["signals"],
                    "opportunities": result["opportunities"],
                    "recommended_action": result["recommended_action"],
                    "raw_payload": result,
                }
            )
        return True

    def action_request_followup(self):
        """Record one public follow-up request and use standard CRM activities when possible."""
        self.ensure_one()
        lead = self.lead_id

        # Serialize requests for this CRM lead so two simultaneous public calls
        # cannot both pass the idempotency check and create duplicate side effects.
        self.env.cr.execute("SELECT id FROM crm_lead WHERE id = %s FOR UPDATE", (lead.id,))
        lead.invalidate_recordset(["monynha_followup_requested_at"])
        if lead.monynha_followup_requested_at:
            return False

        lead.write({"monynha_followup_requested_at": fields.Datetime.now()})
        lead.message_post(
            body="Project Signal follow-up requested from the public Monynha report.",
            subtype_xmlid="mail.mt_note",
        )

        responsible = lead.user_id or lead.team_id.user_id
        if responsible:
            existing = lead.activity_ids.filtered(
                lambda activity: activity.summary == "Monynha Project Signal follow-up"
            )
            if not existing:
                lead.activity_schedule(
                    "mail.mail_activity_data_todo",
                    summary="Monynha Project Signal follow-up",
                    note="The visitor requested a conversation from their public Project Signal.",
                    user_id=responsible.id,
                )

        if lead.email_from:
            template = self.env.ref(
                "monynha_lead_generator.mail_template_followup_received",
                raise_if_not_found=False,
            )
            if template:
                try:
                    template.with_context(report_url=self.public_url).send_mail(
                        lead.id,
                        force_send=False,
                    )
                except Exception:
                    _logger.exception(
                        "Could not queue Monynha follow-up confirmation for lead %s",
                        lead.id,
                    )
        return True
