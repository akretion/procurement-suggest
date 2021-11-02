# Copyright 2019-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Reordering Rules Min/Max Suggest',
    'version': '14.0.1.0.0',
    'category': 'Procurement',
    'license': 'AGPL-3',
    'summary': 'Suggest new min/max qty for orderpoints',
    'description': """
Reordering Rules Min/Max Suggest
================================

This module suggests updated values for min and max quantity on reordering rules.

You may want to increase the **transient_age_limit** (default value = 1h) in your Odoo server configuration file, in order to let some time to the user to finish his work on orderpoint min/max suggestions.

This module has been written by Alexis de Lattre from Akretion France <alexis.delattre@akretion.com>.
    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com',
    'depends': ['stock'],
    'data': [
        'wizard/stock_orderpoint_suggest_view.xml',
        'security/ir.model.access.csv',
        ],
    'installable': True,
}
