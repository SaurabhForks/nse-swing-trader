---
name: swing-paper-trader
description: Daily paper trading assistant CLI to track multi-day positions, check stops/targets, monitor unrealized P&L, and manage cash.
---

# Swing Paper Trader Skill

## Features
- Persistent portfolio tracking stored in `portfolio_state.json`.
- Automatic MTM (mark-to-market) valuations using daily closing prices.
- Checks exit rules (Stop Loss, +12% Target, 20 EMA Trailing Stop, 30d Time Stop) on demand.
- Deducts exact Indian delivery statutory charges (STT 0.1%, DP charges ₹15.34, Stamp Duty, GST).

## CLI Commands
```bash
# Check current portfolio balance and active holdings
python3 swing-paper-trader/paper_trader.py status

# Fetch today's bars and evaluate exits/trailing stops
python3 swing-paper-trader/paper_trader.py update

# Reset paper portfolio with fresh budget (default: ₹20,000)
python3 swing-paper-trader/paper_trader.py reset --capital 20000
```
