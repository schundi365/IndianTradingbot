# Indian Market Web Dashboard - Quick Reference Guide

## Quick Start (5 Minutes)

### 1. Start Dashboard
```bash
python indian_dashboard/indian_dashboard.py
```
Access at: `http://localhost:8080`

### 2. Connect Broker
- Go to **Broker** tab
- Select your broker
- Enter credentials
- Click **Test Connection**

### 3. Select Instruments
- Go to **Instruments** tab
- Search or filter instruments
- Check boxes to select
- Click **Continue**

### 4. Configure Strategy
- Go to **Configuration** tab
- Or load a preset
- Set risk parameters
- Click **Save**

### 5. Start Trading
- Go to **Monitor** tab
- Click **Start Bot**
- Monitor positions and P&L

---

## Tab Overview

| Tab | Purpose | Key Actions |
|-----|---------|-------------|
| **Broker** | Connect to broker | Select, authenticate, test connection |
| **Instruments** | Select what to trade | Search, filter, select instruments |
| **Configuration** | Set strategy & risk | Configure parameters, save/load |
| **Monitor** | Watch bot & positions | Start/stop bot, view positions |
| **Trades** | View history | Filter trades, export data |

---

## Broker Credentials Quick Reference

### Kite Connect
- API Key + API Secret
- Or use "Login with Kite" (OAuth)
- Get from: https://kite.trade/

### Alice Blue
- User ID + API Key
- Contact support for API access

### Angel One
- Client ID + Password + TOTP
- Use trading account credentials

### Upstox
- API Key + API Secret + Redirect URI
- Get from: https://api.upstox.com/

### Paper Trading
- No credentials needed
- Perfect for testing

---

## Configuration Presets

| Preset | Best For | Timeframe | Risk |
|--------|----------|-----------|------|
| **NIFTY Futures** | Index futures | 15min | 2% |
| **BANKNIFTY Futures** | Volatile index | 5min | 2.5% |
| **Equity Intraday** | Stock trading | 5min | 1.5% |
| **Options Trading** | Options strategies | 15min | 3% |

---

## Risk Management Guidelines

### Conservative
- Risk per trade: 1-1.5%
- Max positions: 2-3
- Max daily loss: 3%

### Moderate
- Risk per trade: 2-2.5%
- Max positions: 3-5
- Max daily loss: 5%

### Aggressive
- Risk per trade: 3-4%
- Max positions: 5-7
- Max daily loss: 7%

**Never exceed 5% risk per trade!**

---

## Common Filters

### NSE Stocks
- Exchange: NSE
- Type: EQ

### NIFTY Futures
- Exchange: NFO
- Type: FUT
- Search: "NIFTY"

### BANKNIFTY Options
- Exchange: NFO
- Type: CE or PE
- Search: "BANKNIFTY"

### BSE Stocks
- Exchange: BSE
- Type: EQ

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl + S` | Save configuration |
| `Ctrl + R` | Refresh current tab |
| `Ctrl + 1` | Go to Broker tab |
| `Ctrl + 2` | Go to Instruments tab |
| `Ctrl + 3` | Go to Configuration tab |
| `Ctrl + 4` | Go to Monitor tab |
| `Ctrl + 5` | Go to Trades tab |
| `Esc` | Close dialog |

---

## Status Indicators

### Bot Status
- 🟢 **Running**: Bot is active
- 🔴 **Stopped**: Bot is inactive
- 🟡 **Starting**: Bot is initializing

### Connection Status
- ✅ **Connected**: Broker connected
- ❌ **Disconnected**: No broker connection
- ⚠️ **Error**: Connection issue

### P&L Colors
- 🟢 **Green**: Profit
- 🔴 **Red**: Loss
- ⚪ **Gray**: Break-even

---

## Troubleshooting Quick Fixes

| Problem | Quick Fix |
|---------|-----------|
| Dashboard won't start | Check Python version, install dependencies |
| Can't connect to broker | Verify credentials, check broker status |
| Instruments not loading | Click "Refresh", check broker connection |
| Config won't save | Fix validation errors (red text) |
| Bot won't start | Ensure broker connected, config valid |
| Slow performance | Reduce auto-refresh, limit instruments |

---

## Important Limits

### Trading Hours
- Market Open: 09:15 IST
- Market Close: 15:30 IST
- Pre-market: 09:00-09:15 IST
- Post-market: 15:30-16:00 IST

### Position Limits (NSE)
- Varies by instrument
- Check exchange website for current limits

### API Rate Limits
- Kite: 10 req/sec, 200 req/min
- Alice Blue: 5 req/sec, 100 req/min
- Angel One: 10 req/sec, 250 req/min
- Upstox: 10 req/sec, 200 req/min

---

## Configuration Checklist

Before starting bot:
- [ ] Broker connected
- [ ] At least 1 instrument selected
- [ ] Strategy configured
- [ ] Risk parameters set
- [ ] Trading hours set
- [ ] Configuration saved
- [ ] Sufficient account balance
- [ ] Stop loss configured

---

## Export Options

### Trades Export
- **CSV**: For Excel/Sheets
- **Excel**: With formatting
- **JSON**: For backup

### Configuration Export
- **JSON**: Share or backup
- **Clipboard**: Quick copy

---

## File Locations

```
indian_dashboard/
├── configs/              # Saved configurations
├── data/
│   └── instruments_cache.json  # Cached instruments
├── logs/
│   ├── dashboard.log    # Dashboard logs
│   └── bot.log          # Bot logs
└── credentials/         # Encrypted credentials
```

---

## Support Resources

### Documentation
- User Guide: `USER_GUIDE.md`
- API Docs: `API_DOCUMENTATION.md`
- README: `README.md`

### Logs
- Dashboard: `logs/dashboard.log`
- Bot: `logs/bot.log`

### Help
- Check troubleshooting section
- Review error messages
- Check broker status pages
- GitHub Issues for bugs

---

## Safety Tips

1. **Start with Paper Trading**
   - Test your strategy first
   - No real money at risk

2. **Use Stop Losses**
   - Always set stop loss
   - Never trade without protection

3. **Limit Risk**
   - Never risk more than 2% per trade
   - Set max daily loss limit

4. **Monitor Regularly**
   - Check bot status frequently
   - Review positions daily
   - Analyze trade history

5. **Keep Credentials Safe**
   - Never share API keys
   - Use strong encryption key
   - Disconnect when not trading

6. **Stay Informed**
   - Check market news
   - Be aware of events
   - Know your instruments

---

## Quick Command Reference

### Start Dashboard
```bash
python indian_dashboard/indian_dashboard.py
```

### Start on Different Port
```bash
python indian_dashboard/indian_dashboard.py --port 8081
```

### Set Environment Variables (Windows)
```cmd
set FLASK_SECRET_KEY=your-secret-key
set ENCRYPTION_KEY=your-encryption-key
```

### Set Environment Variables (Linux/Mac)
```bash
export FLASK_SECRET_KEY=your-secret-key
export ENCRYPTION_KEY=your-encryption-key
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run Tests
```bash
pytest indian_dashboard/tests/
```

---

**Print this page for quick reference while trading!**

**Version**: 1.0.0  
**Last Updated**: 2024-02-18
