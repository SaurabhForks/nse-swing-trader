"""
Technical Indicators Module for Indian Stock Market Swing Trading.
Standard library only - Zero external dependencies.
"""

from typing import List, Dict, Any, Optional


def calc_sma(values: List[float], period: int) -> List[Optional[float]]:
    """Calculates Simple Moving Average (SMA)."""
    n = len(values)
    res: List[Optional[float]] = [None] * n
    if n < period or period <= 0:
        return res
    running_sum = sum(values[:period])
    res[period - 1] = running_sum / period
    for i in range(period, n):
        running_sum += values[i] - values[i - period]
        res[i] = running_sum / period
    return res


def calc_ema(values: List[float], period: int) -> List[Optional[float]]:
    """Calculates Exponential Moving Average (EMA)."""
    n = len(values)
    res: List[Optional[float]] = [None] * n
    if n < period or period <= 0:
        return res
    k = 2.0 / (period + 1.0)
    sma_init = sum(values[:period]) / period
    res[period - 1] = sma_init
    for i in range(period, n):
        res[i] = values[i] * k + res[i - 1] * (1.0 - k)
    return res


def calc_atr(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> List[Optional[float]]:
    """Calculates Average True Range (ATR) with Wilder's Smoothing."""
    n = len(closes)
    tr = [0.0] * n
    for i in range(n):
        if i == 0:
            tr[i] = highs[i] - lows[i]
        else:
            tr[i] = max(
                highs[i] - lows[i],
                abs(highs[i] - closes[i - 1]),
                abs(lows[i] - closes[i - 1])
            )
    atr: List[Optional[float]] = [None] * n
    if n < period or period <= 0:
        return atr
    atr[period - 1] = sum(tr[:period]) / period
    for i in range(period, n):
        atr[i] = (atr[i - 1] * (period - 1) + tr[i]) / period
    return atr


def calc_rsi(closes: List[float], period: int = 14) -> List[Optional[float]]:
    """Calculates Relative Strength Index (RSI) using Wilder's smoothing."""
    n = len(closes)
    rsi: List[Optional[float]] = [None] * n
    if n <= period or period <= 0:
        return rsi

    gains = [0.0] * n
    losses = [0.0] * n
    for i in range(1, n):
        diff = closes[i] - closes[i - 1]
        if diff > 0:
            gains[i] = diff
        else:
            losses[i] = -diff

    avg_gain = sum(gains[1 : period + 1]) / period
    avg_loss = sum(losses[1 : period + 1]) / period

    if avg_loss == 0.0:
        rsi[period] = 100.0
    else:
        rs = avg_gain / avg_loss
        rsi[period] = 100.0 - (100.0 / (1.0 + rs))

    for i in range(period + 1, n):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        if avg_loss == 0.0:
            rsi[i] = 100.0
        else:
            rs = avg_gain / avg_loss
            rsi[i] = 100.0 - (100.0 / (1.0 + rs))

    return rsi


def calc_supertrend(
    highs: List[float], lows: List[float], closes: List[float],
    atr_period: int = 10, multiplier: float = 3.0
) -> (List[Optional[float]], List[Optional[int]]):
    """
    Calculates Supertrend indicator.
    Returns (supertrend_levels, directions) where direction is +1 (Bullish/Green) or -1 (Bearish/Red).
    """
    n = len(closes)
    st: List[Optional[float]] = [None] * n
    st_dir: List[Optional[int]] = [None] * n
    atr = calc_atr(highs, lows, closes, period=atr_period)

    for i in range(atr_period, n):
        cur_atr = atr[i]
        if cur_atr is None:
            continue
        hl2 = (highs[i] + lows[i]) / 2.0
        basic_upper = hl2 + (multiplier * cur_atr)
        basic_lower = hl2 - (multiplier * cur_atr)

        if i == atr_period:
            st[i] = basic_lower
            st_dir[i] = 1
            continue

        prev_dir = st_dir[i - 1]
        prev_st = st[i - 1]

        prev_upper = prev_st if prev_dir == -1 else basic_upper
        prev_lower = prev_st if prev_dir == 1 else basic_lower

        final_upper = basic_upper if (basic_upper < prev_upper or closes[i - 1] > prev_upper) else prev_upper
        final_lower = basic_lower if (basic_lower > prev_lower or closes[i - 1] < prev_lower) else prev_lower

        if prev_dir == 1:
            if closes[i] < final_lower:
                st_dir[i] = -1
                st[i] = final_upper
            else:
                st_dir[i] = 1
                st[i] = final_lower
        else:
            if closes[i] > final_upper:
                st_dir[i] = 1
                st[i] = final_lower
            else:
                st_dir[i] = -1
                st[i] = final_upper

    return st, st_dir


def calc_highest(values: List[float], period: int) -> List[Optional[float]]:
    """Calculates highest value over the trailing period."""
    n = len(values)
    res: List[Optional[float]] = [None] * n
    for i in range(n):
        start = max(0, i - period + 1)
        res[i] = max(values[start : i + 1])
    return res


def calc_lowest(values: List[float], period: int) -> List[Optional[float]]:
    """Calculates lowest value over the trailing period."""
    n = len(values)
    res: List[Optional[float]] = [None] * n
    for i in range(n):
        start = max(0, i - period + 1)
        res[i] = min(values[start : i + 1])
    return res


def enrich_bars(bars: List[Dict[str, Any]], benchmark_bars: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
    """
    Computes all standard technical indicators and attaches them to bars dict:
    - ema20, ema50, ema200
    - atr14
    - rsi14
    - supertrend, st_dir
    - vol_sma20
    - high20, high50
    - ret60 (60-day momentum return)
    - rs_rating (relative strength vs benchmark if benchmark provided)
    """
    n = len(bars)
    if n == 0:
        return bars

    closes = [float(b['close']) for b in bars]
    highs = [float(b['high']) for b in bars]
    lows = [float(b['low']) for b in bars]
    vols = [float(b.get('volume', 0.0)) for b in bars]

    ema20 = calc_ema(closes, 20)
    ema50 = calc_ema(closes, 50)
    ema200 = calc_ema(closes, 200)
    atr14 = calc_atr(highs, lows, closes, 14)
    rsi14 = calc_rsi(closes, 14)
    st, st_dir = calc_supertrend(highs, lows, closes, 10, 3.0)
    vol_sma20 = calc_sma(vols, 20)
    high20 = calc_highest(highs, 20)
    high50 = calc_highest(highs, 50)
    low20 = calc_lowest(lows, 20)

    # Benchmark mapping for RS calculation
    bm_map = {}
    if benchmark_bars:
        for bm_b in benchmark_bars:
            bm_map[bm_b['date']] = float(bm_b['close'])

    for i in range(n):
        bars[i]['ema20'] = ema20[i]
        bars[i]['ema50'] = ema50[i]
        bars[i]['ema200'] = ema200[i]
        bars[i]['atr14'] = atr14[i]
        bars[i]['rsi14'] = rsi14[i]
        bars[i]['supertrend'] = st[i]
        bars[i]['st_dir'] = st_dir[i]
        bars[i]['vol_sma20'] = vol_sma20[i]
        bars[i]['high20'] = high20[i]
        bars[i]['high50'] = high50[i]
        bars[i]['low20'] = low20[i]

        # 60-day returns
        if i >= 60 and closes[i - 60] > 0:
            stock_ret60 = (closes[i] - closes[i - 60]) / closes[i - 60]
            bars[i]['ret60'] = stock_ret60

            # RS vs benchmark
            d_cur = bars[i]['date']
            d_prev = bars[i - 60]['date']
            if d_cur in bm_map and d_prev in bm_map and bm_map[d_prev] > 0:
                bm_ret60 = (bm_map[d_cur] - bm_map[d_prev]) / bm_map[d_prev]
                bars[i]['bm_ret60'] = bm_ret60
                bars[i]['rs_spread'] = stock_ret60 - bm_ret60
            else:
                bars[i]['bm_ret60'] = None
                bars[i]['rs_spread'] = None
        else:
            bars[i]['ret60'] = None
            bars[i]['bm_ret60'] = None
            bars[i]['rs_spread'] = None

    return bars
