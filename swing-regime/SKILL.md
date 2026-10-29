---
name: swing-regime
description: Evaluates Nifty 50 macro market regime (Bull, Neutral, Bear) to govern capital deployment and block high-risk trades during market corrections.
---

# Swing Market Regime Skill

## Theoretical Foundations
1. **Mark Minervini (*Trade Like a Stock Market Wizard*)**:
   - ~75-80% of all stocks follow the general market trend.
   - Taking breakout buys in a declining general market results in whipsaws and failed patterns.
   - When the market is in a downtrend (Index below 50 EMA), sitting 100% in cash is a highly profitable active decision.
2. **Jesse Livermore (*How to Trade in Stocks*)**:
   - "There is a time to go long, a time to go short, and a time to go fishing."
   - Patience and capital preservation during bear phases ensure your capital is intact when the next powerful bull run begins.

## Regime Classification Matrix

| Regime | Condition | Allowed Actions | Capital Allocation |
|---|---|---|---|
| **BULL** | Nifty >= 50 EMA & 50 EMA >= 200 EMA | All Breakout & Momentum entries allowed | 100% (Full sizing) |
| **NEUTRAL** | Nifty >= 50 EMA but 50 EMA < 200 EMA (or shallow pullback) | Highly selective entries with high RS only | 50% (Half sizing) |
| **BEAR** | Nifty < 50 EMA and trending down | **ALL NEW BUYS BLOCKED** | 0% (100% Cash preservation) |

## Usage
```bash
python3 swing-regime/regime.py
python3 swing-regime/regime.py --json
```
