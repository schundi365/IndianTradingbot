# TP/SL Calculation Verification

## Summary
The TP/SL calculations in the bot are **CORRECT** and already account for symbol pip units properly.

## How It Works

### ATR Calculation
ATR (Average True Range) is calculated from the actual price data (high, low, close) for each symbol:
```python
df['high_low'] = df['high'] - df['low']
df['high_close'] = np.abs(df['high'] - df['close'].shift())
df['low_close'] = np.abs(df['low'] - df['close'].shift())
df['tr'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
df['atr'] = df['tr'].rolling(window=14).mean()
```

**Key Point**: ATR is automatically in the symbol's native price units because it's calculated from that symbol's price data.

### Actual ATR Values by Symbol

| Symbol | Point Size | Current ATR | ATR in Pips |
|--------|-----------|-------------|-------------|
| EURUSD | 0.00001 | 0.00107 | 107 pips |
| USDJPY | 0.001 | 0.103 | 103 pips |
| GBPUSD | 0.00001 | 0.00172 | 172 pips |
| XAUUSD | 0.01 | 25.28 | 2528 pips |
| EURJPY | 0.001 | 0.145 | 145 pips |

### Stop Loss Calculation
```python
def calculate_stop_loss(self, entry_price, direction, atr):
    if direction == 1:  # Buy
        sl = entry_price - (self.atr_multiplier * atr)
    else:  # Sell
        sl = entry_price + (self.atr_multiplier * atr)
    return sl
```

**Example for EURUSD (Buy)**:
- Entry: 1.18135
- ATR: 0.00107
- ATR Multiplier: 2.0
- SL = 1.18135 - (2.0 × 0.00107) = 1.17921
- Distance: 214 pips ✓

**Example for USDJPY (Buy)**:
- Entry: 156.503
- ATR: 0.103
- ATR Multiplier: 2.0
- SL = 156.503 - (2.0 × 0.103) = 156.297
- Distance: 206 pips ✓

### Take Profit Calculation
```python
def calculate_take_profit(self, entry_price, stop_loss, direction):
    risk = abs(entry_price - stop_loss)
    reward = risk * self.reward_ratio
    
    if direction == 1:  # Buy
        tp = entry_price + reward
    else:  # Sell
        tp = entry_price - reward
    return tp
```

**Example for EURUSD (Buy, 1:2 RR)**:
- Entry: 1.18135
- SL: 1.17921
- Risk: 0.00214 (214 pips)
- Reward: 0.00214 × 2.0 = 0.00428 (428 pips)
- TP = 1.18135 + 0.00428 = 1.18563 ✓

**Example for USDJPY (Buy, 1:2 RR)**:
- Entry: 156.503
- SL: 156.297
- Risk: 0.206 (206 pips)
- Reward: 0.206 × 2.0 = 0.412 (412 pips)
- TP = 156.503 + 0.412 = 156.915 ✓

## Why This Works

1. **ATR is symbol-specific**: Each symbol's ATR is calculated from its own price data, so it's automatically in the correct units.

2. **Price arithmetic is universal**: When you subtract 0.00214 from 1.18135 (EURUSD) or 0.206 from 156.503 (USDJPY), you're working in each symbol's native price units.

3. **No conversion needed**: The point size is only needed for:
   - Rounding to the correct number of decimal places (digits)
   - Calculating pip values for position sizing
   - Displaying pip distances in logs

## Position Sizing
The position sizing DOES use pip values correctly:
```python
pip_value = symbol_info.trade_tick_value
stop_loss_pips = abs(entry_price - stop_loss) / symbol_info.point
lot_size = risk_amount / (stop_loss_pips * pip_value)
```

This ensures that a 200-pip stop loss on EURUSD and a 200-pip stop loss on USDJPY both risk the same dollar amount, even though they have different point sizes.

## Conclusion
✅ **The TP/SL calculations are CORRECT and already account for symbol pip units properly.**

The calculations work because:
- ATR is calculated from each symbol's actual price data
- All arithmetic is done in the symbol's native price units
- The risk:reward ratio is maintained correctly across all symbols
- Position sizing properly accounts for pip values to ensure consistent risk

No changes are needed to the calculation logic.
