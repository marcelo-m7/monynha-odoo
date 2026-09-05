# Monynha M2 End-to-End Experience Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete the Monynha public website and commercial journey from Homepage through discovery, Project Signal and standard CRM follow-up on Odoo 19 Community.

**Architecture:** Keep `theme_monynha` and `monynha_lead_generator` independently installable. Use Odoo 19 theme-native `theme.website.page` and `theme.website.menu` records for initial pages/navigation, Website Builder for editorial ownership, `crm.lead` for the commercial record, append-only `monynha.lead.diagnosis` for Project Signal history, and standard `mail.activity`/`mail.template` for follow-up.

**Tech Stack:** Odoo 19 Community, QWeb/XML, SCSS, Odoo frontend ES modules, Python ORM/controllers, PostgreSQL 16, pytest contract tests, Odoo TransactionCase/HttpCase, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-05-monynha-m2-end-to-end-design.md`

## Global Constraints

- Target Odoo 19 Community.
- `crm.lead` remains canonical; do not create a parallel lead model.
- `website.menu` remains canonical after theme installation; seed it through `theme.website.menu`.
- Seed editable public pages through `theme.website.page`; do not use upgrade-destructive direct `website.page` data.
- Website Builder remains the editor for public editorial content.
- `theme_monynha` must not depend on `monynha_lead_generator`.
- `monynha_lead_generator` must not depend on `theme_monynha`.
- No React, Vue, Supabase, iframe frontend or mandatory external AI provider.
- No source-database IDs or unnecessary `sudo()`.
- Preserve `prefers-reduced-motion`, keyboard navigation, visible focus, responsive behavior and safe install/upgrade.

---

### Task 1: Expand theme contracts and reusable design system

**Files:**
- Modify: `theme_monynha/tests/test_theme.py`
- Modify: `tests/test_contracts.py`
- Modify: `theme_monynha/__manifest__.py`
- Create: `theme_monynha/static/src/scss/tokens.scss`
- Modify: `theme_monynha/static/src/scss/components.scss`
- Modify: `theme_monynha/static/src/scss/snippets.scss`
- Modify: `theme_monynha/static/src/scss/website.scss`
- Create: `theme_monynha/views/snippets_m2.xml`

**Interfaces:**
- Consumes: existing M1 classes such as `.monynha-button`, `.monynha-card`, `.monynha-panel`, `.monynha-spark`.
- Produces: reusable classes `.monynha-section-header`, `.monynha-signal-card`, `.monynha-work-card`, `.monynha-capability`, `.monynha-metric`, `.monynha-faq`, `.monynha-terminal` and M2 snippet template XML IDs.

- [ ] **Step 1: Write failing theme and contract tests**

Add assertions that the M2 snippet templates are registered, the theme manifest does not depend on `monynha_lead_generator`, `tokens.scss` is loaded before component files, and reduced-motion rules remain present.

Example Odoo assertion:

```python
for xmlid in (
    "theme_monynha.s_monynha_signal",
    "theme_monynha.s_monynha_selected_work",
    "theme_monynha.s_monynha_manifesto",
    "theme_monynha.s_monynha_metrics",
    "theme_monynha.s_monynha_faq",
):
    self.assertTrue(self.env.ref(xmlid, raise_if_not_found=False), xmlid)
```

- [ ] **Step 2: Run tests and confirm failure**

Run locally where Odoo is available:

```bash
pytest -q tests
odoo --stop-after-init -d monynha_m2_theme_test -i theme_monynha --test-enable --test-tags /theme_monynha
```

Expected: failures for missing M2 snippets/tokens.

- [ ] **Step 3: Implement minimal token/component/snippet layer**

Move palette/spacing/shadow/motion constants into `tokens.scss`; add only the M2 components required by real pages. Register `snippets_m2.xml` in the manifest and Website Builder group.

- [ ] **Step 4: Re-run tests**

Expected: theme contracts and theme Odoo tests pass.

- [ ] **Step 5: Commit**

```bash
git add theme_monynha tests/test_contracts.py
git commit -m "feat: expand Monynha website design system"
```

---

### Task 2: Add Odoo-native page starters and navigation

**Files:**
- Modify: `theme_monynha/tests/test_theme.py`
- Create: `theme_monynha/data/pages.xml`
- Create: `theme_monynha/data/menu.xml`
- Modify: `theme_monynha/__manifest__.py`
- Modify: `theme_monynha/static/src/scss/website.scss`

**Interfaces:**
- Consumes: M2 snippets/components from Task 1.
- Produces: `theme.website.page` starter pages and `theme.website.menu` seed records that Odoo copies into canonical `website.page`/`website.menu` during theme installation.

- [ ] **Step 1: Write failing page/menu tests**

Assert the following theme records exist after installation:

```python
for xmlid in (
    "theme_monynha.page_services",
    "theme_monynha.page_services_odoo",
    "theme_monynha.page_services_software",
    "theme_monynha.page_services_ai",
    "theme_monynha.page_process",
    "theme_monynha.page_labs",
    "theme_monynha.page_about",
):
    self.assertTrue(self.env.ref(xmlid, raise_if_not_found=False), xmlid)
```

Also assert menu entries use `theme.website.menu` and no direct hardcoded database IDs appear in the XML.

- [ ] **Step 2: Run tests and verify failure**

Expected: missing page/menu XML IDs.

- [ ] **Step 3: Implement page starters using the Odoo 19 theme pattern**

For each page, define a QWeb template with `website.layout` and editable `oe_structure`, then seed it with `theme.website.page`, e.g.:

```xml
<template id="view_services" name="Monynha Services">
    <t t-call="website.layout">
        <div id="wrap" class="oe_structure">
            <!-- compose reusable Monynha sections -->
        </div>
    </t>
</template>
<record id="page_services" model="theme.website.page">
    <field name="view_id" ref="view_services"/>
    <field name="is_published" eval="True"/>
    <field name="url">/services</field>
</record>
```

Seed Services, Process, Labs and About navigation with `theme.website.menu`. Keep `/contactus` standard. Use `/contactus` as the theme-only CTA fallback so standalone installation has no dead route.

- [ ] **Step 4: Style header/footer/navigation narrowly**

Style standard website header/footer selectors under Monynha theme scope; do not replace menu rendering logic or hardcode a navigation tree in QWeb.

- [ ] **Step 5: Verify install/upgrade and route presence**

Run theme install then `-u theme_monynha`; verify pages remain published and no test asserts loss/duplication.

- [ ] **Step 6: Commit**

```bash
git add theme_monynha
git commit -m "feat: add Monynha page starters and navigation"
```

---

### Task 3: Enrich deterministic Project Signal output

**Files:**
- Modify: `monynha_lead_generator/tests/test_diagnosis.py`
- Modify: `tests/test_contracts.py`
- Modify: `monynha_lead_generator/services/scoring.py`
- Modify: `monynha_lead_generator/models/diagnosis.py`
- Modify: `monynha_lead_generator/models/crm_lead.py`
- Modify: `monynha_lead_generator/views/diagnosis_views.xml`
- Modify: `monynha_lead_generator/views/crm_lead_views.xml`

**Interfaces:**
- Consumes: `score_discovery(answers: dict) -> dict`.
- Produces normalized result keys `opportunities: list[str]` and `recommended_action: str` in addition to M1 keys; diagnosis fields `opportunities` (`fields.Json`) and `recommended_action` (`fields.Char`); latest values exposed on `crm.lead` as computed fields.

- [ ] **Step 1: Write failing scoring tests**

Add deterministic expectations, for example:

```python
result = score_discovery({
    "revenue_model": "service",
    "decision_profile": "solo",
    "struggle": "We copy Excel data manually between different tools every day.",
    "website_url": "https://example.com",
})
assert "opportunities" in result
assert result["opportunities"]
assert result["recommended_action"] in {"clarify", "automate", "centralize", "integrate", "architecture"}
```

- [ ] **Step 2: Run tests and verify failure**

Expected: missing normalized keys/fields.

- [ ] **Step 3: Implement deterministic opportunity derivation**

Keep rules transparent. Deduplicate opportunities while preserving order and cap public output to a small list. Example recommendation vocabulary:

```python
RECOMMENDED_ACTIONS = {"clarify", "automate", "centralize", "integrate", "architecture"}
```

Do not turn local rules into an opaque ML-like score.

- [ ] **Step 4: Persist normalized output append-only**

Add diagnosis fields and include them in `action_process()` writes. Extend the latest-diagnosis compute on `crm.lead` rather than duplicating stored values.

- [ ] **Step 5: Re-run diagnosis/contract tests**

Expected: existing M1 behavior plus new output passes.

- [ ] **Step 6: Commit**

```bash
git add monynha_lead_generator tests/test_contracts.py
git commit -m "feat: enrich Monynha Project Signal"
```

---

### Task 4: Upgrade the public Project Signal experience

**Files:**
- Modify: `monynha_lead_generator/tests/test_http.py`
- Modify: `monynha_lead_generator/views/templates.xml`
- Modify: `monynha_lead_generator/static/src/scss/lead_generator.scss`

**Interfaces:**
- Consumes: completed diagnosis fields from Task 3.
- Produces: public report markup exposing only safe normalized fields and a follow-up control keyed by `diagnosis.public_token`.

- [ ] **Step 1: Write failing HTTP/report tests**

Create a completed diagnosis with opportunities and assert `/diagnosis/<token>` returns 200 and includes the safe opportunity/recommended-action presentation while excluding `lead_id`, raw payload and technical error text.

- [ ] **Step 2: Run tests and verify failure**

- [ ] **Step 3: Implement report sections**

Render overall score, four dimensions, summary, signals, opportunities and a suggested route. Keep the token in an HTML data attribute/form value only where needed for the follow-up call.

- [ ] **Step 4: Add responsive/reduced-motion styling**

No canvas loop or third-party animation library.

- [ ] **Step 5: Re-run HTTP tests**

- [ ] **Step 6: Commit**

```bash
git add monynha_lead_generator
git commit -m "feat: complete public Project Signal report"
```

---

### Task 5: Connect Project Signal to standard CRM follow-up

**Files:**
- Modify: `monynha_lead_generator/tests/test_diagnosis.py`
- Modify: `monynha_lead_generator/tests/test_http.py`
- Modify: `monynha_lead_generator/models/crm_lead.py`
- Modify: `monynha_lead_generator/models/diagnosis.py`
- Modify: `monynha_lead_generator/controllers/main.py`
- Modify: `monynha_lead_generator/views/templates.xml`
- Modify: `monynha_lead_generator/data/mail_templates.xml`
- Modify: `monynha_lead_generator/views/crm_lead_views.xml`

**Interfaces:**
- Produces: `monynha_followup_requested_at` on `crm.lead`; `monynha.lead.diagnosis.action_request_followup()`; JSON-RPC route `/monynha/diagnosis/followup` accepting only a secure `token`.
- Uses: `crm.lead.activity_schedule()` and `mail.template` when a responsible CRM user is resolvable.

- [ ] **Step 1: Write failing model test for follow-up**

Example:

```python
diagnosis.action_request_followup()
self.assertTrue(lead.monynha_followup_requested_at)
self.assertIn("follow-up", lead.message_ids[:1].body.lower())
```

When `lead.user_id` is set, assert a standard CRM activity exists for that user. When no responsible user is resolved, assert the request is still recorded and no arbitrary admin activity is created.

- [ ] **Step 2: Write failing public-route tests**

Assert unknown/invalid tokens do not mutate CRM; valid token returns `{ok: True}`; repeated requests are idempotent and do not create unbounded duplicate activities.

- [ ] **Step 3: Implement model-side follow-up**

Put business behavior on the model, not the controller. Resolve assignee as `lead.user_id` first and `lead.team_id.user_id` only if available. Record the timestamp/message regardless. Schedule at most one outstanding Monynha follow-up activity.

- [ ] **Step 4: Implement narrow public endpoint**

Controller accepts only `token`, finds the diagnosis by secure token with narrow `sudo()`, and delegates to `action_request_followup()`.

- [ ] **Step 5: Add visitor confirmation email**

Add `mail_template_followup_received` and queue it after a successful request when `lead.email_from` exists. Email contains no internal CRM data.

- [ ] **Step 6: Re-run model/HTTP tests**

- [ ] **Step 7: Commit**

```bash
git add monynha_lead_generator
git commit -m "feat: connect Project Signal to CRM follow-up"
```

---

### Task 6: Harden discovery UX and accessibility

**Files:**
- Modify: `monynha_lead_generator/static/src/js/discovery.js`
- Modify: `monynha_lead_generator/views/templates.xml`
- Modify: `monynha_lead_generator/static/src/scss/lead_generator.scss`
- Modify: `tests/test_contracts.py`

**Interfaces:**
- Preserves: storage key `monynha_discovery_draft_v1`, six-step submission payload and `/monynha/discovery/submit` contract.
- Produces: clearer state/focus handling without API changes.

- [ ] **Step 1: Add failing contract assertions**

Assert the wizard retains `Escape` back navigation, `Enter` forward navigation outside `textarea`, local draft recovery, `aria-live` errors, reduced-motion styles and no third-party JS import.

- [ ] **Step 2: Refactor the one-line M1 JS into focused functions**

Split internal responsibilities into draft load/save, state render, validation, choice handling and submission. Do not introduce a framework.

- [ ] **Step 3: Improve accessible step transitions**

Move focus to the first control only on fine pointers; preserve touch behavior; expose step progress textually as well as visually; disable submit during active request to prevent duplicates.

- [ ] **Step 4: Re-run contracts and Odoo HTTP tests**

- [ ] **Step 5: Commit**

```bash
git add monynha_lead_generator tests/test_contracts.py
git commit -m "refactor: harden Monynha discovery experience"
```

---

### Task 7: End-to-end regression, documentation and CI gate

**Files:**
- Modify: `theme_monynha/tests/test_theme.py`
- Modify: `monynha_lead_generator/tests/test_http.py`
- Modify: `.github/workflows/ci.yml` only if the existing gate does not exercise both install and upgrade paths needed by M2
- Modify: `README.md`
- Create: `docs/m2-end-to-end.md`

**Interfaces:**
- Validates the complete user journey and both independent-addon boundaries.

- [ ] **Step 1: Add end-to-end regression assertions**

Cover:

```text
Home/page starter available
-> /start
-> public submit
-> crm.lead created
-> diagnosis completed
-> /diagnosis/<token>
-> follow-up request
-> crm.lead timestamp/message/activity
```

Also test failure path: diagnosis failure leaves lead intact and report fallback safe.

- [ ] **Step 2: Run local contract suite**

```bash
pytest -q tests
```

Expected: PASS.

- [ ] **Step 3: Run Odoo clean install**

```bash
odoo --stop-after-init -d monynha_m2 -i theme_monynha,monynha_lead_generator --test-enable
```

Expected: zero ERROR-level module/test failures.

- [ ] **Step 4: Run Odoo upgrades**

```bash
odoo --stop-after-init -d monynha_m2 -u theme_monynha,monynha_lead_generator --test-enable
```

Expected: upgrade succeeds and seeded theme pages/menu do not duplicate or destroy edited content.

- [ ] **Step 5: Update documentation**

Document addon boundaries, page starter mechanism (`theme.website.page`/`theme.website.menu`), Project Signal normalized schema, follow-up behavior, install/upgrade commands and future provider extension point.

- [ ] **Step 6: Run diff review**

Scan for `TODO`, `TBD`, source DB IDs, unnecessary `sudo()`, duplicated QWeb, dead CSS, old Supabase/React references and accidental cross-addon dependencies.

- [ ] **Step 7: Commit**

```bash
git add .
git commit -m "test: verify Monynha M2 end-to-end journey"
```

- [ ] **Step 8: Open/update PR and use GitHub Actions as final gate**

PR title: `M2: complete Monynha end-to-end website and commercial journey`.

Do not merge until contract tests, Odoo 19 clean install and Odoo 19 upgrade jobs are green.
