# Symbols Field Conversion Fix

## Problem
```
Error starting bot: 'symbols'
```

The bot was looking for a `symbols` field but the dashboard sends `instruments`.

## Root Cause

**Bot expects** (`src/indian_trading_bot.py`):
```python
self.symbols = config['symbols']  # List of symbol strings: ["RELIANCE", "TCS", ...]
```

**Dashboard sends** (`config-form.js`):
```javascript
data.instruments = [
    {symbol: "RELIANCE", exchange: "NSE", token: 123, ...},
    {symbol: "TCS", exchange: "NSE", token: 456, ...}
]
```

## Fix Applied

**File**: `indian_dashboard/api/bot.py`

Added conversion logic in the `start_bot()` endpoint:

```python
# Convert instruments to symbols format expected by bot
if 'instruments' in config and 'symbols' not in config:
    instruments = config['instruments']
    if isinstance(instruments, list) and len(instruments) > 0:
        # Extract symbol from each instrument object
        # Instruments have format: {symbol: "RELIANCE", exchange: "NSE", ...}
        # Bot expects: ["RELIANCE", "TCS", ...]
        config['symbols'] = [inst.get('symbol', inst.get('tradingsymbol', '')) for inst in instruments if isinstance(inst, dict)]
        # Filter out empty strings
        config['symbols'] = [s for s in config['symbols'] if s]
    else:
        config['symbols'] = []
```

## How It Works

1. Dashboard sends configuration with `instruments` array
2. Start bot endpoint checks if `instruments` exists and `symbols` doesn't
3. Extracts `symbol` field from each instrument object
4. Creates `symbols` array with just the symbol strings
5. Bot receives config with `symbols` field and starts successfully

## Example Conversion

**Input** (from dashboard):
```json
{
  "instruments": [
    {"symbol": "RELIANCE", "exchange": "NSE", "token": 738561},
    {"symbol": "TCS", "exchange": "NSE", "token": 2953217}
  ]
}
```

**Output** (to bot):
```json
{
  "instruments": [...],
  "symbols": ["RELIANCE", "TCS"]
}
```

## Next Steps

1. Restart dashboard: `.\restart_dashboard.ps1`
2. Try starting the bot again
3. Should work now!

---

**Status**: ✅ Fixed - restart and test
