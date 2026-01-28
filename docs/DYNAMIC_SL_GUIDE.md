# Dynamic Stop Loss Guide

## Overview

The **Dynamic Stop Loss Manager** automatically adjusts your stop loss in real-time based on trend changes and market conditions, instead of using fixed ATR multipliers.

---

## How It Works

### Traditional (Fixed) Stop Loss
```
Entry: 2700
ATR: 10
Multiplier: 2.0 (FIXED)
Stop Loss: 2680 (NEVER CHANGES until trailing activates)
```

### Dynamic Stop Loss
```
Entry: 2700
Initial SL: 2680 (2.0× ATR)

→ Trend strengthens → SL widens to 2675 (give trade more room)
→ Volatility expands → SL widens to 2670 (adapt to volatility)
→ Trend weakens → SL tightens to 2685 (protect profits)
→ MA crossover against → SL tightens to 2690 (exit signal)
→ Trend reversal → SL tightens to 2695 (close to breakeven)
```

---

## Adjustment Triggers

### 1. Trend Reversal (Highest Priority)
**When**: Price action shows trend reversing against your position
- Long: Lower highs + lower lows + bearish MA
- Short: Higher highs + higher lows + bullish MA

**Action**: Tighten SL significantly (0.5× ATR from current price)

**Example**:
```
Long position at 2700, current price 2710
Trend reversal detected
→ New SL: 2710 - (10 × 0.5) = 2705 (very tight!)
```

### 2. MA Crossover Against Position
**When**: Fast MA crosses slow MA in opposite direction
- Long: Fast MA crosses below slow MA (bearish)
- Short: Fast MA crosses above slow MA (bullish)

**Action**: Tighten SL moderately (1.0× ATR from current price)

**Example**:
```
Long position, bearish MA crossover
Current price: 2710
→ New SL: 2710 - (10 × 1.0) = 2700 (at breakeven)
```

### 3. Support/Resistance Break
**When**: Price breaks through key S/R level
- Long: Price breaks below support
- Short: Price breaks above resistance

**Action**: Move SL below/above the broken level

**Example**:
```
Long position, support at 2695 breaks
→ New SL: 2695 - (10 × 0.5) = 2690 (below broken support)
```

### 4. Swing High/Low Formation
**When**: New swing level forms
- Long: New swing low appears
- Short: New swing high appears

**Action**: Move SL to swing level ± 0.3× ATR

**Example**:
```
Long position, new swing low at 2685
→ New SL: 2685 - (10 × 0.3) = 2682 (just below swing)
```

### 5. Trend Strength Change

**Trend Strengthening** (with your position):
- **Action**: Widen SL (give trade more room)
- **Example**: SL 2680 → 2675 (wider)

**Trend Weakening** (against your position):
- **Action**: Tighten SL (protect profits)
- **Example**: SL 2680 → 2690 (tighter)

### 6. Volatility Changes

**Volatility Expansion** (ATR increases 30%+):
- **Action**: Widen SL to accommodate larger swings
- **Example**: SL 2680 → 2675

**Volatility Contraction** (ATR decreases 30%+):
- **Action**: Tighten SL as market calms
- **Example**: SL 2680 → 2685

---

## Priority System

When multiple triggers occur, the system uses this priority:

1. **Trend Reversal** (most urgent)
2. **MA Crossover**
3. **S/R Break**
4. **Swing Level**
5. **Trend Weakening**
6. **Volatility Contraction**
7. **Trend Strengthening**
8. **Volatility Expansion** (least urgent)

---

## Safety Rules

### SL Can Only Move in Favorable Direction
- **Long positions**: SL can only move UP (tighter), never down
- **Short positions**: SL can only move DOWN (tighter), never up

### Minimum Change Threshold
- SL must change by at least 0.1% to be applied
- Prevents tiny, unnecessary adjustments

### Never Move SL Past Current Price
- Long: SL always stays below current price
- Short: SL always stays above current price

---

## Configuration

### Enable Dynamic SL

Add to `src/config.py`:
```python
# Dynamic Stop Loss
USE_DYNAMIC_SL = True           # Enable dynamic SL adjustments
DYNAMIC_SL_CHECK_INTERVAL = 60  # Check every 60 seconds
```

### Integration with Main Bot

The dynamic SL manager works alongside:
- ✅ Adaptive Risk Management (initial SL calculation)
- ✅ Trailing Stops (profit protection)
- ✅ Split Orders (manages all positions in group)

**Flow**:
1. Adaptive Risk sets initial SL based on market type
2. Dynamic SL adjusts based on trend changes
3. Trailing Stop activates when profit target reached

---

## Real-World Example

### Scenario: XAUUSD Long Trade

**Initial Setup**:
```
Entry: 2700
Initial SL: 2680 (2.0× ATR, strong trend)
TP1: 2724 (40% position)
TP2: 2736 (30% position)
TP3: 2750 (30% position)
```

**Timeline**:

**T+5 min**: Price at 2705
- No changes, trend still strong
- SL remains: 2680

**T+10 min**: Price at 2710, volatility expands
- ATR increases from 10 to 13
- **Dynamic SL**: Widen to 2677 (accommodate volatility)

**T+15 min**: Price at 2715, trend strengthening
- Market type changes to "very strong trend"
- **Dynamic SL**: Widen to 2672 (give trade more room)

**T+20 min**: Price at 2720, swing low forms at 2705
- New swing low identified
- **Dynamic SL**: Move to 2702 (just below swing)

**T+25 min**: Price at 2724, TP1 hit!
- 40% of position closes at 2724
- Remaining 60% continues

**T+30 min**: Price at 2722, fast MA crosses below slow MA
- **Bearish crossover detected!**
- **Dynamic SL**: Tighten to 2712 (1.0× ATR from current)

**T+35 min**: Price at 2718, trend reversal pattern
- Lower highs forming
- **Trend reversal detected!**
- **Dynamic SL**: Tighten to 2713 (0.5× ATR from current)

**T+40 min**: Price drops to 2713
- **Stop loss hit**, remaining 60% exits at 2713

**Result**:
- Position 1 (40%): +24 points profit (TP1 hit)
- Position 2+3 (60%): +13 points profit (dynamic SL)
- **Total**: Better than fixed SL at 2680!

---

## Comparison: Fixed vs Dynamic SL

### Fixed SL (Current System)
```
Entry: 2700
SL: 2680 (NEVER CHANGES)

Scenario 1: Price drops to 2680
→ Loss: -20 points

Scenario 2: Trend reverses at 2710
→ Price drops to 2680
→ Loss: -20 points (could have exited at 2710!)
```

### Dynamic SL (New System)
```
Entry: 2700
Initial SL: 2680

Scenario 1: Price drops to 2680
→ Loss: -20 points (same as fixed)

Scenario 2: Trend reverses at 2710
→ Dynamic SL tightens to 2705
→ Exit at 2705
→ Profit: +5 points (saved 25 points!)
```

---

## Benefits

### 1. Adapts to Market Changes
- Responds to trend reversals immediately
- Adjusts for volatility changes
- Follows market structure

### 2. Protects Profits Better
- Tightens SL when trend weakens
- Locks in gains before major reversals
- Exits near breakeven instead of full loss

### 3. Gives Winning Trades Room
- Widens SL when trend strengthens
- Accommodates volatility spikes
- Reduces premature stop-outs

### 4. Intelligent Exit Signals
- Uses MA crossovers as exit signals
- Respects support/resistance levels
- Follows swing highs/lows

---

## When to Use

### ✅ Use Dynamic SL When:
- Trading trending markets (M5, M15, H1)
- Want to adapt to changing conditions
- Experiencing premature stop-outs
- Want better profit protection

### ❌ Don't Use Dynamic SL When:
- Trading very short timeframes (M1)
- Want simple, predictable stops
- Market is extremely volatile (may adjust too often)
- Testing new strategy (use fixed first)

---

## Configuration Examples

### Conservative (Slow Adjustments)
```python
USE_DYNAMIC_SL = True
DYNAMIC_SL_CHECK_INTERVAL = 120  # Check every 2 minutes
ATR_MULTIPLIER_SL = 2.5          # Start with wider stops
```

### Balanced (Recommended)
```python
USE_DYNAMIC_SL = True
DYNAMIC_SL_CHECK_INTERVAL = 60   # Check every minute
ATR_MULTIPLIER_SL = 2.0          # Standard stops
```

### Aggressive (Fast Adjustments)
```python
USE_DYNAMIC_SL = True
DYNAMIC_SL_CHECK_INTERVAL = 30   # Check every 30 seconds
ATR_MULTIPLIER_SL = 1.5          # Start with tighter stops
```

---

## How to Enable

### Step 1: Update Config
Add to `src/config.py`:
```python
# Dynamic Stop Loss Management
USE_DYNAMIC_SL = True
DYNAMIC_SL_CHECK_INTERVAL = 60
```

### Step 2: Bot Will Auto-Enable
The bot automatically uses dynamic SL when:
- `USE_DYNAMIC_SL = True`
- `USE_ADAPTIVE_RISK = True` (for market analysis)

### Step 3: Monitor Logs
Watch for log messages:
```
INFO - Dynamic SL updated for XAUUSD (Ticket: 123456)
INFO -   Old SL: 2680.00 → New SL: 2705.00
INFO -   Reason: Trend reversal detected
```

---

## Summary

**Dynamic SL** = Smart stop loss that adapts to market conditions

**Key Features**:
- ✅ Adjusts based on trend changes
- ✅ Responds to volatility
- ✅ Follows market structure
- ✅ Protects profits better
- ✅ Reduces premature exits

**Best For**: M5+ timeframes with trending markets

**Result**: Better risk management and improved profitability!
