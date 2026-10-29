"""
Unit Tests for Paper Trader Module.
"""

import unittest
import os
import tempfile
from swing_paper_trader.paper_trader import (
    load_portfolio, save_portfolio, update_and_evaluate
)


class TestPaperTrader(unittest.TestCase):

    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json").name

    def tearDown(self):
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)

    def test_load_and_save_portfolio(self):
        state = load_portfolio(self.temp_file, initial_capital=25000.0)
        self.assertEqual(state['initial_capital'], 25000.0)
        self.assertEqual(state['cash'], 25000.0)
        self.assertEqual(len(state['open_positions']), 0)

        # Modify state and save
        state['cash'] = 15000.0
        state['open_positions'].append({
            'ticker': 'SBIN.NS',
            'entry_price': 800.0,
            'shares': 10,
            'stop_loss': 764.0,
            'target1': 896.0,
            'entry_date': '2026-01-01',
            'hold_days': 1
        })
        save_portfolio(state, self.temp_file)

        # Reload and verify
        reloaded = load_portfolio(self.temp_file)
        self.assertEqual(reloaded['cash'], 15000.0)
        self.assertEqual(len(reloaded['open_positions']), 1)
        self.assertEqual(reloaded['open_positions'][0]['ticker'], 'SBIN.NS')


if __name__ == "__main__":
    unittest.main()
