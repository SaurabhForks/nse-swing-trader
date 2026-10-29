---
name: swing-risk
description: Manages portfolio risk, enforces maximum 2% equity risk per trade, limits maximum concurrent open positions, and ensures sector diversification.
---

# Swing Risk Management Skill

## Risk Rules
1. **The 2% Rule (Alexander Elder & Mark Minervini)**:
   - Never risk more than 2% of total equity on any single swing trade.
   - For a ₹20,000 account, the maximum rupee risk on a trade is ₹400.
2. **Capital Concentration Limits**:
   - Maximum 2 concurrent positions for a ₹20,000 account (~₹10,000 allocated per position).
   - This ensures each position has sufficient size so that fixed depository fees (₹15.34 DP charge) do not erode returns.
3. **Sector Diversification**:
   - Maximum 1 open position per sector to avoid systemic correlation risk.

## Sizing Formula
$$\text{Shares} = \min\left( \left\lfloor \frac{\text{Equity} \times 0.02}{\text{Entry} - \text{Stop}} \right\rfloor, \left\lfloor \frac{\text{Equity} / 2}{\text{Entry}} \right\rfloor \right)$$

## Usage
```bash
python3 swing-risk/risk.py --equity 20000 --price 1500 --stop 1432.5
```
