---
name: swing-ui
description: Interactive Web Terminal and REST API server providing live interactive candlestick charting, scanner controls, paper portfolio management, and backtest simulation.
---

# Swing UI Skill

## Features
- **Interactive Candlestick Chart View**:
  - Pure HTML5 Canvas candlestick chart with crosshairs and price/indicator tooltips.
  - Multi-timeframe zooming (1M, 3M, 6M, 1Y, ALL).
  - Dynamic technical overlays: 20 EMA (Cyan), 50 EMA (Amber), 200 EMA (Purple), and Supertrend (10, 3) (Green/Red band).
  - Volume histogram sub-chart.
- **Swing Scanner Dashboard**:
  - Live scanning of 29 liquid NSE stocks with Minervini SEPA & Supertrend Ignition filters.
  - One-click chart loading and one-click paper order execution.
- **Paper Portfolio Manager**:
  - MTM mark-to-market valuations, stop-loss and target tracking, exact delivery fee deduction (STT 0.1%, DP charges ₹15.34).
- **Backtest Simulator**:
  - Custom parameter testing with live interactive equity curve.

## Launch Command
```bash
python3 swing-ui/server.py --port 8501
```
Then open `http://localhost:8501` in your browser.
