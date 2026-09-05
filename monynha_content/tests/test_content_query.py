from datetime import timedelta

from odoo import fields
from odoo.tests import TransactionCase, tagged


@tagged("-at_install", "post_install")
class TestMonynhaContentQuery(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website_a = cls.env["website"].get_current_website()
        cls.website_b = cls.env["website"].create({"name": "M4 Other Website"})
        cls.tag_architecture = cls.env["monynha.work.tag"].create({"name": "Architecture"})
        cls.tag_odoo = cls.env["monynha.work.tag"].create({"name": "Odoo"})

        cls.global_work = cls.env["monynha.work"].create({
            "name": "Global Published Work",
            "type": "project",
            "is_published": True,
            "website_id": False,
            "tag_ids": [(6, 0, [cls.tag_architecture.id])],
            "sequence": 40,
        })
        cls.project_a = cls.env["monynha.work"].create({
            "name": "Published Project A",
            "type": "project",
            "is_published": True,
            "website_id": cls.website_a.id,
            "featured": True,
            "tag_ids": [(6, 0, [cls.tag_architecture.id, cls.tag_odoo.id])],
            "sequence": 10,
        })
        cls.lab_a = cls.env["monynha.work"].create({
            "name": "Published Lab A",
            "type": "lab",
            "is_published": True,
            "website_id": cls.website_a.id,
            "tag_ids": [(6, 0, [cls.tag_odoo.id])],
            "sequence": 20,
        })
        cls.unpublished_a = cls.env["monynha.work"].create({
            "name": "Unpublished A",
            "type": "case",
            "website_id": cls.website_a.id,
            "sequence": 5,
        })
        cls.project_b = cls.env["monynha.work"].create({
            "name": "Published Project B",
            "type": "project",
            "is_published": True,
            "website_id": cls.website_b.id,
            "sequence": 1,
        })

        cls.blog_a = cls.env["blog.blog"].create({
            "name": "Insights A",
            "website_id": cls.website_a.id,
        })
        cls.blog_b = cls.env["blog.blog"].create({
            "name": "Insights B",
            "website_id": cls.website_b.id,
        })
        now = fields.Datetime.now()
        cls.post_a = cls.env["blog.post"].create({
            "name": "Published Insight A",
            "blog_id": cls.blog_a.id,
            "is_published": True,
            "post_date": now - timedelta(days=1),
        })
        cls.future_post_a = cls.env["blog.post"].create({
            "name": "Future Insight A",
            "blog_id": cls.blog_a.id,
            "is_published": True,
            "post_date": now + timedelta(days=2),
        })
        cls.post_b = cls.env["blog.post"].create({
            "name": "Published Insight B",
            "blog_id": cls.blog_b.id,
            "is_published": True,
            "post_date": now - timedelta(days=1),
        })

        cls.query = cls.env["monynha.content.query"]

    def test_get_works_filters_publication_and_website(self):
        works = self.query.get_works(self.website_a, limit=20)
        self.assertEqual(set(works.ids), {self.global_work.id, self.project_a.id, self.lab_a.id})
        self.assertNotIn(self.unpublished_a, works)
        self.assertNotIn(self.project_b, works)

    def test_get_works_supports_type_tag_featured_and_pagination(self):
        projects = self.query.get_works(self.website_a, work_type="project", limit=20)
        self.assertEqual(set(projects.ids), {self.global_work.id, self.project_a.id})

        architecture = self.query.get_works(self.website_a, tag=self.tag_architecture, limit=20)
        self.assertEqual(set(architecture.ids), {self.global_work.id, self.project_a.id})

        featured = self.query.get_works(self.website_a, featured=True, limit=20)
        self.assertEqual(featured, self.project_a)

        ordered = self.query.get_works(self.website_a, limit=1, offset=1, order="sequence asc, id asc")
        self.assertEqual(ordered, self.lab_a)
        self.assertEqual(self.query.count_works(self.website_a), 3)

    def test_work_slug_lookup_requires_canonical_public_current_site_record(self):
        slug = self.env["ir.http"]._slug(self.project_a)
        self.assertEqual(self.query.get_work_by_slug(self.website_a, slug), self.project_a)
        self.assertFalse(self.query.get_work_by_slug(self.website_a, "malformed"))
        self.assertFalse(self.query.get_work_by_slug(self.website_a, f"wrong-name-{self.project_a.id}"))
        self.assertFalse(
            self.query.get_work_by_slug(self.website_a, self.env["ir.http"]._slug(self.unpublished_a))
        )
        self.assertFalse(
            self.query.get_work_by_slug(self.website_a, self.env["ir.http"]._slug(self.project_b))
        )

    def test_blog_query_uses_blog_post_and_excludes_future_or_other_site(self):
        posts = self.query.get_blog_posts(self.website_a, limit=10)
        self.assertEqual(posts, self.post_a)
        self.assertNotIn(self.future_post_a, posts)
        self.assertNotIn(self.post_b, posts)
