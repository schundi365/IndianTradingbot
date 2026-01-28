# Web Dashboard Guide

## Overview
Modern web-based interface for your MT5 Trading Bot with real-time monitoring, configuration, and AI-powered recommendations.

---

## Features

### 1. Real-Time Monitoring
- ✅ Live account balance and equity
- ✅ Current profit/loss
- ✅ Open positions count
- ✅ Win rate and performance metrics
- ✅ Auto-refresh every 5 seconds

### 2. Bot Control
- ✅ Start/Stop bot with one click
- ✅ Visual status indicator (running/stopped)
- ✅ Safe shutdown handling

### 3. Configuration Management
- ✅ Select trading symbols (XAUUSD, GBPUSD, XAGUSD, etc.)
- ✅ Choose timeframe (M1, M5, M15, M30, H1)
- ✅ Adjust risk per trade
- ✅ Configure stop loss (ATR multiplier)
- ✅ Set confidence threshold
- ✅ Configure daily loss limit
- ✅ Adjust scalping parameters
- ✅ Enable/disable trading hours
- ✅ Save changes instantly

### 4. Trade History
- ✅ View all closed trades (last 7 days)
- ✅ Filter by symbol, type, profit
- ✅ Export to CSV (coming soon)
- ✅ Color-coded wins/losses

### 5. Open Positions
- ✅ Real-time position monitoring
- ✅ Entry price, current price, SL, TP
- ✅ Live profit/loss per position
- ✅ Position details (ticket, volume, time)

### 6. AI Recommendations
- ✅ Automated trade analysis
- ✅ Priority-based suggestions
- ✅ Impact estimation ($ savings)
- ✅ One-click implementation
- ✅ Based on your actual trade history

---

## Installation

### Step 1: Install Dependencies
```bash
pip install -r requirements_web.txt
```

### Step 2: Start the Dashboard
```bash
python web_dashboard.py
```

### Step 3: Open Browser
Navigate to: **http://localhost:5000**

---

## Usage

### Starting the Bot

1. **Configure Settings**
   - Click "Configuration" tab
   - Select trading symbols
   - Choose timeframe
   - Adjust risk parameters
   - Click "Save Configuration"

2. **Start Trading**
   - Click "Start Bot" button
   - Status indicator turns green
   - Bot begins scanning for signals

3. **Monitor Performance**
   - Dashboard updates every 5 seconds
   - Watch balance, equity, profit
   - Check open positions
   - Review trade history

4. **Stop Trading**
   - Click "Stop Bot" button
   - Bot safely closes connections
   - Positions remain open (manage manually if needed)

---

## Dashboard Sections

### 1. Status Cards (Top)

#### Bot Status Card
- Current status (Running/Stopped)
- Start/Stop buttons
- Visual indicator

#### Account Balance Card
- Current balance
- Current equity
- Total profit/loss (color-coded)

#### Performance Card
- Win rate percentage
- Total trades count
- Open positions count

### 2. Configuration Tab

**Trading Symbols**
- Select multiple symbols
- Hold Ctrl to select multiple
- Options: XAUUSD, GBPUSD, XAGUSD, EURUSD, USDJPY

**Timeframe**
- M1 (1 minute) - High frequency
- M5 (5 minutes) - Balanced
- M15 (15 minutes) - Medium frequency
- M30 (30 minutes) - Lower frequency
- H1 (1 hour) - Swing trading

**Risk Per Trade**
- Percentage of account to risk
- Range: 0.1% - 5%
- Recommended: 0.3% - 0.5%

**ATR Multiplier (Stop Loss)**
- Multiplier for ATR-based stops
- Range: 0.5 - 3.0
- Recommended: 0.8 for M1, 1.5 for H1

**Min Trade Confidence**
- Minimum confidence to take trade
- Range: 20% - 80%
- Recommended: 40% - 50%

**Max Daily Loss**
- Maximum daily loss percentage
- Range: 1% - 10%
- Recommended: 5%

**Scalping Max Hold**
- Maximum minutes to hold position
- Range: 10 - 60 minutes
- Recommended: 20 minutes for M1

**Enable Trading Hours**
- No (24/7): Trade all day
- Yes: Set specific hours (configure in code)

### 3. Trade History Tab

**Columns:**
- Time: When trade closed
- Symbol: Trading pair
- Type: BUY or SELL (color-coded)
- Volume: Lot size
- Price: Exit price
- Profit: $ profit/loss (color-coded)

**Features:**
- Sortable columns
- Color-coded wins (green) and losses (red)
- Shows last 7 days by default

### 4. Open Positions Tab

**Columns:**
- Ticket: Position ID
- Symbol: Trading pair
- Type: BUY or SELL
- Volume: Lot size
- Entry: Entry price
- Current: Current market price
- SL: Stop loss level
- TP: Take profit level
- Profit: Current $ profit/loss

**Features:**
- Real-time updates
- Color-coded profit/loss
- Shows all open positions

### 5. Analysis & Recommendations Tab

**AI-Powered Suggestions:**
- Priority 1: Critical issues (high impact)
- Priority 2: Important improvements
- Priority 3: Optional optimizations

**Each Recommendation Shows:**
- Title: What to fix
- Description: Why it matters
- Impact: Estimated $ savings
- Action: How to implement

**Example Recommendations:**
1. "Tighten Stop Losses" - Save $2,525
2. "Avoid 19:00 Hour" - Save $825
3. "Cut Losers Faster" - Save $547

---

## Configuration Examples

### Conservative (Low Risk)
```
Symbols: XAUUSD, GBPUSD
Timeframe: M15
Risk Per Trade: 0.2%
ATR Multiplier: 1.5
Min Confidence: 60%
Max Daily Loss: 3%
Scalp Max Hold: 30 min
Trading Hours: Yes (avoid news)
```

### Balanced (Recommended)
```
Symbols: XAUUSD, GBPUSD
Timeframe: M5
Risk Per Trade: 0.3%
ATR Multiplier: 1.0
Min Confidence: 45%
Max Daily Loss: 5%
Scalp Max Hold: 20 min
Trading Hours: No (24/7)
```

### Aggressive (High Frequency)
```
Symbols: XAUUSD, GBPUSD, XAGUSD
Timeframe: M1
Risk Per Trade: 0.5%
ATR Multiplier: 0.8
Min Confidence: 40%
Max Daily Loss: 7%
Scalp Max Hold: 15 min
Trading Hours: No (24/7)
```

---

## API Endpoints

The dashboard uses these REST API endpoints:

### GET /api/bot/status
Returns bot status and account info

### POST /api/bot/start
Starts the trading bot

### POST /api/bot/stop
Stops the trading bot

### GET /api/config
Gets current configuration

### POST /api/config
Updates configuration

### GET /api/trades/history?days=7
Gets trade history

### GET /api/trades/open
Gets open positions

### GET /api/analysis/performance
Gets performance metrics

### GET /api/analysis/recommendations
Gets AI recommendations

---

## Troubleshooting

### Dashboard Won't Start
```bash
# Check if Flask is installed
pip install Flask

# Check if port 5000 is available
netstat -ano | findstr :5000

# Try different port
# Edit web_dashboard.py, change port=5000 to port=8080
```

### Can't Connect to MT5
- Make sure MT5 terminal is running
- Check MT5 is logged in
- Verify bot has trading permissions

### Configuration Not Saving
- Check file permissions on src/config.py
- Make sure bot is stopped before changing config
- Restart bot after configuration changes

### No Trades Showing
- Check date range (default: last 7 days)
- Verify trades exist in MT5 history
- Check MT5 connection

---

## Advanced Features (Coming Soon)

### Phase 2
- [ ] Export trades to CSV/Excel
- [ ] Custom date range for history
- [ ] Real-time charts (balance, equity)
- [ ] Email/Telegram notifications
- [ ] Multi-account support

### Phase 3
- [ ] Backtesting interface
- [ ] Strategy comparison
- [ ] Risk calculator
- [ ] Position size calculator
- [ ] Trade journal with notes

### Phase 4
- [ ] Mobile app (iOS/Android)
- [ ] Cloud deployment
- [ ] Multi-user support
- [ ] Advanced analytics
- [ ] Machine learning predictions

---

## Security Notes

### Local Use Only
- Dashboard runs on localhost (127.0.0.1)
- Not accessible from internet by default
- No authentication required (local only)

### Production Deployment
If deploying to server:
1. Add authentication (username/password)
2. Use HTTPS (SSL certificate)
3. Restrict IP access
4. Use environment variables for secrets
5. Enable CORS protection

---

## Performance

### Resource Usage
- CPU: < 5% (idle), < 15% (active trading)
- RAM: ~100MB
- Network: Minimal (only MT5 API calls)

### Scalability
- Handles 100+ trades/day easily
- Real-time updates for up to 50 open positions
- History supports 1000+ trades

---

## Support

### Common Issues

**Q: Dashboard is slow**
A: Reduce update frequency (change 5000ms to 10000ms in HTML)

**Q: Bot stops unexpectedly**
A: Check trading_bot.log for errors

**Q: Recommendations not showing**
A: Need at least 10 trades for analysis

**Q: Can't change configuration**
A: Stop bot first, then change settings

---

## Status
✅ **DASHBOARD READY**  
✅ **REAL-TIME MONITORING**  
✅ **CONFIGURATION MANAGEMENT**  
✅ **AI RECOMMENDATIONS**  
🚀 **READY TO USE**

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements_web.txt

# 2. Start dashboard
python web_dashboard.py

# 3. Open browser
# Go to: http://localhost:5000

# 4. Configure bot
# Click "Configuration" tab
# Set your preferences
# Click "Save Configuration"

# 5. Start trading
# Click "Start Bot"
# Monitor in real-time!
```

Enjoy your new trading dashboard! 🎯
