# Indian Trading Bot - Running Guide

## ✅ Bot Successfully Started!

The Indian Market Trading Bot is now running in **Paper Trading Mode** (safe mode with no real money).

## Current Status

- **Mode**: Paper Trading (Simulated)
- **Initial Balance**: ₹100,000
- **Broker**: Kite Connect (Paper Trading Adapter)
- **Strategy**: Mean Reversion
- **Timeframe**: 5 minutes
- **Instruments**: 5 NSE stocks (RELIANCE, TCS, INFY, HDFCBANK, ICICIBANK)
- **Risk per Trade**: 0.5%
- **Max Positions**: 5

## What's Happening

The bot is currently monitoring the market. Since Indian markets are closed (trading hours: 09:30 - 15:00 IST), the bot is waiting for the next trading session.

### Market Hours
- **Trading Hours**: 09:30 AM - 03:00 PM IST (Monday to Friday)
- **Current Time**: After market hours
- **Next Session**: Next trading day at 09:30 AM IST

## How to Use

### Running the Bot

```bash
# Start bot with default config (Paper Trading)
python run_indian_bot.py

# Start bot with specific config
python run_indian_bot.py configs/nifty_intraday.json
```

### Stopping the Bot

Press `Ctrl+C` to stop the bot gracefully.

### Monitoring

The bot logs all activity to:
- **Console**: Real-time output
- **Log File**: `indian_trading_bot.log`
- **Decision Log**: `trading_decisions.log`

### Viewing Logs

```bash
# View main log
type indian_trading_bot.log

# View recent activity (last 50 lines)
Get-Content indian_trading_bot.log -Tail 50

# View trading decisions
type trading_decisions.log
```

## Configuration

The bot uses the configuration file at `configs/_current.json`.

### Current Configuration

- **Strategy**: Mean Reversion
- **Instruments**: 5 NSE equities
- **Timeframe**: 5 minutes
- **Risk Management**:
  - Risk per trade: 0.5%
  - Stop loss: 0.75%
  - Take profit: 1.5%
  - Max daily loss: 2.0%
  - Max positions: 5

### Modifying Configuration

You can modify the configuration in two ways:

1. **Using the Dashboard** (Recommended):
   ```bash
   python start_dashboard.py
   # Open browser to http://127.0.0.1:8080
   ```

2. **Editing JSON directly**:
   ```bash
   # Edit the config file
   notepad configs/_current.json
   ```

## Features Enabled

The bot has the following features enabled:

✅ **Paper Trading** - Safe simulation mode
✅ **Adaptive Risk Management** - Dynamic position sizing
✅ **Volume Analysis** - Volume-based signal filtering
✅ **Trend Detection** - Advanced trend analysis
✅ **Market Structure Analysis** - Support/resistance detection
✅ **Multiple Indicators**:
  - Aroon Indicator
  - EMA Momentum
  - Divergence Detection
  - Multi-timeframe Analysis
  - Trendline Analysis

## Trading Logic

### Mean Reversion Strategy

The bot looks for:
1. **Overbought/Oversold Conditions**: RSI > 70 or < 30
2. **Bollinger Band Extremes**: Price touching outer bands
3. **Volume Confirmation**: Adequate volume for reversal
4. **Trend Context**: Favorable market structure

### Entry Conditions
- Price at Bollinger Band extremes
- RSI overbought (>70) for shorts or oversold (<30) for longs
- Minimum reversion distance: 1.5 standard deviations
- Volume above minimum threshold

### Exit Conditions
- Take profit: 1.5% gain
- Stop loss: 0.75% loss
- Max holding time: 180 minutes
- Scale out at 0.75% and 1.5% levels

## Safety Features

### Paper Trading Mode
- No real money at risk
- Simulated order execution
- Realistic price simulation
- Full feature testing

### Risk Management
- Maximum 5 concurrent positions
- 0.5% risk per trade
- 2% maximum daily loss limit
- Position sizing based on account balance

### Trading Hours
- Only trades during market hours (09:30 - 15:00 IST)
- Avoids first and last candles
- Respects market holidays

## Switching to Live Trading

⚠️ **WARNING**: Live trading involves real money and risk!

To switch to live trading:

1. **Ensure you have a Kite Connect account**
2. **Authenticate with Kite**:
   ```bash
   python kite_login.py
   ```
3. **Update configuration**:
   - Set `"paper_trading": false` in config
   - Set `"broker": "kite"` in config
4. **Start bot**:
   ```bash
   python run_indian_bot.py
   ```
5. **Confirm live trading** when prompted

## Troubleshooting

### Bot Not Starting

Check:
- Python dependencies installed: `pip install -r requirements.txt`
- Configuration file exists: `configs/_current.json`
- No syntax errors in config file

### No Trades Happening

Possible reasons:
- Market is closed (check trading hours)
- No signals generated (strategy conditions not met)
- Risk limits reached (max positions or daily loss)
- Instruments not available

### Unicode Errors in Logs

The bot uses emojis in logs which may not display correctly on Windows. This doesn't affect functionality. To fix:
- Use UTF-8 compatible terminal
- Or ignore the warnings (bot works fine)

## Next Steps

1. **Monitor the bot** during market hours to see it in action
2. **Review logs** to understand trading decisions
3. **Adjust configuration** based on performance
4. **Use the dashboard** for visual monitoring and configuration
5. **Test thoroughly** in paper trading before going live

## Dashboard

For a visual interface to monitor and configure the bot:

```bash
# Start the dashboard
python start_dashboard.py

# Open browser
http://127.0.0.1:8080
```

The dashboard provides:
- Real-time bot status
- Position monitoring
- Trade history
- Configuration builder
- Risk metrics
- Account information

## Support

- **Logs**: Check `indian_trading_bot.log` for detailed information
- **Configuration**: See `configs/_current.json`
- **Documentation**: See `README.md` and `USER_GUIDE.md`

---

**Bot Status**: ✅ Running in Paper Trading Mode
**Market Status**: Closed (waiting for next session)
**Balance**: ₹100,000 (simulated)
**Risk**: Minimal (paper trading only)
