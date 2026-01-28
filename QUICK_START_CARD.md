# 💎 GEM Trading Dashboard - Quick Start Card

## 🚀 Access Dashboard

### On Your Computer
```
http://localhost:5000
http://gemtrading:5000
```

### From Other Devices (Same Network)
```
http://192.168.5.39:5000
```

---

## ⚡ Quick Setup (3 Steps)

### 1. Start Dashboard
```cmd
python web_dashboard.py
```

### 2. Configure Bot
- Click "Configuration" tab
- Select symbols: XAUUSD, GBPUSD
- Choose timeframe: M5 (recommended)
- Check "Auto" for all parameters
- Click "Save Configuration"

### 3. Start Trading
- Click "Start Bot" button
- Monitor in real-time!

---

## 📊 Dashboard Tabs

### Configuration
- Set trading symbols
- Choose timeframe
- Adjust risk settings
- Enable/disable features

### Charts & Analytics
- Profit by Symbol
- Win/Loss by Symbol
- Daily Profit Trend
- Hourly Performance
- Trade Distribution

### Trade History
- View all closed trades
- Sort by date/profit/amount
- Filter by wins/losses/today
- Filter by symbol

### Open Positions
- Monitor active trades
- Real-time profit/loss
- Entry/current prices
- Stop loss & take profit

### AI Recommendations
- Priority-based suggestions
- Estimated $ impact
- Implementation actions

---

## ⚙️ Configuration Options

### Trading Symbols
- XAUUSD (Gold) ⭐ Most popular
- GBPUSD (British Pound)
- XAGUSD (Silver)
- EURUSD (Euro)
- USDJPY (Japanese Yen)

### Timeframe
- **M1** (1 min) - 100-200+ trades/day
- **M5** (5 min) - 30-50 trades/day ⭐ Recommended
- **M15** (15 min) - 10-20 trades/day
- **M30** (30 min) - 5-10 trades/day
- **H1** (1 hour) - 2-5 trades/day

### Risk Per Trade
- **0.1-0.2%** - Conservative
- **0.3-0.5%** - Balanced ⭐ Recommended
- **0.5-1.0%** - Aggressive
- **1.0-2.0%** - Very Aggressive

### ATR Multiplier (Stop Loss)
- **0.5-1.0** - Tight stops
- **1.0-1.5** - Medium stops ⭐ Recommended
- **1.5-3.0** - Wide stops

### Min Trade Confidence
- **20-40%** - More trades, lower quality
- **40-60%** - Balanced ⭐ Recommended
- **60-80%** - Fewer trades, higher quality

### Max Daily Loss
- **1-3%** - Conservative
- **3-5%** - Balanced ⭐ Recommended
- **5-10%** - Aggressive

### Adaptive Risk
- **Yes** - Dynamic sizing ⭐ Recommended
- **No** - Fixed sizing

---

## 📈 Status Cards

### Bot Status
- ● Running / ● Stopped
- [Start Bot] / [Stop Bot]

### Account Balance
- Balance: Your account balance
- Equity: Balance + floating P&L
- Floating P&L: Open positions profit/loss
- **Today**: Profit from closed trades today
- **MTD**: Profit this month
- **YTD**: Profit this year

### Performance
- Win Rate: % of winning trades
- Total Trades: All trades executed
- **Today's Wins**: Winning trades today (green)
- **Today's Losses**: Losing trades today (red)
- Open Positions: Currently active trades

---

## 💡 Quick Tips

### For Beginners
✅ Use M5 timeframe  
✅ Risk 0.3% per trade  
✅ Enable adaptive risk  
✅ Check "Auto" for all parameters  
✅ Start with 1-2 symbols  

### Best Practices
✅ Monitor dashboard daily  
✅ Review charts weekly  
✅ Implement AI recommendations  
✅ Never risk more than 2% per trade  
✅ Set max daily loss limit  

### Common Tasks
- **Start trading**: Configure → Start Bot
- **Stop trading**: Stop Bot
- **Change settings**: Stop Bot → Configure → Save → Start Bot
- **View performance**: Charts & Analytics tab
- **Filter trades**: Trade History → Sort/Filter

---

## 🔧 Troubleshooting

### Dashboard won't load
```
1. Check if dashboard is running
2. Verify URL: http://localhost:5000
3. Restart: python web_dashboard.py
```

### Bot not placing trades
```
1. Check min confidence (may be too high)
2. Verify MT5 is running and logged in
3. Check trading hours settings
```

### Can't access from other device
```
1. Check firewall settings
2. Verify both devices on same network
3. Use IP: http://192.168.5.39:5000
```

---

## 📱 Access from Mobile

1. Connect phone to same WiFi
2. Open browser
3. Go to: http://192.168.5.39:5000
4. Full dashboard on mobile!

---

## 📚 Documentation

- **USER_GUIDE.md** - Complete user guide
- **REMOTE_ACCESS_GUIDE.md** - Access from other devices
- **DASHBOARD_ENHANCEMENTS_V2.md** - Technical details
- **WEB_DASHBOARD_GUIDE.md** - Full documentation

---

## 🎯 Recommended Setup

```
Symbols: XAUUSD, GBPUSD
Timeframe: M5
Risk: 0.3%
ATR: 1.0 (Auto)
Confidence: 45% (Auto)
Max Daily Loss: 5%
Scalp Hold: 30 min (Auto)
Adaptive Risk: Yes
Trading Hours: No (24/7)
```

---

## ⚡ One-Minute Setup

```
1. python web_dashboard.py
2. Open http://localhost:5000
3. Configuration tab
4. Check all "Auto" boxes
5. Save Configuration
6. Start Bot
7. Done!
```

---

**Dashboard:** 💎 GEM Trading  
**URL:** http://localhost:5000  
**Support:** See USER_GUIDE.md  
**Version:** 2.0

Happy trading! 💎🚀
