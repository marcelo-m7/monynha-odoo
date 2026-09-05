# Monynha Odoo

Native Odoo 19 Community implementation of the Monynha Softwares website experience and lead-generation workflow.

The project revives the interaction and visual DNA of the historical `open2.tech` v6.0.1 lead-generator while replacing its old parallel frontend/backend stack with standard Odoo Website and CRM mechanisms.

## Addons

### `theme_monynha`

Visual identity and Website Builder layer:

- violet-led brutalist-digital design tokens;
- reusable components and Monynha snippet group;
- Hero, Services, Process, Labs, CTA, Project Signal, Selected Work, Capability, Manifesto, Metrics, FAQ and Page Intro snippets;
- Odoo-native `theme.website.page` starters for Services, Odoo, Software, AI & Automation, Process, Labs, About and a safe `/start` fallback;
- Odoo-native `theme.website.menu` navigation seed;
- homepage composition metadata through `configurator_snippets`;
- standard Website header/footer styling without replacing Odoo navigation logic;
- responsive and `prefers-reduced-motion` behavior.

### `monynha_lead_generator`

Commercial discovery layer:

- interactive six-step `/start` discovery;
- server-side validation and explicit public-field whitelist;
- standard `crm.lead` as the canonical commercial record;
- deterministic `local_rules` Project Signal provider;
- append-only `monynha.lead.diagnosis` history;
- four diagnostic dimensions plus signals, opportunities and a normalized recommended next action;
- secure `/diagnosis/<token>` public Project Signal;
- tokenized, idempotent follow-up request from the public report;
- standard CRM chatter and `mail.activity` follow-up when a responsible user exists;
- Odoo `mail.template` messages for diagnosis-ready and follow-up confirmation;
- no mandatory external AI provider.

The addons are intentionally independent: neither depends on the other. With only the theme installed, `/start` remains a safe Website page that falls back to `/contactus`. With the lead-generator installed, its explicit `/start` controller provides the interactive discovery.

## End-to-end flow

```text
Website
  ↓
/start
  ↓
Discovery
  ↓
crm.lead
  ↓
monynha.lead.diagnosis (local_rules)
  ↓
/diagnosis/<secure-token>
  ↓
Project Signal
  ↓
Follow-up request
  ↓
crm.lead timestamp + internal note + standard CRM activity
```

The lead is created **before** diagnosis processing, so a provider failure never loses the commercial enquiry. Diagnosis history is append-only; later analyses do not silently overwrite prior results.

## Public website

The theme seeds editable starters for:

- `/services`
- `/services/odoo`
- `/services/software`
- `/services/ai-automation`
- `/process`
- `/labs`
- `/about`
- `/start` (theme-only fallback)

Editorial ownership remains with Odoo Website Builder. Labs and selected work are intentionally Website content in M2 rather than a custom CMS model.

## Project Signal schema

The default provider returns a normalized deterministic structure:

```text
overall
digital_maturity
automation_potential
process_clarity
odoo_fit
signals[]
opportunities[]
recommended_action
```

`recommended_action` is one of:

- `clarify`
- `automate`
- `centralize`
- `integrate`
- `architecture`

These values describe where a technical conversation should begin. They are not CRM close-probability scoring and do not automatically convert leads into opportunities or quotations.

## Security boundaries

- Public discovery accepts only the explicit server-side whitelist.
- Public CRM creation uses narrowly scoped server-assembled values.
- Project Signal URLs use high-entropy non-sequential tokens.
- Follow-up requests accept only the diagnosis token and are idempotent.
- Raw diagnosis payloads and technical errors remain internal/system-only.
- No arbitrary administrator is assigned when a lead has no salesperson or team leader.

## Development

Contract tests:

```bash
pytest -q tests
```

Clean install against Odoo 19:

```bash
odoo --stop-after-init -d monynha_test \
  -i theme_monynha,monynha_lead_generator \
  --test-enable
```

Upgrade regression:

```bash
odoo --stop-after-init -d monynha_test \
  -u theme_monynha,monynha_lead_generator \
  --test-enable
```

GitHub Actions runs the contract suite plus clean install and upgrade using the official Odoo 19 image, PostgreSQL 16 and a pinned Odoo `design-themes` checkout for `theme_common`.

## Future provider extensions

The core provider registry is the extension point for optional integrations such as Gemini or OpenAI. Provider-specific credentials and SDK dependencies should live in separate addons; the core must remain functional with `local_rules` alone.
