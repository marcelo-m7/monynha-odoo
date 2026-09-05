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
