# Proactive Profit Booking Features - Implementation Complete ✅

## Overview
Added time-based exit and break-even features from PROFIT_FIX version to the current bot, with full dashboard configuration support.

---

## New Features Added

### 1. Force Close Position Method ✅
**Method**: `_force_close_position(position)`

**Purpose**: Force-close a position at market price

**Usage**: Called by time-based exit logic

**Implementation**:
```python
def _force_close_position(self, position):
    """
    Force-close a single position at market price.
    Returns True if closed successfully.
    """
    # Gets current price
    # Sends close order
    # Returns success/failure
```

**Location**: `src/mt5_trading_bot.py` (before `manage_positions` method)

---

### 2. Time-Based Exit Logic ✅
**Feature**: Automatically close positions after maximum hold time

**Configuration Parameters**:
- `enable_time_based_exit` (bool) - Enable/disable feature
- `max_hold_minutes` (int) - Maximum minutes to hold position

**Default Values**:
- Enabled: `False` (opt-in feature)
- Max Hold Time: `45 minutes`

**How It Works**:
1. Calculates how long position has been open
2. If hold time >= max_hold_minutes, force closes position
3. Logs reason: "TIME LIMIT" (profit) or "TIME STOP" (loss)

**Example Log**:
```
⏰ TIME LIMIT: Closed XAUUSD after 45min | P&L: 12.50
⏰ TIME STOP: Closed GBPUSD after 45min | P&L: -5.20
```

**Use Cases**:
- Prevent winners from turning into losers
- Implement "trades >30min become losers" rule
- Quick scalping strategies
- Volatile market conditions

---

### 3. Break-Even Stop Logic ✅
**Feature**: Move stop loss to entry price once position is profitable

**Configuration Parameters**:
- `enable_breakeven_stop` (bool) - Enable/disable feature
- `breakeven_atr_threshold` (float) - ATR multiplier to trigger

**Default Values**:
- Enabled: `True` (active by default)
- Threshold: `0.3 ATR`

**How It Works**:
1. Monitors position profit in ATR units
2. Once profit >= threshold (e.g., 0.3 ATR), moves SL to entry + spread
3. Protects against turning winners into losers
4. Only moves SL if new level is better than current

**Example Log**:
```
🔒 BREAK-EVEN: XAUUSD SL moved to entry 2650.50
```

**Benefits**:
- Risk-free trades once triggered
- Locks in minimum profit (spread cost)
- Psychological comfort
- Reduces stress

---

### 4. Configurable Trailing Stop Parameters ✅
**Feature**: Dashboard control over trailing stop behavior

**Configuration Parameters**:
- `trail_activation` (float) - ATR multiplier to activate trailing
- `trail_distance` (float) - ATR multiplier for trail distance

**Default Values**:
- Activation: `1.0 ATR` (balanced)
- Distance: `0.8 ATR` (balanced)

**Comparison with PROFIT_FIX**:
| Parameter | Current Default | PROFIT_FIX | Aggressive |
|-----------|----------------|------------|------------|
| Activation | 1.0 ATR | 0.5 ATR | 0.5 ATR |
| Distance | 0.8 ATR | 0.4 ATR | 0.4 ATR |

**Strategy Profiles**:

**Conservative** (Let winners run):
- Activation: 1.5 ATR
- Distance: 1.0 ATR

**Balanced** (Default):
- Activation: 1.0 ATR
- Distance: 0.8 ATR

**Aggressive** (Lock profits fast):
- Activation: 0.5 ATR
- Distance: 0.4 ATR

---

## Configuration Files Modified

### 1. `src/config.py` ✅
Added constants:
```python
# Trailing Stop Parameters
TRAIL_ACTIVATION_ATR = 1      # Default: 1.0, Aggressive: 0.5
TRAIL_DISTANCE_ATR = 0.8      # Default: 0.8, Tight: 0.4

# Proactive Profit Booking
ENABLE_TIME_BASED_EXIT = False      # Opt-in feature
MAX_HOLD_MINUTES = 45                # Maximum hold time

ENABLE_BREAKEVEN_STOP = True         # Active by default
BREAKEVEN_ATR_THRESHOLD = 0.3        # Trigger at 0.3 ATR profit
```

Added to config dictionary:
```python
'trail_activation': TRAIL_ACTIVATION_ATR,
'trail_distance': TRAIL_DISTANCE_ATR,
'enable_time_based_exit': ENABLE_TIME_BASED_EXIT,
'max_hold_minutes': MAX_HOLD_MINUTES,
'enable_breakeven_stop': ENABLE_BREAKEVEN_STOP,
'breakeven_atr_threshold': BREAKEVEN_ATR_THRESHOLD,
```

### 2. `src/config_manager.py` ✅
Added to default config:
```python
'trail_activation': 1.0,
'trail_distance': 0.8,
'enable_time_based_exit': False,
'max_hold_minutes': 45,
'enable_breakeven_stop': True,
'breakeven_atr_threshold': 0.3,
```

### 3. `web_dashboard.py` ✅
Added validation:
```python
# Validate trailing stop parameters
if 'trail_activation' in new_config:
    trail_activation = new_config.get('trail_activation', 1.0)
    if trail_activation < 0.1 or trail_activation > 5.0:
        return jsonify({'status': 'error', 'message': 'Trail activation must be between 0.1 and 5.0 ATR'})

if 'trail_distance' in new_config:
    trail_distance = new_config.get('trail_distance', 0.8)
    if trail_distance < 0.1 or trail_distance > 3.0:
        return jsonify({'status': 'error', 'message': 'Trail distance must be between 0.1 and 3.0 ATR'})

# Validate time-based exit parameters
if 'max_hold_minutes' in new_config:
    max_hold_minutes = new_config.get('max_hold_minutes', 45)
    if max_hold_minutes < 5 or max_hold_minutes > 480:
        return jsonify({'status': 'error', 'message': 'Max hold time must be between 5 and 480 minutes (8 hours)'})

# Validate breakeven threshold
if 'breakeven_atr_threshold' in new_config:
    be_threshold = float(new_config.get('breakeven_atr_threshold', 0.3))
    if be_threshold < 0.1 or be_threshold > 2.0:
        return jsonify({'status': 'error', 'message': 'Breakeven ATR threshold must be between 0.1 and 2.0'})
```

### 4. `src/mt5_trading_bot.py` ✅
Added method:
- `_force_close_position(position)` - Force close at market price

Modified method:
- `manage_positions()` - Added proactive profit booking section

---

## Dashboard Configuration

### How to Configure (via bot_config.json or Dashboard)

**Example Configuration**:
```json
{
  "trail_activation": 1.0,
  "trail_distance": 0.8,
  "enable_time_based_exit": false,
  "max_hold_minutes": 45,
  "enable_breakeven_stop": true,
  "breakeven_atr_threshold": 0.3
}
```

### Configuration Ranges

| Parameter | Min | Max | Default | Unit |
|-----------|-----|-----|---------|------|
| trail_activation | 0.1 | 5.0 | 1.0 | ATR |
| trail_distance | 0.1 | 3.0 | 0.8 | ATR |
| max_hold_minutes | 5 | 480 | 45 | minutes |
| breakeven_atr_threshold | 0.1 | 2.0 | 0.3 | ATR |

---

## Usage Examples

### Example 1: Conservative Trader
**Goal**: Let winners run, only protect against major reversals

**Configuration**:
```json
{
  "trail_activation": 1.5,
  "trail_distance": 1.0,
  "enable_time_based_exit": false,
  "enable_breakeven_stop": true,
  "breakeven_atr_threshold": 0.5
}
```

**Behavior**:
- Trailing activates at 1.5 ATR profit (larger moves)
- Trails 1.0 ATR behind (loose)
- No time limit
- Break-even at 0.5 ATR (conservative)

### Example 2: Scalper (PROFIT_FIX Style)
**Goal**: Lock profits quickly, don't let winners reverse

**Configuration**:
```json
{
  "trail_activation": 0.5,
  "trail_distance": 0.4,
  "enable_time_based_exit": true,
  "max_hold_minutes": 30,
  "enable_breakeven_stop": true,
  "breakeven_atr_threshold": 0.3
}
```

**Behavior**:
- Trailing activates at 0.5 ATR profit (quick)
- Trails 0.4 ATR behind (tight)
- Force closes after 30 minutes
- Break-even at 0.3 ATR (standard)

### Example 3: Balanced Trader (Default)
**Goal**: Balance between letting winners run and protecting profits

**Configuration**:
```json
{
  "trail_activation": 1.0,
  "trail_distance": 0.8,
  "enable_time_based_exit": false,
  "enable_breakeven_stop": true,
  "breakeven_atr_threshold": 0.3
}
```

**Behavior**:
- Trailing activates at 1.0 ATR profit (balanced)
- Trails 0.8 ATR behind (balanced)
- No time limit
- Break-even at 0.3 ATR (standard)

---

## Testing

### Test Scenarios

**Test 1: Time-Based Exit**
1. Enable time-based exit
2. Set max_hold_minutes to 5 (for testing)
3. Place a trade
4. Wait 5 minutes
5. Verify position is force-closed
6. Check log for "⏰ TIME LIMIT" or "⏰ TIME STOP"

**Test 2: Break-Even Stop**
1. Enable break-even stop
2. Set breakeven_atr_threshold to 0.3
3. Place a trade
4. Wait for position to reach 0.3 ATR profit
5. Verify SL moves to entry price
6. Check log for "🔒 BREAK-EVEN"

**Test 3: Trailing Stop Configuration**
1. Set trail_activation to 0.5
2. Set trail_distance to 0.4
3. Place a trade
4. Wait for 0.5 ATR profit
5. Verify trailing stop activates
6. Verify it trails 0.4 ATR behind

---

## Performance Impact

### Time-Based Exit
**Pros**:
- ✅ Prevents winners from turning into losers
- ✅ Enforces discipline
- ✅ Good for volatile markets
- ✅ Reduces overnight risk

**Cons**:
- ⚠️ May exit winning trades early
- ⚠️ Misses larger trends
- ⚠️ Not suitable for swing trading

**Best For**:
- Scalping (M1, M5)
- Day trading (M15, M30)
- Volatile markets
- News trading

### Break-Even Stop
**Pros**:
- ✅ Risk-free trades once triggered
- ✅ Psychological comfort
- ✅ Protects against reversals
- ✅ No downside

**Cons**:
- ⚠️ May get stopped out at entry
- ⚠️ Misses small pullbacks that continue

**Best For**:
- All trading styles
- All timeframes
- Risk-averse traders

### Tighter Trailing Stops
**Pros**:
- ✅ Locks profits faster
- ✅ Reduces drawdown
- ✅ More consistent results

**Cons**:
- ⚠️ Exits winners early
- ⚠️ Reduces profit potential
- ⚠️ More false exits

**Best For**:
- Ranging markets
- Scalping
- High volatility

---

## Migration from PROFIT_FIX

If you were using PROFIT_FIX and want the same behavior:

**Step 1**: Enable time-based exit
```json
{
  "enable_time_based_exit": true,
  "max_hold_minutes": 45
}
```

**Step 2**: Use aggressive trailing stops
```json
{
  "trail_activation": 0.5,
  "trail_distance": 0.4
}
```

**Step 3**: Keep break-even enabled (default)
```json
{
  "enable_breakeven_stop": true,
  "breakeven_atr_threshold": 0.3
}
```

---

## Troubleshooting

### Issue: Time-based exit not working
**Check**:
1. Is `enable_time_based_exit` set to `true`?
2. Has position been open for >= `max_hold_minutes`?
3. Check logs for "⏰ TIME LIMIT" messages

### Issue: Break-even not triggering
**Check**:
1. Is `enable_breakeven_stop` set to `true`?
2. Has position reached `breakeven_atr_threshold` profit?
3. Is current SL already at or better than entry?
4. Check logs for "🔒 BREAK-EVEN" messages

### Issue: Trailing stops too tight/loose
**Solution**:
- Adjust `trail_activation` (when to start)
- Adjust `trail_distance` (how close to follow)
- Test with different values for your strategy

---

## Summary

✅ **Added** `_force_close_position()` method  
✅ **Added** Time-based exit logic (configurable)  
✅ **Added** Break-even stop logic (configurable)  
✅ **Made** Trailing stop parameters configurable  
✅ **Added** Dashboard validation for all parameters  
✅ **Updated** config.py with new constants  
✅ **Updated** config_manager.py with defaults  
✅ **Updated** web_dashboard.py with validation  

**All features are dashboard-configurable** ✅

**Restart Required**: Yes (to load new code)

---

**Implementation Date**: 2026-02-09  
**Status**: COMPLETE ✅  
**Files Modified**: 4 (mt5_trading_bot.py, config.py, config_manager.py, web_dashboard.py)  
**New Methods**: 1 (_force_close_position)  
**New Parameters**: 6 (trail_activation, trail_distance, enable_time_based_exit, max_hold_minutes, enable_breakeven_stop, breakeven_atr_threshold)
