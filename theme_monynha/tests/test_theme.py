from odoo.tests import HttpCase, tagged


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

    def test_active_theme_marks_site_shell(self):
        response = self.url_open("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("monynha-site", response.text)
        self.assertIn('<meta name="theme-color" content="#020205"', response.text)

    def test_core_m2_and_m3_snippets_registered(self):
        keys = {
            "theme_monynha.s_monynha_hero",
            "theme_monynha.s_monynha_services",
            "theme_monynha.s_monynha_process",
            "theme_monynha.s_monynha_labs",
            "theme_monynha.s_monynha_cta",
            "theme_monynha.s_monynha_signal",
            "theme_monynha.s_monynha_selected_work",
            "theme_monynha.s_monynha_capability",
            "theme_monynha.s_monynha_manifesto",
            "theme_monynha.s_monynha_metrics",
            "theme_monynha.s_monynha_faq",
            "theme_monynha.s_monynha_intro",
            "theme_monynha.s_monynha_principles",
            "theme_monynha.s_monynha_labs_showcase",
        }
        views = self.env["ir.ui.view"].search([("key", "in", list(keys)), ("website_id", "!=", False)])
        self.assertEqual(set(views.mapped("key")), keys)

    def test_m4_static_snippets_registered(self):
        views = self.env["ir.ui.view"].search([
            ("key", "in", list(M4_STATIC_KEYS)),
            ("website_id", "!=", False),
        ])
        self.assertEqual(set(views.mapped("key")), M4_STATIC_KEYS)

    def test_m4_new_page_templates_registered(self):
        for xmlid in M4_PAGE_TEMPLATE_XMLIDS:
            page = self.env.ref(xmlid, raise_if_not_found=False)
            self.assertTrue(page, xmlid)
            self.assertEqual(page._name, "theme.website.page")
            self.assertTrue(page.is_new_page_template, xmlid)

    def test_theme_page_starters_registered(self):
        xmlids = (
            "theme_monynha.page_start",
            "theme_monynha.page_services",
            "theme_monynha.page_services_odoo",
            "theme_monynha.page_services_software",
            "theme_monynha.page_services_ai",
            "theme_monynha.page_process",
            "theme_monynha.page_labs",
            "theme_monynha.page_about",
        )
        for xmlid in xmlids:
            page = self.env.ref(xmlid, raise_if_not_found=False)
            self.assertTrue(page, xmlid)
            self.assertEqual(page._name, "theme.website.page")

    def test_theme_menu_seed_registered(self):
        for xmlid in (
            "theme_monynha.menu_services",
            "theme_monynha.menu_process",
            "theme_monynha.menu_labs",
            "theme_monynha.menu_about",
            "theme_monynha.menu_start",
        ):
            menu = self.env.ref(xmlid, raise_if_not_found=False)
            self.assertTrue(menu, xmlid)
            self.assertEqual(menu._name, "theme.website.menu")
