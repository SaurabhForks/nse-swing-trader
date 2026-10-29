"""
Historical Backtesting Engine for Indian Stock Market Swing Trading.
Simulates day-by-day portfolio operations, tracking cash, positions,
statutory delivery fees, and performance metrics across diverse market regimes.
Zero external dependencies.
"""

import sys
import os
import argparse
import json
import math
from typing import List, Dict, Any, Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from swing_core.indicators import enrich_bars
from swing_core.data_feed import fetch_historical_bars
from swing_core.universe import BENCHMARK_INDEX, ACTIVE_UNIVERSE, SECTOR_MAP
from swing_regime.regime import evaluate_market_regime
from swing_entry.entry import evaluate_swing_entry
from swing_exit.exit import evaluate_swing_exit
from swing_budget.budget import calc_delivery_charges
from swing_risk.risk import calculate_risk_sized_position


def run_swing_backtest(
    capital: float = 20000.0,
    max_positions: int = 2,
    profit_target_pct: float = 0.12,
    max_risk_pct: float = 0.045,
    universe: Optional[List[str]] = None,
    cache_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Runs historical simulation over cached 2-year daily NSE dataset.
    """
    if universe is None:
        universe = ACTIVE_UNIVERSE

    # 1. Fetch & enrich Nifty 50
    nifty_bars = fetch_historical_bars(BENCHMARK_INDEX, range_str="2y", interval="1d", cache_dir=cache_dir)
    enriched_nifty = enrich_bars(nifty_bars)
    nifty_by_date = {b['date']: b for b in enriched_nifty}

    # 2. Fetch & enrich all stock series
    stocks_data = {}
    for ticker in universe:
        try:
            bars = fetch_historical_bars(ticker, range_str="2y", interval="1d", cache_dir=cache_dir)
            if len(bars) >= 60:
                enriched = enrich_bars(bars, benchmark_bars=enriched_nifty)
                stocks_data[ticker] = enriched
        except Exception:
            continue

    all_dates = sorted(list(nifty_by_date.keys()))
    # Warmup period: need ~200 trading days for 200 EMA
    test_dates = all_dates[200:]
    if len(test_dates) == 0:
        test_dates = all_dates[60:]

    cur_cash = capital
    open_positions: List[Dict[str, Any]] = []
    closed_trades: List[Dict[str, Any]] = []
    equity_curve: List[Dict[str, Any]] = []

    for d in test_dates:
        nb = nifty_by_date.get(d)
        if not nb:
            continue

        nifty_close = nb['close']
        nifty_ema50 = nb.get('ema50')
        is_bull_regime = (nifty_ema50 is not None and nifty_close >= nifty_ema50)

        # ----------------- 1. EXITS -----------------
        rem_positions = []
        for pos in open_positions:
            t = pos['ticker']
            sb = next((b for b in stocks_data[t] if b['date'] == d), None)
            if not sb:
                rem_positions.append(pos)
                continue

            pos['hold_days'] += 1
            exit_price, exit_reason = evaluate_swing_exit(pos, sb)

            if exit_price is not None:
                cost = pos['shares'] * pos['entry_price']
                val = pos['shares'] * exit_price
                charges_dict = calc_delivery_charges(pos['entry_price'], exit_price, pos['shares'])
                total_charges = charges_dict['total_charges']
                net_pnl = round((val - cost) - total_charges, 2)
                cur_cash += (val - total_charges)

                closed_trades.append({
                    'ticker': t,
                    'clean_symbol': t.replace('.NS', ''),
                    'sector': pos.get('sector', 'General'),
                    'strategy': pos['strategy'],
                    'entry_date': pos['entry_date'],
                    'exit_date': d,
                    'hold_days': pos['hold_days'],
                    'entry_price': pos['entry_price'],
                    'exit_price': exit_price,
                    'shares': pos['shares'],
                    'cost': round(cost, 2),
                    'val': round(val, 2),
                    'charges': total_charges,
                    'pnl': net_pnl,
                    'roi_pct': round((net_pnl / cost) * 100.0, 2),
                    'reason': exit_reason
                })
            else:
                rem_positions.append(pos)
        open_positions = rem_positions

        # ----------------- 2. ENTRIES -----------------
        # Gated by Nifty 50 market regime
        if is_bull_regime and len(open_positions) < max_positions:
            candidates = []
            for t, s_bars in stocks_data.items():
                if any(p['ticker'] == t for p in open_positions):
                    continue

                idx = next((i for i, b in enumerate(s_bars) if b['date'] == d), None)
                if idx is None or idx < 50:
                    continue

                # Pass slice up to today's bar
                sub_bars = s_bars[: idx + 1]
                entry_eval = evaluate_swing_entry(sub_bars, max_risk_pct=max_risk_pct)

                if entry_eval['qualifies']:
                    candidates.append({
                        'ticker': t,
                        'strategy': entry_eval['pattern'],
                        'score': entry_eval['score'],
                        'entry_price': entry_eval['entry_price'],
                        'stop_loss': entry_eval['stop_loss'],
                        'target1': entry_eval['target1'],
                        'sector': SECTOR_MAP.get(t, "General")
                    })

            # Sort descending by setup score
            candidates.sort(key=lambda c: c['score'], reverse=True)

            slots_available = max_positions - len(open_positions)
            for cand in candidates[:slots_available]:
                t = cand['ticker']
                ep = cand['entry_price']
                sl = cand['stop_loss']
                sec = cand['sector']

                # Compute current total equity
                open_pos_val = sum(p['shares'] * (next((b['close'] for b in stocks_data[p['ticker']] if b['date'] == d), p['entry_price'])) for p in open_positions)
                tot_eq = cur_cash + open_pos_val

                risk_res = calculate_risk_sized_position(
                    total_equity=tot_eq,
                    stock_price=ep,
                    stop_loss_price=sl,
                    max_positions=max_positions,
                    existing_positions=open_positions,
                    stock_sector=sec
                )

                if risk_res['allowed']:
                    shares = risk_res['shares']
                    cost = shares * ep
                    # Buy side charges
                    stt_stamp = round(cost * (0.001 + 0.00015 + 0.0000297 + 0.000001), 2)
                    cur_cash -= (cost + stt_stamp)

                    open_positions.append({
                        'ticker': t,
                        'sector': sec,
                        'strategy': cand['strategy'],
                        'entry_date': d,
                        'entry_price': ep,
                        'shares': shares,
                        'stop_loss': sl,
                        'target1': cand['target1'],
                        'peak_price': ep,
                        'hold_days': 0
                    })

        # Calculate day-end mark-to-market equity
        cur_open_mtm = 0.0
        for pos in open_positions:
            t = pos['ticker']
            sb = next((b for b in stocks_data[t] if b['date'] == d), None)
            px = sb['close'] if sb else pos['entry_price']
            cur_open_mtm += pos['shares'] * px

        total_day_equity = round(cur_cash + cur_open_mtm, 2)
        equity_curve.append({
            'date': d,
            'cash': round(cur_cash, 2),
            'open_positions': len(open_positions),
            'equity': total_day_equity
        })

    # Performance Analytics
    final_equity = equity_curve[-1]['equity'] if equity_curve else capital
    net_pnl = round(final_equity - capital, 2)
    roi_pct = round((net_pnl / capital) * 100.0, 2)

    wins = [t for t in closed_trades if t['pnl'] > 0]
    losses = [t for t in closed_trades if t['pnl'] <= 0]
    win_rate = round(len(wins) / len(closed_trades) * 100.0, 2) if closed_trades else 0.0

    tot_wins = round(sum(t['pnl'] for t in wins), 2)
    tot_losses = round(sum(abs(t['pnl']) for t in losses), 2)
    profit_factor = round(tot_wins / tot_losses, 2) if tot_losses > 0 else 999.0

    avg_hold_days = round(sum(t['hold_days'] for t in closed_trades) / len(closed_trades), 1) if closed_trades else 0.0

    # Max Drawdown
    peak = capital
    max_dd = 0.0
    for pt in equity_curve:
        eq = pt['equity']
        if eq > peak:
            peak = eq
        dd = (peak - eq) / peak * 100.0
        if dd > max_dd:
            max_dd = dd
    max_dd = round(max_dd, 2)

    # Monthly breakdown
    monthly_pnl = {}
    for t in closed_trades:
        m = t['exit_date'][:7]
        monthly_pnl[m] = round(monthly_pnl.get(m, 0.0) + t['pnl'], 2)

    return {
        'initial_capital': capital,
        'final_equity': final_equity,
        'net_pnl': net_pnl,
        'roi_pct': roi_pct,
        'total_trades': len(closed_trades),
        'winning_trades': len(wins),
        'losing_trades': len(losses),
        'win_rate_pct': win_rate,
        'profit_factor': profit_factor,
        'gross_profit': tot_wins,
        'gross_loss': tot_losses,
        'max_drawdown_pct': max_dd,
        'avg_hold_days': avg_hold_days,
        'monthly_pnl': monthly_pnl,
        'closed_trades': closed_trades,
        'equity_curve': equity_curve
    }


def main():
    parser = argparse.ArgumentParser(description="Run NSE Swing Trading Historical Backtest.")
    parser.add_argument("--capital", type=float, default=20000.0, help="Initial capital in INR")
    parser.add_argument("--positions", type=int, default=2, help="Max concurrent positions")
    parser.add_argument("--target", type=float, default=0.12, help="Profit target pct (default: 0.12 = 12%)")
    parser.add_argument("--risk", type=float, default=0.045, help="Max stop loss risk pct (default: 0.045 = 4.5%)")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    args = parser.parse_args()

    res = run_swing_backtest(
        capital=args.capital,
        max_positions=args.positions,
        profit_target_pct=args.target,
        max_risk_pct=args.risk
    )

    if args.json:
        # Exclude massive curve for compact stdout
        summary = {k: v for k, v in res.items() if k != 'equity_curve'}
        print(json.dumps(summary, indent=2))
        return

    print("\n================== HISTORICAL SWING BACKTEST RESULTS ==================")
    print(f"Initial Capital   : ₹{res['initial_capital']:,.2f}")
    print(f"Final Equity      : ₹{res['final_equity']:,.2f}")
    print(f"Net Profit (Loss) : ₹{res['net_pnl']:+,.2f} ({res['roi_pct']:+.2f}%)")
    print(f"Total Trades      : {res['total_trades']} (Wins: {res['winning_trades']}, Losses: {res['losing_trades']})")
    print(f"Win Rate          : {res['win_rate_pct']:.1f}%")
    print(f"Profit Factor     : {res['profit_factor']:.2f}")
    print(f"Max Drawdown      : {res['max_drawdown_pct']:.2f}%")
    print(f"Avg Holding Time  : {res['avg_hold_days']} trading days")
    print(f"Gross Profit      : +₹{res['gross_profit']:,.2f}")
    print(f"Gross Loss        : -₹{res['gross_loss']:,.2f}")
    print("------------------------------------------------------------------------")
    print("Monthly Performance Breakdown:")
    for m, p in sorted(res['monthly_pnl'].items()):
        print(f"  {m} : ₹{p:+9.2f}")
    print("------------------------------------------------------------------------")
    print("Sample Trade Log:")
    for t in res['closed_trades']:
        print(f"  {t['entry_date']} -> {t['exit_date']} | {t['clean_symbol']:<11} | Hold: {t['hold_days']:2d}d | Cost: ₹{t['cost']:7.0f} | P&L: ₹{t['pnl']:+7.2f} ({t['roi_pct']:+5.1f}%) | {t['reason']}")
    print("========================================================================\n")


if __name__ == "__main__":
    main()
