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


def test_content_frontend_asset_uses_safe_responsive_grid():
    manifest = _manifest(CONTENT / "__manifest__.py")
    asset = "monynha_content/static/src/scss/content.scss"
    assert asset in manifest.get("assets", {}).get("web.assets_frontend", [])

    scss = (CONTENT / "static/src/scss/content.scss").read_text()
    assert ".monynha-work-grid" in scss
    assert "minmax(0, 1fr)" in scss
    assert "min-width: 0;" in scss
    assert "min(100%," not in scss
    assert "overflow-wrap: anywhere;" in scss


def test_content_templates_preserve_editor_and_accessibility_semantics():
    work_xml = (CONTENT / "views/work_templates.xml").read_text()
    snippets_xml = (CONTENT / "views/snippets.xml").read_text()
    combined = work_xml + snippets_xml

    assert 't-set="main_object" t-value="work"' in work_xml
    assert 't-field="work.body_html"' in work_xml
    assert "<article" in work_xml
    assert 't-att-alt="work.name"' in work_xml
    assert 'aria-label="Work navigation"' in snippets_xml
    assert "focus-visible" in (ROOT / "theme_monynha/static/src/scss/components.scss").read_text()
    assert "javascript:" not in combined.lower()


def test_ci_covers_m4_installation_and_upgrade_boundaries():
    workflow = (ROOT / ".github/workflows/ci.yml").read_text()
    required = (
        "monynha_content_ci",
        "-i monynha_content",
        "-i theme_monynha,monynha_content",
        "-i theme_monynha,monynha_lead_generator",
        "-i theme_monynha,monynha_content,monynha_lead_generator",
        "-u theme_monynha,monynha_content,monynha_lead_generator",
    )
    for marker in required:
        assert marker in workflow


def test_defaults_do_not_ship_fake_proof():
    shipped = "\n".join(
        p.read_text(errors="ignore")
        for p in list((ROOT / "theme_monynha").rglob("*.xml"))
        + list(CONTENT.rglob("*.xml"))
    ).lower()
    forbidden = ["testimonial", "acme", "fortune 500", "99% uptime", "100+ clients"]
    assert not any(term in shipped for term in forbidden)
