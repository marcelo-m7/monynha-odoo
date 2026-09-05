# Monynha M3 — Theme Completion Design

Date: 2026-09-05
Status: proposed for implementation
Repository: `marcelo-m7/monynha-odoo`
Scope: `theme_monynha` only
Base: merged M2 on `96c03e92a54ca9ca4e4f32a1307fd9bba36949ce`

## 1. Goal

Complete `theme_monynha` as a polished Odoo 19 Community Website theme for Monynha Softwares while preserving Odoo-native ownership of pages, navigation, editing and upgrades.

M3 should make the public site feel like a finished Monynha presence rather than a starter theme. It must strengthen identity, hierarchy, editorial quality, responsiveness and visual consistency without creating a parallel frontend or CMS.

## 2. Architectural decision

Use an **Odoo-native branded theme**.

The implementation keeps:

- `website.layout` as the page shell;
- standard Odoo Website header/footer rendering;
- `theme.website.page` for seeded editable pages;
- `theme.website.menu` for navigation seeds;
- `configurator_snippets` for homepage composition;
- Website Builder as the canonical editor after installation;
- standard Website SEO/social metadata mechanisms where configuration is required.

The theme contributes presentation, starter content, reusable snippets and static brand assets. It does not replace Odoo Website routing, menu rendering, footer ownership or content storage.

## 3. Explicit boundaries

M3 must not:

- depend on `monynha_lead_generator`;
- introduce React, Vue, iframe applications, Framer Motion or another frontend runtime;
- create business models such as `monynha.project`, `monynha.lab` or a parallel CMS;
- hardcode database IDs;
- replace the standard Website navbar/menu tree with a custom navigation implementation;
- overwrite user-edited Website Builder content on normal module upgrades;
- fabricate clients, testimonials, revenue metrics or commercial case-study claims;
- add mandatory external APIs, font services or image CDNs.

`/start` remains a theme-only fallback. When `monynha_lead_generator` is installed, its controller continues to own the interactive discovery route.

## 4. Brand direction

The visual language revives the historical Monynha identity as **brutalist futurism** adapted to Odoo Website.

Core visual vocabulary:

- deep void/black surfaces;
- violet as the primary interaction accent;
- paper/light sections for contrast and editorial rhythm;
- cyan/blue/teal only as secondary accents;
- Space Grotesk-style display typography with Inter/system-safe body typography;
- thick borders and hard shadows;
- selective outlined display text;
- asymmetrical cards and strong section rhythm;
- signal/terminal/system motifs;
- subtle blur/glow/gradient atmosphere where it does not reduce readability.

Motion is decorative and CSS-only. Every non-essential motion effect must be disabled or simplified under `prefers-reduced-motion`.

## 5. Homepage

The homepage remains created through Odoo's theme configurator lifecycle rather than a direct `website.page` seed for `/`.

Target composition:

1. Hero
2. Project Signal
3. Capabilities
4. Selected Work
5. Operating Principles
6. Labs / Open Source
7. Manifesto
8. Final CTA

### 5.1 Hero

The hero becomes the primary brand statement.

Content direction:

- Monynha wordmark treatment: `MONYNHA / SOFTWARES`;
- headline: `Where Engineering Meets Intuition`;
- short explanation of Odoo, custom software and applied automation;
- primary CTA: `Start a Project` -> `/start`;
- secondary CTA: `Explore Labs` -> `/labs`.

The hero may use CSS-only decorative grids, glow fields, spark marks or outlined typography. It must remain legible without animation.

### 5.2 Project Signal

Keep the existing theme-level signal snippet independent of the lead generator. It should visually explain the Monynha discovery approach without assuming diagnosis records or JS APIs.

It may describe dimensions such as operation, friction, integration and automation opportunity, but must not simulate a real generated score.

### 5.3 Capabilities

Present the three stable service areas:

- Odoo;
- Custom Software;
- AI & Automation.

Each capability links to its dedicated seeded page and uses the same design vocabulary as those pages.

### 5.4 Selected Work

Only real or explicitly editorial projects may be shown. Initial project references can include:

- FACODI;
- Codoo Importer;
- Monynha Odoo.

Cards must describe the type of work without inventing client outcomes or unverified metrics.

### 5.5 Operating Principles

Express the engineering principles already present in the project:

- standard first;
- smallest useful system;
- observable interfaces and data;
- build, verify, observe, improve;
- automation with explicit boundaries.

### 5.6 Labs / Open Source

Use Website content rather than a new data model. The section should point visitors to `/labs` and describe Labs as an editable showcase for experiments, tooling and open work.

### 5.7 Manifesto and CTA

Close with a concise editorial statement around engineering, intuition and usefulness, then route visitors to `/start`.

## 6. Global header and navigation

The standard Odoo Website header remains canonical.

The theme may:

- style `header#top`, `.navbar`, `.navbar-brand`, `.nav-link`, dropdowns and mobile navigation;
- provide a Monynha wordmark/logo asset compatible with standard Website branding;
- visually distinguish the `Start Project` menu item as the main CTA using CSS selectors/classes available from standard markup;
- style active, hover and focus states consistently;
- preserve standard dropdown/mobile accessibility behavior.

The theme must not render a hardcoded menu tree in a parallel QWeb header.

## 7. Global footer

The standard Odoo footer lifecycle remains canonical.

M3 may style the footer and seed/edit theme-owned footer presentation only through supported Website/theme mechanisms. The intended visual result is:

- dark Monynha surface;
- concise studio statement;
- standard navigation/contact/social links where records already exist or are editorially provided;
- visible link focus/hover states;
- no duplicated navigation system.

If a branded footer content seed cannot be implemented without taking destructive ownership of user content, M3 must limit itself to styling.

## 8. Seeded public pages

Existing M2 pages remain Odoo `theme.website.page` starters and are refined, not replaced by custom controllers.

### Services `/services`

A clear overview of Odoo, Software and AI/Automation with shared capability cards and links to detail pages.

### Odoo `/services/odoo`

Emphasize:

- standard Odoo mechanisms first;
- addon architecture only for concrete gaps;
- portals and Website;
- integrations and APIs;
- data migration/normalization;
- workflow automation.

### Software `/services/software`

Emphasize:

- internal tools;
- web products;
- operational interfaces;
- APIs/integrations;
- small, understandable system boundaries.

### AI & Automation `/services/ai-automation`

Emphasize:

- contextual automation;
- ingestion/enrichment/classification;
- replaceable providers;
- human-in-the-loop decisions;
- fallbacks and observability.

### Process `/process`

Keep the core lifecycle:

`Discovery -> Architecture -> Build -> Observe`

Improve visual storytelling and connect the process back to `/start`.

### Labs `/labs`

Remove starter placeholders such as `Open slot` / `Próximo experimento`.

Initial editable content should use real projects such as FACODI, Codoo Importer and Monynha Odoo. Labs remains ordinary Website content.

### About `/about`

Present Monynha as a digital engineering studio, not a personal biography. Include mission, principles and a concise `engineering meets intuition` narrative.

### Start `/start`

Keep the safe standalone fallback explaining discovery and linking to `/contactus`. Do not duplicate lead-generator UI.

## 9. Reusable snippet layer

M3 should finish the snippet catalogue rather than make pages one-off compositions.

Existing snippets remain reusable. Add or refine only components needed by the final pages, potentially including:

- brand/wordmark hero;
- capability matrix;
- operating-principles grid;
- labs/open-source showcase;
- editorial split section;
- compact contact/final CTA;
- branded footer/editorial utility section if Odoo ownership allows it safely.

Each snippet must:

- appear in the Monynha snippet group;
- use editable Website content rather than hardwired data dependencies;
- render acceptably standalone;
- work on mobile without horizontal overflow;
- preserve semantic heading order when used as intended.

## 10. Static brand assets

M3 may add theme-owned static assets such as:

- Monynha wordmark/logo SVG;
- favicon SVG/PNG if required by the supported Odoo Website mechanism;
- theme preview artwork;
- social-preview artwork only when it can be used through standard Website metadata configuration without hardcoding production host assumptions.

Assets must be self-contained in the addon. Do not add font binaries to the repository solely for this work; use safe stacks and the existing typographic approach unless Odoo provides a standard web-font mechanism already present in the theme stack.

## 11. SEO and metadata

M3 should improve starter-page titles and descriptions using Odoo Website/QWeb-supported metadata patterns.

Requirements:

- meaningful page titles;
- sensible descriptions for main seeded pages;
- no fake schema.org claims;
- no hardcoded canonical host where Odoo can generate it dynamically;
- social metadata only through standard Odoo Website mechanisms or harmless template metadata.

SEO changes must remain editable after installation where standard Website ownership permits it.

## 12. Responsive and accessibility requirements

The theme must explicitly support:

- desktop, tablet and narrow mobile layouts;
- standard mobile navbar behavior;
- no horizontal overflow from display typography or hard shadows;
- minimum practical touch targets for main CTAs;
- visible `:focus-visible` states;
- meaningful contrast on dark and light sections;
- semantic links/buttons instead of click-only containers;
- decorative elements with `aria-hidden="true"`;
- `prefers-reduced-motion: reduce` coverage for every M3 animation/transition class;
- no JS required for core navigation or content access.

## 13. Upgrade and Website Builder safety

M3 must preserve the M2 ownership model.

Rules:

- seeded pages use `theme.website.page`;
- navigation uses `theme.website.menu`;
- homepage continues through `configurator_snippets`;
- upgrades must not replace user-owned `website.page` bodies with direct data writes;
- no post-init hook that rewrites public pages;
- no source-database IDs;
- clean install and `-u theme_monynha` both remain CI gates.

## 14. Testing strategy

M3 implementation follows TDD.

### Contract tests

Add assertions for:

- M3 snippet registration;
- no dependency on `monynha_lead_generator`;
- homepage configurator composition;
- no direct homepage `website.page` seed;
- absence of known starter placeholder text;
- brand asset presence;
- reduced-motion coverage;
- no external frontend framework imports;
- no hardcoded DB IDs or production-only host assumptions.

### Odoo theme tests

Validate:

- all `theme.website.page` records load;
- menu hierarchy loads;
- M3 snippets resolve by XML ID;
- install succeeds with theme alone;
- upgrade succeeds with theme alone;
- combined install with lead generator remains valid.

### Runtime/HTML checks

Where practical in the existing CI shape, verify rendered public routes return successful responses after installation.

## 15. Documentation

Update `README.md` and create `docs/m3-theme-completion.md` describing:

- theme ownership boundaries;
- final route map;
- homepage composition;
- branding/design-system principles;
- how Website Builder editors should customize Labs, Selected Work and page content;
- how `/start` behaves with and without `monynha_lead_generator`.

## 16. Acceptance criteria

M3 is ready only when:

- `theme_monynha` remains independently installable on Odoo 19 Community;
- homepage composition reads as a finished Monynha site rather than starter content;
- no known placeholder content remains in Labs/public starters;
- header/footer retain standard Odoo rendering and behavior;
- service/process/about/labs pages are editorially coherent and editable;
- Monynha visual identity is consistent across dark/light sections, cards and CTAs;
- mobile layout and reduced-motion behavior are covered by tests/contracts;
- clean install and theme-only upgrade are green;
- combined theme + lead-generator regression remains green;
- no M3 change introduces a new business model, CMS, JS framework or external runtime dependency;
- exact-head CI is green before the PR is marked ready for review.
