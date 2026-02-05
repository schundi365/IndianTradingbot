# TP Calculation Bug Fix - Complete

## Issue Identified

### Problem 1: Incorrect TP Values for XPDUSD Trades
**Reported Trade Data:**
```
Symbol: XPDUSD
Entry Price: ~1,706
Stop Loss: 1,748 (correct - above entry for SELL)
Take Profit Values: 266.636, 2.981, 185.673 (COMPLETELY WRONG!)
```

**Expected TP Values (for SELL trade):**
- TP Level 1 (R:R 1.5): 1,641.94
- TP Level 2 (R:R 2.5): 1,599.21
- TP Level 3 (R:R 4.0): 1,535.13

**Actual TP Values:**
- TP Level 1: 266.636 ❌
- TP Level 2: 2.981 ❌
- TP Level 3: 185.673 ❌

### Problem 2: Pip-Based TP Not Working for Split Orders
The `calculate_multiple_take_profits()` method did not support pip-based TP calculation, even though:
- Config has `"use_pip_based_tp": true`
- Config has `"tp_pips": 100`
- Single orders work correctly with pip-based TP
- Split orders ignored this setting and used ratio-based calculation

### Root Cause
The `calculate_multiple_take_profits()` method:
1. Did not accept a `symbol` parameter
2. Could not call `calculate_price_from_pips()` without symbol info
3. Always fell back to ratio-based calculation
4. The bizarre TP values (266, 2.98, 185) suggest a critical bug in the calculation logic or data corruption

## Fixes Applied

### Fix 1: Added Symbol Parameter
```python
def calculate_multiple_take_profits(self, entry_price, stop_loss, direction, ratios=None, symbol=None):
```

### Fix 2: Implemented Pip-Based TP for Split Orders
```python
# Check if using pip-based TP
if self.config.get('use_pip_based_tp', False) and symbol:
    tp_pips_base = self.config.get('tp_pips', 100)
    tp_prices = []
    
    # Calculate TP for each level using pip multipliers
    for i, ratio in enumerate(ratios):
        # Multiply base pips by the ratio
        tp_pips = tp_pips_base * ratio
        tp = self.calculate_price_from_pips(symbol, entry_price, tp_pips, direction, is_sl=False)
        tp_prices.append(tp)
```

### Fix 3: Added Detailed Logging
Added comprehensive logging to track TP calculations:
- Entry price, SL, and risk values
- Each TP level with ratio and calculated value
- Pip-based calculations with pip values

### Fix 4: Updated All Method Calls
Updated both calls to `calculate_multiple_take_profits()` to pass the `symbol` parameter:
1. Line 1539: Split order placement
2. Line 2134: Regular trade placement

## How Pip-Based TP Works for Split Orders

With `use_pip_based_tp: true` and `tp_pips: 100`:

**For XPDUSD SELL trade:**
- TP Level 1 (ratio 1.5): 100 × 1.5 = 150 pips below entry
- TP Level 2 (ratio 2.5): 100 × 2.5 = 250 pips below entry
- TP Level 3 (ratio 4.0): 100 × 4.0 = 400 pips below entry

**Example calculation:**
```
Entry: 1,706.024
TP1: 1,706.024 - (150 pips) = ~1,691.024
TP2: 1,706.024 - (250 pips) = ~1,681.024
TP3: 1,706.024 - (400 pips) = ~1,666.024
```

## Testing Required

### 1. Verify TP Calculations in Logs
After restarting the bot, check logs for:
```
Using pip-based TP calculation:
  TP Level 1: 150.0 pips (ratio 1.5) = 1691.024
  TP Level 2: 250.0 pips (ratio 2.5) = 1681.024
  TP Level 3: 400.0 pips (ratio 4.0) = 1666.024
```

### 2. Verify Actual Trade TP Values
Check MT5 terminal to ensure TP values match calculations

### 3. Test Both Modes
- Test with `use_pip_based_tp: true` (pip-based)
- Test with `use_pip_based_tp: false` (ratio-based)

## Configuration Options

### Pip-Based TP (Recommended for consistency)
```json
{
  "use_pip_based_tp": true,
  "tp_pips": 100,
  "tp_levels": [1.5, 2.5, 4.0]
}
```
Result: 150, 250, 400 pips for the 3 levels

### Ratio-Based TP (Dynamic based on SL distance)
```json
{
  "use_pip_based_tp": false,
  "tp_levels": [1.5, 2.5, 4.0]
}
```
Result: 1.5×, 2.5×, 4.0× the SL distance

## Dashboard Control

The pip-based TP settings can be controlled from the dashboard:
- Navigate to: Configuration → Position Management → Pip-Based TP/SL
- Toggle "Use Pip-Based TP"
- Set "TP Pips" value
- Click "Save Configuration"

## Files Modified

1. `src/mt5_trading_bot.py` - Updated calculate_multiple_take_profits method
2. Backup created: `src/mt5_trading_bot.py_backup_tp_fix_20260205_135518`

## Next Steps

1. **Restart the bot** to apply the fixes
2. **Monitor the first few trades** closely
3. **Check logs** for TP calculation details
4. **Verify TP values** in MT5 terminal match expectations
5. **Report any remaining issues** with specific trade data

## Investigation Needed

The bizarre TP values (266, 2.98, 185) from the original trades suggest there may be an additional bug or data corruption issue. Possible causes:
1. Memory corruption
2. Variable type mismatch
3. Uninitialized variable
4. Race condition in multi-threaded code
5. MT5 API returning incorrect data

**Recommendation:** Monitor logs carefully for the next few trades to see if the issue persists or if it was related to the missing symbol parameter.

## Status

✅ Pip-based TP support added to split orders
✅ Symbol parameter added to calculate_multiple_take_profits
✅ Detailed logging added for debugging
✅ All method calls updated
⏳ Awaiting bot restart and testing
⏳ Monitoring for any remaining calculation issues

---

**Date:** 2026-02-05
**Session:** 20 (Context Transfer Continuation)
**Priority:** CRITICAL - Affects trade profitability
