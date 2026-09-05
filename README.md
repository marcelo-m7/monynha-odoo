# Monynha Odoo

Native Odoo 19 Community implementation of the Monynha Softwares website experience and lead-generation workflow.

The project revives the interaction and visual DNA of the historical Monynha/open2.tech presence while replacing its old parallel frontend/backend stack with standard Odoo Website and CRM mechanisms.

## Addons

### `theme_monynha`

M3 completes the visual identity and Website Builder layer as an **Odoo-native branded theme**:

- brutalist-futuristic design system led by void/black, violet and paper surfaces;
- self-contained Monynha wordmark asset;
- reusable Monynha Website Builder snippet group;
- Hero, Services, Process, Labs, CTA, Project Signal, Selected Work, Capability, Manifesto, Metrics, FAQ, Page Intro, Operating Principles and Labs Showcase snippets;
- Odoo-native `theme.website.page` starters for Services, Odoo, Software, AI & Automation, Process, Labs, About and a safe `/start` fallback;
- Odoo-native `theme.website.menu` navigation seed;
- homepage composition through `configurator_snippets`, not a destructive direct `/` page seed;
- standard Odoo Website header, menu, dropdown, mobile navbar and footer rendering with Monynha styling layered on top;
- responsive typography, reduced hard shadows on narrow screens, visible focus states and `prefers-reduced-motion` support;
- no React/Vue frontend runtime, parallel CMS or theme-specific business model.

The final homepage composition is:

```text
Hero
→ Project Signal
→ Capabilities
→ Selected Work
→ Operating Principles
→ Labs / Open Work
→ Manifesto
→ CTA
```

Selected Work and Labs use real editorial project references — FACODI, Codoo Importer and Monynha Odoo — without fabricated client outcomes or commercial metrics.

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

The addons are intentionally independent: neither depends on the other. With only the theme installed, `/start` remains a safe Website page that falls back to `/contactus`. With the lead generator installed, its explicit `/start` controller provides the interactive discovery.

## Website ownership model

M3 deliberately keeps Odoo Website as the owner of the public experience:

```text
Homepage starter     configurator_snippets
Seeded pages         theme.website.page → editable website.page copies
Navigation           theme.website.menu → standard website.menu copies
Header / footer      standard Odoo Website rendering + Monynha SCSS
Labs / Selected Work ordinary editable Website content
/start               theme fallback; lead-generator controller when installed
```

The theme does not hardcode a second navigation tree, replace the Odoo header/footer, create a Labs CMS, or rewrite user-edited `website.page` bodies during normal upgrades.

## Public routes

The theme seeds editable starters for:

- `/services`
- `/services/odoo`
- `/services/software`
- `/services/ai-automation`
- `/process`
- `/labs`
- `/about`
- `/start` — safe standalone fallback

`/process` uses the four-stage method:

```text
Discovery → Architecture → Build → Observe
```

## End-to-end commercial flow

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

## Website Builder editing

After theme installation, editors should use normal Odoo Website tools:

- edit page copy and hierarchy through Website Builder;
- reorder or replace Monynha snippets as normal sections;
- edit Labs and Selected Work cards directly rather than changing a model;
- manage the canonical Website menu in Odoo after the initial theme seed;
- keep `/start` content as a safe theme-only fallback — the lead generator owns the interactive controller when installed.

See `docs/m3-theme-completion.md` for the M3 ownership and route map.

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

GitHub Actions uses the official Odoo 19 image, PostgreSQL 16 and a pinned Odoo `design-themes` checkout for `theme_common`. The release gate verifies:

- theme-only installation;
- lead-generator-only installation and regressions;
- combined installation;
- combined upgrade regressions.

## Future provider extensions

The core provider registry is the extension point for optional integrations such as Gemini or OpenAI. Provider-specific credentials and SDK dependencies should live in separate addons; the core must remain functional with `local_rules` alone.
