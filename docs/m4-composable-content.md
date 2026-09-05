# Monynha M4 — Composable Content

M4 turns the Monynha Odoo website into a reusable Odoo-native composition and publishing system without introducing a parallel frontend or CMS.

## Architecture and dependencies

The implementation is split by responsibility:

```text
theme_monynha
  └─ visual identity, static Website Builder snippets, page starters
     depends: theme_common, website

monynha_content
  └─ structured Work + dynamic content snippets + standard Blog aggregation
     depends: theme_monynha, website, website_blog

monynha_lead_generator
  └─ discovery / Project Signal / CRM journey
     independent from monynha_content
```

`theme_monynha` never depends on `monynha_content`. Static theme blocks remain ORM-free. Structured public reads live behind the `monynha.content.query` AbstractModel.

## Creating and publishing a Work record

Website editors can manage Work from **Website → Configuration → Monynha Content → Work**.

A Work record exposes:

- **Title** (`name`)
- **Type** (`project`, `case`, `lab`)
- **Website** (`website_id`)
- **Featured** flag
- **Published** state through Odoo Website publication
- **Publication date**
- **Tags**
- **Cover image** through the inherited `image.mixin` (`image_1920`)
- **Summary**
- **Rich body** (`body_html`) using the normal Odoo HTML editor
- **Repository URL**
- **External URL**
- **Sequence**
- **Website SEO metadata** through `website.seo.metadata`

Publishing a record without an explicit publication date records the current datetime. Unpublishing clears the publication date unless a value is explicitly supplied by the caller.

The detail page renders the Work as `main_object` and uses `t-field="work.body_html"`, preserving Odoo Website editor compatibility instead of copying the body into a separate `website.page`.

## Project, Case and Lab types

M4 deliberately uses one domain model rather than parallel models:

```text
monynha.work
├─ project
├─ case
└─ lab
```

The three types share publication, SEO, cover, tags, links, ordering, cards and canonical detail rendering. Type-specific index routes are filters over this one model.

## Tags, cover, SEO, publication and website assignment

`monynha.work.tag` stores a translatable name, sequence and Odoo color index. Tag names are globally unique in the current model.

A Work can be:

- assigned to a specific Website; or
- website-neutral (`website_id = False`), in which case it is eligible on every Website.

Public queries always require `is_published = True`. Website-scoped queries accept only the active Website plus website-neutral records.

SEO fields are standard Odoo Website SEO metadata. The Work cover uses the image fields supplied by `image.mixin`; templates only render the cover when present and use the Work title as alternative text.

## Public route table

| Route | Owner | Behavior |
| --- | --- | --- |
| `/work` | `monynha_content` | All published Work for current/general Website |
| `/projects` | `monynha_content` | Published Work with `type=project` |
| `/cases` | `monynha_content` | Published Work with `type=case` |
| `/labs` | `monynha_content` when installed | Published Work with `type=lab` |
| `/work/<slug>` | `monynha_content` | Canonical Work detail |
| `/blog` and Blog post URLs | `website_blog` | Standard Odoo Insights/articles |
| `/start` | lead generator when installed | Guided commercial discovery |

Catalogue routes accept GET only, paginate at 12 records and accept an optional `tag` filter. Invalid tag values result in an empty filtered catalogue rather than widening the query.

The detail route resolves the Odoo slug, applies publication/website filtering and requires the exact canonical slug. Hidden, wrong-website or noncanonical records return 404.

## Static snippet inventory

M4 adds the following reusable static Website Builder blocks in the existing `monynha` group:

- Hero Split — `theme_monynha.s_monynha_hero_split`
- Section Header — `theme_monynha.s_monynha_section_header`
- Long-form Intro — `theme_monynha.s_monynha_longform_intro`
- Split Content — `theme_monynha.s_monynha_split_content`
- Image + Copy — `theme_monynha.s_monynha_media_copy`
- Pull Quote — `theme_monynha.s_monynha_quote`
- Numbered Steps — `theme_monynha.s_monynha_steps`
- Process Timeline — `theme_monynha.s_monynha_timeline`
- Feature Grid — `theme_monynha.s_monynha_feature_grid`
- Technology Grid — `theme_monynha.s_monynha_technology_grid`
- Deliverables — `theme_monynha.s_monynha_deliverables`
- Engagement Scope — `theme_monynha.s_monynha_engagement_scope`
- Comparison — `theme_monynha.s_monynha_comparison`
- Terminal Panel — `theme_monynha.s_monynha_terminal_panel`
- Contact CTA — `theme_monynha.s_monynha_contact_cta`

These complement the earlier Monynha Hero, Services, Process, Labs, CTA, Signal, Selected Work, Capability, Manifesto, Metrics, FAQ, Intro, Principles and Labs Showcase sections.

Static theme snippet XML contains no `request.env`, `monynha.work` or `blog.post` access.

## Dynamic snippet inventory

`monynha_content` registers dynamic blocks in the same `monynha` Website Builder group:

- `monynha_content.s_monynha_featured_work`
- `monynha_content.s_monynha_work_grid`
- `monynha_content.s_monynha_latest_projects`
- `monynha_content.s_monynha_selected_cases`
- `monynha_content.s_monynha_latest_labs`
- `monynha_content.s_monynha_related_work`
- `monynha_content.s_monynha_work_tags`
- `monynha_content.s_monynha_work_metadata`
- `monynha_content.s_monynha_work_navigation`
- `monynha_content.s_monynha_latest_insights`
- `monynha_content.s_monynha_insights_grid`

All Work and Blog searches are delegated to `monynha.content.query`; domain and sudo logic are not duplicated in snippet templates.

Work-detail helper snippets render only when `main_object` exists and is a `monynha.work`, so placing them on an ordinary Website page does not crash rendering. Catalogue-style snippets provide a usable empty state when no content exists.

## Using Odoo + New page templates

M4 uses the native theme page-template mechanism: `theme.website.page` records with `is_new_page_template=True`.

Available M4 starters are:

- Landing
- Service
- About
- Contact
- Work Story
- Lab Story
- Insights Index
- Documentation
- Changelog

They are starting compositions, not a second page system. Once selected, the resulting Website page remains owned and editable by normal Odoo Website Builder behavior.

Documentation stays on ordinary Website pages unless the content naturally belongs in another standard Odoo mechanism. The starter explicitly avoids creating a separate documentation CMS.

## Blog / Insights ownership

Insights are standard `website_blog` content:

```text
blog.blog → blog.post → standard Odoo public Blog URL
```

M4 does not copy Blog data into `monynha.work` and does not define `monynha.article` or another article model.

Dynamic Insights snippets query published, non-future `blog.post` records for the active/general Website and link to each post's canonical `website_url`.

## Theme-only and content-installed `/labs`

`theme_monynha` predates the structured Work catalogue and includes an editable `/labs` Website page. This remains the theme-only fallback.

When `monynha_content` is installed, the explicit GET `/labs` controller owns the public request and renders the structured Lab catalogue. The theme is not modified to depend on the content addon, so it remains independently installable.

This is intentional route ownership, not two competing data stores: structured Lab records exist only in `monynha_content`; the theme fallback is ordinary Website content.

## Security and public-read model

There is no generic public model ACL and no public write route for Work.

Backend ACLs are scoped to Website authoring groups:

- restricted Website editor: read/write/create Work and tags, no unlink;
- Website designer: full CRUD on Work and tags.

Public controllers and dynamic snippets call `monynha.content.query`. That service performs narrow `sudo()` reads only after constructing domains that enforce publication and Website visibility.

The public surface is GET-only. Content mutation remains a normal authenticated Odoo backend/editor operation.

## Multiwebsite behavior

For Work, the centralized domain is effectively:

```text
is_published = True
AND website_id IN (False, current_website.id)
```

A record assigned to Website A therefore does not appear on Website B. A record with no Website assignment can appear on both.

The same current/general Website rule is used for Blog aggregation. HTTP regressions cover isolation and canonical detail behavior.

## Presentation, accessibility and responsive behavior

`monynha_content/static/src/scss/content.scss` only defines content-specific layout behavior and reuses the theme's visual primitives.

Key constraints include:

- resilient CSS grids based on `minmax(0, 1fr)`;
- `min-width: 0` on content cards/details;
- `overflow-wrap: anywhere` for rich narrative content;
- responsive media with aspect ratio/object fit;
- semantic `<article>` Work/card structures;
- descriptive navigation labels;
- cover alternative text from the Work title;
- theme focus-visible and `prefers-reduced-motion` behavior retained;
- no external runtime font/CDN dependency introduced.

## Extension points and non-goals

Recommended extension points:

- add fields to `monynha.work` only when a repeated editorial need is real;
- extend `monynha.content.query` when a new public selection rule is required;
- add optional dynamic snippets in `monynha_content`, not in the static theme;
- continue using standard `website_blog` for article-like content;
- keep provider-specific AI logic outside the core lead-generator addon.

M4 intentionally does **not** provide:

- a generic cross-project design system;
- separate Project/Case/Lab models;
- a second Blog/article model;
- a parallel frontend or CMS;
- a public content-write API;
- fabricated clients, testimonials, metrics or cases;
- mandatory external AI/runtime providers.

## Test and CI matrix

Repository contracts run with:

```bash
pytest -q tests
```

The permanent Odoo 19 CI matrix validates:

```text
1. theme_monynha standalone install/tests
2. monynha_lead_generator standalone install
3. lead-generator model regressions
4. lead-generator HTTP regressions
5. monynha_content stack install + /monynha_content tests
6. theme_monynha + monynha_content
7. theme_monynha + monynha_lead_generator
8. theme_monynha + monynha_content + monynha_lead_generator
9. full-stack upgrade + all regression tests
```

CI uses the official Odoo 19 container, PostgreSQL 16 and a pinned checkout of Odoo `design-themes` for `theme_common`.
