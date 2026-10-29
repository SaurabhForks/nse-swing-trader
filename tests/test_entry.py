"""
Unit Tests for Swing Entry Evaluator with Edge Cases.
"""

import unittest
from swing_entry.entry import evaluate_swing_entry, round_tick


class TestEntry(unittest.TestCase):

    def test_round_tick(self):
        self.assertEqual(round_tick(100.02), 100.05)
        self.assertEqual(round_tick(100.00), 100.00)
        self.assertEqual(round_tick(100.06), 100.10)

    def test_stage2_breakout_entry(self):
        bars = []
        for i in range(70):
            p = 100.0 + (i * 1.5)
            bars.append({
                'date': '2026-01-01',
                'open': p,
                'high': p + 2,
                'low': p - 2,
                'close': p,
                'volume': 10000.0,
                'ema20': p - 5,
                'ema50': p - 10,
                'ema200': p - 25,
                'atr14': 3.0,
                'rsi14': 62.0,
                'vol_sma20': 8000.0,
                'high50': p,
                'ret60': 0.25,
                'rs_spread': 0.10
            })

        bars[-1]['close'] = 220.0
        bars[-1]['high'] = 221.0
        bars[-1]['low'] = 217.0
        bars[-1]['volume'] = 20000.0
        bars[-2]['high50'] = 215.0

        res = evaluate_swing_entry(bars)
        self.assertTrue(res['qualifies'])
        self.assertEqual(res['pattern'], 'MINERVINI_50D_BREAKOUT')
        self.assertGreater(res['entry_price'], res['stop_loss'])
        self.assertGreater(res['target1'], res['entry_price'])

    def test_rejection_below_50ema(self):
        bars = []
        for i in range(70):
            p = 200.0 - (i * 1.0)
            bars.append({
                'date': '2026-01-01',
                'open': p,
                'high': p + 2,
                'low': p - 2,
                'close': p,
                'volume': 10000.0,
                'ema20': p + 5,
                'ema50': p + 10,
                'ema200': p + 20,
                'atr14': 3.0,
                'rsi14': 35.0,
                'vol_sma20': 8000.0,
                'high50': 200.0,
                'ret60': -0.15,
                'rs_spread': -0.05
            })
        res = evaluate_swing_entry(bars)
        self.assertFalse(res['qualifies'])
        self.assertIn("Not in Stage 2 Uptrend", res['reason'])

    def test_rejection_negative_rs(self):
        bars = []
        for i in range(70):
            p = 100.0 + (i * 1.0)
            bars.append({
                'date': '2026-01-01',
                'open': p,
                'high': p + 2,
                'low': p - 2,
                'close': p,
                'volume': 10000.0,
                'ema20': p - 2,
                'ema50': p - 5,
                'ema200': p - 10,
                'atr14': 3.0,
                'rsi14': 58.0,
                'vol_sma20': 8000.0,
                'high50': p,
                'ret60': 0.05,
                'rs_spread': -0.08 # Underperforming index!
            })
        res = evaluate_swing_entry(bars)
        self.assertFalse(res['qualifies'])
        self.assertIn("Underperforming Nifty 50", res['reason'])


if __name__ == "__main__":
    unittest.main()
