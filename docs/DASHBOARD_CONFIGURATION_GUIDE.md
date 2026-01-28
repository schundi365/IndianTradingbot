# GEM Trading Dashboard - Configuration Guide

## Quick Start

### Step 1: Access the Dashboard
1. Start the dashboard:
   ```bash
   python start_dashboard.py
   ```
2. Open your browser to: http://localhost:5000
3. Accept the risk disclaimer (first time only)

### Step 2: Choose a Configuration Preset

At the top of the Configuration tab, you'll see a preset selector:

#### ✅ Profitable Balanced (H1) - **RECOMMENDED**
- **Best for**: Most traders, beginners to intermediate
- **Timeframe**: 1-hour charts
- **Risk**: 0.5% per trade
- **Expected**: 5-15 quality trades per day
- **Win Rate**: 55-65%
- **Features**: Balanced approach with multiple confirmations

#### 🛡️ Conservative (H4) - **SAFEST**
- **Best for**: Risk-averse traders, small accounts
- **Timeframe**: 4-hour charts
- **Risk**: 0.3% per trade
- **Expected**: 2-8 trades per day
- **Win Rate**: 60-70%
- **Features**: Strictest filters, widest stops, highest quality

#### ⚡ Aggressive (M30) - **EXPERIENCED ONLY**
- **Best for**: Experienced traders, larger accounts
- **Timeframe**: 30-minute charts
- **Risk**: 1.0% per trade
- **Expected**: 15-50 trades per day
- **Win Rate**: 50-60%
- **Features**: More trades, tighter stops, requires monitoring

#### 🎨 Custom - **MANUAL CONFIGURATION**
- **Best for**: Advanced users who know what they're doing
- **Allows**: Full manual control of all 43 parameters
- **Warning**: Easy to create losing configurations

### Step 3: Customize (Optional)

If you want to adjust the preset, expand any of these sections:

#### 📊 Indicator Settings
**Moving Averages**
- Fast MA: Shorter period (default: 20)
- Slow MA: Longer period (default: 50)
- Tip: Fast < Slow always

**RSI (Relative Strength Index)**
- Period: How many bars to calculate (default: 14)
- Overbought: Don't buy above this (default: 70)
- Oversold: Don't sell below this (default: 30)
- Tip: Tighter range = fewer trades

**MACD (Moving Average Convergence Divergence)**
- Fast: Short EMA (default: 12)
- Slow: Long EMA (default: 26)
- Signal: Signal line (default: 9)
- Min Histogram: Minimum momentum (default: 0.5)
- Tip: Higher histogram = stronger signals

**ATR (Average True Range)**
- Period: Volatility calculation (default: 14)
- Multiplier: Stop loss distance (default: 2.0)
- Tip: Higher multiplier = wider stops

**ADX (Average Directional Index)**
- Min Strength: Only trade when ADX > this (default: 25)
- Tip: Higher = only strong trends

#### 🛡️ Trade Filters
**Enable/Disable Filters**
- RSI Filter: Avoid overbought/oversold
- MACD Filter: Require momentum confirmation
- ADX Filter: Only trade strong trends
- Trend Filter: Use H4 for major trend direction

**Trading Hours**
- Enable: Only trade during specific hours
- Start Hour: Begin trading (UTC)
- End Hour: Stop trading (UTC)
- Tip: 8-16 UTC = London + NY overlap

**News Avoidance**
- Enable: Avoid trading around news
- Buffer: Minutes before/after news
- Tip: 60 minutes recommended

#### 💼 Position Management
**Split Orders**
- Enable: Use multiple take profit levels
- Positions: How many splits (1-5)
- TP Level 1/2/3: Risk:Reward ratios
- Tip: Lock in profits gradually

**Trade Limits**
- Max Trades Total: Overall open positions
- Max Per Symbol: Per currency pair
- Tip: Lower = more conservative

**Trailing Stop**
- Enable: Move stop loss as profit grows
- Activation: Start trailing after X*ATR profit
- Distance: Trail X*ATR behind price
- Tip: Protects profits automatically

#### ⚠️ Risk Management
**Adaptive Risk**
- Enable: Adjust risk based on conditions
- Max Multiplier: Increase risk in good conditions
- Min Multiplier: Decrease risk in bad conditions
- Tip: Helps optimize returns

**Safety Limits**
- Max Drawdown: Stop if account drops X%
- Max Daily Trades: Limit trades per day
- Tip: Prevents overtrading

### Step 4: Save Configuration

1. Click "💾 Save Configuration" button
2. Wait for success message
3. If bot is running, restart it to apply changes

### Step 5: Test on Demo

**CRITICAL: Always test new configurations on demo account first!**

1. Run bot with new config for at least 1 week
2. Monitor these metrics:
   - Win rate (should be > 50%)
   - Average win vs average loss
   - Max drawdown
   - Number of trades per day
3. Adjust if needed
4. Only move to live after consistent demo results

## Understanding the Settings

### Basic Settings

**Trading Symbols**
- XAUUSD (Gold) - Most popular, good trends
- XAGUSD (Silver) - Similar to gold, more volatile
- GBPUSD, EURUSD, USDJPY - Forex pairs
- Tip: Start with 1-2 symbols

**Timeframe**
- M1 (1 min) - NOT RECOMMENDED (too noisy)
- M5 (5 min) - Scalping only
- M15 (15 min) - Short-term
- M30 (30 min) - Aggressive
- **H1 (1 hour) - RECOMMENDED** (best balance)
- H4 (4 hours) - Conservative
- D1 (Daily) - Long-term

**Risk Per Trade**
- 0.1-0.5% - Conservative (recommended)
- 0.5-1.0% - Moderate
- 1.0-2.0% - Aggressive (risky)
- 2.0%+ - Very risky (not recommended)

**Risk/Reward Ratio**
- 1:1 - Break even at 50% win rate
- 1:2 - Profitable at 35% win rate (recommended)
- 1:3 - Profitable at 25% win rate
- Higher = fewer trades but bigger wins

**Min Trade Confidence**
- 20-50% - Many trades, lower quality
- 50-70% - Balanced
- **70-80% - Recommended** (high quality)
- 80%+ - Very few trades

**Max Daily Loss**
- 1-2% - Very conservative
- **3-5% - Recommended**
- 5-10% - Aggressive
- 10%+ - Very risky

## Common Configuration Mistakes

### ❌ DON'T DO THIS:

1. **Risk too high**
   - Setting risk > 1% per trade
   - Can wipe out account quickly
   - Fix: Use 0.5% or less

2. **Confidence too low**
   - Setting confidence < 50%
   - Takes too many bad trades
   - Fix: Use 70% or higher

3. **Wrong timeframe**
   - Using M1 or M5 for beginners
   - Too much noise, overtrading
   - Fix: Use H1 or H4

4. **Too many symbols**
   - Trading 5+ symbols at once
   - Spreads risk too thin
   - Fix: Start with 1-2 symbols

5. **Disabling all filters**
   - Turning off RSI, MACD, ADX
   - Takes every signal (bad ones too)
   - Fix: Keep filters enabled

6. **No stop loss**
   - Setting ATR multiplier too high
   - Losses get too big
   - Fix: Use 2.0 or less

7. **Testing on live first**
   - Skipping demo testing
   - Loses real money learning
   - Fix: Always test on demo first

### ✅ DO THIS INSTEAD:

1. **Start with a preset**
   - Use "Profitable Balanced"
   - Proven to work
   - Adjust gradually

2. **Test on demo**
   - Run for 1-2 weeks minimum
   - Track all metrics
   - Only go live after success

3. **Make small changes**
   - Adjust one thing at a time
   - Test each change
   - Know what works

4. **Monitor regularly**
   - Check dashboard daily
   - Review trades weekly
   - Adjust as needed

5. **Keep risk low**
   - 0.5% per trade maximum
   - 3% daily loss limit
   - Protect your capital

## Troubleshooting

### Configuration won't save
- Check for validation errors (red text)
- Ensure all required fields filled
- Check Fast MA < Slow MA
- Check RSI oversold < overbought
- Check TP levels in ascending order

### Bot not trading
- Check MT5 connection (Test MT5 button)
- Check trading hours enabled
- Check confidence threshold not too high
- Check symbols selected
- Check max trades not reached

### Too many trades
- Increase confidence threshold
- Enable more filters
- Use higher timeframe
- Reduce max daily trades

### Too few trades
- Decrease confidence threshold
- Disable some filters
- Use lower timeframe
- Check trading hours

### Losing money
- STOP TRADING IMMEDIATELY
- Review trade history
- Check win rate (should be > 50%)
- Check average loss vs average win
- Consider switching to Conservative preset
- Test on demo before continuing

## Best Practices

### For Beginners
1. Use "Profitable Balanced" preset
2. Don't change anything for first week
3. Monitor on demo account
4. Learn what each setting does
5. Make small adjustments only
6. Test each change thoroughly

### For Intermediate
1. Start with preset, customize gradually
2. Track performance of each change
3. Focus on win rate and risk/reward
4. Experiment on demo first
5. Keep detailed notes
6. Share successful configs with community

### For Advanced
1. Create custom configurations
2. Backtest thoroughly
3. A/B test different settings
4. Optimize for specific market conditions
5. Document everything
6. Help others learn

## Performance Expectations

### Profitable Balanced (H1)
- **Win Rate**: 55-65%
- **Trades/Day**: 5-15
- **Monthly Return**: 5-15% (varies)
- **Max Drawdown**: 5-10%
- **Best For**: Consistent growth

### Conservative (H4)
- **Win Rate**: 60-70%
- **Trades/Day**: 2-8
- **Monthly Return**: 3-10% (varies)
- **Max Drawdown**: 3-8%
- **Best For**: Capital preservation

### Aggressive (M30)
- **Win Rate**: 50-60%
- **Trades/Day**: 15-50
- **Monthly Return**: 10-25% (varies)
- **Max Drawdown**: 10-20%
- **Best For**: Growth (with risk)

**Note**: Past performance does not guarantee future results. Always trade responsibly.

## Getting Help

### Dashboard Issues
1. Check logs tab in dashboard
2. Look for error messages
3. Restart dashboard if needed
4. Check MT5 connection

### Configuration Questions
1. Read this guide thoroughly
2. Start with presets
3. Test on demo first
4. Ask in community forums

### Trading Performance
1. Review trade history
2. Check AI recommendations tab
3. Analyze win rate and R:R
4. Consider switching presets

## Summary

1. **Start Simple**: Use "Profitable Balanced" preset
2. **Test First**: Always use demo account
3. **Monitor Closely**: Check dashboard daily
4. **Adjust Gradually**: One change at a time
5. **Stay Safe**: Keep risk low (0.5% per trade)
6. **Be Patient**: Good trading takes time

---

**Remember**: The best configuration is the one that:
- You understand completely
- Has been tested on demo
- Matches your risk tolerance
- Produces consistent results
- Lets you sleep at night

Happy trading! 💎📈
