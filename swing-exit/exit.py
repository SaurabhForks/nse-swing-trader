"""
Swing Trade Exit Manager for Indian Equities.
Applies disciplined trade management:
1. Hard Stop Loss protection (max 4.5% risk)
2. Profit Target 1 (+12%)
3. Dynamic Trailing Stop along rising 20 EMA once in profit (>= +5%)
4. 30-Day Time Stop to recycle idle capital.
"""

from typing import Dict, Any, Tuple, Optional


def evaluate_swing_exit(
    position: Dict[str, Any],
    current_bar: Dict[str, Any]
) -> Tuple[Optional[float], Optional[str]]:
    """
    Evaluates whether an active swing position should be closed on the current bar.
    
    Args:
        position: Active position dict containing:
            - ticker: str
            - entry_price: float
            - stop_loss: float
            - target1: float
            - peak_price: float
            - hold_days: int
        current_bar: Today's OHLCV bar dict containing 'open', 'high', 'low', 'close', 'ema20'
        
    Returns:
        (exit_price, exit_reason) if exit triggered, else (None, None).
    """
    open_p = float(current_bar['open'])
    high_p = float(current_bar['high'])
    low_p = float(current_bar['low'])
    close_p = float(current_bar['close'])
    ema20 = current_bar.get('ema20')

    entry_price = position['entry_price']
    stop_loss = position['stop_loss']
    target1 = position.get('target1', entry_price * 1.12)
    peak_price = max(position.get('peak_price', entry_price), high_p)
    position['peak_price'] = peak_price
    hold_days = position.get('hold_days', 0)

    # 1. Hard Stop Loss Check
    if low_p <= stop_loss:
        exit_price = min(open_p, stop_loss)
        return round(exit_price, 2), "STOP_LOSS"

    # 2. Profit Target Check (+12%)
    if high_p >= target1:
        return round(target1, 2), "TARGET_12PCT"

    # 3. Dynamic 20 EMA Trailing Stop
    # Once peak gain reaches at least +5%, exit if daily close breaks below 20 EMA
    gain_pct = (peak_price - entry_price) / entry_price
    if gain_pct >= 0.05 and ema20 is not None:
        if close_p < ema20:
            return round(close_p, 2), "TRAIL_20EMA"

    # 4. Time Stop (Max 30 trading days)
    if hold_days >= 30:
        return round(close_p, 2), "TIME_STOP_30D"

    return None, None
