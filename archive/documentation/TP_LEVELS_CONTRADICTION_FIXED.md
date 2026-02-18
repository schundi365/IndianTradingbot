# TP Levels Contradiction - FIXED

## Problem Identified

The configuration had **contradictory TP level definitions**:

```json
{
  "tp_level_1": 1,      // ❌ Obsolete individual fields
  "tp_level_2": 2,
  "tp_level_3": 3,
  "tp_levels": [1.5, 2.5, 4.0],  // ✓ What the bot actually uses
}
```

### Why This Was a Problem

1. **Confusion**: Two different sets of values for the same thing
2. **Inconsistency**: Individual fields had values `[1, 2, 3]` while array had `[1.5, 2.5, 4.0]`
3. **Maintenance**: Changes to one wouldn't update the other
4. **Bugs**: Dashboard saved individual fields, but bot read from array

### Which Format is Used?

**Bot Code (`src/mt5_trading_bot.py`):**
```python
self.tp_levels = config.get('tp_levels', [1.5, 2.5, 4.0])  # ✓ Uses array
```

**Dashboard (before fix):**
```javascript
tp_level_1: parseFloat(document.getElementById('tp-level-1').value),  // ❌ Saved individual
tp_level_2: parseFloat(document.getElementById('tp-level-2').value),
tp_level_3: parseFloat(document.getElementById('tp-level-3').value),
```

## Solution Applied

### 1. Removed Obsolete Fields from Config

**File:** `bot_config.json`

**Before:**
```json
{
  "tp_level_1": 1,
  "tp_level_2": 2,
  "tp_level_3": 3,
  "tp_levels": [1.5, 2.5, 4.0]
}
```

**After:**
```json
{
  "tp_levels": [1.5, 2.5, 4.0]
}
```

### 2. Updated Dashboard to Save Array

**File:** `templates/dashboard.html`

**Before:**
```javascript
tp_level_1: parseFloat(document.getElementById('tp-level-1').value),
tp_level_2: parseFloat(document.getElementById('tp-level-2').value),
tp_level_3: parseFloat(document.getElementById('tp-level-3').value),
```

**After:**
```javascript
tp_levels: [
    parseFloat(document.getElementById('tp-level-1').value),
    parseFloat(document.getElementById('tp-level-2').value),
    parseFloat(document.getElementById('tp-level-3').value)
],
```

### 3. Updated Dashboard to Load from Array

**File:** `templates/dashboard.html`

**Before:**
```javascript
document.getElementById('tp-level-1').value = config.tp_level_1;
document.getElementById('tp-level-2').value = config.tp_level_2;
document.getElementById('tp-level-3').value = config.tp_level_3;
```

**After:**
```javascript
// Load from array with fallback for backward compatibility
const tpLevels = config.tp_levels || [config.tp_level_1 || 1.5, config.tp_level_2 || 2.5, config.tp_level_3 || 4.0];
document.getElementById('tp-level-1').value = tpLevels[0];
document.getElementById('tp-level-2').value = tpLevels[1];
document.getElementById('tp-level-3').value = tpLevels[2];
```

### 4. Updated Config Manager Defaults

**File:** `src/config_manager.py`

**Before:**
```python
'tp_level_1': 1.5,
'tp_level_2': 2.5,
'tp_level_3': 4,
'tp_levels': [1.5, 2.5, 4.0],
```

**After:**
```python
'tp_levels': [1.5, 2.5, 4.0],
```

## Files Modified

1. ✓ `bot_config.json` - Removed obsolete fields
2. ✓ `templates/dashboard.html` - Updated save/load logic
3. ✓ `src/config_manager.py` - Removed from defaults

## Verification

### Bot Code
✓ Uses `tp_levels` array only
✓ No references to individual `tp_level_1/2/3` fields

### Dashboard
✓ Now saves to `tp_levels` array
✓ Loads from `tp_levels` array with backward compatibility fallback
✓ UI still uses same input fields (tp-level-1, tp-level-2, tp-level-3)

### Config File
✓ No more contradictory fields
✓ Single source of truth: `tp_levels` array

## Benefits

### 1. No More Confusion
- Single definition of TP levels
- Clear which values are being used
- Easier to understand and maintain

### 2. Consistency
- Dashboard saves what bot reads
- No more sync issues
- Changes immediately reflected

### 3. Backward Compatibility
- Dashboard can still load old configs with individual fields
- Automatically converts to array format on save
- No data loss during migration

## What TP Levels Mean

The `tp_levels` array contains **risk/reward ratio multipliers**:

```json
"tp_levels": [1.5, 2.5, 4.0]
```

### With Ratio-Based TP (use_pip_based_tp: false)
- TP1: SL distance × 1.5
- TP2: SL distance × 2.5
- TP3: SL distance × 4.0

**Example:** If SL is 50 pips from entry:
- TP1: 75 pips (50 × 1.5)
- TP2: 125 pips (50 × 2.5)
- TP3: 200 pips (50 × 4.0)

### With Pip-Based TP (use_pip_based_tp: true)
- TP1: tp_pips × 1.5
- TP2: tp_pips × 2.5
- TP3: tp_pips × 4.0

**Example:** If tp_pips is 100:
- TP1: 150 pips (100 × 1.5)
- TP2: 250 pips (100 × 2.5)
- TP3: 400 pips (100 × 4.0)

## Testing

### Test 1: Save from Dashboard
1. Open dashboard
2. Change TP levels to [2.0, 3.0, 5.0]
3. Save configuration
4. Check `bot_config.json`
5. Should see: `"tp_levels": [2.0, 3.0, 5.0]`
6. Should NOT see: `tp_level_1`, `tp_level_2`, `tp_level_3`

### Test 2: Load in Dashboard
1. Edit `bot_config.json` manually
2. Set `"tp_levels": [1.8, 3.2, 6.0]`
3. Refresh dashboard
4. TP level inputs should show: 1.8, 3.2, 6.0

### Test 3: Bot Reads Correctly
1. Start bot
2. Check logs for TP level values
3. Should use values from `tp_levels` array

## Migration Notes

### If You Have Old Configs

Old configs with individual fields will still work:
- Dashboard will load from individual fields if array doesn't exist
- On next save, dashboard will convert to array format
- Bot always reads from array (with fallback to defaults)

### Manual Migration

If you want to manually migrate:
```bash
python fix_tp_levels_contradiction.py
```

This will:
- Remove obsolete individual fields
- Keep `tp_levels` array
- Create backup of old config

## Summary

✓ **Contradiction resolved** - Only `tp_levels` array remains
✓ **Dashboard updated** - Saves and loads from array
✓ **Config cleaned** - Obsolete fields removed
✓ **Backward compatible** - Old configs still work
✓ **Single source of truth** - No more confusion

---

**Date:** 2026-02-06
**Issue:** Contradictory TP level definitions
**Solution:** Standardized on `tp_levels` array
**Result:** Clean, consistent configuration
