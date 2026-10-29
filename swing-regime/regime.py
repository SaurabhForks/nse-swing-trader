"""
Market Regime Filter for Indian Equities.
Uses Nifty 50 (^NSEI) daily price action and moving averages to determine
whether the broader market environment is favorable for swing trading.

Trading Philosophy:
- Mark Minervini: ~75-80% of stocks follow the general market trend. Never fight the market tide.
- Jesse Livermore: "There is a time to go long, a time to go short, and a time to go fishing."
- When Nifty is in a correction or bear trend (Close < 50 EMA), sitting 100% in cash preserves capital.
"""

import sys
import os
import argparse
from typing import Dict, Any, List, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from swing_core.indicators import enrich_bars
from swing_core.data_feed import fetch_historical_bars
from swing_core.universe import BENCHMARK_INDEX


def evaluate_market_regime(nifty_bars: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """
    Evaluates current Nifty 50 market regime.
    Returns:
        dict: {
            'regime': 'BULL' | 'NEUTRAL' | 'BEAR',
            'allow_new_entries': bool,
            'allocation_multiplier': float,
            'current_price': float,
            'ema50': float,
            'ema200': float,
            'distance_ema50_pct': float,
            'trend_50_vs_200': str,
            'reason': str
        }
    """
    if nifty_bars is None:
        nifty_bars = fetch_historical_bars(BENCHMARK_INDEX, range_str="2y", interval="1d")

    enriched = enrich_bars(nifty_bars)
    if len(enriched) < 50:
        return {
            'regime': 'NEUTRAL',
            'allow_new_entries': False,
            'allocation_multiplier': 0.0,
            'reason': 'Insufficient historical bars to compute market regime'
        }

    latest = enriched[-1]
    prev_20 = enriched[-20] if len(enriched) >= 20 else enriched[0]

    close = float(latest['close'])
    ema50 = latest.get('ema50')
    ema200 = latest.get('ema200')

    if ema50 is None or ema200 is None:
        return {
            'regime': 'NEUTRAL',
            'allow_new_entries': False,
            'allocation_multiplier': 0.0,
            'reason': 'Moving averages not yet established'
        }

    dist_50_pct = ((close - ema50) / ema50) * 100.0
    ema50_slope = (ema50 - prev_20.get('ema50', ema50)) / ema50

    if close >= ema50 and ema50 >= ema200:
        regime = "BULL"
        allow_entries = True
        mult = 1.0
        reason = f"Nifty (₹{close:,.2f}) is above rising 50 EMA (₹{ema50:,.2f}) and 50 EMA is above 200 EMA."
    elif close >= ema50:
        regime = "NEUTRAL"
        allow_entries = True
        mult = 0.5
        reason = f"Nifty (₹{close:,.2f}) is above 50 EMA but 50 EMA is below 200 EMA (Cautious recovery phase)."
    elif dist_50_pct >= -1.5 and ema50_slope > 0:
        regime = "NEUTRAL"
        allow_entries = True
        mult = 0.5
        reason = f"Nifty is in shallow pullback within 1.5% of rising 50 EMA."
    else:
        regime = "BEAR"
        allow_entries = False
        mult = 0.0
        reason = f"Nifty (₹{close:,.2f}) is below 50 EMA (₹{ema50:,.2f}, {dist_50_pct:.1f}%). Cash is king."

    return {
        'regime': regime,
        'allow_new_entries': allow_entries,
        'allocation_multiplier': mult,
        'current_price': close,
        'ema50': round(ema50, 2),
        'ema200': round(ema200, 2),
        'distance_ema50_pct': round(dist_50_pct, 2),
        'trend_50_vs_200': 'BULLISH' if ema50 >= ema200 else 'BEARISH',
        'date': latest.get('date'),
        'reason': reason
    }


def main():
    parser = argparse.ArgumentParser(description="Evaluate Nifty 50 Market Regime for Swing Trading.")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    args = parser.parse_args()

    res = evaluate_market_regime()
    if args.json:
        import json
        print(json.dumps(res, indent=2))
    else:
        print("\n================== NIFTY 50 MARKET REGIME ==================")
        print(f"Date            : {res.get('date')}")
        print(f"Current Nifty   : ₹{res.get('current_price', 0):,.2f}")
        print(f"50-Day EMA      : ₹{res.get('ema50', 0):,.2f}")
        print(f"200-Day EMA     : ₹{res.get('ema200', 0):,.2f}")
        print(f"Distance to 50D : {res.get('distance_ema50_pct', 0):+.2f}%")
        print(f"Regime Status   : {res.get('regime')} ({'ALLOWED' if res.get('allow_new_entries') else 'BLOCKED'})")
        print(f"Capital Sizing  : {res.get('allocation_multiplier', 0)*100:.0f}%")
        print(f"Summary         : {res.get('reason')}")
        print("============================================================\n")


if __name__ == "__main__":
    main()
