"""
Unit Tests for Swing Exit Manager.
"""

import unittest
from swing_exit.exit import evaluate_swing_exit


class TestExit(unittest.TestCase):

    def setUp(self):
        self.pos = {
            'ticker': 'RELIANCE.NS',
            'entry_price': 1000.0,
            'stop_loss': 955.0, # 4.5% risk
            'target1': 1120.0, # +12% target
            'peak_price': 1000.0,
            'hold_days': 5
        }

    def test_stop_loss_trigger(self):
        bar = {
            'open': 960.0,
            'high': 970.0,
            'low': 950.0, # touches 955
            'close': 952.0,
            'ema20': 980.0
        }
        exit_p, reason = evaluate_swing_exit(self.pos, bar)
        self.assertIsNotNone(exit_p)
        self.assertEqual(reason, "STOP_LOSS")
        self.assertEqual(exit_p, 955.0)

    def test_target1_trigger(self):
        bar = {
            'open': 1100.0,
            'high': 1130.0, # hits 1120 target
            'low': 1090.0,
            'close': 1125.0,
            'ema20': 1050.0
        }
        exit_p, reason = evaluate_swing_exit(self.pos, bar)
        self.assertIsNotNone(exit_p)
        self.assertEqual(reason, "TARGET_12PCT")
        self.assertEqual(exit_p, 1120.0)

    def test_trail_20ema_trigger(self):
        # Stock gained +7% (peak was 1070), now breaks below 20 EMA
        self.pos['peak_price'] = 1070.0
        bar = {
            'open': 1045.0,
            'high': 1050.0,
            'low': 1030.0,
            'close': 1032.0, # Below 20 EMA (1040)
            'ema20': 1040.0
        }
        exit_p, reason = evaluate_swing_exit(self.pos, bar)
        self.assertIsNotNone(exit_p)
        self.assertEqual(reason, "TRAIL_20EMA")
        self.assertEqual(exit_p, 1032.0)

    def test_time_stop_trigger(self):
        self.pos['hold_days'] = 30
        bar = {
            'open': 1020.0,
            'high': 1025.0,
            'low': 1015.0,
            'close': 1018.0,
            'ema20': 1010.0
        }
        exit_p, reason = evaluate_swing_exit(self.pos, bar)
        self.assertIsNotNone(exit_p)
        self.assertEqual(reason, "TIME_STOP_30D")
        self.assertEqual(exit_p, 1018.0)

    def test_no_exit_when_healthy(self):
        bar = {
            'open': 1020.0,
            'high': 1040.0,
            'low': 1015.0,
            'close': 1035.0,
            'ema20': 1010.0
        }
        exit_p, reason = evaluate_swing_exit(self.pos, bar)
        self.assertIsNone(exit_p)


if __name__ == "__main__":
    unittest.main()
