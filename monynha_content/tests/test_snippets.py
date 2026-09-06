from odoo.tests import HttpCase, tagged


@tagged("-at_install", "post_install")
class TestMonynhaContentSnippets(HttpCase):
    SNIPPET_KEYS = (
        "s_monynha_featured_work",
        "s_monynha_work_grid",
        "s_monynha_latest_projects",
        "s_monynha_selected_cases",
        "s_monynha_latest_labs",
        "s_monynha_related_work",
        "s_monynha_work_tags",
        "s_monynha_work_metadata",
        "s_monynha_work_navigation",
        "s_monynha_latest_insights",
        "s_monynha_insights_grid",
    )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website = cls.env["website"].get_current_website()
        cls.tag = cls.env["monynha.work.tag"].create({"name": "Snippet Architecture"})
        cls.published_lab = cls.env["monynha.work"].create({
            "name": "Published Lab",
            "type": "lab",
            "summary": "Visible lab snippet marker",
            "is_published": True,
            "website_id": cls.website.id,
            "tag_ids": [(6, 0, cls.tag.ids)],
        })
        cls.unpublished_lab = cls.env["monynha.work"].create({
            "name": "Unpublished Lab",
            "type": "lab",
            "summary": "Hidden lab snippet marker",
            "website_id": cls.website.id,
        })
        cls.featured_project = cls.env["monynha.work"].create({
            "name": "Featured Project",
            "type": "project",
            "summary": "Featured project marker",
            "featured": True,
            "is_published": True,
            "website_id": cls.website.id,
        })
        cls.published_case = cls.env["monynha.work"].create({
            "name": "Selected Case",
            "type": "case",
            "summary": "Selected case marker",
            "featured": True,
            "is_published": True,
            "website_id": cls.website.id,
        })
        cls.blog = cls.env["blog.blog"].create({
            "name": "Monynha Insights Test",
            "website_id": cls.website.id,
        })
        cls.insight = cls.env["blog.post"].create({
            "name": "Published Insight",
            "blog_id": cls.blog.id,
            "content": "<p>Real Blog content marker.</p>",
            "teaser_manual": "Published insight teaser",
            "is_published": True,
        })

    def setUp(self):
        super().setUp()
        self._render_counter = 0

    def _render(self, key, main_object=False):
        self._render_counter += 1
        suffix = f"{key}_{self._render_counter}"
        if main_object:
            slug_value = main_object.website_url.rsplit("/", 1)[-1]
            setup = (
                "<t t-set=\"main_object\" "
                "t-value=\"request.env['monynha.content.query']"
                f".get_work_by_slug(request.website, '{slug_value}')\"/>"
            )
        else:
            setup = '<t t-set="main_object" t-value="False"/>'
        view = self.env["ir.ui.view"].create({
            "name": f"M4 snippet test {suffix}",
            "type": "qweb",
            "key": f"monynha_content.test_snippet_{suffix}",
            "arch_db": f'<div>{setup}<t t-call="monynha_content.{key}"/></div>',
        })
        page = self.env["website.page"].create({
            "view_id": view.id,
            "url": f"/m4-snippet-test/{suffix}",
            "is_published": True,
            "website_id": self.website.id,
        })
        self.website._force()
        response = self.url_open(page.url)
        self.assertEqual(response.status_code, 200)
        return response.text

    def test_dynamic_snippets_exist_and_use_monynha_group(self):
        registration = self.env.ref("monynha_content.snippets")
        arch = registration.arch_db
        for key in self.SNIPPET_KEYS:
            self.assertTrue(self.env.ref(f"monynha_content.{key}"))
            self.assertIn(f't-snippet="monynha_content.{key}"', arch)
        self.assertGreaterEqual(arch.count('group="monynha"'), len(self.SNIPPET_KEYS))

    def test_builder_preview_renders_without_frontend_request_website(self):
        # Reproduce the Website Builder backend RPC path from the production
        # traceback.  This request has request.env, but does not initialize the
        # frontend-only request.website attribute.
        self.authenticate("admin", "admin")
        rendered = self.make_jsonrpc_request(
            "/web/dataset/call_kw/ir.ui.view/render_public_asset",
            {
                "model": "ir.ui.view",
                "method": "render_public_asset",
                "args": ["monynha_content.s_monynha_featured_work"],
                "kwargs": {"context": {"website_id": self.website.id}},
            },
        )
        self.assertIn("Featured Project", rendered)

    def test_latest_labs_filters_publication_and_handles_empty_state(self):
        rendered = self._render("s_monynha_latest_labs")
        self.assertIn("Published Lab", rendered)
        self.assertNotIn("Unpublished Lab", rendered)

        self.env["monynha.work"].search([("type", "=", "lab")]).write({"is_published": False})
        empty = self._render("s_monynha_latest_labs")
        self.assertNotIn("Published Lab", empty)
        self.assertIn("No labs are published yet.", empty)

    def test_work_snippets_use_real_work_records(self):
        self.assertIn("Featured Project", self._render("s_monynha_featured_work"))
        self.assertIn("Featured Project", self._render("s_monynha_latest_projects"))
        self.assertIn("Selected Case", self._render("s_monynha_selected_cases"))
        self.assertIn("Published Lab", self._render("s_monynha_work_grid"))

    def test_detail_helpers_are_defensive_and_render_for_work(self):
        for key in (
            "s_monynha_related_work",
            "s_monynha_work_tags",
            "s_monynha_work_metadata",
            "s_monynha_work_navigation",
        ):
            self._render(key)

        self.assertIn(
            "Snippet Architecture",
            self._render("s_monynha_work_tags", main_object=self.published_lab),
        )
        self.assertIn(
            "Lab",
            self._render("s_monynha_work_metadata", main_object=self.published_lab),
        )
        self.assertIn(
            "/labs",
            self._render("s_monynha_work_navigation", main_object=self.published_lab),
        )

    def test_insights_snippets_use_standard_blog_post(self):
        latest = self._render("s_monynha_latest_insights")
        grid = self._render("s_monynha_insights_grid")
        self.assertIn("Published Insight", latest)
        self.assertIn("Published Insight", grid)
        self.assertIn(self.insight.website_url, latest)
        self.assertNotIn("monynha.article", self.env.registry.models)
