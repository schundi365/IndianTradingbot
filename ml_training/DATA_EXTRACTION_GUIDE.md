# ML Training Data Extraction Guide

**Two Methods to Get Training Data**

---

## 📊 Method Comparison

| Feature | Method 1: Bot Logs | Method 2: MT5 History |
|---------|-------------------|----------------------|
| **Data Source** | Real bot trades | MT5 historical data |
| **Data Quality** | Actual outcomes | Simulated outcomes |
| **Speed** | Depends on trading | Fast (minutes) |
| **Minimum Requirement** | 50 real trades | MT5 connection |
| **Best For** | Production training | Bootstrap/Initial training |
| **Script** | `1_extract_training_data.py` | `0_extract_from_mt5.py` |

---

## 🎯 Method 1: Extract from Bot Logs (Recommended)

### When to Use:
- ✅ Bot has been running and making trades
- ✅ You want to train on actual trading results
- ✅ You have at least 50 real trades
- ✅ You want the most accurate training data

### How It Works:
1. Reads `trading_bot.log`
2. Extracts trade signals with indicators
3. Extracts actual trade outcomes (profit/loss)
4. Creates `data/training_data.csv`

### Usage:
```bash
python ml_training/1_extract_training_data.py
```

### Output:
```
Extracting training data from trading_bot.log
Extracted 150 trades from logs
Profitable trades: 105 (70.0%)
Losing trades: 45 (30.0%)
Training data saved to data/training_data.csv
```

### Advantages:
- ✅ Real trading data
- ✅ Actual outcomes (not simulated)
- ✅ Includes all bot logic
- ✅ Reflects real market conditions
- ✅ Best for production models

### Disadvantages:
- ❌ Requires bot to have been running
- ❌ Takes time to collect enough trades
- ❌ Limited to symbols bot traded

---

## 🔄 Method 2: Extract from MT5 History (Alternative)

### When to Use:
- ✅ Bot hasn't collected enough trades yet
- ✅ You want to bootstrap training quickly
- ✅ You need more diverse data
- ✅ You want to test ML before live trading

### How It Works:
1. Connects to MT5
2. Downloads historical price data
3. Calculates technical indicators
4. Simulates trades based on indicators
5. Labels outcomes by looking ahead
6. Creates `data/training_data.csv`

### Usage:
```bash
python ml_training/0_extract_from_mt5.py
```

### Interactive Prompts:
```
Enter symbols (comma-separated) or press Enter for defaults:
> XAUUSD, EURUSD, GBPUSD, USDJPY
XAUUSD,XAGUSD,EURUSD,GBPUSD,USDJPY,USDCHF,AUDUSD,USDCAD,NZDUSD,EURJPY,GBPJPY,EURGBP,EURAUD,EURCAD,GBPAUD,GBPCAD

Processing symbols: XAUUSD, EURUSD, GBPUSD, USDJPY
This may take a few minutes...
```

### Output:
```
Processing XAUUSD...
Generated 245 samples from XAUUSD
Processing EURUSD...
Generated 198 samples from EURUSD
Processing GBPUSD...
Generated 212 samples from GBPUSD
Processing USDJPY...
Generated 189 samples from USDJPY

Total samples generated: 844
Profitable: 456 (54.0%)
Losing: 388 (46.0%)
Training data saved to data/training_data.csv
```

### Advantages:
- ✅ Fast data collection (minutes)
- ✅ Large dataset quickly
- ✅ Multiple symbols easily
- ✅ Good for initial training
- ✅ No waiting for real trades

### Disadvantages:
- ❌ Simulated outcomes (not real)
- ❌ May not reflect actual bot behavior
- ❌ Look-ahead bias possible
- ❌ Less accurate than real data

---

## 🔀 Combined Approach (Best Practice)

### Strategy:
1. **Bootstrap with MT5 History** (Method 2)
   - Get initial training data quickly
   - Train first model
   - Start bot with basic ML

2. **Retrain with Real Data** (Method 1)
   - After bot collects 50+ real trades
   - Extract from logs
   - Train improved model
   - Deploy better model

3. **Continuous Improvement**
   - Retrain weekly/monthly with new real trades
   - Model improves over time
   - Adapts to changing markets

### Workflow:
```bash
# Week 1: Bootstrap
python ml_training/0_extract_from_mt5.py
python ml_training/2_prepare_training_data.py
python ml_training/3_train_ml_model.py
python ml_training/5_deploy_model.py

# Start bot, collect real trades...

# Week 2-4: First retrain with real data
python ml_training/1_extract_training_data.py
python ml_training/2_prepare_training_data.py
python ml_training/3_train_ml_model.py
python ml_training/5_deploy_model.py

# Monthly: Continuous retraining
python ml_training/1_extract_training_data.py
python ml_training/3_train_ml_model.py
python ml_training/5_deploy_model.py
```

---

## 📋 Detailed Script Information

### Script 0: Extract from MT5
**File:** `ml_training/0_extract_from_mt5.py`

**What it extracts:**
- Historical OHLCV data
- Calculated indicators (RSI, MACD, ADX, ATR, EMA)
- Bollinger Bands
- Simulated trade signals
- Simulated outcomes (look-ahead)

**Parameters:**
- Symbols: Default ['XAUUSD', 'EURUSD', 'GBPUSD', 'USDJPY']
- Timeframe: M30 (30 minutes)
- Bars: 1000 historical bars per symbol
- Output: `data/training_data.csv`

**Signal Logic:**
- BUY: RSI < 35 AND MACD > Signal
- SELL: RSI > 65 AND MACD < Signal
- Profitable: Price moves 0.2% in favor within 10 bars

**Requirements:**
- MT5 installed and running
- Symbols available in MT5
- Sufficient historical data

---

### Script 1: Extract from Logs
**File:** `ml_training/1_extract_training_data.py`

**What it extracts:**
- Trade signals from logs
- Indicator values at signal time
- Actual trade outcomes
- Profit/loss amounts

**Data Sources:**
- File: `trading_bot.log`
- Patterns: Signal logs, indicator logs, profit logs
- Timeframe: All historical logs

**Extracted Fields:**
- timestamp, symbol, close price
- rsi, macd, macd_signal
- adx, atr
- ema_fast, ema_slow
- volume
- profitable (1 or 0)

**Requirements:**
- Bot has been running
- Log file exists
- At least 50 trades logged

---

## 🔍 Data Quality Comparison

### Method 1 (Bot Logs):
```csv
timestamp,symbol,close,rsi,macd,adx,atr,profitable
2026-02-10 10:30:00,EURUSD,1.0850,65.5,0.0012,28.5,0.0015,1
2026-02-10 11:00:00,GBPUSD,1.2650,45.2,-0.0008,22.1,0.0018,0
```
- ✅ Real trade outcomes
- ✅ Actual bot decisions
- ✅ Real market conditions
- ✅ Includes slippage, spreads

### Method 2 (MT5 History):
```csv
timestamp,symbol,close,rsi,macd,adx,atr,profitable
2026-02-10 10:30:00,EURUSD,1.0850,65.5,0.0012,28.5,0.0015,1
2026-02-10 11:00:00,GBPUSD,1.2650,45.2,-0.0008,22.1,0.0018,0
```
- ⚠️ Simulated outcomes
- ⚠️ Idealized conditions
- ⚠️ No slippage/spreads
- ⚠️ Look-ahead bias

---

## 🎯 Recommendations

### For New Users:
1. Start with Method 2 (MT5 History)
2. Get initial model trained quickly
3. Start bot with basic ML
4. Switch to Method 1 after 50+ trades

### For Experienced Users:
1. Use Method 1 (Bot Logs) exclusively
2. Collect real trading data
3. Train on actual outcomes
4. Retrain regularly

### For Best Results:
1. Bootstrap with Method 2
2. Transition to Method 1
3. Combine both datasets initially
4. Eventually use only Method 1

---

## 📊 Expected Results

### Method 1 (Real Data):
- Model Accuracy: 70-80%
- Production Performance: Matches training
- Reliability: High
- Generalization: Good

### Method 2 (Simulated Data):
- Model Accuracy: 60-75%
- Production Performance: May differ
- Reliability: Medium
- Generalization: Fair

### Combined Approach:
- Model Accuracy: 65-75% initially
- Improves to 70-80% with real data
- Production Performance: Good
- Reliability: High after retraining

---

## 🛠️ Troubleshooting

### Method 1 Issues:

**Issue:** No trades found in logs
```
Solution:
1. Run bot first: python web_dashboard.py
2. Wait for trades to be made
3. Check trading_bot.log exists
```

**Issue:** Insufficient data (< 50 trades)
```
Solution:
1. Run bot longer
2. Use demo account for faster collection
3. Or use Method 2 to bootstrap
```

---

### Method 2 Issues:

**Issue:** MT5 connection failed
```
Solution:
1. Start MT5 application
2. Login to account
3. Check MT5 is not busy
```

**Issue:** Symbol not available
```
Solution:
1. Check symbol name spelling
2. Verify symbol in Market Watch
3. Use available symbols only
```

**Issue:** Insufficient historical data
```
Solution:
1. Download more history in MT5
2. Use different timeframe
3. Reduce bars parameter
```

---

## 📝 Summary

### Quick Decision Guide:

**Use Method 1 (Bot Logs) if:**
- ✅ Bot has 50+ trades
- ✅ You want best accuracy
- ✅ You can wait for data collection

**Use Method 2 (MT5 History) if:**
- ✅ Bot is new (< 50 trades)
- ✅ You want to start quickly
- ✅ You need bootstrap data

**Use Both if:**
- ✅ You want best of both worlds
- ✅ You're starting fresh
- ✅ You plan to retrain regularly

---

## 🚀 Next Steps

After extracting data with either method:

```bash
# Step 2: Prepare data
python ml_training/2_prepare_training_data.py

# Step 3: Train model
python ml_training/3_train_ml_model.py

# Step 4: Evaluate
python ml_training/4_evaluate_model.py

# Step 5: Deploy
python ml_training/5_deploy_model.py
```

---

**Both methods work! Choose based on your situation.** 🎯

For most users: Start with Method 2, transition to Method 1.
