# Copyright 2019-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.tools import float_compare
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
import logging

logger = logging.getLogger(__name__)


class StockOrderpointSuggestGenerate(models.TransientModel):
    _name = 'stock.orderpoint.suggest.generate'
    _description = 'Start to generate the orderpoint suggestions'

    company_id = fields.Many2one(
        'res.company', string='Company', required=True)
    categ_ids = fields.Many2many(
        'product.category', string='Product Categories')
    supplier_ids = fields.Many2many(
        'res.partner', string='Suppliers',
        # ('parent_id', '=', False) in the domain of the 'name' field of
        # product.supplierinfo is provided by product_usability...
        domain=[('parent_id', '=', False)])
    route_ids = fields.Many2many(
        'stock.location.route', string='Routes',
        domain=[('product_selectable', '=', True)])
    location_id = fields.Many2one(
        'stock.location', string='Stock Location', required=True)
    rotation_duration_source = fields.Selection([
        ('wizard', 'Wizard'),
        ('orderpoint_supplierinfo', 'Reordering Rule and Supplierinfo'),
        ], default='wizard', required=True,
        string='Rotation Duration Source')
    # when rotation_duration_source = wizard
    min_days = fields.Integer(string='Min Rotation Duration')
    max_days = fields.Integer(string='Max Rotation Duration')
    # when rotation_duration_source = orderpoint_supplierinfo
    security_days = fields.Integer(
        string='Additional Security Rotation Duration')
    min2max_ratio = fields.Integer(
        string='Min to Max Rotation Duration Ratio',
        help="If you enter 20, the suggested max quantity will be the "
        "suggested min quantity + 20 %")
    suggest_from = fields.Selection([
        ('last', 'Last Rotation'),
        ('avg', 'Average Rotation'),
        ], default='last', string='Suggest From', required=True)
    rotation_average_multiplier = fields.Float(
        string='Average Rotation Duration Multiplier',
        default=2, required=True)

    _sql_constraints = [
        (
            'min_days_positive',
            'CHECK(min_days >= 0)',
            "The value of the field 'Min Rotation Duration' must be positive"),
        (
            'max_days_positive',
            'CHECK(max_days >= 0)',
            "The value of the field 'Max Rotation Duration' must be positive"),
        (
            'security_days_positive',
            'CHECK(security_days >= 0)',
            "The value of the field 'Additional Security Rotation Duration' "
            "must be positive"),
        (
            'min2max_ratio_positive',
            'CHECK(min2max_ratio >= 0)',
            "The value of the field 'Min to Max Ratio' must be positive"),
        (
            'rotation_average_multiplier_positive',
            'CHECK(rotation_average_multiplier > 0)',
            "The value of the field 'Average Rotation Delay Multiplier' "
            "must be strictly positive"),
        ]

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        res['company_id'] = self.env.company.id
        wh = self.env['stock.warehouse'].search(
            [('company_id', '=', res['company_id'])], limit=1)
        if wh:
            res['location_id'] = wh.lot_stock_id.id
        return res

    @api.onchange('min_days')
    def min_max_days_change(self):
        if self.min_days and not self.max_days:
            self.max_days = self.min_days

    @api.constrains('min_days', 'max_days')
    def check_min_max_days(self):
        for wiz in self:
            if wiz.max_days < wiz.min_days:
                raise ValidationError(_(
                    "The min days (%d) cannot be higher than max days (%d).")
                    % (wiz.wiz.min_days, wiz.max_days))

    def _prepare_suggest_line(self, orderpoint, return_locations):
        product = orderpoint.product_id
        seller = product._select_seller(quantity=100000)
        company_id = self.company_id.id
        smo = self.env['stock.move']
        if self.rotation_duration_source == 'wizard':
            min_days = self.min_days
            max_days = self.max_days
        elif self.rotation_duration_source == 'orderpoint_supplierinfo':
            lead_days_res = orderpoint.rule_ids._get_lead_days(orderpoint.product_id)
            min_days = lead_days_res[0] + self.security_days
            max_days = round(min_days * (1 + self.min2max_ratio / 100.0))
        else:
            raise

        sline = {
            'company_id': company_id,
            'orderpoint_id': orderpoint.id,
            'product_id': product.id,
            'supplier_id': seller and seller.name.id or False,
            'min_days': min_days,
            'max_days': max_days,
            }

        # compute rotation
        today_dt = fields.Date.context_today(self)
        today = fields.Date.to_string(today_dt)
        rotation_qty = {
            'last_min_days': min_days,
            'last_max_days': max_days,
            'avg_min_days': min_days * self.rotation_average_multiplier,
            'avg_max_days': max_days * self.rotation_average_multiplier,
            }
        move_domain = [
            ('product_id', '=', product.id),
            ('date', '<=', '%s 00:00:00' % today),  # ends yesterday evening
            ('state', '=', 'done'),
            ('company_id', '=', company_id),
            ]
        regular_loc_domain = [
            ('location_id', '=', self.location_id.id),
            ('location_dest_id', '!=', self.location_id.id),
            ]
        return_loc_domain = []
        if return_locations:
            return_loc_domain = [
                ('location_dest_id', '=', self.location_id.id),
                ('location_id', 'in', return_locations.ids),
                ]
        suggest_from = self.suggest_from
        unit_uom = self.env.ref('uom.product_uom_unit')
        for mxx in ['last_min', 'last_max', 'avg_min', 'avg_max']:
            start_date_dt = today_dt - relativedelta(
                days=rotation_qty[mxx + '_days'])
            start_date = fields.Date.to_string(start_date_dt)
            start_date_domain = [(
                'date', '>=', '%s 00:00:00' % start_date)]
            qty_rg = smo.read_group(
                move_domain + regular_loc_domain + start_date_domain,
                ['product_uom_qty'], [])
            qty = qty_rg[0]['product_uom_qty'] or 0.0
            if return_locations:
                return_qty_rg = smo.read_group(
                    move_domain + return_loc_domain + start_date_domain,
                    ['product_uom_qty'], [])
                return_qty = return_qty_rg and\
                    return_qty_rg[0]['product_uom_qty'] or 0.0
                qty -= return_qty
            if mxx.startswith('avg') and self.rotation_average_multiplier:
                qty = qty / self.rotation_average_multiplier
            sline[mxx + '_rotation_qty'] = qty
            if mxx.startswith(suggest_from):
                # Make it a config param and extend it to other UoMs ?
                if product.uom_id == unit_uom:
                    qty = round(qty, 0)
                sline['new_' + mxx[-3:] + '_qty'] = qty
        return sline

    def _prepare_product_domain(self):
        product_domain = []
        if self.categ_ids:
            product_domain.append(
                ('categ_id', 'child_of', self.categ_ids.ids))
        if self.supplier_ids:
            product_domain.append(
                ('seller_ids.name', 'in', self.supplier_ids.ids))
        if self.route_ids:
            product_domain.append(
                ('route_ids', 'in', self.route_ids.ids))
        return product_domain

    def get_return_locations(self):
        '''Designed to be inherited'''
        return_locs = self.env['stock.location'].search([
            ('usage', '=', 'customer'),
            '|', ('company_id', '=', False), ('company_id', '=', self.company_id.id),
            ])
        return return_locs

    def run(self):
        self.ensure_one()
        soso = self.env['stock.orderpoint.suggest']
        product_domain = self._prepare_product_domain()
        products = self.env['product.product'].search(product_domain)
        if not products:
            raise UserError(_(
                "There are no products matching the filters."))
        orderpoints = self.env['stock.warehouse.orderpoint'].search([
            ('product_id', 'in', products.ids),
            ('location_id', '=', self.location_id.id),
            ('company_id', '=', self.company_id.id),
            ])
        logger.info(
            '%d orderpoints selected for suggestions', len(orderpoints))
        if not orderpoints:
            raise UserError(_(
                "There are no reordering rules on the stock location '%s' "
                "matching the product filters.")
                % self.location_id.display_name)

        return_locs = self.get_return_locations()
        o_suggest_lines = []
        for orderpoint in orderpoints:
            vals = self._prepare_suggest_line(orderpoint, return_locs)
            if vals:
                o_suggest_lines.append(vals)
        o_suggest_lines_sorted = sorted(
            o_suggest_lines, key=lambda to_sort: to_sort['supplier_id'])
        o_suggest_ids = []
        for o_suggest_line in o_suggest_lines_sorted:
            o_suggest = soso.create(o_suggest_line)
            o_suggest_ids.append(o_suggest.id)
        action = self.env['ir.actions.actions']._for_xml_id(
            'stock_orderpoint_min_max_suggest.stock_orderpoint_suggest_action')
        action.update({
            'target': 'current',
            'domain': [('id', 'in', o_suggest_ids)],
        })
        return action


class StockOrderpointSuggest(models.TransientModel):
    _name = 'stock.orderpoint.suggest'
    _description = 'Orderpoint Suggestions'
    _rec_name = 'product_id'

    company_id = fields.Many2one(
        'res.company', string='Company', required=True)
    product_id = fields.Many2one(
        'product.product', string='Product', required=True, readonly=True)
    uom_id = fields.Many2one(
        'uom.uom', string='UoM', related='product_id.uom_id',
        readonly=True)
    supplier_id = fields.Many2one(
        'res.partner', string='Supplier', readonly=True)
    orderpoint_id = fields.Many2one(
        'stock.warehouse.orderpoint', string='Reordering Rule',
        readonly=True)
    location_id = fields.Many2one(
        related='orderpoint_id.location_id',
        string='Location', readonly=True)
    trigger = fields.Selection(
        related='orderpoint_id.trigger',
        readonly=True)
    current_min_qty = fields.Float(
        related='orderpoint_id.product_min_qty',
        string='Current Min Qty', readonly=True,
        digits='Product Unit of Measure',
        help="in the unit of measure for the product")
    current_max_qty = fields.Float(
        related='orderpoint_id.product_max_qty',
        string="Current Max Qty", readonly=True,
        digits='Product Unit of Measure',
        help="in the unit of measure for the product")
    min_days = fields.Integer(string='Min Days', readonly=True)
    max_days = fields.Integer(string='Max Days', readonly=True)
    last_min_rotation_qty = fields.Float(readonly=True)
    last_max_rotation_qty = fields.Float(readonly=True)
    avg_min_rotation_qty = fields.Float(readonly=True)
    avg_max_rotation_qty = fields.Float(readonly=True)
    new_min_qty = fields.Float(
        string='New Min Qty',
        digits='Product Unit of Measure',
        help="New minimum quantity in the unit of measure of the product")
    new_max_qty = fields.Float(
        string='New Max Qty',
        digits='Product Unit of Measure',
        help="New maximum quantity in the unit of measure of the product")


class StockOrderpointUpdateFromSuggest(models.TransientModel):
    _name = 'stock.orderpoint.update.from.suggest'
    _description = 'Update orderpoints from suggestions'

    def update_orderpoints(self):
        self.ensure_one()
        assert self._context.get('active_model') == 'stock.orderpoint.suggest'
        osuggest_ids = self._context.get('active_ids')
        prec = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        updated_orderpoints = self.env['stock.warehouse.orderpoint']
        for line in self.env['stock.orderpoint.suggest'].browse(osuggest_ids):
            op = line.orderpoint_id
            vals = {}
            if float_compare(
                    line.new_max_qty, line.new_min_qty,
                    precision_digits=prec) < 0:
                raise UserError(_(
                    "For the reordering rule '%s' of product '%s' "
                    "the maximum quantity (%s) is bigger than the "
                    "minimum quantity (%s).") % (
                        op.display_name, line.product_id.display_name,
                        line.new_max_qty, line.new_min_qty))
            if float_compare(
                    line.new_min_qty, op.product_min_qty,
                    precision_digits=prec):
                vals['product_min_qty'] = line.new_min_qty
            if float_compare(
                    line.new_max_qty, op.product_max_qty,
                    precision_digits=prec):
                vals['product_max_qty'] = line.new_max_qty
            if vals:
                op.write(vals)
                updated_orderpoints += op
        action = self.env['ir.actions.actions']._for_xml_id(
            'stock.action_orderpoint')
        action['domain'] = [('id', 'in', updated_orderpoints.ids)]
        action['view_mode'] = 'tree,form'
        return action
