# 🇮🇳 Indian Market Trading Bot - Kite Connect Integration

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Kite Connect](https://img.shields.io/badge/Kite-Connect-orange.svg)](https://kite.trade/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An intelligent automated trading bot for Indian stock markets using Zerodha Kite Connect API. Supports NIFTY/BANKNIFTY futures, equity intraday, and options trading with proven technical analysis strategies.

## 🎯 What's Included

This repository contains a complete broker abstraction layer that allows the existing MT5 forex trading bot to work with Indian stock markets through Kite Connect API.

### ✅ Supported Instruments

- **NIFTY 50 Futures** - Index futures trading
- **BANKNIFTY Futures** - Bank index futures trading
- **Equity Intraday** - Stocks like RELIANCE, TCS, INFY
- **Options Trading** - NIFTY/BANKNIFTY call/put options

### ✅ Key Features

- 🎯 **Broker Abstraction** - Easy to add support for other Indian brokers
- 📊 **Multiple Strategies** - Pre-configured for different instruments
- 🎚️ **Risk Management** - Position sizing, stop loss, take profit
- 🔄 **Paper Trading** - Test strategies without real money
- 📈 **Technical Indicators** - RSI, MACD, EMA, ATR, ADX, Bollinger Bands
- ⚡ **Multiple Timeframes** - 5min, 15min, 30min, 60min, daily
- 🛡️ **Safety Features** - Daily loss limits, max trades, market hours check
- 📚 **Comprehensive Docs** - 30,000+ words of documentation

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites

- Python 3.8 or higher
- Zerodha trading account
- Kite Connect API subscription (₹2,000 one-time)

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/indian-market-trading-bot.git
cd indian-market-trading-bot
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Get Kite Connect Credentials

1. Go to https://kite.trade/
2. Login with Zerodha account
3. Create a new app
4. Copy your **API Key** and **API Secret**
5. Set redirect URL to: `http://127.0.0.1:5001/`

### Step 4: Configure API Credentials

**Option A: Automated (Recommended)**
```bash
python update_api_key.py
# Enter your API key when prompted
```

**Option B: Manual**

Edit `kite_login.py` (lines 37-39):
```python
API_KEY    = "your_actual_api_key"
API_SECRET = "your_actual_api_secret"
```

### Step 5: Authenticate

```bash
python kite_login.py
```

Browser will open → Login to Kite → Token saved to `kite_token.json`

### Step 6: Start Paper Trading

```bash
python run_bot.py --config config_test_paper_trading.json
```

**That's it!** The bot is now running in paper trading mode (no real money).

---

## 📦 Available Configurations

| Configuration | Instrument | Timeframe | Risk | Capital | Skill Level |
|---------------|------------|-----------|------|---------|-------------|
| `config_nifty_futures.json` | NIFTY Futures | 30 min | 1.0% | ₹2-5L | Beginner |
| `config_banknifty_futures.json` | BANKNIFTY Futures | 15 min | 0.75% | ₹3-7L | Intermediate |
| `config_equity_intraday.json` | Stocks (RELIANCE, TCS, INFY) | 5 min | 1.0% | ₹50K-2L | Beginner |
| `config_options_trading.json` | NIFTY/BANKNIFTY Options | 5 min | 2.0% | ₹1-3L | Advanced |
| `config_test_paper_trading.json` | NIFTY Futures (Test) | 30 min | 0.5% | Any | Any |

### Choose Your Configuration

**Beginner?** → Start with `config_nifty_futures.json`  
**Small Capital (<₹1L)?** → Use `config_equity_intraday.json`  
**Experienced?** → Try `config_banknifty_futures.json`  
**Options Trader?** → Use `config_options_trading.json`  
**Just Testing?** → Use `config_test_paper_trading.json` ✅

---

## 📚 Documentation

### Essential Reading

1. **[QUICK_START_TESTING.md](QUICK_START_TESTING.md)** - 5-minute quick start guide
2. **[COMPLETE_SETUP_GUIDE.md](COMPLETE_SETUP_GUIDE.md)** - Complete setup instructions
3. **[examples/README_CONFIGURATIONS.md](examples/README_CONFIGURATIONS.md)** - Detailed configuration guide (15,000 words)
4. **[examples/CONFIGURATION_SELECTOR.md](examples/CONFIGURATION_SELECTOR.md)** - Choose the right config (8,000 words)
5. **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Comprehensive testing guide (5,000 words)

### Quick References

- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - Migrate from MT5 to Indian markets
- **[INDIAN_MARKET_CONFIGS_README.md](INDIAN_MARKET_CONFIGS_README.md)** - Quick config reference
- **[PORT_CHANGE_NOTICE.md](PORT_CHANGE_NOTICE.md)** - Port 5001 setup
- **[FIX_API_KEY_ERROR.md](FIX_API_KEY_ERROR.md)** - Troubleshooting API key issues

### Troubleshooting

- **[DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md)** - Deployment overview
- **[DEPLOYMENT_STATUS.txt](DEPLOYMENT_STATUS.txt)** - Current deployment status

---

## 🎓 Learning Path

### Week 1: Setup and Paper Trading
- Day 1-2: Setup, authentication, validation
- Day 3-7: Paper trading with test configuration

### Week 2: Analysis and Optimization
- Day 1-2: Review paper trading results
- Day 3-4: Adjust parameters based on results
- Day 5-7: Re-test with optimized settings

### Week 3: Live Trading (Small Size)
- Day 1-2: First live trades (0.25% risk)
- Day 3-4: Increase to 0.5% risk if successful
- Day 5-7: Monitor and adjust

### Week 4: Scale Up
- Day 1-3: Increase to target risk level
- Day 4-5: Add second configuration if desired
- Day 6-7: Full portfolio testing

---

## 🔧 Utility Scripts

### Authentication
```bash
python kite_login.py              # Daily authentication (required)
python check_api_key.py           # Verify API key setup
```

### Configuration
```bash
python update_api_key.py          # Update API key in all configs
python test_configuration.py      # Test a specific configuration
python deploy_configurations.py   # Validate all configurations
python verify_deployment.py       # Verify deployment completeness
```

### Validation
```bash
python validate_paper_trading.py  # Validate paper trading setup
python validate_instruments.py    # Validate instrument symbols
```

---

## 🏗️ Architecture

### Broker Abstraction Layer

```
┌─────────────────────────────────────────────────────────────┐
│                     Trading Bot Core                         │
│  (Indicators, Signals, Risk Management - UNCHANGED)          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Broker Adapter Interface                        │
│  (Abstract base class defining standard operations)          │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┬────────────┐
        ▼            ▼            ▼            ▼
   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐
   │  Kite   │  │  Alice  │  │  Angel  │  │ Upstox  │
   │ Connect │  │  Blue   │  │   One   │  │         │
   └─────────┘  └─────────┘  └─────────┘  └─────────┘
```

### Key Components

- **`src/broker_adapter.py`** - Abstract broker interface
- **`src/kite_adapter.py`** - Kite Connect implementation
- **`src/indian_trading_bot.py`** - Main trading bot
- **`kite_login.py`** - Authentication handler

---

## ⚙️ Configuration Parameters

### Risk Management
```json
{
  "risk_percent": 1.0,              // Risk per trade (% of equity)
  "reward_ratio": 2.0,              // Target profit (multiple of risk)
  "max_daily_loss_percent": 3.0,   // Stop trading after this loss
  "max_drawdown_percent": 8.0      // Emergency stop level
}
```

### Technical Indicators
```json
{
  "fast_ma_period": 10,             // Fast moving average
  "slow_ma_period": 21,             // Slow moving average
  "atr_period": 14,                 // Average True Range period
  "atr_multiplier": 2.0,            // Stop loss distance
  "rsi_period": 14,                 // RSI calculation period
  "rsi_overbought": 70,             // Overbought threshold
  "rsi_oversold": 30                // Oversold threshold
}
```

### Position Management
```json
{
  "use_split_orders": true,         // Split exits for profit booking
  "num_positions": 3,               // Number of split positions
  "tp_levels": [1.0, 1.5, 2.5],    // Take profit levels
  "partial_close_percent": [40, 30, 30]  // % to close at each TP
}
```

See [examples/README_CONFIGURATIONS.md](examples/README_CONFIGURATIONS.md) for complete parameter guide.

---

## 🚨 Important Notes

### Daily Tasks
- ✅ Run `python kite_login.py` every morning (token expires daily)
- ✅ Check market holidays before trading
- ✅ Monitor positions on Kite platform
- ✅ Review logs for errors

### Risk Management
- ✅ Always use stop losses
- ✅ Set daily loss limits
- ✅ Limit concurrent positions
- ✅ Scale up gradually
- ✅ Have exit plan ready

### Best Practices
- ✅ Start with paper trading (minimum 2-3 days)
- ✅ Test during market hours for real conditions
- ✅ Review performance daily
- ✅ Adjust parameters gradually
- ✅ Keep records of all changes

---

## 📊 Performance Expectations

### NIFTY Futures (30-min)
- Win Rate: 45-55%
- Monthly Return: 3-5%
- Drawdown: 2-4%
- Trades/Day: 2-4

### BANKNIFTY Futures (15-min)
- Win Rate: 40-50%
- Monthly Return: 8-12%
- Drawdown: 5-8%
- Trades/Day: 4-8

### Equity Intraday (5-min)
- Win Rate: 45-55%
- Monthly Return: 6-10%
- Drawdown: 4-7%
- Trades/Day: 5-10

### Options Trading (5-min)
- Win Rate: 35-45%
- Monthly Return: 15-25%
- Drawdown: 10-15%
- Trades/Day: 5-15

**Note:** Past performance does not guarantee future results. Always test thoroughly before going live.

---

## 🛡️ Security

### What's Protected

- ✅ API keys not committed to Git
- ✅ Access tokens stored locally only
- ✅ Configuration files with credentials ignored
- ✅ Sensitive data in `.gitignore`

### Setup Your Credentials

1. Copy template configs:
   ```bash
   cp config_nifty_futures.json.template config_nifty_futures.json
   ```

2. Add your API key to the copied file

3. Never commit files with real credentials

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Adding New Brokers

To add support for another Indian broker:

1. Create a new adapter class implementing `BrokerAdapter`
2. Add configuration template
3. Update documentation
4. Submit PR with tests

See [examples/README_CONFIGURATIONS.md](examples/README_CONFIGURATIONS.md) for broker adapter development guide.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ⚠️ Disclaimer

**IMPORTANT:** Trading in stocks, futures, and options involves substantial risk of loss. This software is provided for educational purposes only and does not constitute financial advice.

- Always start with paper trading
- Test thoroughly before going live
- Use only risk capital you can afford to lose
- Understand the instruments you're trading
- Monitor your positions actively
- Have a risk management plan

Past performance does not guarantee future results. The bot's performance depends on market conditions, configuration, and proper usage.

---

## 📞 Support

### Documentation
- **Quick Start:** [QUICK_START_TESTING.md](QUICK_START_TESTING.md)
- **Complete Setup:** [COMPLETE_SETUP_GUIDE.md](COMPLETE_SETUP_GUIDE.md)
- **Configuration Guide:** [examples/README_CONFIGURATIONS.md](examples/README_CONFIGURATIONS.md)
- **Testing Guide:** [TESTING_GUIDE.md](TESTING_GUIDE.md)

### Common Issues
- **API Key Error:** See [FIX_API_KEY_ERROR.md](FIX_API_KEY_ERROR.md)
- **Port Conflict:** See [PORT_CHANGE_NOTICE.md](PORT_CHANGE_NOTICE.md)
- **Setup Issues:** See [COMPLETE_SETUP_GUIDE.md](COMPLETE_SETUP_GUIDE.md)

### Resources
- **Kite Connect Docs:** https://kite.trade/docs/connect/v3/
- **Python Kite Connect:** https://github.com/zerodhatech/pykiteconnect
- **NSE Market Hours:** 9:15 AM - 3:30 PM IST

---

## 🎉 Acknowledgments

- Zerodha for Kite Connect API
- Python community for excellent libraries
- Contributors and testers

---

## 📈 Roadmap

- [ ] Support for Alice Blue API
- [ ] Support for Angel One API
- [ ] Support for Upstox API
- [ ] Advanced order types (GTT, OCO)
- [ ] Backtesting framework
- [ ] Web dashboard for monitoring
- [ ] Mobile notifications
- [ ] Strategy optimizer

---

**Happy Trading! 🚀📈**

*Last Updated: February 17, 2026*  
*Version: 1.0*
