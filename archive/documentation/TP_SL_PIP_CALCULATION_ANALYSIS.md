# TP/SL Pip Calculation Analysis

## Investigation Summary

After thorough investigation, the TP/SL calculations in the bot are **CORRECT** and properly account for symbol pip units.

## Key Findings

### 1. ATR is Symbol-Specific
ATR (Average True Range) is calculated from each symbol's actual price data:
```python
df['high_low'] = df['high'] - df['low']
df['high_close'] = np.abs(df['high'] - df['close'].shift())
df['low_close'] = np.abs(df['low'] - df['close'].shift())
df['tr'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
df['atr'] = df['tr'].rolling(window=14).mean()
```

This means ATR is automatically in the correct price units for each symbol.

### 2. Actual ATR Values Verified

| Symbol | Point Size | ATR Value | ATR in Pips |
|--------|-----------|-----------|-------------|
| EURUSD | 0.00001 | 0.00107 | 107 pips |
| USDJPY | 0.001 | 0.103 | 103 pips |
| GBPUSD | 0.00001 | 0.00172 | 172 pips |
| XAUUSD | 0.01 | 25.28 | 2528 pips |
| EURJPY | 0.001 | 0.145 | 145 pips |

### 3. Stop Loss Calculation
```python
def calculate_stop_loss(self, entry_price, direction, atr):
    if direction == 1:  # Buy
        sl = entry_price - (self.atr_multiplier * atr)
    else:  # Sell
        sl = entry_price + (self.atr_multiplier * atr)
    return sl
```

**This is correct** because:
- ATR is already in symbol's price units
- Direct arithmetic works: 1.18135 - (2.0 × 0.00107) = 1.17921
- Result is automatically in correct units

### 4. Take Profit Calculation
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

**This is correct** because:
- Risk is calculated in price units
- Reward maintains the risk:reward ratio
- Works for all symbols automatically

### 5. Position Sizing Uses Pip Values Correctly
```python
pip_value = symbol_info.trade_tick_value
stop_loss_pips = abs(entry_price - stop_loss) / symbol_info.point
lot_size = risk_amount / (stop_loss_pips * pip_value)
```

This ensures consistent dollar risk across different symbols.

### 6. Dynamic TP/SL Managers
Both `dynamic_tp_manager.py` and `dynamic_sl_manager.py` use ATR-based calculations correctly:
- All adjustments use ATR multipliers
- ATR is already in correct units
- No conversion needed

## Example Calculations

### EURUSD (Buy)
- Entry: 1.18135
- ATR: 0.00107
- SL = 1.18135 - (2.0 × 0.00107) = 1.17921 ✓
- Risk = 0.00214 (214 pips)
- TP = 1.18135 + (0.00214 × 2.0) = 1.18563 ✓
- Reward = 428 pips (1:2 RR) ✓

### USDJPY (Buy)
- Entry: 156.503
- ATR: 0.103
- SL = 156.503 - (2.0 × 0.103) = 156.297 ✓
- Risk = 0.206 (206 pips)
- TP = 156.503 + (0.206 × 2.0) = 156.915 ✓
- Reward = 412 pips (1:2 RR) ✓

### XAUUSD (Buy)
- Entry: 5043.33
- ATR: 25.28
- SL = 5043.33 - (2.0 × 25.28) = 4992.77 ✓
- Risk = 50.56 (5056 pips)
- TP = 5043.33 + (50.56 × 2.0) = 5144.45 ✓
- Reward = 10112 pips (1:2 RR) ✓

## Why This Works

1. **ATR is calculated from actual prices** - Each symbol's ATR reflects its own volatility in its native price units

2. **Price arithmetic is universal** - Subtracting 0.00214 from 1.18135 works the same as subtracting 0.206 from 156.503

3. **Point size only needed for**:
   - Rounding to correct decimal places
   - Converting to pip counts for display
   - Position sizing calculations

4. **Risk:Reward ratio is maintained** - The ratio is based on price distances, which automatically accounts for pip sizes

## Conclusion

✅ **No changes needed** - The TP/SL calculations are correct and already account for symbol pip units properly.

If you're seeing incorrect TP/SL values in actual trades, the issue is likely:
- Configuration values (atr_multiplier, reward_ratio)
- Rounding issues
- MT5 broker restrictions
- Not the calculation logic itself

## Verification Scripts Created

1. `verify_tp_sl_calculation.py` - Shows symbol information and example calculations
2. `check_actual_atr_values.py` - Displays real ATR values and TP/SL for current market

Run these scripts to verify calculations with live data.
