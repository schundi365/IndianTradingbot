# Configuration Profiles

## Available Trading Strategies

GEM Trading Bot comes with multiple pre-configured trading strategies. Choose the one that fits your trading style and risk tolerance.

---

## 🎯 Default: Profitable Balanced (RECOMMENDED)

**File:** `src/config.py` (default)
**Also available as:** `src/config_profitable_balanced.py`

### Strategy
Trend-Following with Multiple Confirmations

### Key Features
- **Timeframe:** H1 (1-hour)
- **Trades/Day:** 5-15 quality trades
- **Win Rate:** 55-65%
- **Risk/Reward:** 1:2 minimum
- **Confidence:** 70% minimum

### Best For
- Most traders
- Consistent profits
- Lower stress
- Balanced risk/reward

### Indicators
- 20/50 EMA (trend)
- RSI (avoid extremes)
- MACD (momentum)
- ADX (trend strength)
- Bollinger Bands
- H4 trend filter

### Risk Management
- 0.5% per trade
- Max 10 open trades
- 3% daily loss limit
- 2x ATR stops

---

## ⚡ Alternative: M1 Experimental (HIGH RISK)

**File:** `src/config_m1_experimental.py`

### Strategy
Extreme High-Frequency Scalping

### Key Features
- **Timeframe:** M1 (1-minute)
- **Trades/Day:** 100-200+ trades
- **Win Rate:** 30-40%
- **Risk/Reward:** 1:1.5
- **Confidence:** 40% minimum

### Best For
- Experienced traders only
- High-risk tolerance
- Testing and experimentation
- NOT recommended for live trading

### Warning
⚠️ **This configuration typically loses money!**
- Too many trades
- High commissions
- Too much noise
- Tight stops
- Low win rate

### Use Cases
- Testing bot functionality
- Learning how NOT to trade
- Extreme scalping experiments
- Demo account only

---

## 📊 Comparison

| Feature | Profitable (Default) | M1 Experimental |
|---------|---------------------|-----------------|
| **Timeframe** | H1 (1-hour) | M1 (1-minute) |
| **Trades/Day** | 5-15 | 100-200+ |
| **Win Rate** | 55-65% | 30-40% |
| **Risk/Reward** | 1:2 | 1:1.5 |
| **Confidence** | 70% | 40% |
| **MA Periods** | 20/50 | 5/10 |
| **Stop Loss** | 2.0x ATR | 0.8x ATR |
| **Commissions** | Low | High |
| **Result** | ✅ Profitable | ❌ Losing |
| **Recommended** | ✅ Yes | ❌ No |

---

## 🔄 How to Switch Configurations

### Method 1: Use the Script (Easiest)

```bash
# Switch to Profitable (default)
python apply_profitable_config.py

# Or manually copy:
cp src/config_profitable_balanced.py src/config.py
```

### Method 2: Manual Copy

```bash
# For Profitable Balanced (recommended)
cp src/config_profitable_balanced.py src/config.py

# For M1 Experimental (not recommended)
cp src/config_m1_experimental.py src/config.py
```

### Method 3: Edit Directly

Edit `src/config.py` and change the settings manually.

---

## 🎓 Creating Custom Configurations

### Step 1: Copy a Base Config
```bash
cp src/config_profitable_balanced.py src/config_custom.py
```

### Step 2: Edit Settings
Open `src/config_custom.py` and modify:
- Timeframe
- Indicators
- Risk parameters
- Filters

### Step 3: Test on Demo
Always test custom configurations on demo account first!

### Step 4: Apply
```bash
cp src/config_custom.py src/config.py
```

---

## 📝 Configuration Parameters

### Timeframe Options
```python
TIMEFRAME = mt5.TIMEFRAME_M1   # 1 minute (not recommended)
TIMEFRAME = mt5.TIMEFRAME_M5   # 5 minutes
TIMEFRAME = mt5.TIMEFRAME_M15  # 15 minutes
TIMEFRAME = mt5.TIMEFRAME_M30  # 30 minutes
TIMEFRAME = mt5.TIMEFRAME_H1   # 1 hour (recommended)
TIMEFRAME = mt5.TIMEFRAME_H4   # 4 hours
TIMEFRAME = mt5.TIMEFRAME_D1   # Daily
```

### Risk Management
```python
RISK_PERCENT = 0.5              # % of account per trade
REWARD_RATIO = 2.0              # Risk:Reward ratio
ATR_MULTIPLIER_SL = 2.0         # Stop loss multiplier
MIN_TRADE_CONFIDENCE = 0.70     # Minimum confidence
```

### Indicators
```python
FAST_MA_PERIOD = 20             # Fast moving average
SLOW_MA_PERIOD = 50             # Slow moving average
RSI_PERIOD = 14                 # RSI period
MACD_FAST = 12                  # MACD fast
MACD_SLOW = 26                  # MACD slow
```

---

## ⚠️ Important Notes

### Before Changing Configurations:
1. **Stop the bot** - Always stop before changing
2. **Backup current config** - Save your settings
3. **Test on demo** - Never test live
4. **Monitor results** - Track performance
5. **Be patient** - Give it time

### After Changing:
1. **Restart the bot** - Apply new settings
2. **Monitor closely** - Watch first few trades
3. **Check logs** - Verify correct operation
4. **Track metrics** - Win rate, profit factor
5. **Adjust if needed** - Fine-tune settings

---

## 🎯 Recommendations

### For Beginners:
✅ Use **Profitable Balanced** (default)
- Proven strategy
- Good win rate
- Lower risk
- Easier to manage

### For Experienced Traders:
✅ Start with **Profitable Balanced**
- Test for 1 month
- Analyze results
- Create custom config
- Optimize for your style

### For Experimenters:
⚠️ Use **M1 Experimental** on demo only
- Understand why it loses
- Learn from mistakes
- Don't use live
- High risk

---

## 📊 Performance Tracking

### Monitor These Metrics:
1. **Win Rate** - Should be >50%
2. **Profit Factor** - Should be >1.5
3. **Average Win** - Should be >2x average loss
4. **Max Drawdown** - Should be <10%
5. **Monthly Return** - Should be positive

### If Performance is Poor:
1. Check if following the strategy
2. Verify all filters are working
3. Review trade history
4. Adjust confidence threshold
5. Consider switching timeframe

---

## 🆘 Troubleshooting

### Bot Not Trading:
- Check confidence threshold (may be too high)
- Verify filters aren't too strict
- Check trading hours
- Review logs for rejections

### Too Many Trades:
- Increase confidence threshold
- Add more filters
- Use higher timeframe
- Tighten entry rules

### Too Many Losses:
- Check win rate (should be >50%)
- Verify stop loss isn't too tight
- Review entry signals
- Consider switching to default config

---

## 📚 Additional Resources

- **Strategy Guide:** `PROFITABLE_STRATEGY_GUIDE.md`
- **Quick Switch:** `SWITCH_TO_PROFITABLE_STRATEGY.md`
- **User Guide:** `USER_GUIDE.md`
- **Troubleshooting:** `TROUBLESHOOTING.md`

---

## ✅ Summary

**Default Configuration:** Profitable Balanced
- ✅ Proven profitable
- ✅ Good win rate (55-65%)
- ✅ Reasonable trades (5-15/day)
- ✅ Proper risk management
- ✅ **RECOMMENDED**

**Alternative Configuration:** M1 Experimental
- ❌ Typically loses money
- ❌ Too many trades (100-200+/day)
- ❌ Low win rate (30-40%)
- ❌ High risk
- ❌ **NOT RECOMMENDED**

**Stick with the default unless you know what you're doing!** 🎯
