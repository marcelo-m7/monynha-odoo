# M3 — Monynha Theme Completion

## Scope

M3 completes `theme_monynha` as a polished Odoo 19 Community Website theme while preserving the ownership boundaries established in M2.

The theme owns presentation, reusable Website Builder snippets, starter content and static brand assets. Odoo Website remains the canonical owner of page copies, navigation, header/footer rendering and editorial changes after installation.

`monynha_lead_generator` is unchanged by M3 and remains independently installable.

## Ownership map

| Concern | Owner |
| --- | --- |
| Homepage starter | `configurator_snippets` in `theme_monynha` |
| Public page starters | `theme.website.page` |
| Installed/editable page copies | standard `website.page` |
| Initial navigation seed | `theme.website.menu` |
| Installed/editable navigation | standard `website.menu` |
| Header/footer markup and behavior | standard Odoo Website |
| Header/footer visual identity | `theme_monynha` SCSS |
| Labs and Selected Work | editable Website content |
| Interactive discovery | `monynha_lead_generator` when installed |
| Theme-only `/start` | safe editable fallback page |

No M3 mechanism writes directly into user-owned page bodies after installation.

## Homepage

The final homepage is composed through the Odoo theme configurator in this order:

1. Hero
2. Project Signal
3. Capabilities
4. Selected Work
5. Operating Principles
6. Labs / Open Work
7. Manifesto
8. Final CTA

The homepage is not seeded as a direct `website.page` record for `/`. This keeps the standard Odoo configurator lifecycle and Website Builder ownership intact.

### Hero

The hero uses the self-contained Monynha wordmark and the statement:

`Where Engineering Meets Intuition`

Primary actions:

- `Start a Project` → `/start`
- `Explore Labs` → `/labs`

Decorative motion is CSS-only and non-essential. Reduced-motion users receive the same content without animation.

### Project Signal

The theme-level Project Signal explains the discovery lens without pretending to show a generated diagnosis. It presents four editorial dimensions:

- Operation
- Friction
- Integration
- Automation

No fake numeric score is rendered by the theme snippet.

### Selected Work and Labs

M3 uses real editorial project references:

- FACODI
- Codoo Importer
- Monynha Odoo

These are ordinary Website content cards. They are not backed by a `monynha.project`, `monynha.lab` or another parallel CMS model.

Editors can replace or reorder them directly through Website Builder when the active work changes.

## Public route map

### `/services`

Overview of the three stable capabilities:

- Odoo
- Custom Software
- AI & Automation

### `/services/odoo`

Standard-first Odoo delivery, including addon architecture, Website/Portal, APIs, migration/normalization and operational automation.

### `/services/software`

Focused web products, internal tools, APIs and integration adapters with small, understandable boundaries.

### `/services/ai-automation`

Contextual automation with replaceable providers, explicit fallbacks, observability and human review where decisions matter.

### `/process`

The public working method remains exactly:

`Discovery → Architecture → Build → Observe`

### `/labs`

Editable showcase for FACODI, Codoo Importer, Monynha Odoo and future experiments. It remains Website content, not a data model.

### `/about`

Studio-level mission and engineering principles around the idea `Where Engineering Meets Intuition`. It is intentionally not a personal biography.

### `/start`

With only `theme_monynha`, `/start` is an editable fallback page that links to the standard `/contactus` route.

When `monynha_lead_generator` is installed, its explicit controller owns the interactive `/start` discovery flow. The theme does not duplicate the wizard markup.

## Header and footer

M3 does not replace Odoo's header or footer QWeb structures.

The theme styles standard selectors such as:

- `header#top`
- `.navbar`
- `.nav-link`
- `.dropdown-menu`
- `.navbar-collapse`
- `footer#bottom`
- `footer.o_footer`

The canonical `/start` menu entry is visually promoted as the primary CTA with CSS only. Dropdown and mobile navigation behavior remains standard Odoo behavior.

## Visual system

M3 consolidates the historical Monynha brutalist-futuristic identity into Odoo-native assets and SCSS:

- void/black and night surfaces;
- violet as the main interaction accent;
- paper sections for editorial contrast;
- cyan as a secondary signal accent;
- thick borders and hard shadows;
- Space Grotesk-style display stack and Inter/system body stack;
- cards, terminal and signal motifs;
- lightweight decorative grid/orbit effects.

No external font binary, animation runtime or frontend framework is required by the theme.

## Responsive and accessibility behavior

M3 explicitly protects:

- visible `:focus-visible` states;
- standard semantic links/buttons;
- minimum practical CTA heights;
- mobile navbar behavior inherited from Odoo;
- `clamp()` display typography;
- `minmax(0, 1fr)` grids where overflow is possible;
- `overflow-wrap: anywhere` for long editorial labels/content;
- smaller hard-shadow tokens on narrow screens;
- decorative M3 orbit elements marked `aria-hidden="true"`;
- `prefers-reduced-motion: reduce` overrides for decorative animation and interaction transforms.

Core navigation and content remain available without JavaScript.

## Website Builder editing guidance

After installation:

1. Use **Website → Edit** to change the installed page copies.
2. Reorder Monynha blocks exactly like standard Odoo snippets.
3. Edit Labs/Selected Work text directly in the page; do not create a parallel project model just to manage marketing cards.
4. Manage the installed menu in standard Website menu tools. `theme.website.menu` is only the initial seed.
5. Keep the `/start` fallback useful for a theme-only installation. Do not copy the lead-generator wizard into the theme.
6. Prefer changing content through Website Builder rather than writing data migrations that overwrite existing page bodies.

## Upgrade safety

The M3 ownership rules are designed so that a clean installation and a normal module upgrade do not require database-specific IDs or post-install rewriting of Website content.

Release validation covers:

- theme-only clean installation;
- lead-generator-only installation/regressions;
- combined clean installation;
- combined module upgrade and regression tests.

`theme_monynha` still has no dependency on `monynha_lead_generator`, and `monynha_lead_generator` still has no dependency on `theme_monynha`.
