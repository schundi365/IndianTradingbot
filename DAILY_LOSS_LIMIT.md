# Daily Loss Limit Feature

## Overview

The bot now includes an intelligent daily loss limit that stops trading when losses reach **3% of current equity** per day. This protects your account from excessive losses during bad market conditions.

---

## How It Works

### Real-Time Monitoring
- Bot checks daily P/L before each new trade
- Calculates loss as percentage of **current equity** (not balance)
- Automatically pauses trading when limit is reached

### Calculation Method
```
Daily Loss % = |Daily P/L| / Current Equity × 100

Example:
- Current Equity: $50,000
- Daily P/L: -$1,500
- Loss %: 1,500 / 50,000 × 100 = 3.0%
- Result: Trading paused
```

### Dynamic Limit
- Limit is based on **current equity**, not starting balance
- Adapts to account growth/shrinkage
- More protective as account grows

---

## Configuration

### Current Setting
```python
# In src/config.py
MAX_DAILY_LOSS_PERCENT = 3.0  # Stop at 3% daily loss
```

### Adjust if Needed
```python
# Conservative (recommended for live)
MAX_DAILY_LOSS_PERCENT = 2.0  # Stop at 2%

# Moderate (current setting)
MAX_DAILY_LOSS_PERCENT = 3.0  # Stop at 3%

# Aggressive (not recommended)
MAX_DAILY_LOSS_PERCENT = 5.0  # Stop at 5%
```

---

## Features

### 1. Automatic Pause
When daily loss reaches 3%:
- ✅ Bot stops opening new positions
- ✅ Existing positions continue to be managed
- ✅ Trailing stops still active
- ✅ Resumes automatically next day

### 2. Early Warning
At 80% of limit (2.4% loss):
- ⚠️ Warning logged
- Shows remaining loss allowance
- Helps you monitor closely

### 3. Daily Reset
- Limit resets at midnight (00:00)
- Fresh start each trading day
- Previous day's losses don't carry over

---

## Example Scenarios

### Scenario 1: Normal Trading Day
```
Starting Equity: $50,000
Max Loss: $1,500 (3%)

Trade 1: -$200 (0.4% loss)
Trade 2: -$150 (0.3% loss)
Trade 3: +$300 (0.6% profit)
Trade 4: -$100 (0.2% loss)

Daily P/L: -$150 (0.3% loss)
Status: ✅ Continue trading
```

### Scenario 2: Bad Trading Day
```
Starting Equity: $50,000
Max Loss: $1,500 (3%)

Trade 1: -$400 (0.8% loss)
Trade 2: -$350 (0.7% loss)
Trade 3: -$450 (0.9% loss)
Trade 4: -$300 (0.6% loss)

Daily P/L: -$1,500 (3.0% loss)
Status: 🛑 Trading paused
Message: "Daily loss limit reached: 3.00% (Max: 3.0%)"
```

### Scenario 3: Approaching Limit
```
Starting Equity: $50,000
Max Loss: $1,500 (3%)

Trade 1: -$500 (1.0% loss)
Trade 2: -$600 (1.2% loss)

Daily P/L: -$1,100 (2.2% loss)
Status: ⚠️ Warning issued
Message: "Approaching daily loss limit: 2.20% of 3.0%"
Remaining: $400 before pause
```

---

## Log Messages

### Normal Operation
```
INFO - Daily P/L: -$500.00, Equity: $50,000.00
INFO - Daily loss: 1.00% (Max: 3.0%)
```

### Warning (80% of limit)
```
WARNING - Approaching daily loss limit: 2.40% of 3.0%
WARNING - Daily P/L: -$1,200.00, Remaining: $300.00
```

### Limit Reached
```
WARNING - Daily loss limit reached: 3.00% (Max: 3.0%)
WARNING - Daily P/L: -$1,500.00, Equity: $50,000.00
WARNING - Trading paused for today. Will resume tomorrow.
```

---

## Benefits

### 1. Account Protection
- Prevents catastrophic daily losses
- Limits damage during bad market conditions
- Protects against strategy failures

### 2. Emotional Control
- Removes emotion from stopping
- Automatic enforcement
- No manual intervention needed

### 3. Risk Management
- Consistent daily risk limit
- Adapts to account size
- Professional-grade protection

### 4. Recovery Time
- Gives time to analyze what went wrong
- Prevents revenge trading
- Fresh start next day

---

## Best Practices

### 1. Set Appropriate Limit
```python
# Account Size Based
Small account (<$10k): 2.0%
Medium account ($10k-$50k): 3.0%
Large account (>$50k): 2.0%
```

### 2. Monitor Warnings
- Pay attention to 80% warnings
- Review trades when approaching limit
- Consider manual pause if needed

### 3. Analyze Stopped Days
When trading is paused:
1. Review all trades from that day
2. Check market conditions
3. Verify strategy is working
4. Adjust parameters if needed

### 4. Don't Override
- Resist urge to disable limit
- Trust the protection system
- Bad days happen - accept them

---

## Technical Details

### Calculation Timing
- Checked before each new trade
- Uses real-time equity value
- Includes all closed deals from today

### What's Included
- ✅ Closed trade P/L
- ✅ Commissions and swaps
- ✅ All bot trades (magic number)
- ❌ Open position P/L (not counted)
- ❌ Manual trades (different magic)

### Reset Timing
- Resets at 00:00 server time
- Based on MT5 server timezone
- Usually UTC or broker timezone

---

## Comparison with Other Limits

### Daily Loss Limit (NEW)
- **Type**: Percentage of equity
- **Resets**: Daily
- **Purpose**: Prevent bad days
- **Action**: Pause trading

### Max Drawdown
- **Type**: Percentage from peak
- **Resets**: Never (until new peak)
- **Purpose**: Protect from extended losses
- **Action**: Pause trading

### Max Daily Trades
- **Type**: Trade count
- **Resets**: Daily
- **Purpose**: Prevent overtrading
- **Action**: Stop new trades

### Risk Per Trade
- **Type**: Percentage per position
- **Resets**: Per trade
- **Purpose**: Limit single trade risk
- **Action**: Reduce position size

---

## FAQ

### Q: What if I'm close to limit but have a good signal?
**A**: The limit is enforced automatically. If you're at 2.9% loss, one more losing trade could exceed 3%. The system protects you from "one more trade" syndrome.

### Q: Can I override the limit?
**A**: Yes, by increasing `MAX_DAILY_LOSS_PERCENT` in config, but **not recommended**. The limit exists to protect you.

### Q: Does it count open positions?
**A**: No, only closed trades count. Open positions are managed normally with trailing stops.

### Q: What if I have a winning day?
**A**: No limit on profits! The limit only applies to losses.

### Q: When does it reset?
**A**: At midnight (00:00) server time. Fresh start each day.

### Q: What about weekends?
**A**: Limit resets each day, including weekends. Monday starts fresh regardless of Friday's performance.

---

## Example Configuration

### Conservative Setup
```python
# For live trading or small accounts
MAX_DAILY_LOSS_PERCENT = 2.0    # Stop at 2%
RISK_PERCENT = 0.1              # Risk 0.1% per trade
MAX_TRADES_TOTAL = 3            # Max 3 positions
```

### Moderate Setup (Current)
```python
# For demo or medium accounts
MAX_DAILY_LOSS_PERCENT = 3.0    # Stop at 3%
RISK_PERCENT = 0.2              # Risk 0.2% per trade
MAX_TRADES_TOTAL = 6            # Max 6 positions
```

### Aggressive Setup
```python
# For testing only
MAX_DAILY_LOSS_PERCENT = 5.0    # Stop at 5%
RISK_PERCENT = 0.3              # Risk 0.3% per trade
MAX_TRADES_TOTAL = 10           # Max 10 positions
```

---

## Summary

**Daily Loss Limit** = Smart protection that stops trading at 3% daily loss

**Key Features**:
- ✅ Automatic enforcement
- ✅ Based on current equity
- ✅ Resets daily
- ✅ Early warning at 80%
- ✅ Prevents bad days from getting worse

**Result**: Professional-grade account protection!
