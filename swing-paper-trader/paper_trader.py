"""
Interactive Paper Trading Assistant for Indian Stock Market Swing Trading.
Tracks multi-day portfolio state, open positions, trailing stops,
statutory delivery fees, and daily candidate generation.
"""

import sys
import os
import argparse
import json
import datetime
from typing import Dict, Any, List, Optional

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

PORTFOLIO_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "portfolio_state.json")


def load_portfolio(filepath: str = PORTFOLIO_FILE, initial_capital: float = 20000.0) -> Dict[str, Any]:
    """Loads existing portfolio state or initializes a new one."""
    if os.path.exists(filepath):
        try:
            with open(filepath, "r") as f:
                return json.load(f)
        except Exception:
            pass

    state = {
        'initial_capital': initial_capital,
        'cash': initial_capital,
        'created_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'last_updated': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'open_positions': [],
        'closed_trades': []
    }
    save_portfolio(state, filepath)
    return state


def save_portfolio(state: Dict[str, Any], filepath: str = PORTFOLIO_FILE):
    """Saves portfolio state to disk."""
    state['last_updated'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(filepath, "w") as f:
        json.dump(state, f, indent=2)


def display_portfolio_status(state: Dict[str, Any]):
    """Prints beautiful status of the paper trading portfolio."""
    cash = state['cash']
    open_pos = state['open_positions']
    closed = state['closed_trades']

    print("\n================== SWING PAPER TRADING PORTFOLIO ==================")
    print(f"Initial Capital   : ₹{state['initial_capital']:,.2f}")
    print(f"Available Cash    : ₹{cash:,.2f}")
    print(f"Open Positions    : {len(open_pos)} / 2")

    tot_open_val = 0.0
    tot_open_cost = 0.0

    if open_pos:
        print("\n--- ACTIVE OPEN POSITIONS ---")
        for p in open_pos:
            t = p['ticker']
            clean = t.replace('.NS', '')
            cost = p['shares'] * p['entry_price']
            # Fetch latest price
            try:
                b = fetch_historical_bars(t, range_str="5d", interval="1d")
                cur_p = b[-1]['close'] if b else p['entry_price']
            except Exception:
                cur_p = p['entry_price']

            cur_val = p['shares'] * cur_p
            tot_open_cost += cost
            tot_open_val += cur_val
            unrealized_pnl = cur_val - cost
            unrealized_pct = (unrealized_pnl / cost) * 100.0

            print(f"• {clean:<11} | Shares: {p['shares']:2d} | Entry: ₹{p['entry_price']:,.2f} | Current: ₹{cur_p:,.2f} | Stop: ₹{p['stop_loss']:,.2f} | T1: ₹{p.get('target1', 0):,.2f}")
            print(f"  Hold: {p.get('hold_days', 0)}d | Cost: ₹{cost:,.2f} | Current Val: ₹{cur_val:,.2f} | Unrealized: ₹{unrealized_pnl:+,.2f} ({unrealized_pct:+.2f}%)")
    else:
        print("\nNo open positions currently active. Capital is 100% in cash.")

    total_portfolio_equity = cash + tot_open_val
    overall_net_pnl = total_portfolio_equity - state['initial_capital']
    overall_roi_pct = (overall_net_pnl / state['initial_capital']) * 100.0

    print("-------------------------------------------------------------------")
    print(f"Total Portfolio Value : ₹{total_portfolio_equity:,.2f}")
    print(f"Net Cumulative P&L    : ₹{overall_net_pnl:+,.2f} ({overall_roi_pct:+.2f}%)")
    print(f"Total Completed Trades: {len(closed)}")
    print("===================================================================\n")


def update_and_evaluate(state: Dict[str, Any], filepath: str = PORTFOLIO_FILE):
    """
    Evaluates current open positions against today's price action and
    checks for exit triggers or new entries.
    """
    open_pos = state['open_positions']
    cash = state['cash']
    closed = state['closed_trades']

    print("\n[Updating Portfolio with Latest Market Bars...]")
    rem_pos = []
    actions_taken = []

    for pos in open_pos:
        t = pos['ticker']
        clean = t.replace('.NS', '')
        try:
            bars = fetch_historical_bars(t, range_str="3mo", interval="1d")
            enriched = enrich_bars(bars)
            today_bar = enriched[-1]
        except Exception as e:
            print(f"Warning: Could not fetch data for {clean}: {e}")
            rem_pos.append(pos)
            continue

        pos['hold_days'] = pos.get('hold_days', 0) + 1
        exit_p, exit_reason = evaluate_swing_exit(pos, today_bar)

        if exit_p is not None:
            # Execute Paper Sell
            cost = pos['shares'] * pos['entry_price']
            val = pos['shares'] * exit_p
            charges_dict = calc_delivery_charges(pos['entry_price'], exit_p, pos['shares'])
            net_pnl = round((val - cost) - charges_dict['total_charges'], 2)
            cash += round(val - charges_dict['total_charges'], 2)

            trade_record = {
                'ticker': t,
                'clean_symbol': clean,
                'strategy': pos.get('strategy', 'SWING'),
                'entry_date': pos['entry_date'],
                'exit_date': today_bar['date'],
                'hold_days': pos['hold_days'],
                'entry_price': pos['entry_price'],
                'exit_price': exit_p,
                'shares': pos['shares'],
                'cost': round(cost, 2),
                'charges': charges_dict['total_charges'],
                'pnl': net_pnl,
                'roi_pct': round((net_pnl / cost) * 100.0, 2),
                'reason': exit_reason
            }
            closed.append(trade_record)
            actions_taken.append(f"EXIT TRIGGERED on {clean}: Sold {pos['shares']} shares @ ₹{exit_p:,.2f} ({exit_reason}) | P&L: ₹{net_pnl:+,.2f}")
        else:
            rem_pos.append(pos)

    state['open_positions'] = rem_pos
    state['cash'] = round(cash, 2)
    state['closed_trades'] = closed
    save_portfolio(state, filepath)

    for act in actions_taken:
        print(f"  -> {act}")

    display_portfolio_status(state)


def main():
    parser = argparse.ArgumentParser(description="NSE Swing Paper Trading Assistant.")
    parser.add_argument("command", choices=["status", "update", "reset"], default="status", nargs="?", help="Action to perform")
    parser.add_argument("--capital", type=float, default=20000.0, help="Initial capital (for reset)")
    args = parser.parse_args()

    if args.command == "reset":
        if os.path.exists(PORTFOLIO_FILE):
            os.remove(PORTFOLIO_FILE)
        state = load_portfolio(PORTFOLIO_FILE, initial_capital=args.capital)
        print(f"Portfolio reset with ₹{args.capital:,.2f} capital.")
        display_portfolio_status(state)
    elif args.command == "update":
        state = load_portfolio(PORTFOLIO_FILE)
        update_and_evaluate(state)
    else:
        state = load_portfolio(PORTFOLIO_FILE)
        display_portfolio_status(state)


if __name__ == "__main__":
    main()
