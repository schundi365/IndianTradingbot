# ML Training Data Sources - Complete Guide

## Overview

This guide explains what data you can use to train the ML model and how to collect it.

---

## 📊 Best Data Sources (Ranked)

### 1. ⭐⭐⭐⭐⭐ Your Bot's Trade History (BEST)

**Why it's best:** Matches your exact trading conditions, strategy, and market behavior.

**What it includes:**
- Entry/exit prices
- Indicators at trade time (RSI, MACD, ADX, ATR, EMAs)
- Trade outcome (profit/loss)
- Symbol and timeframe
- Actual market conditions you trade in

**How to collect:**
```bash
# Run bot for 1-2 weeks to collect trades
python run_bot.py

# Extract training data from logs
python extract_training_data_from_logs.py
```

**Output:** `data/training_data.csv` with 100+ real trades

---

### 2. ⭐⭐⭐⭐ Demo Account Trading (SAFE & EFFECTIVE)

**Why it's good:** Real market conditions with zero financial risk.

**How to do it:**
1. Switch MT5 to demo account
2. Run bot for 1-2 weeks
3. Let it make 100+ trades
4. Extract data using script above

**Advantages:**
- Real market data
- No financial risk
- Matches your strategy
- Quick to collect (1-2 weeks)

---

### 3. ⭐⭐⭐ Historical MT5 Data (GOOD FOR INITIAL TRAINING)

**Why it's useful:** Large dataset available immediately.

**How to use:**
```bash
# Prepare historical data
python prepare_historical_data.py

# Follow prompts to select symbols
# Script will simulate trades on historical data
```

**What it does:**
- Fetches historical OHLCV data from MT5
- Calculates all indicators
- Simulates trades based on strategy
- Labels outcomes (profitable/loss)

**Output:** `data/training_data.csv` with 200+ simulated trades

---

### 4. ⭐⭐ External Data Sources (SUPPLEMENTARY)

**Free sources:**
- Yahoo Finance (stocks, forex)
- Alpha Vantage API
- Investing.com

**Paid sources:**
- Quandl
- IEX Cloud
- TradingView

**Note:** Must match your symbols and timeframes. Requires additional processing.

---

## 📋 Required Data Format

### CSV Structure

```csv
timestamp,symbol,close,rsi,macd,macd_signal,adx,atr,ema_fast,ema_slow,volume,profitable
2024-01-15 10:00,EURUSD,1.0850,65.2,0.0015,0.0012,25.3,0.0015,1.0865,1.0855,1200,1
2024-01-15 11:00,EURUSD,1.0855,67.1,0.0018,0.0014,26.1,0.0016,1.0868,1.0857,1350,1
2024-01-15 12:00,EURUSD,1.0845,62.3,0.0012,0.0015,24.8,0.0014,1.0862,1.0856,1100,0
```

### Column Descriptions

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| timestamp | datetime | When trade occurred | 2024-01-15 10:00 |
| symbol | string | Trading pair | EURUSD, XAUUSD |
| close | float | Close price at entry | 1.0850 |
| rsi | float | RSI indicator (0-100) | 65.2 |
| macd | float | MACD value | 0.0015 |
| macd_signal | float | MACD signal line | 0.0012 |
| adx | float | ADX trend strength (0-100) | 25.3 |
| atr | float | ATR volatility | 0.0015 |
| ema_fast | float | Fast EMA value | 1.0865 |
| ema_slow | float | Slow EMA value | 1.0855 |
| volume | int | Trading volume | 1200 |
| profitable | int | 1 if profit, 0 if loss | 1 |

### Optional Columns (Improve Accuracy)

- `bb_upper` - Bollinger Band upper
- `bb_lower` - Bollinger Band lower
- `volume_ma` - Volume moving average
- `profit_pips` - Actual profit in pips
- `hold_time` - Trade duration in minutes

---

## 🎯 Data Quality Requirements

### Minimum Requirements

| Requirement | Minimum | Recommended | Ideal |
|-------------|---------|-------------|-------|
| Total samples | 50 | 100 | 200+ |
| Win rate | 20-80% | 40-60% | 45-55% |
| Symbols | 1 | 2-3 | 4+ |
| Data age | < 6 months | < 3 months | < 1 month |
| Timeframe match | Same | Same | Same |

### Good Data Characteristics

✅ Mix of profitable and losing trades (balanced)
✅ Multiple symbols (if you trade multiple)
✅ Different market conditions (trending, ranging)
✅ Recent data (last 3-6 months)
✅ Matches your actual trading timeframe
✅ Complete indicator values (no missing data)

### Bad Data Characteristics

❌ All wins or all losses (unbalanced)
❌ Only one symbol (if you trade multiple)
❌ Very old data (>1 year)
❌ Different timeframe than you trade
❌ Simulated data that doesn't match reality
❌ Missing or incomplete indicator values

---

## 🚀 Quick Start Guide

### Option A: Use Existing Trades (If Bot Has Been Running)

```bash
# Step 1: Extract data from logs
python extract_training_data_from_logs.py

# Step 2: Validate data quality
python validate_training_data.py

# Step 3: Train model via dashboard
# Open dashboard → ML Features → Train ML Model
```

### Option B: Collect New Data (Demo Account)

```bash
# Step 1: Switch MT5 to demo account

# Step 2: Run bot for 1-2 weeks
python run_bot.py

# Step 3: Extract data
python extract_training_data_from_logs.py

# Step 4: Train model via dashboard
```

### Option C: Use Historical Data (Immediate Start)

```bash
# Step 1: Prepare historical data
python prepare_historical_data.py

# Step 2: Validate data
python validate_training_data.py

# Step 3: Train model via dashboard
```

---

## 📁 Data Storage Locations

### Default Paths

```
data/training_data.csv          # Training dataset
models/ml_signal_model.pkl      # Trained model
trading_bot.log                 # Bot logs
data/news_data.json            # News data (optional)
```

### Configurable in Dashboard

Go to: **Dashboard → Configuration → ML Features → Data Paths**

- Training Data Path
- ML Model Path
- News Data Path

---

## 🔧 Scripts Provided

### 1. extract_training_data_from_logs.py

**Purpose:** Extract training data from bot logs

**Usage:**
```bash
python extract_training_data_from_logs.py
```

**Output:** `data/training_data.csv`

**What it does:**
- Parses `trading_bot.log`
- Extracts trade signals and indicators
- Labels trades as profitable/loss
- Saves to CSV format

---

### 2. prepare_historical_data.py

**Purpose:** Create training data from MT5 historical data

**Usage:**
```bash
python prepare_historical_data.py
```

**Interactive prompts:**
- Enter symbols (or use defaults)
- Fetches historical data
- Simulates trades
- Saves to CSV

**Output:** `data/training_data.csv`

---

### 3. validate_training_data.py

**Purpose:** Check data quality before training

**Usage:**
```bash
python validate_training_data.py
```

**Checks:**
- CSV format correctness
- Required columns present
- Data types valid
- Sufficient samples
- Class balance
- Value ranges

**Output:** Validation report with issues/warnings

---

## 🎓 Training the Model

### Via Dashboard (Recommended)

1. Open dashboard: `http://gemtrading:5000`
2. Go to **Configuration** tab
3. Scroll to **ML Features** section
4. Set paths:
   - Training Data Path: `data/training_data.csv`
   - ML Model Path: `models/ml_signal_model.pkl`
5. Click **Train ML Model**
6. Wait for training to complete
7. Check accuracy (>60% is good, >70% is great)
8. Enable ML predictions

### Via API

```python
import requests

response = requests.post('http://gemtrading:5000/api/ml/train', json={
    'training_data_path': 'data/training_data.csv',
    'model_path': 'models/ml_signal_model.pkl'
})

print(response.json())
```

---

## 📊 Understanding Training Results

### Accuracy Metrics

| Metric | Description | Good Value |
|--------|-------------|------------|
| Accuracy | Overall correctness | >60% |
| Precision | Correct positive predictions | >65% |
| Recall | Found all positives | >55% |

### What the Numbers Mean

- **60-70% accuracy:** Good, model is learning patterns
- **70-80% accuracy:** Very good, reliable predictions
- **80%+ accuracy:** Excellent, but watch for overfitting
- **<60% accuracy:** Need more/better data

---

## 🔄 Retraining Schedule

### When to Retrain

- **Monthly:** Recommended for active trading
- **After 100+ new trades:** When you have new data
- **Market changes:** After major market events
- **Poor performance:** If predictions become inaccurate

### Auto-Retrain (Optional)

Enable in dashboard:
- **ML Auto Retrain:** ON
- **Retrain Frequency:** 30 days
- **Min Training Samples:** 100

---

## ❓ Troubleshooting

### Problem: Not enough data

**Solution:** 
- Run bot on demo for 1-2 weeks
- Use historical data script
- Combine multiple data sources

### Problem: All trades are wins/losses

**Solution:**
- Adjust bot settings for more balanced results
- Use demo account to collect diverse trades
- Check if strategy is too aggressive/conservative

### Problem: Data format errors

**Solution:**
- Use provided extraction scripts
- Run validation script
- Check CSV has all required columns

### Problem: Model accuracy low (<60%)

**Solution:**
- Collect more data (200+ samples)
- Ensure data quality (balanced, recent)
- Check indicators are calculated correctly
- Try different symbols/timeframes

### Problem: Can't find trade history

**Solution:**
- Check `trading_bot.log` exists
- Verify bot has been running
- Check MT5 history tab
- Ensure trades were actually executed

---

## 📚 Additional Resources

- **ML Features Guide:** `docs/ML_FEATURES_GUIDE.md`
- **Quick Start:** `ML_QUICK_START.md`
- **Implementation Details:** `ML_IMPLEMENTATION_COMPLETE.md`
- **Dashboard Guide:** `ML_DASHBOARD_INTEGRATION_COMPLETE.md`

---

## 🎯 Next Steps

1. **Choose your data source** (bot logs recommended)
2. **Collect/export 100+ trades**
3. **Validate data quality**
4. **Train model via dashboard**
5. **Test predictions**
6. **Enable ML features**
7. **Monitor performance**
8. **Retrain monthly**

---

**Need Help?**

Check the troubleshooting section above or review the detailed guides in the `docs/` folder.

**Ready to Start?**

Run: `python extract_training_data_from_logs.py` or `python prepare_historical_data.py`
