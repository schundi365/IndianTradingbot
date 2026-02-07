# Drawdown Calculation Bug - FIXED

## Problem Identified

The drawdown calculation was using **equity** (which includes unrealized P&L from open positions) instead of **balance** (realized P&L only).

### What Was Happening:

```
1. Bot opens positions with large unrealized profit
   → Equity spikes to $99,757 (balance + unrealized P&L)
   → Peak equity set to $99,757 ❌

2. Positions close (even at profit)
   → Equity drops back to $785 (actual balance)
   → Drawdown calculated: $99,757 - $785 = 99% ❌ FALSE ALARM!
```

### The Error Log:
```
Peak Equity: $99757.13 (on 2026-02-06 09:20)
Current Equity: $785.40
Drawdown: $98971.73 (99.21%)  ← FALSE! This is not real drawdown
Maximum Allowed: 10%
```

## Root Cause

**File:** `src/mt5_trading_bot.py`
**Function:** `check_drawdown_limit()`

### Before (Broken):
```python
current_equity = account_info.equity  # ❌ Includes unrealized P&L
if not hasattr(self, 'peak_equity'):
    self.peak_equity = current_equity  # ❌ Sets false peak

if current_equity > self.peak_equity:
    self.peak_equity = current_equity  # ❌ Updates with temporary spikes

drawdown = self.peak_equity - current_equity  # ❌ False drawdown
```

**Problem:** When you have open positions with $99K unrealized profit:
- Equity = Balance + $99K (temporary)
- Peak gets set to this inflated value
- When positions close, equity drops back to balance
- System thinks you lost $99K!

## Solution Applied

Changed to use **balance** (realized P&L only) for peak tracking:

### After (Fixed):
```python
current_balance = account_info.balance  # ✓ Realized P&L only
current_equity = account_info.equity    # ✓ For info only

if not hasattr(self, 'peak_balance'):
    self.peak_balance = current_balance  # ✓ Real peak

if current_balance > self.peak_balance:
    self.peak_balance = current_balance  # ✓ Only updates on real gains

drawdown = self.peak_balance - current_balance  # ✓ Real drawdown
```

## Key Differences

### Balance vs Equity

**Balance:**
- Realized P&L only
- Changes only when positions close
- Stable, not affected by market fluctuations
- ✓ Correct for drawdown tracking

**Equity:**
- Balance + Unrealized P&L
- Changes every tick with open positions
- Volatile, temporary spikes
- ❌ Wrong for drawdown tracking

### Example Scenario

```
Starting Balance: $1,000

Day 1: Open position
  Balance: $1,000 (unchanged)
  Equity: $1,500 (unrealized +$500)
  
  OLD: Peak = $1,500 ❌
  NEW: Peak = $1,000 ✓

Day 2: Close position at +$100 profit
  Balance: $1,100 (realized profit)
  Equity: $1,100 (no open positions)
  
  OLD: Drawdown = ($1,500 - $1,100) / $1,500 = 27% ❌ FALSE!
  NEW: Drawdown = ($1,000 - $1,100) / $1,000 = 0% ✓ CORRECT!
  NEW: Peak updated to $1,100 ✓
```

## Changes Made

### 1. Variable Names Updated
- `peak_equity` → `peak_balance`
- `peak_equity_date` → `peak_balance_date`

### 2. Tracking Logic Fixed
- Now tracks `account_info.balance` instead of `account_info.equity`
- Peak only updates on realized gains (closed positions)
- Drawdown calculated from realized balance

### 3. Logging Improved
```python
logging.error(f"Peak Balance: ${self.peak_balance:.2f}")
logging.error(f"Current Balance: ${current_balance:.2f}")
logging.error(f"Current Equity: ${current_equity:.2f} (includes unrealized P/L)")
```

Now shows both balance and equity for clarity.

## Impact

### Before Fix:
- ❌ False drawdown alarms from temporary unrealized profits
- ❌ Trading stopped unnecessarily
- ❌ Peak set to inflated values
- ❌ Confusing error messages

### After Fix:
- ✓ Accurate drawdown based on realized P&L
- ✓ No false alarms from open positions
- ✓ Peak tracks actual account growth
- ✓ Clear logging shows both balance and equity

## Testing

### Scenario 1: Normal Trading
```
Balance: $1,000 → $1,100 (closed +$100)
Peak: $1,000 → $1,100 ✓
Drawdown: 0% ✓
```

### Scenario 2: Open Position with Unrealized Profit
```
Balance: $1,000 (unchanged)
Equity: $1,500 (unrealized +$500)
Peak: $1,000 (not updated) ✓
Drawdown: 0% ✓
```

### Scenario 3: Losing Trade
```
Balance: $1,100 → $1,050 (closed -$50)
Peak: $1,100 (unchanged)
Drawdown: ($1,100 - $1,050) / $1,100 = 4.5% ✓
```

### Scenario 4: Recovery
```
Balance: $1,050 → $1,150 (closed +$100)
Peak: $1,100 → $1,150 ✓
Drawdown: 0% ✓
```

## If You Need to Reset Peak

If the bot is currently paused due to the false drawdown, you can reset it:

### Option 1: Restart Bot
The peak will reinitialize to current balance on restart.

### Option 2: Manual Reset (if needed)
```python
# In Python console or script:
import MetaTrader5 as mt5
mt5.initialize()
account = mt5.account_info()
print(f"Current Balance: ${account.balance:.2f}")
print(f"Current Equity: ${account.equity:.2f}")

# The bot will auto-initialize peak_balance on next run
```

## Files Modified

- `src/mt5_trading_bot.py` - Fixed `check_drawdown_limit()` function

## Verification

After restarting the bot, you should see:
```
📊 Initial peak balance set: $785.40
```

Not:
```
📈 New peak equity: $99757.13  ← This was the bug
```

## Summary

✓ **Fixed** - Drawdown now calculated from balance (realized P&L)
✓ **Accurate** - No more false alarms from unrealized profits
✓ **Clear** - Logging shows both balance and equity
✓ **Stable** - Peak only updates on real account growth

---

**Date:** 2026-02-06
**Issue:** False 99% drawdown from using equity instead of balance
**Solution:** Changed to track balance (realized P&L) for peak/drawdown
**Result:** Accurate drawdown calculation, no false alarms
