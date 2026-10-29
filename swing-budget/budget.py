"""
Indian Stock Market Delivery Statutory Charges & Budget Calculator.
Calculates exact fees, taxes, DP charges, and net P&L down to the paisa.
Zero external dependencies.
"""

from typing import Dict, Any


def calc_delivery_charges(
    buy_price: float,
    sell_price: float,
    shares: int,
    brokerage_per_trade: float = 0.0
) -> Dict[str, Any]:
    """
    Calculates exact NSE delivery trade statutory charges.
    
    Rates:
    - STT (Securities Transaction Tax): 0.1% on buy value + 0.1% on sell value
    - DP Charges (Depository Participant): Flat ₹15.34 (₹13 + GST) per company per day on selling
    - Stamp Duty: 0.015% on buy value
    - Exchange Turnover Charge: 0.00297% on both buy and sell
    - SEBI Turnover Charge: 0.0001% on both buy and sell
    - GST: 18% on (Brokerage + Exchange turnover charge + SEBI charge)
    """
    buy_value = round(buy_price * shares, 2)
    sell_value = round(sell_price * shares, 2)
    gross_pnl = round(sell_value - buy_value, 2)

    # 1. STT
    stt_buy = round(buy_value * 0.001, 2)
    stt_sell = round(sell_value * 0.001, 2)
    stt_total = stt_buy + stt_sell

    # 2. Stamp Duty (Buy only)
    stamp_duty = round(buy_value * 0.00015, 2)

    # 3. DP Charges (Sell only)
    dp_charges = 15.34 if shares > 0 else 0.0

    # 4. Exchange & SEBI Turnover Charges
    nse_charges = round((buy_value + sell_value) * 0.0000297, 2)
    sebi_charges = round((buy_value + sell_value) * 0.000001, 2)

    # 5. Brokerage
    brokerage = round(brokerage_per_trade * 2, 2)

    # 6. GST (18% on Brokerage + NSE + SEBI)
    gst = round((brokerage + nse_charges + sebi_charges) * 0.18, 2)

    # Total charges
    total_charges = round(stt_total + stamp_duty + dp_charges + nse_charges + sebi_charges + brokerage + gst, 2)
    net_pnl = round(gross_pnl - total_charges, 2)
    roi_pct = round((net_pnl / buy_value) * 100.0, 2) if buy_value > 0 else 0.0

    # Breakeven sell price (price required to cover all charges)
    # Approx: buy_price + (charges / shares)
    breakeven_sell_price = round(buy_price * 1.0025 + (15.34 / max(1, shares)), 2)

    return {
        'buy_value': buy_value,
        'sell_value': sell_value,
        'gross_pnl': gross_pnl,
        'stt_total': stt_total,
        'stamp_duty': stamp_duty,
        'dp_charges': dp_charges,
        'nse_charges': nse_charges,
        'sebi_charges': sebi_charges,
        'brokerage': brokerage,
        'gst': gst,
        'total_charges': total_charges,
        'net_pnl': net_pnl,
        'roi_pct': roi_pct,
        'breakeven_sell_price': breakeven_sell_price
    }


def calculate_position_allocation(
    total_capital: float,
    max_concurrent_positions: int = 2,
    stock_price: float = 1000.0,
    regime_multiplier: float = 1.0
) -> Dict[str, Any]:
    """
    Calculates position allocation and share count for a given stock price.
    """
    effective_capital = total_capital * regime_multiplier
    slot_capital = effective_capital / max(1, max_concurrent_positions)
    shares = int(slot_capital // stock_price) if stock_price > 0 else 0
    trade_value = round(shares * stock_price, 2)
    buy_charges = round(trade_value * (0.001 + 0.00015 + 0.0000297 + 0.000001), 2)

    return {
        'total_capital': total_capital,
        'effective_capital': effective_capital,
        'max_concurrent_positions': max_concurrent_positions,
        'slot_capital': round(slot_capital, 2),
        'stock_price': stock_price,
        'shares': shares,
        'allocated_value': trade_value,
        'estimated_buy_charges': buy_charges,
        'cash_remaining': round(slot_capital - trade_value - buy_charges, 2)
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="NSE Delivery Charges & Position Budget Calculator.")
    parser.add_argument("--buy", type=float, default=1500.0, help="Buy price in INR")
    parser.add_argument("--sell", type=float, default=1680.0, help="Sell price in INR")
    parser.add_argument("--shares", type=int, default=6, help="Number of shares")
    parser.add_argument("--capital", type=float, default=20000.0, help="Total available budget in INR")
    args = parser.parse_args()

    res = calc_delivery_charges(args.buy, args.sell, args.shares)
    pos = calculate_position_allocation(args.capital, stock_price=args.buy)

    print("\n================== NSE DELIVERY CHARGES CALCULATOR ==================")
    print(f"Buy Price         : ₹{args.buy:,.2f} x {args.shares} shares = ₹{res['buy_value']:,.2f}")
    print(f"Sell Price        : ₹{args.sell:,.2f} x {args.shares} shares = ₹{res['sell_value']:,.2f}")
    print(f"Gross P&L         : ₹{res['gross_pnl']:+,.2f}")
    print("---------------------------------------------------------------------")
    print(f"STT (0.1% B + S)  : ₹{res['stt_total']:,.2f}")
    print(f"DP Charges (CDSL) : ₹{res['dp_charges']:,.2f}")
    print(f"Stamp Duty (0.015): ₹{res['stamp_duty']:,.2f}")
    print(f"NSE Turnover Chg  : ₹{res['nse_charges']:,.2f}")
    print(f"SEBI Turnover Chg : ₹{res['sebi_charges']:,.2f}")
    print(f"GST (18%)         : ₹{res['gst']:,.2f}")
    print(f"TOTAL CHARGES     : ₹{res['total_charges']:,.2f} ({(res['total_charges']/res['buy_value'])*100:.2f}% of buy value)")
    print("---------------------------------------------------------------------")
    print(f"NET P&L           : ₹{res['net_pnl']:+,.2f} ({res['roi_pct']:+.2f}%)")
    print(f"Breakeven Price   : ₹{res['breakeven_sell_price']:,.2f} (+{((res['breakeven_sell_price']-args.buy)/args.buy)*100:.2f}%)")
    print("=====================================================================\n")


if __name__ == "__main__":
    main()
