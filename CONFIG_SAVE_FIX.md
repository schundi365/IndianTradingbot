# Configuration Save 400 Error - Fix Applied

## Problem

When trying to save configuration, getting:
```
Failed to load resource: the server responded with a status of 400 (BAD REQUEST)
```

## Root Cause

Found a bug in the validation function - it was using the wrong validator for the broker field:

```python
# WRONG - was using validate_strategy for broker
is_valid, error = validate_strategy(config.get('broker', ''))

# CORRECT - should use validate_broker_type
is_valid, error = validate_broker_type(config.get('broker', ''))
```

## Fixes Applied

### 1. Fixed Broker Validation Bug
**File**: `indian_dashboard/api/config.py`
- Line 403: Changed from `validate_strategy` to `validate_broker_type`
- This was causing broker validation to fail incorrectly

### 2. Added Detailed Logging
**File**: `indian_dashboard/api/config.py`
- Added logging of configuration being saved
- Added logging of validation errors
- Will help diagnose any remaining issues

## How to Test

1. Restart dashboard:
   ```powershell
   .\restart_dashboard.ps1
   ```

2. Clear browser cache or use incognito mode

3. Try to save configuration again

4. If still getting 400 error, check the dashboard logs:
   - Look for "Saving configuration:" message (shows what's being sent)
   - Look for "Configuration validation failed:" message (shows what's wrong)

5. Share the log output if error persists

## What the Logs Will Show

### Success Case:
```
INFO - Saving configuration: {
  "broker": "paper",
  "instruments": [...],
  "strategy": "breakout",
  "timeframe": "15min",
  ...
}
INFO - Current configuration saved
```

### Error Case:
```
INFO - Saving configuration: {...}
ERROR - Configuration validation failed: ['broker: Invalid broker type', 'timeframe: Invalid timeframe']
```

The error details will tell us exactly what field is failing validation and why.

## Common Validation Issues

1. **Broker**: Must be one of: 'kite', 'paper', 'zerodha'
2. **Instruments**: Must be a non-empty array
3. **Strategy**: Must be one of: 'breakout', 'mean_reversion', 'trend_following', 'scalping', 'momentum'
4. **Timeframe**: Must be one of: '1min', '5min', '15min', '30min', '1hour', '1day'

## Next Steps

After restarting, try to save again and check:
1. Does it work now?
2. If not, what do the logs say?
3. Share the log output for further diagnosis

---

**Status**: ✅ Bug fixed, logging added - restart and test
