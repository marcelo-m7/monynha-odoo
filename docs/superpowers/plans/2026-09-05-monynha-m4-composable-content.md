# Monynha M4 — Composable Content & Website Builder Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the completed M3 Monynha theme into an Odoo-native reusable composition system and add structured Projects/Cases/Labs through a separate `monynha_content` addon without breaking theme or lead-generator independence.

**Architecture:** `theme_monynha` remains the standalone presentation layer and gains reusable primitives, static snippets, and native Odoo new-page templates. `monynha_content` depends on the theme plus `website_blog`, owns one `monynha.work` model, server-rendered public routes, shared query helpers, dynamic Work/Insights snippets, and backend editorial management. Public reads are narrowly scoped to published current-website records; no public write API or parallel CMS is introduced.

**Tech Stack:** Odoo 19 Community, Python 3.12, QWeb/XML, Odoo Website/Website Builder, `website_blog`, SCSS, PostgreSQL 16, Docker `odoo:19.0`, pytest, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-05-monynha-m4-composable-content-design.md`

## Global Constraints

- `theme_monynha` must continue to depend only on `theme_common` and `website`.
- `monynha_content` must depend on `theme_monynha`, `website`, and `website_blog`; the dependency direction must never be reversed.
- `monynha_lead_generator` must remain independent from `monynha_content`.
- Preserve `website.layout`, standard Odoo header/footer/menu ownership, Website Builder, Blog, SEO, publication, and Odoo security.
- Projects, Cases, and Labs share one `monynha.work` model with `type in {'project', 'case', 'lab'}`.
- Public routes are exactly `/work`, `/projects`, `/cases`, `/labs`, and `/work/<slug>`.
- The existing M3 theme-only `/labs` page remains the fallback when `monynha_content` is not installed; the content addon owns `/labs` when installed.
- Insights remain `website_blog` / `blog.post`; do not create a Monynha article model.
- Dynamic listings must render server-side. JavaScript is not required merely to display Work or Blog records.
- No fake clients, testimonials, outcomes, portfolio entries, production metrics, broken-image placeholders, or public demo content.
- Public content must respect publication and current website. Cross-website records must never leak through routes, related content, or snippets.
- Avoid generalized `sudo()`. Any elevated public read must be centralized, narrowly scoped, and constrained by publication + website domains.
- Preserve M3 responsive/accessibility rules: fluid sizing, safe wrapping, `minmax(0, 1fr)`, `min-width: 0`, visible `:focus-visible`, semantic markup, and `prefers-reduced-motion`.
- Completion requires contract, clean-install, model, HTTP, combined-install, and upgrade/regression CI — not merely successful module installation.

---

## Planned file structure

### `theme_monynha`

- Modify `theme_monynha/__manifest__.py` — bump M4 version; load static snippets and new-page templates.
- Create `theme_monynha/views/snippets_m4.xml` — M4 reusable static Website Builder blocks and registrations.
- Create `theme_monynha/data/page_templates_m4.xml` — native `theme.website.page` records marked `is_new_page_template=True` so they appear in Odoo's `+New` page templates.
- Modify `theme_monynha/static/src/scss/components.scss` — shared primitive/component vocabulary.
- Modify `theme_monynha/static/src/scss/snippets.scss` — M4 snippet composition/layout only.
- Modify `theme_monynha/static/src/scss/website.scss` only if a page-template/global website rule cannot live in components/snippets.
- Modify `theme_monynha/tests/test_theme.py` — Odoo-level registration/new-page-template tests.
- Create `tests/test_m4_theme_contract.py` — repository-level dependency/content/accessibility/static-snippet contracts.

### `monynha_content`

- Create `monynha_content/__init__.py` and `monynha_content/__manifest__.py`.
- Create `monynha_content/models/__init__.py`.
- Create `monynha_content/models/work.py` — `monynha.work` and `monynha.work.tag`, website URL behavior, publication date behavior.
- Create `monynha_content/models/content_query.py` — one AbstractModel centralizing safe public Work and Blog queries.
- Create `monynha_content/controllers/__init__.py` and `monynha_content/controllers/main.py` — catalogue/detail routes only.
- Create `monynha_content/security/ir.model.access.csv` — backend/editor ACLs only; no public write ACL.
- Create `monynha_content/views/work_views.xml` — backend list/form/search/action/menu.
- Create `monynha_content/views/work_templates.xml` — shared Work card, catalogue, detail, metadata, related-content QWeb components.
- Create `monynha_content/views/snippets.xml` — dynamic Website Builder snippet registrations and server-rendered templates.
- Create `monynha_content/static/src/scss/content.scss` — only content-addon-specific presentation; reuse theme primitives.
- Create `monynha_content/tests/__init__.py`.
- Create `monynha_content/tests/test_work.py` — model/query/security/multiwebsite regressions.
- Create `monynha_content/tests/test_http.py` — public route/list/detail/filter/pagination/fallback regressions.
- Create `monynha_content/tests/test_snippets.py` — dynamic snippet server-render/empty-state/Blog integration regressions.
- Create `tests/test_m4_content_contract.py` — repository-level addon contract checks.

### CI/docs

- Modify `.github/workflows/ci.yml` — add dedicated content DB, clean installs, combined installs, and upgrade coverage.
- Modify `README.md` — module matrix and M4 usage.
- Create `docs/m4-composable-content.md` — authoring, routes, snippets, page templates, extension boundaries.

---

### Task 1: Lock the M4 module and theme contracts in failing repository tests

**Files:**
- Create: `tests/test_m4_theme_contract.py`
- Create: `tests/test_m4_content_contract.py`

**Interfaces:**
- Consumes: current M3 `theme_monynha` manifest/snippets/pages and approved M4 spec.
- Produces: repository-level contracts that every later task must keep green.

- [ ] **Step 1: Add the failing theme contract**

Create `tests/test_m4_theme_contract.py` with assertions that:

```python
from pathlib import Path
import ast

ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / "theme_monynha"


def _manifest(path):
    return ast.literal_eval(path.read_text())


def test_theme_stays_independent_from_content():
    manifest = _manifest(THEME / "__manifest__.py")
    assert set(manifest["depends"]) == {"theme_common", "website"}
    assert "monynha_content" not in (THEME / "__manifest__.py").read_text()


def test_m4_static_library_and_page_templates_are_loaded():
    manifest = _manifest(THEME / "__manifest__.py")
    assert "views/snippets_m4.xml" in manifest["data"]
    assert "data/page_templates_m4.xml" in manifest["data"]


def test_m4_static_snippets_do_not_query_optional_models():
    xml = (THEME / "views/snippets_m4.xml").read_text()
    assert "monynha.work" not in xml
    assert "blog.post" not in xml
    assert "request.env" not in xml


def test_m4_uses_native_new_page_template_mechanism():
    xml = (THEME / "data/page_templates_m4.xml").read_text()
    assert "theme.website.page" in xml
    assert "is_new_page_template" in xml
```

- [ ] **Step 2: Add the failing content-addon contract**

Create `tests/test_m4_content_contract.py` with:

```python
from pathlib import Path
import ast

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "monynha_content"


def _manifest(path):
    return ast.literal_eval(path.read_text())


def test_content_dependency_direction():
    manifest = _manifest(CONTENT / "__manifest__.py")
    assert set(manifest["depends"]) == {"theme_monynha", "website", "website_blog"}


def test_content_declares_one_work_domain_model():
    source = (CONTENT / "models/work.py").read_text()
    assert "_name = \"monynha.work\"" in source
    assert "_name = \"monynha.work.tag\"" in source
    assert "monynha.project" not in source
    assert "monynha.case" not in source
    assert "monynha.lab" not in source


def test_content_public_surface_has_no_write_route():
    source = (CONTENT / "controllers/main.py").read_text()
    assert "/work" in source
    assert "/projects" in source
    assert "/cases" in source
    assert "/labs" in source
    assert "methods=[\"POST\"]" not in source


def test_defaults_do_not_ship_fake_proof():
    shipped = "\n".join(
        p.read_text(errors="ignore")
        for p in list((ROOT / "theme_monynha").rglob("*.xml"))
        + list(CONTENT.rglob("*.xml"))
    ).lower()
    forbidden = ["testimonial", "acme", "fortune 500", "99% uptime", "100+ clients"]
    assert not any(term in shipped for term in forbidden)
```

- [ ] **Step 3: Run the contract suite and verify RED**

Run:

```bash
pytest -q tests/test_m4_theme_contract.py tests/test_m4_content_contract.py
```

Expected: failures because `snippets_m4.xml`, `page_templates_m4.xml`, and the `monynha_content` addon do not exist yet.

- [ ] **Step 4: Commit the RED contract**

```bash
git add tests/test_m4_theme_contract.py tests/test_m4_content_contract.py
git commit -m "test: define Monynha M4 contracts"
```

---

### Task 2: Build the M4 static primitive and snippet library in `theme_monynha`

**Files:**
- Modify: `theme_monynha/__manifest__.py`
- Create: `theme_monynha/views/snippets_m4.xml`
- Modify: `theme_monynha/static/src/scss/components.scss`
- Modify: `theme_monynha/static/src/scss/snippets.scss`
- Modify: `theme_monynha/tests/test_theme.py`

**Interfaces:**
- Consumes: existing `.monynha-button`, `.monynha-card`, `.monynha-grid`, M2/M3 snippet conventions.
- Produces: registered static QWeb snippets and shared CSS primitives usable by page templates and content addon templates.

- [ ] **Step 1: Extend the Odoo theme test with the exact M4 snippet keys**

Add to `theme_monynha/tests/test_theme.py` a test expecting these keys:

```python
M4_STATIC_KEYS = {
    "theme_monynha.s_monynha_hero_split",
    "theme_monynha.s_monynha_section_header",
    "theme_monynha.s_monynha_longform_intro",
    "theme_monynha.s_monynha_split_content",
    "theme_monynha.s_monynha_media_copy",
    "theme_monynha.s_monynha_quote",
    "theme_monynha.s_monynha_steps",
    "theme_monynha.s_monynha_timeline",
    "theme_monynha.s_monynha_feature_grid",
    "theme_monynha.s_monynha_technology_grid",
    "theme_monynha.s_monynha_deliverables",
    "theme_monynha.s_monynha_engagement_scope",
    "theme_monynha.s_monynha_comparison",
    "theme_monynha.s_monynha_terminal_panel",
    "theme_monynha.s_monynha_contact_cta",
}


def test_m4_static_snippets_registered(self):
    views = self.env["ir.ui.view"].search([
        ("key", "in", list(M4_STATIC_KEYS)),
        ("website_id", "!=", False),
    ])
    self.assertEqual(set(views.mapped("key")), M4_STATIC_KEYS)
```

- [ ] **Step 2: Run theme tests and verify RED**

Run the same Docker pattern used by CI against a temporary DB with `-i theme_monynha --test-tags /theme_monynha --stop-after-init`.

Expected: `test_m4_static_snippets_registered` fails because the M4 views are absent.

- [ ] **Step 3: Add `views/snippets_m4.xml` and register every snippet in the existing Monynha group**

Use the existing `website.snippets` inheritance point and explicit `t-snippet` registrations, e.g.:

```xml
<template id="snippets_m4" inherit_id="website.snippets" name="Monynha M4 snippets">
    <xpath expr="//snippets[@id='snippet_structure']" position="inside">
        <t t-snippet="theme_monynha.s_monynha_hero_split" string="Hero Split" group="monynha" t-thumbnail="/theme_monynha/static/description/theme_monynha.svg"/>
        <t t-snippet="theme_monynha.s_monynha_section_header" string="Section Header" group="monynha" t-thumbnail="/theme_monynha/static/description/theme_monynha.svg"/>
        <t t-snippet="theme_monynha.s_monynha_longform_intro" string="Long-form Intro" group="monynha" t-thumbnail="/theme_monynha/static/description/theme_monynha.svg"/>
        <t t-snippet="theme_monynha.s_monynha_split_content" string="Split Content" group="monynha" t-thumbnail="/theme_monynha/static/description/theme_monynha.svg"/>
        <t t-snippet="theme_monynha.s_monynha_media_copy" string="Image + Copy" group="monynha" t-thumbnail="/theme_monynha/static/description/theme_monynha.svg"/>
        <t t-snippet="theme_monynha.s_monynha_quote" string="Pull Quote" group="monynha" t-thumbnail="/theme_monynha/static/description/theme_monynha.svg"/>
        <t t-snippet="theme_monynha.s_monynha_steps" string="Numbered Steps" group="monynha" t-thumbnail="/theme_monynha/static/description/theme_monynha.svg"/>
        <t t-snippet="theme_monynha.s_monynha_timeline" string="Process Timeline" group="monynha" t-thumbnail="/theme_monynha/static/description/theme_monynha.svg"/>
        <t t-snippet="theme_monynha.s_monynha_feature_grid" string="Feature Grid" group="monynha" t-thumbnail="/theme_monynha/static/description/theme_monynha.svg"/>
        <t t-snippet="theme_monynha.s_monynha_technology_grid" string="Technology Grid" group="monynha" t-thumbnail="/theme_monynha/static/description/theme_monynha.svg"/>
        <t t-snippet="theme_monynha.s_monynha_deliverables" string="Deliverables" group="monynha" t-thumbnail="/theme_monynha/static/description/theme_monynha.svg"/>
        <t t-snippet="theme_monynha.s_monynha_engagement_scope" string="Engagement Scope" group="monynha" t-thumbnail="/theme_monynha/static/description/theme_monynha.svg"/>
        <t t-snippet="theme_monynha.s_monynha_comparison" string="Comparison" group="monynha" t-thumbnail="/theme_monynha/static/description/theme_monynha.svg"/>
        <t t-snippet="theme_monynha.s_monynha_terminal_panel" string="Terminal Panel" group="monynha" t-thumbnail="/theme_monynha/static/description/theme_monynha.svg"/>
        <t t-snippet="theme_monynha.s_monynha_contact_cta" string="Contact CTA" group="monynha" t-thumbnail="/theme_monynha/static/description/theme_monynha.svg"/>
    </xpath>
</template>
```

Each template must use semantic `<section>`, `.container`, the shared Monynha primitives, truthful neutral copy, and `oe_structure`-friendly editable text. Do not embed ORM queries or optional model references.

- [ ] **Step 4: Add the shared primitive vocabulary to `components.scss`**

Implement concrete reusable rules for:

```scss
.monynha-section { padding-block: clamp(4rem, 8vw, 8rem); }
.monynha-container { width: min(100% - 2rem, 80rem); margin-inline: auto; }
.monynha-stack { display: flex; flex-direction: column; gap: var(--monynha-stack-gap, 1.5rem); min-width: 0; }
.monynha-cluster { display: flex; flex-wrap: wrap; gap: 0.75rem; align-items: center; }
.monynha-split { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: clamp(2rem, 5vw, 5rem); align-items: center; }
.monynha-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 16rem), 1fr)); gap: 1rem; }
.monynha-tag { display: inline-flex; align-items: center; max-width: 100%; overflow-wrap: anywhere; }
.monynha-meta { font-size: 0.875rem; line-height: 1.4; }
.monynha-eyebrow { text-transform: uppercase; letter-spacing: 0.12em; font-size: 0.75rem; }

@media (max-width: 767.98px) {
    .monynha-split { grid-template-columns: minmax(0, 1fr); }
}
```

Reuse existing token variables and button/card styles instead of introducing new hard-coded brand palettes.

- [ ] **Step 5: Add snippet-specific layout only to `snippets.scss`**

Keep section-specific CSS limited to composition selectors such as `.s_monynha_timeline`, `.s_monynha_comparison`, and `.s_monynha_media_copy`. Every flexible child gets `min-width: 0`; grids use `minmax(0, 1fr)`; decorative transitions are disabled under the existing reduced-motion media query.

- [ ] **Step 6: Load `views/snippets_m4.xml` and bump the theme version**

Change `theme_monynha/__manifest__.py` to version `19.0.4.0.0` and append `views/snippets_m4.xml` after the M3 snippets. Keep dependencies unchanged.

- [ ] **Step 7: Run repository + Odoo theme tests and verify GREEN**

Run:

```bash
pytest -q tests/test_m4_theme_contract.py tests/test_module_contract.py tests/test_m3_theme_contract.py
```

Then run the CI theme-install command. Expected: all theme contract and `/theme_monynha` tests pass.

- [ ] **Step 8: Commit**

```bash
git add theme_monynha tests/test_m4_theme_contract.py
git commit -m "feat: add Monynha M4 static composition library"
```

---

### Task 3: Add native Odoo `+New` page templates

**Files:**
- Create: `theme_monynha/data/page_templates_m4.xml`
- Modify: `theme_monynha/__manifest__.py`
- Modify: `theme_monynha/tests/test_theme.py`

**Interfaces:**
- Consumes: M4 static snippets from Task 2 and Odoo 19 `theme.website.page.is_new_page_template`.
- Produces: editable native Website page templates for Landing, Service, About, Contact, Documentation, Changelog, and static editorial starters.

- [ ] **Step 1: Write the failing Odoo test for new-page templates**

Add:

```python
M4_PAGE_TEMPLATE_XMLIDS = (
    "theme_monynha.page_template_landing",
    "theme_monynha.page_template_service",
    "theme_monynha.page_template_about",
    "theme_monynha.page_template_contact",
    "theme_monynha.page_template_work_story",
    "theme_monynha.page_template_lab_story",
    "theme_monynha.page_template_insights_index",
    "theme_monynha.page_template_documentation",
    "theme_monynha.page_template_changelog",
)


def test_m4_new_page_templates_registered(self):
    for xmlid in M4_PAGE_TEMPLATE_XMLIDS:
        page = self.env.ref(xmlid, raise_if_not_found=False)
        self.assertTrue(page, xmlid)
        self.assertEqual(page._name, "theme.website.page")
        self.assertTrue(page.is_new_page_template, xmlid)
```

- [ ] **Step 2: Verify RED**

Run `/theme_monynha` tests. Expected: the first missing `page_template_*` XML ID fails.

- [ ] **Step 3: Define each template as a `theme.website.page` with `is_new_page_template=True`**

Use one QWeb view plus one theme page record per starter. The record pattern is:

```xml
<record id="page_template_landing" model="theme.website.page">
    <field name="view_id" ref="view_page_template_landing"/>
    <field name="url">/monynha-template-landing</field>
    <field name="is_published" eval="False"/>
    <field name="is_new_page_template" eval="True"/>
</record>
```

The associated view must call `website.layout`, expose `<div id="wrap" class="oe_structure">`, and compose already-registered static snippets. Template seed URLs stay unpublished and exist only as Odoo template source records; new pages are copies created through the standard Website `+New` flow.

Use these compositions:

```text
Landing: Hero Split → Section Header → Services → Selected Work → CTA
Service: Page Intro → Split Content → Capability → Process → FAQ → CTA
About: Page Intro → Manifesto → Principles → Process → CTA
Contact: Page Intro → Split Content → standard /contactus CTA/form path → CTA
Work Story: Page Intro → Long-form Intro → Media + Copy → Quote → CTA
Lab Story: Page Intro → Terminal Panel → Long-form Intro → Timeline → CTA
Insights Index: Page Intro → narrative intro → link to standard Blog
Documentation: Page Intro → Split Content → Deliverables/List → CTA
Changelog: Page Intro → Timeline → CTA
```

- [ ] **Step 4: Load `data/page_templates_m4.xml` after snippets in the manifest**

Ensure the page-template file loads after all snippets it composes.

- [ ] **Step 5: Run tests and verify GREEN**

Run repository contracts and `/theme_monynha` Odoo tests. Expected: every template exists, is a `theme.website.page`, is unpublished, and has `is_new_page_template=True`.

- [ ] **Step 6: Commit**

```bash
git add theme_monynha/data/page_templates_m4.xml theme_monynha/__manifest__.py theme_monynha/tests/test_theme.py
git commit -m "feat: add Monynha Website page starters"
```

---

### Task 4: Scaffold `monynha_content` and implement the Work domain model

**Files:**
- Create: `monynha_content/__init__.py`
- Create: `monynha_content/__manifest__.py`
- Create: `monynha_content/models/__init__.py`
- Create: `monynha_content/models/work.py`
- Create: `monynha_content/security/ir.model.access.csv`
- Create: `monynha_content/views/work_views.xml`
- Create: `monynha_content/tests/__init__.py`
- Create: `monynha_content/tests/test_work.py`

**Interfaces:**
- Produces: models `monynha.work`, `monynha.work.tag`; computed `website_url`; publication metadata; backend editorial CRUD.
- Later tasks consume: `work.type`, `work.summary`, `work.body_html`, `work.tag_ids`, `work.featured`, `work.published_date`, `work.website_id`, `work.website_url`.

- [ ] **Step 1: Write RED model tests**

Create `test_work.py` with a `TransactionCase` tagged `post_install` that asserts:

```python
work = self.env["monynha.work"].create({
    "name": "Architecture Notes",
    "type": "lab",
    "summary": "A real editorial record used only by tests.",
    "website_id": self.env["website"].get_current_website().id,
})
self.assertEqual(work.type, "lab")
self.assertFalse(work.is_published)
self.assertTrue(work.website_url.startswith("/work/"))
self.assertIn(str(work.id), work.website_url)
```

Also assert an invalid type raises `ValueError`/ORM validation and tags can be attached.

- [ ] **Step 2: Verify RED with a clean content DB**

Create a PostgreSQL test DB and run `-i monynha_content --test-tags /monynha_content:TestMonynhaWork --stop-after-init` after the addon manifest exists minimally. Expected: model tests fail until fields/mixins are implemented.

- [ ] **Step 3: Implement the manifest and model inheritance**

Use:

```python
class MonynhaWork(models.Model):
    _name = "monynha.work"
    _description = "Monynha Work"
    _inherit = [
        "image.mixin",
        "website.seo.metadata",
        "website.published.multi.mixin",
        "website.searchable.mixin",
    ]
    _order = "sequence, published_date desc, id desc"
```

Fields must include:

```python
name = fields.Char(required=True, translate=True)
type = fields.Selection([
    ("project", "Project"),
    ("case", "Case"),
    ("lab", "Lab"),
], required=True, default="project", index=True)
summary = fields.Text(translate=True)
body_html = fields.Html(translate=html_translate, sanitize=False)
tag_ids = fields.Many2many("monynha.work.tag", string="Tags")
sequence = fields.Integer(default=10)
featured = fields.Boolean(default=False, index=True)
published_date = fields.Datetime(index=True)
repository_url = fields.Char()
external_url = fields.Char()
```

Use the `website_id` supplied by `website.published.multi.mixin`; do not redefine it unless Odoo 19 inspection proves it absent.

Implement:

```python
@api.depends("name")
def _compute_website_url(self):
    super()._compute_website_url()
    for work in self:
        if work.id:
            work.website_url = f"/work/{self.env['ir.http']._slug(work)}"
```

and synchronize `published_date` when `is_published` changes, following the same narrow pattern used by `blog.post`.

- [ ] **Step 4: Implement `monynha.work.tag`**

```python
class MonynhaWorkTag(models.Model):
    _name = "monynha.work.tag"
    _description = "Monynha Work Tag"
    _order = "sequence, name, id"

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    color = fields.Integer()
```

Add a SQL/model constraint preventing duplicate tag names where practical for the current Odoo API.

- [ ] **Step 5: Add backend ACLs with no public ACL**

`ir.model.access.csv` must grant:

```text
website.group_website_restricted_editor: read/create/write, no unlink
website.group_website_designer: read/create/write/unlink
```

for both Work and Work Tag. Do not grant `base.group_public` or `base.group_portal` model ACLs; public reads will be mediated by the scoped query helper in Task 5.

- [ ] **Step 6: Add backend list/form/search/action/menu views**

The Work form must expose: title, type, publication toggle, website, featured, publication date, tags, cover image, summary, repository/external URLs, SEO fields provided by the mixin, and `body_html` in a dedicated content tab. Use standard Website/editor widgets where available rather than custom JS.

- [ ] **Step 7: Run model tests and verify GREEN**

Expected: valid Work/tag creation passes, invalid type is rejected by the selection field, publication defaults false, and `website_url` is Odoo-slug based.

- [ ] **Step 8: Commit**

```bash
git add monynha_content tests/test_m4_content_contract.py
git commit -m "feat: add structured Monynha Work content model"
```

---

### Task 5: Centralize safe public Work and Blog queries

**Files:**
- Create: `monynha_content/models/content_query.py`
- Modify: `monynha_content/models/__init__.py`
- Modify: `monynha_content/tests/test_work.py`

**Interfaces:**
- Produces AbstractModel `monynha.content.query` with:
  - `get_works(website, work_type=None, tag=None, featured=None, limit=12, offset=0, order=None)`
  - `count_works(website, work_type=None, tag=None, featured=None)`
  - `get_work_by_slug(website, slug_value)`
  - `get_blog_posts(website, limit=3, offset=0)`
- Controllers and dynamic QWeb snippets must use these methods instead of direct ad-hoc searches.

- [ ] **Step 1: Write RED tests for publication and multiwebsite isolation**

Create two websites and records assigned to each plus one global record. Assert:

```python
visible = self.env["monynha.content.query"].get_works(website_a)
self.assertIn(published_a, visible)
self.assertIn(published_global, visible)
self.assertNotIn(unpublished_a, visible)
self.assertNotIn(published_b, visible)
```

Also test `work_type`, tag, featured, limit, offset, and deterministic order.

- [ ] **Step 2: Implement one fixed public domain builder**

The helper must construct the equivalent of:

```python
Domain.AND([
    [("is_published", "=", True)],
    [("website_id", "in", [False, website.id])],
])
```

Then append type/tag/featured filters. Use `sudo()` only inside this helper after the domain is built; callers never receive unrelated records.

- [ ] **Step 3: Implement slug resolution safely**

Use:

```python
_, record_id = self.env["ir.http"]._unslug(slug_value)
```

Then fetch by `id` plus the same publication/current-website domain. Return an empty recordset if the slug is malformed, the ID does not exist, the canonical slug differs, the record is unpublished, or it belongs only to another website.

Canonical-slug mismatch must not silently expose the record; either return empty for the controller to 404 or return a canonical redirect decision from the controller in Task 6.

- [ ] **Step 4: Implement Blog query using `blog.post` as source of truth**

Use only published posts valid for the current website and respect post publication dates. Do not copy Blog fields into Monynha tables.

- [ ] **Step 5: Run model/query tests and verify GREEN**

Expected: all publication, website, filter, limit, and Blog-source assertions pass.

- [ ] **Step 6: Commit**

```bash
git add monynha_content/models/content_query.py monynha_content/models/__init__.py monynha_content/tests/test_work.py
git commit -m "feat: centralize Monynha public content queries"
```

---

### Task 6: Implement public Work catalogue and detail routes

**Files:**
- Create: `monynha_content/controllers/__init__.py`
- Create: `monynha_content/controllers/main.py`
- Create: `monynha_content/views/work_templates.xml`
- Create: `monynha_content/tests/test_http.py`
- Modify: `monynha_content/__manifest__.py`

**Interfaces:**
- Consumes: `monynha.content.query` from Task 5.
- Produces routes `/work`, `/projects`, `/cases`, `/labs`, `/work/<slug>` and QWeb templates `monynha_content.work_index`, `monynha_content.work_detail`, `monynha_content.work_card`.

- [ ] **Step 1: Write RED `HttpCase` tests for route matrix**

Create published project/case/lab records and assert HTTP 200 plus expected title on:

```text
/work
/projects
/cases
/labs
/work/<canonical slug>
```

Assert unpublished, wrong-website, unknown, and malformed slug detail URLs return 404.

- [ ] **Step 2: Add filter/pagination HTTP tests**

Create enough published Work records to force pagination. Assert `?page=2` changes the result set, `?tag=<id>` limits records, and an unknown tag produces a valid empty result rather than 500.

- [ ] **Step 3: Implement one controller path for all indices**

Use a private method like:

```python
def _render_catalogue(self, *, work_type=None, page=1, tag=None):
    website = request.website
    query = request.env["monynha.content.query"]
    per_page = 12
    total = query.count_works(website, work_type=work_type, tag=tag)
    pager = request.website.pager(
        url=request.httprequest.path,
        total=total,
        page=page,
        step=per_page,
        url_args={"tag": tag} if tag else {},
    )
    works = query.get_works(
        website,
        work_type=work_type,
        tag=tag,
        limit=per_page,
        offset=pager["offset"],
    )
    return request.render("monynha_content.work_index", {
        "works": works,
        "work_type": work_type,
        "pager": pager,
    })
```

Expose four `type="http"`, `auth="public"`, `website=True`, `sitemap=True` GET routes. Do not add POST routes.

- [ ] **Step 4: Implement detail resolution through the query helper only**

`/work/<string:slug_value>` must call `get_work_by_slug(request.website, slug_value)` and raise `werkzeug.exceptions.NotFound()` for an empty result. Set `main_object` to the Work record in the QWeb context.

- [ ] **Step 5: Build shared server-rendered QWeb components**

`work_templates.xml` must contain:

```text
work_card        — title, type, summary, tags, optional cover, canonical URL
work_metadata    — type/date/tags/optional repository/external links
work_index       — intro + server-rendered card grid + pager
work_detail      — website.layout + cover/meta + editable body_html + related area + CTA
```

Missing cover image must omit the `<img>` entirely rather than output a broken source.

- [ ] **Step 6: Resolve `/labs` ownership cleanly**

The content controller route must take precedence only when `monynha_content` is installed. The theme's `/labs` remains an independent `theme.website.page` fallback when the content addon is absent. Add an HTTP assertion in the content-installed DB that `/labs` renders structured Lab records.

- [ ] **Step 7: Run HTTP tests and verify GREEN**

Expected: route/filter/pager/detail/404/multiwebsite tests all pass.

- [ ] **Step 8: Commit**

```bash
git add monynha_content/controllers monynha_content/views/work_templates.xml monynha_content/tests/test_http.py monynha_content/__manifest__.py
git commit -m "feat: publish Monynha Work routes"
```

---

### Task 7: Add dynamic Work and Insights snippets with server-rendered data

**Files:**
- Create: `monynha_content/views/snippets.xml`
- Create: `monynha_content/tests/test_snippets.py`
- Modify: `monynha_content/__manifest__.py`

**Interfaces:**
- Consumes: `monynha.content.query`, `work_card`, theme primitive classes.
- Produces dynamic snippet keys:
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

- [ ] **Step 1: Write RED snippet-registration tests**

In `test_snippets.py`, assert all keys exist after installation and are registered in the Monynha snippet group.

- [ ] **Step 2: Write RED render tests with real records and empty state**

Render the QWeb snippets under a website request context and assert:

```python
self.assertIn("Published Lab", rendered_with_records)
self.assertNotIn("Unpublished Lab", rendered_with_records)
self.assertNotIn("Project 1", rendered_empty)
self.assertNotIn("broken", rendered_empty.lower())
```

Create one real `blog.post` and assert the Insights snippet contains its title without creating a Monynha article record.

- [ ] **Step 3: Register dynamic snippets**

Inherit `website.snippets` and add all dynamic blocks to the existing `monynha` group. Keep registrations in `monynha_content`; do not modify static theme snippets to reference `monynha.work`.

- [ ] **Step 4: Render data server-side through the centralized helper**

For arbitrary Website Builder pages, the snippet template may obtain the current request website and call only the AbstractModel helper, e.g.:

```xml
<t t-set="works" t-value="request.env['monynha.content.query'].get_works(request.website, featured=True, limit=3)"/>
<t t-if="works">
    <div class="monynha-grid">
        <t t-foreach="works" t-as="work">
            <t t-call="monynha_content.work_card"/>
        </t>
    </div>
</t>
```

This is the only permitted `request.env` use in dynamic snippet XML; all search/domain/elevation logic remains inside `monynha.content.query`. Static `theme_monynha` snippets must remain ORM-free.

- [ ] **Step 5: Implement related Work and Work-detail helper snippets defensively**

`Related Work`, `Work Metadata`, and `Work Navigation` must render only when `main_object` exists and `_name == 'monynha.work'`. On a normal page they render nothing rather than crash.

- [ ] **Step 6: Implement Blog snippets from the same query service**

Render `blog.post` title, teaser, cover only when present, and canonical `website_url`. No copied Blog data, no fake cards.

- [ ] **Step 7: Run snippet tests and verify GREEN**

Expected: registration, publication filtering, Blog integration, and empty-state tests pass with no custom frontend JS.

- [ ] **Step 8: Commit**

```bash
git add monynha_content/views/snippets.xml monynha_content/tests/test_snippets.py monynha_content/__manifest__.py
git commit -m "feat: add Monynha dynamic content snippets"
```

---

### Task 8: Complete content presentation, editing, accessibility, and responsive behavior

**Files:**
- Create: `monynha_content/static/src/scss/content.scss`
- Modify: `monynha_content/__manifest__.py`
- Modify: `monynha_content/views/work_templates.xml`
- Modify: `monynha_content/views/snippets.xml`
- Modify: `tests/test_m4_theme_contract.py`
- Modify: `tests/test_m4_content_contract.py`

**Interfaces:**
- Consumes: theme primitives from Task 2.
- Produces: responsive content catalogue/detail/snippets without a parallel visual system.

- [ ] **Step 1: Add failing static accessibility/responsive contract assertions**

Assert M4 markup/CSS contains:

```text
main_object on Work detail
alt handling on conditional images
focus-visible inherited or preserved
minmax(0, 1fr) / min-width: 0 for Work grids/cards
prefers-reduced-motion remains present in theme assets
no external runtime font/CDN references
```

- [ ] **Step 2: Implement `content.scss` using theme primitives**

Only add selectors specific to content such as:

```scss
.monynha-work-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 18rem), 1fr));
    gap: 1rem;
}

.monynha-work-card,
.monynha-work-detail,
.monynha-work-body { min-width: 0; }

.monynha-work-body { overflow-wrap: anywhere; }
```

Do not redefine brand colors/buttons/cards already owned by the theme.

- [ ] **Step 3: Make the narrative body Website-editor compatible**

Render the rich body with the Work record set as `main_object`, and use the normal editable field rendering pattern for `body_html` rather than duplicating the content into a `website.page`.

- [ ] **Step 4: Add semantic/accessible details**

Use meaningful headings, `<article>` for Work cards/details, `<nav aria-label="Work pagination">` where custom nav markup exists, descriptive link text, `alt` from Work title on real covers, and `aria-hidden="true"` only for decorative assets.

- [ ] **Step 5: Run all repository/Odoo content tests and verify GREEN**

Expected: accessibility/responsive contracts, model tests, HTTP tests, and snippet tests all pass.

- [ ] **Step 6: Commit**

```bash
git add monynha_content theme_monynha tests/test_m4_*_contract.py
git commit -m "feat: harden Monynha content presentation"
```

---

### Task 9: Extend CI to enforce all installation boundaries and upgrades

**Files:**
- Modify: `.github/workflows/ci.yml`

**Interfaces:**
- Consumes: all M4 modules/tests.
- Produces: CI evidence for standalone theme, standalone lead generator, content stack, combined stack, HTTP/model tests, and upgrade regression.

- [ ] **Step 1: Add RED repository assertion for CI coverage**

Extend `tests/test_m4_content_contract.py` to assert `.github/workflows/ci.yml` contains the database/module combinations:

```text
monynha_content_ci
-i monynha_content
-i theme_monynha,monynha_content
-i theme_monynha,monynha_lead_generator
-i theme_monynha,monynha_content,monynha_lead_generator
-u theme_monynha,monynha_content,monynha_lead_generator
```

- [ ] **Step 2: Verify RED with pytest**

Expected: CI contract fails because the current workflow only covers M3 modules.

- [ ] **Step 3: Create dedicated databases in the PostgreSQL setup step**

Add at least:

```bash
createdb -U odoo monynha_content_ci
createdb -U odoo monynha_theme_content_ci
createdb -U odoo monynha_theme_lead_ci
```

Retain existing `monynha_theme_ci`, `monynha_lead_ci`, and combined `monynha_ci`.

- [ ] **Step 4: Add clean content-stack install and test step**

Run:

```bash
-i monynha_content \
--test-tags /monynha_content \
--stop-after-init
```

Because `monynha_content` declares `theme_monynha` and `website_blog`, Odoo resolves those dependencies naturally.

- [ ] **Step 5: Preserve independent theme and lead-generator installs**

Do not remove or weaken the existing standalone `theme_monynha` and standalone `monynha_lead_generator` steps.

- [ ] **Step 6: Add explicit theme+content, theme+lead, and all-module combined runs**

The all-module DB must install:

```bash
-i theme_monynha,monynha_content,monynha_lead_generator \
--test-tags /theme_monynha,/monynha_content,/monynha_lead_generator
```

- [ ] **Step 7: Upgrade the full stack and rerun regression tests**

Use:

```bash
-u theme_monynha,monynha_content,monynha_lead_generator \
--test-tags /theme_monynha,/monynha_content,/monynha_lead_generator
```

against the previously installed all-module DB.

- [ ] **Step 8: Run pytest contract suite locally and push to obtain GitHub Actions evidence**

Expected: contract job green and Odoo job green on the exact branch head.

- [ ] **Step 9: Commit**

```bash
git add .github/workflows/ci.yml tests/test_m4_content_contract.py
git commit -m "ci: validate Monynha M4 module boundaries"
```

---

### Task 10: Document M4 authoring and extension boundaries

**Files:**
- Modify: `README.md`
- Create: `docs/m4-composable-content.md`

**Interfaces:**
- Produces: operator/editor/developer documentation aligned with actual code and routes.

- [ ] **Step 1: Add README module matrix**

Document exactly:

```text
theme_monynha                standalone visual/Website Builder layer
monynha_content              structured Work + Blog aggregation; depends on theme
monynha_lead_generator       discovery/CRM journey; independent from content
```

Include supported installation combinations and state that theme-only `/labs` is a fallback while structured `/labs` is owned by `monynha_content` when installed.

- [ ] **Step 2: Write `docs/m4-composable-content.md`**

Include concrete sections:

```text
Architecture and dependencies
Creating/publishing a Work record
Project / Case / Lab types
Tags, cover image, SEO, publication and website assignment
Public route table
Static snippet inventory
Dynamic snippet inventory
Using Odoo +New page templates
Blog/Insights ownership
Theme-only and content-installed /labs behavior
Security/public-read model
Multiwebsite behavior
Extension points and non-goals
Test/CI matrix
```

- [ ] **Step 3: Verify docs against manifests/routes/snippet XML**

Run simple grep/diff checks so every documented route/snippet/module name exists in code and no removed M3 behavior is described as current.

- [ ] **Step 4: Commit**

```bash
git add README.md docs/m4-composable-content.md
git commit -m "docs: document Monynha M4 content system"
```

---

### Task 11: Final regression, exact-scope review, and PR preparation

**Files:**
- Review only unless a regression fix is required.

**Interfaces:**
- Consumes: all previous tasks.
- Produces: verified M4 branch ready for review; no merge.

- [ ] **Step 1: Run the full repository contract suite**

```bash
pytest -q tests
```

Expected: PASS.

- [ ] **Step 2: Run/confirm the exact GitHub Actions workflow on branch head**

Required green evidence:

```text
contract
standalone theme install/tests
standalone lead-generator install/tests
content stack install/model/HTTP/snippet tests
theme+content
theme+lead
all modules together
full-stack upgrade/regression
```

- [ ] **Step 3: Compare branch against `main`**

Confirm the merge base is the M3 `main` commit used to create `feat/m4-composable-content`, and review every changed file. Expected scope is only:

```text
theme_monynha/**
monynha_content/**
tests/**
.github/workflows/ci.yml
README.md
docs/m4-composable-content.md
docs/superpowers/specs/2026-09-05-monynha-m4-composable-content-design.md
docs/superpowers/plans/2026-09-05-monynha-m4-composable-content.md
```

No `monynha_lead_generator` functional code should change unless a test proves an M4 regression requires a compatibility-only fix.

- [ ] **Step 4: Re-check architectural invariants**

Verify explicitly:

```text
theme manifest has no monynha_content dependency
lead generator has no monynha_content dependency
content depends on theme + website + website_blog
no public POST/write route
no generic public model ACL
no parallel article model
no duplicate project/case/lab models
no fake content
no external runtime dependency introduced
standard website.layout remains canonical
```

- [ ] **Step 5: Open a PR without merging**

Suggested title:

```text
M4: add composable Monynha content and Website Builder library
```

PR body must summarize module boundaries, Work routes/model, static/dynamic snippets, native page templates, Blog reuse, security/multiwebsite behavior, and exact CI evidence. Do not merge without explicit user instruction.

---

## Self-review result

The plan covers every approved spec area: theme independence, reusable primitives, static snippets, native Odoo new-page templates, one Work model, hybrid rich-content authorship, Work routes, `/labs` fallback/ownership, dynamic server-rendered snippets, Blog reuse, publication, SEO, multiwebsite isolation, scoped public reads, backend ACLs, responsive/accessibility hardening, installation boundaries, CI upgrades, and documentation.

No M4 requirement is intentionally deferred. The implementation sequence is TDD-first: repository contracts → static library → page templates → model → query boundary → HTTP surface → dynamic snippets → presentation hardening → CI → documentation → final regression/PR.