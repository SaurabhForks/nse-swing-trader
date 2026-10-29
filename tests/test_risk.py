"""
Unit Tests for Risk Management & Position Sizing.
"""

import unittest
from swing_risk.risk import calculate_risk_sized_position


class TestRisk(unittest.TestCase):

    def test_risk_sized_calculation(self):
        res = calculate_risk_sized_position(
            total_equity=20000.0,
            stock_price=1000.0,
            stop_loss_price=960.0 # 4.0% risk distance (₹40/share)
        )
        self.assertTrue(res['allowed'])
        # Max risk budget = 2% of 20000 = ₹400
        # Shares by risk = 400 // 40 = 10 shares
        # Slot capital = 20000 // 2 = ₹10,000 -> 10 shares
        self.assertEqual(res['shares'], 10)
        self.assertEqual(res['actual_risk_rupees'], 400.0)

    def test_sector_concentration_block(self):
        existing = [{'ticker': 'TCS.NS', 'sector': 'IT'}]
        res = calculate_risk_sized_position(
            total_equity=20000.0,
            stock_price=1500.0,
            stop_loss_price=1430.0,
            existing_positions=existing,
            stock_sector='IT'
        )
        self.assertFalse(res['allowed'])
        self.assertIn("already has an active position", res['reason'])

    def test_excessive_stop_distance_block(self):
        res = calculate_risk_sized_position(
            total_equity=20000.0,
            stock_price=1000.0,
            stop_loss_price=900.0 # 10% risk -> exceeds 6.5% limit
        )
        self.assertFalse(res['allowed'])
        self.assertIn("exceeds maximum allowable risk", res['reason'])


if __name__ == "__main__":
    unittest.main()
