"""
Unit Tests for Technical Indicators Module with Edge Cases.
"""

import unittest
from swing_core.indicators import (
    calc_sma, calc_ema, calc_atr, calc_rsi, calc_supertrend,
    calc_highest, calc_lowest, enrich_bars
)


class TestIndicators(unittest.TestCase):

    def test_calc_sma(self):
        values = [10.0, 20.0, 30.0, 40.0, 50.0]
        sma3 = calc_sma(values, 3)
        self.assertIsNone(sma3[0])
        self.assertIsNone(sma3[1])
        self.assertAlmostEqual(sma3[2], 20.0)
        self.assertAlmostEqual(sma3[3], 30.0)
        self.assertAlmostEqual(sma3[4], 40.0)

    def test_calc_sma_edge_cases(self):
        self.assertEqual(calc_sma([], 5), [])
        self.assertEqual(calc_sma([10.0, 20.0], 5), [None, None])
        self.assertEqual(calc_sma([10.0], 0), [None])

    def test_calc_ema(self):
        values = [10.0, 10.0, 10.0, 20.0, 20.0]
        ema3 = calc_ema(values, 3)
        self.assertIsNone(ema3[0])
        self.assertIsNone(ema3[1])
        self.assertAlmostEqual(ema3[2], 10.0)
        self.assertAlmostEqual(ema3[3], 15.0)

    def test_calc_ema_edge_cases(self):
        self.assertEqual(calc_ema([], 5), [])
        self.assertEqual(calc_ema([10.0], 5), [None])

    def test_calc_atr(self):
        highs = [105.0, 106.0, 104.0, 108.0]
        lows = [95.0, 96.0, 94.0, 98.0]
        closes = [100.0, 102.0, 99.0, 105.0]
        atr3 = calc_atr(highs, lows, closes, 3)
        self.assertIsNone(atr3[0])
        self.assertIsNone(atr3[1])
        self.assertIsNotNone(atr3[2])
        self.assertGreater(atr3[2], 0.0)

    def test_calc_atr_edge_cases(self):
        self.assertEqual(calc_atr([], [], [], 14), [])
        self.assertEqual(calc_atr([100.0], [90.0], [95.0], 14), [None])

    def test_calc_rsi(self):
        closes = [float(i) for i in range(100, 130)]
        rsi14 = calc_rsi(closes, 14)
        self.assertIsNone(rsi14[0])
        self.assertAlmostEqual(rsi14[14], 100.0)
        self.assertAlmostEqual(rsi14[-1], 100.0)

        closes_down = [float(i) for i in range(130, 100, -1)]
        rsi_down = calc_rsi(closes_down, 14)
        self.assertAlmostEqual(rsi_down[14], 0.0)

    def test_calc_rsi_edge_cases(self):
        self.assertEqual(calc_rsi([], 14), [])
        self.assertEqual(calc_rsi([100.0] * 5, 14), [None] * 5)

    def test_calc_supertrend(self):
        highs = [100.0 + i for i in range(30)]
        lows = [90.0 + i for i in range(30)]
        closes = [95.0 + i for i in range(30)]
        st, st_dir = calc_supertrend(highs, lows, closes, atr_period=10, multiplier=3.0)
        self.assertEqual(len(st), 30)
        self.assertIn(st_dir[-1], [1, -1])

    def test_calc_highest_and_lowest(self):
        values = [5.0, 10.0, 15.0, 8.0, 12.0]
        highs = calc_highest(values, 3)
        lows = calc_lowest(values, 3)
        self.assertEqual(highs[2], 15.0)
        self.assertEqual(highs[3], 15.0)
        self.assertEqual(highs[4], 15.0)
        self.assertEqual(lows[2], 5.0)
        self.assertEqual(lows[3], 8.0)
        self.assertEqual(lows[4], 8.0)

    def test_enrich_bars(self):
        bars = []
        for i in range(70):
            bars.append({
                'date': f"2026-01-{i+1:02d}" if i < 31 else f"2026-02-{i-30:02d}",
                'open': 100.0 + i,
                'high': 105.0 + i,
                'low': 98.0 + i,
                'close': 102.0 + i,
                'volume': 10000.0
            })
        enriched = enrich_bars(bars)
        self.assertIn('ema20', enriched[-1])
        self.assertIn('ema50', enriched[-1])
        self.assertIn('atr14', enriched[-1])
        self.assertIn('rsi14', enriched[-1])
        self.assertIn('ret60', enriched[-1])

    def test_enrich_bars_empty(self):
        self.assertEqual(enrich_bars([]), [])


if __name__ == "__main__":
    unittest.main()
