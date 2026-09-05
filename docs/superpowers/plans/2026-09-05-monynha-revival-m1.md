# Monynha Revival M1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver the first native Odoo 19 Community vertical slice of Monynha Softwares: reusable visual theme, interactive discovery wizard, CRM lead creation, deterministic diagnosis, secure public report, and notification email.

**Architecture:** `theme_monynha` owns presentation and Website Builder snippets. `monynha_lead_generator` owns the discovery workflow and extends standard `crm.lead`; diagnosis history lives in `monynha.lead.diagnosis`. The two addons install independently and external AI providers are explicitly deferred behind a provider registry.

**Tech Stack:** Odoo 19 Community, Website/QWeb, CRM, mail, SCSS, Odoo frontend ES modules.

**Spec:** Conversation-approved “Monynha Softwares 2.0 — Especificação arquitetural Odoo 19”.

## Global Constraints
- Odoo 19 Community only.
- `crm.lead` is the canonical commercial record.
- No Supabase, React SPA, iframe, or mandatory external AI provider.
- `theme_monynha` must not depend on `monynha_lead_generator`.
- `monynha_lead_generator` must not depend on `theme_monynha`.
- Public report access must use an unguessable token, never a sequential lead ID.
- Create the lead before diagnosis processing so diagnosis failure cannot lose the lead.
- First provider is deterministic `local_rules`.

## Tasks
- [x] Theme foundation and reusable snippets.
- [x] CRM discovery fields and deterministic diagnosis domain.
- [x] Public `/start` wizard and tokenized report.
- [x] Diagnosis-ready email template.
- [x] Contract tests and Odoo install/upgrade CI.
- [ ] Confirm GitHub Actions green after push.
