# -*- coding: utf-8 -*-
# © 2015-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from odoo.tools import float_compare, float_is_zero
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = 'product.product'

    min_qty = fields.Float(
        string=u'Minimum Quantity', track_visibility='onchange',
        digits=dp.get_precision('Product Unit of Measure'),
        company_dependent=True,
        help="If the forecast quantity is lower than the value of this field, "
        "Odoo will suggest to re-order this product. This field is in the "
        "unit of measure of the product.")
    max_qty = fields.Float(
        string=u'Maximum Quantity', track_visibility='onchange',
        digits=dp.get_precision('Product Unit of Measure'),
        company_dependent=True,
        help="If the forecast quantity is lower than the value of the minimum "
        " quantity, Odoo will suggest to re-order this product to go up to "
        "the maximum quantity. This field is in the unit of measure of the "
        "product.")

    @api.constrains('min_qty', 'max_qty')
    def check_min_max_qty(self):
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        for product in self:
            if (
                    not float_is_zero(
                        product.max_qty, precision_digits=precision) and
                    float_compare(
                        product.max_qty, product.min_qty,
                        precision_digits=precision) != 1):
                raise ValidationError(_(
                    "On product '%s', the maximum quantity (%s) is lower "
                    "than the minimum quantity (%s).") % (
                    product.name_get()[0][1],
                    product.max_qty, product.min_qty))
