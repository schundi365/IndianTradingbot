# ML Features Guide

## Overview

The GEM Trading Bot now includes advanced Machine Learning capabilities:

1. **ML-Based Signal Generation** - XGBoost classifier for trend prediction
2. **Sentiment Analysis** - Market sentiment from news and social media
3. **Advanced Pattern Recognition** - ML-based chart pattern detection

## Installation

### Install ML Dependencies

```bash
pip install -r requirements_ml.txt
```

This installs:
- XGBoost (gradient boosting)
- scikit-learn (ML utilities)
- TextBlob (sentiment analysis)
- SciPy (pattern recognition)

### Download TextBlob Corpora (First Time Only)

```bash
python -m textblob.download_corpora
```

## Features

### 1. ML-Based Signal Generation

Uses XGBoost machine learning model to predict market direction.

**Features Used:**
- Price returns and volatility
- RSI, MACD, ADX indicators
- ATR (volatility)
- EMA crossovers
- Volume patterns
- Bollinger Band position

**How It Works:**
1. Extracts 15+ features from market data
2. Feeds features to trained XGBoost model
3. Outputs BUY/SELL/NEUTRAL with confidence score
4. Model learns from historical data

**Training the Model:**
```python
from src.ml_integration import MLIntegration

ml_integration = MLIntegration(config, logger)

# Prepare historical data
# historical_data = DataFrame with features
# labels = Binary labels (1=buy, 0=sell)

ml_integration.train_ml_model(historical_data, labels)
```

### 2. Sentiment Analysis

Analyzes market sentiment from news headlines and text.

**Capabilities:**
- Text sentiment scoring (-1 to 1)
- Keyword-based analysis
- News headline aggregation
- Confidence scoring based on consistency

**Sentiment Sources:**
- News headlines
- Market commentary
- Social media (future)
- Economic reports

**How It Works:**
1. Analyzes text using TextBlob or keyword matching
2. Calculates polarity (positive/negative)
3. Weights by objectivity
4. Aggregates multiple sources
5. Generates trading signal

**Example:**
```python
from src.sentiment_analyzer import SentimentAnalyzer

analyzer = SentimentAnalyzer()

headlines = [
    "EUR/USD rallies on strong economic data",
    "Markets show bullish momentum",
    "Positive outlook for forex pairs"
]

sentiment = analyzer.analyze_news_headlines(headlines)
# Returns: {'average_score': 0.65, 'classification': 'BULLISH', 'confidence': 0.8}
```

### 3. Advanced Pattern Recognition

Detects chart patterns using statistical methods and ML.

**Patterns Detected:**
- **Reversal Patterns:**
  - Double Top/Bottom
  - Head and Shoulders
  - Inverse Head and Shoulders
  - Rising/Falling Wedges

- **Continuation Patterns:**
  - Ascending/Descending Triangles
  - Bullish/Bearish Flags
  - Symmetrical Triangles

**How It Works:**
1. Identifies peaks and troughs using scipy
2. Analyzes trendlines with linear regression
3. Matches patterns to known formations
4. Calculates confidence scores
5. Generates trading signals

**Example:**
```python
from src.pattern_recognition import PatternRecognition

recognizer = PatternRecognition()

ohlc_data = {
    'open': [...],
    'high': [...],
    'low': [...],
    'close': [...]
}

patterns = recognizer.detect_all_patterns(ohlc_data)
# Returns list of detected patterns with confidence scores
```

## Configuration

Add to your `bot_config.json`:

```json
{
  "ml_enabled": true,
  "sentiment_enabled": true,
  "pattern_enabled": true,
  
  "technical_weight": 0.4,
  "ml_weight": 0.3,
  "sentiment_weight": 0.15,
  "pattern_weight": 0.15,
  
  "ml_min_confidence": 0.6,
  "ml_training_enabled": false
}
```

### Configuration Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ml_enabled` | Enable ML signal generation | `false` |
| `sentiment_enabled` | Enable sentiment analysis | `false` |
| `pattern_enabled` | Enable pattern recognition | `true` |
| `technical_weight` | Weight for technical signals | `0.4` |
| `ml_weight` | Weight for ML signals | `0.3` |
| `sentiment_weight` | Weight for sentiment signals | `0.15` |
| `pattern_weight` | Weight for pattern signals | `0.15` |
| `ml_min_confidence` | Minimum confidence to trade | `0.6` |

**Note:** Weights are automatically normalized to sum to 1.0

## Integration with Trading Bot

The ML features integrate seamlessly with your existing bot:

### Signal Combination

All signals are combined using weighted voting:

```
Combined Score = (Technical × 0.4) + (ML × 0.3) + (Sentiment × 0.15) + (Pattern × 0.15)
```

### Enhanced Decision Making

```python
from src.ml_integration import MLIntegration

ml_integration = MLIntegration(config, logger)

# Get enhanced signal
enhanced_signals = ml_integration.get_enhanced_signal(
    symbol='EURUSD',
    market_data=market_data,
    technical_signal='BUY',
    technical_confidence=0.7,
    news_data=news_headlines  # Optional
)

# Check if should trade
should_trade = ml_integration.should_trade(enhanced_signals, min_confidence=0.6)

# Get position size multiplier
multiplier = ml_integration.get_signal_strength_multiplier(enhanced_signals)
```

### Signal Output

Enhanced signals include:

```python
{
    'technical': {'signal': 'BUY', 'confidence': 0.7},
    'ml': {'signal': 'BUY', 'confidence': 0.75},
    'sentiment': {'signal': 'NEUTRAL', 'confidence': 0.5},
    'pattern': {'signal': 'BUY', 'confidence': 0.8},
    'combined': {'signal': 'BUY', 'confidence': 0.72},
    'analysis': 'Technical: BUY (0.70) | ML: BUY (0.75) | Sentiment: NEUTRAL (0.50) | Pattern: BUY (0.80) | Combined: BUY (0.72)'
}
```

## Dashboard Integration

The ML features can be controlled from the dashboard:

### ML Controls Section

Add to dashboard:
- Enable/Disable ML signals
- Enable/Disable sentiment analysis
- Enable/Disable pattern recognition
- Adjust signal weights
- View ML analysis in real-time
- Display detected patterns
- Show sentiment scores

## Training the ML Model

### Collecting Training Data

```python
import pandas as pd
from src.ml_signal_generator import MLSignalGenerator

# Collect historical data
historical_features = []
historical_labels = []

for trade in past_trades:
    features = extract_features(trade['market_data'])
    label = 1 if trade['profitable'] else 0
    
    historical_features.append(features)
    historical_labels.append(label)

# Create DataFrame
df = pd.DataFrame(historical_features)
labels = np.array(historical_labels)

# Train model
ml_generator = MLSignalGenerator()
ml_generator.train_model(df, labels)
```

### Model Updates

The model can be updated incrementally:

```python
# Update with new data
ml_generator.update_model(new_data, new_labels)
```

### Model Persistence

Models are automatically saved to `models/ml_signal_model.pkl` and loaded on startup.

## Performance Optimization

### Signal Agreement

The system requires at least 2 out of 4 components to agree before trading:

```python
# Example: BUY signal requires 2+ components showing BUY
Technical: BUY ✓
ML: BUY ✓
Sentiment: NEUTRAL
Pattern: SELL

Result: Trade allowed (2 BUY signals)
```

### Position Sizing

Position size is adjusted based on combined confidence:

| Confidence | Multiplier | Effect |
|------------|------------|--------|
| < 0.5 | 0.5x | Reduce position |
| 0.5-0.7 | 0.75x | Slightly reduce |
| 0.7-0.85 | 1.0x | Normal position |
| > 0.85 | 1.25x | Increase position |

## Best Practices

### 1. Start Conservative

Begin with pattern recognition only:
```json
{
  "ml_enabled": false,
  "sentiment_enabled": false,
  "pattern_enabled": true
}
```

### 2. Add ML Gradually

Once comfortable, enable ML:
```json
{
  "ml_enabled": true,
  "ml_weight": 0.2,
  "technical_weight": 0.6
}
```

### 3. Train on Your Data

Train the ML model on your specific:
- Trading symbols
- Timeframes
- Market conditions
- Historical performance

### 4. Monitor Performance

Track ML signal accuracy:
- Win rate by signal type
- Confidence vs. profitability
- Pattern detection accuracy
- Sentiment correlation

### 5. Adjust Weights

Fine-tune weights based on performance:
```python
# If ML performs well, increase weight
config['ml_weight'] = 0.4
config['technical_weight'] = 0.4

# If sentiment is unreliable, decrease weight
config['sentiment_weight'] = 0.05
```

## Troubleshooting

### XGBoost Not Available

```bash
pip install xgboost
```

### TextBlob Not Working

```bash
pip install textblob
python -m textblob.download_corpora
```

### Model Not Training

Check:
1. Sufficient historical data (100+ samples)
2. Balanced labels (not all buy or all sell)
3. Valid feature values (no NaN or inf)

### Low Confidence Scores

Possible causes:
- Conflicting signals
- Insufficient training data
- Market uncertainty
- Need to retrain model

## Future Enhancements

Planned features:
1. **LSTM Networks** - Deep learning for time series
2. **Reinforcement Learning** - Adaptive trading policies
3. **Real-time News API** - Live sentiment feeds
4. **Social Media Sentiment** - Twitter/Reddit analysis
5. **Multi-timeframe ML** - Signals across timeframes
6. **Ensemble Models** - Multiple ML models voting
7. **Feature Engineering** - Advanced technical features
8. **AutoML** - Automatic model optimization

## Support

For issues or questions:
1. Check logs for ML-related errors
2. Verify dependencies installed
3. Test individual components
4. Review configuration settings

## Example: Complete Integration

```python
from src.ml_integration import MLIntegration

# Initialize
config = {
    'ml_enabled': True,
    'sentiment_enabled': True,
    'pattern_enabled': True,
    'technical_weight': 0.4,
    'ml_weight': 0.3,
    'sentiment_weight': 0.15,
    'pattern_weight': 0.15
}

ml_integration = MLIntegration(config, logger)

# In your trading loop
for symbol in symbols:
    # Get market data
    market_data = get_market_data(symbol)
    
    # Get technical signal
    technical_signal = analyze_technical(market_data)
    
    # Get enhanced signal
    enhanced = ml_integration.get_enhanced_signal(
        symbol=symbol,
        market_data=market_data,
        technical_signal=technical_signal,
        technical_confidence=0.7
    )
    
    # Make trading decision
    if ml_integration.should_trade(enhanced, min_confidence=0.6):
        multiplier = ml_integration.get_signal_strength_multiplier(enhanced)
        position_size = base_position_size * multiplier
        
        execute_trade(
            symbol=symbol,
            signal=enhanced['combined']['signal'],
            size=position_size
        )
```

## Conclusion

The ML features provide powerful enhancements to your trading bot:
- More accurate signals through ensemble methods
- Sentiment-aware trading decisions
- Automated pattern detection
- Adaptive position sizing
- Continuous learning capability

Start with pattern recognition, gradually enable ML and sentiment, and fine-tune based on your results.
