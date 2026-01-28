# Quick Reference Card

## 🚀 Getting Started (First Time)

```bash
# 1. Setup
python setup.py

# 2. Test MT5 (make sure MT5 is running & logged in!)
python test_mt5_simple.py

# 3. Start bot
python run_bot.py
```

## ⚠️ Before Running Bot

**MT5 Must Be:**
- ✅ Installed
- ✅ Running (window open)
- ✅ Logged into an account (demo or live)
- ✅ Showing account balance

**If you get "Authorization failed":**
1. Open MT5
2. File → Login to Trade Account
3. Enter credentials
4. Run test again

## 🧪 Testing Commands

```bash
# 1. Simple connection test
python test_mt5_simple.py

# 2. Check trading permissions (safe - no trades)
python test_trading_permissions.py

# 3. Test actual trading capability (places 1 test trade)
python test_trading_capability.py

# 4. Full connection test
python test_connection.py

# 5. Validate setup
python validate_setup.py

# 6. Quick signal test (no trades)
python examples/quick_test.py
```

## 🎯 Running the Bot

```bash
# Start with default settings
python run_bot.py

# Stop the bot
Press Ctrl+C
```

## 📝 Configuration

**File:** `src/config.py`

**Key Settings:**
```python
# Risk management
RISK_PERCENT = 1.0          # Risk per trade (0.5-2%)
MAX_DAILY_LOSS = 100.0      # Stop after this loss

# Symbols
SYMBOLS = ['XAUUSD', 'XAGUSD']  # Change if needed

# Features
USE_ADAPTIVE_RISK = True    # Enable adaptive risk
USE_SPLIT_ORDERS = True     # Enable split orders
ENABLE_TRAILING_STOP = True # Enable trailing
```

## 📊 Monitoring

**Log File:** `trading_bot.log`

**Check:**
- Signals detected
- Trades placed
- Errors/warnings
- Performance

**In MT5:**
- Open positions
- Account balance
- Trade history

## 🛑 Emergency Stop

```bash
# Stop bot immediately
Press Ctrl+C

# Close all positions manually in MT5
Right-click position → Close
```

## ⚙️ Common Adjustments

### Lower Risk
```python
RISK_PERCENT = 0.5  # From 1.0 to 0.5
```

### Change Symbols
```python
SYMBOLS = ['XAUUSD']  # Trade only Gold
```

### Disable Features
```python
USE_SPLIT_ORDERS = False
USE_ADAPTIVE_RISK = False
```

### Adjust Confidence
```python
MIN_TRADE_CONFIDENCE = 0.50  # From 0.60 to 0.50
```

## 🐛 Troubleshooting

| Error | Solution |
|-------|----------|
| Authorization failed | Login to MT5 account |
| Symbol not found | Check symbol name in MT5 |
| Not enough money | Lower RISK_PERCENT |
| Trade disabled | Enable algo trading in MT5 |
| No signals | Wait or adjust parameters |

**Full guide:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## 📖 Documentation

| Document | Purpose |
|----------|---------|
| [README.md](README.md) | Main overview |
| [QUICK_START.md](QUICK_START.md) | 5-minute setup |
| [docs/README.md](docs/README.md) | Complete guide |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Fix issues |
| [docs/TESTING_GUIDE.md](docs/TESTING_GUIDE.md) | Testing procedures |

## 🔧 File Locations

```
mt5-trading-bot/
├── src/config.py           # ← Edit settings here
├── run_bot.py              # ← Run this to start
├── test_mt5_simple.py      # ← Test connection
├── trading_bot.log         # ← Check logs here
└── docs/                   # ← Read guides here
```

## 📞 Getting Help

1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Review `trading_bot.log`
3. Run `python test_mt5_simple.py`
4. Check [GitHub Issues](https://github.com/yourusername/mt5-trading-bot/issues)

## ⚠️ Safety Reminders

- ✅ Always test on demo first (2+ weeks)
- ✅ Start with low risk (0.5-1%)
- ✅ Monitor regularly
- ✅ Never risk more than you can afford to lose
- ✅ Have stop losses on every trade

## 🎓 Learning Path

1. **Day 1:** Setup and test connection
2. **Day 2-3:** Read documentation
3. **Week 1:** Demo testing with default settings
4. **Week 2:** Adjust parameters and optimize
5. **Week 3+:** Continue demo or go live (carefully!)

## 📈 Performance Tracking

**Track These Metrics:**
- Win rate (target: 40-60%)
- Profit factor (target: 1.5+)
- Max drawdown (target: <10%)
- Risk:Reward ratio (target: 1.5:1+)

**Review:**
- Daily: Check trades and balance
- Weekly: Analyze performance
- Monthly: Optimize parameters

---

**Quick Start:** `python test_mt5_simple.py` → `python run_bot.py`

**Need Help?** Read [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

**Ready to Deploy?** Read [READY_TO_DEPLOY.md](READY_TO_DEPLOY.md)
