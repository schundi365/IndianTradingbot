# 💎 GEM Trading Bot - Installation Guide

## Welcome!

Thank you for choosing GEM Trading Bot. This guide will help you get started in minutes.

---

## 🎯 What You Need

### Required
- ✅ Windows 10 or 11
- ✅ MetaTrader 5 (MT5) installed
- ✅ MT5 account with your broker
- ✅ Internet connection
- ✅ 2 GB free disk space

### Optional
- Modern web browser (Chrome, Firefox, Edge)
- Second monitor (for dashboard)

---

## 🚀 Quick Start (3 Steps)

### Step 1: Install MetaTrader 5

**If you don't have MT5:**
1. Download MT5 from your broker's website
2. Install MT5
3. Login with your account credentials
4. Enable Algo Trading:
   - Go to: Tools → Options → Expert Advisors
   - Check "Allow algorithmic trading"
   - Click OK

**Keep MT5 running while the bot trades!**

### Step 2: Install GEM Trading Bot

**Choose your installation method:**

#### Option A: Standalone Executable (Recommended - Easiest!)

1. **Download** `GEM_Trading_Bot.exe`
2. **Save** to a folder (e.g., `C:\GEM_Trading`)
3. **Double-click** `GEM_Trading_Bot.exe`
4. **Wait** for dashboard to open (may take 30 seconds first time)
5. **Done!** Dashboard opens in your browser

**No Python needed! No dependencies! Just run!**

#### Option B: Python Installation (Advanced Users)

1. **Download Python 3.12**
   - Go to: python.org
   - Download Python 3.12
   - During installation: Check "Add Python to PATH"
   - Install

2. **Download Bot Files**
   - Download and extract bot files
   - Open folder in File Explorer

3. **Install Dependencies**
   - Right-click in folder → "Open in Terminal"
   - Run: `pip install -r requirements.txt`
   - Run: `pip install -r requirements_web.txt`
   - Wait for installation to complete

4. **Start Bot**
   - Run: `python web_dashboard.py`
   - Dashboard opens in browser

### Step 3: Configure & Start Trading

1. **Dashboard opens automatically** at http://localhost:5000

2. **Click "Configuration" tab**

3. **Select Trading Symbols**
   - Hold Ctrl and click to select multiple
   - Recommended: XAUUSD (Gold), GBPUSD

4. **Choose Timeframe**
   - Recommended: M5 (5 minutes)
   - M1 = Very fast (100+ trades/day)
   - M5 = Balanced (30-50 trades/day)
   - M15 = Slower (10-20 trades/day)

5. **Enable Auto-Calculate**
   - Check "Auto" next to:
     - Risk Per Trade
     - ATR Multiplier
     - Min Trade Confidence
     - Scalping Max Hold
   - This uses optimal values for your timeframe

6. **Set Max Daily Loss**
   - Recommended: 5%
   - Bot stops trading if daily loss reaches this limit

7. **Enable Adaptive Risk**
   - Select: "Yes (Recommended)"
   - Automatically adjusts position size

8. **Click "Save Configuration"**

9. **Click "Start Bot"**

10. **Monitor Dashboard!**
    - Watch trades in real-time
    - Check performance stats
    - View charts and analytics

---

## 📱 Access from Other Devices

### Same Network Access

**From Phone/Tablet/Laptop:**
1. Connect device to same WiFi
2. Open browser
3. Go to: http://192.168.5.39:5000
   (Replace with your computer's IP - shown when dashboard starts)
4. Full dashboard on any device!

**Find Your IP:**
- Dashboard shows it when starting
- Or run: `ipconfig` in command prompt
- Look for "IPv4 Address"

---

## 🎓 First Time Setup Wizard

### Recommended Settings for Beginners

```
Trading Symbols: XAUUSD, GBPUSD
Timeframe: M5 (5 minutes)
Risk Per Trade: 0.3% (Auto)
ATR Multiplier: 1.0 (Auto)
Min Confidence: 45% (Auto)
Max Daily Loss: 5%
Scalping Max Hold: 30 min (Auto)
Adaptive Risk: Yes
Trading Hours: No (24/7)
```

**Why these settings?**
- M5 timeframe: Balanced speed and quality
- 0.3% risk: Safe for account growth
- Auto-calculate: Optimal values
- 5% daily loss: Protects your account
- Adaptive risk: Better risk management

---

## 📊 Understanding the Dashboard

### Top Cards

**Bot Status**
- Shows if bot is running or stopped
- Click "Start Bot" to begin trading
- Click "Stop Bot" to pause

**Account Balance**
- Balance: Your account balance
- Equity: Balance + open positions
- Today: Profit from today's closed trades
- MTD: Profit this month
- YTD: Profit this year

**Performance**
- Win Rate: % of winning trades
- Total Trades: All trades executed
- Today's Wins: Winning trades today
- Today's Losses: Losing trades today
- Open Positions: Currently active trades

### Tabs

**Configuration**
- Adjust all bot settings
- Enable/disable features
- Save changes

**Charts & Analytics**
- 5 interactive charts
- Profit by symbol
- Win/loss ratios
- Daily trends
- Hourly performance

**Trade History**
- View all closed trades
- Sort and filter
- Analyze performance

**Open Positions**
- Monitor active trades
- Real-time profit/loss
- Entry and current prices

**AI Recommendations**
- Smart suggestions
- Estimated impact
- Implementation actions

---

## ✅ Verification Checklist

Before starting, verify:

- [ ] MT5 is installed and running
- [ ] MT5 is logged in to your account
- [ ] Algo trading is enabled in MT5
- [ ] Dashboard is running (http://localhost:5000)
- [ ] Configuration is saved
- [ ] Bot status shows "Running"
- [ ] Account balance is visible
- [ ] You understand the risk settings

---

## 🔧 Troubleshooting

### Dashboard won't open

**Solution 1: Check if running**
- Look for "Running on http://127.0.0.1:5000" message
- If not running, start the bot again

**Solution 2: Try different URL**
- http://localhost:5000
- http://127.0.0.1:5000

**Solution 3: Check firewall**
- Windows may block the first time
- Click "Allow access" if prompted

### Bot won't start

**Solution 1: Check MT5**
- Make sure MT5 is running
- Verify you're logged in
- Check algo trading is enabled

**Solution 2: Check configuration**
- Verify all settings are saved
- Try default settings first

**Solution 3: Restart everything**
- Close dashboard
- Close MT5
- Start MT5
- Start dashboard
- Try again

### No trades executing

**Solution 1: Check confidence level**
- May be set too high
- Try lowering to 40%

**Solution 2: Check symbols**
- Verify symbols are selected
- Make sure they're available in MT5

**Solution 3: Check account**
- Verify sufficient balance
- Check margin requirements

### Dashboard is slow

**Solution 1: Close other programs**
- Free up RAM
- Close unnecessary browser tabs

**Solution 2: Reduce update frequency**
- Dashboard updates every 5 seconds
- This is normal

**Solution 3: Check internet**
- Verify stable connection
- MT5 needs internet to work

---

## 📚 Learning Resources

### Included Documentation

- **USER_GUIDE.md** - Complete user manual
- **QUICK_START_CARD.md** - Quick reference
- **REMOTE_ACCESS_GUIDE.md** - Access from other devices
- **TROUBLESHOOTING.md** - Common issues

### Recommended Reading Order

1. This guide (INSTALLATION_GUIDE)
2. QUICK_START_CARD.md (quick reference)
3. USER_GUIDE.md (detailed manual)
4. Experiment with settings
5. Review charts and analytics

---

## 💡 Tips for Success

### Day 1-7: Learning Phase
- Start with recommended settings
- Monitor dashboard daily
- Don't change settings yet
- Learn how bot behaves
- Review trade history

### Week 2-4: Optimization Phase
- Review Charts & Analytics
- Check Hourly Performance
- Implement AI Recommendations
- Adjust settings based on data
- Test different timeframes

### Month 2+: Advanced Phase
- Fine-tune risk settings
- Optimize symbol selection
- Use custom configurations
- Track monthly performance
- Scale up gradually

### Best Practices

✅ **Do:**
- Start with small risk (0.3%)
- Monitor daily
- Review charts weekly
- Implement recommendations
- Keep MT5 running
- Maintain stable internet
- Set max daily loss limit

❌ **Don't:**
- Risk more than 2% per trade
- Change settings constantly
- Ignore AI recommendations
- Trade without monitoring
- Close MT5 while bot runs
- Disable safety limits

---

## 🆘 Getting Help

### Self-Help

1. Check TROUBLESHOOTING.md
2. Review USER_GUIDE.md
3. Check dashboard for errors
4. Verify MT5 connection

### Support Channels

- Email: support@gemtrading.com (if available)
- Discord: discord.gg/gemtrading (if available)
- GitHub Issues: github.com/yourrepo (if available)
- Documentation: Read all .md files

---

## 🔄 Updates

### Checking for Updates

**Standalone EXE:**
- Check website for new version
- Download and replace old file

**Python Version:**
- Run: `git pull` (if using Git)
- Or download new files

### Update Frequency

- Bug fixes: As needed
- New features: Monthly
- Major updates: Quarterly

---

## 📊 What to Expect

### First Day
- Bot learns your account
- May execute 5-20 trades (M5)
- Performance varies
- Monitor closely

### First Week
- Bot adapts to market
- Win rate stabilizes
- You learn the dashboard
- Adjust settings if needed

### First Month
- Clear performance pattern
- Consistent results
- Optimized settings
- Comfortable with bot

### Realistic Expectations

**Good:**
- 50-65% win rate
- Consistent small profits
- Automated trading
- Time savings

**Not Realistic:**
- 100% win rate
- Get rich quick
- No losses ever
- Zero monitoring needed

---

## 🎊 You're Ready!

### Quick Recap

1. ✅ Install MT5 and enable algo trading
2. ✅ Run GEM_Trading_Bot.exe
3. ✅ Configure settings (use Auto)
4. ✅ Click "Start Bot"
5. ✅ Monitor dashboard
6. ✅ Review performance
7. ✅ Optimize based on data

### Final Checklist

- [ ] MT5 installed and running
- [ ] Bot installed and running
- [ ] Dashboard accessible
- [ ] Configuration saved
- [ ] Bot started
- [ ] First trade executed
- [ ] Documentation read

---

## 🌟 Welcome to GEM Trading!

You're now ready to start automated trading with GEM Trading Bot!

**Remember:**
- Start small
- Monitor regularly
- Learn from data
- Optimize gradually
- Trade responsibly

**Happy Trading! 💎🚀**

---

**Version:** 1.0  
**Last Updated:** January 28, 2026  
**Support:** See USER_GUIDE.md for detailed help
