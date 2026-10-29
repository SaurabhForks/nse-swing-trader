"""
Swing Trade Entry Evaluator for Indian Equities.
Applies Mark Minervini SEPA Trend Template, Relative Strength vs Nifty 50,
and volume confirmation filters to validate high-conviction swing entries.
"""

from typing import Dict, Any, List, Optional
import math


def round_tick(price: float, tick: float = 0.05) -> float:
    """Rounds price to nearest NSE tick (₹0.05)."""
    return round(math.ceil(price / tick) * tick, 2)


def evaluate_swing_entry(
    bars: List[Dict[str, Any]],
    nifty_bars: Optional[List[Dict[str, Any]]] = None,
    max_risk_pct: float = 0.045 # 4.5% initial stop distance
) -> Dict[str, Any]:
    """
    Evaluates whether the latest bar qualifies for a swing entry.
    Returns:
        dict: {
            'qualifies': bool,
            'pattern': str,
            'score': float,
            'entry_price': float,
            'stop_loss': float,
            'target1': float,
            'target2': float,
            'rs_spread': float,
            'rvol': float,
            'reason': str
        }
    """
    if len(bars) < 60:
        return {'qualifies': False, 'reason': 'Insufficient history (< 60 bars)'}

    latest = bars[-1]
    prev = bars[-2]

    close = float(latest['close'])
    high = float(latest['high'])
    low = float(latest['low'])
    vol = float(latest.get('volume', 0.0))

    ema20 = latest.get('ema20')
    ema50 = latest.get('ema50')
    ema200 = latest.get('ema200')
    atr14 = latest.get('atr14')
    rsi14 = latest.get('rsi14')
    vol_sma20 = latest.get('vol_sma20')
    high50_prev = prev.get('high50')
    ret60 = latest.get('ret60')
    rs_spread = latest.get('rs_spread')

    # Basic indicator readiness
    if not (ema20 and ema50 and ema200 and atr14 and vol_sma20 and rsi14 is not None):
        return {'qualifies': False, 'reason': 'Technical indicators not fully computed'}

    # 1. Minervini Stage 2 Filter: Close > 50 EMA > 200 EMA
    if not (close > ema50 and ema50 > ema200):
        return {
            'qualifies': False,
            'reason': f"Not in Stage 2 Uptrend (Close: ₹{close:.2f}, 50EMA: ₹{ema50:.2f}, 200EMA: ₹{ema200:.2f})"
        }

    # 2. Relative Strength vs Benchmark
    if rs_spread is not None and rs_spread < 0:
        return {
            'qualifies': False,
            'reason': f"Underperforming Nifty 50 (RS Spread: {rs_spread*100:.2f}%)"
        }

    rvol = vol / vol_sma20 if vol_sma20 > 0 else 1.0
    candle_ratio = (close - low) / (high - low + 1e-6)

    # 3. Check Patterns
    # Pattern A: Minervini 50-Day Breakout
    if high50_prev and close >= high50_prev:
        if rvol >= 1.25 and rsi14 > 54 and candle_ratio >= 0.55:
            entry_p = round_tick(close)
            stop_loss = round_tick(entry_p * (1.0 - max_risk_pct))
            t1 = round_tick(entry_p * 1.12) # +12%
            t2 = round_tick(entry_p * 1.20) # +20%
            rs_val = rs_spread if rs_spread is not None else 0.0
            score = round(rvol * 20.0 + rs_val * 30.0 + (rsi14 - 50.0), 2)

            return {
                'qualifies': True,
                'pattern': 'MINERVINI_50D_BREAKOUT',
                'score': score,
                'entry_price': entry_p,
                'stop_loss': stop_loss,
                'target1': t1,
                'target2': t2,
                'rvol': round(rvol, 2),
                'rsi14': round(rsi14, 2),
                'rs_spread': round(rs_val * 100.0, 2),
                'reason': f"50-day breakout with volume {rvol:.2f}x average and strong RS spread."
            }

    # Pattern B: Supertrend Momentum Ignition
    prev_st_dir = prev.get('st_dir')
    cur_st_dir = latest.get('st_dir')
    st_level = latest.get('supertrend')

    if prev_st_dir == -1 and cur_st_dir == 1 and rsi14 > 50 and st_level:
        stop_dist_pct = (close - st_level) / close
        if 0.025 <= stop_dist_pct <= 0.065:
            entry_p = round_tick(close)
            stop_loss = round_tick(st_level)
            t1 = round_tick(entry_p * 1.12)
            t2 = round_tick(entry_p * 1.20)
            rs_val = rs_spread if rs_spread is not None else 0.0
            score = round(rvol * 15.0 + rs_val * 25.0 + (rsi14 - 50.0), 2)

            return {
                'qualifies': True,
                'pattern': 'SUPERTREND_IGNITION',
                'score': score,
                'entry_price': entry_p,
                'stop_loss': stop_loss,
                'target1': t1,
                'target2': t2,
                'rvol': round(rvol, 2),
                'rsi14': round(rsi14, 2),
                'rs_spread': round(rs_val * 100.0, 2),
                'reason': f"Supertrend turned green with momentum ignition and RS outperformance."
            }

    return {
        'qualifies': False,
        'reason': 'No qualifying swing setup detected on current bar'
    }
