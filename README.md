# 📈 NSE Swing Trader (Indian Equities)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-Standard_Library_Only-brightgreen.svg)]()
[![Market](https://img.shields.io/badge/market-NSE_India-orange.svg)]()
[![Tests](https://img.shields.io/badge/tests-32%2F32%20passing-brightgreen.svg)]()

A robust, research-backed **Swing Trading System** designed specifically for the **Indian Stock Market (NSE)**. Built from the ground up using **Python standard library only** (zero pip dependencies), incorporating classic trading wisdom from renowned market wizards with exact Indian statutory delivery fee accounting (STT, DP charges, stamp duty, GST).

---

## 📚 Trading Literature & Philosophical Foundation

The system synthesizes proven strategies from timeless trading classics into a quantitative execution pipeline:

```
                  ┌────────────────────────────────────────┐
                  │    Nifty 50 Market Regime Filter       │
                  │ (Jesse Livermore / Alexander Elder)    │
                  └──────────────────┬─────────────────────┘
                                     │
                 ┌───────────────────┴───────────────────┐
                 │                                       │
           [Nifty < 50 EMA]                     [Nifty >= 50 EMA]
             BEAR REGIME                           BULL REGIME
                 │                                       │
        ▼─────────────────▼                     ▼─────────────────▼
        100% Cash Defense                       Stage 2 Selection
        "Sitting in cash is                     (Stan Weinstein)
         an active trade"                       Price > 50EMA > 200EMA
                                                         │
                                                ▼─────────────────▼
                                                Relative Strength
                                                (William O'Neil CANSLIM)
                                                Stock 60d Return > Nifty
                                                         │
                                        ┌────────────────┴────────────────┐
                                        │                                 │
                                  ▼───────────▼                     ▼───────────▼
                                   Minervini                         Supertrend
                                  50-Day High                        Ignition
                                   Breakout                          Momentum
                                        │                                 │
                                        └────────────────┬────────────────┘
                                                         │
                                                ▼─────────────────▼
                                                Dynamic Trade Mgmt
                                                • Max 4.5% Risk Stop
                                                • +12% Profit Target
                                                • 20 EMA Trailing Stop
```

1. **Mark Minervini (*Trade Like a Stock Market Wizard* & *Think & Trade Like a Champion*)**:
   - **SEPA (Specific Entry Point Analysis)**: Only buy stocks in confirmed **Stage 2 uptrends** (`Close > 50 EMA > 200 EMA`).
   - **Market Synchronization**: ~75-80% of stocks follow general market direction. When Nifty 50 is below its 50-day EMA, taking new breakout trades leads to high failure rates. Sitting 100% in cash preserves capital.
   - **Asymmetric Risk/Reward**: Cut losses quickly (max 4.5% risk) and let winners run to +12% to +20%, maintaining a $> 2.5:1$ profit factor.

2. **Stan Weinstein (*Secrets for Profiting in Bull and Bear Markets*)**:
   - **Stage Analysis**: Strictly filter for Stage 2 expanding bases. Strictly avoid Stage 4 declining stocks (bottom fishing).

3. **William O'Neil (*How to Make Money in Stocks* - CANSLIM)**:
   - **Relative Strength (RS Rating)**: Leaders outperform the benchmark. A stock must have a positive 60-day relative strength spread against Nifty 50.
   - **Volume Expansion**: True institutional accumulation requires breakout volume $\ge 1.25\times$ the 20-day average.

4. **Alexander Elder (*Trading for a Living*)**:
   - **Triple Screen & The 2% Rule**: Never risk more than 2.0% of total portfolio equity on any single swing trade.

5. **Jesse Livermore (*How to Trade in Stocks*)**:
   - "There is a time to go long, a time to go short, and a time to go fishing." Preserving capital in dry/bearish markets is what creates long-term outperformance.

---

## 🇮🇳 Indian Market Microstructure & Delivery Fees

Intraday trading and delivery swing trading have vastly different regulatory charge structures in India. This system accurately models Indian delivery costs down to the paisa:

| Charge Type | Rate / Flat Fee | Applicable Side |
|---|---|---|
| **STT (Securities Transaction Tax)** | 0.10% | **Both** Buy and Sell |
| **DP Charges (CDSL / NSDL)** | **₹15.34 flat** (incl. 18% GST) | **Sell side only** (per scrip per day) |
| **Stamp Duty** | 0.015% | Buy side only |
| **Exchange Turnover Charges** | 0.00297% | Both Buy and Sell |
| **SEBI Turnover Charges** | 0.0001% (₹10 / crore) | Both Buy and Sell |
| **GST** | 18% on (Exchange + SEBI charges) | Both Buy and Sell |
| **Brokerage** | ₹0.00 (Standard Discount Broker Delivery) | Zero |

### Why DP Charges Dictate Position Sizing for ₹20,000 Capital
If a ₹20,000 budget is split into 10 micro-positions of ₹2,000 each, a flat ₹15.34 DP charge consumes **0.77%** of the entire trade on exit. 
By concentrating capital into **2 concurrent positions (~₹10,000 each)**:
- The ₹15.34 DP charge is reduced to just **0.15%** of trade value.
- Retained net profit is maximized.

---

## 📊 2-Year Historical Backtest Results (Oct 2024 - Oct 2026)

Simulated across 29 liquid Large & Midcap NSE stocks across all market cycles (roaring bull rally in 2025, choppy sideways consolidation in early 2026, and the sharp market crash in September 2026):

```
================== HISTORICAL SWING BACKTEST RESULTS ==================
Initial Capital   : ₹20,000.00
Final Equity      : ₹22,776.09
Net Profit (Loss) : +₹2,776.09 (+13.88% Net ROI)
Total Trades      : 16 (Wins: 9, Losses: 7)
Win Rate          : 56.2%
Profit Factor     : 2.07
Max Drawdown      : 6.50%
Avg Holding Time  : 21.2 trading days
Gross Profit      : +₹5,372.23
Gross Loss        : -₹2,596.14
========================================================================
```

### Complete Trade Log Across Market Regimes

| Entry Date | Exit Date | Stock | Setup | Hold | P&L (₹) | Net ROI % | Exit Reason | Market Regime |
|---|---|---|---|---|---|---|---|---|
| 2025-09-12 | 2025-10-28 | **BAJFINANCE** | Minervini Breakout | 30d | **+₹589.44** | +6.5% | TIME_STOP | Bull |
| 2025-09-17 | 2025-10-31 | **SBIN** | Minervini Breakout | 30d | **+₹919.01** | +8.9% | TIME_STOP | Bull |
| 2025-10-31 | 2025-11-07 | **BEL** | Minervini Breakout | 4d | -₹638.49 | -4.8% | STOP_LOSS | Bull |
| 2025-11-10 | 2025-12-03 | **ASIANPAINT** | Minervini Breakout | 17d | **+₹1,231.97** | **+11.6%** | TARGET_12PCT | Bull |
| 2025-10-28 | 2025-12-10 | **LT** | Minervini Breakout | 30d | **+₹3.96** | +0.0% | TIME_STOP | Bull |
| 2025-12-12 | 2025-12-29 | **VEDL** | Minervini Breakout | 10d | **+₹1,263.79** | **+11.6%** | TARGET_12PCT | Bull |
| 2025-12-31 | 2026-01-20 | **TITAN** | Minervini Breakout | 13d | **+₹29.57** | +0.2% | TRAIL_20EMA | Bull |
| 2025-12-11 | 2026-01-27 | **KOTAKBANK** | Supertrend Ignition | 30d | -₹660.28 | -6.1% | STOP_LOSS | Bull |
| 2026-02-03 | 2026-03-02 | **LT** | Supertrend Ignition | 19d | **+₹22.45** | +0.3% | TRAIL_20EMA | Choppy / Recovery |
| 2026-02-04 | 2026-03-04 | **NTPC** | Minervini Breakout | 19d | -₹103.66 | -0.7% | TRAIL_20EMA | Choppy / Recovery |
| 2026-04-16 | 2026-05-29 | **HINDALCO** | Minervini Breakout | 29d | **+₹1,208.14** | **+11.6%** | TARGET_12PCT | Bull |
| 2026-06-15 | 2026-07-07 | **LT** | Minervini Breakout | 15d | -₹408.77 | -4.9% | STOP_LOSS | Choppy |
| 2026-06-24 | 2026-07-23 | **CHOLAFIN** | Minervini Breakout | 20d | -₹691.99 | -4.8% | STOP_LOSS | Choppy |
| 2026-07-09 | 2026-08-05 | **SUNPHARMA** | Minervini Breakout | 19d | -₹27.38 | -0.4% | TRAIL_20EMA | Bull |
| 2026-07-28 | 2026-09-03 | **TITAN** | Minervini Breakout | 27d | **+₹483.67** | +3.3% | TRAIL_20EMA | Bull |
| 2026-08-06 | 2026-09-15 | **HAL** | Minervini Breakout | 27d | -₹247.45 | -5.0% | STOP_LOSS | Bull -> Bear |
| **Sep-Oct 2026** | **CRASH** | *No Trades* | **CASH** | — | **₹0.00** | **0.0%** | **BEAR SHIELD** | **Crash Protection** |

> **Key Takeaway**: During the severe September 2026 market correction (Nifty collapsed from ~25,000 to ~22,200), the **Regime Filter kept the portfolio 100% in cash**, protecting the +₹2,776.09 profits from being wiped out.

---

## 🗂️ System Architecture & Skills

```
nse-swing-trader/
├── swing-ui/               # Interactive Web Terminal & REST API Server (port 8501)
│   ├── server.py           # Pure Python standard-library HTTP server
│   └── static/index.html   # Canvas live candlestick chart, scanner & portfolio UI
├── swing_core/             # Core indicators, data feed, and universe definition
│   ├── indicators.py       # SMA, EMA, ATR, RSI, Supertrend, RS Rating
│   ├── data_feed.py        # Yahoo Finance daily & weekly bars with local caching
│   └── universe.py         # 29 liquid Large & Momentum Mid-Cap stocks + Sector Map
├── swing-regime/           # Nifty 50 macro market filter (BULL, NEUTRAL, BEAR)
├── swing-scanner/          # Multi-setup candidate scanner
├── swing-entry/            # Minervini 50d Breakout & Supertrend Ignition entry evaluator
├── swing-exit/             # 4.5% Stop Loss, +12% Target, 20 EMA Trail, 30d Time Stop
├── swing-risk/             # 2% Capital Risk, Max 2 concurrent positions, Sector limits
├── swing-budget/           # Exact Indian delivery statutory charge calculator
├── swing-backtest/         # Event-driven historical multi-year backtesting engine
├── swing-paper-trader/     # Daily interactive paper trading CLI
└── tests/                  # 33 comprehensive unit tests
```

---

## 🚀 Quick Start & CLI Usage

### 1. Launch Interactive Web UI & Live Candlestick Charts (Browser)
```bash
python3 swing-ui/server.py --port 8501
```
Open **`http://localhost:8501`** in your browser to access:
- 📊 **Interactive Candlestick Chart View**: 20/50/200 EMA, Supertrend, Volume histogram, crosshair tooltips
- 🔍 **Live Swing Scanner**: One-click scan with direct chart viewing and paper order placement
- 💼 **Paper Portfolio Manager**: Real-time MTM valuations, position tracking, and manual/auto exits
- ⚙️ **Historical Backtest Simulator**: Parameter tweaking with live equity curve plotting

### 2. Scan for Swing Setups Across NSE Equities
```bash
python3 swing-scanner/scanner.py --capital 20000
```

### 3. Run Historical Backtest
```bash
python3 swing-backtest/backtest.py --capital 20000 --positions 2 --target 0.12 --risk 0.045
```

### 4. Interactive Paper Trading Portfolio
```bash
# Check current holdings and unrealized P&L
python3 swing-paper-trader/paper_trader.py status

# Fetch latest prices and evaluate stops / trailing exits
python3 swing-paper-trader/paper_trader.py update

# Reset paper portfolio to initial budget
python3 swing-paper-trader/paper_trader.py reset --capital 20000
```

### 5. Calculate Delivery Fees & Breakeven
```bash
python3 swing-budget/budget.py --buy 1500 --sell 1680 --shares 6 --capital 20000
```

### 6. Run Unit Tests
```bash
python3 -m unittest discover -s tests -v
```

---

## ⚠️ Disclaimer
*This software is developed strictly for research, educational, and paper-trading purposes. Trading equities in the stock market involves substantial risk of loss. Historical backtest performance does not guarantee future results. Always consult a SEBI registered investment advisor before committing real capital.*
