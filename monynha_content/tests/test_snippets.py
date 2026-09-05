from types import SimpleNamespace

from odoo.tests import TransactionCase, tagged


@tagged("-at_install", "post_install")
class TestMonynhaContentSnippets(TransactionCase):
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
        cls.empty_website = cls.env["website"].create({"name": "M4 Empty Snippet Website"})
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

    def _render(self, key, website=None, main_object=False):
        website = website or self.website
        request_stub = SimpleNamespace(env=self.env, website=website)
        rendered = self.env["ir.ui.view"]._render_template(
            f"monynha_content.{key}",
            {
                "request": request_stub,
                "main_object": main_object,
            },
        )
        return str(rendered)

    def test_dynamic_snippets_exist_and_use_monynha_group(self):
        registration = self.env.ref("monynha_content.snippets")
        arch = registration.arch_db
        for key in self.SNIPPET_KEYS:
            self.assertTrue(self.env.ref(f"monynha_content.{key}"))
            self.assertIn(f't-snippet="monynha_content.{key}"', arch)
        self.assertGreaterEqual(arch.count('group="monynha"'), len(self.SNIPPET_KEYS))

    def test_latest_labs_filters_publication_and_website_and_handles_empty_state(self):
        rendered = self._render("s_monynha_latest_labs")
        self.assertIn("Published Lab", rendered)
        self.assertNotIn("Unpublished Lab", rendered)

        empty = self._render("s_monynha_latest_labs", website=self.empty_website)
        self.assertNotIn("Published Lab", empty)
        self.assertNotIn("broken", empty.lower())

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
            self._render(key, main_object=False)

        self.assertIn(
            "Snippet Architecture",
            self._render("s_monynha_work_tags", main_object=self.published_lab),
        )
        self.assertIn(
            "Lab",
            self._render("s_monynha_work_metadata", main_object=self.published_lab),
        )

    def test_insights_snippets_use_standard_blog_post(self):
        latest = self._render("s_monynha_latest_insights")
        grid = self._render("s_monynha_insights_grid")
        self.assertIn("Published Insight", latest)
        self.assertIn("Published Insight", grid)
        self.assertIn(self.insight.website_url, latest)
        self.assertNotIn("monynha.article", self.env.registry.models)
