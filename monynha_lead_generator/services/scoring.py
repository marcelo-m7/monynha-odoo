"""Deterministic first-pass scoring for the Monynha discovery flow."""

RECOMMENDED_ACTIONS = {"clarify", "automate", "centralize", "integrate", "architecture"}


def _bounded(value):
    return max(0, min(100, int(round(value))))


def _append_unique(items, value):
    if value and value not in items:
        items.append(value)


def score_discovery(answers):
    answers = answers or {}
    revenue = (answers.get("revenue_model") or "").strip().lower()
    decision = (answers.get("decision_profile") or "").strip().lower()
    struggle = (answers.get("struggle") or "").strip().lower()
    digital_channels = sum(
        bool((answers.get(key) or "").strip())
        for key in ("website_url", "instagram_url", "linkedin_url")
    )

    digital_maturity = 25 + digital_channels * 18
    process_clarity = 58
    automation_potential = 48
    odoo_fit = 45
    signals = []
    opportunities = []

    manual_terms = (
        "manual",
        "spreadsheet",
        "excel",
        "repeat",
        "repet",
        "duplicat",
        "copy",
        "whatsapp",
    )
    scale_terms = ("scale", "grow", "crescer", "escala", "overload", "sobrecarga")
    fragmented_terms = (
        "fragment",
        "different tools",
        "many tools",
        "muitas ferramentas",
        "vários sistemas",
        "varios sistemas",
        "various systems",
    )
    integration_terms = ("integrat", "api", "sync", "sincron", "channel", "canal")

    has_manual_pressure = any(term in struggle for term in manual_terms)
    has_scale_pressure = any(term in struggle for term in scale_terms)
    has_fragmentation = any(term in struggle for term in fragmented_terms)
    has_integration_pressure = any(term in struggle for term in integration_terms)

    if has_manual_pressure:
        automation_potential += 30
        process_clarity -= 8
        odoo_fit += 18
        _append_unique(signals, "Manual or repetitive work is a strong automation opportunity.")
        _append_unique(opportunities, "Automate repetitive handoffs and data-entry work.")

    if has_scale_pressure:
        automation_potential += 12
        odoo_fit += 8
        _append_unique(signals, "The current operating model shows scaling pressure.")
        _append_unique(opportunities, "Stabilize the operating workflow before adding more volume.")

    if has_fragmentation:
        digital_maturity -= 8
        odoo_fit += 18
        _append_unique(signals, "Fragmented systems suggest a centralisation opportunity.")
        _append_unique(opportunities, "Centralize operational context and reduce duplicated systems.")

    if has_integration_pressure and not has_fragmentation:
        automation_potential += 8
        _append_unique(signals, "The workflow depends on information crossing system boundaries.")
        _append_unique(opportunities, "Integrate the systems that currently require manual handoffs.")

    if revenue == "service":
        odoo_fit += 15
        _append_unique(
            signals,
            "A service operation can benefit from connected CRM, delivery and billing workflows.",
        )
        _append_unique(opportunities, "Connect sales, delivery and billing around one customer lifecycle.")
    elif revenue == "subscription":
        odoo_fit += 12
        automation_potential += 8
        _append_unique(signals, "Recurring revenue benefits from consistent lifecycle automation.")
        _append_unique(opportunities, "Automate recurring lifecycle events and exceptions.")
    elif revenue == "product":
        odoo_fit += 10
        _append_unique(opportunities, "Connect demand, fulfilment and customer context.")

    if decision == "solo":
        automation_potential += 14
        process_clarity -= 5
        _append_unique(signals, "Execution is concentrated in one person, increasing automation leverage.")
        _append_unique(opportunities, "Remove repetitive work from the person holding most operational context.")
    elif decision == "sales_focus":
        automation_potential += 12
        _append_unique(signals, "Sales focus creates a strong case for automating delivery handoffs.")
        _append_unique(opportunities, "Create a reliable handoff from sales into delivery.")
    elif decision == "delegate":
        process_clarity += 8
        _append_unique(opportunities, "Make ownership and handoffs visible across the team.")
    elif decision == "unclear":
        process_clarity -= 18
        _append_unique(signals, "The first priority is clarifying ownership and operating boundaries.")
        _append_unique(opportunities, "Clarify ownership, responsibilities and the operating boundary first.")

    if len(struggle) >= 80:
        process_clarity += 8
    elif len(struggle) < 20:
        process_clarity -= 10

    if digital_channels == 0:
        digital_maturity -= 10
        _append_unique(signals, "Digital presence is still early, leaving room to design a cleaner foundation.")
        _append_unique(opportunities, "Establish a simple digital foundation before multiplying channels.")
    elif digital_channels >= 2:
        digital_maturity += 8
        if not has_fragmentation:
            _append_unique(opportunities, "Keep customer context consistent across digital channels.")

    if decision == "unclear":
        recommended_action = "clarify"
    elif has_fragmentation:
        recommended_action = "centralize"
    elif has_manual_pressure:
        recommended_action = "automate"
    elif has_integration_pressure or digital_channels >= 2:
        recommended_action = "integrate"
    else:
        recommended_action = "architecture"

    digital_maturity = _bounded(digital_maturity)
    automation_potential = _bounded(automation_potential)
    process_clarity = _bounded(process_clarity)
    odoo_fit = _bounded(odoo_fit)
    overall = _bounded(
        digital_maturity * 0.20
        + automation_potential * 0.30
        + process_clarity * 0.20
        + odoo_fit * 0.30
    )

    return {
        "overall": overall,
        "digital_maturity": digital_maturity,
        "automation_potential": automation_potential,
        "process_clarity": process_clarity,
        "odoo_fit": odoo_fit,
        "signals": signals[:6],
        "opportunities": opportunities[:5],
        "recommended_action": recommended_action,
    }
