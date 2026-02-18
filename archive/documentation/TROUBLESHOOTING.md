# Troubleshooting Guide

Common issues and solutions for MT5 Trading Bot.

## Error: "Terminal: Authorization failed" (Error -6)

### Problem
MT5 is not logged into a trading account.

### Solution

**Step 1: Make sure MT5 is running**
- Open MetaTrader 5 application
- You should see the MT5 window

**Step 2: Login to an account**

If you have an account:
1. In MT5, go to **File → Login to Trade Account**
2. Enter your:
   - Login (account number)
   - Password
   - Server (e.g., "MetaQuotes-Demo")
3. Click **Login**
4. You should see your account balance in the bottom-left corner

If you DON'T have an account (Create Demo):
1. In MT5, go to **File → Open an Account**
2. Choose a broker (e.g., **MetaQuotes-Demo**)
3. Click **Next**
4. Select **Open a demo account**
5. Fill in the registration form:
   - Name
   - Email
   - Phone (optional)
   - Account type (Standard)
   - Deposit (e.g., $10,000)
   - Leverage (e.g., 1:100)
6. Click **Next**
7. You'll receive:
   - Login number
   - Password
   - Server name
8. Save these credentials!
9. MT5 will automatically log you in

**Step 3: Verify connection**
- Check bottom-right corner of MT5
- Should show connection speed (e.g., "1234/567 ms")
- Should NOT show "No connection"

**Step 4: Test again**
```bash
python test_mt5_simple.py
```

You should see: `✅ Account connected!`

---

## Error: "MT5 terminal not found" (Error -2)

### Problem
MetaTrader 5 is not installed or not running.

### Solution

**Step 1: Install MT5**
1. Download from: https://www.metatrader5.com/en/download
2. Run the installer
3. Follow installation wizard
4. Launch MT5

**Step 2: Make sure MT5 is running**
- You should see MT5 window open
- Check Windows taskbar for MT5 icon

**Step 3: Test again**
```bash
python test_mt5_simple.py
```

---

## Error: "Symbol XAUUSD not found"

### Problem
Your broker doesn't offer Gold with symbol name "XAUUSD".

### Solution

**Step 1: Check available symbols**
1. In MT5, press **Ctrl+U** (or View → Symbols)
2. Search for "gold" or "XAU"
3. Note the exact symbol name (might be "GOLD", "XAUUSD.a", etc.)

**Step 2: Update configuration**
Edit `src/config.py`:
```python
# Change this:
SYMBOLS = ['XAUUSD', 'XAGUSD']

# To your broker's symbol names:
SYMBOLS = ['GOLD', 'SILVER']  # Example
```

**Step 3: Enable symbol in Market Watch**
1. In MT5, right-click in Market Watch
2. Select **Show All**
3. Find your symbol
4. Right-click → **Show**

---

## Error: "Not enough money" / "Invalid volume"

### Problem
Position size is too large for your account or broker's limits.

### Solution

**Step 1: Check broker's lot size limits**
1. In MT5, right-click on symbol → **Specification**
2. Note:
   - Minimal volume (e.g., 0.01)
   - Maximal volume (e.g., 100.00)
   - Volume step (e.g., 0.01)

**Step 2: Reduce risk in configuration**
Edit `src/config.py`:
```python
# Reduce risk percentage
RISK_PERCENT = 0.5  # From 1.0 to 0.5

# Set minimum lot size
MIN_LOT_SIZE = 0.01  # Match broker's minimum

# Set maximum lot size
MAX_LOT_SIZE = 0.1  # Start small
```

**Step 3: Check account balance**
- Make sure you have sufficient balance
- Demo accounts usually start with $10,000
- Don't risk more than 1% per trade

---

## Error: "Trade is disabled"

### Problem
Algorithmic trading is not enabled in MT5.

### Solution

**Step 1: Enable algo trading**
1. In MT5, go to **Tools → Options**
2. Click **Expert Advisors** tab
3. Check these boxes:
   - ✅ Allow algorithmic trading
   - ✅ Allow DLL imports
   - ✅ Allow WebRequest for listed URL (optional)
4. Click **OK**

**Step 2: Check if trading is allowed**
- Look at top-right corner of MT5
- Should show green "AutoTrading" button
- If red, click it to enable

**Step 3: Test again**

---

## Bot doesn't place trades

### Possible Causes & Solutions

**1. No signals generated**
- Check log file: `trading_bot.log`
- Look for "Signal detected" messages
- If no signals, market conditions may not meet criteria

**2. Safety limits reached**
- Check if daily loss limit hit
- Check if max trades per day reached
- Review safety settings in `src/config.py`

**3. Trade filtering**
- Adaptive risk may be rejecting low-confidence trades
- Check log for "Trade rejected" messages
- Lower `MIN_TRADE_CONFIDENCE` if needed:
```python
MIN_TRADE_CONFIDENCE = 0.50  # From 0.60 to 0.50
```

**4. Wrong timeframe**
- Make sure enough bars are available
- H1 timeframe needs at least 50 bars of history
- Wait for market to be open

**5. Market closed**
- Gold/Silver markets have trading hours
- Check if market is currently open
- Enable trading hours filter if needed

---

## Bot places trades but they close immediately

### Problem
Stop loss or take profit is too close to entry price.

### Solution

**Step 1: Check broker's stop level**
1. In MT5, right-click symbol → **Specification**
2. Note "Stops level" (e.g., 10 points)
3. SL/TP must be at least this far from entry

**Step 2: Increase ATR multiplier**
Edit `src/config.py`:
```python
# Increase stop loss distance
ATR_MULTIPLIER_SL = 3.0  # From 2.0 to 3.0
```

---

## Trailing stop not working

### Problem
Profit hasn't reached activation threshold.

### Solution

**Step 1: Check activation threshold**
Default is 1.5× ATR profit before trailing activates.

**Step 2: Lower activation threshold**
Edit `src/config.py`:
```python
# Activate trailing sooner
TRAIL_ACTIVATION_ATR = 1.0  # From 1.5 to 1.0
```

**Step 3: Check logs**
Look for "Trailing stop activated" in `trading_bot.log`

---

## High CPU usage

### Problem
Bot is checking too frequently.

### Solution

Edit `src/config.py`:
```python
# Increase update interval
UPDATE_INTERVAL = 300  # Check every 5 minutes instead of 1
```

---

## Bot crashes or freezes

### Possible Causes & Solutions

**1. MT5 connection lost**
- Check MT5 is still running
- Check internet connection
- Restart MT5 and bot

**2. Memory issues**
- Close other applications
- Restart bot periodically
- Check log file size

**3. Code error**
- Check `trading_bot.log` for error messages
- Report bug on GitHub with log excerpt

---

## Performance is poor

### Not a Bug - Strategy Optimization Needed

**1. Test on demo first**
- Run for at least 2 weeks
- Track win rate and profit factor
- Adjust parameters based on results

**2. Optimize parameters**
- Try different MA periods
- Adjust ATR multiplier
- Test different timeframes

**3. Market conditions**
- Strategy works best in trending markets
- May underperform in ranging markets
- Consider adding filters

**4. Review adaptive risk settings**
- Check if confidence threshold is too high
- Review market condition analysis
- Adjust multipliers if needed

---

## Getting Help

### Before Asking for Help

1. **Check logs**: `trading_bot.log`
2. **Run tests**: `python test_mt5_simple.py`
3. **Verify setup**: `python validate_setup.py`
4. **Read documentation**: `docs/README.md`

### When Reporting Issues

Include:
- Error message (exact text)
- Log file excerpt
- Your configuration (relevant parts)
- MT5 version
- Python version
- Operating system
- Steps to reproduce

### Where to Get Help

- **GitHub Issues**: Bug reports
- **GitHub Discussions**: Questions
- **Documentation**: `docs/` folder

---

## Quick Diagnostic Commands

```bash
# Test MT5 connection
python test_mt5_simple.py

# Validate setup
python validate_setup.py

# Quick functionality test
python examples/quick_test.py

# Check Python version
python --version

# Check installed packages
pip list | findstr "MetaTrader5 pandas numpy"
```

---

## Common Configuration Mistakes

### 1. Risk too high
```python
# ❌ BAD
RISK_PERCENT = 5.0  # Too risky!

# ✅ GOOD
RISK_PERCENT = 1.0  # Safe
```

### 2. Wrong symbol names
```python
# ❌ BAD (if your broker uses different names)
SYMBOLS = ['XAUUSD', 'XAGUSD']

# ✅ GOOD (check your broker)
SYMBOLS = ['GOLD', 'SILVER']
```

### 3. Lot sizes don't match broker
```python
# ❌ BAD
MIN_LOT_SIZE = 0.001  # Broker minimum is 0.01

# ✅ GOOD
MIN_LOT_SIZE = 0.01  # Matches broker
```

### 4. Safety limits disabled
```python
# ❌ BAD
MAX_DAILY_LOSS = 999999  # No protection!

# ✅ GOOD
MAX_DAILY_LOSS = 100.0  # Reasonable limit
```

---

## Still Having Issues?

1. **Start fresh**: Delete and reinstall
2. **Use demo account**: Test thoroughly
3. **Check broker**: Some brokers restrict algo trading
4. **Update software**: Latest MT5 and Python
5. **Ask community**: GitHub Discussions

---

**Remember**: Always test on demo account first! Never risk real money until you're confident everything works correctly.
