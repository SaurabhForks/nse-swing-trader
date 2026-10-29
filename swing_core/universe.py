"""
NSE Stock Universe Definitions for Swing Trading.
Includes highly liquid Large-Cap and Momentum Mid-Cap stocks traded on NSE.
"""

# Benchmark
BENCHMARK_INDEX = "^NSEI"  # NIFTY 50

# Core High-Liquidity Swing Universe
NIFTY_CORE = [
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "SBIN.NS",
    "BHARTIARTL.NS",
    "ITC.NS",
    "LT.NS",
    "KOTAKBANK.NS",
    "SUNPHARMA.NS",
    "TITAN.NS",
    "BAJFINANCE.NS",
    "TATACONSUM.NS",
    "MARUTI.NS",
    "AXISBANK.NS",
    "ASIANPAINT.NS",
    "NTPC.NS",
    "POWERGRID.NS"
]

# High-Beta Momentum Leaders (Nifty Next 50 & Midcap Leaders)
MOMENTUM_LEADERS = [
    "TRENT.NS",
    "BEL.NS",
    "HAL.NS",
    "VBL.NS",
    "CHOLAFIN.NS",
    "INDHOTEL.NS",
    "PERSISTENT.NS",
    "COALINDIA.NS",
    "VEDL.NS",
    "HINDALCO.NS"
]

# Combined 29-stock Active Swing Universe
ACTIVE_UNIVERSE = NIFTY_CORE + MOMENTUM_LEADERS

# Sector Mapping to avoid portfolio over-concentration
SECTOR_MAP = {
    "RELIANCE.NS": "Energy",
    "TCS.NS": "IT",
    "INFY.NS": "IT",
    "PERSISTENT.NS": "IT",
    "HDFCBANK.NS": "Banking",
    "ICICIBANK.NS": "Banking",
    "SBIN.NS": "Banking",
    "KOTAKBANK.NS": "Banking",
    "AXISBANK.NS": "Banking",
    "BAJFINANCE.NS": "Financials",
    "CHOLAFIN.NS": "Financials",
    "BHARTIARTL.NS": "Telecom",
    "ITC.NS": "FMCG",
    "TATACONSUM.NS": "FMCG",
    "VBL.NS": "FMCG",
    "LT.NS": "Capital Goods",
    "BEL.NS": "Defence",
    "HAL.NS": "Defence",
    "SUNPHARMA.NS": "Pharma",
    "TITAN.NS": "Consumer Discretionary",
    "TRENT.NS": "Retail",
    "INDHOTEL.NS": "Hospitality",
    "MARUTI.NS": "Auto",
    "ASIANPAINT.NS": "Paints/Chemicals",
    "NTPC.NS": "Power",
    "POWERGRID.NS": "Power",
    "COALINDIA.NS": "Metals/Mining",
    "VEDL.NS": "Metals/Mining",
    "HINDALCO.NS": "Metals/Mining"
}
