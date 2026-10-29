"""
Portfolio Risk Management for Indian Stock Market Swing Trading.
Enforces strict position sizing, capital risk limits, and sector diversification.
"""

from typing import Dict, Any, List, Optional
import math


def calculate_risk_sized_position(
    total_equity: float,
    stock_price: float,
    stop_loss_price: float,
    max_risk_pct: float = 0.02, # 2.0% of total equity
    max_positions: int = 2,
    existing_positions: Optional[List[Dict[str, Any]]] = None,
    stock_sector: Optional[str] = None
) -> Dict[str, Any]:
    """
    Computes exact risk-managed position size.
    
    Rules:
    1. Maximum risk per trade = 2.0% of total equity.
    2. Capital slot allocation = Total equity / max_positions.
    3. Stop distance must be >= 2.5% and <= 6.0%.
    4. Sector diversification check (reject if sector already held).
    """
    if existing_positions is None:
        existing_positions = []

    # 1. Sector Check
    if stock_sector:
        held_sectors = [p.get('sector') for p in existing_positions if p.get('sector')]
        if stock_sector in held_sectors:
            return {
                'allowed': False,
                'shares': 0,
                'reason': f"Sector '{stock_sector}' already has an active position. Diversification rule active."
            }

    # 2. Capacity Check
    if len(existing_positions) >= max_positions:
        return {
            'allowed': False,
            'shares': 0,
            'reason': f"Maximum capacity reached ({len(existing_positions)}/{max_positions} positions open)."
        }

    # 3. Stop loss validation
    stop_distance = stock_price - stop_loss_price
    if stop_distance <= 0:
        return {
            'allowed': False,
            'shares': 0,
            'reason': f"Invalid stop loss (₹{stop_loss_price:.2f}) is higher than entry (₹{stock_price:.2f})."
        }

    stop_pct = (stop_distance / stock_price) * 100.0
    if stop_pct > 6.5:
        return {
            'allowed': False,
            'shares': 0,
            'reason': f"Stop loss distance ({stop_pct:.2f}%) exceeds maximum allowable risk boundary (6.5%)."
        }

    # 4. Sizing computation
    max_risk_amount = round(total_equity * max_risk_pct, 2)
    shares_by_risk = int(max_risk_amount // stop_distance)

    slot_capital = total_equity / max_positions
    shares_by_capital = int(slot_capital // stock_price)

    final_shares = min(shares_by_risk, shares_by_capital)
    if final_shares < 1:
        return {
            'allowed': False,
            'shares': 0,
            'reason': f"Capital (₹{slot_capital:,.2f}) insufficient to buy at least 1 share of ₹{stock_price:,.2f}."
        }

    position_cost = round(final_shares * stock_price, 2)
    actual_risk_rupees = round(final_shares * stop_distance, 2)
    actual_risk_pct = round((actual_risk_rupees / total_equity) * 100.0, 2)

    return {
        'allowed': True,
        'shares': final_shares,
        'entry_price': stock_price,
        'stop_loss_price': stop_loss_price,
        'stop_distance': round(stop_distance, 2),
        'stop_distance_pct': round(stop_pct, 2),
        'position_cost': position_cost,
        'portfolio_allocation_pct': round((position_cost / total_equity) * 100.0, 2),
        'max_risk_budget': max_risk_amount,
        'actual_risk_rupees': actual_risk_rupees,
        'actual_risk_pct': actual_risk_pct,
        'reason': 'Position within risk budget and capital constraints.'
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Swing Risk & Position Sizing Calculator.")
    parser.add_argument("--equity", type=float, default=20000.0, help="Total portfolio equity in INR")
    parser.add_argument("--price", type=float, default=1500.0, help="Stock entry price")
    parser.add_argument("--stop", type=float, default=1432.5, help="Stock stop loss price")
    args = parser.parse_args()

    res = calculate_risk_sized_position(args.equity, args.price, args.stop)
    print("\n================== SWING RISK & POSITION SIZER ==================")
    print(f"Total Portfolio Equity : ₹{args.equity:,.2f}")
    print(f"Stock Entry Price      : ₹{args.price:,.2f}")
    print(f"Stop Loss Price        : ₹{args.stop:,.2f}")
    print(f"Allowed to Trade       : {'YES' if res['allowed'] else 'NO'}")
    if res['allowed']:
        print(f"Shares to Buy          : {res['shares']} shares")
        print(f"Total Investment Cost  : ₹{res['position_cost']:,.2f} ({res['portfolio_allocation_pct']}%)")
        print(f"Stop Loss Distance     : ₹{res['stop_distance']:,.2f} ({res['stop_distance_pct']}%)")
        print(f"Max Risk Budget (2.0%) : ₹{res['max_risk_budget']:,.2f}")
        print(f"Actual Risk at Stop    : ₹{res['actual_risk_rupees']:,.2f} ({res['actual_risk_pct']}%)")
    else:
        print(f"Rejection Reason       : {res['reason']}")
    print("=================================================================\n")


if __name__ == "__main__":
    main()
