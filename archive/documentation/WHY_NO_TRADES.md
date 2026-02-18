# Why Is My Bot Not Trading?

**Quick Answer**: This is normal! Your bot is being selective and waiting for high-quality trade setups.

---

## Is This Normal?

**YES!** Seeing "No trades found" or zero trades is completely normal for:

✅ **New Installations** - Bot just started, hasn't found signals yet  
✅ **Fresh Demo Accounts** - No trading history yet  
✅ **High Confidence Settings** - Bot is selective (quality over quantity)  
✅ **Ranging Markets** - No clear trends to trade  
✅ **Outside Trading Hours** - If trading hours filter is enabled  

---

## Common Reasons

### 1. High Confidence Threshold (Most Common)

**Default Setting**: 60% minimum confidence  
**What It Means**: Bot only trades when 60%+ confident  
**Result**: Fewer but higher quality trades

**Solution**:
```
Dashboard > Configuration > Min Trade Confidence > Change to 40-50%
Click "Save Configuration"
Restart Bot
```

### 2. Strict Filters Enabled

Your bot has multiple filters that reject weak signals:

- ✅ **RSI Filter** - Avoids overbought/oversold conditions
- ✅ **MACD Confirmation** - Requires momentum confirmation
- ✅ **Volume Filter** - Only trades on above-average volume
- ✅ **Trend Filter** - Only trades with the trend
- ✅ **ADX Filter** - Requires strong trend strength

**Solution**: Disable some filters if you want more trades
```
Dashboard > Configuration > Uncheck some filters
```

### 3. Limited Symbols

**Default**: 2-4 symbols (XAUUSD, XAGUSD, etc.)  
**Result**: Fewer opportunities

**Solution**: Add more symbols
```
Dashboard > Configuration > Trading Symbols
Select: EURUSD, GBPUSD, AUDUSD, NZDUSD
Click "Save Configuration"
```

### 4. Long Timeframe

**H1 Timeframe** = 1 trade per hour maximum per symbol  
**Result**: 5-15 quality trades per day

**Solution**: Use shorter timeframe for more trades
```
Dashboard > Configuration > Timeframe > M5 or M15
```

### 5. Market Conditions

- **Ranging Market** - No clear trend
- **Low Volatility** - Small price movements
- **News Events** - Bot avoids trading during news
- **Weekend** - Markets closed

**Solution**: Wait for better market conditions or adjust settings

---

## Quick Fixes

### Want Trades FAST? (Aggressive)

```
1. Min Trade Confidence: 40%
2. Timeframe: M5
3. Symbols: Select 10+ symbols
4. Disable: Trend Filter, News Filter
5. Risk: 0.5% (start small)
```
**Expected**: 20-50 trades per day  
**Win Rate**: 50-55%

### Want Quality Trades? (Recommended)

```
1. Min Trade Confidence: 60%
2. Timeframe: H1
3. Symbols: 2-4 symbols
4. Enable: All filters
5. Risk: 1%
```
**Expected**: 5-15 trades per day  
**Win Rate**: 55-65%

### Want Safe Trading? (Conservative)

```
1. Min Trade Confidence: 70%
2. Timeframe: H4
3. Symbols: 2 symbols (XAUUSD, EURUSD)
4. Enable: All filters
5. Risk: 0.3%
```
**Expected**: 2-5 trades per day  
**Win Rate**: 60-70%

---

## How to Check If Bot Is Working

### 1. Check Logs

```
Dashboard > System Logs

Look for:
✅ "MT5 initialized successfully"
✅ "Trading bot started"
✅ "Analyzing XAUUSD..."
✅ "Bullish MA crossover detected"
✅ "RSI filter: OK"
```

If you see these, bot is working!

### 2. Check Bot Status

```
Dashboard > Top Right

Should show:
✅ "Bot Status: Running"
✅ Green indicator
```

### 3. Check MT5 Connection

```
Dashboard > Test MT5 Button

Should show:
✅ "Connected"
✅ Account balance
✅ Account number
```

---

## Understanding Bot Behavior

### What Bot Does Every Minute

1. **Analyzes Each Symbol**
   - Fetches latest price data
   - Calculates indicators (MA, RSI, MACD, ATR)
   - Checks for entry signals

2. **Applies Filters**
   - RSI not overbought/oversold?
   - MACD confirms signal?
   - Volume above average?
   - Trend is strong?

3. **Calculates Confidence**
   - Market conditions
   - Trend strength
   - Volatility
   - Volume confirmation

4. **Makes Decision**
   - If confidence ≥ threshold → TRADE
   - If confidence < threshold → SKIP

### Why Bot Skips Trades

```
Example Log:
"Bullish MA crossover detected"
"[X] RSI filter: Too overbought (RSI: 78.5)"
→ Trade rejected

"Bearish MA crossover detected"
"[X] Volume filter: Below average (0.8x)"
→ Trade rejected

"Bullish trend confirmation"
"[OK] RSI filter: OK (RSI: 55.2)"
"[OK] MACD filter: Confirmed"
"[OK] Volume filter: Above average (1.4x)"
"Trade confidence: 75%"
→ Trade executed!
```

---

## Troubleshooting

### "Bot says running but no trades for hours"

**Check**:
1. Confidence threshold (lower to 40%)
2. Number of symbols (add more)
3. Timeframe (try M15)
4. Logs for rejected signals

### "Bot was trading yesterday, not today"

**Possible Reasons**:
1. Market conditions changed (ranging vs trending)
2. Volatility decreased
3. Different trading session (Asian vs London)
4. Weekend (markets closed)

### "I want trades NOW for testing"

**Quick Test Settings**:
```
Min Confidence: 30%
Timeframe: M5
Symbols: 10+ symbols
Disable all filters
Risk: 0.1% (very small)
```

**Warning**: These settings are for testing only! Not recommended for real trading.

---

## Expected Trade Frequency

### By Timeframe

| Timeframe | Trades/Day | Quality |
|-----------|------------|---------|
| M5        | 30-100     | Lower   |
| M15       | 15-50      | Medium  |
| M30       | 10-30      | Good    |
| H1        | 5-15       | High    |
| H4        | 2-5        | Highest |

### By Confidence

| Confidence | Trades/Day | Win Rate |
|------------|------------|----------|
| 30%        | 50-100     | 45-50%   |
| 40%        | 30-60      | 50-55%   |
| 50%        | 20-40      | 52-58%   |
| 60%        | 10-20      | 55-65%   |
| 70%        | 5-10       | 60-70%   |

---

## Best Practices

### For Beginners

1. **Start with Recommended Settings**
   - Use "Profitable Balanced" preset
   - Don't change anything for first week
   - Monitor and learn

2. **Test on Demo First**
   - At least 1 week on demo
   - Verify bot behavior
   - Understand settings

3. **Start Small**
   - Risk: 0.3-0.5% per trade
   - 2-3 symbols only
   - Increase gradually

### For Experienced Traders

1. **Optimize for Your Style**
   - Scalper: M5, 40% confidence, many symbols
   - Day Trader: M30, 50% confidence, 5-10 symbols
   - Swing Trader: H4, 70% confidence, 2-3 symbols

2. **Monitor Performance**
   - Track win rate
   - Adjust confidence based on results
   - Fine-tune filters

3. **Adapt to Market**
   - Trending: Enable trend filter
   - Ranging: Disable trend filter
   - Volatile: Increase ATR multiplier

---

## Still No Trades?

### Check These

1. **MT5 is Running** ✓
2. **Logged into Account** ✓
3. **Algo Trading Enabled** ✓
4. **Bot Status: Running** ✓
5. **Symbols Selected** ✓
6. **Confidence < 70%** ✓
7. **Timeframe ≤ H1** ✓

If all checked and still no trades after 1 hour:

1. Check logs for error messages
2. Lower confidence to 30% temporarily
3. Add 10+ symbols
4. Switch to M5 timeframe
5. Disable all filters

This should generate trades within 15-30 minutes.

---

## Summary

**"No trades found" is NORMAL and EXPECTED for:**
- New installations
- High-quality trading strategy
- Selective bot behavior
- Waiting for optimal setups

**To see trades faster:**
- Lower confidence threshold
- Add more symbols
- Use shorter timeframe
- Disable some filters

**Remember**: Quality > Quantity. The bot is designed to be selective and only trade high-probability setups. This is a feature, not a bug!

---

**Need Help?**
- Check: `TROUBLESHOOTING.md`
- Read: `USER_GUIDE.md`
- Review: Dashboard > System Logs
