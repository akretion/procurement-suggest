# -*- coding: utf-8 -*-
# © 2015-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from odoo.tools import float_compare
from odoo.exceptions import UserError
import logging

logger = logging.getLogger(__name__)


class ProcurementSuggestGenerate(models.TransientModel):
    _name = 'procurement.suggest.generate'
    _description = 'Start to generate the procurement suggestions'

    categ_ids = fields.Many2many(
        'product.category', string='Product Categories')
    seller_ids = fields.Many2many(
        'res.partner', string='Suppliers',
        domain=[('supplier', '=', True)])
    route_ids = fields.Many2many(
        'stock.location.route', string='Routes',
        domain=[('product_selectable', '=', True)])
    location_id = fields.Many2one(
        'stock.location', string='Stock Location', required=True,
        default=lambda self: self.env.ref('stock.stock_location_stock'))

    @api.model
    def _prepare_suggest_line(self, product_id, qty_dict):
        future_qty = qty_dict['virtual_available'] + qty_dict['draft_qty']
        if float_compare(
                qty_dict['max_qty'], qty_dict['min_qty'],
                precision_rounding=qty_dict['product'].uom_id.rounding) == 1:
            # order to go up to qty_max
            procure_qty = qty_dict['max_qty'] - future_qty
        else:
            # order to go up to qty_min
            procure_qty = qty_dict['min_qty'] - future_qty

        sline = {
            'company_id':
            qty_dict['orderpoint'] and qty_dict['orderpoint'].company_id.id,
            'product_id': product_id,
            'seller_id': qty_dict['product'].seller_id.id or False,
            'qty_available': qty_dict['qty_available'],
            'incoming_qty': qty_dict['incoming_qty'],
            'outgoing_qty': qty_dict['outgoing_qty'],
            'draft_qty': qty_dict['draft_qty'],
            'orderpoint_id':
            qty_dict['orderpoint'] and qty_dict['orderpoint'].id,
            'location_id': self.location_id.id,
            'min_qty': qty_dict['min_qty'],
            'max_qty': qty_dict['max_qty'],
            'procure_qty': procure_qty,
            }
        return sline

    @api.model
    def _prepare_product_domain(self):
        product_domain = []
        if self.categ_ids:
            product_domain.append(
                ('categ_id', 'child_of', self.categ_ids.ids))
        if self.seller_ids:
            product_domain.append(
                ('seller_id', 'in', self.seller_ids.ids))
        if self.route_ids:
            product_domain.append(
                ('route_ids', 'in', self.route_ids.ids))
        return product_domain

    @api.model
    def generate_products_dict(self):
        ppo = self.env['product.product']
        swoo = self.env['stock.warehouse.orderpoint']
        products = {}
        products_rec = ppo
        op_domain = [
            ('suggest', '=', True),
            ('company_id', '=', self.env.user.company_id.id),
            ('location_id', 'child_of', self.location_id.id),
            ]
        if self.categ_ids or self.seller_ids or self.route_ids:

            products_subset = ppo.search(self._prepare_product_domain())
            op_domain.append(('product_id', 'in', products_subset.ids))
        ops = swoo.search(op_domain)
        logger.info('%d suggest orderpoints selected', len(ops))
        logger.debug('Suggest orderpoints IDs selected: %s', ops.ids)
        if not ops:
            raise UserError(_(
                "There are no suggest reordering rules corresponding "
                "to the criterias."))
        substract_dict = ops.subtract_procurements_from_orderpoints()
        for op in ops:
            if op.product_id.id not in products:
                products[op.product_id.id] = {
                    'min_qty': op.product_min_qty,
                    'max_qty': op.product_max_qty,
                    'draft_qty': substract_dict[op.id],
                    'orderpoint': op,
                    'product': op.product_id
                    }
                products_rec += op.product_id
            else:
                raise UserError(_(
                    "There are 2 orderpoints (%s and %s) for the same "
                    "product on stock location %s or its "
                    "children.") % (
                        products[op.product_id.id]['orderpoint'].name,
                        op.name,
                        self.location_id.complete_name))
        return products, products_rec

    @api.multi
    def run(self):
        self.ensure_one()
        pso = self.env['procurement.suggest']
        p_suggest_lines = []
        (products, products_rec) = self.generate_products_dict()
        # key = product_id
        # value = {'virtual_qty': 1.0, 'draft_qty': 4.0, 'min_qty': 6.0}
        # They are all in the uom of the product
        logger.info('Starting to compute the procurement suggestions')
        logger.info('Min qty computed on %d products', len(products))
        virtual_qties = products_rec.with_context(
            location=self.location_id.id)._compute_quantities_dict(
                False, False, False)
        logger.info('Stock levels qty computed on %d products', len(products))
        for product_id, qty_dict in products.iteritems():
            qty_dict['virtual_available'] =\
                virtual_qties[product_id]['virtual_available']
            qty_dict['incoming_qty'] =\
                virtual_qties[product_id]['incoming_qty']
            qty_dict['outgoing_qty'] =\
                virtual_qties[product_id]['outgoing_qty']
            qty_dict['qty_available'] =\
                virtual_qties[product_id]['qty_available']
            logger.debug(
                'Product ID: %d Virtual qty = %s Draft qty = %s '
                'Min. qty = %s',
                product_id, qty_dict['virtual_available'],
                qty_dict['draft_qty'], qty_dict['min_qty'])
            compare = float_compare(
                qty_dict['virtual_available'] + qty_dict['draft_qty'],
                qty_dict['min_qty'],
                precision_rounding=qty_dict['product'].uom_id.rounding)
            if compare < 0:
                vals = self._prepare_suggest_line(product_id, qty_dict)
                if vals:
                    p_suggest_lines.append(vals)
                    logger.debug(
                        'Created a procurement suggestion for product ID %d',
                        product_id)
        p_suggest_lines_sorted = sorted(
            p_suggest_lines, key=lambda to_sort: to_sort['seller_id'])
        if p_suggest_lines_sorted:
            p_suggest_ids = []
            for p_suggest_line in p_suggest_lines_sorted:
                p_suggest = pso.create(p_suggest_line)
                p_suggest_ids.append(p_suggest.id)
            action = self.env['ir.actions.act_window'].for_xml_id(
                'procurement_suggest', 'procurement_suggest_action')
            action.update({
                'target': 'current',
                'domain': [('id', 'in', p_suggest_ids)],
            })
            return action
        else:
            raise UserError(_(
                "There are no purchase suggestions to generate."))


class ProcurementSuggest(models.TransientModel):
    _name = 'procurement.suggest'
    _description = 'Procurement Suggestions'
    _rec_name = 'product_id'

    company_id = fields.Many2one(
        'res.company', string='Company', required=True)
    product_id = fields.Many2one(
        'product.product', string='Product', required=True, readonly=True)
    uom_id = fields.Many2one(
        'product.uom', string='UoM', related='product_id.uom_id',
        readonly=True)
    seller_id = fields.Many2one(
        'res.partner', string='Supplier', readonly=True,
        domain=[('supplier', '=', True)])
    qty_available = fields.Float(
        string='Quantity On Hand', readonly=True,
        digits=dp.get_precision('Product Unit of Measure'),
        help="in the unit of measure of the product")
    incoming_qty = fields.Float(
        string='Incoming Quantity', readonly=True,
        digits=dp.get_precision('Product Unit of Measure'),
        help="in the unit of measure of the product")
    outgoing_qty = fields.Float(
        string='Outgoing Quantity', readonly=True,
        digits=dp.get_precision('Product Unit of Measure'),
        help="in the unit of measure of the product")
    draft_qty = fields.Float(
        string='Draft PO/MO', readonly=True,
        digits=dp.get_precision('Product Unit of Measure'),
        help="Draft purchase orders and manufacturing orders. "
        "It is computed from the quantity on procurements "
        "which are not in done nor cancel state. It doesn't "
        "take into account the purchase orders and manufacturing "
        "orders that have been created manually (i.e. not created by "
        "a procurement).")
    orderpoint_id = fields.Many2one(
        'stock.warehouse.orderpoint', string='Re-ordering Rule',
        readonly=True)
    location_id = fields.Many2one(
        'stock.location', string='Stock Location', readonly=True)
    min_qty = fields.Float(
        string="Min Quantity", readonly=True,
        digits=dp.get_precision('Product Unit of Measure'),
        help="in the unit of measure for the product")
    max_qty = fields.Float(
        string="Max Quantity", readonly=True,
        digits=dp.get_precision('Product Unit of Measure'),
        help="in the unit of measure for the product")
    procure_qty = fields.Float(
        string='Quantity to Procure',
        digits=dp.get_precision('Product Unit of Measure'),
        help="Quantity to procure in the unit of measure of the product")


class ProcurementCreateFromSuggest(models.TransientModel):
    _name = 'procurement.create.from.suggest'
    _description = 'Create procurement from suggests'

    @api.multi
    def create_proc(self):
        self.ensure_one()
        assert self._context.get('active_model') == 'procurement.suggest'
        psuggest_ids = self._context.get('active_ids')
        poo = self.env['procurement.order']
        new_procs = poo
        # TODO: add support for qty rounded
        # add support for date planned ?
        # add support for stock_calendar,
        # with _procurement_from_orderpoint_post_process ?
        for line in self.env['procurement.suggest'].browse(psuggest_ids):
            if float_compare(
                    line.procure_qty, 0,
                    precision_rounding=line.uom_id.rounding) == 1:
                vals = line.orderpoint_id._prepare_procurement_values(
                    line.procure_qty)
                vals['origin'] += _(' Suggest')
                vals['name'] += _(' Suggest')
                # _procurement_from_orderpoint_post_process
                new_procs += poo.create(vals)
        if new_procs:
            new_procs.run()
        else:
            raise UserError(_('All requested quantities are null.'))
        action = self.env['ir.actions.act_window'].for_xml_id(
            'procurement', 'procurement_action')
        action['domain'] = [('id', 'in', new_procs.ids)]
        action['view_mode'] = 'tree,form'
        return action
