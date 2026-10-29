---
name: swing-scanner
description: Scans 29 liquid NSE stocks for Minervini Stage 2 Breakouts and Supertrend Ignition setups with Nifty market regime gating.
---

# Swing Scanner Skill

## Scanner Architecture
1. **Regime Gating**:
   - Queries `swing-regime` to check Nifty 50 status.
   - If Nifty is in **BEAR** regime (Close < 50 EMA), the scanner aborts new buy checks to avoid whipsaws.
2. **Universe Coverage**:
   - Scans 29 top liquid NSE equities (Nifty Core large-caps + high-beta momentum leaders).
3. **Filter Pipeline**:
   - Checks Minervini Stage 2 status (`Close > 50 EMA > 200 EMA`).
   - Relative Strength verification (stock 60-day return > Nifty 60-day return).
   - Volume surge verification ($RVol \ge 1.25\times$).
   - Computes delivery charges and expected net profit at Target 1.

## Usage
```bash
python3 swing-scanner/scanner.py
python3 swing-scanner/scanner.py --capital 20000 --json
```
