from odoo import fields, models


class MonynhaWork(models.Model):
    _name = "monynha.work"
    _description = "Monynha Work"

    name = fields.Char(required=True, translate=True)
