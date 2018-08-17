# -*- coding: utf-8 -*-
# © 2010-2018 OPTIMA DSI - OPTIMA COM - OPTIMA FIBRE
# @author: Audrey Papin
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Merge Invoice with timesheet sale',
    'summary': 'Merge account invoices with timesheet sale',
    'license': 'AGPL-3',
    'version': '10.0.1.0.2',
    'author': "Optima DSI",
    'maintainer': 'Optima DSI',
    'category': 'Accounting',
    'depends': ['base','account'],
    'website': 'http://www.optimadsi.fr/',
    'data': ['wizard/merge_invoice_view.xml'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 15.00,
    'currency': 'EUR'
}
