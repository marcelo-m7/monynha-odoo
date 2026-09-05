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


def test_m4_container_avoids_mixed_unit_sass_min():
    scss = (THEME / "static/src/scss/components.scss").read_text()
    assert "min(100% - 2rem" not in scss
    assert "min(100%, 16rem)" not in scss
    assert "width: calc(100% - 2rem);" in scss
    assert "max-width: 80rem;" in scss


def test_m4_preserves_reduced_motion_and_has_no_external_runtime_assets():
    component_scss = (THEME / "static/src/scss/components.scss").read_text()
    assert "prefers-reduced-motion: reduce" in component_scss

    runtime_text = "\n".join(
        path.read_text(errors="ignore")
        for path in list((THEME / "static/src").rglob("*.scss"))
        + list((THEME / "views").rglob("*.xml"))
        + list((THEME / "data").rglob("*.xml"))
    ).lower()
    forbidden = ("fonts.googleapis.com", "fonts.gstatic.com", "cdnjs.cloudflare.com", "unpkg.com", "@import url(")
    assert not any(token in runtime_text for token in forbidden)


def test_theme_runtime_chrome_styles_are_isolated_to_active_monynha_site():
    manifest = _manifest(THEME / "__manifest__.py")
    assert "views/customizations.xml" in manifest["data"]

    customization = (THEME / "views/customizations.xml").read_text()
    assert 'inherit_id="website.layout"' in customization
    assert "wrapwrap" in customization
    assert "monynha-site" in customization

    scss = (THEME / "static/src/scss/website.scss").read_text()
    root_level_forbidden = (
        "body {",
        "#wrap {",
        "h1, h2, h3, h4, h5, h6, .monynha-display {",
        "::selection {",
        ":focus-visible {",
        "header#top {",
        "footer#bottom,",
    )
    for line in scss.splitlines():
        if line == line.lstrip():
            assert not any(line.startswith(selector) for selector in root_level_forbidden), line
    assert ".monynha-site {" in scss
