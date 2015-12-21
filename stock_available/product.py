#-*- coding: utf-8 -*-
# © 2014 Numérigraphe SARL.
# © 2015 Therp BV (http://therp.nl).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models
from openerp.addons import decimal_precision as dp


class ProductTemplate(models.Model):
    """Add a field for the stock available to promise.
    Useful implementations need to be installed through the Settings menu or by
    installing one of the modules stock_available_*
    """
    _inherit = 'product.template'

    @api.multi
    @api.depends('virtual_available')
    def _immediately_usable_qty(self):
        """Immediately usable quantity calculated with the quant method."""
        location_model = self.env['stock.location']
        product_model = self.env['product.product']
        quant_model = self.env['stock.quant']
        internal_locations = location_model.search([
            ('usage', '=', 'internal')
        ])
        sublocation_ids = []
        for location in internal_locations:
            sublocation_ids += location_model.search([
                ('id', 'child_of', location.id),
                ('id', 'not in', sublocation_ids),
            ]).ids
        for product_template in self:
            product_ids = product_model.search([
                ('product_tmpl_id', '=', product_template.id),
            ]).ids
            quants = quant_model.search([
                ('location_id', 'in', sublocation_ids),
                ('product_id', 'in', product_ids),
                ('reservation_id', '=', False),
            ])
            availability = 0
            for quant in quants:
                availability += quant.qty
            product_template.immediately_usable_qty = availability

    immediately_usable_qty = fields.Float(
        digits=dp.get_precision('Product Unit of Measure'),
        compute='_immediately_usable_qty',
        string='Available to promise (quant calculation)',
        help="Stock for this Product that can be safely proposed "
             "for sale to Customers.\n"
             "The definition of this value can be configured to suit "
             "your needs. This number is obtained by using the new odoo 8 "
             "quants, so it gives us the actual current quants minus reserved"
             "quants."
    )
