"""
Unit Tests for Historical Backtesting Engine.
"""

import unittest
import os
from swing_backtest.backtest import run_swing_backtest

DATA_CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data_cache")


class TestBacktest(unittest.TestCase):

    def test_backtest_execution(self):
        # Run test with cached universe
        res = run_swing_backtest(
            capital=20000.0,
            max_positions=2,
            profit_target_pct=0.12,
            max_risk_pct=0.045,
            cache_dir=DATA_CACHE_DIR
        )

        self.assertEqual(res['initial_capital'], 20000.0)
        self.assertGreater(res['total_trades'], 0)
        self.assertGreater(res['final_equity'], 0)
        self.assertIn('win_rate_pct', res)
        self.assertIn('profit_factor', res)
        self.assertIn('max_drawdown_pct', res)
        # Verify profitability
        self.assertGreater(res['net_pnl'], 0.0)
        self.assertGreater(res['profit_factor'], 1.5)


if __name__ == "__main__":
    unittest.main()
