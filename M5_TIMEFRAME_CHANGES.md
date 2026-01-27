# ⚠️ M5 Timeframe Configuration Changes

## 🔄 Changes Made

Your bot has been reconfigured for **M5 (5-minute) timeframe** trading.

---

## 📊 What Changed

### Timeframe
- **Before:** H1 (1 hour)
- **After:** M5 (5 minutes) ✅

### Moving Averages (Adjusted for faster timeframe)
- **Fast MA:** 20 → 10 periods (50 minutes)
- **Slow MA:** 50 → 20 periods (100 minutes)
- **MA Type:** SMA → EMA (better for lower timeframes)

### Risk Management (Reduced for more trades)
- **Risk per trade:** 1.0% → 0.5%
- **Reward ratio:** 1:2 → 1:1.5

### Safety Limits (Adjusted for higher activity)
- **Max daily trades:** 10 → 30
- **Update interval:** 60s → 30s

---

## ⚠️ CRITICAL WARNINGS

### M5 is VERY DIFFERENT from H1!

**What to Expect:**
- 🔥 **20-50+ trades per day** (vs 2-5 on H1)
- 🔥 **Constant activity** - bot will be very busy
- 🔥 **Higher spread costs** - more entries = more spread paid
- 🔥 **More false signals** - lower timeframe = more noise
- 🔥 **Requires monitoring** - check every 30-60 minutes
- 🔥 **Higher stress** - fast-paced trading

**Costs:**
- Each trade costs spread (typically $0.20-0.40)
- 30 trades/day = $6-12/day in spread costs
- Must make profit to cover these costs

**Time Commitment:**
- H1: Check 2-3 times per day
- M5: Check every 30-60 minutes
- Cannot leave unattended for long

---

## 📈 M5 Trading Characteristics

### Pros ✅
- More trading opportunities
- Faster reactions to market changes
- Can catch quick moves
- Good for active traders

### Cons ❌
- Much higher activity
- More false signals
- Higher transaction costs
- Requires constant monitoring
- More stressful
- Not suitable for beginners

---

## 🎯 Recommended Settings for M5

### Conservative (Current Settings) ✅
```python
RISK_PERCENT = 0.5          # Low risk
REWARD_RATIO = 1.5          # Realistic target
MAX_DAILY_TRADES = 30       # Limit activity
UPDATE_INTERVAL = 30        # Check every 30 seconds
```

### Aggressive (Not Recommended)
```python
RISK_PERCENT = 1.0          # Higher risk
REWARD_RATIO = 2.0          # Harder to achieve
MAX_DAILY_TRADES = 50       # Very active
UPDATE_INTERVAL = 15        # Check every 15 seconds
```

---

## 🧪 Testing M5 Configuration

Before running the bot, test the new settings:

```bash
# 1. Check configuration
python check_timeframe.py

# 2. Test signal detection
python examples/quick_test.py

# 3. Test bot functionality
python test_bot_live.py
```

---

## 📊 Expected Performance

### H1 vs M5 Comparison

| Metric | H1 (Before) | M5 (Now) |
|--------|-------------|----------|
| Trades/Day | 2-5 | 20-50+ |
| Monitoring | 2-3x/day | Every hour |
| Spread Cost | $0.40-1.00 | $4-10+ |
| Win Rate | 50-60% | 40-50% |
| Difficulty | Easy | Hard |
| Stress | Low | High |

### Realistic Expectations

**Good Day:**
- 30 trades, 18 wins, 12 losses
- Win rate: 60%
- Profit: $50-100 (after spread costs)

**Bad Day:**
- 30 trades, 12 wins, 18 losses
- Win rate: 40%
- Loss: $50-100 (including spread costs)

**Average:**
- Expect 45-55% win rate
- Small daily profits/losses
- Need consistency over weeks

---

## ⚠️ Important Considerations

### 1. Spread Costs
- XAUUSD spread: ~$0.20-0.40 per 0.01 lot
- 30 trades = $6-12 in spread costs
- Must make $6-12 profit just to break even

### 2. Slippage
- M5 moves fast
- May not get exact entry price
- 1-2 pips slippage common

### 3. False Signals
- Lower timeframes = more noise
- Many signals won't work out
- Need good risk management

### 4. Monitoring
- Check bot every 30-60 minutes
- Watch for excessive losses
- Be ready to stop if needed

### 5. Market Conditions
- M5 works better in trending markets
- Struggles in ranging/choppy markets
- May need to pause during news

---

## 🛡️ Safety Recommendations

### Before Starting:

1. **Test on Demo First** ⚠️
   - Run for at least 1 week
   - Monitor closely
   - Track all trades
   - Calculate actual costs

2. **Start with Low Risk** ⚠️
   - Keep 0.5% risk (current setting)
   - Don't increase until proven profitable
   - Consider 0.3% if very cautious

3. **Set Strict Limits** ⚠️
   - Max daily loss: $50-100
   - Max daily trades: 30
   - Stop if 5 losses in a row

4. **Monitor Constantly** ⚠️
   - Check every 30-60 minutes
   - Watch for unusual behavior
   - Be ready to stop bot

5. **Track Performance** ⚠️
   - Log all trades
   - Calculate win rate
   - Track spread costs
   - Review daily

---

## 🚀 How to Start

### Step 1: Verify Configuration
```bash
python check_timeframe.py
```

Expected output:
```
Timeframe: M5 (5 minutes)
Fast MA: 10 periods
Slow MA: 20 periods
```

### Step 2: Test Signals
```bash
python examples/quick_test.py
```

Watch for:
- Signals being detected
- MA values updating
- No errors

### Step 3: Start Bot
```bash
python run_bot.py
```

**Monitor closely for first hour!**

---

## 📊 Monitoring Checklist

### Every 30 Minutes:
- [ ] Bot still running?
- [ ] Any new trades?
- [ ] Trades profitable?
- [ ] Any errors in log?

### Every Hour:
- [ ] Check account balance
- [ ] Review open positions
- [ ] Check daily P/L
- [ ] Verify within limits

### End of Day:
- [ ] Total trades: ___
- [ ] Win rate: ___%
- [ ] Total P/L: $___
- [ ] Spread costs: $___
- [ ] Net profit: $___

---

## 🛑 When to Stop

**Stop the bot immediately if:**
- ❌ Daily loss exceeds $100
- ❌ 10 consecutive losses
- ❌ Win rate below 30%
- ❌ Unusual behavior
- ❌ Excessive spread costs
- ❌ Can't monitor properly

---

## 🔄 Reverting to H1

If M5 is too active, revert to H1:

1. Edit `src/config.py`
2. Change line 17:
```python
TIMEFRAME = mt5.TIMEFRAME_H1  # Back to 1 hour
```
3. Change line 103:
```python
FAST_MA_PERIOD = 20
SLOW_MA_PERIOD = 50
```
4. Change line 106:
```python
MA_TYPE = 'SMA'
```
5. Change line 33:
```python
RISK_PERCENT = 1.0
REWARD_RATIO = 2.0
```
6. Save and restart bot

---

## 📞 Need Help?

**If M5 is overwhelming:**
- Consider M15 or M30 instead
- Or revert to H1
- Read TROUBLESHOOTING.md

**If performance is poor:**
- Check win rate (need 45%+)
- Calculate spread costs
- Review trade quality
- Consider higher timeframe

---

## ✅ Final Checklist

Before running on M5:

- [ ] Understand M5 is VERY active (20-50+ trades/day)
- [ ] Prepared to monitor every 30-60 minutes
- [ ] Comfortable with higher spread costs
- [ ] Risk set to 0.5% (low)
- [ ] Daily limits set (30 trades, $100 loss)
- [ ] Tested on demo first
- [ ] Ready to stop if needed
- [ ] Have time to monitor closely

**If you checked all boxes:** You're ready! ✅

**If you're unsure:** Consider M15, M30, or H1 instead ⚠️

---

## 🎯 Summary

**Changed:** H1 → M5  
**Impact:** MUCH more active trading  
**Risk:** Reduced to 0.5%  
**Monitoring:** Required every 30-60 min  
**Recommendation:** Test thoroughly on demo first!  

**Good luck! 🚀**

---

*Last Updated: January 27, 2026*  
*Timeframe: M5 (5 minutes)*  
*Status: Configuration Updated*
