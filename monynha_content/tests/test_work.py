from odoo import fields
from odoo.tests import TransactionCase, tagged


@tagged("-at_install", "post_install")
class TestMonynhaWork(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website = cls.env["website"].get_current_website()

    def test_work_defaults_slug_and_tags(self):
        tag = self.env["monynha.work.tag"].create({"name": "Architecture"})
        work = self.env["monynha.work"].create({
            "name": "Architecture Notes",
            "type": "lab",
            "summary": "A real editorial record used only by tests.",
            "website_id": self.website.id,
            "tag_ids": [(6, 0, [tag.id])],
        })
        self.assertEqual(work.type, "lab")
        self.assertFalse(work.is_published)
        self.assertTrue(work.website_url.startswith("/work/"))
        self.assertIn(str(work.id), work.website_url)
        self.assertEqual(work.tag_ids, tag)

    def test_invalid_work_type_is_rejected(self):
        with self.assertRaises(ValueError):
            self.env["monynha.work"].create({
                "name": "Invalid type",
                "type": "not-a-type",
                "website_id": self.website.id,
            })

    def test_published_date_tracks_publication_toggle(self):
        work = self.env["monynha.work"].create({
            "name": "Publication lifecycle",
            "type": "project",
            "website_id": self.website.id,
        })
        self.assertFalse(work.published_date)
        before = fields.Datetime.now()
        work.is_published = True
        self.assertTrue(work.published_date)
        self.assertGreaterEqual(work.published_date, before)
        work.is_published = False
        self.assertFalse(work.published_date)
