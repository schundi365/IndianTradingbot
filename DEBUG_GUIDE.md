# Debug Guide - Troubleshooting MT5 Connection & Trading Issues

**Quick Start**: Run `python enable_debug_logging.py` to enable detailed logging

---

## Step 1: Enable Debug Logging

### Method 1: Run Debug Script (Recommended)

```bash
python enable_debug_logging.py
```

This will:
- Test MT5 connection
- Show detailed connection info
- Enable debug logging
- Create `logs/debug.log` file

### Method 2: Manual Configuration

Edit `web_dashboard.py` or `src/mt5_trading_bot.py`:

```python
# Change this line:
logging.basicConfig(level=logging.INFO, ...)

# To this:
logging.basicConfig(level=logging.DEBUG, ...)
```

---

## Step 2: Check MT5 Connection

### Test MT5 Connection

```bash
python enable_debug_logging.py
```

**Expected Output**:
```
Step 1: Attempting MT5 initialization...
✓ MT5 initialized successfully

Step 2: MT5 Version Information
   Version: (5, 0, 4415, 0)

Step 3: Terminal Information
   Build: 5549
   Company: MetaQuotes Software Corp.
   Connected: True
   Trade allowed: True

Step 4: Account Information
   Login: 12345678
   Server: Demo-Server
   Balance: 10000.00
   Trade allowed: True
   Trade expert: True

Step 5: Testing Symbol Access
   ✓ XAUUSD: Available (spread: 25)
   ✓ EURUSD: Available (spread: 2)
   ✓ GBPUSD: Available (spread: 3)

Step 6: Testing Data Retrieval
   ✓ Successfully retrieved 10 bars of XAUUSD M30 data
   Latest close: 2650.45

✅ MT5 CONNECTION TEST COMPLETE
```

### Common Connection Issues

#### Issue 1: "MT5 initialization failed"

**Possible Causes**:
1. MT5 not running
2. Not logged into account
3. Algo trading disabled

**Solutions**:
```
1. Open MetaTrader 5
2. Login to your account
3. Tools > Options > Expert Advisors
4. Check "Allow algorithmic trading"
5. Click OK
6. Restart bot
```

#### Issue 2: "Cannot get account info"

**Possible Causes**:
1. Not logged in
2. Connection lost
3. Server issues

**Solutions**:
```
1. Check MT5 shows "Connected" in bottom right
2. Try logging out and back in
3. Check internet connection
4. Try different server if available
```

#### Issue 3: "Symbol not available"

**Possible Causes**:
1. Symbol not offered by broker
2. Symbol name different
3. Market closed

**Solutions**:
```
1. Check symbol in MT5 Market Watch
2. Right-click Market Watch > Show All
3. Find correct symbol name
4. Update bot configuration with correct name
```

---

## Step 3: Check Bot Logs

### Where to Find Logs

1. **Main Log**: `trading_bot.log`
2. **Debug Log**: `logs/debug.log` (if debug enabled)
3. **Dashboard**: System Logs tab

### What to Look For

#### Good Logs (Bot Working)

```
2026-01-29 10:00:00 - INFO - MT5 initialized successfully
2026-01-29 10:00:00 - INFO - MT5 build: 5549
2026-01-29 10:00:00 - INFO - Account balance: 10000.00
2026-01-29 10:00:00 - INFO - Trading bot started
2026-01-29 10:00:00 - INFO - Configuration loaded: Symbols=['XAUUSD', 'EURUSD']
2026-01-29 10:00:05 - DEBUG - ============================================================
2026-01-29 10:00:05 - DEBUG - ANALYZING XAUUSD
2026-01-29 10:00:05 - DEBUG - ============================================================
2026-01-29 10:00:05 - DEBUG - Fetching historical data for XAUUSD...
2026-01-29 10:00:05 - DEBUG - Calculating indicators for XAUUSD...
2026-01-29 10:00:05 - DEBUG - Checking entry signals for XAUUSD...
2026-01-29 10:00:05 - DEBUG - Signal Check - Close: 2650.45, Fast MA: 2648.20, Slow MA: 2645.10
2026-01-29 10:00:05 - DEBUG - No signal: Price=2650.45, Fast MA=2648.20, Slow MA=2645.10
2026-01-29 10:00:05 - DEBUG - No entry signal for XAUUSD
```

#### Bad Logs (Connection Issues)

```
2026-01-29 10:00:00 - ERROR - MT5 initialization failed: (1, 'Terminal not found')
2026-01-29 10:00:00 - ERROR - Failed to connect to MT5
2026-01-29 10:00:00 - ERROR - Bot stopped
```

**Solution**: MT5 not running or not found

```
2026-01-29 10:00:00 - INFO - MT5 initialized successfully
2026-01-29 10:00:05 - ERROR - Failed to get data for XAUUSD after 3 attempts
```

**Solution**: Symbol not available or connection lost

---

## Step 4: Understand Why No Trades

### Enable Detailed Signal Logging

With debug logging enabled, you'll see:

```
2026-01-29 10:00:05 - DEBUG - ANALYZING XAUUSD
2026-01-29 10:00:05 - DEBUG - Fetching historical data for XAUUSD...
2026-01-29 10:00:05 - DEBUG - Calculating indicators for XAUUSD...
2026-01-29 10:00:05 - DEBUG - Checking entry signals for XAUUSD...
2026-01-29 10:00:05 - DEBUG - Signal Check - Close: 2650.45, Fast MA: 2648.20, Slow MA: 2645.10
2026-01-29 10:00:05 - INFO - ✓ Bullish MA crossover detected
2026-01-29 10:00:05 - INFO -   ✗ RSI filter: Too overbought (RSI: 78.5) - TRADE REJECTED
2026-01-29 10:00:05 - DEBUG - No entry signal for XAUUSD
```

This shows:
- ✓ Signal was detected (MA crossover)
- ✗ But rejected by RSI filter (too overbought)

### Common Rejection Reasons

#### 1. RSI Filter

```
✗ RSI filter: Too overbought (RSI: 78.5) - TRADE REJECTED
```

**Meaning**: Price is too high (overbought)  
**Solution**: Wait for RSI to drop below 70, or disable RSI filter

#### 2. MACD Filter

```
✗ MACD filter: Histogram not positive (-0.000123) - TRADE REJECTED
```

**Meaning**: Momentum not confirming signal  
**Solution**: Wait for MACD to turn positive, or disable MACD filter

#### 3. Volume Filter

```
✗ Trade REJECTED by volume filter for XAUUSD
```

**Meaning**: Volume too low (below 1.2x average)  
**Solution**: Wait for higher volume, or disable volume filter

#### 4. Confidence Too Low

```
Trade confidence: 45% (Min required: 60%) - TRADE REJECTED
```

**Meaning**: Overall confidence below threshold  
**Solution**: Lower min confidence to 40-50%

---

## Step 5: Diagnostic Commands

### Check MT5 Status

```bash
python -c "import MetaTrader5 as mt5; print('Init:', mt5.initialize()); info = mt5.terminal_info(); print('Build:', info.build if info else 'N/A'); print('Connected:', info.connected if info else False); mt5.shutdown()"
```

### Check Symbol Availability

```bash
python -c "import MetaTrader5 as mt5; mt5.initialize(); symbols = ['XAUUSD', 'EURUSD', 'GBPUSD']; [print(f'{s}: {\"OK\" if mt5.symbol_info(s) else \"NOT FOUND\"}') for s in symbols]; mt5.shutdown()"
```

### Check Data Retrieval

```bash
python -c "import MetaTrader5 as mt5; mt5.initialize(); rates = mt5.copy_rates_from_pos('XAUUSD', mt5.TIMEFRAME_M30, 0, 10); print(f'Bars: {len(rates) if rates else 0}'); mt5.shutdown()"
```

### Check Configuration

```bash
python -c "from src.config_manager import get_config; c = get_config(); print('Symbols:', c['symbols']); print('Timeframe:', c['timeframe']); print('Risk:', c['risk_percent']); print('Confidence:', c['min_confidence'])"
```

---

## Step 6: Common Issues & Solutions

### Issue: Bot Says Running But No Analysis

**Check Logs For**:
```
Trading bot started
Configuration loaded: Symbols=[...]
```

**If Missing**:
- Bot didn't start properly
- Check for errors in logs
- Restart bot

**If Present But No Analysis**:
- Check update interval (default 60 seconds)
- Wait 1-2 minutes
- Check for error messages

### Issue: Analysis Running But No Signals

**Check Logs For**:
```
ANALYZING XAUUSD
Fetching historical data...
Calculating indicators...
Checking entry signals...
No signal: Price=X, Fast MA=Y, Slow MA=Z
```

**This Means**:
- Bot is working correctly
- No MA crossover detected
- Waiting for signal

**To Get Signals Faster**:
1. Lower confidence threshold
2. Add more symbols
3. Use shorter timeframe (M5)

### Issue: Signals Detected But Rejected

**Check Logs For**:
```
✓ Bullish MA crossover detected
✗ RSI filter: Too overbought (RSI: 78.5) - TRADE REJECTED
```

**This Means**:
- Bot found signal
- But filters rejected it
- This is normal and expected

**To Pass Filters**:
1. Disable strict filters
2. Adjust filter thresholds
3. Wait for better conditions

### Issue: All Filters Pass But No Trade

**Check Logs For**:
```
✓ Bullish MA crossover detected
✓ RSI filter: OK (RSI: 55.2)
✓ MACD filter: Confirmed
✓ Volume analysis passed
Trade confidence: 45% (Min required: 60%) - TRADE REJECTED
```

**This Means**:
- Signal and filters OK
- But confidence too low

**Solution**:
```
Dashboard > Configuration > Min Trade Confidence > 40%
```

---

## Step 7: Enable Maximum Debug Output

### For Developers

Edit `src/mt5_trading_bot.py`:

```python
# Add at top of file
import logging
logging.getLogger().setLevel(logging.DEBUG)

# In run_strategy method, add:
logging.debug(f"Latest candle: {df.iloc[-1].to_dict()}")
logging.debug(f"Indicators: RSI={latest['rsi']:.2f}, MACD={latest['macd']:.6f}")
logging.debug(f"Volume: {latest['tick_volume']}, MA: {df['tick_volume'].rolling(20).mean().iloc[-1]:.0f}")
```

### For Users

Just run:
```bash
python enable_debug_logging.py
```

Then start bot and check `logs/debug.log`

---

## Step 8: Log Analysis Checklist

### Connection Issues

- [ ] "MT5 initialized successfully" in logs?
- [ ] "MT5 build: XXXX" shown?
- [ ] "Account balance: XXXX" shown?
- [ ] "Trading bot started" shown?

### Configuration Issues

- [ ] "Configuration loaded: Symbols=[...]" shown?
- [ ] Correct symbols listed?
- [ ] Correct timeframe shown?
- [ ] Correct risk percentage?

### Analysis Issues

- [ ] "ANALYZING [SYMBOL]" appearing every 60 seconds?
- [ ] "Fetching historical data" shown?
- [ ] "Calculating indicators" shown?
- [ ] "Checking entry signals" shown?

### Signal Issues

- [ ] "Bullish/Bearish MA crossover detected" appearing?
- [ ] "RSI filter: OK" or "REJECTED" shown?
- [ ] "MACD filter: Confirmed" or "REJECTED" shown?
- [ ] "Volume analysis passed" or "REJECTED" shown?

---

## Step 9: Get Help

### Information to Provide

When asking for help, include:

1. **Last 50 lines of log**:
   ```bash
   tail -n 50 trading_bot.log
   ```

2. **MT5 connection test output**:
   ```bash
   python enable_debug_logging.py
   ```

3. **Configuration**:
   ```bash
   python -c "from src.config_manager import get_config; import json; print(json.dumps(get_config(), indent=2))"
   ```

4. **System info**:
   - Windows version
   - MT5 build number
   - Bot version

---

## Quick Reference

### Enable Debug Logging
```bash
python enable_debug_logging.py
```

### Check Logs
```bash
# Last 50 lines
tail -n 50 trading_bot.log

# Last 100 lines
tail -n 100 logs/debug.log

# Follow live
tail -f trading_bot.log
```

### Test MT5
```bash
python enable_debug_logging.py
```

### Check Config
```bash
python -c "from src.config_manager import get_config; c = get_config(); print('Symbols:', c['symbols']); print('Confidence:', c['min_confidence'])"
```

---

**Remember**: Most "no trades" issues are normal bot behavior (being selective). Use debug logging to understand exactly why trades are rejected.
