# Analysis Bars Issue - Final Status

## Issue Report
**User**: Changed `analysis_bars` to 100 in web dashboard, but logs still show 200 bars being fetched  
**Date**: 2026-02-09  
**Status**: ✅ **FIXED - Restart Required**

---

## Root Cause Analysis

### The Problem
The bot was **always fetching 200 bars** regardless of dashboard settings because:

1. ❌ `config.py` didn't define `ANALYSIS_BARS` constant
2. ❌ `config.py` didn't include `analysis_bars` in config dictionary  
3. ❌ Bot's `__init__` didn't read `analysis_bars` from config
4. ❌ `run_strategy` called `get_historical_data()` without bars parameter

This caused the method to use its hardcoded default: `bars=200`

### Code Flow (Before Fix)
```
Dashboard Setting (100)
    ↓
bot_config.json (100) ✅
    ↓
Bot.__init__ (ignored) ❌
    ↓
run_strategy() (no parameter) ❌
    ↓
get_historical_data(bars=200) ← HARDCODED DEFAULT
```

---

## What Was Fixed

### 1. `src/config.py`
```python
# Added constant definition
ANALYSIS_BARS = 200

# Added to config dictionary
def get_config():
    return {
        ...
        'analysis_bars': ANALYSIS_BARS,
        ...
    }
```

### 2. `src/config_manager.py`
```python
def _get_default_config(self):
    return {
        ...
        'analysis_bars': 200,
        ...
    }
```

### 3. `src/mt5_trading_bot.py` - `__init__` method
```python
# Added to __init__
self.analysis_bars = config.get('analysis_bars', 200)
```

### 4. `src/mt5_trading_bot.py` - `run_strategy` method
```python
# OLD CODE:
logging.info(f"📈 Fetching historical data for {symbol}...")
df = self.get_historical_data(symbol, self.timeframe)  # ❌ No bars param
logging.info(f"✅ Retrieved {len(df)} bars of data")

# NEW CODE:
logging.info(f"📈 Fetching historical data for {symbol}...")
logging.info(f"   Requesting {self.analysis_bars} bars for analysis")  # ✅ NEW
df = self.get_historical_data(symbol, self.timeframe, self.analysis_bars)  # ✅ FIXED
logging.info(f"✅ Retrieved {len(df)} bars of data (requested: {self.analysis_bars})")  # ✅ IMPROVED
```

---

## Verification Results

### Code Verification ✅
```bash
python verify_analysis_bars_fix.py
```

**Results:**
- ✅ config.py has ANALYSIS_BARS defined (200)
- ✅ config_manager.py has analysis_bars in defaults (200)
- ✅ Bot reads analysis_bars from config correctly
- ✅ bot_config.json has analysis_bars (100)

### Fresh Import Test ✅
```bash
python check_loaded_code.py
```

**Results:**
- ✅ Bot HAS analysis_bars attribute (value: 123 test value)
- ✅ Bot is using UPDATED code (reads from config)
- ✅ run_strategy method has UPDATED logging
- ✅ Contains: 'Requesting {self.analysis_bars} bars'

### Current Dashboard Status ⚠️
**Issue**: Dashboard process has old code cached in memory

**Evidence**: Logs still show old format:
```
📈 Fetching historical data for GBPAUD (Timeframe: M15)...
✅ Retrieved 200 bars of data
```

**Reason**: Python module cache - Stop/Start bot doesn't reload code

---

## Solution Required

### ⚠️ DASHBOARD RESTART NEEDED

The code is fixed, but the running dashboard has old code in memory.

**Steps:**
1. **Stop Dashboard**: Press Ctrl+C in dashboard terminal
2. **Close Terminal**: Close the window completely
3. **Wait**: 5-10 seconds for Python to exit
4. **Start Fresh**: Open new terminal, run `python web_dashboard.py`
5. **Start Bot**: Open browser, click "Start Bot"
6. **Verify**: Check logs for new format

---

## Expected Behavior After Restart

### Before Fix (Current)
```
📈 Fetching historical data for GBPAUD (Timeframe: M15)...
✅ Retrieved 200 bars of data
```
- No "Requesting" line
- Always shows 200 (hardcoded)
- Ignores dashboard setting

### After Fix (After Restart)
```
📈 Fetching historical data for GBPAUD (Timeframe: M30)...
   Requesting 100 bars for analysis
✅ Retrieved 100 bars of data (requested: 100)
```
- Shows "Requesting X bars" line
- Uses dashboard setting (100)
- Shows requested vs retrieved

---

## Configuration Details

### Current Settings
- **bot_config.json**: `"analysis_bars": 100`
- **config.py default**: `ANALYSIS_BARS = 200`
- **Bot will use**: 100 (from bot_config.json)

### How to Change
1. **Via Dashboard** (Recommended):
   - Configuration tab → Analysis Bars field
   - Set value (50-1000)
   - Click "Save Configuration"
   - Restart bot

2. **Via bot_config.json**:
   ```json
   {
     "analysis_bars": 150
   }
   ```
   - Restart bot

3. **Via config.py** (Default only):
   ```python
   ANALYSIS_BARS = 200
   ```
   - Affects new installations only

---

## Performance Impact

### Fewer Bars (50-100)
- ✅ Faster data fetching
- ✅ Less memory usage
- ✅ Quicker calculations
- ⚠️ Less historical context

### More Bars (200-500)
- ✅ Better trend detection
- ✅ More reliable indicators
- ⚠️ Slower fetching
- ⚠️ More memory

### Recommended by Timeframe
- **M1-M5**: 100-150 bars
- **M15-M30**: 150-200 bars ← Your current timeframe
- **H1-H4**: 200-300 bars
- **D1**: 300-500 bars

---

## Troubleshooting

### If logs still show 200 after restart:

1. **Verify bot_config.json**:
   ```bash
   type bot_config.json | findstr analysis_bars
   ```
   Should show: `"analysis_bars": 100`

2. **Check for multiple Python processes**:
   - Task Manager → Find all python.exe
   - End all processes
   - Wait 10 seconds
   - Start dashboard fresh

3. **Force config reload**:
   - Stop bot
   - Delete `bot_config.json`
   - Set analysis_bars in dashboard
   - Save configuration
   - Start bot

4. **Verify code is loaded**:
   ```bash
   python check_loaded_code.py
   ```
   Should show: "✅ UPDATED CODE IS LOADED"

---

## Technical Details

### Method Signature
```python
def get_historical_data(self, symbol, timeframe, bars=200):
    """
    Fetch historical price data from MT5
    
    Args:
        symbol (str): Trading symbol
        timeframe: MT5 timeframe constant
        bars (int): Number of bars to fetch (default: 200)
    
    Returns:
        pd.DataFrame: Historical price data
    """
```

### Call Chain
```
run_strategy()
    ↓
get_historical_data(symbol, self.timeframe, self.analysis_bars)
    ↓
mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
    ↓
Returns DataFrame with 'bars' rows
```

### Configuration Priority
```
1. bot_config.json (highest - user settings)
2. config.py constants (defaults)
3. Method defaults (fallback)
```

---

## Summary

| Item | Status |
|------|--------|
| Code Fixed | ✅ Complete |
| Tests Passing | ✅ All pass |
| Fresh Import | ✅ Works correctly |
| Dashboard Running | ⚠️ Has old code cached |
| **Action Required** | **Restart Dashboard** |

---

## Files Modified

1. `src/config.py` - Added ANALYSIS_BARS constant and config entry
2. `src/config_manager.py` - Added analysis_bars to defaults
3. `src/mt5_trading_bot.py` - Added self.analysis_bars and updated logging

## Files Created

1. `verify_analysis_bars_fix.py` - Verification script
2. `check_loaded_code.py` - Check what code is loaded
3. `force_restart_dashboard.py` - Helper to restart dashboard
4. `RESTART_DASHBOARD_NOW.txt` - User instructions
5. `ANALYSIS_BARS_FIX_COMPLETE.md` - Detailed documentation
6. `ANALYSIS_BARS_FINAL_STATUS.md` - This file

---

**Fix Date**: 2026-02-09  
**Issue**: Analysis bars always 200 regardless of dashboard setting  
**Root Cause**: Config not read, parameter not passed  
**Status**: ✅ FIXED - Dashboard restart required  
**Next Action**: Restart dashboard to load updated code
