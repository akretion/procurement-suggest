# Copyright 2019 Akretion France
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Reordering Rules Min/Max Suggest',
    'version': '12.0.1.0.0',
    'category': 'Procurement',
    'license': 'AGPL-3',
    'summary': 'Suggest new min/max qty for orderpoints',
    'description': """
Reordering Rules Min/Max Suggest
================================

This module suggests updated values for min and max quantity on reordering rules. The use of this module is very similar to the use of the *procurement_suggest* module ; if you haven't installed the *procurement_suggest* module, you should try it.

You may want to increase the osv_memory_age_limit (default value = 1h) in Odoo server config file, in order to let some time to the user to finish his work on orderpoint min/max suggestions.

This module has been written by Alexis de Lattre from Akretion <alexis.delattre@akretion.com>.
    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com',
    'depends': ['stock'],
    'data': [
        'wizard/stock_orderpoint_suggest_view.xml',
        ],
    'installable': True,
}
