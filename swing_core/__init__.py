"""
Swing Core package for technical indicators, data feeding, and universe definitions.
"""
from swing_core.indicators import (
    calc_sma, calc_ema, calc_atr, calc_rsi, calc_supertrend,
    calc_highest, calc_lowest, enrich_bars
)
from swing_core.data_feed import fetch_historical_bars
from swing_core.universe import BENCHMARK_INDEX, ACTIVE_UNIVERSE, SECTOR_MAP
