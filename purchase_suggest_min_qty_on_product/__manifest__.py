# -*- coding: utf-8 -*-
# © 2015-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Purchase Suggest Min Qty on Product',
    'version': '10.0.1.0.0',
    'category': 'Purchase',
    'license': 'AGPL-3',
    'summary': 'Replace orderpoints by a min_qty field on product',
    'description': """
Purchase Suggest Min Qty on Product
===================================

With this module, instead of using orderpoints, we add *min_qty* and *max_qty* fields on product.product and we use this value as the minimum stock. This makes it easier for users to read and update min_qty and max_qty. But this should only be used if there is only 1 warehouse where we handle min stock rules (because, with this module, you cannot set min_qty/max_qty per warehouse or per stock location).

This module has been written by Alexis de Lattre from Akretion <alexis.delattre@akretion.com>.
    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com',
    'depends': ['purchase_suggest'],
    'data': [
        'product_view.xml',
        'wizard/purchase_suggest_view.xml',
        ],
    'installable': False,
}
