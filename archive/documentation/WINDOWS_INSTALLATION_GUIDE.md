# 💎 GEM Trading Bot - Windows Installation Guide

**Version 2.1.0 | For Windows 10/11 | No Python Required**

---

## 📥 What You Downloaded

You have the **Windows Standalone Edition** - a complete package that includes:
- ✅ Trading bot executable (no Python needed!)
- ✅ Web dashboard interface
- ✅ All dependencies included
- ✅ Complete documentation
- ✅ Ready to run immediately

**File:** `GEM_Trading_Bot_v2.1.0_Windows.zip` (~150-200 MB)

---

## 🎯 System Requirements

### Minimum Requirements
- **Operating System:** Windows 10 (64-bit) or Windows 11
- **RAM:** 4 GB minimum (8 GB recommended)
- **Disk Space:** 500 MB free space
- **Internet:** Stable broadband connection
- **MetaTrader 5:** Must be installed and running
- **Browser:** Chrome, Firefox, or Edge (modern version)

### What You Need Before Starting
1. ✅ MetaTrader 5 installed from your broker
2. ✅ MT5 account (demo or live)
3. ✅ Administrator access to your computer
4. ✅ Antivirus configured (see Security section)

---

## 🚀 Installation Steps

### Step 1: Extract the Files

1. **Locate the downloaded ZIP file**
   - Usually in your `Downloads` folder
   - File name: `GEM_Trading_Bot_v2.1.0_Windows.zip`

2. **Extract the ZIP file**
   - Right-click the ZIP file
   - Select "Extract All..."
   - Choose destination (recommended: `C:\GEM_Trading_Bot`)
   - Click "Extract"

3. **Verify extraction**
   - Open the extracted folder
   - You should see:
     ```
     GEM_Trading_Bot_Windows/
     ├── GEM_Trading_Bot.exe  ← Main executable
     ├── START_HERE.txt       ← Quick start guide
     ├── USER_GUIDE.md        ← Complete manual
     ├── QUICK_START.md       ← 5-minute guide
     ├── TROUBLESHOOTING.md   ← Problem solving
     ├── README.md            ← Project overview
     ├── CHANGELOG.md         ← Version history
     └── docs/                ← Additional guides
         ├── INSTALLATION_GUIDE_FOR_USERS.md
         ├── DASHBOARD_CONFIGURATION_GUIDE.md
         ├── PROFITABLE_STRATEGY_GUIDE.md
         ├── WEB_DASHBOARD_GUIDE.md
         └── CONFIGURATION_QUICK_REFERENCE.md
     ```

### Step 2: Configure Windows Security

**Important:** Windows may block the executable on first run.

#### Windows Defender SmartScreen

If you see "Windows protected your PC":
1. Click "More info"
2. Click "Run anyway"
3. This is normal for new executables

#### Antivirus Software

If your antivirus blocks the file:
1. Add exception for `GEM_Trading_Bot.exe`
2. Add exception for the entire folder
3. This is a false positive (common with PyInstaller executables)

#### Windows Firewall

When prompted:
1. Check "Private networks"
2. Click "Allow access"
3. This allows the web dashboard to run

### Step 3: Install MetaTrader 5

**If you already have MT5 installed, skip to Step 4.**

1. **Download MT5**
   - Go to your broker's website
   - Find "Download MT5" or "Trading Platforms"
   - Download the installer
   - Common brokers: IC Markets, Pepperstone, XM, FXTM, etc.

2. **Install MT5**
   - Run the installer
   - Follow installation wizard
   - Accept default settings
   - Wait for installation to complete

3. **Login to MT5**
   - Open MetaTrader 5
   - Click "File" → "Login to Trade Account"
   - Enter your account credentials
   - Select your broker's server
   - Click "Login"

4. **Enable Algorithmic Trading**
   - In MT5, go to: **Tools** → **Options**
   - Click **Expert Advisors** tab
   - Check ✅ **"Allow algorithmic trading"**
   - Check ✅ **"Allow DLL imports"** (if available)
   - Click **OK**

5. **Verify MT5 is ready**
   - You should see your account balance
   - Market Watch should show symbols
   - Charts should be updating
   - **Keep MT5 running!**

### Step 4: Run GEM Trading Bot

1. **Navigate to the extracted folder**
   - Open File Explorer
   - Go to where you extracted the files
   - Example: `C:\GEM_Trading_Bot\GEM_Trading_Bot_Windows`

2. **Run the executable**
   - Double-click **`GEM_Trading_Bot.exe`**
   - Wait 20-30 seconds (first run takes longer)
   - A command window will open (don't close it!)
   - Your browser will open automatically

3. **Dashboard opens automatically**
   - Browser opens to: `http://localhost:5000`
   - You'll see the GEM Trading Dashboard
   - If browser doesn't open, manually go to: `http://localhost:5000`

4. **Verify dashboard is running**
   - You should see:
     - Bot Status card (showing "Stopped")
     - Account Balance card
     - Performance card
     - Navigation tabs at top

**✅ Success!** The bot is now running and ready to configure.

---

## ⚙️ Initial Configuration

### First-Time Setup (Recommended Settings)

1. **Click the "Configuration" tab**

2. **Select Trading Symbols**
   - Hold `Ctrl` and click to select multiple
   - **Recommended for beginners:**
     - ✅ XAUUSD (Gold)
     - ✅ GBPUSD (British Pound)
   - **Available symbols:**
     - XAUUSD (Gold) - Most popular
     - XAGUSD (Silver)
     - GBPUSD (British Pound)
     - EURUSD (Euro)
     - USDJPY (Japanese Yen)

3. **Choose Timeframe**
   - Select: **M5 (5 minutes)** ← Recommended for beginners
   - Other options:
     - M1 = Very fast (100+ trades/day) - Advanced users only
     - M15 = Medium (10-20 trades/day)
     - M30 = Slower (5-10 trades/day)
     - H1 = Very slow (2-5 trades/day) - Most profitable

4. **Enable Auto-Calculate (Recommended)**
   - Check the **"Auto"** checkbox next to:
     - ✅ Risk Per Trade %
     - ✅ ATR Multiplier (Stop Loss)
     - ✅ Min Trade Confidence %
     - ✅ Scalping Max Hold (minutes)
   - This automatically sets optimal values for your timeframe

5. **Set Maximum Daily Loss**
   - Enter: **5%** ← Recommended
   - This protects your account from bad days
   - Bot stops trading when limit is reached

6. **Enable Adaptive Risk**
   - Select: **"Yes (Recommended)"**
   - Automatically adjusts position size based on market conditions

7. **Trading Hours**
   - Select: **"No (24/7)"** ← Trade all day
   - Change to "Yes" later if you want to restrict hours

8. **Save Configuration**
   - Scroll to bottom
   - Click **"Save Configuration"** button
   - Wait for confirmation message

### Verify Configuration Saved

- You should see: "Configuration saved successfully!"
- Settings are now active
- Ready to start trading!

---

## 🎮 Starting the Bot

### Start Trading

1. **Make sure MT5 is running and logged in**

2. **Click "Start Bot" button**
   - Located in the Bot Status card (top left)
   - Button turns green
   - Status changes to "Running"

3. **Monitor the dashboard**
   - Account Balance updates every 5 seconds
   - Performance stats update in real-time
   - Open positions appear when trades are placed

### What to Expect

**First 5 minutes:**
- Bot connects to MT5
- Analyzes market conditions
- Calculates indicators
- Waits for trading signals

**First hour:**
- May execute 0-5 trades (depends on timeframe and market)
- M5 timeframe: Expect 1-3 trades per hour
- H1 timeframe: May take 1-2 hours for first trade

**First day:**
- M5: 30-50 trades
- M15: 10-20 trades
- H1: 2-5 trades
- Win rate: 50-65% (normal)

### Monitoring

**Dashboard Updates:**
- Account balance: Every 5 seconds
- Open positions: Every 2 seconds (when tab is active)
- Trade history: Real-time
- Charts: Updated with each trade

**What to Watch:**
- Today's Profit (should be positive overall)
- Win Rate (aim for 50%+)
- Open Positions (monitor floating P&L)
- Bot Status (should stay "Running")

---

## 📊 Using the Dashboard

### Main Tabs

#### 1. Dashboard (Home)
- **Bot Status:** Start/stop bot
- **Account Balance:** Balance, equity, profit
- **Performance:** Win rate, trades, positions

#### 2. Configuration
- Adjust all bot settings
- Enable/disable features
- Save changes

#### 3. Charts & Analytics
- **Profit by Symbol:** Which symbols are profitable
- **Win/Loss by Symbol:** Win rates per symbol
- **Daily Profit Trend:** Performance over time
- **Hourly Performance:** Best trading hours
- **Trade Distribution:** Symbol allocation

#### 4. Trade History
- View all closed trades (last 7 days)
- Sort by date, profit, amount
- Filter by wins/losses, symbol, date
- Analyze performance

#### 5. Open Positions
- Monitor active trades
- Real-time profit/loss
- Entry and current prices
- Stop loss and take profit levels

#### 6. AI Recommendations
- Smart suggestions to improve performance
- Priority-based (1 = critical, 2 = important, 3 = optional)
- Estimated impact in dollars
- Implementation instructions

### Key Features

**Auto-Refresh:**
- Dashboard updates automatically
- No need to refresh browser
- Real-time data

**Mobile Friendly:**
- Access from phone/tablet
- Same network: `http://YOUR_IP:5000`
- Full functionality on mobile

**Color Coding:**
- 🟢 Green = Profit, Running, Buy
- 🔴 Red = Loss, Stopped, Sell
- 🔵 Blue = Neutral, Info

---

## 🛡️ Safety & Best Practices

### Before Live Trading

**✅ Test on Demo Account First**
1. Run bot on demo for at least 1 week
2. Verify all features work correctly
3. Understand how bot behaves
4. Check win rate and profitability
5. Only then switch to live account

**✅ Start with Low Risk**
- Use 0.3% risk per trade (or lower)
- Set max daily loss to 5%
- Trade only 1-2 symbols initially
- Monitor closely for first week

**✅ Keep MT5 Running**
- Bot needs MT5 to be open
- Don't close MT5 while bot is running
- Don't log out of MT5
- Keep computer on (or use VPS)

**✅ Stable Internet**
- Bot needs constant internet connection
- Use wired connection if possible
- Avoid WiFi if unstable
- Consider VPS for 24/7 trading

### Risk Management

**Daily Loss Limit:**
- Set to 5% (recommended)
- Bot stops trading when reached
- Protects account from bad days
- Resets at midnight

**Position Sizing:**
- Bot calculates automatically
- Based on account balance and risk %
- Adjusts for market volatility
- Respects broker's min/max lots

**Stop Losses:**
- Always enabled
- Based on ATR (volatility)
- Automatically adjusted
- Never trade without stops

### Monitoring Schedule

**Daily:**
- Check Today's Profit
- Review open positions
- Verify bot is running
- Check for errors

**Weekly:**
- Review Charts & Analytics
- Analyze trade history
- Implement AI recommendations
- Adjust settings if needed

**Monthly:**
- Calculate monthly profit
- Review overall performance
- Optimize configuration
- Update strategy if needed

---

## 🔧 Troubleshooting

### Dashboard Won't Open

**Problem:** Browser doesn't open or shows error

**Solutions:**
1. **Wait longer** - First run takes 30-60 seconds
2. **Manual access** - Open browser and go to `http://localhost:5000`
3. **Try alternative** - Use `http://127.0.0.1:5000`
4. **Check firewall** - Allow access when prompted
5. **Restart bot** - Close and run `GEM_Trading_Bot.exe` again

### Bot Won't Start

**Problem:** Click "Start Bot" but nothing happens

**Solutions:**
1. **Check MT5** - Make sure MT5 is running and logged in
2. **Enable algo trading** - Tools → Options → Expert Advisors → Check "Allow algorithmic trading"
3. **Check configuration** - Verify settings are saved
4. **Restart everything** - Close bot, close MT5, restart both
5. **Check logs** - Look for error messages in command window

### No Trades Executing

**Problem:** Bot is running but not placing trades

**Solutions:**
1. **Lower confidence** - Set Min Trade Confidence to 40%
2. **Check symbols** - Verify symbols are selected and available in MT5
3. **Wait longer** - May take 30-60 minutes for first trade (especially H1)
4. **Check balance** - Verify sufficient account balance
5. **Check market** - May be no trading opportunities right now

### MT5 Connection Failed

**Problem:** Bot can't connect to MT5

**Solutions:**
1. **Start MT5 first** - Always run MT5 before the bot
2. **Login to MT5** - Make sure you're logged in to an account
3. **Check algo trading** - Must be enabled in MT5 settings
4. **Restart MT5** - Close and reopen MT5
5. **Check MT5 version** - Update to latest version

### Dashboard is Slow

**Problem:** Dashboard takes long to load or update

**Solutions:**
1. **Close other programs** - Free up RAM
2. **Close browser tabs** - Reduce browser memory usage
3. **Check internet** - Verify stable connection
4. **Restart bot** - Close and reopen
5. **Use Chrome** - Best performance with Chrome browser

### Antivirus Blocking

**Problem:** Antivirus deletes or blocks the executable

**Solutions:**
1. **Add exception** - Add `GEM_Trading_Bot.exe` to antivirus exceptions
2. **Whitelist folder** - Add entire folder to whitelist
3. **Temporarily disable** - Disable antivirus, run bot, re-enable
4. **Use different antivirus** - Some are more aggressive than others
5. **Download again** - Re-download if file was deleted

### High CPU Usage

**Problem:** Bot uses too much CPU

**Solutions:**
1. **Normal on M1** - M1 timeframe is CPU-intensive
2. **Use higher timeframe** - Switch to M5 or M15
3. **Reduce symbols** - Trade fewer symbols
4. **Close other programs** - Free up CPU
5. **Upgrade hardware** - Consider better computer or VPS

---

## 📱 Remote Access

### Access from Other Devices

**Same Network (WiFi):**
1. Find your computer's IP address:
   - Open Command Prompt
   - Type: `ipconfig`
   - Look for "IPv4 Address" (e.g., 192.168.1.100)

2. On other device (phone/tablet/laptop):
   - Connect to same WiFi
   - Open browser
   - Go to: `http://YOUR_IP:5000`
   - Example: `http://192.168.1.100:5000`

3. Full dashboard access from any device!

**From Internet (Advanced):**
- Requires port forwarding on router
- Security risk - not recommended
- Consider VPS instead
- See `docs/REMOTE_ACCESS_GUIDE.md` for details

---

## 🔄 Updates & Maintenance

### Checking for Updates

1. Visit GitHub releases page (if available)
2. Check for new version
3. Download new ZIP file
4. Extract to new folder
5. Copy your configuration (if needed)

### Backup Configuration

**Your settings are saved in:**
- `src/config.py` (if using Python version)
- Dashboard saves to bot's memory (executable version)

**To backup:**
1. Take screenshot of Configuration tab
2. Note all your settings
3. Save to document for reference

### Updating the Bot

1. **Stop the bot** - Click "Stop Bot"
2. **Close the executable** - Close command window
3. **Download new version** - Get latest ZIP
4. **Extract to new folder** - Don't overwrite old version
5. **Reconfigure** - Apply your settings again
6. **Test** - Verify everything works
7. **Delete old version** - Once confirmed working

---

## 💡 Tips for Success

### Week 1: Learning Phase
- ✅ Use demo account
- ✅ Use recommended settings
- ✅ Monitor daily
- ✅ Don't change settings yet
- ✅ Learn dashboard features
- ✅ Read USER_GUIDE.md

### Week 2-4: Optimization Phase
- ✅ Review Charts & Analytics
- ✅ Check Hourly Performance
- ✅ Implement AI Recommendations
- ✅ Adjust settings based on data
- ✅ Test different timeframes
- ✅ Still on demo!

### Month 2+: Live Trading Phase
- ✅ Switch to live account
- ✅ Start with low risk (0.3%)
- ✅ Monitor closely
- ✅ Scale up gradually
- ✅ Track monthly performance
- ✅ Optimize continuously

### Best Practices

**✅ DO:**
- Start with demo account
- Use low risk (0.3-0.5%)
- Monitor regularly
- Keep MT5 running
- Set max daily loss
- Review charts weekly
- Implement AI recommendations
- Read all documentation

**❌ DON'T:**
- Start with live account immediately
- Risk more than 2% per trade
- Change settings constantly
- Close MT5 while bot runs
- Ignore AI recommendations
- Trade without monitoring
- Disable safety limits
- Skip documentation

---

## 📚 Documentation Guide

### Essential Reading (In Order)

1. **START_HERE.txt** (5 minutes)
   - Quick overview
   - Basic instructions
   - First steps

2. **QUICK_START.md** (10 minutes)
   - Fast setup guide
   - Basic configuration
   - Start trading quickly

3. **USER_GUIDE.md** (30 minutes)
   - Complete manual
   - All features explained
   - Detailed instructions

4. **TROUBLESHOOTING.md** (As needed)
   - Common problems
   - Solutions
   - Error messages

### Additional Guides

**In docs/ folder:**

- **INSTALLATION_GUIDE_FOR_USERS.md**
  - Detailed installation steps
  - System requirements
  - Verification checklist

- **DASHBOARD_CONFIGURATION_GUIDE.md**
  - All settings explained
  - Configuration presets
  - Advanced options

- **PROFITABLE_STRATEGY_GUIDE.md**
  - Trading strategy details
  - How bot makes decisions
  - Indicator explanations

- **WEB_DASHBOARD_GUIDE.md**
  - Dashboard features
  - Charts and analytics
  - Trade management

- **CONFIGURATION_QUICK_REFERENCE.md**
  - Quick settings guide
  - Recommended values
  - Preset configurations

---

## 🆘 Getting Help

### Self-Help Resources

1. **Read documentation** - Most answers are in the guides
2. **Check TROUBLESHOOTING.md** - Common issues covered
3. **Review USER_GUIDE.md** - Detailed explanations
4. **Check command window** - Look for error messages
5. **Verify MT5 connection** - Most issues are MT5-related

### Support Channels

- **GitHub Issues:** Report bugs and request features
- **Documentation:** Complete guides included
- **Community:** Discord/Forum (if available)
- **Email:** support@gemtrading.com (if available)

### Before Asking for Help

**Provide this information:**
1. Windows version (10 or 11)
2. Bot version (check CHANGELOG.md)
3. MT5 version
4. Error message (exact text)
5. What you were doing when error occurred
6. Screenshots (if applicable)

---

## ⚠️ Important Disclaimers

### Trading Risk Warning

**IMPORTANT:** Trading foreign exchange and contracts for difference (CFDs) on margin carries a high level of risk and may not be suitable for all investors. The high degree of leverage can work against you as well as for you. Before deciding to trade, you should carefully consider your investment objectives, level of experience, and risk appetite.

**The possibility exists that you could sustain a loss of some or all of your initial investment. Therefore, you should not invest money that you cannot afford to lose.**

### Software Disclaimer

This software is provided "as is" without warranty of any kind, either expressed or implied. The authors and distributors of this software:

- ❌ Do NOT guarantee profits
- ❌ Do NOT guarantee performance
- ❌ Are NOT responsible for losses
- ❌ Are NOT financial advisors
- ❌ Do NOT provide investment advice

**Use at your own risk.**

### Recommendations

- ✅ Test on demo account first (minimum 1 week)
- ✅ Start with low risk (0.3% or less)
- ✅ Never risk more than you can afford to lose
- ✅ Monitor the bot regularly
- ✅ Understand the risks involved
- ✅ Seek professional financial advice if needed

---

## 🎊 You're Ready to Start!

### Final Checklist

Before starting live trading:

- [ ] Windows 10/11 installed
- [ ] Bot extracted and running
- [ ] MT5 installed and logged in
- [ ] Algo trading enabled in MT5
- [ ] Dashboard accessible at http://localhost:5000
- [ ] Configuration saved
- [ ] Tested on demo account (1+ week)
- [ ] Read USER_GUIDE.md
- [ ] Understand the risks
- [ ] Ready to monitor regularly

### Quick Start Summary

1. ✅ Extract ZIP file
2. ✅ Run `GEM_Trading_Bot.exe`
3. ✅ Configure settings (use Auto)
4. ✅ Click "Start Bot"
5. ✅ Monitor dashboard
6. ✅ Review performance
7. ✅ Optimize based on data

---

## 🌟 Welcome to Automated Trading!

You now have everything you need to start automated trading with GEM Trading Bot!

**Remember:**
- Start with demo
- Use low risk
- Monitor regularly
- Learn from data
- Optimize gradually
- Trade responsibly

**Happy Trading! 💎🚀**

---

## 📞 Support Information

**Version:** 2.1.0  
**Build Date:** January 28, 2026  
**Platform:** Windows 10/11 (64-bit)  
**Documentation:** Complete guides included  

**For help:**
- Read USER_GUIDE.md
- Check TROUBLESHOOTING.md
- Review docs/ folder
- Contact support (if available)

---

**© 2026 GEM Trading Bot | All Rights Reserved**
