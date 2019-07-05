# Copyright 2015-2019 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class StockWarehouseOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    suggest = fields.Boolean(string='Suggest', default=True)

    @api.depends('name', 'suggest')
    def name_get(self):
        res = []
        for rec in self:
            name = rec.name
            if rec.suggest:
                name = _('%s (S)') % name
            res.append((rec.id, name))
        return res
