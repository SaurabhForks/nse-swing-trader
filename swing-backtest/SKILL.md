---
name: swing-backtest
description: Event-driven historical swing trading backtester across 2 years of daily NSE data with exact statutory fees and regime gating.
---

# Swing Backtesting Skill

## Simulation Mechanics
1. **Chronological Day-by-Day Event Loop**:
   - Updates market regime via Nifty 50 daily bars.
   - Evaluates and processes all exits first (Stops, Targets, 20 EMA Trailing Stops, Time Stops).
   - Updates portfolio cash and realizes gains/losses including STT, DP charges, stamp duty, and turnover charges.
   - Evaluates new entries if cash and slot capacity exist, applying Minervini Stage 2 criteria and relative strength ranking.
   - Computes daily mark-to-market equity curve and drawdown metrics.

## Usage
```bash
python3 swing-backtest/backtest.py
python3 swing-backtest/backtest.py --capital 20000 --positions 2 --target 0.12 --risk 0.045
```
