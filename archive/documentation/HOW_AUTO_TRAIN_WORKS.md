# How Auto-Train ML Model Works from Dashboard

## Overview
The dashboard provides ML model training configuration and manual training capabilities. However, **auto-retrain is currently configured but NOT fully implemented** in the bot's main loop.

---

## Dashboard Configuration

### Location in Dashboard
The ML training options are in the "Machine Learning Configuration" section:

### Configuration Fields

1. **ML Model Path** (`ml_model_path`)
   - Default: `models/ml_signal_model.pkl`
   - Where the trained model is saved/loaded

2. **Training Data Path** (`ml_training_data_path`)
   - Default: `data/training_data.csv`
   - Where historical trade data is stored for training

3. **Auto-Retrain Model** (`ml_auto_retrain`)
   - Checkbox to enable automatic retraining
   - Default: `false` (disabled)
   - **Status: Configured but not implemented in bot loop**

4. **Retrain Frequency** (`ml_retrain_frequency`)
   - Options: Daily, Weekly (default), Monthly
   - **Status: Configured but not used**

5. **Min Training Samples** (`ml_min_training_samples`)
   - Default: 100
   - Minimum number of samples needed before training
   - Range: 50-1000

---

## How Manual Training Works

### From Dashboard UI

1. **User clicks "Train ML Model" button**
   ```javascript
   // templates/dashboard.html line 5258
   async function trainMLModel() {
       const trainingDataPath = document.getElementById('ml_training_data_path')?.value;
       const modelPath = document.getElementById('ml_model_path')?.value;
       
       const response = await fetch('/api/ml/train', {
           method: 'POST',
           headers: {'Content-Type': 'application/json'},
           body: JSON.stringify({
               training_data_path: trainingDataPath,
               model_path: modelPath
           })
       });
   }
   ```

2. **Backend API receives request**
   ```python
   # web_dashboard.py line 1541
   @app.route('/api/ml/train', methods=['POST'])
   def train_ml_model():
       training_data_path = data.get('training_data_path', 'data/training_data.csv')
       model_path = data.get('model_path', 'models/ml_signal_model.pkl')
   ```

3. **Training Process**
   ```python
   # Load training data
   df = pd.read_csv(training_data_path)
   
   # Validate minimum samples (50 required)
   if len(df) < 50:
       return error
   
   # Extract features
   feature_columns = ['rsi', 'macd', 'macd_signal', 'adx', 'atr', 
                      'ema_fast', 'ema_slow', 'volume']
   X = df[feature_columns]
   y = df['profitable'].values  # Target: was trade profitable?
   
   # Train model
   ml_generator = MLSignalGenerator(logger=logger)
   ml_generator.model_path = model_path
   success = ml_generator.train_model(X, y)
   
   # Evaluate on test set (80/20 split)
   X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
   y_pred = ml_generator.model.predict(X_test)
   
   # Calculate metrics
   accuracy = accuracy_score(y_test, y_pred)
   precision = precision_score(y_test, y_pred)
   recall = recall_score(y_test, y_pred)
   ```

4. **Model is saved**
   ```python
   # src/ml_signal_generator.py line 327
   def _save_model(self):
       with open(self.model_path, 'wb') as f:
           pickle.dump({
               'model': self.model,
               'scaler': self.scaler,
               'feature_names': self.feature_names,
               'version': '1.0'
           }, f)
   ```

5. **Dashboard shows results**
   - Training samples count
   - Accuracy percentage
   - Precision percentage
   - Recall percentage
   - Model path

---

## Auto-Retrain Feature Status

### ⚠️ IMPORTANT: Auto-Retrain is NOT Implemented

The dashboard has configuration fields for auto-retrain, but the bot does NOT automatically retrain the model.

### What's Configured
```python
# src/config_manager.py line 135
'ml_auto_retrain': False,
'ml_retrain_frequency_days': 30,
'ml_min_training_samples': 100,
```

### What's Missing
The bot's main loop (`src/mt5_trading_bot.py`) does NOT:
- Check if auto-retrain is enabled
- Track time since last training
- Automatically trigger retraining
- Monitor training data accumulation

### How to Implement Auto-Retrain

To implement auto-retrain, you would need to add this logic to the bot:

```python
# Pseudo-code for auto-retrain implementation
class MT5TradingBot:
    def __init__(self):
        self.last_retrain_time = None
        self.training_data_buffer = []
    
    def run(self):
        while self.running:
            # ... existing trading logic ...
            
            # Check if auto-retrain is enabled
            if self.config.get('ml_auto_retrain', False):
                self._check_and_retrain()
    
    def _check_and_retrain(self):
        """Check if retraining is needed and trigger it"""
        frequency_days = self.config.get('ml_retrain_frequency_days', 30)
        min_samples = self.config.get('ml_min_training_samples', 100)
        
        # Check if enough time has passed
        if self.last_retrain_time:
            days_since_retrain = (datetime.now() - self.last_retrain_time).days
            if days_since_retrain < frequency_days:
                return
        
        # Check if we have enough new samples
        training_data_path = self.config.get('ml_training_data_path')
        df = pd.read_csv(training_data_path)
        
        if len(df) < min_samples:
            self.logger.info(f"Not enough samples for retraining: {len(df)}/{min_samples}")
            return
        
        # Trigger retraining
        self.logger.info("Auto-retraining ML model...")
        self._retrain_model(df)
        self.last_retrain_time = datetime.now()
    
    def _retrain_model(self, df):
        """Retrain the ML model with new data"""
        # Same logic as web_dashboard.py train_ml_model()
        pass
```

---

## Training Data Collection

### How Training Data is Generated

The bot collects training data from actual trades:

1. **Trade Execution**: Bot places a trade based on signals
2. **Trade Monitoring**: Bot tracks the trade until close
3. **Result Recording**: Bot records:
   - Entry indicators (RSI, MACD, ADX, ATR, EMA, volume)
   - Trade outcome (profitable: True/False)
   - Signal type (BUY/SELL)

4. **Data Storage**: Saved to `data/training_data.csv`

### Training Data Format
```csv
rsi,macd,macd_signal,adx,atr,ema_fast,ema_slow,volume,profitable,signal_type
45.2,0.0012,0.0008,28.5,0.0015,1.2345,1.2340,150000,True,BUY
62.8,-0.0005,-0.0002,32.1,0.0018,1.2350,1.2355,180000,False,SELL
...
```

---

## Current Workflow

### Step-by-Step Process

1. **Enable ML Data Collection**
   - Dashboard → ML Configuration → Enable ML features
   - Bot starts collecting trade data

2. **Run Bot for Data Collection**
   - Bot executes trades normally
   - Each trade result is saved to training data CSV
   - Recommended: 100+ trades (1-2 weeks)

3. **Manual Training**
   - Dashboard → ML Configuration → "Train ML Model" button
   - Bot trains model on collected data
   - Model saved to `models/ml_signal_model.pkl`

4. **Enable ML Predictions**
   - Dashboard → ML Configuration → Enable ML predictions
   - Bot uses trained model to filter signals

5. **Repeat Periodically**
   - Manually retrain every week/month
   - Or implement auto-retrain logic (see above)

---

## Key Files

### Dashboard
- `templates/dashboard.html` (lines 1581-1608): ML training UI
- `templates/dashboard.html` (lines 5258-5302): Training JavaScript

### Backend
- `web_dashboard.py` (lines 1541-1640): Training API endpoint
- `src/ml_signal_generator.py`: ML model training logic
- `src/config_manager.py` (lines 135-138): Default config

### Training Scripts
- `ml_training/FIX_OVERFITTING.py`: Fixed training script
- `ml_training/1_extract_training_data.py`: Data extraction
- `ml_training/2_train_model.py`: Model training
- `ml_training/4_evaluate_model.py`: Model evaluation

---

## Recommendations

### To Enable Auto-Retrain

1. **Add scheduler to bot main loop**
   - Check retrain conditions every hour
   - Track last retrain timestamp
   - Monitor training data size

2. **Add background training**
   - Don't block trading during retraining
   - Use threading or async training
   - Swap models atomically after training

3. **Add safety checks**
   - Validate new model performance before deployment
   - Keep backup of previous model
   - Rollback if new model performs worse

4. **Add monitoring**
   - Log retraining events
   - Track model performance over time
   - Alert if training fails

### Example Implementation
```python
import threading
from datetime import datetime, timedelta

class AutoRetrainer:
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config
        self.last_retrain = None
        self.is_training = False
    
    def check_and_retrain(self):
        """Check if retraining is needed"""
        if not self.config.get('ml_auto_retrain', False):
            return
        
        if self.is_training:
            return  # Already training
        
        # Check frequency
        frequency = self.config.get('ml_retrain_frequency', 'weekly')
        days_map = {'daily': 1, 'weekly': 7, 'monthly': 30}
        days = days_map.get(frequency, 7)
        
        if self.last_retrain:
            if datetime.now() - self.last_retrain < timedelta(days=days):
                return
        
        # Check sample count
        min_samples = self.config.get('ml_min_training_samples', 100)
        data_path = self.config.get('ml_training_data_path')
        
        try:
            df = pd.read_csv(data_path)
            if len(df) < min_samples:
                return
        except:
            return
        
        # Start training in background
        self.is_training = True
        thread = threading.Thread(target=self._train_async)
        thread.start()
    
    def _train_async(self):
        """Train model in background"""
        try:
            self.bot.logger.info("🎓 Auto-retraining ML model...")
            # Call training logic
            success = self._retrain_model()
            if success:
                self.last_retrain = datetime.now()
                self.bot.logger.info("✅ Auto-retrain completed successfully")
            else:
                self.bot.logger.error("❌ Auto-retrain failed")
        finally:
            self.is_training = False
```

---

## Summary

✅ **What Works**:
- Manual training from dashboard
- Training data collection
- Model saving/loading
- Configuration UI

❌ **What Doesn't Work**:
- Automatic periodic retraining
- Background training scheduler
- Auto-retrain monitoring

🔧 **To Enable Auto-Retrain**:
- Add scheduler to bot main loop
- Implement background training
- Add safety checks and monitoring
