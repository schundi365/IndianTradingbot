# TP/SL Inconsistency Issue - RESOLVED

## Problem Identified

**Stop losses were closer than take profits** due to a configuration inconsistency:

- **Stop Loss**: Using ATR-based calculation (`use_pip_based_sl: false`)
  - Formula: `entry_price ± (ATR × 2.0)`
  - For volatile symbols like XAUUSD (gold), ATR can be 10-20+ points
  - This resulted in SL distances of 200-400+ pips

- **Take Profit**: Using fixed pip-based calculation (`use_pip_based_tp: true`)
  - Fixed at 250 pips
  - Did not scale with volatility

**Result**: SL distance > TP distance = **Negative risk/reward ratio!**

## Root Cause

The configuration had mixed calculation methods:
```json
"use_pip_based_sl": false,  // ATR-based
"sl_pips": 50,
"use_pip_based_tp": true,   // Pip-based
"tp_pips": 250,
"atr_multiplier": 2.0
```

## Solution Applied

Changed both SL and TP to use **pip-based calculation** for consistency:

```json
"use_pip_based_sl": true,   // Now pip-based
"sl_pips": 50,
"use_pip_based_tp": true,   // Still pip-based
"tp_pips": 100,
"tp_levels": [1.5, 2.5, 4.0]
```

## New Configuration

### Stop Loss
- **Distance**: 50 pips from entry
- **Consistent** across all symbols

### Take Profit Levels
- **TP Level 1**: 150 pips (100 × 1.5) = **3:1 reward/risk**
- **TP Level 2**: 250 pips (100 × 2.5) = **5:1 reward/risk**
- **TP Level 3**: 400 pips (100 × 4.0) = **8:1 reward/risk**

## Verification Results

✓ Both SL and TP use pip-based calculation
✓ All TP levels are greater than SL distance
✓ Positive risk/reward ratios on all levels
✓ Configuration is consistent and correct

## Alternative Option (Not Applied)

If you prefer **volatility-adaptive** calculations:

```json
"use_pip_based_sl": false,
"use_pip_based_tp": false,
"atr_multiplier": 2.0,
"reward_ratio": 2.0
```

This makes both SL and TP scale with ATR, maintaining consistent risk/reward ratios while adapting to market volatility.

## Files Created

1. `fix_tp_sl_inconsistency.py` - Script that fixed the configuration
2. `verify_tp_sl_fix.py` - Verification script
3. `bot_config_backup_20260206_054928.json` - Backup of old config

## Next Steps

1. ✓ Configuration fixed
2. ✓ Verification passed
3. **Restart the bot** to apply changes
4. Monitor first few trades to confirm SL < TP
5. Adjust `sl_pips`/`tp_pips` if needed for your strategy

## Impact

- **Before**: Negative risk/reward (SL > TP)
- **After**: Positive risk/reward (TP 3-8× larger than SL)
- **Expected**: Better trade outcomes with proper risk management

---

**Status**: ✓ FIXED AND VERIFIED
**Date**: 2026-02-06
**Action Required**: Restart bot to apply changes
