from odoo import api, fields, models


class MonynhaContentQuery(models.AbstractModel):
    _name = "monynha.content.query"
    _description = "Monynha Public Content Query"

    @api.model
    def _work_domain(self, website, work_type=None, tag=None, featured=None):
        domain = [
            ("is_published", "=", True),
            ("website_id", "in", [False, website.id]),
        ]
        if work_type:
            domain.append(("type", "=", work_type))
        if tag:
            tag_id = tag.id if hasattr(tag, "id") else int(tag)
            domain.append(("tag_ids", "in", [tag_id]))
        if featured is not None:
            domain.append(("featured", "=", bool(featured)))
        return domain

    @api.model
    def get_works(
        self,
        website,
        work_type=None,
        tag=None,
        featured=None,
        limit=12,
        offset=0,
        order=None,
    ):
        domain = self._work_domain(
            website,
            work_type=work_type,
            tag=tag,
            featured=featured,
        )
        return self.env["monynha.work"].sudo().search(
            domain,
            limit=max(0, int(limit)) if limit is not None else None,
            offset=max(0, int(offset)),
            order=order or "sequence asc, published_date desc, id desc",
        )

    @api.model
    def count_works(self, website, work_type=None, tag=None, featured=None):
        domain = self._work_domain(
            website,
            work_type=work_type,
            tag=tag,
            featured=featured,
        )
        return self.env["monynha.work"].sudo().search_count(domain)

    @api.model
    def get_work_by_slug(self, website, slug_value):
        _, record_id = self.env["ir.http"]._unslug(slug_value or "")
        if not record_id:
            return self.env["monynha.work"]

        domain = self._work_domain(website)
        domain.append(("id", "=", record_id))
        work = self.env["monynha.work"].sudo().search(domain, limit=1)
        if not work:
            return work
        if self.env["ir.http"]._slug(work) != slug_value:
            return self.env["monynha.work"]
        return work

    @api.model
    def get_blog_posts(self, website, limit=3, offset=0):
        domain = [
            ("is_published", "=", True),
            ("website_id", "in", [False, website.id]),
            ("post_date", "<=", fields.Datetime.now()),
        ]
        return self.env["blog.post"].sudo().search(
            domain,
            limit=max(0, int(limit)) if limit is not None else None,
            offset=max(0, int(offset)),
            order="post_date desc, id desc",
        )
