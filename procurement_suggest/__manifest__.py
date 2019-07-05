# -*- coding: utf-8 -*-
# Copyright 2015-2016 Akretion France
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Procurement Suggest',
    'version': '10.0.1.0.0',
    'category': 'Purchase',
    'license': 'AGPL-3',
    'summary': 'Suggest procurements from special suggest orderpoints',
    'description': """
Procurement Suggest
===================

This module creates procurement suggestions from special *suggest* orderpoints.

IT IS CURRENTLY incompatible with the module purchase_suggest.

You may want to increase the osv_memory_age_limit (default value = 1h) in Odoo server config file, in order to let some time to the user to finish his work on the procurement suggestions.

This module has been written by Alexis de Lattre from Akretion <alexis.delattre@akretion.com>.
    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com',
    'depends': ['stock'],
    'conflicts': ['purchase_suggest'],
    'data': [
        'stock_view.xml',
        'wizard/procurement_suggest_view.xml',
        ],
    'installable': False,
}
