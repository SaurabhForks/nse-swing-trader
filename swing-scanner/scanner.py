"""
Swing Stock Scanner for Indian Equities.
Scans liquid NSE universe for Minervini Stage 2 Breakouts and Supertrend Momentum Ignition setups.
Incorporates Nifty 50 Market Regime Filter and Relative Strength rankings.
"""

import sys
import os
import argparse
import json
from typing import List, Dict, Any, Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from swing_core.indicators import enrich_bars
from swing_core.data_feed import fetch_historical_bars
from swing_core.universe import BENCHMARK_INDEX, ACTIVE_UNIVERSE, SECTOR_MAP
from swing_regime.regime import evaluate_market_regime
from swing_entry.entry import evaluate_swing_entry
from swing_budget.budget import calc_delivery_charges, calculate_position_allocation


def scan_swing_candidates(
    tickers: Optional[List[str]] = None,
    capital: float = 20000.0,
    max_positions: int = 2
) -> Dict[str, Any]:
    """
    Scans the NSE universe for qualified swing setups.
    """
    if tickers is None:
        tickers = ACTIVE_UNIVERSE

    # 1. Market Regime Check
    nifty_bars = fetch_historical_bars(BENCHMARK_INDEX, range_str="2y", interval="1d")
    regime = evaluate_market_regime(nifty_bars)

    if not regime['allow_new_entries']:
        return {
            'market_regime': regime,
            'candidates_found': 0,
            'candidates': [],
            'message': f"Scanning halted: Nifty 50 is in {regime['regime']} regime. Cash preservation active."
        }

    # 2. Enrich Benchmark
    enriched_nifty = enrich_bars(nifty_bars)

    candidates = []
    for ticker in tickers:
        try:
            bars = fetch_historical_bars(ticker, range_str="2y", interval="1d")
            if len(bars) < 60:
                continue
            enriched = enrich_bars(bars, benchmark_bars=enriched_nifty)
            entry_res = evaluate_swing_entry(enriched)

            if entry_res['qualifies']:
                price = entry_res['entry_price']
                stop = entry_res['stop_loss']
                t1 = entry_res['target1']
                sector = SECTOR_MAP.get(ticker, "Diversified")

                # Sizing
                slot_cap = capital / max_positions
                shares = int(slot_cap // price)
                charges_t1 = calc_delivery_charges(price, t1, max(1, shares))

                candidates.append({
                    'ticker': ticker,
                    'clean_symbol': ticker.replace('.NS', ''),
                    'sector': sector,
                    'pattern': entry_res['pattern'],
                    'score': entry_res['score'],
                    'entry_price': price,
                    'stop_loss': stop,
                    'target1': t1,
                    'target2': entry_res['target2'],
                    'rvol': entry_res['rvol'],
                    'rsi14': entry_res['rsi14'],
                    'rs_spread': entry_res['rs_spread'],
                    'recommended_shares': shares,
                    'position_value': round(shares * price, 2),
                    'est_profit_at_t1': charges_t1['net_pnl'],
                    'est_roi_at_t1': charges_t1['roi_pct'],
                    'reason': entry_res['reason']
                })
        except Exception:
            continue

    # Sort by score descending
    candidates.sort(key=lambda c: c['score'], reverse=True)

    return {
        'market_regime': regime,
        'candidates_found': len(candidates),
        'candidates': candidates,
        'message': f"Scan complete. Found {len(candidates)} high-conviction swing candidate(s)."
    }


def main():
    parser = argparse.ArgumentParser(description="Scan NSE stocks for Swing Trading setups.")
    parser.add_argument("--capital", type=float, default=20000.0, help="Total trading capital in INR")
    parser.add_argument("--json", action="store_true", help="Output raw JSON format")
    args = parser.parse_args()

    res = scan_swing_candidates(capital=args.capital)

    if args.json:
        print(json.dumps(res, indent=2))
        return

    reg = res['market_regime']
    print("\n================== NSE SWING TRADING SCANNER ==================")
    print(f"Market Regime   : {reg['regime']} (Nifty: ₹{reg['current_price']:,.2f} | 50 EMA: ₹{reg['ema50']:,.2f})")
    print(f"Status          : {res['message']}")
    print("----------------------------------------------------------------")

    if res['candidates_found'] == 0:
        print("No candidates qualify under strict criteria. Sitting patiently in cash.")
    else:
        for idx, c in enumerate(res['candidates'], 1):
            print(f"\n#{idx} {c['clean_symbol']} ({c['sector']}) | Setup: {c['pattern']} | Score: {c['score']}")
            print(f"    Entry Price    : ₹{c['entry_price']:,.2f}")
            print(f"    Stop Loss      : ₹{c['stop_loss']:,.2f} (-{((c['entry_price']-c['stop_loss'])/c['entry_price'])*100:.1f}%)")
            print(f"    Target 1 (12%) : ₹{c['target1']:,.2f} (+12.0%) | Net Profit: ₹{c['est_profit_at_t1']:+,.2f} ({c['est_roi_at_t1']:+.1f}%)")
            print(f"    Volume / RS    : RVol {c['rvol']}x | RS Spread: {c['rs_spread']:+.1f}% vs Nifty")
            print(f"    Allocation     : {c['recommended_shares']} shares (₹{c['position_value']:,.2f})")
            print(f"    Thesis         : {c['reason']}")

    print("================================================================\n")


if __name__ == "__main__":
    main()
