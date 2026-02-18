# Pip-Based TP/SL Configuration Guide

## Overview

The bot now supports **two methods** for calculating Take Profit (TP) and Stop Loss (SL):

1. **ATR-Based** (Default) - Dynamic calculation based on market volatility
2. **Pip-Based** (New) - Fixed pip values for consistent risk management

## Why Use Pip-Based TP/SL?

### Advantages:
- **Consistent risk** across all symbols
- **Predictable** profit/loss targets
- **Easier to backtest** and optimize
- **Better position sizing** accuracy
- **Simpler to understand** and manage

### When to Use:
- Trading multiple symbols with different volatilities
- Want consistent pip-based risk:reward ratios
- Need precise control over trade parameters
- Backtesting specific pip-based strategies

## Configuration

### Enable Pip-Based TP/SL

Add these settings to your `bot_config.json`:

```json
{
  "use_pip_based_sl": true,
  "use_pip_based_tp": true,
  "sl_pips": 50,
  "tp_pips": 100
}
```

### Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `use_pip_based_sl` | boolean | false | Enable pip-based stop loss |
| `use_pip_based_tp` | boolean | false | Enable pip-based take profit |
| `sl_pips` | number | 50 | Stop loss in pips |
| `tp_pips` | number | 100 | Take profit in pips |

### Mixed Mode

You can mix ATR-based SL with pip-based TP (or vice versa):

```json
{
  "use_pip_based_sl": false,
  "use_pip_based_tp": true,
  "atr_multiplier": 2.0,
  "tp_pips": 150
}
```

## How It Works

### Pip Calculation by Symbol Type

The bot automatically handles different broker digit formats:

| Symbol Type | Digits | Point | Pip Calculation |
|-------------|--------|-------|-----------------|
| EURUSD | 5 | 0.00001 | 50 pips = 0.00500 |
| USDJPY | 3 | 0.001 | 50 pips = 0.500 |
| GBPUSD | 5 | 0.00001 | 50 pips = 0.00500 |
| XAUUSD | 2 | 0.01 | 50 pips = 0.50 |

### Example Calculations

#### EURUSD (5-digit broker)
```
Entry: 1.18185
SL (50 pips): 1.17685
TP (100 pips): 1.19185
Risk:Reward = 1:2
```

#### USDJPY (3-digit broker)
```
Entry: 156.466
SL (50 pips): 155.966
TP (100 pips): 157.466
Risk:Reward = 1:2
```

#### XAUUSD (Gold, 2-digit)
```
Entry: 5008.14
SL (50 pips): 5007.64
TP (100 pips): 5009.14
Risk:Reward = 1:2
```

## Recommended Settings

### Conservative (Low Risk)
```json
{
  "use_pip_based_sl": true,
  "use_pip_based_tp": true,
  "sl_pips": 30,
  "tp_pips": 90,
  "risk_percent": 1.0
}
```
- 30 pip SL
- 90 pip TP (1:3 RR)
- 1% risk per trade

### Balanced (Medium Risk)
```json
{
  "use_pip_based_sl": true,
  "use_pip_based_tp": true,
  "sl_pips": 50,
  "tp_pips": 100,
  "risk_percent": 1.5
}
```
- 50 pip SL
- 100 pip TP (1:2 RR)
- 1.5% risk per trade

### Aggressive (High Risk)
```json
{
  "use_pip_based_sl": true,
  "use_pip_based_tp": true,
  "sl_pips": 80,
  "tp_pips": 160,
  "risk_percent": 2.0
}
```
- 80 pip SL
- 160 pip TP (1:2 RR)
- 2% risk per trade

### Scalping (Very Tight)
```json
{
  "use_pip_based_sl": true,
  "use_pip_based_tp": true,
  "sl_pips": 15,
  "tp_pips": 30,
  "risk_percent": 0.5,
  "timeframe": "M5"
}
```
- 15 pip SL
- 30 pip TP (1:2 RR)
- 0.5% risk per trade
- 5-minute timeframe

## Position Sizing with Pip-Based TP/SL

The bot automatically calculates correct position sizes based on pip values:

### Formula:
```
Lot Size = (Account Balance × Risk%) / (SL Pips × Pip Value)
```

### Example (EURUSD):
```
Account: $10,000
Risk: 1% = $100
SL: 50 pips
Pip Value: $10 per lot (standard lot)

Lot Size = $100 / (50 × $10) = 0.20 lots
```

## Comparison: ATR vs Pip-Based

| Feature | ATR-Based | Pip-Based |
|---------|-----------|-----------|
| **Adaptability** | ✅ Adapts to volatility | ❌ Fixed values |
| **Consistency** | ❌ Varies by market | ✅ Always same pips |
| **Simplicity** | ❌ Complex calculation | ✅ Simple to understand |
| **Backtesting** | ❌ Harder to optimize | ✅ Easy to optimize |
| **Risk Control** | ⚠️ Variable risk | ✅ Precise risk |
| **Market Conditions** | ✅ Better in volatile markets | ✅ Better in stable markets |

## Best Practices

### 1. Choose Based on Strategy
- **Trend Following**: ATR-based (adapts to volatility)
- **Range Trading**: Pip-based (consistent targets)
- **Scalping**: Pip-based (tight, predictable stops)
- **Swing Trading**: Either (depends on preference)

### 2. Test Both Methods
Run backtests with both methods to see which performs better for your symbols and timeframe.

### 3. Adjust for Symbol Volatility
Different symbols have different average pip movements:
- **EURUSD**: 50-100 pips/day → SL: 30-50 pips
- **GBPJPY**: 150-250 pips/day → SL: 80-120 pips
- **XAUUSD**: 1000-2000 pips/day → SL: 200-400 pips

### 4. Monitor Performance
Track your win rate and average R:R to optimize pip values:
- If win rate < 40%: Reduce SL or increase TP
- If win rate > 60%: Can increase SL for better entries
- Target: 45-55% win rate with 1:2 R:R

## Troubleshooting

### Issue: Stops Too Tight
**Symptom**: High stop-out rate, low win rate

**Solution**:
```json
{
  "sl_pips": 80,  // Increase from 50
  "tp_pips": 160  // Maintain 1:2 ratio
}
```

### Issue: Targets Too Far
**Symptom**: Trades reverse before hitting TP

**Solution**:
```json
{
  "sl_pips": 50,
  "tp_pips": 75,  // Reduce from 100 (1:1.5 ratio)
  "use_split_orders": true  // Take partial profits
}
```

### Issue: Inconsistent Results Across Symbols
**Symptom**: Good results on EURUSD, poor on GBPJPY

**Solution**: Use symbol-specific pip values (requires custom configuration per symbol)

## Migration from ATR-Based

### Step 1: Calculate Equivalent Pip Values
Check your current ATR-based trades to see average SL/TP in pips:

```python
# Run this to analyze your trades
python analyze_trades.py --show-pips
```

### Step 2: Set Initial Pip Values
Use the average values from your analysis:

```json
{
  "use_pip_based_sl": true,
  "use_pip_based_tp": true,
  "sl_pips": 60,  // Your average ATR-based SL
  "tp_pips": 120  // Your average ATR-based TP
}
```

### Step 3: Test and Optimize
Run forward tests for 1-2 weeks and adjust based on results.

## Advanced: Dynamic Pip Adjustment

For advanced users, you can combine both methods:

```json
{
  "use_pip_based_sl": true,
  "use_pip_based_tp": false,
  "sl_pips": 50,
  "reward_ratio": 2.0
}
```

This gives you:
- Fixed 50-pip stop loss
- Dynamic TP based on 1:2 risk:reward ratio

## Summary

Pip-based TP/SL provides:
- ✅ Consistent risk management
- ✅ Easier position sizing
- ✅ Better for backtesting
- ✅ Simpler to understand
- ✅ Precise control

Enable it by adding to your config:
```json
{
  "use_pip_based_sl": true,
  "use_pip_based_tp": true,
  "sl_pips": 50,
  "tp_pips": 100
}
```

The bot will automatically handle all pip calculations correctly for any symbol!
