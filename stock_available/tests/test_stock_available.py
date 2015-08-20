# -*- coding: utf-8 -*-
"""Tests for quantity available immediately, based on quants."""
##############################################################################
#
#    Copyright (C) 2015 Therp BV <http://therp.nl>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.tests.common import TransactionCase


class TestStockAvailable(TransactionCase):
    """Tests for quantity available immediately, based on quants."""

    def setUp(self):
        """Setup products and moves for test."""
        super(TestStockAvailable, self).setUp()
        product_model = self.env['product.product']
        template_model = self.env['product.template']

        self.uom_unit = self.env.ref('product.product_uom_unit')
        self.uom_kgm = self.env.ref('product.product_uom_kgm')

        # Create product template
        self.template_ab = template_model.create({
            'name': 'templAB',
            'uom_id': self.uom_unit.id,
        })

        # Create product A and B
        self.product_a = product_model.create({
            'name': 'product A',
            'standard_price': 1,
            'type': 'product',
            'uom_id': self.uom_unit.id,
            'default_code': 'A',
            'product_tmpl_id': self.template_ab.id,
        })

        self.product_b = product_model.create({
            'name': 'product B',
            'standard_price': 1,
            'type': 'product',
            'uom_id': self.uom_unit.id,
            'default_code': 'B',
            'product_tmpl_id': self.template_ab.id,
        })

    def test_qty_available(self):
        """Run test to check immediate quantity available."""

        def compare_product_usable_qty(product, value):
            """Assert that factual quantity equals expected quantity."""
            # Refresh, because the function field is not recalculated between
            # transactions
            product.refresh()
            self.assertEqual(product.immediately_usable_qty, value)

        move_model = self.env['stock.move']

        supplier_location = self.env.ref('stock.stock_location_suppliers')
        stock_location = self.env.ref('stock.stock_location_stock')
        customer_location = self.env.ref('stock.stock_location_customers')

        # Create a stock move from INCOMING to STOCK
        stock_move_in_a = move_model.create({
            'location_id': supplier_location.id,
            'location_dest_id': stock_location.id,
            'name': 'MOVE INCOMING -> STOCK ',
            'product_id': self.product_a.id,
            'product_uom': self.product_a.uom_id.id,
            'product_uom_qty': 2,
            'weight_uom_id': self.uom_kgm.id,
        })

        stock_move_in_b = move_model.create({
            'location_id': supplier_location.id,
            'location_dest_id': stock_location.id,
            'name': 'MOVE INCOMING -> STOCK ',
            'product_id': self.product_b.id,
            'product_uom': self.product_b.uom_id.id,
            'product_uom_qty': 3,
            'weight_uom_id': self.uom_kgm.id,
        })

        compare_product_usable_qty(self.product_a, 0)
        compare_product_usable_qty(self.template_ab, 0)

        stock_move_in_a.action_confirm()
        compare_product_usable_qty(self.product_a, 0)
        compare_product_usable_qty(self.template_ab, 0)

        stock_move_in_a.action_assign()
        compare_product_usable_qty(self.product_a, 0)
        compare_product_usable_qty(self.template_ab, 0)

        stock_move_in_a.action_done()
        compare_product_usable_qty(self.product_a, 2)
        compare_product_usable_qty(self.template_ab, 2)

        # will directly trigger action_done on product_b
        # BECAUSE USABLE QUANTITY IS ON TEMPLATE, DOES NOT
        # MATTER WETHER MOVES ARE FOR PRODUCT A OR PRODUCT B
        # WILL NEED DIFFERENT FIELDS FOR TEMPLATE AN PRODUCT TO
        # GET DESIRED FUNCTIONALITY
        stock_move_in_b.action_done()
        compare_product_usable_qty(self.product_a, 5)
        compare_product_usable_qty(self.product_b, 5)
        compare_product_usable_qty(self.template_ab, 5)

        # Create a stock move from STOCK to CUSTOMER
        stock_move_out_a = move_model.create({
            'location_id': stock_location.id,
            'location_dest_id': customer_location.id,
            'name': ' STOCK --> CUSTOMER ',
            'product_id': self.product_a.id,
            'product_uom': self.product_a.uom_id.id,
            'product_uom_qty': 1,
            'weight_uom_id': self.uom_kgm.id,
            'state': 'confirmed',
        })

        stock_move_out_a.action_done()
        compare_product_usable_qty(self.product_a, 4)
        compare_product_usable_qty(self.template_ab, 4)
