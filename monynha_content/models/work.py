from odoo import api, fields, models
from odoo.tools.translate import html_translate


class MonynhaWork(models.Model):
    _name = "monynha.work"
    _description = "Monynha Work"
    _inherit = [
        "image.mixin",
        "website.seo.metadata",
        "website.published.multi.mixin",
    ]
    _order = "sequence, published_date desc, id desc"

    name = fields.Char(required=True, translate=True, index=True)
    type = fields.Selection(
        [
            ("project", "Project"),
            ("case", "Case"),
            ("lab", "Lab"),
        ],
        required=True,
        default="project",
        index=True,
    )
    summary = fields.Text(translate=True)
    body_html = fields.Html(translate=html_translate, sanitize=True)
    featured = fields.Boolean(default=False, index=True)
    published_date = fields.Datetime(index=True)
    repository_url = fields.Char()
    external_url = fields.Char()
    sequence = fields.Integer(default=10)
    tag_ids = fields.Many2many("monynha.work.tag", string="Tags")

    @api.depends("name")
    def _compute_website_url(self):
        super()._compute_website_url()
        for work in self:
            if work.id:
                work.website_url = f"/work/{self.env['ir.http']._slug(work)}"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("is_published") and "published_date" not in vals:
                vals["published_date"] = fields.Datetime.now()
        return super().create(vals_list)

    def write(self, vals):
        result = True
        published_fields = set(vals) & {"is_published", "website_published"}
        for work in self:
            copy_vals = dict(vals)
            if published_fields and "published_date" not in vals:
                publication_field = next(iter(published_fields))
                copy_vals["published_date"] = (
                    fields.Datetime.now() if vals[publication_field] else False
                )
            result &= super(MonynhaWork, work).write(copy_vals)
        return result


class MonynhaWorkTag(models.Model):
    _name = "monynha.work.tag"
    _description = "Monynha Work Tag"
    _order = "sequence, name, id"

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    color = fields.Integer()

    _name_uniq = models.Constraint(
        "unique (name)",
        "Tag name already exists!",
    )
