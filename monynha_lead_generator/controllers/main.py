import logging

from odoo import fields, http, tools
from odoo.http import request

_logger = logging.getLogger(__name__)

ALLOWED_SUBMISSION_FIELDS = {
    "email",
    "brand_name",
    "no_brand",
    "revenue_model",
    "decision_profile",
    "struggle",
    "website_url",
    "instagram_url",
    "linkedin_url",
    "website_company",
}
ALLOWED_REVENUE_MODELS = {"service", "product", "subscription", "other"}
ALLOWED_DECISION_PROFILES = {"solo", "delegate", "sales_focus", "unclear"}


class MonynhaDiscoveryController(http.Controller):
    @http.route("/start", type="http", auth="public", website=True, sitemap=True)
    def discovery_start(self, **kwargs):
        return request.render("monynha_lead_generator.discovery_start")

    @http.route(
        "/monynha/discovery/submit",
        type="jsonrpc",
        auth="public",
        website=True,
        methods=["POST"],
    )
    def submit_discovery(self, **payload):
        unknown = set(payload) - ALLOWED_SUBMISSION_FIELDS
        if unknown:
            return {"ok": False, "error": "Invalid submission fields."}
        if (payload.get("website_company") or "").strip():
            return {"ok": True, "report_url": "/contactus"}

        email = tools.email_normalize((payload.get("email") or "").strip())
        brand_name = (payload.get("brand_name") or "").strip()
        no_brand = bool(payload.get("no_brand"))
        revenue_model = (payload.get("revenue_model") or "").strip()
        decision_profile = (payload.get("decision_profile") or "").strip()
        struggle = (payload.get("struggle") or "").strip()

        if not email:
            return {"ok": False, "error": "Please enter a valid email address."}
        if not no_brand and len(brand_name) < 2:
            return {
                "ok": False,
                "error": "Tell us the project or brand name, or choose the no-name option.",
            }
        if revenue_model not in ALLOWED_REVENUE_MODELS:
            return {"ok": False, "error": "Choose a valid revenue model."}
        if decision_profile not in ALLOWED_DECISION_PROFILES:
            return {"ok": False, "error": "Choose a valid operating style."}
        if len(struggle) < 10:
            return {
                "ok": False,
                "error": "Describe the main challenge in a little more detail.",
            }

        lead_values = {
            "name": f"Monynha Discovery — {brand_name or email}",
            "type": "lead",
            "email_from": email,
            "partner_name": brand_name or False,
            "website": (payload.get("website_url") or "").strip() or False,
            "referred": "Monynha Discovery",
            "monynha_brand_name": brand_name or False,
            "monynha_revenue_model": revenue_model,
            "monynha_decision_profile": decision_profile,
            "monynha_struggle": struggle,
            "monynha_instagram_url": (payload.get("instagram_url") or "").strip() or False,
            "monynha_linkedin_url": (payload.get("linkedin_url") or "").strip() or False,
            "monynha_discovery_version": "1",
            "monynha_discovery_completed_at": fields.Datetime.now(),
        }
        # Public users have no CRM create access. sudo is limited to this server-side whitelist.
        lead = request.env["crm.lead"].sudo().create(lead_values)
        diagnosis = lead.sudo()._monynha_create_diagnosis(provider="local_rules")
        report_url = diagnosis.public_url if diagnosis.public_token else "/contactus"

        if diagnosis.state == "completed":
            template = request.env.ref(
                "monynha_lead_generator.mail_template_diagnosis_ready",
                raise_if_not_found=False,
            )
            if template:
                try:
                    template.sudo().with_context(report_url=report_url).send_mail(
                        lead.id,
                        force_send=False,
                    )
                except Exception:
                    _logger.exception(
                        "Could not queue Monynha diagnosis email for lead %s",
                        lead.id,
                    )

        lead.sudo().message_post(body="Monynha website discovery completed.")
        return {"ok": True, "report_url": report_url}

    @http.route(
        "/monynha/diagnosis/followup",
        type="jsonrpc",
        auth="public",
        website=True,
        methods=["POST"],
    )
    def request_followup(self, token=None, **kwargs):
        token = (token or "").strip()
        if len(token) < 20 or len(token) > 128:
            return {"ok": False, "error": "not_found"}
        diagnosis = request.env["monynha.lead.diagnosis"].sudo().search(
            [("public_token", "=", token)],
            limit=1,
        )
        if not diagnosis:
            return {"ok": False, "error": "not_found"}
        created = diagnosis.action_request_followup()
        return {
            "ok": True,
            "already_requested": not created,
        }

    @http.route(
        "/diagnosis/<string:token>",
        type="http",
        auth="public",
        website=True,
        sitemap=False,
    )
    def diagnosis_report(self, token, **kwargs):
        diagnosis = request.env["monynha.lead.diagnosis"].sudo().search(
            [("public_token", "=", token)],
            limit=1,
        )
        if not diagnosis:
            return request.not_found()
        return request.render(
            "monynha_lead_generator.diagnosis_report",
            {"diagnosis": diagnosis},
        )
