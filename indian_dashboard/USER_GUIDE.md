# Indian Market Web Dashboard - User Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Broker Setup](#broker-setup)
4. [Instrument Selection](#instrument-selection)
5. [Configuration](#configuration)
6. [Monitoring Your Bot](#monitoring-your-bot)
7. [Trade History](#trade-history)
8. [Troubleshooting](#troubleshooting)

---

## 1. Introduction

Welcome to the Indian Market Web Dashboard! This web-based interface allows you to configure and monitor your automated trading bot for Indian stock markets (NSE, BSE, NFO). 

### Key Features
- **Multi-Broker Support**: Connect to Kite Connect, Alice Blue, Angel One, Upstox, or use Paper Trading
- **Visual Instrument Selection**: Browse and select stocks/instruments without manual symbol lookup
- **Configuration Management**: Save, load, and manage multiple trading configurations
- **Real-Time Monitoring**: Track bot status, positions, and account information
- **Trade History**: View and analyze your trading performance

### System Requirements
- Python 3.8 or higher
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Active broker account (for live trading)
- Internet connection

---

## 2. Getting Started

### Installation

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variables**
   ```bash
   # Windows
   set FLASK_SECRET_KEY=your-secret-key-here
   set ENCRYPTION_KEY=your-encryption-key-here
   
   # Linux/Mac
   export FLASK_SECRET_KEY=your-secret-key-here
   export ENCRYPTION_KEY=your-encryption-key-here
   ```

3. **Start the Dashboard**
   ```bash
   python indian_dashboard/indian_dashboard.py
   ```

4. **Access the Dashboard**
   - Open your browser and navigate to: `http://localhost:8080`
   - You should see the dashboard home page with the Broker tab active

### First-Time Setup Checklist
- [ ] Dashboard is running and accessible
- [ ] Broker credentials are ready
- [ ] Trading strategy is planned
- [ ] Risk parameters are defined

---

## 3. Broker Setup

The Broker tab is where you connect your trading account to the dashboard. This is the first step before you can select instruments or configure trading parameters.

### 3.1 Selecting Your Broker

**Screenshot Placeholder: Broker Selection Screen**
*Shows dropdown/cards with broker logos: Kite Connect, Alice Blue, Angel One, Upstox, Paper Trading*

1. Navigate to the **Broker** tab (should be active by default)
2. You'll see a list of supported brokers
3. Click on your broker to select it

### 3.2 Broker-Specific Setup

#### Kite Connect (Zerodha)

**Screenshot Placeholder: Kite Connect Login Form**
*Shows API Key, API Secret fields, and "Login with Kite" button*

**Option 1: OAuth Flow (Recommended)**
1. Click the **"Login with Kite"** button
2. You'll be redirected to Zerodha's login page
3. Enter your Kite credentials and complete 2FA
4. Authorize the application
5. You'll be redirected back to the dashboard
6. Connection status will show "Connected"

**Option 2: Manual Credentials**
1. Enter your **API Key** (from Kite Connect developer console)
2. Enter your **API Secret**
3. Click **"Request Token"** to get access token
4. Click **"Test Connection"**

**Where to Get Credentials:**
- Log in to [Kite Connect](https://kite.trade/)
- Go to "Apps" → "Create New App"
- Note down your API Key and API Secret

#### Alice Blue

**Screenshot Placeholder: Alice Blue Login Form**
*Shows User ID and API Key fields*

1. Enter your **User ID** (your Alice Blue client ID)
2. Enter your **API Key** (from Alice Blue API portal)
3. Click **"Test Connection"**

**Where to Get Credentials:**
- Contact Alice Blue support for API access
- API Key will be provided via email

#### Angel One

**Screenshot Placeholder: Angel One Login Form**
*Shows Client ID, Password, and TOTP fields*

1. Enter your **Client ID**
2. Enter your **Password**
3. Enter your **TOTP** (Time-based One-Time Password from authenticator app)
4. Click **"Test Connection"**

**Where to Get Credentials:**
- Use your Angel One trading account credentials
- Enable TOTP in your Angel One account settings

#### Upstox

**Screenshot Placeholder: Upstox Login Form**
*Shows API Key, API Secret, and Redirect URI fields*

1. Enter your **API Key**
2. Enter your **API Secret**
3. Enter your **Redirect URI** (usually `http://localhost:8080/callback`)
4. Click **"Test Connection"**

**Where to Get Credentials:**
- Log in to [Upstox Developer Console](https://api.upstox.com/)
- Create a new app
- Note down API Key and Secret

#### Paper Trading

**Screenshot Placeholder: Paper Trading Option**
*Shows "No credentials required" message with Connect button*

1. Select **"Paper Trading"**
2. Click **"Connect"**
3. No credentials needed - this is for testing without real money

**Note:** Paper trading simulates trades without using real money. Perfect for testing strategies!

### 3.3 Verifying Connection

**Screenshot Placeholder: Successful Connection Status**
*Shows green checkmark, broker name, user info, and connection time*

After successful connection, you'll see:
- ✅ **Connection Status**: Connected
- **Broker**: Your selected broker name
- **User**: Your name/ID from broker
- **Connected At**: Timestamp of connection

If connection fails:
- Check your credentials
- Ensure your broker account is active
- Verify internet connection
- Check broker API status

### 3.4 Disconnecting

To disconnect from your broker:
1. Click the **"Disconnect"** button
2. Confirm the action
3. You'll be returned to broker selection

**Note:** Disconnecting will stop any running bot and clear your session.

---

## 4. Instrument Selection

The Instruments tab allows you to browse and select stocks/instruments to trade. No need to manually look up symbols!

### 4.1 Loading Instruments

**Screenshot Placeholder: Instrument Table**
*Shows table with columns: Symbol, Name, Exchange, Type, Price, Select checkbox*

1. Navigate to the **Instruments** tab
2. Instruments will load automatically from your connected broker
3. First load may take a few seconds (instruments are cached for 24 hours)

### 4.2 Searching for Instruments

**Screenshot Placeholder: Search Bar**
*Shows search input with example "RELIANCE" typed*

1. Use the **search bar** at the top of the table
2. Type symbol name (e.g., "RELIANCE") or company name
3. Results update as you type (debounced search)
4. Search matches are highlighted

**Search Tips:**
- Search by symbol: "INFY", "TCS", "NIFTY"
- Search by company name: "Infosys", "Tata"
- Partial matches work: "REL" finds "RELIANCE"

### 4.3 Filtering Instruments

**Screenshot Placeholder: Filter Controls**
*Shows dropdown filters for Exchange and Instrument Type*

**Filter by Exchange:**
- **NSE**: National Stock Exchange (equity, indices)
- **BSE**: Bombay Stock Exchange (equity)
- **NFO**: NSE Futures & Options

**Filter by Instrument Type:**
- **EQ**: Equity (stocks)
- **FUT**: Futures
- **CE**: Call Options
- **PE**: Put Options

**Example Filters:**
- NSE + EQ = NSE stocks
- NFO + FUT = Futures contracts
- NFO + CE = Call options

### 4.4 Selecting Instruments

**Screenshot Placeholder: Selected Instruments**
*Shows checkboxes selected for multiple instruments*

**Single Selection:**
1. Click the checkbox next to an instrument
2. It will be added to your selection

**Multiple Selection:**
1. Click **"Select All"** to select all visible instruments
2. Or manually check multiple instruments
3. Click **"Clear All"** to deselect everything

**Selection Tips:**
- Select instruments you want to trade
- You can select from different exchanges
- Mix equity and F&O instruments
- Minimum 1 instrument required

### 4.5 Selected Instruments Panel

**Screenshot Placeholder: Selected Panel**
*Shows list of selected instruments with count and remove buttons*

The right panel shows your selected instruments:
- **Count**: Total number selected
- **List**: Each selected instrument with remove (×) button
- **Continue Button**: Proceed to configuration

To remove an instrument:
1. Click the **×** button next to it
2. Or uncheck it in the main table

### 4.6 Refreshing Instruments

**Screenshot Placeholder: Refresh Button**
*Shows refresh icon button with last updated timestamp*

To refresh the instrument list:
1. Click the **"Refresh"** button
2. Wait for instruments to reload from broker
3. Cache timestamp updates

**When to Refresh:**
- New instruments added by broker
- Expiry of F&O contracts
- Price data seems stale
- After 24 hours (cache expiry)

---

## 5. Configuration

The Configuration tab is where you set up your trading strategy, risk parameters, and other settings.

### 5.1 Configuration Form Overview

**Screenshot Placeholder: Configuration Form**
*Shows tabbed interface with Basic, Strategy, Risk, Advanced sections*

The configuration form has four sections:
1. **Basic Settings**: Instruments, timeframe, strategy
2. **Risk Management**: Risk per trade, position limits
3. **Strategy Parameters**: Indicator settings, TP/SL
4. **Advanced**: Trading hours, paper trading toggle

### 5.2 Basic Settings

**Screenshot Placeholder: Basic Settings Section**
*Shows selected instruments, timeframe dropdown, strategy selector*

**Selected Instruments**
- Displays instruments you selected in the Instruments tab
- Click "Change" to go back and modify selection

**Timeframe**
- Select your trading timeframe
- Options: 1min, 5min, 15min, 1hour, 1day
- Recommendation: 5min or 15min for intraday

**Strategy**
- Select your trading strategy
- Options: Trend Following, Mean Reversion, Breakout, etc.
- Each strategy has different indicator requirements

**Trading Hours**
- **Start Time**: Default 09:15 (market open)
- **End Time**: Default 15:30 (market close)
- Adjust for your trading schedule

### 5.3 Risk Management

**Screenshot Placeholder: Risk Management Section**
*Shows sliders and inputs for risk parameters*

**Risk Per Trade**
- Percentage of capital to risk per trade
- Slider: 0.5% to 5%
- Recommendation: 1-2% for conservative, 2-3% for moderate

**Max Positions**
- Maximum number of concurrent open positions
- Range: 1 to 10
- Recommendation: 3-5 positions for diversification

**Max Daily Loss**
- Maximum loss allowed per day (percentage)
- Range: 1% to 10%
- Bot stops trading if this limit is hit
- Recommendation: 3-5% of capital

**Position Sizing**
- **Fixed**: Same size for all trades
- **Risk-Based**: Size based on stop loss distance
- **Percentage**: Fixed percentage of capital

### 5.4 Strategy Parameters

**Screenshot Placeholder: Strategy Parameters Section**
*Shows indicator parameter inputs*

Parameters vary by strategy. Common indicators:

**Moving Averages**
- Fast MA Period: 10-20
- Slow MA Period: 50-200

**RSI (Relative Strength Index)**
- Period: 14 (standard)
- Overbought: 70
- Oversold: 30

**ADX (Average Directional Index)**
- Period: 14
- Threshold: 25 (trend strength)

**Take Profit / Stop Loss**
- **TP Percentage**: Target profit (e.g., 2%)
- **SL Percentage**: Maximum loss (e.g., 1%)
- **Trailing Stop**: Enable/disable trailing stop loss

### 5.5 Real-Time Validation

**Screenshot Placeholder: Validation Errors**
*Shows inline error messages in red*

The form validates your inputs in real-time:
- ✅ **Green checkmark**: Valid input
- ❌ **Red error**: Invalid input with explanation
- **Save button disabled** until all errors are fixed

Common validation errors:
- "Risk per trade must be between 0.5% and 5%"
- "At least one instrument must be selected"
- "Trading hours must be within market hours"

### 5.6 Risk Metrics Panel

**Screenshot Placeholder: Risk Metrics Display**
*Shows calculated risk metrics in a card*

The risk metrics panel shows:
- **Max Position Size**: ₹ per trade
- **Risk Per Trade**: ₹ and %
- **Margin Required**: Estimated margin
- **Max Concurrent Risk**: Total risk if all positions lose

These update automatically as you change parameters.

### 5.7 Configuration Presets

**Screenshot Placeholder: Preset Dropdown**
*Shows preset options: NIFTY Futures, BANKNIFTY Futures, etc.*

Quick-start with preset configurations:

**NIFTY 50 Futures**
- Timeframe: 15min
- Strategy: Trend Following
- Risk: 2% per trade
- Suitable for: Index futures trading

**BANKNIFTY Futures**
- Timeframe: 5min
- Strategy: Breakout
- Risk: 2.5% per trade
- Suitable for: Volatile index trading

**Equity Intraday**
- Timeframe: 5min
- Strategy: Mean Reversion
- Risk: 1.5% per trade
- Suitable for: Stock intraday trading

**Options Trading**
- Timeframe: 15min
- Strategy: Directional
- Risk: 3% per trade
- Suitable for: Options strategies

To use a preset:
1. Click **"Load Preset"** dropdown
2. Select a preset
3. Modify parameters as needed
4. Save your configuration

### 5.8 Saving Configurations

**Screenshot Placeholder: Save Dialog**
*Shows input field for configuration name*

To save your configuration:
1. Click **"Save Configuration"**
2. Enter a name (e.g., "NIFTY Scalping Strategy")
3. Click **"Save"**
4. Configuration is saved to disk

**Overwriting:**
- If name exists, you'll be asked to confirm overwrite
- Original configuration is backed up

### 5.9 Loading Configurations

**Screenshot Placeholder: Load Dialog**
*Shows list of saved configurations with dates*

To load a saved configuration:
1. Click **"Load Configuration"**
2. Select from list of saved configs
3. Configuration loads into form
4. Review and modify if needed

**Deleting Configurations:**
- Click the trash icon next to a configuration
- Confirm deletion
- Configuration file is removed

### 5.10 Export/Import

**Screenshot Placeholder: Export/Import Buttons**
*Shows Export JSON and Import JSON buttons*

**Export Configuration:**
1. Click **"Export to JSON"**
2. Configuration downloads as JSON file
3. Share with others or backup

**Import Configuration:**
1. Click **"Import from JSON"**
2. Select JSON file from your computer
3. Configuration is validated and loaded

**Copy to Clipboard:**
- Click **"Copy to Clipboard"**
- Configuration copied as JSON
- Paste into text editor or share

---

## 6. Monitoring Your Bot

The Monitor tab shows real-time information about your running bot, account, and positions.

### 6.1 Bot Status Card

**Screenshot Placeholder: Bot Status Card**
*Shows status indicator, uptime, and control buttons*

**Status Indicators:**
- 🟢 **Running**: Bot is active and trading
- 🔴 **Stopped**: Bot is not running
- 🟡 **Starting**: Bot is initializing

**Information Displayed:**
- **Status**: Current bot state
- **Uptime**: How long bot has been running
- **Broker**: Connected broker name
- **Positions**: Number of open positions

**Control Buttons:**
- **Start**: Start the trading bot
- **Stop**: Stop the trading bot
- **Restart**: Restart the bot (stop + start)

### 6.2 Starting the Bot

**Screenshot Placeholder: Start Confirmation**
*Shows confirmation dialog before starting bot*

To start the bot:
1. Ensure broker is connected
2. Ensure configuration is saved
3. Click **"Start Bot"**
4. Confirm the action
5. Bot begins trading

**Pre-Start Checklist:**
- ✅ Broker connected
- ✅ Instruments selected
- ✅ Configuration validated
- ✅ Risk parameters set
- ✅ Sufficient account balance

### 6.3 Stopping the Bot

To stop the bot:
1. Click **"Stop Bot"**
2. Confirm the action
3. Bot stops after current iteration
4. Open positions remain (not auto-closed)

**When to Stop:**
- End of trading day
- Unexpected market conditions
- Need to modify configuration
- Reached daily loss limit

### 6.4 Account Information Card

**Screenshot Placeholder: Account Info Card**
*Shows balance, equity, margin, and P&L*

**Account Metrics:**
- **Balance**: Total account balance
- **Equity**: Balance + unrealized P&L
- **Available Margin**: Margin available for new trades
- **Used Margin**: Margin locked in open positions
- **Today's P&L**: Profit/Loss for current day

**Color Coding:**
- 🟢 Green: Positive P&L
- 🔴 Red: Negative P&L
- ⚪ Gray: Neutral/Zero

### 6.5 Positions Table

**Screenshot Placeholder: Positions Table**
*Shows open positions with details*

**Columns:**
- **Symbol**: Instrument symbol
- **Qty**: Quantity (positive for long, negative for short)
- **Entry Price**: Average entry price
- **Current Price**: Latest market price
- **P&L**: Unrealized profit/loss
- **Actions**: Close position button

**Position Actions:**
- Click **"Close"** to manually close a position
- Confirm the action
- Position is closed at market price

**Total P&L:**
- Displayed at bottom of table
- Sum of all open positions

### 6.6 Auto-Refresh

**Screenshot Placeholder: Refresh Controls**
*Shows auto-refresh toggle and manual refresh button*

**Auto-Refresh:**
- Enabled by default
- Updates every 5 seconds
- Pauses when tab is inactive (saves resources)

**Manual Refresh:**
- Click **"Refresh"** button
- Forces immediate update
- Shows last updated timestamp

**What Gets Refreshed:**
- Bot status
- Account information
- Open positions
- Current prices

---

## 7. Trade History

The Trades tab shows your historical trades and performance statistics.

### 7.1 Trade History Table

**Screenshot Placeholder: Trade History Table**
*Shows completed trades with all details*

**Columns:**
- **Date/Time**: When trade was executed
- **Symbol**: Instrument traded
- **Type**: BUY or SELL
- **Qty**: Quantity traded
- **Entry Price**: Entry price
- **Exit Price**: Exit price
- **P&L**: Realized profit/loss
- **Duration**: How long position was held

**Sorting:**
- Click column headers to sort
- Default: Most recent first

**Pagination:**
- Navigate through pages if many trades
- Adjust items per page

### 7.2 Date Range Filter

**Screenshot Placeholder: Date Range Picker**
*Shows from/to date inputs and quick filter buttons*

**Custom Date Range:**
1. Select **"From Date"**
2. Select **"To Date"**
3. Click **"Apply"**
4. Table updates with filtered trades

**Quick Filters:**
- **Today**: Today's trades only
- **This Week**: Last 7 days
- **This Month**: Current month
- **All Time**: All trades

### 7.3 Trade Statistics

**Screenshot Placeholder: Statistics Cards**
*Shows key performance metrics*

**Key Metrics:**
- **Total Trades**: Number of completed trades
- **Win Rate**: Percentage of profitable trades
- **Total P&L**: Sum of all realized P&L
- **Average P&L**: Average profit/loss per trade
- **Best Trade**: Largest winning trade
- **Worst Trade**: Largest losing trade

**Performance Indicators:**
- 🟢 Win Rate > 50%: Good
- 🟡 Win Rate 40-50%: Average
- 🔴 Win Rate < 40%: Needs improvement

### 7.4 Exporting Trades

**Screenshot Placeholder: Export Buttons**
*Shows CSV and Excel export buttons*

**Export to CSV:**
1. Click **"Export to CSV"**
2. File downloads automatically
3. Open in Excel or Google Sheets

**Export to Excel:**
1. Click **"Export to Excel"**
2. File downloads as .xlsx
3. Includes formatting and formulas

**What's Exported:**
- All trades in current filter
- All columns from table
- Summary statistics

---

## 8. Troubleshooting

### 8.1 Common Issues

#### Dashboard Won't Start

**Problem:** Error when running `python indian_dashboard.py`

**Solutions:**
1. Check Python version: `python --version` (need 3.8+)
2. Install dependencies: `pip install -r requirements.txt`
3. Check port 8080 is not in use
4. Set environment variables (FLASK_SECRET_KEY, ENCRYPTION_KEY)

#### Can't Connect to Broker

**Problem:** "Connection failed" error

**Solutions:**
1. Verify credentials are correct
2. Check broker API status (visit broker's status page)
3. Ensure broker account is active
4. Check internet connection
5. Try disconnecting and reconnecting
6. For Kite: Ensure access token is not expired

#### Instruments Not Loading

**Problem:** Instrument table is empty

**Solutions:**
1. Ensure broker is connected
2. Click "Refresh Instruments"
3. Check browser console for errors (F12)
4. Clear cache and reload page
5. Check broker API limits

#### Configuration Won't Save

**Problem:** "Failed to save configuration" error

**Solutions:**
1. Check all validation errors are fixed
2. Ensure `configs/` directory exists
3. Check file permissions
4. Try a different configuration name
5. Check disk space

#### Bot Won't Start

**Problem:** Bot fails to start

**Solutions:**
1. Ensure broker is connected
2. Verify configuration is valid
3. Check at least one instrument is selected
4. Ensure sufficient account balance
5. Check bot logs for specific errors

### 8.2 Error Messages

| Error Message | Meaning | Solution |
|--------------|---------|----------|
| "No broker connected" | Broker not authenticated | Connect to broker first |
| "Invalid configuration" | Config has errors | Fix validation errors |
| "Insufficient margin" | Not enough funds | Add funds or reduce position size |
| "Rate limit exceeded" | Too many API calls | Wait and try again |
| "Session expired" | Login session timed out | Reconnect to broker |
| "Invalid instrument" | Instrument not found | Refresh instruments list |

### 8.3 Performance Issues

#### Dashboard is Slow

**Solutions:**
1. Reduce auto-refresh frequency
2. Limit number of selected instruments
3. Clear browser cache
4. Close other browser tabs
5. Check system resources

#### Bot is Missing Trades

**Solutions:**
1. Check timeframe is appropriate
2. Verify strategy parameters
3. Ensure sufficient margin
4. Check max positions limit
5. Review bot logs

### 8.4 Getting Help

**Log Files:**
- Dashboard logs: `logs/dashboard.log`
- Bot logs: `logs/bot.log`
- Check logs for detailed error messages

**Support Channels:**
- GitHub Issues: Report bugs and request features
- Documentation: Check README files
- Community: Trading forums and groups

**Before Asking for Help:**
1. Check this troubleshooting section
2. Review error messages in logs
3. Try basic solutions (restart, reconnect)
4. Note exact steps to reproduce issue
5. Gather relevant information (OS, Python version, broker)

---

## Appendix A: Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl + S` | Save configuration |
| `Ctrl + R` | Refresh current tab |
| `Ctrl + 1-5` | Switch to tab 1-5 |
| `Esc` | Close dialog/modal |

## Appendix B: Configuration File Format

Configurations are saved as JSON files in the `configs/` directory:

```json
{
  "name": "My Strategy",
  "broker": "kite",
  "instruments": [
    {
      "symbol": "RELIANCE",
      "exchange": "NSE",
      "instrument_token": "738561"
    }
  ],
  "strategy": "trend_following",
  "timeframe": "15min",
  "risk_per_trade": 2.0,
  "max_positions": 3,
  "max_daily_loss": 5.0,
  "indicators": {
    "fast_ma": 10,
    "slow_ma": 50,
    "rsi_period": 14
  },
  "trading_hours": {
    "start": "09:15",
    "end": "15:30"
  },
  "paper_trading": false
}
```

## Appendix C: API Rate Limits

Different brokers have different API rate limits:

| Broker | Requests/Second | Requests/Minute |
|--------|----------------|-----------------|
| Kite Connect | 10 | 200 |
| Alice Blue | 5 | 100 |
| Angel One | 10 | 250 |
| Upstox | 10 | 200 |
| Paper Trading | Unlimited | Unlimited |

**Tips to Avoid Rate Limits:**
- Use appropriate timeframes (avoid 1min for many instruments)
- Cache instrument data
- Limit number of concurrent positions
- Use websockets for real-time data (if available)

## Appendix D: Glossary

**Terms:**
- **Instrument**: A tradeable security (stock, future, option)
- **Symbol**: Unique identifier for an instrument
- **Exchange**: Trading venue (NSE, BSE, NFO)
- **Timeframe**: Candlestick interval (1min, 5min, etc.)
- **Position**: An open trade (long or short)
- **P&L**: Profit and Loss
- **Margin**: Collateral required to open a position
- **Stop Loss**: Price level to exit losing trade
- **Take Profit**: Price level to exit winning trade
- **Paper Trading**: Simulated trading without real money

---

**Document Version**: 1.0.0  
**Last Updated**: 2024-02-18  
**Dashboard Version**: 1.0.0

For the latest version of this guide, visit the project repository.
