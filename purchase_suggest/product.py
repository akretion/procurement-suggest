# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # restore v8 field
    seller_id = fields.Many2one(
        'res.partner', related='seller_ids.name', string='Main Supplier',
        readonly=True)
