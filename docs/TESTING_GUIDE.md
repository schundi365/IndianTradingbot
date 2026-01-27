# Testing Guide

Complete guide for testing the MT5 Trading Bot before live deployment.

## Table of Contents
1. [Pre-Testing Setup](#pre-testing-setup)
2. [Connection Testing](#connection-testing)
3. [Functionality Testing](#functionality-testing)
4. [Demo Account Testing](#demo-account-testing)
5. [Performance Validation](#performance-validation)
6. [Going Live](#going-live)

---

## Pre-Testing Setup

### 1. Validate Installation

```bash
python validate_setup.py
```

This checks:
- ✅ Python version (3.8+)
- ✅ Required packages installed
- ✅ File structure is correct
- ✅ Configuration loads properly

### 2. Test MT5 Connection

```bash
python test_connection.py
```

This verifies:
- ✅ MT5 initializes successfully
- ✅ Account is connected
- ✅ Trading is allowed
- ✅ Symbols are available
- ✅ Historical data can be retrieved

**Expected Output:**
```
✅ ALL TESTS PASSED - Ready to run the bot!
```

---

## Connection Testing

### Test 1: Basic Connection

```python
import MetaTrader5 as mt5

# Initialize
if mt5.initialize():
    print("✅ Connected")
    print(f"Account: {mt5.account_info().login}")
    mt5.shutdown()
else:
    print("❌ Connection failed")
```

### Test 2: Symbol Availability

```python
import MetaTrader5 as mt5

mt5.initialize()

for symbol in ['XAUUSD', 'XAGUSD']:
    info = mt5.symbol_info(symbol)
    if info:
        print(f"✅ {symbol}: Bid={info.bid}, Ask={info.ask}")
    else:
        print(f"❌ {symbol} not available")

mt5.shutdown()
```

### Test 3: Historical Data

```python
import MetaTrader5 as mt5

mt5.initialize()

rates = mt5.copy_rates_from_pos('XAUUSD', mt5.TIMEFRAME_H1, 0, 100)
if rates is not None:
    print(f"✅ Retrieved {len(rates)} bars")
else:
    print("❌ Failed to get data")

mt5.shutdown()
```

---

## Functionality Testing

### Test 1: Quick Signal Check

```bash
python examples/quick_test.py
```

This runs one iteration and checks for signals without placing trades.

**Expected Output:**
```
✅ MT5 connected
Testing with: ['XAUUSD', 'XAGUSD']
Checking for signals...
📈 BUY signal detected for XAUUSD
⏸️  No signal for XAGUSD
Test complete!
```

### Test 2: Adaptive Risk Demo

```bash
python examples/adaptive_risk_demo.py
```

This demonstrates how adaptive risk adjusts parameters based on market conditions.

**Expected Output:**
```
Market Analysis:
  Trend Strength: Strong (ADX: 28.5)
  Volatility: Normal (ATR Ratio: 1.1)
  
Adjustments:
  Stop Loss: 2.0× ATR (from 2.0× base)
  Position Size: 1.2× multiplier
  Confidence: 75%
```

### Test 3: Configuration Validation

```python
import sys
sys.path.insert(0, 'src')
from config import get_config

config = get_config()

# Verify critical settings
assert config['risk_percent'] <= 2.0, "Risk too high!"
assert config['max_daily_loss'] > 0, "Daily loss limit not set!"
assert len(config['symbols']) > 0, "No symbols configured!"

print("✅ Configuration is valid")
```

---

## Demo Account Testing

### Phase 1: Basic Trading (Days 1-3)

**Objective:** Verify bot can place and manage trades

**Test Checklist:**
- [ ] Bot starts without errors
- [ ] Signals are generated
- [ ] Orders are placed successfully
- [ ] Stop loss is set correctly
- [ ] Take profit is set correctly
- [ ] Position size is calculated correctly
- [ ] Bot logs all activities

**How to Test:**
1. Start bot: `python run_bot.py`
2. Let it run for 2-3 hours
3. Check log file: `trading_bot.log`
4. Verify trades in MT5
5. Manually close positions to test

**Success Criteria:**
- No errors in log
- Orders placed with correct parameters
- SL/TP calculated accurately
- Position sizes respect risk limits

### Phase 2: Advanced Features (Days 4-7)

**Objective:** Test split orders and adaptive risk

**Test Checklist:**
- [ ] Split orders create multiple positions
- [ ] Each position has different TP
- [ ] Position sizes sum to total calculated
- [ ] Adaptive risk adjusts parameters
- [ ] Trade filtering rejects low-confidence setups
- [ ] Trailing stops activate correctly

**How to Test:**
1. Enable split orders in config
2. Enable adaptive risk
3. Run bot for several days
4. Monitor how it handles different market conditions
5. Check if partial profits are taken

**Success Criteria:**
- Multiple positions created per signal
- TPs are at different levels
- Some positions close before others
- Risk adjusts based on market conditions

### Phase 3: Safety Features (Days 8-14)

**Objective:** Verify safety limits work

**Test Checklist:**
- [ ] Daily loss limit stops trading
- [ ] Max trades per day is respected
- [ ] Drawdown protection activates
- [ ] Trading hours are respected
- [ ] Bot handles errors gracefully

**How to Test:**
1. Set low daily loss limit (e.g., $50)
2. Set low max trades (e.g., 3)
3. Let bot run until limits hit
4. Verify it stops trading
5. Test restart after reset

**Success Criteria:**
- Bot stops at daily loss limit
- Bot stops at max trades
- Bot resumes next day
- No trades outside allowed hours

---

## Performance Validation

### Metrics to Track

**Win Rate:**
```
Win Rate = (Winning Trades / Total Trades) × 100%
Target: 40-60%
```

**Risk:Reward Ratio:**
```
Average Win / Average Loss
Target: 1.5:1 or better
```

**Profit Factor:**
```
Profit Factor = Total Profit / Total Loss
Target: 1.5 or higher
```

**Maximum Drawdown:**
```
Max Drawdown = (Peak - Trough) / Peak × 100%
Target: < 10%
```

### Performance Analysis

After 2 weeks of demo trading:

1. **Export Trade History**
   - In MT5: Account History → Right-click → Save as Report
   - Or check `trading_bot.log`

2. **Calculate Metrics**
   ```python
   # Example calculation
   total_trades = 50
   winning_trades = 28
   total_profit = 450
   total_loss = 280
   
   win_rate = (winning_trades / total_trades) * 100
   profit_factor = total_profit / total_loss
   
   print(f"Win Rate: {win_rate:.1f}%")
   print(f"Profit Factor: {profit_factor:.2f}")
   ```

3. **Evaluate Results**
   - Is win rate acceptable?
   - Is profit factor > 1.5?
   - Is drawdown manageable?
   - Are you comfortable with the strategy?

---

## Going Live

### Pre-Live Checklist

**Account Preparation:**
- [ ] Funded live account
- [ ] Broker supports Gold/Silver
- [ ] Leverage is appropriate
- [ ] Understand commission structure
- [ ] Have emergency funds

**Configuration:**
- [ ] Risk per trade ≤ 1%
- [ ] Daily loss limit ≤ 3%
- [ ] Max drawdown ≤ 10%
- [ ] Conservative position sizes
- [ ] Safety limits enabled

**Monitoring:**
- [ ] Can check bot remotely
- [ ] Have alerts set up (optional)
- [ ] Know how to stop bot
- [ ] Can manually close positions
- [ ] Have backup plan

### First Week Live

**Day 1:**
- Start with minimum risk (0.5%)
- Monitor every hour
- Check all trades manually
- Verify everything works

**Days 2-3:**
- Continue close monitoring
- Check twice daily
- Review all trades
- Adjust if needed

**Days 4-7:**
- Reduce monitoring frequency
- Check daily
- Analyze performance
- Document any issues

### Scaling Up

**After 2 Weeks:**
- If profitable, consider increasing risk to 1%
- If losing, reduce risk or stop

**After 1 Month:**
- Evaluate overall performance
- Decide whether to continue
- Optimize parameters if needed

**After 3 Months:**
- Full performance review
- Consider strategy adjustments
- Document lessons learned

---

## Troubleshooting

### Common Issues

**Bot doesn't place trades:**
- Check if signals are being generated
- Verify trading is allowed in MT5
- Check if safety limits are hit
- Review log file for errors

**Orders are rejected:**
- Check lot size (too small/large?)
- Verify account has sufficient margin
- Check if symbol is tradable
- Review broker's requirements

**Trailing stops don't work:**
- Verify profit reached activation threshold
- Check if trailing is enabled in config
- Review log for trailing updates
- Ensure MT5 connection is stable

**Performance is poor:**
- Review market conditions
- Check if parameters need adjustment
- Verify strategy is suitable for current market
- Consider reducing risk or stopping

---

## Testing Logs

Keep a testing journal:

```
Date: 2026-01-27
Phase: Connection Testing
Result: ✅ All tests passed
Notes: MT5 connected successfully, symbols available

Date: 2026-01-28
Phase: Demo Trading Day 1
Result: ✅ 2 trades placed
Notes: Both trades had correct SL/TP, position sizing accurate

Date: 2026-01-29
Phase: Demo Trading Day 2
Result: ⚠️ 1 trade rejected
Notes: Lot size too small for broker, adjusted MIN_LOT_SIZE
```

---

## Final Validation

Before going live, answer these questions:

1. ✅ Have you tested for at least 2 weeks on demo?
2. ✅ Is the bot profitable on demo?
3. ✅ Do you understand all configuration options?
4. ✅ Have you verified all safety limits work?
5. ✅ Are you comfortable with the risk level?
6. ✅ Do you have a plan if things go wrong?
7. ✅ Can you afford to lose your trading capital?

If you answered YES to all questions, you're ready to go live!

If you answered NO to any question, continue testing until you're confident.

---

**Remember:** There's no rush. Better to test thoroughly than to lose money due to inadequate testing.
