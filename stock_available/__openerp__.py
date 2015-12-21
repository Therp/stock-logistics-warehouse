# -*- coding: utf-8 -*-
# © 2014 Numérigraphe SARL.
# © 2015 Therp BV (http://therp.nl).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Stock available to promise',
    'version': '2.0',
    "author": u"Numérigraphe,Odoo Community Association (OCA)",
    'category': 'Warehouse',
    'depends': [
        'stock',
        'delivery',  # Because it adds required fields to stock.move
    ],
    'license': 'AGPL-3',
    'data': [
        'product_view.xml',
        'res_config_view.xml',
    ]
}
