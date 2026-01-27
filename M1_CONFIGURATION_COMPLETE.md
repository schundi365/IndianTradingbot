# M1 Configuration Complete ✓

## Summary
All settings have been optimized for M1 (1-minute) timeframe testing with 5% daily loss limit.

---

## ⚠️ CRITICAL WARNINGS

### Expected Behavior
- **100-200+ trades per day** (possibly more!)
- **Very fast execution** (10-second update interval)
- **High activity** until 5% daily loss is reached
- **Tight stops** mean quick exits (wins and losses)

### Safety Limits Active
✓ **5% daily loss limit** - Bot stops trading when reached  
✓ **10% max drawdown** - Emergency brake  
✓ **$100 minimum balance** - Account protection  

---

## Complete M1 Settings Applied

### 1. Timeframe
```python
TIMEFRAME = mt5.TIMEFRAME_M1  # 1-minute bars
UPDATE_INTERVAL = 10          # Check every 10 seconds
```

### 2. Moving Averages (M1 Optimized)
```python
FAST_MA_PERIOD = 5   # 5-minute EMA
SLOW_MA_PERIOD = 10  # 10-minute EMA
```

### 3. MACD (M1 Optimized)
```python
MACD_FAST = 5        # Faster response
MACD_SLOW = 13       # Faster response
MACD_SIGNAL = 3      # Faster response
MACD_MIN_HISTOGRAM = 0.0  # No minimum (more signals)
```

### 4. Stop Loss (M1 Optimized)
```python
ATR_PERIOD = 14              # 14 minutes
ATR_MULTIPLIER_SL = 1.2      # Very tight stops
```

### 5. Take Profit (M1 Optimized)
```python
TP_LEVELS = [1.0, 1.3, 1.8]  # Quick profit targets
```

### 6. Trailing Stops (M1 Optimized)
```python
TRAIL_ACTIVATION_ATR = 0.8   # Activate very quickly
TRAIL_DISTANCE_ATR = 0.6     # Trail very close
BREAKEVEN_ACTIVATION_PIPS = 30  # Fast breakeven
TRAIL_START_PIPS = 50        # Fast trailing start
```

### 7. Trend Filter (M1 Optimized)
```python
TREND_TIMEFRAME = mt5.TIMEFRAME_M15  # M15 for trend
TREND_MA_PERIOD = 20                 # Shorter MA
```

### 8. Risk Management (M1 Testing)
```python
RISK_PERCENT = 0.3              # 0.3% per trade
MIN_TRADE_CONFIDENCE = 0.50     # 50% minimum (more signals)
MAX_DAILY_LOSS_PERCENT = 5.0    # 5% daily loss limit
```

### 9. Adaptive Risk (M1 Optimized)
```python
TREND_STRENGTH_PERIOD = 20      # Shorter period
ADX_STRONG_TREND = 18           # Lower threshold
ADX_RANGING = 12                # Lower threshold
TREND_CONSISTENCY_HIGH = 60     # Lower threshold
```

### 10. Trade Limits (Testing Mode)
```python
ENABLE_TRADING_HOURS = False    # Trade 24/7
MAX_TRADES_TOTAL = 999          # Unlimited
MAX_TRADES_PER_SYMBOL = 999     # Unlimited
MAX_DAILY_TRADES = 999          # Unlimited
```

---

## What Changed from Previous Config

| Setting | Before (M5) | Now (M1) | Reason |
|---------|-------------|----------|--------|
| Timeframe | M5 | M1 | Maximum frequency |
| Update Interval | 30s | 10s | Faster response |
| Fast MA | 10 | 5 | M1 optimized |
| Slow MA | 20 | 10 | M1 optimized |
| MACD Fast | 8 | 5 | Faster signals |
| MACD Slow | 17 | 13 | Faster signals |
| MACD Signal | 5 | 3 | Faster signals |
| MACD Min Histogram | 0.5 | 0.0 | More signals |
| TP Levels | [1.2, 1.8, 2.5] | [1.0, 1.3, 1.8] | Quicker exits |
| Trend Timeframe | H1 | M15 | Faster trend |
| Trend MA Period | 50 | 20 | Faster trend |
| Risk % | 0.2% | 0.3% | Higher for testing |
| Min Confidence | 70% | 50% | More trades |
| Daily Loss Limit | 3% | 5% | User requested |
| Breakeven Pips | 50 | 30 | Faster breakeven |
| Trail Start Pips | 75 | 50 | Faster trailing |
| Trend Strength Period | 30 | 20 | Faster response |
| ADX Strong Trend | 20 | 18 | More signals |
| ADX Ranging | 15 | 12 | More signals |
| Trend Consistency | 65 | 60 | More signals |

---

## Expected Performance

### Trade Frequency
- **M1 timeframe**: 100-200+ signals per day
- **50% confidence**: ~50-100+ actual trades per day
- **Multiple symbols**: XAUUSD, GBPUSD, XAGUSD

### Risk Profile
- **Per trade**: 0.3% risk
- **Daily limit**: 5% total equity
- **Typical scenario**: 15-20 trades before hitting limit (if all losses)
- **Best case**: Unlimited trades if profitable

### Monitoring
- Bot checks every **10 seconds**
- Dynamic SL/TP updates every **60 seconds**
- Very responsive to market changes

---

## How to Use

### 1. Start the Bot
```bash
python run_bot.py
```

### 2. Monitor Closely
- Watch for high trade frequency
- Check daily P/L regularly
- Bot will auto-stop at 5% daily loss

### 3. Stop the Bot
- Press `Ctrl+C` in terminal
- Or close the terminal window
- Positions remain open (manage manually if needed)

### 4. Review Results
- Check `trading_bot.log` for all trades
- Analyze performance with `analyze_trades.py`
- Adjust settings based on results

---

## Next Steps

1. **Test with small account** or demo first
2. **Monitor first hour** to see trade frequency
3. **Check daily loss tracking** is working
4. **Review trades** after hitting 5% limit
5. **Adjust settings** based on results

---

## Files Modified
- `src/config.py` - Complete M1 configuration

## Status
✅ **READY FOR M1 TESTING**

All settings optimized for 1-minute timeframe with 5% daily loss limit.
