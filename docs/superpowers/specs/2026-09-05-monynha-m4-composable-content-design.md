# Monynha M4 — Composable Content & Website Builder Design

## Status

Approved design for M4 of `marcelo-m7/monynha-odoo`.

M4 extends the completed M3 Odoo-native branded theme into a reusable Monynha composition system while preserving Odoo Website, Website Builder, Blog, SEO, publication, security, and standard layout ownership.

The implementation must remain upgrade-safe, independently installable by module boundary, and must not introduce a parallel frontend or a generic cross-project design system.

## Goals

M4 must:

1. turn `theme_monynha` into a reusable Monynha Website Builder composition kit;
2. add reusable static snippets, smaller visual primitives, and page starters;
3. add structured public content for Projects, Cases, and Labs without turning the theme into a CMS;
4. reuse Odoo standard Blog for Insights/Articles;
5. keep institutional pages Website Builder-owned;
6. provide dynamic snippets backed by real Odoo records;
7. preserve independent installation of `theme_monynha` and `monynha_lead_generator`;
8. remain safe for clean install, upgrade, multi-website use, public access, and future extension.

## Non-goals

M4 does not:

- create a generic design system for FACODI or other websites;
- introduce React, Vue, a SPA, iframe-based rendering, or a parallel CMS;
- replace `website.layout`, the standard header/footer, Website Builder, Blog, publication, SEO, or Odoo security;
- create separate models for Projects, Cases, and Labs;
- create a custom article CMS when `website_blog` already owns that domain;
- create a public API for Work content;
- add invented customers, testimonials, commercial results, metrics, or placeholder portfolio entries;
- make `theme_monynha` depend on the structured-content addon.

## Architectural decision

M4 uses two layers:

```text
monynha-odoo/
├── theme_monynha/
│   ├── design tokens
│   ├── primitives
│   ├── reusable static snippets
│   ├── page starters
│   └── Website Builder integration
│
├── monynha_content/
│   ├── structured Work models
│   ├── public routes
│   ├── backend management
│   ├── public listing/detail views
│   └── dynamic snippets
│
└── monynha_lead_generator/
    └── remains independent
```

Dependency direction:

```text
theme_monynha
 └── theme_common + website

monynha_content
 └── theme_monynha + website + website_blog

monynha_lead_generator
 └── remains independent from monynha_content
```

`monynha_content` depends on `theme_monynha`, not the opposite. The theme therefore remains a valid standalone Monynha website theme.

## Content ownership

### Website Builder-owned content

The following remain normal Website pages and page starters:

- Landing pages;
- Services;
- About;
- Contact;
- institutional pages;
- documentation-style pages when a normal Website/eLearning mechanism is sufficient.

These must continue to use `theme.website.page`, `website.layout`, `oe_structure`, standard Odoo forms/components, and Website Builder editing.

### Blog-owned content

Insights and Articles remain `website_blog` / `blog.post` content.

M4 may style, aggregate, and expose Blog records through Monynha components and snippets, but it must not duplicate article data into a Monynha model.

### Structured Work content

Projects, Cases, and Labs share one model:

```text
monynha.work
```

with a type field:

```text
project
case
lab
```

This avoids three nearly identical models, controllers, forms, route implementations, and card components.

## `monynha.work` model

The model is a structured editorial record exposed on the website through Odoo Website mechanisms.

### Core fields

The minimum public/editorial contract is:

- `name`;
- `type` — selection: `project`, `case`, `lab`;
- `summary`;
- `body_html`;
- cover image compatible with standard Odoo image conventions;
- `tag_ids`;
- `sequence`;
- `featured`;
- publication date;
- `website_id`;
- optional repository URL;
- optional external URL;
- publication metadata;
- SEO metadata.

Implementation should reuse Odoo Website mixins where appropriate rather than recreating publication, SEO, or website ownership behavior.

Expected standard capabilities include:

- website-aware publication;
- SEO metadata;
- public-search compatibility when practical;
- website-aware URL generation.

### Tags

Use a single lightweight `monynha.work.tag` model.

It may contain only what the catalogue currently needs, such as:

- name;
- sequence;
- color or equivalent display metadata.

Do not introduce separate models for technology, industry, stack, category, capability, or platform until a concrete requirement justifies them.

### Hybrid authorship

Metadata is structured in `monynha.work`.

The narrative body remains editable as rich website content:

```text
cover / metadata / tags
        ↓
body_html editable content
        ↓
related work
        ↓
CTA / navigation
```

The detail page must set the Work record as the website page's main object where required by Odoo editing/SEO conventions.

Editors can therefore change the body without destroying publication, routing, tags, or related-content structure.

## Public routes

Approved public routes:

```text
/work
/projects
/cases
/labs
/work/<slug>
```

Behavior:

- `/work` lists all published Work records for the current website;
- `/projects` filters `type = project`;
- `/cases` filters `type = case`;
- `/labs` filters `type = lab`;
- `/work/<slug>` renders the shared detail template for all Work types.

The implementation should use Odoo's record slug conventions rather than introducing a manually maintained second slug field unless testing proves a concrete incompatibility.

Public controllers must:

- return 404 for unknown records;
- return 404 to public users for unpublished records;
- respect the current website;
- avoid leaking records from another website;
- use server-side pagination;
- support type/tag filtering without requiring JavaScript;
- use progressive enhancement only where interaction genuinely benefits from frontend code.

There is no M4 public API.

### Route ownership and theme-only fallback

M3 already provides a static `/labs` Website page in `theme_monynha`. M4 must preserve the same fallback pattern already used by `/start` and `monynha_lead_generator`:

- with only `theme_monynha` installed, `/labs` remains the existing editable Website page;
- when `monynha_content` is installed, its `/labs` catalogue route becomes the active structured Labs experience;
- uninstalling `monynha_content` restores the theme-only `/labs` fallback without requiring a theme data migration;
- this ownership rule must be covered by HTTP/integration tests.

No static theme page should be introduced at `/work`, `/projects`, or `/cases`, because those routes belong exclusively to `monynha_content`.

## Theme composition system

M4 evolves the existing M2/M3 snippets into a clearer composition hierarchy:

```text
design token
    ↓
primitive
    ↓
component
    ↓
snippet
    ↓
page starter
```

New work should reuse existing M2/M3 patterns instead of replacing them wholesale.

### Primitive layer

The SCSS/component vocabulary should support reusable primitives such as:

```text
.monynha-section
.monynha-container
.monynha-stack
.monynha-cluster
.monynha-grid
.monynha-split

.monynha-card
.monynha-card--dark
.monynha-card--outlined
.monynha-panel
.monynha-terminal

.monynha-button
.monynha-link
.monynha-tag
.monynha-kicker
.monynha-meta
.monynha-eyebrow
```

Names may be adjusted when required by existing code conventions, but the architectural intent is mandatory: new snippets should mostly compose shared primitives rather than grow independent one-off CSS systems.

### Static snippet families

#### Structure and narrative

Provide reusable Website Builder blocks for:

- Hero variants: dark, light, split;
- Page Intro;
- Section Header;
- Manifesto / Statement;
- Long-form Intro;
- Split Content;
- Image + Copy;
- Quote / Pull Quote;
- Numbered Steps;
- Process Timeline;
- Principles Grid;
- FAQ;
- Closing CTA.

#### Commercial and product-oriented blocks

Provide reusable blocks for:

- Services Grid;
- Capability Card / capability composition;
- Feature Grid;
- Integration / Technology Grid;
- Deliverables List;
- Engagement / Scope block;
- Comparison block;
- Project Signal;
- Contact / Start Project CTA;
- technology badge group;
- terminal/code-style panel.

Defaults must be neutral and truthful. No fake projects, metrics, customer names, testimonials, or commercial outcomes are allowed.

## Dynamic snippets

Dynamic snippets belong to `monynha_content`, because they depend on structured records.

Initial dynamic blocks:

- Featured Work;
- Work Grid;
- Latest Projects;
- Selected Cases;
- Latest Labs;
- Related Work;
- Work Tags;
- Work Metadata;
- Work Navigation;
- Latest Insights;
- Insights Grid.

### Query behavior

Shared query logic must be centralized so that dynamic snippets do not each implement slightly different versions of publication, website filtering, ordering, type filtering, or limits.

Supported selection concepts include:

- type;
- tag;
- featured;
- quantity/limit;
- ordering.

Simple listings must render server-side. JavaScript is not required merely to display records.

### Empty states

Dynamic snippets must degrade safely:

- no fake placeholder cards;
- no broken images;
- no visible demo metrics;
- no 500 when content is absent;
- empty collections may hide the content area or render an intentionally neutral empty state where appropriate.

### Blog integration

`Latest Insights` and `Insights Grid` read published `blog.post` records.

```text
website_blog
    ↓
blog.post
    ↓
Monynha presentation component
    ↓
Website snippet
```

Blog remains the source of truth.

## Page starters

M4 adds reusable Monynha starting compositions. They are starting points, not rigid page types.

| Starter | Initial composition |
| --- | --- |
| Landing | Hero → context/proof → capabilities → work → CTA |
| Service | Intro → problem → capability → process → FAQ → CTA |
| About | Intro → manifesto → principles → process → CTA |
| Contact | Intro → contact/context → standard Odoo form → CTA |
| Work catalogue composition | Intro → Work catalogue block → CTA |
| Project/Case composition | Intro → metadata-style block → narrative → related-work-style block → CTA |
| Lab composition | Intro → experiment context → body → related-Labs-style block |
| Insight index | Intro → standard Blog feed |
| Documentation | Intro → navigation/content → related resources |
| Changelog | Intro → chronological entries |

The Work/Project/Case/Lab entries in this table are **static composition starters** available from the theme. They do not own the structured public routes and do not query `monynha.work` unless the corresponding dynamic blocks from `monynha_content` are explicitly used. Structured `/work*` and `/labs` catalogue/detail pages remain owned by `monynha_content` as defined above.

Existing M3 pages remain valid and should be refactored only when doing so directly improves reuse or consistency. M4 is not a rewrite of the existing site.

## Responsive and accessibility contract

M4 must preserve and extend the M3 hardening:

- one semantic markup structure for responsive layouts;
- fluid `clamp()` sizing where appropriate;
- `minmax(0, 1fr)` for grid tracks where overflow risk exists;
- `min-width: 0` for flexible children where needed;
- safe text wrapping;
- no horizontal-page overflow;
- visible `:focus-visible` states;
- accessible labels/names for interactive elements;
- decorative elements marked appropriately;
- support for `prefers-reduced-motion`;
- motion must remain optional presentation, never a functional dependency.

Do not create separate desktop/mobile templates for the same component.

## Security

Security must follow Odoo conventions, not controller-side improvisation.

Requirements:

- explicit ACLs for Work and Work tags;
- public routes expose only public/published records for the current website;
- no public write routes;
- avoid generalized `sudo()` in controllers;
- any required elevated read must remain narrowly scoped and followed by explicit website/publication domains;
- backend editing must use appropriate standard Website/editor groups;
- multi-website data must not leak through lists, detail routes, related content, or snippets.

## Error handling

Expected public behavior:

- unknown Work slug → 404;
- unpublished Work for public user → 404;
- Work assigned to another website → unavailable on current website;
- invalid/unknown filter → predictable empty/ignored filter behavior, never 500;
- missing cover image → valid layout without a broken-image element;
- no Blog posts → Insights snippets degrade gracefully;
- `monynha_content` not installed → all static theme pages/snippets continue to function;
- `monynha_lead_generator` remains independent.

## Installation boundaries

The following must remain true:

1. `theme_monynha` installs and upgrades by itself.
2. `monynha_lead_generator` installs independently of `monynha_content`.
3. `monynha_content` installs with its declared dependencies.
4. `theme_monynha + monynha_content` works as the structured-content website stack.
5. `theme_monynha + monynha_lead_generator` continues to work.
6. all Monynha modules can coexist in one database.
7. uninstalling `monynha_content` must not remove the theme's institutional presence or static snippets.

## Testing strategy

M4 follows the RED → GREEN → regression workflow already used in M2/M3.

### Contract tests

Cover at least:

- dependency direction;
- theme independence from `monynha_content`;
- lead-generator independence;
- expected module manifests and data files;
- static snippets do not reference optional content models;
- no fake customers/testimonials/results/metrics in shipped defaults;
- required page starters/snippets are registered.

### Model tests

Cover at least:

- Work creation;
- valid type values;
- tags;
- featured behavior;
- ordering;
- publication;
- website ownership;
- URL/slug generation;
- SEO/publication mixins used by the final implementation;
- multi-website isolation.

### HTTP tests

Cover at least:

- `/work`;
- `/projects`;
- `/cases`;
- `/labs` with content addon route ownership;
- `/labs` theme-only fallback when content addon is absent;
- published Work detail;
- unpublished Work detail;
- wrong-website Work detail;
- 404 behavior;
- pagination;
- filtering;
- public listing isolation.

### Website/theme integration tests

Cover at least:

- static snippets registered in Website Builder;
- dynamic snippets registered only through the content addon;
- real Work records render in dynamic snippets;
- Blog records render in Insights snippets;
- safe empty states;
- responsive/accessibility contracts where statically testable.

### CI installation matrix

The regression matrix must exercise, at minimum:

```text
theme_monynha
monynha_lead_generator
theme_monynha + monynha_content
theme_monynha + monynha_lead_generator
all Monynha modules together
upgrade/regression
```

Completion requires more than successful installation: clean install, upgrade, model, HTTP, and boundary regressions must pass.

## Documentation requirements

M4 implementation must update user/developer documentation with:

- module boundaries;
- how Work records are authored and published;
- public routes;
- available static snippets;
- available dynamic snippets;
- page starters;
- installation combinations;
- Website Builder ownership rules;
- known extension points.

## Acceptance criteria

M4 is complete when all of the following are true:

1. `theme_monynha` exposes a coherent reusable Monynha composition library in Website Builder.
2. Existing M2/M3 pages still work and preserve Odoo standard chrome/layout ownership.
3. `monynha_content` provides one structured `monynha.work` model for Projects, Cases, and Labs.
4. `/work`, `/projects`, `/cases`, `/labs`, and `/work/<slug>` work for published current-website records.
5. Theme-only `/labs` remains available when `monynha_content` is not installed.
6. Work detail supports structured metadata plus an editable rich narrative body.
7. Work tags, publication, SEO, images, ordering, featured state, and multi-website ownership are supported.
8. Dynamic Work snippets use real records and centralized query behavior.
9. Insights snippets consume `blog.post` rather than duplicate Blog content.
10. Empty dynamic blocks never ship fake production content.
11. Static theme functionality remains valid without `monynha_content`.
12. Lead Generator remains independent.
13. Security and multi-website isolation tests pass.
14. Clean-install, combined-install, HTTP, and upgrade/regression CI passes.
15. No parallel CMS, frontend, header/footer, SEO layer, publication engine, or Blog implementation is introduced.

## Implementation principle

M4 must continue the Monynha Odoo-native rule established in M2/M3:

> Use Odoo as the platform, not merely as the database. Add the smallest Monynha-specific layer required for a coherent branded experience, structured editorial reuse, and safe operational ownership.
