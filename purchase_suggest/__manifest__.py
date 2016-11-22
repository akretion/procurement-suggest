# -*- coding: utf-8 -*-
# © 2015-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Purchase Suggest',
    'version': '10.0.1.0.0',
    'category': 'Purchase',
    'license': 'AGPL-3',
    'summary': 'Suggest POs from special suggest orderpoints',
    'description': """
Purchase Suggest
================

This module is an ALTERNATIVE to the module *procurement_suggest* ; it is similar but it only handles the purchase orders and doesn't generate any procurement : the suggestions create a new purchase order directly.

The advantage is that you are not impacted by the faulty procurements (for example :  a procurement generates a PO ; the PO is confirmed ; the related picking is cancelled and deleted -> the procurements will always stay in running without related stock moves !)

To use this module, you need to apply the patch *odoo-purchase_suggest.patch* on the source code of Odoo.

You may want to increase the osv_memory_age_limit (default value = 1h) in Odoo server config file, in order to let some time to the purchase user to finish his work on the purchase suggestions.

This module has been written by Alexis de Lattre from Akretion <alexis.delattre@akretion.com>.
    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com',
    'depends': ['purchase'],
    'conflicts': ['procurement_suggest'],
    'data': [
        'stock_view.xml',
        'wizard/purchase_suggest_view.xml',
        ],
    'installable': True,
}
