# Monynha Odoo

Native Odoo 19 Community implementation of the Monynha Softwares website, structured content and commercial discovery experience.

The project preserves the visual and interaction DNA of the historical Monynha/open2.tech presence while using standard Odoo Website, Blog and CRM mechanisms as the owners of public content, editing and commercial workflows.

## Addons

| Addon | Responsibility | Dependency boundary |
| --- | --- | --- |
| `theme_monynha` | Standalone visual identity, reusable Website Builder snippets and native new-page starters | `theme_common`, `website` only |
| `monynha_content` | Structured Work catalogue plus aggregation of standard Odoo Blog posts | Depends on `theme_monynha`, `website`, `website_blog` |
| `monynha_lead_generator` | Guided discovery, Project Signal and CRM follow-up | Independent from `monynha_content` |

### `theme_monynha`

The theme is the presentation layer. It keeps `website.layout`, standard Website navigation/footer, `theme.website.page`, snippets and Website Builder as the structural owners.

It provides the Monynha design system, responsive/reduced-motion behavior, the existing section library, M4 composition primitives, and Odoo-native `+ New` page starters for Landing, Service, About, Contact, Work Story, Lab Story, Insights, Documentation and Changelog compositions. Static theme snippets never query `monynha.work` or `blog.post`.

The theme can be installed by itself. Its `/start` page remains a safe fallback to standard Website contact behavior, and its `/labs` page remains editable fallback content when `monynha_content` is absent.

### `monynha_content`

The content addon adds a single structured Work domain model:

```text
monynha.work
  type = project | case | lab
```

It owns the public catalogue routes:

- `/work`
- `/projects`
- `/cases`
- `/labs`
- canonical detail `/work/<slug>`

Work records support Website publication, website assignment, cover image, summary, editable rich HTML body, tags, featured state, repository/external links, publication date and standard Website SEO metadata.

Dynamic Website Builder snippets render Work and Insights server-side through the centralized `monynha.content.query` service. Insights remain standard `blog.post` records; M4 does not introduce a parallel article model.

When `monynha_content` is installed, its explicit `/labs` controller becomes the public structured Labs catalogue. The theme fallback page remains useful for theme-only installations and as editable source material, but it does not become a second Labs CMS.

### `monynha_lead_generator`

The commercial discovery addon remains separate from content. It provides:

- interactive six-step `/start` discovery;
- server-side validation and an explicit public-field whitelist;
- standard `crm.lead` as the canonical commercial record;
- deterministic `local_rules` Project Signal provider;
- append-only `monynha.lead.diagnosis` history;
- secure `/diagnosis/<token>` reports and idempotent follow-up;
- standard CRM chatter, activities and mail templates.

With the addon installed, its explicit `/start` controller owns the interactive route. Without it, the theme fallback remains safe and usable.

## Installation combinations

Supported boundaries are validated in CI:

```text
theme_monynha
monynha_lead_generator
monynha_content                         # resolves theme + website_blog dependencies
theme_monynha + monynha_content
theme_monynha + monynha_lead_generator
theme_monynha + monynha_content + monynha_lead_generator
```

The full stack is also upgraded in CI with all module regression tests rerun after `-u`.

## Website ownership model

```text
Global layout/header/footer  standard Odoo Website
Navigation                   standard website.menu copies
Homepage                     configurator_snippets + Website Builder
Static page starters         theme.website.page + is_new_page_template
Static Monynha blocks        theme_monynha, ORM-free
Structured Work              monynha_content / monynha.work
Insights                     standard website_blog / blog.post
/start                       theme fallback; lead generator when installed
/labs                        theme fallback; content catalogue when installed
```

There is no React/Vue frontend runtime, parallel CMS, duplicated Blog model or custom navigation engine.

## M4 reusable Website Builder library

M4 adds composition-level blocks including Hero Split, Section Header, Long-form Intro, Split Content, Image + Copy, Pull Quote, Numbered Steps, Process Timeline, Feature Grid, Technology Grid, Deliverables, Engagement Scope, Comparison, Terminal Panel and Contact CTA.

When `monynha_content` is installed, additional dynamic blocks include Featured Work, Work Grid, Latest Projects, Selected Cases, Latest Labs, Related Work, Work Tags, Work Metadata, Work Navigation, Latest Insights and Insights Grid.

See `docs/m4-composable-content.md` for the complete authoring, route, security and extension map.

## Security and multiwebsite boundaries

Public catalogue controllers are GET-only. They do not expose a public create/write route or a generic public ACL on `monynha.work`.

Public rendering goes through `monynha.content.query`, which performs the narrow read elevation and enforces:

- published records only;
- current website or website-neutral records only;
- type/tag/featured filters when requested;
- exact canonical Work slug resolution;
- published, non-future Blog posts for the current/general website.

Backend Work and tag editing is granted to Website editors/designers through scoped ACLs.

## Development

Repository contracts:

```bash
pytest -q tests
```

The GitHub Actions release gate uses the official Odoo 19 image, PostgreSQL 16 and a pinned Odoo `design-themes` checkout for `theme_common`. It verifies standalone boundaries, content/model/HTTP/snippet behavior, combined installations and full-stack upgrade regressions.

## Future provider extensions

The lead-generator provider registry remains the extension point for optional AI integrations. Provider-specific credentials and SDK dependencies should live in separate addons; the core discovery flow remains functional with `local_rules` alone.
