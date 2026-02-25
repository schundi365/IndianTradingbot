# Source Code Structure

This directory contains the modular source code for the MT5 Trading Bot.

## Directory Organization

### 📦 adapters/
Broker and trading platform integrations
- `broker_adapter.py` - Generic broker adapter interface
- `kite_adapter.py` - Zerodha Kite Connect integration
- `paper_trading_adapter.py` - Paper trading simulation adapter

### 📊 analyzers/
Market analysis and trend detection modules
- `ema_momentum_analyzer.py` - EMA-based momentum analysis
- `market_structure_analyzer.py` - Market structure detection
- `multi_timeframe_analyzer.py` - Multi-timeframe analysis
- `sentiment_analyzer.py` - Market sentiment analysis
- `trend_detection_engine.py` - Trend identification engine
- `trendline_analyzer.py` - Trendline detection and analysis
- `volume_analyzer.py` - Volume profile analysis

### 🎯 core/
Core trading bot functionality
- `config.py` - Configuration definitions
- `indian_trading_bot.py` - Main trading bot implementation
- `paper_trading.py` - Paper trading core logic
- `pattern_recognition.py` - Chart pattern recognition
- `trading_decision_logger.py` - Trade decision logging
- `trailing_strategies.py` - Trailing stop strategies

### 📈 indicators/
Technical indicators and signal generators
- `aroon_indicator.py` - Aroon indicator implementation
- `divergence_detector.py` - Price/indicator divergence detection
- `enhanced_indicators.py` - Enhanced technical indicators

### ⚙️ managers/
Risk, configuration, and database management
- `adaptive_risk_manager.py` - Dynamic risk management
- `config_manager.py` - Configuration management
- `database_manager.py` - Database operations
- `dynamic_sl_manager.py` - Dynamic stop-loss management
- `dynamic_tp_manager.py` - Dynamic take-profit management
- `scalping_manager.py` - Scalping strategy management

### 🤖 ml/
Machine learning and reinforcement learning
- `ml_integration.py` - ML model integration
- `ml_signal_generator.py` - ML-based signal generation
- `reinforcement_learning.py` - RL trading agent
- `rl_log_trainer.py` - RL model training from logs

### 🛠️ utils/
Utility functions and helpers
- `config_migration.py` - Configuration migration tools
- `db_logging_handler.py` - Database logging handler
- `error_handler.py` - Error handling utilities
- `instrument_validator.py` - Trading instrument validation
- `logging_utils.py` - Logging utilities
- `split_order_calculator.py` - Order splitting calculations

## Import Examples

```python
# Adapters
from src.adapters.kite_adapter import KiteAdapter
from src.adapters.paper_trading_adapter import PaperTradingAdapter

# Core
from src.core.indian_trading_bot import IndianTradingBot
from src.core.config import Config

# Analyzers
from src.analyzers.trend_detection_engine import TrendDetectionEngine
from src.analyzers.volume_analyzer import VolumeAnalyzer

# Managers
from src.managers.adaptive_risk_manager import AdaptiveRiskManager
from src.managers.config_manager import ConfigManager

# ML
from src.ml.ml_signal_generator import MLSignalGenerator

# Utils
from src.utils.logging_utils import setup_logging
from src.utils.error_handler import ErrorHandler
```

## Module Dependencies

```
core/
├── adapters/
├── analyzers/
├── indicators/
├── managers/
├── ml/
└── utils/
```

The `core` module depends on all other modules. Other modules should minimize cross-dependencies.
