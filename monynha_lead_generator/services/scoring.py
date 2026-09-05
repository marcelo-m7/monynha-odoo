"""Deterministic first-pass scoring for the Monynha discovery flow."""


def _bounded(value):
    return max(0, min(100, int(round(value))))


def score_discovery(answers):
    answers = answers or {}
    revenue = (answers.get("revenue_model") or "").strip().lower()
    decision = (answers.get("decision_profile") or "").strip().lower()
    struggle = (answers.get("struggle") or "").strip().lower()
    digital_channels = sum(bool((answers.get(key) or "").strip()) for key in ("website_url", "instagram_url", "linkedin_url"))

    digital_maturity = 25 + digital_channels * 18
    process_clarity = 58
    automation_potential = 48
    odoo_fit = 45
    signals = []

    manual_terms = ("manual", "spreadsheet", "excel", "repeat", "duplicat", "copy", "whatsapp")
    scale_terms = ("scale", "grow", "crescer", "escala", "overload", "sobrecarga")
    fragmented_terms = ("fragment", "different tools", "muitas ferramentas", "vários sistemas", "varios sistemas")

    if any(term in struggle for term in manual_terms):
        automation_potential += 30
        process_clarity -= 8
        odoo_fit += 18
        signals.append("Manual or repetitive work is a strong automation opportunity.")
    if any(term in struggle for term in scale_terms):
        automation_potential += 12
        odoo_fit += 8
        signals.append("The current operating model shows scaling pressure.")
    if any(term in struggle for term in fragmented_terms):
        digital_maturity -= 8
        odoo_fit += 18
        signals.append("Fragmented systems suggest a centralisation opportunity.")

    if revenue == "service":
        odoo_fit += 15
        signals.append("A service operation can benefit from connected CRM, delivery and billing workflows.")
    elif revenue == "subscription":
        odoo_fit += 12
        automation_potential += 8
        signals.append("Recurring revenue benefits from consistent lifecycle automation.")
    elif revenue == "product":
        odoo_fit += 10

    if decision == "solo":
        automation_potential += 14
        process_clarity -= 5
        signals.append("Execution is concentrated in one person, increasing automation leverage.")
    elif decision == "sales_focus":
        automation_potential += 12
        signals.append("Sales focus creates a strong case for automating delivery handoffs.")
    elif decision == "delegate":
        process_clarity += 8
    elif decision == "unclear":
        process_clarity -= 18
        signals.append("The first priority is clarifying ownership and operating boundaries.")

    if len(struggle) >= 80:
        process_clarity += 8
    elif len(struggle) < 20:
        process_clarity -= 10
    if digital_channels == 0:
        digital_maturity -= 10
        signals.append("Digital presence is still early, leaving room to design a cleaner foundation.")
    elif digital_channels >= 2:
        digital_maturity += 8

    digital_maturity = _bounded(digital_maturity)
    automation_potential = _bounded(automation_potential)
    process_clarity = _bounded(process_clarity)
    odoo_fit = _bounded(odoo_fit)
    overall = _bounded(digital_maturity * 0.20 + automation_potential * 0.30 + process_clarity * 0.20 + odoo_fit * 0.30)
    return {"overall": overall, "digital_maturity": digital_maturity, "automation_potential": automation_potential, "process_clarity": process_clarity, "odoo_fit": odoo_fit, "signals": signals[:6]}
