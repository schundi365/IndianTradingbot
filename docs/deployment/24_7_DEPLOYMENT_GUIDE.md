# 24/7 Bot Deployment Guide - No Downtime

## Problem
Your laptop may shut down, causing the bot to stop trading and miss opportunities.

---

## Solutions (Best to Worst)

### ⭐ Option 1: VPS (Virtual Private Server) - RECOMMENDED
**Best for**: 24/7 automated trading with zero downtime

#### What is VPS?
- Remote Windows computer that runs 24/7 in a data center
- You connect to it remotely (like Remote Desktop)
- Runs MT5 and your bot continuously
- Never shuts down (99.9% uptime)

#### Recommended VPS Providers

##### 1. Forex VPS (Specialized for Trading)
**Best for MT5 trading**

- **ForexVPS.net** - $20-30/month
  - Pre-installed MT5
  - Low latency to broker servers
  - 24/7 support
  - Website: https://www.forexvps.net

- **ChicagoVPS** - $15-25/month
  - Good for US traders
  - Fast execution
  - Website: https://www.chicagovps.net

- **Vultr** - $10-20/month
  - Flexible, good performance
  - Choose location near your broker
  - Website: https://www.vultr.com

##### 2. General VPS (Cheaper)
**Good for budget-conscious traders**

- **AWS EC2** - $10-15/month
  - Free tier for 1 year (limited)
  - Windows Server available
  - Website: https://aws.amazon.com/ec2

- **DigitalOcean** - $12-20/month
  - Simple setup
  - Good performance
  - Website: https://www.digitalocean.com

- **Contabo** - $7-15/month
  - Very cheap
  - Decent performance
  - Website: https://contabo.com

#### VPS Setup Steps

1. **Sign up for VPS**
   - Choose Windows Server (not Linux)
   - Minimum: 2GB RAM, 2 CPU cores
   - Recommended: 4GB RAM, 2-4 CPU cores

2. **Connect to VPS**
   - Use Remote Desktop Connection (Windows)
   - Or Microsoft Remote Desktop (Mac)
   - Enter VPS IP address and credentials

3. **Install on VPS**
   ```
   1. Download and install MetaTrader 5
   2. Login to your MT5 account
   3. Install Python 3.9+ on VPS
   4. Clone your bot repository
   5. Install requirements: pip install -r requirements.txt
   6. Run bot: python run_bot.py
   ```

4. **Keep Bot Running**
   - Bot runs 24/7 on VPS
   - You can disconnect from VPS (bot keeps running)
   - Reconnect anytime to check status

#### VPS Advantages
✅ 24/7 uptime (99.9%)  
✅ Fast execution (low latency to broker)  
✅ No electricity costs  
✅ No laptop wear and tear  
✅ Access from anywhere  
✅ Professional setup  

#### VPS Disadvantages
❌ Monthly cost ($10-30)  
❌ Requires setup  
❌ Need to manage remote server  

---

### Option 2: Dedicated PC/Old Laptop - FREE
**Best for**: Budget traders with spare hardware

#### Setup
1. **Use old laptop or cheap PC**
   - Any Windows PC/laptop
   - Doesn't need to be powerful
   - 4GB RAM minimum

2. **Prevent Sleep/Shutdown**
   ```
   Windows Settings:
   1. Settings → System → Power & Sleep
   2. Set "Screen" to "Never"
   3. Set "Sleep" to "Never"
   4. Plugged in: Never sleep
   ```

3. **Disable Windows Updates Auto-Restart**
   ```
   1. Settings → Update & Security
   2. Advanced options
   3. Uncheck "Restart this device as soon as possible"
   4. Set active hours: 24 hours
   ```

4. **Keep MT5 and Bot Running**
   - Start MT5 on boot
   - Start bot on boot (see auto-start section below)

#### Advantages
✅ Free (if you have spare hardware)  
✅ Full control  
✅ No monthly fees  

#### Disadvantages
❌ Electricity costs (~$5-10/month)  
❌ Hardware wear and tear  
❌ Risk of power outage  
❌ Risk of Windows updates  
❌ Slower than VPS  

---

### Option 3: Cloud Desktop (Windows 365, Azure)
**Best for**: Enterprise/professional traders

#### Providers
- **Windows 365** - $30-60/month
- **Azure Virtual Desktop** - $20-50/month
- **Amazon WorkSpaces** - $25-50/month

#### Advantages
✅ Professional grade  
✅ 99.9% uptime  
✅ Managed by Microsoft/Amazon  
✅ Automatic backups  

#### Disadvantages
❌ Expensive ($30-60/month)  
❌ Overkill for simple bot  

---

### Option 4: Keep Laptop Running - NOT RECOMMENDED
**Only if**: You have no other option

#### Setup
1. **Prevent sleep**
   - Settings → Power & Sleep → Never
   
2. **Keep plugged in**
   - Always connected to power
   
3. **Prevent overheating**
   - Use laptop cooling pad
   - Keep in well-ventilated area
   
4. **Disable lid close sleep**
   ```
   Control Panel → Power Options → Choose what closing the lid does
   Set to "Do nothing"
   ```

#### Advantages
✅ Free  
✅ No setup needed  

#### Disadvantages
❌ Laptop wear and tear  
❌ High electricity cost  
❌ Overheating risk  
❌ Risk of accidental shutdown  
❌ Can't use laptop for other tasks  

---

## Auto-Start Bot on Windows

### Method 1: Task Scheduler (Recommended)

1. **Create Batch File**
   Create `start_bot.bat` in your bot folder:
   ```batch
   @echo off
   cd /d "C:\Users\YourName\Labs\AgenticAI\Bots\tradegold"
   python run_bot.py
   pause
   ```

2. **Create Task**
   ```
   1. Open Task Scheduler (search in Windows)
   2. Create Basic Task
   3. Name: "MT5 Trading Bot"
   4. Trigger: "When I log on"
   5. Action: "Start a program"
   6. Program: C:\path\to\start_bot.bat
   7. Finish
   ```

3. **Test**
   - Restart computer
   - Bot should start automatically

### Method 2: Startup Folder

1. **Create Shortcut**
   - Right-click `start_bot.bat`
   - Create shortcut

2. **Move to Startup**
   ```
   1. Press Win+R
   2. Type: shell:startup
   3. Move shortcut to this folder
   ```

3. **Test**
   - Restart computer
   - Bot starts automatically

---

## Auto-Start MT5 on Windows

### Method 1: Startup Folder
```
1. Find MT5 shortcut (usually Desktop or Start Menu)
2. Copy shortcut
3. Press Win+R, type: shell:startup
4. Paste shortcut
5. Restart to test
```

### Method 2: Task Scheduler
```
1. Task Scheduler → Create Basic Task
2. Name: "MetaTrader 5"
3. Trigger: "When I log on"
4. Action: "Start a program"
5. Program: C:\Program Files\MetaTrader 5\terminal64.exe
6. Finish
```

---

## Monitoring & Alerts

### Option 1: Telegram Notifications
Enable in config:
```python
ENABLE_TELEGRAM = True
TELEGRAM_TOKEN = 'your_bot_token'
TELEGRAM_CHAT_ID = 'your_chat_id'
```

Get notifications for:
- Bot started/stopped
- Trades opened/closed
- Errors and issues

### Option 2: Email Alerts
```python
ENABLE_EMAIL = True
EMAIL_ADDRESS = 'your_email@gmail.com'
EMAIL_PASSWORD = 'your_app_password'
```

### Option 3: Remote Desktop
- Connect to VPS/PC from phone/tablet
- Check bot status anytime
- Use Microsoft Remote Desktop app

---

## Recommended Setup (Best Practice)

### For Serious Trading
```
1. Get Forex VPS ($20-30/month)
2. Install MT5 and bot on VPS
3. Enable Telegram notifications
4. Set up auto-start for MT5 and bot
5. Monitor remotely via phone
```

### For Budget Trading
```
1. Use old laptop/cheap PC
2. Disable sleep and auto-restart
3. Set up auto-start
4. Keep plugged in 24/7
5. Check daily via Remote Desktop
```

### For Testing
```
1. Use your current laptop
2. Keep it running during trading hours
3. Manually start/stop bot
4. Upgrade to VPS when ready for 24/7
```

---

## Cost Comparison

| Solution | Setup Cost | Monthly Cost | Uptime | Effort |
|----------|-----------|--------------|--------|--------|
| Forex VPS | $0 | $20-30 | 99.9% | Low |
| General VPS | $0 | $10-20 | 99.5% | Medium |
| Old Laptop | $0-100 | $5-10 (electricity) | 95% | Medium |
| Keep Laptop Running | $0 | $10-15 (electricity) | 90% | High |
| Cloud Desktop | $0 | $30-60 | 99.9% | Low |

---

## My Recommendation

### If Budget Allows ($20-30/month)
**Get a Forex VPS** - It's worth it for:
- Zero downtime
- Fast execution
- Professional setup
- Peace of mind
- No laptop wear

### If Budget Tight
**Use old laptop or cheap PC** ($50-100 one-time):
- Buy used laptop on eBay/Craigslist
- Set up auto-start
- Keep running 24/7
- Upgrade to VPS later

### For Testing Only
**Keep current laptop running**:
- Test bot for 1-2 weeks
- See if it's profitable
- Then invest in VPS

---

## Quick Start: VPS Setup

### Step-by-Step (30 minutes)

1. **Sign up for VPS** (5 min)
   - Go to ForexVPS.net or Vultr
   - Choose Windows Server plan
   - Complete payment

2. **Connect to VPS** (2 min)
   - Open Remote Desktop Connection
   - Enter VPS IP and password
   - Connect

3. **Install MT5** (5 min)
   - Download MT5 from broker website
   - Install and login

4. **Install Python** (5 min)
   - Download Python 3.9+ from python.org
   - Install with "Add to PATH" checked

5. **Setup Bot** (10 min)
   ```
   1. Download bot from GitHub
   2. Extract to C:\TradingBot
   3. Open Command Prompt
   4. cd C:\TradingBot
   5. pip install -r requirements.txt
   6. python run_bot.py
   ```

6. **Setup Auto-Start** (3 min)
   - Create start_bot.bat
   - Add to Task Scheduler
   - Test restart

**Done!** Bot runs 24/7 with zero downtime.

---

## Troubleshooting

### Bot Stops After Disconnect
**Problem**: Bot stops when you close Remote Desktop  
**Solution**: Use Task Scheduler, not manual start

### MT5 Asks for Login After Restart
**Problem**: MT5 doesn't save credentials  
**Solution**: Check "Save password" in MT5 login

### Windows Updates Restart VPS
**Problem**: Automatic updates restart server  
**Solution**: Disable auto-restart in Windows Update settings

### High Latency to Broker
**Problem**: Slow execution from VPS  
**Solution**: Choose VPS location near broker server

---

## Next Steps

1. **Decide on solution** (VPS vs dedicated PC)
2. **Set up chosen solution** (follow guide above)
3. **Test auto-start** (restart and verify bot runs)
4. **Enable notifications** (Telegram or email)
5. **Monitor for 24 hours** (ensure stability)
6. **Go live with confidence** (24/7 trading!)

---

## Support

### VPS Setup Help
- ForexVPS.net has 24/7 support
- Most VPS providers have setup guides
- YouTube has many VPS setup tutorials

### Bot Setup Help
- Check bot logs: `trading_bot.log`
- Test connection: `python test_connection.py`
- Verify symbols: `python verify_symbols.py`

---

## Status
📋 **GUIDE COMPLETE**  
💡 **RECOMMENDATION: Forex VPS ($20-30/month)**  
🎯 **GOAL: 24/7 uptime, zero missed trades**

Choose your solution and follow the setup guide above!
