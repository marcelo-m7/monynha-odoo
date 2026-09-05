# M2 — End-to-End Monynha Journey

## Scope

M2 turns the M1 lead generator into a complete Odoo-native public and commercial journey while keeping the theme and CRM addons independent.

## Website ownership

`theme_monynha` owns presentation only. Page starters are declared with `theme.website.page` and navigation seeds with `theme.website.menu`, following Odoo's theme conversion mechanism. Once installed, the resulting `website.page` and `website.menu` records are normal Website content and can be edited through Website Builder.

The theme does not create a parallel CMS for Labs or Selected Work. These remain editable website sections until a concrete workflow requirement justifies a dedicated model.

## Route behavior

### Theme only

`/start` resolves to the theme's editable fallback page and points visitors to `/contactus`.

### Theme + lead generator, or lead generator alone

`monynha_lead_generator` declares the explicit `/start` controller and serves the six-step discovery wizard. The theme remains optional.

## Discovery lifecycle

1. Browser keeps a recoverable `monynha_discovery_draft_v1` draft only for UX.
2. Client submits the explicit discovery payload to `/monynha/discovery/submit`.
3. Server rejects unknown fields and validates email, project/name state, revenue model, operating style and struggle text.
4. Server creates `crm.lead` first.
5. The lead creates an append-only `monynha.lead.diagnosis`.
6. `local_rules` produces normalized Project Signal output.
7. The public report is available through a high-entropy diagnosis token.
8. Diagnosis-ready email is queued using `mail.template`.

A diagnosis failure does not roll back or remove the lead.

## Project Signal

`local_rules` remains deterministic and transparent. It calculates:

- digital maturity;
- automation potential;
- process clarity;
- Odoo fit;
- overall signal;
- explanatory signals;
- explicit opportunities;
- one recommended next action.

Recommended actions are normalized to `clarify`, `automate`, `centralize`, `integrate`, or `architecture`.

The result is guidance for discovery and architecture. It is not a prediction of sales probability and does not automatically change CRM stages.

## Follow-up lifecycle

The public Project Signal contains a progressive-enhancement CTA. Without JavaScript it remains a normal `/contactus` link. With the frontend asset loaded it calls `/monynha/diagnosis/followup` with only the secure diagnosis token.

On the first valid request:

- `crm.lead.monynha_followup_requested_at` is set;
- an internal chatter note is added;
- if the lead has `user_id`, that user receives a standard Todo activity;
- otherwise the sales-team leader is used when configured;
- if neither exists, no arbitrary fallback user is assigned;
- a visitor confirmation email is queued when an email exists.

Repeated requests are idempotent and do not create duplicate activities or repeated confirmation mail.

## Public-data boundary

The public report may render normalized scores, summary, signals, opportunities and recommended action. It must not render:

- lead IDs;
- raw provider payloads;
- technical error messages;
- internal CRM notes;
- salesperson/team internals;
- visitor email or other unnecessary PII.

## Accessibility

The discovery flow includes:

- semantic fieldsets and labels;
- `aria-live` validation/status messages;
- textual and visual step progress;
- `role="progressbar"` with dynamic values;
- `aria-pressed` choice states;
- Enter/Escape keyboard navigation;
- double-submit prevention;
- focus behavior that avoids forcing focus on coarse-pointer devices;
- reduced-motion CSS.

## Upgrade behavior

Both addons are tested through clean installation and `-u` in CI. Theme records use Odoo's theme models instead of direct database-specific page/menu IDs. User-edited Website content must remain under Website Builder ownership across upgrades.

## Extension rule

Future AI providers should be separate addons that extend the diagnosis provider registry. `monynha_lead_generator` must remain installable and useful without provider credentials or third-party SDKs.
