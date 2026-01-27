# Trailing Stop Strategies - Quick Reference Guide

## Overview
This guide explains the different trailing stop strategies available in the MT5 Trading Bot and when to use each one.

---

## 1. ATR Trailing Stop (Default)
**Best for**: Volatile markets, adapts to changing volatility

### How it works:
- Trails at a distance of `ATR × Multiplier` from current price
- Automatically adjusts to market volatility
- Wider stops in volatile markets, tighter in calm markets

### Configuration:
```python
TRAIL_TYPE = 'atr'
TRAIL_DISTANCE_ATR = 1.0  # Distance = 1 × ATR
TRAIL_ACTIVATION_ATR = 1.5  # Activate after 1.5 × ATR profit
```

### Example (Gold at $2000):
```
Entry: $2000
ATR: $10
Profit reaches $2015 (1.5 × ATR) → Trailing activates
Price moves to $2030 → SL moves to $2020 ($2030 - $10)
Price moves to $2040 → SL moves to $2030 ($2040 - $10)
```

### Pros:
✅ Adapts to volatility
✅ Prevents being stopped out by normal fluctuations
✅ Good for gold/silver (volatile commodities)

### Cons:
❌ May give back more profit in rapidly reversing markets
❌ Requires ATR calculation

---

## 2. Percentage Trailing Stop
**Best for**: Consistent risk management, simple implementation

### How it works:
- Trails at a fixed percentage from current price
- Simple and predictable
- Doesn't adapt to volatility

### Configuration:
```python
TRAIL_TYPE = 'percentage'
TRAIL_PERCENT = 2.0  # Trail 2% from current price
```

### Example (Gold at $2000):
```
Entry: $2000 (BUY)
Price moves to $2100 → SL = $2100 - 2% = $2058
Price moves to $2150 → SL = $2150 - 2% = $2107
Price drops to $2120 → SL stays at $2107 (never widens)
```

### Pros:
✅ Very simple to understand
✅ Predictable profit protection
✅ No indicator calculations needed

### Cons:
❌ Doesn't adapt to volatility
❌ May be too tight in volatile markets
❌ May be too wide in calm markets

---

## 3. Swing High/Low Trailing
**Best for**: Trend-following, respecting market structure

### How it works:
- For BUY: Trails below recent swing lows
- For SELL: Trails above recent swing highs
- Respects natural support/resistance levels

### Configuration:
```python
TRAIL_TYPE = 'swing'
SWING_LOOKBACK = 10  # Look back 10 bars for swing points
```

### Example (Gold BUY):
```
Entry: $2000
Recent swing lows: $2010, $2025, $2030
SL placed at: $2010 (lowest swing low)
Price creates new swing low at $2040
SL moves to: $2025 (new lowest swing low)
```

### Pros:
✅ Follows market structure
✅ Gives trades "breathing room"
✅ Less likely to be stopped by minor retracements

### Cons:
❌ Can be quite wide
❌ May give back significant profit
❌ Requires clear swing points

---

## 4. Chandelier Exit
**Best for**: Momentum trading, trending markets

### How it works:
- For BUY: Highest High - (ATR × Multiplier)
- For SELL: Lowest Low + (ATR × Multiplier)
- Combines price action with volatility

### Configuration:
```python
TRAIL_TYPE = 'chandelier'
CHANDELIER_PERIOD = 14
CHANDELIER_MULTIPLIER = 3.0
```

### Example (Gold BUY):
```
Entry: $2000
Highest high (14 bars): $2050
ATR: $10
SL = $2050 - (3 × $10) = $2020

New highest high: $2080
SL moves to: $2080 - $30 = $2050
```

### Pros:
✅ Excellent for strong trends
✅ Locks in profits as new highs/lows form
✅ Volatility-adjusted

### Cons:
❌ Can be stopped out in ranging markets
❌ Requires strong directional movement
❌ May exit good trades during consolidation

---

## 5. Breakeven Plus Trailing
**Best for**: Conservative traders, risk elimination

### How it works:
- Stage 1: Initial stop loss
- Stage 2: Move to breakeven + small profit
- Stage 3: Start normal trailing

### Configuration:
```python
TRAIL_TYPE = 'breakeven'
BREAKEVEN_ACTIVATION_PIPS = 100  # Move to BE after 100 pips profit
BREAKEVEN_PLUS_PIPS = 10         # Lock in 10 pips
TRAIL_START_PIPS = 150           # Start trailing after 150 pips
```

### Example (Gold at $2000):
```
Entry: $2000 (BUY)
Initial SL: $1980

Price reaches $2100 (100 pips) → Move SL to $2010 (BE + 10 pips)
Price reaches $2150 (150 pips) → Start normal trailing
Price at $2180 → Trail with ATR or percentage method
```

### Pros:
✅ Eliminates risk quickly
✅ Psychological comfort (can't lose)
✅ Good for beginners

### Cons:
❌ May exit winning trades early
❌ Gives up some profit potential
❌ Multiple stages to manage

---

## 6. Step Trailing
**Best for**: Systematic profit locking, predictable management

### How it works:
- SL moves in fixed increments (steps)
- Only moves after price moves X pips
- Locks profit systematically

### Configuration:
```python
TRAIL_TYPE = 'step'
STEP_SIZE = 50          # Move SL after 50 pips profit
TRAIL_DISTANCE = 30     # Keep SL 30 pips away
```

### Example (Gold at $2000):
```
Entry: $2000 (BUY)
Initial SL: $1980

Price reaches $2050 (50 pips) → SL moves to $2020 (entry + 20)
Price reaches $2100 (100 pips) → SL moves to $2070 (entry + 70)
Price reaches $2150 (150 pips) → SL moves to $2120 (entry + 120)
```

### Pros:
✅ Very systematic
✅ Easy to backtest
✅ Predictable profit locking

### Cons:
❌ Arbitrary step sizes
❌ Doesn't adapt to volatility
❌ May lock in too early or too late

---

## Strategy Comparison Table

| Strategy | Volatility Adaptation | Complexity | Best Market | Profit Protection |
|----------|----------------------|------------|-------------|-------------------|
| ATR Trailing | ✅ High | Medium | Trending/Volatile | Good |
| Percentage | ❌ None | Low | Stable trends | Moderate |
| Swing H/L | ⚠️ Indirect | Medium | Strong trends | Variable |
| Chandelier | ✅ High | Medium | Momentum | Excellent |
| Breakeven+ | ❌ None | High | Any | Conservative |
| Step | ❌ None | Low | Trending | Systematic |

---

## Choosing the Right Strategy

### For Gold & Silver (Recommended):
1. **Primary choice**: ATR Trailing
   - Gold/Silver are volatile
   - ATR adapts automatically
   - Works in most conditions

2. **Conservative traders**: Breakeven Plus
   - Eliminates risk quickly
   - Good for peace of mind
   - May miss some profits

3. **Trend followers**: Chandelier Exit
   - Excellent in strong trends
   - Maximizes trend profits
   - Can whipsaw in ranges

### Market Conditions:

**Volatile Markets** (ATR > average):
- Use ATR Trailing with higher multiplier (1.5-2.0)
- Consider Chandelier Exit
- Avoid tight percentage trailing

**Calm Markets** (ATR < average):
- Percentage trailing works well
- Tighter ATR multipliers (0.8-1.0)
- Step trailing is effective

**Trending Markets**:
- Chandelier Exit (best)
- ATR Trailing
- Swing High/Low

**Ranging Markets**:
- Percentage trailing
- Breakeven Plus
- Avoid Chandelier (stops too easily)

---

## Combining Strategies

You can use different strategies for different stages:

### Example Hybrid Approach:
```python
# Stage 1: Initial entry
if profit_pips < 100:
    # Use fixed initial SL
    
# Stage 2: Risk elimination
elif 100 <= profit_pips < 150:
    # Move to breakeven + 10 pips
    
# Stage 3: Profit maximization
else:
    # Use ATR trailing or Chandelier
```

---

## Testing Recommendations

### Before live trading:
1. Backtest each strategy with historical data
2. Compare win rates and average profit
3. Test in different market conditions
4. Consider your trading personality

### Key metrics to track:
- Average winning trade
- Average losing trade
- Win rate
- Profit factor
- Maximum drawdown
- Time in trades

---

## Quick Start Commands

### Test ATR Trailing (Default):
```python
config['trail_type'] = 'atr'
config['trail_distance'] = 1.0
config['trail_activation'] = 1.5
```

### Test Breakeven Plus:
```python
config['trail_type'] = 'breakeven'
config['breakeven_activation_pips'] = 100
config['breakeven_plus_pips'] = 10
config['trail_start_pips'] = 150
```

### Test Percentage:
```python
config['trail_type'] = 'percentage'
config['trail_percent'] = 2.0
```

---

## Advanced: Dynamic Strategy Selection

You can implement logic to choose strategy based on market conditions:

```python
# Calculate market volatility
current_atr = df.iloc[-1]['atr']
avg_atr = df['atr'].rolling(50).mean().iloc[-1]

# High volatility → Use ATR trailing with wider stops
if current_atr > avg_atr * 1.5:
    trail_type = 'atr'
    trail_distance = 1.5
    
# Normal volatility → Use ATR trailing standard
elif current_atr > avg_atr * 0.8:
    trail_type = 'atr'
    trail_distance = 1.0
    
# Low volatility → Use percentage trailing
else:
    trail_type = 'percentage'
    trail_percent = 1.5
```

---

**Remember**: No single trailing strategy works best in all conditions. Test thoroughly and choose based on your risk tolerance and market conditions!
