# -*- coding: utf-8 -*-
# © 2015-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class StockWarehouseOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    suggest = fields.Boolean(string='Suggest', default=True)

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if self._context.get('suggest_procure_orderpoint_confirm'):
            args.append(('suggest', '=', False))
        return super(StockWarehouseOrderpoint, self).search(
            args, offset=offset, limit=limit, order=order, count=count)
