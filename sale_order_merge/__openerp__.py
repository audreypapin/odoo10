# -*- coding: utf-8 -*-
# © 2010-2018 OPTIMA DSI - OPTIMA COM - OPTIMA FIBRE
# @author: Audrey Papin
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Fusionner des devis",
    "summary": "Permets la fusion de devis d'un même partenaire avant confirmation",
    "version": "10",
    "category": "Sales",
    "website": "https://www.optimadsi.fr",
    "author": "Audrey Papin",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "sale_stock",
    ],
    "data": [
        "views/sale_order.xml",
        "views/sale_order_merge.xml",
    ],
    'price': 15.00,
    'currency': 'EUR'
}
