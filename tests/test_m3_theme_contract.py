from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / "theme_monynha"


def test_standard_odoo_chrome_is_branded_without_parallel_header_or_footer():
    website_scss = (THEME / "static/src/scss/website.scss").read_text()
    assert "header#top" in website_scss
    assert "footer.o_footer" in website_scss
    assert 'a[href="/start"]' in website_scss
    assert ".navbar-collapse" in website_scss
    assert ".dropdown-menu" in website_scss
    assert "@media" in website_scss

    xml = "\n".join(path.read_text() for path in THEME.rglob("*.xml"))
    assert 'position="replace"' not in xml or "//header" not in xml
    assert "<header" not in xml
    assert "<footer" not in xml


def test_seeded_public_pages_are_complete_editorial_starters():
    pages = (THEME / "data/pages.xml").read_text()
    for route in (
        "/start",
        "/services",
        "/services/odoo",
        "/services/software",
        "/services/ai-automation",
        "/process",
        "/labs",
        "/about",
    ):
        assert f'<field name="url">{route}</field>' in pages

    for forbidden in ("Open slot", "Próximo experimento", "Edite, substitua e publique"):
        assert forbidden not in pages

    for project in ("FACODI", "Codoo Importer", "Monynha Odoo"):
        assert project in pages

    for stage in (">Discovery<", ">Architecture<", ">Build<", ">Observe<"):
        assert stage in pages

    assert 'href="/contactus"' in pages
    assert 'model="theme.website.page"' in pages
    assert 'model="website.page"' not in pages


def test_m3_accessibility_motion_and_overflow_contract():
    scss = "\n".join(path.read_text() for path in (THEME / "static/src/scss").glob("*.scss"))
    tokens = (THEME / "static/src/scss/tokens.scss").read_text()
    m3 = (THEME / "views/snippets_m3.xml").read_text()

    assert ":focus-visible" in scss
    assert "prefers-reduced-motion" in scss
    assert "overflow-wrap" in scss
    assert "--monynha-ease-standard" in tokens
    assert "width: min(" not in scss

    lowered = scss.lower()
    for forbidden in ("framer", "reactbits", "@import url("):
        assert forbidden not in lowered

    assert 'class="monynha-labs-orbit monynha-labs-orbit-one" aria-hidden="true"' in m3
    assert 'class="monynha-labs-orbit monynha-labs-orbit-two" aria-hidden="true"' in m3
