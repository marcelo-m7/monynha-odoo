from odoo.tests import HttpCase, tagged


@tagged("-at_install", "post_install")
class TestMonynhaTheme(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        website = cls.env["website"].get_current_website()
        theme = cls.env["ir.module.module"].search([("name", "=", "theme_monynha")], limit=1)
        if not theme:
            raise AssertionError("theme_monynha module was not found")
        website.theme_id = theme
        theme._theme_get_stream_themes().with_context(load_all_views=True)._theme_load(website)

    def test_core_snippets_registered(self):
        keys = {
            "theme_monynha.s_monynha_hero",
            "theme_monynha.s_monynha_services",
            "theme_monynha.s_monynha_process",
            "theme_monynha.s_monynha_labs",
            "theme_monynha.s_monynha_cta",
        }
        views = self.env["ir.ui.view"].search([("key", "in", list(keys)), ("website_id", "!=", False)])
        self.assertEqual(set(views.mapped("key")), keys)
