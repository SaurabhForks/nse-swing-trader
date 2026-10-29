---
name: swing-budget
description: Calculates exact Indian statutory delivery trading charges (STT 0.1%, DP charges ₹15.34, GST, stamp duty) and sizes position allocations.
---

# Swing Budget Skill

## Indian Equities Delivery Fee Structure
Unlike intraday trading (where STT is only 0.025% on sell and DP charges do not apply), **swing/delivery trades** have distinct statutory charges:
1. **STT (Securities Transaction Tax)**: 0.1% on buy value + 0.1% on sell value (total 0.20% on turnover).
2. **DP Charges (Depository Participant)**: Fixed ₹15.34 (₹13.00 + 18% GST) charged by CDSL/NSDL per stock per day when selling delivery shares.
3. **Stamp Duty**: 0.015% on buy turnover.
4. **Exchange Turnover Charges**: 0.00297% on buy and sell.
5. **SEBI Turnover Charges**: 0.0001% (₹10 per crore) on buy and sell.
6. **GST**: 18% on (Exchange turnover charges + SEBI charges + Brokerage).

## Budget Allocation for ₹20,000 Portfolio
- **Max Concurrent Positions**: 2 positions (allocated ~₹10,000 each).
- Holding fewer positions (~₹10,000 per trade) ensures that the fixed ₹15.34 DP charge is only ~0.15% of the position, keeping overhead minimal and maximizing net retained profit!

## Usage
```bash
python3 swing-budget/budget.py --buy 1500 --sell 1680 --shares 6 --capital 20000
```
