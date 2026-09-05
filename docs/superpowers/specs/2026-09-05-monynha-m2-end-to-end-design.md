# Monynha M2 End-to-End Experience Design

## Context

M1 established two independent Odoo 19 Community addons:

- `theme_monynha`: visual identity and reusable Website Builder snippets.
- `monynha_lead_generator`: `/start` discovery wizard, `crm.lead` integration, deterministic `local_rules` diagnosis, append-only `monynha.lead.diagnosis` history, secure public Project Signal, CRM views, email and tests.

M2 completes the public website and commercial journey without collapsing these responsibilities or introducing a parallel CRM, SPA, Supabase dependency, or mandatory external AI provider.

## Goal

Deliver a complete Monynha website and commercial journey in which a visitor can understand the studio, explore capabilities and projects, start a discovery, receive a useful Project Signal, and create a clear next commercial action in standard Odoo CRM.

## Architectural choice

Use the Odoo-native approach approved for M2:

1. `theme_monynha` owns visual identity, Website Builder components, public page composition, header/footer styling, responsive behavior, accessibility and editorial page starters.
2. `monynha_lead_generator` owns discovery state, CRM enrichment, diagnosis, Project Signal, transactional communication and commercial follow-up.
3. The addons remain independently installable and do not depend on one another.
4. Standard Odoo models and workflows remain canonical wherever they already solve the requirement.

## Global constraints

- Target Odoo 19 Community.
- Keep `crm.lead` as the canonical commercial record.
- Keep `website.menu` as the canonical website navigation model.
- Keep Website Builder as the canonical editor for public editorial content.
- Do not add React, Vue, Supabase, iframe-based frontends or a parallel SPA.
- Do not make the core depend on OpenAI, Gemini or another external AI provider.
- Do not copy large upstream Odoo templates when narrow inheritance or standard page composition is sufficient.
- Do not hardcode source-database record IDs.
- Module upgrades must not overwrite user-edited website content.
- Preserve the historical Monynha `v6.0.1` visual/interaction DNA: dark, violet, brutalist-digital, playful progress, spark/fairy motifs and a useful lead journey.
- Respect keyboard navigation, visible focus, contrast, mobile touch targets and `prefers-reduced-motion`.

## Theme architecture

### Design system layers

`theme_monynha` is organized conceptually as:

`tokens -> primitives -> components -> snippets -> page starters`

Tokens cover palette, spacing, radii, shadows, typography scale and motion durations. Components cover repeatable UI such as buttons, cards, choice cards, badges, progress, Project Signal indicators, terminal panels, section headers and CTAs. Snippets compose those components into Website Builder blocks.

### Snippet library

M1 snippets remain and are refined rather than replaced:

- Monynha Hero
- Services
- Process
- Labs
- CTA

M2 adds reusable snippets only where a real page composition requires them:

- Project Signal teaser
- Selected Work
- Capability detail
- Manifesto / Philosophy
- Metrics / Proof
- FAQ
- Contact / Start Project CTA
- Compact intro banner

Each snippet must be editable, responsive, translatable, semantic and independent of fixed database IDs.

### Page starters

Provide safe, editable page starters for:

- `/` — Home
- `/services` — capabilities overview
- `/services/odoo`
- `/services/software`
- `/services/ai-automation`
- `/process`
- `/labs`
- `/about`
- `/contactus`

The implementation must not use upgrade-sensitive `website.page` data that overwrites editorial edits on every `-u`. Prefer theme page templates/page presets supported by Odoo 19; where initial records are required, use `noupdate` semantics and stable XML IDs so that user edits survive upgrades.

### Header, footer and navigation

Keep `website.menu` canonical. The theme may style header/footer and provide an initial menu skeleton, but it must not encode navigation logic in QWeb. Required public navigation:

- Services
- Process
- Labs
- About
- Start Project

The primary CTA points to `/start` when the lead-generator addon is present. The theme must remain independently installable; therefore any CTA authored in theme content must degrade safely to `/contactus` or remain editable without requiring the business addon.

## Public content direction

The site should feel like a digital studio rather than a generic consultancy. Copy should be concise, technically credible, slightly irreverent and action-oriented. The visual identity remains violet-led with spark colors used as accents rather than as the base palette.

Home composition:

1. Hero
2. What We Build
3. Project Signal teaser
4. Services
5. How We Work
6. Labs / Selected Work
7. Philosophy
8. Start Project CTA

## Lead-generator architecture

### Discovery

Keep the existing `/start` flow and six-step progressive disclosure pattern. M2 refines copy, validation, keyboard behavior, draft recovery and success/error states without turning the flow into a long conventional form.

The browser may keep a recoverable draft for UX, but Odoo remains the source of truth after submission.

### CRM enrichment

`crm.lead` remains canonical. M2 adds only fields that are not already adequately represented by standard CRM. The Monynha Discovery area should expose:

- discovery version
- brand/project context
- business/revenue model
- operating/decision profile
- current pain
- public digital presence
- latest Project Signal dimensions
- latest diagnosis state
- recommended next commercial action

Computed or related fields are preferred where data already exists in `monynha.lead.diagnosis`.

### Diagnosis

Keep `monynha.lead.diagnosis` append-only. `local_rules` remains the default provider and must produce a useful result without external AI.

M2 extends normalized diagnosis output with explicit opportunity recommendations and a recommended next step. Example normalized fields:

- `score`
- `digital_maturity`
- `automation_potential`
- `process_clarity`
- `odoo_fit`
- `signals`
- `opportunities`
- `recommended_action`

The provider registry remains the extension point for future AI-specific addons.

### Retry and failure handling

A failed diagnosis never deletes or rolls back the lead. Failed diagnoses remain auditable. CRM users can retry a failed diagnosis by creating or reprocessing a diagnosis according to the existing history model without overwriting completed history.

### Project Signal

The public Project Signal must be useful enough to justify the visitor's time. It displays:

- overall signal score
- four dimensions
- concise explanation
- evidence/signals derived from answers
- opportunities
- suggested route / next action
- commercial CTA

The public route continues using the secure diagnosis token and never exposes sequential lead IDs or internal CRM data.

### Commercial next action

M2 connects Project Signal to standard Odoo commercial follow-up instead of inventing another workflow.

When the visitor requests follow-up from a Project Signal:

1. the action is written to the existing `crm.lead`;
2. an internal CRM activity is scheduled for the appropriate sales user/team when one can be resolved safely;
3. the visitor receives a confirmation using `mail.template`;
4. the public response does not expose CRM internals.

Do not auto-create quotations in M2. Opportunity conversion and quotation creation remain standard CRM/Sales actions for a human user.

## Labs and selected work

M2 does not introduce a custom project/CMS model. Labs and selected work remain editorial Website content for now. A dedicated model is deferred until there is a concrete filtering, ownership, workflow or API requirement that Website pages/snippets cannot satisfy.

## JavaScript boundaries

Use frontend JavaScript only for interaction that benefits from it:

- discovery wizard state and keyboard navigation
- draft recovery
- progress/transitions
- reduced-motion-aware Spark effects
- optional Project Signal microinteractions

Institutional page navigation remains normal Odoo Website navigation. Avoid global animation loops and large third-party libraries.

## Security and privacy

- Public endpoints accept explicit whitelisted fields only.
- Server-side validation is authoritative.
- Honeypot/anti-spam behavior remains in the discovery flow.
- Public report and follow-up endpoints use secure non-sequential tokens.
- `sudo()` is restricted to narrow server-assembled values required to create/update the public lead workflow.
- Raw provider payload and technical errors remain restricted to internal/system users.
- Public pages link to appropriate privacy information and avoid collecting data without a clear commercial purpose.

## Accessibility and performance

Required acceptance behavior:

- all interactive discovery steps usable by keyboard;
- visible focus states;
- semantic labels and accessible validation messages;
- no required motion for comprehension;
- `prefers-reduced-motion` disables nonessential animation;
- mobile layout has no horizontal overflow;
- touch targets are usable at common mobile widths;
- no persistent high-frequency canvas/particle loop;
- no unnecessary external JS/CSS dependencies.

## Testing strategy

### Theme

- clean install of `theme_monynha` alone;
- upgrade of `theme_monynha` alone;
- XML/QWeb loading;
- asset compilation;
- snippet registration;
- required page starter/menu records where applicable;
- no dependency on `monynha_lead_generator`;
- reduced-motion styles present;
- no source-database IDs.

### Lead generator

- clean install and upgrade;
- `/start` route;
- public submission -> `crm.lead` -> diagnosis;
- validation and whitelist enforcement;
- local rules normalized output;
- diagnosis failure preserves the lead;
- retry behavior;
- secure public report token;
- Project Signal opportunities/recommended action;
- follow-up request creates the expected CRM-side action without leaking data;
- ACLs and internal-only technical fields.

### End-to-end

Validate the core journey:

`Home -> Start Project -> complete discovery -> crm.lead -> diagnosis -> Project Signal -> request follow-up -> CRM activity/lead update`

GitHub Actions remains the clean-install/upgrade gate on the official Odoo 19 image and PostgreSQL 16.

## Delivery slices

### Slice 1 — Website system

Expand design tokens/components/snippets, add safe page starters and style header/footer/navigation. Deliver a coherent site that still works with the theme installed alone.

### Slice 2 — Rich Project Signal

Extend local scoring normalization, diagnosis fields and public report with opportunities and recommended action while preserving append-only history.

### Slice 3 — Commercial follow-up

Add the public follow-up action from Project Signal to standard `crm.lead` and CRM activities/mail templates.

### Slice 4 — End-to-end hardening

Add regression tests, accessibility/mobile refinements, install/upgrade validation, documentation and PR review fixes.

## Definition of done

M2 is complete when:

- the public Monynha website is coherent and buildable from reusable Odoo Website components;
- `theme_monynha` still installs independently;
- a visitor can navigate from Home to `/start` without dead ends;
- discovery creates a standard CRM lead;
- the default local provider creates a useful Project Signal with explicit opportunities;
- the visitor can request a follow-up from the report;
- that request produces a standard CRM-side next action;
- failures do not lose leads or overwrite diagnosis history;
- both addons pass clean install and upgrade CI on Odoo 19;
- user-edited Website content is not overwritten by module upgrade;
- no React, Supabase or mandatory external AI dependency is introduced.
