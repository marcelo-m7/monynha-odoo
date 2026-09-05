from odoo.tests import HttpCase, tagged


@tagged("-at_install", "post_install")
class TestMonynhaContentHttp(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website = cls.env["website"].get_current_website()
        cls.other_website = cls.env["website"].create({"name": "M4 HTTP Other Website"})
        cls.tag = cls.env["monynha.work.tag"].create({"name": "HTTP Architecture"})

        cls.published = cls.env["monynha.work"].create({
            "name": "HTTP Published Work",
            "type": "project",
            "summary": "Public detail marker",
            "is_published": True,
            "website_id": cls.website.id,
            "sequence": 1,
            "tag_ids": [(6, 0, cls.tag.ids)],
        })
        cls.published_lab = cls.env["monynha.work"].create({
            "name": "HTTP Published Lab",
            "type": "lab",
            "summary": "Structured lab marker",
            "is_published": True,
            "website_id": cls.website.id,
            "sequence": 2,
        })
        cls.unpublished = cls.env["monynha.work"].create({
            "name": "HTTP Unpublished Work",
            "type": "case",
            "summary": "Should never be public",
            "website_id": cls.website.id,
            "sequence": 3,
        })
        cls.other_site = cls.env["monynha.work"].create({
            "name": "HTTP Other Website Work",
            "type": "lab",
            "summary": "Wrong website marker",
            "is_published": True,
            "website_id": cls.other_website.id,
            "sequence": 4,
        })
        cls.page_items = cls.env["monynha.work"]
        for index in range(12):
            cls.page_items |= cls.env["monynha.work"].create({
                "name": f"Catalogue Item {index + 1:02d}",
                "type": "project",
                "is_published": True,
                "website_id": cls.website.id,
                "sequence": 10 + index,
            })

    def test_public_catalogue_routes_render(self):
        for route in ("/work", "/projects", "/cases", "/labs"):
            response = self.url_open(route)
            self.assertEqual(response.status_code, 200, route)
        labs = self.url_open("/labs")
        self.assertIn("HTTP Published Lab", labs.text)
        self.assertNotIn("HTTP Other Website Work", labs.text)

    def test_published_current_site_detail_renders(self):
        response = self.url_open(self.published.website_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("HTTP Published Work", response.text)
        self.assertIn("Public detail marker", response.text)

    def test_unpublished_other_site_and_malformed_details_are_404(self):
        for route in (
            self.unpublished.website_url,
            self.other_site.website_url,
            "/work/not-a-valid-slug",
            f"/work/wrong-title-{self.published.id}",
        ):
            response = self.url_open(route, allow_redirects=False)
            self.assertEqual(response.status_code, 404, route)

    def test_catalogue_pagination_is_deterministic(self):
        first_page = self.url_open("/projects?page=1")
        second_page = self.url_open("/projects?page=2")
        self.assertEqual(first_page.status_code, 200)
        self.assertEqual(second_page.status_code, 200)
        self.assertIn("HTTP Published Work", first_page.text)
        self.assertNotIn("Catalogue Item 12", first_page.text)
        self.assertIn("Catalogue Item 12", second_page.text)

    def test_catalogue_tag_filter_and_unknown_tag(self):
        filtered = self.url_open(f"/projects?tag={self.tag.id}")
        self.assertEqual(filtered.status_code, 200)
        self.assertIn("HTTP Published Work", filtered.text)
        self.assertNotIn("Catalogue Item 01", filtered.text)

        empty = self.url_open("/projects?tag=999999999")
        self.assertEqual(empty.status_code, 200)
        self.assertNotIn("HTTP Published Work", empty.text)
        self.assertNotIn("Catalogue Item 01", empty.text)
