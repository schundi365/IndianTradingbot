# 🤖 MT5 Gold & Silver Trading Bot

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MT5](https://img.shields.io/badge/MetaTrader-5-green.svg)](https://www.metatrader5.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An intelligent automated trading bot for MetaTrader 5 that trades Gold (XAUUSD) and Silver (XAGUSD) using adaptive risk management, split orders, and advanced trailing strategies.

## ✨ Key Features

- 🎯 **Adaptive Risk Management** - Automatically adjusts stop loss, take profit, and position size based on real-time market conditions
- 📊 **Smart Position Sizing** - Calculates optimal lot sizes based on account balance, free margin, and risk percentage
- 🎚️ **Split Orders** - Divides positions into multiple orders with different take profit levels for progressive profit-taking
- 🔄 **Intelligent Trailing Stops** - 6 different trailing strategies to protect and maximize profits
- 🛡️ **Trade Filtering** - Rejects low-probability setups based on confidence scores (60%+ required)
- 📈 **Market Analysis** - Analyzes trend strength, volatility, price structure, and support/resistance levels
- ⚡ **Multiple Strategies** - Moving average crossover with ATR-based stops and dynamic targets
- 🔒 **Safety Limits** - Daily loss limits, max trades, drawdown protection, and account safeguards
- 🚀 **MT5 Native** - Direct integration with MetaTrader 5, no external services needed

## 🚀 Quick Start

### Prerequisites

- MetaTrader 5 platform installed and running
- Python 3.8 or higher
- Demo or live MT5 account with Gold/Silver access

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/mt5-trading-bot.git
cd mt5-trading-bot

# Run setup
python setup.py

# Test connection
python test_connection.py

# Start trading
python run_bot.py
```

### Configuration

Edit `src/config.py` to customize your trading strategy:

```python
# Basic settings
SYMBOLS = ['XAUUSD', 'XAGUSD']  # Gold and Silver
RISK_PERCENT = 1.0               # Risk 1% per trade
REWARD_RATIO = 2.0               # 1:2 Risk:Reward

# Adaptive risk
USE_ADAPTIVE_RISK = True         # Enable intelligent adjustments
MIN_TRADE_CONFIDENCE = 0.60      # Minimum 60% confidence

# Split orders
USE_SPLIT_ORDERS = True
TP_LEVELS = [1.5, 2.5, 4.0]     # Multiple profit targets
```

## 📖 Documentation

- **[Complete Setup Guide](docs/README.md)** - Detailed installation and configuration
- **[Adaptive Risk Guide](docs/ADAPTIVE_RISK_GUIDE.md)** - How adaptive risk management works
- **[Split Orders Guide](docs/SPLIT_ORDERS_GUIDE.md)** - Understanding split order strategy
- **[Trailing Strategies](docs/TRAILING_STRATEGIES_GUIDE.md)** - 6 different trailing methods
- **[Quick Start](docs/QUICK_START_ADAPTIVE.md)** - Get started in 5 minutes

## 🎯 Trading Strategy

### Entry Signals

**Moving Average Crossover Strategy:**
- **BUY**: Fast MA (20) crosses above Slow MA (50) + price above both MAs
- **SELL**: Fast MA (20) crosses below Slow MA (50) + price below both MAs

### Risk Management

**Adaptive Stop Loss:**
- Ranging market: 1.5× ATR
- Trending market: 2.0× ATR  
- Volatile market: 3.0× ATR

**Dynamic Take Profit:**
- Conservative: [1.0, 1.5, 2.0] R:R ratios
- Balanced: [1.5, 2.5, 4.0] R:R ratios
- Aggressive: [1.5, 3.0, 5.0] R:R ratios

**Position Sizing:**
- Automatically calculated based on account balance and free margin
- Adjusts for market conditions (0.3× to 1.5× multiplier)
- Respects broker's min/max lot sizes

## 📊 Example Configurations

### Conservative (Beginners)
```python
RISK_PERCENT = 0.5
TP_LEVELS = [1.0, 1.5, 2.0]
MIN_TRADE_CONFIDENCE = 0.70
MAX_TRADES_TOTAL = 2
```

### Balanced (Recommended)
```python
RISK_PERCENT = 1.0
TP_LEVELS = [1.5, 2.5, 4.0]
MIN_TRADE_CONFIDENCE = 0.60
MAX_TRADES_TOTAL = 5
```

### Aggressive (Experienced)
```python
RISK_PERCENT = 2.0
TP_LEVELS = [2.0, 3.5, 6.0]
MIN_TRADE_CONFIDENCE = 0.55
MAX_TRADES_TOTAL = 5
```

See `examples/` folder for complete configuration files.

## 🧪 Testing

### Test MT5 Connection
```bash
python test_connection.py
```

### Quick Test (Single Iteration)
```bash
python examples/quick_test.py
```

### Demo Adaptive Risk
```bash
python examples/adaptive_risk_demo.py
```

## 📁 Project Structure

```
mt5-trading-bot/
├── src/                    # Core bot code
│   ├── mt5_trading_bot.py
│   ├── config.py
│   ├── adaptive_risk_manager.py
│   ├── split_order_calculator.py
│   └── trailing_strategies.py
├── docs/                   # Documentation
├── examples/               # Example scripts & configs
├── run_bot.py             # Main entry point
├── test_connection.py     # Connection test
└── setup.py               # Setup helper
```

## ⚙️ Advanced Features

### Adaptive Risk Management

The bot analyzes 6 market conditions in real-time:
1. Trend strength (ADX)
2. Volatility levels (ATR ratio)
3. Trend consistency
4. Price position vs MAs
5. Price momentum
6. Support/Resistance proximity

Based on this analysis, it dynamically adjusts:
- Stop loss width (1.5× to 3.0× ATR)
- Take profit targets (conservative to aggressive)
- Position size (0.3× to 1.5× multiplier)
- Trade filtering (rejects low-confidence setups)

### Split Orders

Instead of one position with one target:
```
Traditional: 0.30 lots @ TP $2160
```

The bot creates multiple positions:
```
Position 1: 0.12 lots @ TP $2145 (40% - quick profit)
Position 2: 0.09 lots @ TP $2175 (30% - moderate)
Position 3: 0.09 lots @ TP $2220 (30% - let it run)
```

Benefits:
- ✅ Lock in profits progressively
- ✅ Let winners run while protecting gains
- ✅ Higher win rate
- ✅ Better risk management

### Trailing Strategies

6 different trailing methods:
1. **ATR Trailing** - Volatility-based (default)
2. **Percentage Trailing** - Fixed percentage from price
3. **Swing High/Low** - Based on recent swing points
4. **Chandelier Exit** - Highest/Lowest point minus ATR
5. **Breakeven Plus** - Move to BE+, then trail
6. **Parabolic SAR** - Acceleration-based trailing

## 🛡️ Safety Features

- Daily loss limits
- Maximum trades per day
- Drawdown protection
- Minimum account balance checks
- Trading hours restrictions
- Position size limits
- Broker compatibility checks

## ⚠️ Risk Warning

**IMPORTANT:** Trading involves substantial risk of loss. This bot is provided for educational purposes only. The authors are not responsible for any financial losses incurred through the use of this software.

**Before Live Trading:**
1. ✅ Test on demo account for at least 1-2 weeks
2. ✅ Understand all configuration options
3. ✅ Start with minimum lot sizes
4. ✅ Use low risk percentage (0.5-1%)
5. ✅ Monitor regularly
6. ✅ Never risk more than you can afford to lose

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- MetaTrader 5 platform by MetaQuotes
- Python community for excellent libraries
- Trading community for strategy insights

## 📧 Support

- 📖 Read the [documentation](docs/README.md)
- 🐛 Report bugs via [GitHub Issues](https://github.com/yourusername/mt5-trading-bot/issues)
- 💬 Ask questions in [Discussions](https://github.com/yourusername/mt5-trading-bot/discussions)

---

**Made with ❤️ for algorithmic traders**

⭐ Star this repo if you find it useful!
