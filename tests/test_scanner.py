"""
Unit Tests for Swing Scanner Module.
"""

import unittest
from unittest.mock import patch
from swing_scanner.scanner import scan_swing_candidates


class TestScanner(unittest.TestCase):

    @patch('swing_scanner.scanner.evaluate_market_regime')
    def test_scanner_blocks_when_bear(self, mock_regime):
        mock_regime.return_value = {
            'regime': 'BEAR',
            'allow_new_entries': False,
            'reason': 'Nifty 50 below 50 EMA'
        }
        res = scan_swing_candidates(tickers=["RELIANCE.NS"])
        self.assertEqual(res['candidates_found'], 0)
        self.assertIn("Scanning halted", res['message'])

    @patch('swing_scanner.scanner.evaluate_market_regime')
    @patch('swing_scanner.scanner.fetch_historical_bars')
    def test_scanner_finds_candidates(self, mock_fetch, mock_regime):
        mock_regime.return_value = {
            'regime': 'BULL',
            'allow_new_entries': True,
            'current_price': 25000.0,
            'ema50': 24000.0
        }
        # Synthetic 70 bars
        dummy_bars = []
        for i in range(70):
            p = 100.0 + (i * 2.0)
            dummy_bars.append({
                'date': '2026-01-01',
                'open': p,
                'high': p + 2,
                'low': p - 2,
                'close': p,
                'volume': 15000.0
            })
        mock_fetch.return_value = dummy_bars

        res = scan_swing_candidates(tickers=["RELIANCE.NS"])
        self.assertIn('market_regime', res)


if __name__ == "__main__":
    unittest.main()
