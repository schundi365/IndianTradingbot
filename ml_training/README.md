# ML Training Scripts

This folder contains all scripts needed to train and manage ML models for the GEM Trading Bot.

## 📁 Folder Structure

```
ml_training/
├── README.md                           # This file
├── 1_extract_training_data.py          # Extract data from logs
├── 2_prepare_training_data.py          # Clean and prepare data
├── 3_train_ml_model.py                 # Train the ML model
├── 4_evaluate_model.py                 # Test model performance
├── 5_deploy_model.py                   # Deploy to bot
└── utils/
    ├── data_validator.py               # Validate training data
    └── feature_engineering.py          # Create features
```

## 🚀 Quick Start

### Step 1: Extract Training Data from Logs
```bash
python ml_training/1_extract_training_data.py
```
**What it does:**
- Reads `trading_bot.log`
- Extracts trade signals and outcomes
- Creates `data/training_data.csv`

**Requirements:**
- Bot must have been running
- At least 50 trades in logs

---

### Step 2: Prepare Training Data
```bash
python ml_training/2_prepare_training_data.py
```
**What it does:**
- Cleans the extracted data
- Removes invalid entries
- Normalizes features
- Splits into train/test sets
- Creates `data/training_data_prepared.csv`

---

### Step 3: Train ML Model
```bash
python ml_training/3_train_ml_model.py
```
**What it does:**
- Trains XGBoost model
- Performs cross-validation
- Saves model to `models/ml_signal_model.pkl`
- Shows accuracy metrics

**Expected Output:**
```
Training ML model...
Accuracy: 75.5%
Precision: 78.2%
Recall: 72.8%
F1 Score: 75.4%
Model saved to models/ml_signal_model.pkl
```

---

### Step 4: Evaluate Model
```bash
python ml_training/4_evaluate_model.py
```
**What it does:**
- Tests model on unseen data
- Shows confusion matrix
- Displays feature importance
- Generates performance report

---

### Step 5: Deploy Model
```bash
python ml_training/5_deploy_model.py
```
**What it does:**
- Copies model to production location
- Updates bot configuration
- Verifies model loads correctly
- Restarts bot (optional)

---

## 📊 Data Requirements

### Minimum Requirements:
- **50+ trades** for basic training
- **200+ trades** for good performance
- **500+ trades** for optimal results

### Data Quality:
- Complete indicator values (RSI, MACD, ADX, ATR)
- Clear trade outcomes (profit/loss)
- Diverse market conditions
- Multiple symbols

---

## 🔄 Retraining Schedule

### When to Retrain:
- **Weekly**: If trading actively (100+ trades/week)
- **Monthly**: For normal usage (50+ trades/month)
- **After major changes**: New strategy, different symbols
- **Performance drop**: Win rate decreases significantly

### How to Retrain:
```bash
# Extract new data
python ml_training/1_extract_training_data.py

# Train with new data
python ml_training/3_train_ml_model.py

# Evaluate performance
python ml_training/4_evaluate_model.py

# Deploy if better
python ml_training/5_deploy_model.py
```

---

## 🛠️ Troubleshooting

### Issue: Not Enough Training Data
**Solution:**
- Run bot longer to collect more trades
- Lower minimum sample requirement (not recommended)
- Use demo account for faster data collection

### Issue: Low Model Accuracy (<60%)
**Causes:**
- Insufficient training data
- Poor data quality
- Overfitting

**Solutions:**
- Collect more diverse data
- Check indicator calculations
- Adjust model hyperparameters

### Issue: Model Not Loading
**Causes:**
- Wrong file path
- Corrupted model file
- Version mismatch

**Solutions:**
- Check `models/ml_signal_model.pkl` exists
- Retrain model
- Verify XGBoost version matches

---

## 📈 Expected Performance

### Before ML Training:
- Win Rate: ~60-70%
- Based on technical indicators only

### After ML Training (Good Data):
- Win Rate: ~70-80%
- Improved signal quality
- Better risk management

### After ML Training (Excellent Data):
- Win Rate: ~75-85%
- Highly accurate predictions
- Optimal position sizing

---

## 🔍 Data Sources

### Primary Source: Bot Logs
- File: `trading_bot.log`
- Contains: All trade signals and outcomes
- Updated: Real-time during trading

### Alternative Sources:
1. **MT5 History Export**
   - Export trade history from MT5
   - Convert to CSV format
   - Use `prepare_training_data.py`

2. **Manual Data Collection**
   - Record trades manually
   - Follow CSV format
   - Ensure data quality

3. **Historical Backtesting**
   - Run bot on historical data
   - Collect signals and outcomes
   - Use for initial training

---

## 📝 CSV Format

### Required Columns:
```csv
timestamp,symbol,close,rsi,macd,macd_signal,adx,atr,ema_fast,ema_slow,volume,profitable
2026-02-10 10:30:00,EURUSD,1.0850,65.5,0.0012,0.0008,28.5,0.0015,1.0845,1.0840,1500,1
2026-02-10 11:00:00,GBPUSD,1.2650,45.2,-0.0008,-0.0005,22.1,0.0018,1.2655,1.2660,1200,0
```

### Column Descriptions:
- **timestamp**: Trade date/time
- **symbol**: Currency pair
- **close**: Current price
- **rsi**: RSI indicator value
- **macd**: MACD line value
- **macd_signal**: MACD signal line
- **adx**: ADX strength value
- **atr**: ATR volatility value
- **ema_fast**: Fast EMA value
- **ema_slow**: Slow EMA value
- **volume**: Trade volume
- **profitable**: 1 = profit, 0 = loss

---

## 🎯 Best Practices

### Data Collection:
1. **Run bot on demo account first**
2. **Collect data from multiple symbols**
3. **Include various market conditions**
4. **Ensure indicator accuracy**

### Model Training:
1. **Use cross-validation**
2. **Monitor for overfitting**
3. **Test on unseen data**
4. **Compare with baseline**

### Model Deployment:
1. **Backup old model**
2. **Test new model first**
3. **Monitor performance**
4. **Rollback if needed**

---

## 📚 Additional Resources

### Documentation:
- `ML_TRAINING_DATA_GUIDE.md` - Detailed training guide
- `ML_INTEGRATION_COMPLETE_SESSION24.md` - ML integration details
- `ML_QUICK_START.md` - Quick start guide

### Scripts:
- `validate_training_data.py` - Validate data quality
- `verify_ml_integration_complete.py` - Verify ML is working

### Dashboard:
- Configuration → ML Features
- Train ML Model button
- View model statistics

---

## ⚙️ Configuration

### bot_config.json Settings:
```json
{
  "ml_enabled": true,
  "ml_model_path": "models/ml_signal_model.pkl",
  "ml_training_data_path": "data/training_data.csv",
  "ml_min_confidence": 0.6,
  "ml_auto_retrain": false,
  "ml_retrain_frequency_days": 30,
  "ml_min_training_samples": 100
}
```

---

## 🎓 Learning Resources

### XGBoost:
- Official Docs: https://xgboost.readthedocs.io/
- Tutorials: https://xgboost.readthedocs.io/en/stable/tutorials/

### Machine Learning for Trading:
- Feature engineering for financial data
- Time series prediction
- Classification vs regression
- Overfitting prevention

---

## 📞 Support

### Common Questions:

**Q: How much data do I need?**
A: Minimum 50 trades, recommended 200+, optimal 500+

**Q: How long does training take?**
A: 1-5 minutes depending on data size

**Q: Can I use data from multiple bots?**
A: Yes, combine CSV files before training

**Q: What if model accuracy is low?**
A: Collect more data, check data quality, adjust parameters

---

## ✅ Checklist

Before Training:
- [ ] Bot has been running
- [ ] At least 50 trades collected
- [ ] Log file exists and readable
- [ ] Data directory created

During Training:
- [ ] Data extracted successfully
- [ ] Data prepared and validated
- [ ] Model trained without errors
- [ ] Accuracy above 60%

After Training:
- [ ] Model file created
- [ ] Model loads in bot
- [ ] ML logs appear
- [ ] Performance monitored

---

**Ready to train your ML model!** 🚀

Start with Step 1: `python ml_training/1_extract_training_data.py`
