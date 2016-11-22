# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.model
    def _procure_orderpoint_confirm(
            self, use_new_cursor=False, company_id=False):
        return super(ProcurementOrder, self.with_context(
            suggest_procure_orderpoint_confirm=True)).\
            _procure_orderpoint_confirm(
                use_new_cursor=use_new_cursor, company_id=company_id)
