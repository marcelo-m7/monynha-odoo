# Monynha M3 Theme Completion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Finish `theme_monynha` as a polished, Odoo-native Monynha Softwares Website theme while preserving standard Odoo Website ownership, editability and upgrade safety.

**Architecture:** Keep `website.layout`, standard header/footer rendering, `theme.website.page`, `theme.website.menu`, `configurator_snippets` and Website Builder as the canonical structure. M3 changes presentation, reusable snippets, seeded editorial content, static brand assets and responsive/accessibility styling only; it introduces no business model, parallel CMS, frontend framework or dependency on `monynha_lead_generator`.

**Tech Stack:** Odoo 19 Community, QWeb/XML, SCSS, theme models, Website Builder, pytest contract tests, Odoo HttpCase, PostgreSQL 16, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-05-monynha-m3-theme-completion-design.md`

## Global Constraints

- Target Odoo 19 Community.
- `theme_monynha` must remain independently installable.
- `theme_monynha` must not depend on `monynha_lead_generator`.
- Keep standard Odoo Website header/footer rendering; do not hardcode a parallel navigation tree.
- Seed editable public pages only through `theme.website.page`.
- Seed navigation only through `theme.website.menu`.
- Keep homepage composition in `configurator_snippets`; do not seed `/` as direct `website.page` data.
- Website Builder remains canonical after installation.
- No React, Vue, iframe frontend, Framer Motion, external runtime, mandatory CDN or external API.
- No business models such as `monynha.project` or `monynha.lab`.
- No fabricated client outcomes, testimonials, commercial metrics or unsupported case-study claims.
- No source-database IDs.
- Preserve keyboard navigation, visible focus, responsive behavior and `prefers-reduced-motion`.
- Clean install and upgrade must remain CI gates.

---

### Task 1: Lock M3 theme contracts and brand asset boundary

**Files:**
- Modify: `tests/test_module_contract.py`
- Modify: `theme_monynha/tests/test_theme.py`
- Create: `theme_monynha/static/src/img/monynha-wordmark.svg`
- Modify: `theme_monynha/__manifest__.py`

**Interfaces:**
- Produces static asset `/theme_monynha/static/src/img/monynha-wordmark.svg` for theme-owned presentation.
- Preserves independent addon dependency boundary.

- [ ] **Step 1: Add failing contract assertions**

Extend `tests/test_module_contract.py` with a test that asserts:

```python
def test_m3_theme_contract_and_brand_asset():
    manifest = _manifest('theme_monynha')
    assert 'monynha_lead_generator' not in manifest['depends']
    assert (ROOT / 'theme_monynha/static/src/img/monynha-wordmark.svg').exists()
    homepage = manifest['configurator_snippets']['homepage']
    assert homepage == [
        's_monynha_hero',
        's_monynha_signal',
        's_monynha_services',
        's_monynha_selected_work',
        's_monynha_principles',
        's_monynha_labs_showcase',
        's_monynha_manifesto',
        's_monynha_cta',
    ]
```

Also assert the theme XML does not seed `model="website.page"` for `/`.

- [ ] **Step 2: Run contracts and verify RED**

Run:

```bash
pytest -q tests/test_module_contract.py
```

Expected: failure for missing M3 snippets/asset/homepage order.

- [ ] **Step 3: Add the self-contained wordmark asset**

Create a simple SVG containing only vector/text-path-safe shapes and no external resource references. Keep the asset decorative/presentational; do not replace the standard Website logo record.

- [ ] **Step 4: Update manifest homepage composition**

Set `configurator_snippets.homepage` exactly to the ordered list asserted above. Keep `depends` unchanged except for version bump to `19.0.3.0.0`.

- [ ] **Step 5: Extend Odoo theme test expectations**

Add `theme_monynha.s_monynha_principles` and `theme_monynha.s_monynha_labs_showcase` to the registered snippet key set in `theme_monynha/tests/test_theme.py`.

- [ ] **Step 6: Re-run contracts**

Run:

```bash
pytest -q tests/test_module_contract.py
```

Expected: remaining failures only for snippets not yet implemented.

- [ ] **Step 7: Commit**

```bash
git add tests/test_module_contract.py theme_monynha/tests/test_theme.py theme_monynha/static/src/img/monynha-wordmark.svg theme_monynha/__manifest__.py
git commit -m "test: define Monynha M3 theme contract"
```

---

### Task 2: Finish reusable M3 homepage snippets

**Files:**
- Modify: `theme_monynha/views/snippets.xml`
- Modify: `theme_monynha/views/snippets_m2.xml`
- Create: `theme_monynha/views/snippets_m3.xml`
- Modify: `theme_monynha/__manifest__.py`
- Modify: `theme_monynha/static/src/scss/snippets.scss`
- Modify: `theme_monynha/static/src/scss/components.scss`

**Interfaces:**
- Produces XML IDs `theme_monynha.s_monynha_principles` and `theme_monynha.s_monynha_labs_showcase`.
- Refines existing hero, services, selected-work, manifesto and CTA snippets without changing their XML IDs.

- [ ] **Step 1: Add failing snippet-content contracts**

Assert in `tests/test_module_contract.py` that:

```python
m3 = (ROOT / 'theme_monynha/views/snippets_m3.xml').read_text()
assert 's_monynha_principles' in m3
assert 's_monynha_labs_showcase' in m3
for text in ('FACODI', 'Codoo Importer', 'Monynha Odoo'):
    assert text in m3
for forbidden in ('Open slot', 'Próximo experimento'):
    assert forbidden not in m3
```

Also assert the hero contains `Where Engineering Meets Intuition`, `/start` and `/labs`.

- [ ] **Step 2: Run contracts and verify RED**

```bash
pytest -q tests/test_module_contract.py
```

- [ ] **Step 3: Refine the hero and capability snippets**

Keep `s_monynha_hero` and `s_monynha_services` IDs. Update the hero to use the Monynha wordmark treatment, English brand headline, concise Odoo/custom-software/automation copy, and two semantic links to `/start` and `/labs`. Keep all decorative marks `aria-hidden="true"`.

- [ ] **Step 4: Implement `s_monynha_principles`**

Create a Website Builder snippet with five editorial principles:

```text
Standard first
Smallest useful system
Observable interfaces
Build, verify, observe, improve
Automation with boundaries
```

Use semantic `<article>` cards and no data/model lookup.

- [ ] **Step 5: Implement `s_monynha_labs_showcase`**

Create three editable cards for FACODI, Codoo Importer and Monynha Odoo. Describe only project type/scope; do not claim client outcomes or metrics. Link the section to `/labs`.

- [ ] **Step 6: Register M3 snippets in Website Builder**

Load `views/snippets_m3.xml` in the manifest and add the two snippets to the existing Monynha snippet group.

- [ ] **Step 7: Style M3 snippets responsively**

Add only component classes needed by the new sections. Use grid collapse at tablet/mobile widths, `overflow-wrap`, safe hard-shadow dimensions, and no fixed viewport widths that can cause horizontal scrolling.

- [ ] **Step 8: Run contract tests**

```bash
pytest -q tests/test_module_contract.py
```

Expected: M3 snippet contracts pass.

- [ ] **Step 9: Commit**

```bash
git add theme_monynha tests/test_module_contract.py
git commit -m "feat: complete Monynha homepage snippet system"
```

---

### Task 3: Complete global Website chrome without replacing Odoo structure

**Files:**
- Modify: `theme_monynha/static/src/scss/website.scss`
- Modify: `theme_monynha/static/src/scss/components.scss`
- Modify: `tests/test_module_contract.py`

**Interfaces:**
- Consumes standard Odoo `header#top`, `.navbar`, `.navbar-brand`, `.nav-link`, dropdown/mobile markup and `footer#bottom` / `.o_footer`.
- Produces Monynha visual treatment only; no QWeb header/footer replacement.

- [ ] **Step 1: Add failing chrome contract**

Assert CSS contains selectors for standard header/footer, mobile nav and the `/start` CTA while XML does not inherit/replace the entire `website.layout` header/footer tree.

Required assertions:

```python
website_scss = (ROOT / 'theme_monynha/static/src/scss/website.scss').read_text()
assert 'header#top' in website_scss
assert 'footer.o_footer' in website_scss
assert 'a[href="/start"]' in website_scss
assert '@media' in website_scss
```

- [ ] **Step 2: Run contract and verify RED where new selectors are absent**

```bash
pytest -q tests/test_module_contract.py
```

- [ ] **Step 3: Implement branded navbar treatment**

Style the existing brand/nav/dropdowns/mobile menu with void/paper/violet treatment, thick borders, clear hover/focus states and a visually distinct standard `/start` menu link. Do not create custom menu HTML.

- [ ] **Step 4: Implement branded footer treatment**

Style standard footer surfaces, links and spacing. Do not seed destructive footer content; preserve editor ownership.

- [ ] **Step 5: Add responsive and touch-safe rules**

Ensure nav items and primary CTA have practical touch height, dropdowns remain readable, and display typography cannot overflow narrow screens.

- [ ] **Step 6: Run contracts**

```bash
pytest -q tests/test_module_contract.py
```

- [ ] **Step 7: Commit**

```bash
git add theme_monynha/static/src/scss tests/test_module_contract.py
git commit -m "feat: brand standard Odoo website chrome"
```

---

### Task 4: Refine all seeded public pages and remove starter content

**Files:**
- Modify: `theme_monynha/data/pages.xml`
- Modify: `theme_monynha/static/src/scss/website.scss`
- Modify: `theme_monynha/tests/test_theme.py`
- Modify: `tests/test_module_contract.py`

**Interfaces:**
- Preserves existing page XML IDs and URLs.
- Continues using `theme.website.page` only.

- [ ] **Step 1: Add failing editorial contracts**

Assert all existing URLs remain present and forbid known starter language:

```python
pages = (ROOT / 'theme_monynha/data/pages.xml').read_text()
for route in (
    '/start', '/services', '/services/odoo', '/services/software',
    '/services/ai-automation', '/process', '/labs', '/about',
):
    assert f'<field name="url">{route}</field>' in pages
for forbidden in ('Open slot', 'Próximo experimento', 'Edite, substitua e publique'):
    assert forbidden not in pages
```

Assert `FACODI`, `Codoo Importer` and `Monynha Odoo` appear in Labs content.

- [ ] **Step 2: Run contracts and verify RED**

```bash
pytest -q tests/test_module_contract.py
```

- [ ] **Step 3: Refine `/services` and three service detail pages**

Use the approved editorial direction: Odoo standard-first; software as small operational tools/interfaces/APIs; AI as contextual automation with replaceable providers, fallbacks and human review. Keep all content inside editable `oe_structure` page bodies.

- [ ] **Step 4: Refine `/process`**

Keep exactly the four conceptual stages `Discovery -> Architecture -> Build -> Observe`, improve visual storytelling and retain `/start` CTA.

- [ ] **Step 5: Replace Labs placeholders with real projects**

Use FACODI, Codoo Importer and Monynha Odoo as editable cards. Avoid metrics and unsupported outcome claims.

- [ ] **Step 6: Refine `/about`**

Describe Monynha as a digital engineering studio, include mission and operating principles, and keep the page non-biographical.

- [ ] **Step 7: Preserve `/start` standalone fallback**

Keep theme-only explanation and `/contactus` fallback. Do not duplicate discovery wizard markup.

- [ ] **Step 8: Add/retain meaningful page titles**

Use each template's existing `additional_title` variable with specific titles such as `Services`, `Odoo`, `Software`, `AI & Automation`, `Process`, `Labs`, `About`, and `Start a Project`.

- [ ] **Step 9: Run contracts and Odoo theme tests**

```bash
pytest -q tests/test_module_contract.py
```

Then in Odoo CI-equivalent environment:

```bash
odoo --stop-after-init -d monynha_m3_theme_test -i theme_monynha --test-enable --test-tags /theme_monynha
```

- [ ] **Step 10: Commit**

```bash
git add theme_monynha/data/pages.xml theme_monynha/static/src/scss/website.scss theme_monynha/tests/test_theme.py tests/test_module_contract.py
git commit -m "feat: finish Monynha public page starters"
```

---

### Task 5: Accessibility, motion and visual hardening

**Files:**
- Modify: `theme_monynha/static/src/scss/tokens.scss`
- Modify: `theme_monynha/static/src/scss/components.scss`
- Modify: `theme_monynha/static/src/scss/snippets.scss`
- Modify: `theme_monynha/static/src/scss/website.scss`
- Modify: `tests/test_module_contract.py`

**Interfaces:**
- Applies to all M1/M2/M3 Monynha theme classes.

- [ ] **Step 1: Add failing accessibility contracts**

Assert the aggregate theme SCSS contains:

```text
:focus-visible
prefers-reduced-motion
overflow-wrap
```

and does not contain third-party framework imports or animation-library URLs.

Also assert M3 XML decorative elements use `aria-hidden="true"`.

- [ ] **Step 2: Run contract and verify RED for missing M3 coverage**

```bash
pytest -q tests/test_module_contract.py
```

- [ ] **Step 3: Normalize motion tokens**

Use shared duration/easing tokens for decorative transitions and ensure every animation/transform enhancement has a reduced-motion override.

- [ ] **Step 4: Harden typography and layout**

Use `clamp()`-based display sizes, `minmax(0, 1fr)` where grid overflow is possible, `overflow-wrap: anywhere` for long labels/URLs and smaller hard-shadow offsets on narrow screens.

- [ ] **Step 5: Harden focus/contrast states**

Ensure buttons, cards with links, nav links and footer links have visible keyboard focus on both dark and light surfaces.

- [ ] **Step 6: Run contracts**

```bash
pytest -q tests/test_module_contract.py
```

- [ ] **Step 7: Commit**

```bash
git add theme_monynha/static/src/scss tests/test_module_contract.py
git commit -m "fix: harden Monynha theme accessibility and responsiveness"
```

---

### Task 6: Documentation and exact-head release gate

**Files:**
- Modify: `README.md`
- Create: `docs/m3-theme-completion.md`
- Modify: `.github/workflows/ci.yml` only if current CI no longer covers a required M3 gate

**Interfaces:**
- Documents final ownership and editing model.
- Uses existing CI independent install, combined install and upgrade gates.

- [ ] **Step 1: Write M3 documentation**

Document:

```text
Homepage: configurator snippets
Pages: theme.website.page -> editable website.page copies
Menus: theme.website.menu -> standard Website menus
Header/footer: standard Odoo rendering, Monynha styling only
Labs/Selected Work: editorial Website content
/start: theme fallback; lead generator controller when installed
```

Include final route map and Website Builder editing guidance.

- [ ] **Step 2: Update README**

Add M3 theme-completion status, list current homepage composition and explicitly state the independent-addon boundary.

- [ ] **Step 3: Verify CI already covers required install/upgrade paths**

The current workflow must retain all of these steps:

```text
Install theme independently
Install lead generator independently
Install addons together and run tests
Upgrade addons and rerun regression tests
```

Do not modify CI if these gates remain present and green.

- [ ] **Step 4: Run local/static contract suite**

```bash
pytest -q tests
```

Expected: all contract tests pass.

- [ ] **Step 5: Push final head and wait for GitHub Actions**

Require the exact head to complete with both jobs green:

```text
contract = success
odoo = success
```

The Odoo job must show successful theme-only install, lead-only install, combined install and combined upgrade.

- [ ] **Step 6: Review PR diff for scope leakage**

Confirm no changes under `monynha_lead_generator/` unless a regression test requires a compatibility-only adjustment. Confirm no new model, controller, JS framework, hardcoded database ID, direct homepage `website.page` seed or header/footer replacement.

- [ ] **Step 7: Commit documentation**

```bash
git add README.md docs/m3-theme-completion.md .github/workflows/ci.yml
git commit -m "docs: complete Monynha M3 theme guidance"
```

- [ ] **Step 8: Mark PR ready only after exact-head CI success**

Do not merge without explicit user instruction.
