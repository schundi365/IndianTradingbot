# Split Orders & Partial Profit Taking Guide

## Overview

The split order system allows you to divide your total position into multiple smaller orders, each with its own take profit level. This strategy helps you:

1. **Lock in profits progressively** - Take partial profits at different levels
2. **Let winners run** - Keep part of the position for bigger moves
3. **Reduce regret** - Balance between taking profits early and holding for more
4. **Better risk management** - Adapt to market conditions dynamically

---

## How It Works

### Traditional Single Position
```
Entry: $2000
Stop Loss: $1980 (risking $20)
Take Profit: $2040 (targeting $40 - 1:2 R:R)
Total Lots: 0.10
```

**Problem**: All-or-nothing - either hit TP or SL, no middle ground.

### Split Position Approach
```
Entry: $2000
Stop Loss: $1980 (risking $20)
Total Lots: 0.10

Position 1: 0.04 lots, TP at $2030 (1.5:1 R:R) - 40% of position
Position 2: 0.03 lots, TP at $2050 (2.5:1 R:R) - 30% of position
Position 3: 0.03 lots, TP at $2080 (4.0:1 R:R) - 30% of position
```

**Benefit**: Progressive profit-taking adapts to market momentum!

---

## Configuration Explained

### Basic Settings

```python
USE_SPLIT_ORDERS = True     # Enable split order system
NUM_POSITIONS = 3           # Split into 3 separate orders
```

### Take Profit Levels

```python
TP_LEVELS = [1.5, 2.5, 4.0]
```

These are **Risk:Reward ratios**:
- `1.5` = Take profit at 1.5x your risk distance
- `2.5` = Take profit at 2.5x your risk distance
- `4.0` = Take profit at 4.0x your risk distance

**Example Calculation**:
```
Entry: $2000 (BUY)
Stop Loss: $1980 (risk = $20)

TP1 = $2000 + ($20 × 1.5) = $2030
TP2 = $2000 + ($20 × 2.5) = $2050
TP3 = $2000 + ($20 × 4.0) = $2080
```

### Position Allocation

```python
PARTIAL_CLOSE_PERCENT = [40, 30, 30]
```

This determines **what percentage of your total position** closes at each TP:
- `40%` closes at first TP (quick profit)
- `30%` closes at second TP (moderate target)
- `30%` closes at third TP (let it run)

**Must sum to 100%!**

---

## Position Sizing Logic

The bot automatically calculates lot sizes based on your **available funds** and **risk percentage**.

### Step-by-Step Calculation

#### 1. Calculate Total Risk Amount
```python
Account Balance: $10,000
Risk Percent: 1%
Total Risk Amount = $10,000 × 1% = $100
```

#### 2. Calculate Total Lot Size
```python
Entry Price: $2000
Stop Loss: $1980
Risk Distance: $20

# For gold (XAUUSD), pip value varies by lot size
# Simplified: If 0.01 lot = $0.10 per pip
# $20 = 200 pips (for gold pricing)

Total Lots = $100 / ($20 per 0.01 lot × 100)
Total Lots ≈ 0.50 lots
```

#### 3. Check Available Margin
```python
Free Margin: $5,000
Required Margin (0.50 lots): $2,000
Available? Yes

# If not enough margin, reduce lot size:
Max Lots = (Free Margin × 0.8 × Leverage) / (Contract Size × Entry Price)
```

#### 4. Split Into Multiple Orders
```python
Total Lots: 0.50
Allocation: [40%, 30%, 30%]

Position 1: 0.50 × 40% = 0.20 lots
Position 2: 0.50 × 30% = 0.15 lots
Position 3: 0.50 × 30% = 0.15 lots
```

#### 5. Check Max Lot Per Order Limit
```python
MAX_LOT_PER_ORDER = 0.5

Position 1: 0.20 lots ✓ (within limit)
Position 2: 0.15 lots ✓ (within limit)
Position 3: 0.15 lots ✓ (within limit)
```

---

## Real-World Example

### Scenario: Gold Trade

**Account Details**:
- Balance: $5,000
- Free Margin: $3,000
- Risk: 1% per trade

**Market Conditions**:
- Gold (XAUUSD): $2,100
- ATR: $15
- Signal: BUY

**Bot Calculations**:

1. **Stop Loss**:
   ```
   SL = Entry - (ATR × Multiplier)
   SL = $2,100 - ($15 × 2.0)
   SL = $2,070
   Risk = $30
   ```

2. **Total Position Size**:
   ```
   Risk Amount = $5,000 × 1% = $50
   
   # Simplified calculation
   Total Lots ≈ 0.30 lots
   ```

3. **Take Profit Levels**:
   ```
   TP1 = $2,100 + ($30 × 1.5) = $2,145
   TP2 = $2,100 + ($30 × 2.5) = $2,175
   TP3 = $2,100 + ($30 × 4.0) = $2,220
   ```

4. **Split Allocation**:
   ```
   Position 1: 0.12 lots @ TP $2,145 (40%)
   Position 2: 0.09 lots @ TP $2,175 (30%)
   Position 3: 0.09 lots @ TP $2,220 (30%)
   ```

### Trade Outcomes

**Scenario A: Price reaches $2,145**
- Position 1 closes: +$45 profit (0.12 lots × $45)
- Positions 2 & 3 still open
- **Profit locked**: $45
- **Risk**: Moved to breakeven on remaining positions

**Scenario B: Price reaches $2,175**
- Position 1 closed: +$45
- Position 2 closes: +$75 (0.09 lots × $75)
- Position 3 still open
- **Total profit locked**: $120

**Scenario C: Price reaches $2,220**
- All positions close
- **Total profit**: $45 + $75 + $108 = $228

**Scenario D: Price reverses after $2,145**
- Position 1 closed: +$45
- Positions 2 & 3 hit trailing SL at $2,130 (moved to breakeven)
- **Total outcome**: +$45 (instead of full loss!)

---

## Strategy Presets

### Conservative (Quick Profits)
```python
TP_LEVELS = [1.0, 2.0, 3.0]
PARTIAL_CLOSE_PERCENT = [50, 30, 20]
```
- 50% closes at 1:1 (quick exit)
- Good for ranging markets
- Lower profit potential but higher win rate

### Balanced (Default)
```python
TP_LEVELS = [1.5, 2.5, 4.0]
PARTIAL_CLOSE_PERCENT = [40, 30, 30]
```
- Balanced approach
- Good for most market conditions
- Moderate profit potential

### Aggressive (Let It Run)
```python
TP_LEVELS = [2.0, 3.5, 6.0]
PARTIAL_CLOSE_PERCENT = [30, 30, 40]
```
- Larger portion held for big moves
- Good for strong trending markets
- Higher profit potential but lower win rate

### Scalper (Many Small Exits)
```python
NUM_POSITIONS = 5
TP_LEVELS = [0.8, 1.2, 1.8, 2.5, 4.0]
PARTIAL_CLOSE_PERCENT = [30, 25, 20, 15, 10]
```
- Many small profit targets
- Very gradual exit
- Good for volatile markets

---

## Advantages of Split Orders

### 1. Psychological Benefits
✅ Less stress - always locking in some profit  
✅ Reduces FOMO - still have exposure for big moves  
✅ Less second-guessing - automated decisions  

### 2. Statistical Improvements
✅ Higher win rate - easier to hit first TP  
✅ Better profit factor - partial profits add up  
✅ Smoother equity curve - less volatility  

### 3. Flexibility
✅ Adapts to different market conditions  
✅ Combines conservative and aggressive strategies  
✅ Can customize for each symbol  

---

## Disadvantages & Considerations

### 1. Spread Costs
❌ Pay spread multiple times (3 orders = 3× spread)  
❌ More significant in high-spread pairs  
**Solution**: Use for gold/silver where spreads are reasonable

### 2. Commission Costs
❌ Some brokers charge per trade  
❌ 3 orders = 3× commission  
**Solution**: Calculate if split strategy outperforms commission cost

### 3. Complexity
❌ More positions to manage  
❌ More data to track  
**Solution**: Bot handles this automatically!

### 4. Broker Limitations
❌ Some brokers have minimum distance between TP levels  
❌ Order minimums may affect small accounts  
**Solution**: Adjust TP_LEVELS spacing, check broker specs

---

## Advanced Tips

### 1. Adjust for Volatility

**High Volatility** (ATR > Average):
```python
# Wider spacing needed
TP_LEVELS = [2.0, 4.0, 7.0]
```

**Low Volatility** (ATR < Average):
```python
# Tighter spacing works
TP_LEVELS = [1.2, 2.0, 3.0]
```

### 2. Trailing Stops Work on All Positions

The bot trails the stop loss for **all positions together**:
- When profit reaches 1.5× ATR, all positions trail
- Stop loss moves together for consistency
- Protects remaining positions as price moves favorably

### 3. Symbol-Specific Settings

You can create different configs for different symbols:

```python
if symbol == 'XAUUSD':  # Gold - more volatile
    tp_levels = [2.0, 3.5, 6.0]
elif symbol == 'XAGUSD':  # Silver - even more volatile
    tp_levels = [2.5, 4.5, 8.0]
```

### 4. Time-Based Adjustments

```python
# During high-impact news
TP_LEVELS = [1.0, 1.5, 2.0]  # Take profits quickly

# During quiet sessions
TP_LEVELS = [1.5, 3.0, 5.0]  # Let them run
```

---

## Monitoring Your Split Positions

### In MT5 Terminal

You'll see multiple positions for one signal:
```
XAUUSD BUY 0.12 @ 2100, SL: 2070, TP: 2145  [MT5Bot_Split_a3f7_1]
XAUUSD BUY 0.09 @ 2100, SL: 2070, TP: 2175  [MT5Bot_Split_a3f7_2]
XAUUSD BUY 0.09 @ 2100, SL: 2070, TP: 2220  [MT5Bot_Split_a3f7_3]
```

The `_a3f7_` is the group ID - all positions with same ID are from one signal.

### In Bot Logs

```
Opening split positions for XAUUSD:
  Group ID: a3f7
  Total lots: 0.30, Split into: [0.12, 0.09, 0.09]
  TP levels: [2145.0, 2175.0, 2220.0]
  Position 1: 0.12 lots at 2100.0, TP: 2145.0 (Ticket: 123456)
  Position 2: 0.09 lots at 2100.0, TP: 2175.0 (Ticket: 123457)
  Position 3: 0.09 lots at 2100.0, TP: 2220.0 (Ticket: 123458)
Successfully opened 3 split positions (Group: a3f7)
```

---

## Common Issues & Solutions

### Issue: Positions too small (less than min lot)
**Solution**: 
- Increase account balance
- Increase risk percentage
- Reduce number of splits (NUM_POSITIONS = 2)

### Issue: "Not enough margin" error
**Solution**:
- Reduce total lot size (lower RISK_PERCENT)
- Close other positions
- Reduce MAX_LOT_PER_ORDER
- Check broker leverage

### Issue: First TP too close, keeps hitting
**Solution**:
- Increase first TP level (e.g., 1.5 → 2.0)
- This is actually good - locking profits!
- Adjust if it's TOO frequent

### Issue: Last TP never hits
**Solution**:
- Reduce final TP level (e.g., 4.0 → 3.0)
- Increase allocation to middle TPs
- This is normal in ranging markets

---

## Backtesting Recommendations

Before going live, test your split strategy:

### Metrics to Track

1. **Hit Rate by TP Level**
   - How often does TP1 hit? TP2? TP3?
   - Adjust levels based on data

2. **Average Profit per TP Level**
   - Which TP contributes most profit?
   - Adjust allocation accordingly

3. **Comparison vs Single TP**
   - Does split strategy outperform?
   - Account for extra spread costs

4. **Optimal Allocation**
   - Test different PARTIAL_CLOSE_PERCENT combinations
   - Find what works for your symbols

### Example Test Results

```
Single TP (1:2 R:R):
- Win Rate: 45%
- Avg Win: $80
- Avg Loss: $40
- Profit Factor: 1.8

Split TP [1.5, 2.5, 4.0]:
- Win Rate: 62% (TP1), 38% (TP2), 18% (TP3)
- Avg Win: $75 (combined)
- Avg Loss: $25 (protected by TP1)
- Profit Factor: 2.3

Winner: Split TP! ✓
```

---

## Quick Start

1. **Enable split orders** in config.py:
   ```python
   USE_SPLIT_ORDERS = True
   ```

2. **Choose your strategy**:
   - Conservative, Balanced, or Aggressive preset
   - Or customize your own

3. **Set position limits**:
   ```python
   MAX_LOT_PER_ORDER = 0.5  # Broker-specific
   ```

4. **Test on demo** first!

5. **Monitor and adjust** based on results

---

## Summary

Split orders transform your trading from "all-or-nothing" to "progressive profit-taking":

- **Locks in profits early** while keeping exposure for big moves
- **Automatically calculated** based on your account size
- **Reduces risk** by taking partial profits
- **Adapts to market conditions** through TP levels
- **Psychological edge** - less stress, more confidence

The bot handles all the complexity - you just configure your preferences!

**Remember**: No strategy works 100% of the time. Split orders improve your odds, but proper risk management is still essential. Never risk more than you can afford to lose!

---

**Ready to use split orders?** Check your config.py and run the bot! 🚀
