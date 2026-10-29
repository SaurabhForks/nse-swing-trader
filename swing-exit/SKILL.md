---
name: swing-exit
description: Multi-stage exit rules (initial stop loss 4.5%, profit target +12%, dynamic 20 EMA trailing stop, and 30-day time stop).
---

# Swing Exit Skill

## Exit Rules & Execution Priority
1. **Initial Hard Stop Loss**:
   - Placed at maximum 4.5% below entry (or Supertrend level).
   - If day's low touches or crosses stop loss, position is closed immediately.
2. **Profit Target (+12%)**:
   - Fixed swing profit objective locking in +12% gain (giving a $> 2.6:1$ reward-to-risk ratio on a 4.5% risk).
3. **Dynamic 20 EMA Trailing Stop**:
   - When the position achieves at least +5% gain, the trader trails along the rising 20 EMA.
   - If the daily close drops below the 20 EMA, the position is closed to lock in accumulated profits while preventing a winning trade from turning into a loss.
4. **Time Stop (30 Trading Days)**:
   - If a stock consolidates without hitting either target or stop for 30 trading days (~6 calendar weeks), the trade is closed at the market to redeploy capital into newer, faster-moving leaders.
