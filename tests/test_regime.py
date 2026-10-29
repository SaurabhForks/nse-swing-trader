"""
Unit Tests for Nifty 50 Market Regime Filter.
"""

import unittest
from swing_regime.regime import evaluate_market_regime


class TestRegime(unittest.TestCase):

    def _make_dummy_bars(self, base_price, slope=1.0, count=250):
        bars = []
        for i in range(count):
            p = base_price + (i * slope)
            bars.append({
                'date': f"2025-01-01",
                'open': p,
                'high': p + 10,
                'low': p - 10,
                'close': p,
                'volume': 1000000.0
            })
        return bars

    def test_bull_regime(self):
        bars = self._make_dummy_bars(base_price=20000.0, slope=25.0, count=250)
        res = evaluate_market_regime(bars)
        self.assertEqual(res['regime'], "BULL")
        self.assertTrue(res['allow_new_entries'])
        self.assertEqual(res['allocation_multiplier'], 1.0)

    def test_bear_regime(self):
        bars = self._make_dummy_bars(base_price=26000.0, slope=-30.0, count=250)
        res = evaluate_market_regime(bars)
        self.assertEqual(res['regime'], "BEAR")
        self.assertFalse(res['allow_new_entries'])
        self.assertEqual(res['allocation_multiplier'], 0.0)


if __name__ == "__main__":
    unittest.main()
