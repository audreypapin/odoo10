# -*- coding: utf-8 -*-
# © 2010-2018 OPTIMA DSI - OPTIMA COM - OPTIMA FIBRE
# @author: Audrey Papin
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Ajout de Ecotax',
    'summary': 'ajout_ecotax',
    'license': 'AGPL-3',
    'category': 'Purchases',
    'version': '1',
    'author': "Optima DSI",
    'depends': ['purchase'],
    'data': ['inherit_ecotaxe_frais_de_port.xml'],
    'website': 'http://www.optimadsi.fr/',
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 10,
    'currency': 'EUR',
}
