# Position Size, Stop Loss & Take Profit Calculation Guide

## Overview

The bot uses a **risk-based position sizing** approach with **ATR-based stop losses** and **risk:reward ratio take profits**. This ensures consistent risk management across all trades.

---

## 1. Stop Loss Calculation (ATR-Based)

### Formula
```
For BUY:  Stop Loss = Entry Price - (ATR × ATR Multiplier)
For SELL: Stop Loss = Entry Price + (ATR × ATR Multiplier)
```

### How It Works

**ATR (Average True Range)**: Measures market volatility
- Calculated over 14 periods (configurable)
- Higher ATR = more volatile market = wider stops
- Lower ATR = calmer market = tighter stops

**ATR Multiplier**: Controls stop loss width
- Current M1 config: **1.2x ATR** (very tight)
- Optimized M5 config: **2.0x ATR** (wider, better)
- Higher multiplier = more room for price to move

### Example (XAUUSD)

**Scenario**: BUY Gold at 2,700
- ATR = 10 points
- ATR Multiplier = 2.0
- **Stop Loss = 2,700 - (10 × 2.0) = 2,680**

**Scenario**: SELL Gold at 2,700
- ATR = 10 points
- ATR Multiplier = 2.0
- **Stop Loss = 2,700 + (10 × 2.0) = 2,720**

### Configuration
```python
# In config.py
ATR_PERIOD = 14           # How many bars to calculate ATR
ATR_MULTIPLIER_SL = 2.0   # Stop loss width (2.0x recommended for M5)
```

---

## 2. Take Profit Calculation (Risk:Reward Based)

### Formula
```
Risk = |Entry Price - Stop Loss|
Reward = Risk × Reward Ratio

For BUY:  Take Profit = Entry Price + Reward
For SELL: Take Profit = Entry Price - Reward
```

### How It Works

**Risk**: The distance from entry to stop loss (in price)

**Reward Ratio**: How much profit vs risk
- 1.5 = Take profit is 1.5× the risk distance
- 2.0 = Take profit is 2× the risk distance
- Higher ratio = bigger profit target

### Example (XAUUSD)

**Scenario**: BUY Gold at 2,700, SL at 2,680
- Risk = |2,700 - 2,680| = 20 points
- Reward Ratio = 1.5
- Reward = 20 × 1.5 = 30 points
- **Take Profit = 2,700 + 30 = 2,730**

**Scenario**: SELL Gold at 2,700, SL at 2,720
- Risk = |2,700 - 2,720| = 20 points
- Reward Ratio = 1.5
- Reward = 20 × 1.5 = 30 points
- **Take Profit = 2,700 - 30 = 2,670**

### Multiple Take Profits (Split Orders)

The bot can split positions into multiple orders with different TPs:

**Example**: 3 positions with TP ratios [1.2, 1.8, 2.5]
- Position 1 (40%): TP at 1.2× risk = Quick profit
- Position 2 (30%): TP at 1.8× risk = Medium profit
- Position 3 (30%): TP at 2.5× risk = Large profit

### Configuration
```python
# In config.py
REWARD_RATIO = 1.5              # Single TP ratio
TP_LEVELS = [1.2, 1.8, 2.5]     # Multiple TP ratios
PARTIAL_CLOSE_PERCENT = [40, 30, 30]  # % allocation
```

---

## 3. Position Size Calculation (Risk-Based)

### Formula
```
Risk Amount = Account Balance × (Risk % / 100)
Stop Loss Pips = |Entry Price - Stop Loss| / Point Size
Lot Size = Risk Amount / (Stop Loss Pips × Pip Value)
```

### How It Works

**Step 1: Calculate Risk Amount**
- Determines how much money to risk on this trade
- Example: $50,000 balance × 0.3% = $150 risk

**Step 2: Calculate Stop Loss Distance in Pips**
- Converts price distance to pips
- Example: 20 points / 0.01 = 2,000 pips

**Step 3: Calculate Lot Size**
- Determines position size to risk exactly $150
- Accounts for pip value of the symbol

**Step 4: Margin Check**
- Ensures enough free margin available
- Reduces lot size if needed (uses max 80% of free margin)

**Step 5: Round & Limit**
- Rounds to broker's volume step (e.g., 0.01)
- Ensures within min/max lot size limits

### Example (XAUUSD)

**Account**: $50,000 balance, $48,000 free margin
**Risk**: 0.3% = $150
**Entry**: 2,700
**Stop Loss**: 2,680 (20 points)

**Calculation**:
1. Risk Amount = $50,000 × 0.003 = **$150**
2. SL Pips = 20 / 0.01 = **2,000 pips**
3. Pip Value = $1 per pip per lot (for Gold)
4. Lot Size = $150 / (2,000 × $1) = **0.075 lots**
5. Rounded = **0.08 lots** (rounded to 0.01 step)

**Margin Check**:
- Required Margin = (0.08 × 100 oz × 2,700) / 100 leverage = $216
- Available = $48,000 × 0.8 = $38,400
- ✅ Enough margin, proceed with 0.08 lots

### Example (GBPUSD)

**Account**: $50,000 balance
**Risk**: 0.3% = $150
**Entry**: 1.2500
**Stop Loss**: 1.2480 (20 pips)

**Calculation**:
1. Risk Amount = **$150**
2. SL Pips = 0.0020 / 0.0001 = **20 pips**
3. Pip Value = $10 per pip per lot (for GBPUSD)
4. Lot Size = $150 / (20 × $10) = **0.75 lots**

### Configuration
```python
# In config.py
RISK_PERCENT = 0.3          # Risk 0.3% per trade
USE_DYNAMIC_SIZING = True   # Enable risk-based sizing
MAX_LOT_SIZE = 1.0          # Maximum allowed
MIN_LOT_SIZE = 0.01         # Minimum allowed
DEFAULT_LOT_SIZE = 0.01     # Fallback if calculation fails
```

---

## 4. Complete Trade Example

### Scenario: BUY XAUUSD

**Market Conditions**:
- Current Price: 2,700
- ATR (14): 10 points
- Account Balance: $50,000
- Free Margin: $48,000

**Configuration**:
- Risk: 0.3%
- ATR Multiplier: 2.0
- Reward Ratio: 1.5
- Split Orders: 3 positions [1.2, 1.8, 2.5]
- Allocations: [40%, 30%, 30%]

### Step-by-Step Calculation

**1. Calculate Stop Loss**
```
SL = Entry - (ATR × Multiplier)
SL = 2,700 - (10 × 2.0)
SL = 2,680
```

**2. Calculate Take Profits**
```
Risk = |2,700 - 2,680| = 20 points

TP1 = 2,700 + (20 × 1.2) = 2,724  (40% of position)
TP2 = 2,700 + (20 × 1.8) = 2,736  (30% of position)
TP3 = 2,700 + (20 × 2.5) = 2,750  (30% of position)
```

**3. Calculate Position Size**
```
Risk Amount = $50,000 × 0.003 = $150
SL Pips = 20 / 0.01 = 2,000 pips
Pip Value = $1 per pip per lot
Lot Size = $150 / (2,000 × $1) = 0.075 lots
Rounded = 0.08 lots
```

**4. Split Into 3 Orders**
```
Total Lots = 0.08

Order 1: 0.08 × 40% = 0.032 → 0.03 lots, TP: 2,724
Order 2: 0.08 × 30% = 0.024 → 0.02 lots, TP: 2,736
Order 3: 0.08 × 30% = 0.024 → 0.02 lots, TP: 2,750
```

### Trade Summary

| Order | Lots | Entry | Stop Loss | Take Profit | Risk | Reward |
|-------|------|-------|-----------|-------------|------|--------|
| 1     | 0.03 | 2,700 | 2,680     | 2,724       | $60  | $72    |
| 2     | 0.02 | 2,700 | 2,680     | 2,736       | $40  | $72    |
| 3     | 0.02 | 2,700 | 2,680     | 2,750       | $40  | $100   |
| **Total** | **0.07** | - | - | - | **$140** | **$244** |

**Risk:Reward**: $140 risk for $244 potential reward = **1:1.74 average**

---

## 5. Adaptive Risk Adjustments

When **Adaptive Risk Management** is enabled, the bot modifies these calculations based on market conditions:

### Stop Loss Adjustments

| Market Type | ATR Multiplier | Effect |
|-------------|----------------|--------|
| Strong Trend | 2.5× | Wider stops (more room) |
| Weak Trend | 2.0× | Standard stops |
| Ranging | 1.5× | Tighter stops |
| Volatile | 2.5× | Wider stops |

### Take Profit Adjustments

| Market Type | TP Ratios | Effect |
|-------------|-----------|--------|
| Strong Trend | [1.5, 2.5, 4.0] | Bigger targets |
| Weak Trend | [1.5, 2.0, 3.0] | Moderate targets |
| Ranging | [1.0, 1.5, 2.0] | Smaller targets |

### Position Size Adjustments

| Market Type | Risk Multiplier | Effect |
|-------------|-----------------|--------|
| High Confidence (>80%) | 1.3× | Larger position |
| Medium Confidence (60-80%) | 1.0× | Normal position |
| Low Confidence (<60%) | 0.7× | Smaller position |

**Example**: 
- Base risk: 0.3% = $150
- High confidence trade: $150 × 1.3 = **$195 risk**
- Low confidence trade: $150 × 0.7 = **$105 risk**

---

## 6. Key Formulas Summary

### Stop Loss
```
BUY:  SL = Entry - (ATR × Multiplier)
SELL: SL = Entry + (ATR × Multiplier)
```

### Take Profit
```
Risk = |Entry - SL|
Reward = Risk × Ratio
BUY:  TP = Entry + Reward
SELL: TP = Entry - Reward
```

### Position Size
```
Risk $ = Balance × (Risk % / 100)
SL Pips = |Entry - SL| / Point
Lot Size = Risk $ / (SL Pips × Pip Value)
```

---

## 7. Configuration Parameters

### Current M1 Config (Aggressive)
```python
RISK_PERCENT = 0.3          # 0.3% per trade
ATR_MULTIPLIER_SL = 1.2     # Very tight stops
REWARD_RATIO = 1.2          # Small targets
TP_LEVELS = [1.0, 1.3, 1.8] # Quick exits
```

### Optimized M5 Config (Recommended)
```python
RISK_PERCENT = 0.2          # 0.2% per trade (safer)
ATR_MULTIPLIER_SL = 2.0     # Wider stops (better)
REWARD_RATIO = 1.5          # Balanced targets
TP_LEVELS = [1.2, 1.8, 2.5] # Realistic exits
```

---

## 8. Tips for Optimization

### If Getting Stopped Out Too Often:
- ✅ Increase `ATR_MULTIPLIER_SL` (1.2 → 2.0 or 2.5)
- ✅ Switch to higher timeframe (M1 → M5)
- ✅ Increase `MIN_TRADE_CONFIDENCE` (50% → 70%)

### If Not Reaching Take Profits:
- ✅ Reduce `REWARD_RATIO` (2.0 → 1.5)
- ✅ Use split orders with closer TPs
- ✅ Enable trailing stops

### If Losing Too Much Per Trade:
- ✅ Reduce `RISK_PERCENT` (0.3% → 0.2% or 0.1%)
- ✅ Reduce `MAX_LOT_SIZE`
- ✅ Enable adaptive risk (reduces size on low confidence)

### If Not Trading Enough:
- ✅ Reduce `MIN_TRADE_CONFIDENCE` (70% → 60%)
- ✅ Reduce `ATR_MULTIPLIER_SL` (wider stops = more trades)
- ✅ Switch to lower timeframe (M5 → M1, not recommended)

---

## 9. Real Trade Analysis

From your actual trades:

### XAUUSD Trade (SELL)
- **Entry**: 5,081.64
- **Stop Loss**: 5,096.03 (14.39 points)
- **ATR Used**: ~7.2 points (14.39 / 2.0)
- **Total Lots**: 0.73 lots
- **Risk**: ~$150 (0.3% of $50,000)
- **TPs**: 5,067.25, 5,062.93, 5,055.74

**Analysis**:
- ❌ Market went UP (wrong direction)
- ❌ Stop loss hit (trailing moved to 5,092.34)
- ❌ M1 timeframe gave false signal

### XAGUSD Trade (SELL)
- **Entry**: 106.856
- **Stop Loss**: 108.347 (1.491 points)
- **Total Lots**: 0.14 lots
- **Risk**: ~$150
- **TPs**: 105.365, 104.918, 104.172

**Analysis**:
- ❌ Market went UP (wrong direction)
- ❌ Stop loss hit (trailing moved to 107.777)
- ❌ High confidence (85%) but still wrong

---

## Summary

The bot uses **professional risk management**:
- ✅ ATR-based stops adapt to volatility
- ✅ Risk-based sizing ensures consistent risk
- ✅ Multiple TPs allow partial profit taking
- ✅ Adaptive adjustments based on market conditions

**Key to Success**: Proper configuration for your timeframe and market conditions!
