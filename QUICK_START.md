# Quick Start Guide

Get the MT5 Trading Bot running in 5 minutes!

## Prerequisites

- ✅ MetaTrader 5 installed
- ✅ Python 3.8+ installed
- ✅ Demo or live MT5 account

## Installation (3 steps)

### 1. Clone & Setup

```bash
git clone https://github.com/yourusername/mt5-trading-bot.git
cd mt5-trading-bot
python setup.py
```

### 2. Test Connection

Make sure MT5 is running, then:

```bash
python test_connection.py
```

You should see: `✅ ALL TESTS PASSED`

### 3. Start Trading

```bash
python run_bot.py
```

That's it! The bot is now running with default settings.

## Default Configuration

- **Symbols:** Gold (XAUUSD) & Silver (XAGUSD)
- **Risk:** 1% per trade
- **Strategy:** Moving Average Crossover
- **Features:** Adaptive risk, split orders, trailing stops

## Customization

Edit `src/config.py` to change settings:

```python
# Trade only Gold
SYMBOLS = ['XAUUSD']

# Lower risk
RISK_PERCENT = 0.5

# Disable split orders
USE_SPLIT_ORDERS = False
```

## Monitoring

- **Log file:** `trading_bot.log`
- **MT5 terminal:** Check open positions
- **Stop bot:** Press `Ctrl+C`

## Safety First

⚠️ **Always test on demo account first!**

1. Run for at least 2 weeks on demo
2. Verify all features work correctly
3. Start with low risk (0.5-1%)
4. Monitor closely initially

## Next Steps

- 📖 Read [Complete Documentation](docs/README.md)
- 🎯 Learn about [Adaptive Risk](docs/ADAPTIVE_RISK_GUIDE.md)
- 📊 Understand [Split Orders](docs/SPLIT_ORDERS_GUIDE.md)
- 🧪 Follow [Testing Guide](docs/TESTING_GUIDE.md)

## Need Help?

- 🐛 [Report a bug](https://github.com/yourusername/mt5-trading-bot/issues)
- 💬 [Ask questions](https://github.com/yourusername/mt5-trading-bot/discussions)
- 📚 [Read the docs](docs/)

## Common Issues

**"MT5 initialization failed"**
- Make sure MT5 is running
- Check you're logged into an account

**"Symbol XAUUSD not found"**
- Your broker may use different symbol names
- Check available symbols in MT5

**"Not enough money"**
- Reduce `RISK_PERCENT` in config
- Check your account balance

---

**Happy Trading! 🚀**
