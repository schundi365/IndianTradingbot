# Fix: IPC Send Failed Error

## Error
```
ERROR - Failed to get data for XAGUSD after 3 attempts. Error: (-10001, 'IPC send failed')
```

## What It Means
The bot lost communication with MetaTrader 5 terminal. This is a connection issue, not a code bug.

---

## Causes

### 1. MT5 Terminal Closed/Crashed
Most common cause - MT5 terminal was closed or crashed.

### 2. MT5 Overloaded
Too many rapid requests (M1 with 10-second updates = 6 requests/minute × 3 symbols = 18 requests/minute).

### 3. MT5 Busy
MT5 is processing other operations (manual trades, updates, etc.).

### 4. Network Issue
Connection between bot and MT5 terminal interrupted.

---

## Quick Fixes

### Fix 1: Restart MT5 Terminal ⭐ (Most Effective)
1. Close MetaTrader 5 completely
2. Reopen MetaTrader 5
3. Wait for it to fully load
4. Restart the bot

### Fix 2: Check MT5 is Running
- Make sure MT5 terminal is open and logged in
- Check MT5 is not frozen (try clicking around)
- Verify you can see live prices in MT5

### Fix 3: Reduce Bot Update Frequency
The bot now checks every 15 seconds instead of 10 (less load on MT5).

---

## Changes Applied

### 1. Increased Update Interval
```python
# Before
UPDATE_INTERVAL = 10  # Too aggressive for M1

# After
UPDATE_INTERVAL = 15  # Reduced load on MT5
```

### 2. Auto-Reconnect on IPC Error
```python
# New behavior:
if error_code == -10001:  # IPC error
    - Shutdown MT5 connection
    - Wait 2 seconds
    - Reinitialize MT5
    - Retry request
```

### 3. Longer Retry Delays
```python
# Before
time.sleep(1)  # 1 second between retries

# After
time.sleep(2)  # 2 seconds between retries
```

---

## Prevention

### Best Practices
1. **Keep MT5 open** - Don't close MT5 while bot is running
2. **Don't overload MT5** - Avoid manual trading while bot is active
3. **Stable connection** - Use wired internet if possible
4. **Restart MT5 daily** - Fresh start prevents memory issues

### If Error Persists
1. **Increase update interval** to 20-30 seconds
2. **Reduce symbols** - Trade only XAUUSD (remove GBPUSD, XAGUSD)
3. **Switch to M5** - Less data requests than M1
4. **Check MT5 logs** - Look for errors in MT5 terminal

---

## Manual Restart Steps

### When You See IPC Error:

1. **Stop the bot**
   ```
   Press Ctrl+C in terminal
   ```

2. **Close MT5**
   - Right-click MT5 in taskbar
   - Click "Close window"

3. **Wait 5 seconds**
   - Let MT5 fully close

4. **Reopen MT5**
   - Launch MetaTrader 5
   - Wait for login and data load

5. **Restart bot**
   ```bash
   python run_bot.py
   ```

---

## Advanced Solutions

### If Error Happens Frequently

#### Option 1: Reduce Symbols
```python
# Trade only gold (most liquid)
SYMBOLS = ['XAUUSD']  # Remove GBPUSD, XAGUSD
```

#### Option 2: Increase Update Interval
```python
UPDATE_INTERVAL = 20  # Or even 30 seconds
```

#### Option 3: Switch to M5 Timeframe
```python
TIMEFRAME = mt5.TIMEFRAME_M5  # Less data requests
```

#### Option 4: Reduce Historical Bars
In `get_historical_data()`:
```python
bars=100  # Instead of 200 (less data to fetch)
```

---

## Monitoring

### Check MT5 Health
- **CPU usage**: Should be < 50%
- **Memory**: Should be < 500MB
- **Response time**: MT5 should respond instantly to clicks

### Check Bot Logs
Look for patterns:
```
# Good
INFO - Successfully fetched data for XAUUSD

# Warning (occasional is OK)
WARNING - Failed to get data for XAGUSD (attempt 1/3), retrying...

# Bad (frequent)
ERROR - Failed to get data after 3 attempts
```

---

## Status
✅ **AUTO-RECONNECT ADDED**  
✅ **UPDATE INTERVAL INCREASED (10s → 15s)**  
✅ **RETRY DELAY INCREASED (1s → 2s)**  
⚠️ **RESTART MT5 IF ERROR PERSISTS**

---

## Quick Reference

| Error | Solution |
|-------|----------|
| IPC send failed | Restart MT5 terminal |
| Frequent IPC errors | Increase UPDATE_INTERVAL to 20-30s |
| MT5 frozen | Close and reopen MT5 |
| Bot can't connect | Check MT5 is running and logged in |
| Slow performance | Reduce symbols or switch to M5 |

---

## Next Steps

1. **Restart MT5 now** (most important!)
2. **Restart the bot** (to apply 15s update interval)
3. **Monitor for 30 minutes** (check if error repeats)
4. **If error persists**: Increase UPDATE_INTERVAL to 20s

The bot will now automatically try to reconnect when IPC errors occur.
