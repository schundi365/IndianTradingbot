# MT5 Gold & Silver Trading Bot - Setup Guide

## 🎯 Key Features

✅ **Adaptive Risk Management** - Adjusts SL, TP, and position size based on market conditions  
✅ **Smart Position Sizing** - Automatically calculates lots based on account balance and free margin  
✅ **Split Orders** - Divides position into multiple orders with different take profit levels  
✅ **Intelligent Trailing Stops** - Automatically follows price to protect profits  
✅ **Trade Filtering** - Rejects low-probability setups based on confidence scores (60%+ required)  
✅ **Market Analysis** - Analyzes trend strength, volatility, price structure, and S/R levels  
✅ **Multiple Strategies** - 6 different trailing methods to choose from  
✅ **Safety Limits** - Daily loss limits, max trades, drawdown protection  
✅ **MT5 Native** - Direct integration, no external services needed  

### 🆕 Adaptive Risk Management

The bot intelligently adjusts trading parameters based on real-time market conditions:

**Market Analysis**:
- Trend strength (ADX)
- Volatility levels (ATR ratio)
- Trend consistency
- Price position vs MAs
- Price action momentum
- Support/Resistance proximity

**Dynamic Adjustments**:
- **Stop Loss**: 1.5×ATR (ranging) to 3.0×ATR (volatile)
- **Take Profit**: Conservative [1.0, 1.5, 2.0] to Aggressive [1.5, 3.0, 5.0]
- **Position Size**: 0.3× to 1.5× based on market favorability
- **Trade Filtering**: Rejects setups with confidence < 60%

See `ADAPTIVE_RISK_GUIDE.md` for complete details.

---

## Prerequisites

### 1. MetaTrader 5 Platform
- Download and install MT5 from your broker or [MetaQuotes website](https://www.metatrader5.com/)
- Open a demo or live account with a broker that supports Gold (XAUUSD) and Silver (XAGUSD)
- Make sure MT5 is running when you start the bot

### 2. Python Environment
- Python 3.8 or higher
- Required libraries (install via pip)

## Installation Steps

### Quick Setup

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/mt5-trading-bot.git
cd mt5-trading-bot

# 2. Run setup script
python setup.py

# 3. Test MT5 connection
python test_connection.py

# 4. Configure settings
# Edit src/config.py with your preferences

# 5. Start the bot
python run_bot.py
```

### Manual Installation

### Step 1: Install Python Libraries

```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install MetaTrader5
pip install pandas
pip install numpy
```

### Step 2: Enable Algo Trading in MT5

1. Open MetaTrader 5
2. Go to **Tools → Options → Expert Advisors**
3. Check the following boxes:
   - ✅ Allow algorithmic trading
   - ✅ Allow DLL imports (if required by your broker)
   - ✅ Allow WebRequest for listed URL (optional for news feeds)
4. Click **OK**

### Step 3: Configure Your Bot

Edit `config.py` to match your trading preferences:

```python
# Basic settings
SYMBOLS = ['XAUUSD', 'XAGUSD']  # Gold and Silver
TIMEFRAME = mt5.TIMEFRAME_H1     # 1-hour charts
RISK_PERCENT = 1.0               # Risk 1% per trade

# Strategy settings
FAST_MA_PERIOD = 20              # Fast MA
SLOW_MA_PERIOD = 50              # Slow MA
ATR_MULTIPLIER_SL = 2.0          # Stop loss = 2 × ATR
```

### Step 4: Verify MT5 Connection

Run the test script:

```python
import MetaTrader5 as mt5

# Initialize MT5
if not mt5.initialize():
    print("MT5 initialization failed")
    quit()

# Check connection
print("MT5 version:", mt5.version())

# Check account info
account_info = mt5.account_info()
if account_info:
    print(f"Account balance: {account_info.balance}")
    print(f"Account currency: {account_info.currency}")

# Check if symbols are available
for symbol in ['XAUUSD', 'XAGUSD']:
    info = mt5.symbol_info(symbol)
    if info:
        print(f"{symbol} is available")
    else:
        print(f"{symbol} NOT available - check your broker")

mt5.shutdown()
```

## Running the Bot

### Basic Usage

```bash
python mt5_trading_bot.py
```

### With Custom Configuration

```python
from config import get_config
from mt5_trading_bot import MT5TradingBot

# Load configuration
config = get_config()

# Modify specific settings if needed
config['symbols'] = ['XAUUSD']  # Trade only gold
config['risk_percent'] = 0.5    # Lower risk

# Run bot
bot = MT5TradingBot(config)
bot.run()
```

## Understanding the Strategy

### Entry Signals

The bot uses **Moving Average Crossover Strategy**:

1. **Bullish Signal (BUY)**:
   - Fast MA (20) crosses above Slow MA (50)
   - Price is above both moving averages
   
2. **Bearish Signal (SELL)**:
   - Fast MA (20) crosses below Slow MA (50)
   - Price is below both moving averages

### Risk Management

#### Dynamic Position Sizing
The bot automatically calculates position size based on:
- **Available account balance** and **free margin**
- Your **risk percentage** (default 1% per trade)
- Distance to **stop loss** (wider SL = smaller position)

This ensures you never risk more than your configured percentage, regardless of market volatility.

#### Split Orders & Partial Profit Taking

**NEW FEATURE**: The bot can split your position into multiple orders with different take profit levels!

Instead of one "all-or-nothing" position:
```
Traditional: 0.30 lots @ TP $2160 (one target)
```

The bot creates multiple positions:
```
Split Orders:
- Position 1: 0.12 lots @ TP $2145 (quick profit - 40%)
- Position 2: 0.09 lots @ TP $2175 (moderate - 30%)
- Position 3: 0.09 lots @ TP $2220 (let it run - 30%)
```

**Benefits**:
- ✅ Lock in profits progressively
- ✅ Let winners run while protecting gains
- ✅ Higher win rate (easier to hit first TP)
- ✅ Better risk management
- ✅ Less regret - multiple exit points

**Configuration**:
```python
USE_SPLIT_ORDERS = True
NUM_POSITIONS = 3
TP_LEVELS = [1.5, 2.5, 4.0]  # Risk:Reward ratios
PARTIAL_CLOSE_PERCENT = [40, 30, 30]  # % for each level
```

See `SPLIT_ORDERS_GUIDE.md` for detailed explanation and examples.

#### Stop Loss Calculation
```
Stop Loss = Entry Price ± (ATR × Multiplier)
```
- For BUY: SL = Entry - (2 × ATR)
- For SELL: SL = Entry + (2 × ATR)
- ATR adjusts to market volatility automatically

#### Take Profit Calculation

**Single Position Mode**:
```
Take Profit = Entry ± (Stop Loss Distance × Reward Ratio)
```
- Default 1:2 Risk/Reward ratio
- If risking $50, target is $100 profit

**Split Orders Mode**:
Multiple TPs calculated based on configured ratios:
```
TP1 = Entry ± (SL Distance × 1.5)
TP2 = Entry ± (SL Distance × 2.5)
TP3 = Entry ± (SL Distance × 4.0)
```

### Trailing Stop Management

#### Activation
Trailing stop activates when profit reaches `1.5 × ATR`:
- Protects profits once trade moves favorably
- Initial stop loss remains until activation

#### Trailing Distance
Stop loss trails at `1.0 × ATR` from current price:
- For BUY: SL = Current Price - ATR
- For SELL: SL = Current Price + ATR
- Only moves in profitable direction (never widens)

## Advanced Features

### Multiple Trailing Strategies

Import advanced strategies:

```python
from trailing_strategies import TrailingStrategies, apply_advanced_trailing

# Use different trailing methods
TRAIL_TYPE = 'chandelier'  # Options: 'atr', 'percentage', 'swing', 
                           # 'chandelier', 'breakeven'
```

### Strategy Options

1. **ATR Trailing**: Volatility-based (default)
2. **Percentage Trailing**: Fixed percentage from price
3. **Swing High/Low**: Based on recent swing points
4. **Chandelier Exit**: Highest/Lowest point minus ATR
5. **Breakeven Plus**: Move to BE+, then trail

### Trading Hours Filter

Limit trading to specific times:

```python
ENABLE_TRADING_HOURS = True
TRADING_START_HOUR = 8   # Start at 8:00 UTC
TRADING_END_HOUR = 17    # Stop at 17:00 UTC
TRADING_DAYS = [0, 1, 2, 3, 4]  # Monday-Friday
```

### Safety Limits

Protect your account:

```python
MAX_DAILY_LOSS = 100.0           # Stop if lose $100 in a day
MAX_DAILY_TRADES = 10            # Max 10 trades per day
MAX_DRAWDOWN_PERCENT = 10.0      # Pause if 10% drawdown
MIN_ACCOUNT_BALANCE = 100.0      # Stop if balance < $100
```

## Monitoring Your Bot

### Log Files

The bot creates `trading_bot.log` with detailed information:
- Entry/exit signals
- Trade executions
- Trailing stop updates
- Errors and warnings

### Real-time Monitoring

```python
# Check positions
positions = mt5.positions_get(magic=MAGIC_NUMBER)
for pos in positions:
    print(f"{pos.symbol}: {pos.profit} profit")
```

## Important Notes

### Before Live Trading

1. **Test on Demo Account First**
   - Run for at least 1-2 weeks
   - Verify all functions work correctly
   - Check position sizing calculations

2. **Backtest Your Strategy**
   - Use historical data to test performance
   - Understand expected win rate and drawdowns
   - Adjust parameters based on results

3. **Start Small**
   - Begin with minimum lot sizes
   - Use low risk percentage (0.5-1%)
   - Gradually increase as you gain confidence

### Risk Warnings

⚠️ **Important**: 
- Algorithmic trading carries risk of financial loss
- Past performance doesn't guarantee future results
- Never risk more than you can afford to lose
- Gold and silver markets can be highly volatile
- Always have a stop loss on every trade
- Monitor your bot regularly

### Common Issues & Solutions

**Problem**: "Symbol XAUUSD not found"
- **Solution**: Check if your broker offers this symbol. Some use "GOLD" or "XAUUSD.a"

**Problem**: "Order failed, retcode 10014"
- **Solution**: Invalid volume. Check broker's min/max lot sizes.

**Problem**: "Not enough money"
- **Solution**: Reduce lot size or risk percentage in config.

**Problem**: Bot not placing trades
- **Solution**: 
  - Verify "Allow algorithmic trading" is enabled
  - Check if signals are being generated (check logs)
  - Ensure MT5 is logged in and connected to server

**Problem**: Stop loss not updating
- **Solution**: Check if profit has reached activation threshold (1.5×ATR default)

## Support & Customization

### Customizing the Strategy

To modify entry logic, edit the `check_entry_signal()` method:

```python
def check_entry_signal(self, df):
    # Add your own conditions here
    # Example: Add RSI filter
    
    if latest['rsi'] > 70:  # Overbought
        return 0  # No signal
    
    # Original MA crossover logic
    if latest['ma_cross'] == 1:
        return 1  # Buy signal
```

### Adding Indicators

Add new indicators in `calculate_indicators()`:

```python
# RSI
delta = df['close'].diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / loss
df['rsi'] = 100 - (100 / (1 + rs))

# Bollinger Bands
df['bb_middle'] = df['close'].rolling(20).mean()
df['bb_std'] = df['close'].rolling(20).std()
df['bb_upper'] = df['bb_middle'] + (df['bb_std'] * 2)
df['bb_lower'] = df['bb_middle'] - (df['bb_std'] * 2)
```

## File Structure

```
mt5-trading-bot/
├── src/                           # Core bot code
│   ├── mt5_trading_bot.py        # Main bot script
│   ├── config.py                 # Configuration file
│   ├── adaptive_risk_manager.py  # Adaptive risk system
│   ├── split_order_calculator.py # Position size calculator
│   └── trailing_strategies.py    # Advanced trailing methods
├── docs/                          # Documentation
│   ├── README.md                 # Main documentation
│   ├── ADAPTIVE_RISK_GUIDE.md    # Adaptive risk explained
│   ├── SPLIT_ORDERS_GUIDE.md     # Split orders guide
│   ├── TRAILING_STRATEGIES_GUIDE.md  # Trailing strategies
│   └── QUICK_START_ADAPTIVE.md   # Quick start guide
├── examples/                      # Example configurations
│   ├── config_conservative.py    # Conservative settings
│   ├── config_aggressive.py      # Aggressive settings
│   ├── quick_test.py             # Quick test script
│   └── adaptive_risk_demo.py     # Demo of adaptive features
├── run_bot.py                     # Main entry point
├── test_connection.py             # Connection test script
├── setup.py                       # Setup helper
├── requirements.txt               # Python dependencies
├── .gitignore                     # Git ignore rules
├── LICENSE                        # MIT License
└── CONTRIBUTING.md                # Contribution guidelines
```

## Next Steps

1. Read through all three Python files
2. Understand the strategy logic
3. Test on demo account
4. Optimize parameters using backtest data
5. Monitor performance and adjust as needed

## Disclaimer

This trading bot is provided for educational purposes. The developer is not responsible for any financial losses incurred through the use of this software. Always conduct thorough testing and use proper risk management.

---

**Good luck with your automated trading!** 🚀

For questions or issues, check the log files first, then review the code comments for guidance.
