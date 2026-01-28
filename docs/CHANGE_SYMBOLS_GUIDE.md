# How to Change Trading Symbols

## Quick Guide to Trade Any Symbols

The bot is **already generic** and can trade any MT5 symbols. You just need to change the symbol list!

---

## 🎯 Main Change Required

### Edit `src/config.py` - Line 11

**Current:**
```python
SYMBOLS = ['XAUUSD', 'XAGUSD']  # Gold and Silver
```

**Change to your desired symbols:**

### Forex Pairs
```python
SYMBOLS = ['EURUSD', 'GBPUSD']  # Major pairs
SYMBOLS = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD']  # Multiple pairs
```

### Indices
```python
SYMBOLS = ['US30', 'US500']  # Dow Jones, S&P 500
SYMBOLS = ['NAS100', 'GER40']  # Nasdaq, DAX
```

### Commodities (Keep current)
```python
SYMBOLS = ['XAUUSD', 'XAGUSD']  # Gold, Silver
SYMBOLS = ['XTIUSD', 'XBRUSD']  # Oil (WTI, Brent)
```

### Crypto (if broker supports)
```python
SYMBOLS = ['BTCUSD', 'ETHUSD']  # Bitcoin, Ethereum
```

### Mixed
```python
SYMBOLS = ['EURUSD', 'XAUUSD', 'US30']  # Forex + Gold + Index
```

---

## ⚠️ Important Notes

### 1. Check Symbol Names
Symbol names vary by broker. Check your MT5 Market Watch for exact names.

**Examples:**
- Gold might be: `XAUUSD`, `GOLD`, `XAUUSD.a`, `XAU/USD`
- EUR/USD might be: `EURUSD`, `EURUSDm`, `EURUSD.a`

### 2. Verify Symbol Availability
```bash
python test_connection.py
```
This will show if your symbols are available.

### 3. Check Symbol Specifications
Different symbols have different:
- **Lot sizes** (min/max)
- **Spreads** (cost per trade)
- **Volatility** (affects stop loss)
- **Trading hours** (when market is open)

---

## 🧪 Testing New Symbols

### Step 1: Update Configuration
```python
# In src/config.py
SYMBOLS = ['EURUSD']  # Start with one symbol
```

### Step 2: Test Connection
```bash
python test_connection.py
```

Should show:
```
✅ EURUSD is available
   Bid: 1.08234
   Ask: 1.08236
   Spread: 2 points
```

### Step 3: Test Bot
```bash
python test_bot_live.py
```

Should show:
```
EURUSD:
  Current Price: Bid=1.08234, Ask=1.08236
  ✅ Retrieved 100 bars of data
```

### Step 4: Run Bot
```bash
python run_bot.py
```

---

## 📊 Symbol-Specific Settings

### Forex Pairs (EURUSD, GBPUSD, etc.)

**Recommended settings:**
```python
RISK_PERCENT = 0.5          # 0.5% per trade
ATR_MULTIPLIER_SL = 1.5     # Tighter stops for forex
TP_LEVELS = [1.2, 1.8, 2.5] # Standard targets
```

**Characteristics:**
- Lower volatility than commodities
- Tighter spreads (1-3 pips)
- 24/5 trading
- Good for M1/M5 timeframes

### Indices (US30, US500, NAS100)

**Recommended settings:**
```python
RISK_PERCENT = 0.3          # Lower risk (more volatile)
ATR_MULTIPLIER_SL = 2.0     # Wider stops
TP_LEVELS = [1.5, 2.5, 4.0] # Larger targets
```

**Characteristics:**
- Higher volatility
- Larger point values
- Limited trading hours
- Better on M5/M15 timeframes

### Commodities (XAUUSD, XAGUSD, Oil)

**Current settings are optimized for commodities:**
```python
RISK_PERCENT = 0.3          # Low risk
ATR_MULTIPLIER_SL = 1.2     # Tight stops
TP_LEVELS = [1.0, 1.3, 1.8] # Quick exits
```

**Characteristics:**
- High volatility
- Larger spreads
- 24/5 trading
- Works on M1/M5 timeframes

### Crypto (BTCUSD, ETHUSD)

**Recommended settings:**
```python
RISK_PERCENT = 0.2          # Very low risk (extreme volatility)
ATR_MULTIPLIER_SL = 2.5     # Very wide stops
TP_LEVELS = [1.5, 3.0, 5.0] # Large targets
TIMEFRAME = mt5.TIMEFRAME_M15  # Use M15 or higher
```

**Characteristics:**
- EXTREME volatility
- Large spreads
- 24/7 trading
- NOT recommended for M1

---

## 🔧 Advanced: Multiple Symbol Types

If trading different symbol types together:

```python
# Mix of symbols
SYMBOLS = ['EURUSD', 'XAUUSD', 'US30']

# Use moderate settings that work for all
RISK_PERCENT = 0.3
ATR_MULTIPLIER_SL = 1.5
TP_LEVELS = [1.2, 1.8, 2.5]
```

Or create separate configs:

```python
# config_forex.py
SYMBOLS = ['EURUSD', 'GBPUSD']
RISK_PERCENT = 0.5

# config_commodities.py
SYMBOLS = ['XAUUSD', 'XAGUSD']
RISK_PERCENT = 0.3

# config_indices.py
SYMBOLS = ['US30', 'US500']
RISK_PERCENT = 0.3
```

---

## 📋 Quick Reference

### Popular Symbols by Category

**Forex (Low Spread, Good for M1/M5):**
- EURUSD - Euro/US Dollar
- GBPUSD - British Pound/US Dollar
- USDJPY - US Dollar/Japanese Yen
- AUDUSD - Australian Dollar/US Dollar
- USDCAD - US Dollar/Canadian Dollar
- NZDUSD - New Zealand Dollar/US Dollar

**Commodities (High Spread, M5+ recommended):**
- XAUUSD - Gold
- XAGUSD - Silver
- XTIUSD - Crude Oil (WTI)
- XBRUSD - Brent Oil
- XPTUSD - Platinum
- XPDUSD - Palladium

**Indices (Volatile, M5+ recommended):**
- US30 - Dow Jones
- US500 - S&P 500
- NAS100 - Nasdaq 100
- GER40 - DAX (Germany)
- UK100 - FTSE 100
- JPN225 - Nikkei 225

**Crypto (Very Volatile, M15+ only):**
- BTCUSD - Bitcoin
- ETHUSD - Ethereum
- LTCUSD - Litecoin
- XRPUSD - Ripple

---

## ✅ Verification Checklist

After changing symbols:

- [ ] Updated SYMBOLS in src/config.py
- [ ] Ran python test_connection.py
- [ ] Verified symbols are available
- [ ] Checked spread costs
- [ ] Adjusted risk settings if needed
- [ ] Tested with python test_bot_live.py
- [ ] Ran on demo account first
- [ ] Monitored first few trades

---

## 🆘 Troubleshooting

### Symbol Not Found
```
❌ EURUSD not found
```

**Solutions:**
1. Check exact symbol name in MT5 Market Watch
2. Enable symbol: Right-click in Market Watch → Show All
3. Your broker might use different names (e.g., EURUSDm, EURUSD.a)

### Invalid Volume
```
❌ Order failed, retcode 10014
```

**Solutions:**
1. Check broker's min/max lot sizes
2. Adjust MIN_LOT_SIZE in config
3. Some symbols require larger minimum lots

### High Spread Costs
```
⚠️ Spread: 50 points
```

**Solutions:**
1. Avoid trading during low liquidity
2. Use higher timeframes (M5, M15 instead of M1)
3. Consider different symbols with lower spreads

---

## 💡 Tips

1. **Start with one symbol** - Test thoroughly before adding more
2. **Check trading hours** - Some symbols have limited hours
3. **Monitor spread costs** - Can eat into profits quickly
4. **Adjust settings per symbol** - Different symbols need different settings
5. **Test on demo first** - Always test new symbols on demo account

---

## 🎯 Summary

**To change symbols:**
1. Edit `src/config.py` line 11
2. Change `SYMBOLS = ['YOUR', 'SYMBOLS']`
3. Test with `python test_connection.py`
4. Run bot with `python run_bot.py`

**That's it!** The bot works with any MT5 symbols.

---

*The bot is already generic - just change the symbol list!*
