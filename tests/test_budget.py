"""
Unit Tests for Budget & Statutory Delivery Charges.
"""

import unittest
from swing_budget.budget import calc_delivery_charges, calculate_position_allocation


class TestBudget(unittest.TestCase):

    def test_calc_delivery_charges(self):
        buy_p = 1000.0
        sell_p = 1120.0
        shares = 10
        res = calc_delivery_charges(buy_p, sell_p, shares)

        self.assertEqual(res['buy_value'], 10000.0)
        self.assertEqual(res['sell_value'], 11200.0)
        self.assertEqual(res['gross_pnl'], 1200.0)

        # STT = 0.1% buy (10.0) + 0.1% sell (11.20) = 21.20
        self.assertAlmostEqual(res['stt_total'], 21.20)
        # DP charges = 15.34
        self.assertEqual(res['dp_charges'], 15.34)
        # Stamp duty = 0.015% of 10000 = 1.50
        self.assertAlmostEqual(res['stamp_duty'], 1.50)

        self.assertGreater(res['net_pnl'], 1100.0)
        self.assertGreater(res['breakeven_sell_price'], buy_p)

    def test_calculate_position_allocation(self):
        alloc = calculate_position_allocation(
            total_capital=20000.0,
            max_concurrent_positions=2,
            stock_price=2000.0
        )
        self.assertEqual(alloc['slot_capital'], 10000.0)
        self.assertEqual(alloc['shares'], 5)
        self.assertEqual(alloc['allocated_value'], 10000.0)


if __name__ == "__main__":
    unittest.main()
