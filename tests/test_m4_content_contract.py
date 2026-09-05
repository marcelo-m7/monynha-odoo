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
