# 💎 GEM Trading Dashboard - Complete User Guide

## Welcome to GEM Trading!

This guide explains all features and options available in your trading dashboard.

---

## 📋 Table of Contents

1. [Getting Started](#getting-started)
2. [Dashboard Overview](#dashboard-overview)
3. [Configuration Options](#configuration-options)
4. [Charts & Analytics](#charts--analytics)
5. [Trade Management](#trade-management)
6. [AI Recommendations](#ai-recommendations)
7. [Best Practices](#best-practices)

---

## 🚀 Getting Started

### Accessing the Dashboard

**On your computer:**
- http://localhost:5000
- http://gemtrading:5000 (after hostname setup)

**From other devices (same network):**
- http://192.168.5.39:5000

### First Time Setup

1. **Start Dashboard**
   ```cmd
   python web_dashboard.py
   ```

2. **Open Browser**
   - Go to http://localhost:5000

3. **Configure Bot**
   - Click "Configuration" tab
   - Set your preferences
   - Click "Save Configuration"

4. **Start Trading**
   - Click "Start Bot" button
   - Monitor in real-time!

---

## 📊 Dashboard Overview

### Top Status Cards

#### 1. Bot Status Card
```
┌──────────────┐
│ Bot Status   │
│ ● Running    │  ← Green = Running, Red = Stopped
│ [Start Bot]  │  ← Click to start trading
│ [Stop Bot]   │  ← Click to stop trading
└──────────────┘
```

**What it shows:**
- Current bot status (Running/Stopped)
- Control buttons to start/stop bot

**How to use:**
- Click "Start Bot" to begin trading
- Click "Stop Bot" to pause trading
- Status updates automatically every 5 seconds

#### 2. Account Balance Card
```
┌──────────────┐
│ Account      │
│ Balance: $X  │  ← Your account balance
│ Equity: $X   │  ← Balance + floating P&L
│ Float P&L: $X│  ← Current open positions profit/loss
│ Today: $X    │  ← Profit from closed trades today
│ MTD: $X      │  ← Profit this month
│ YTD: $X      │  ← Profit this year
└──────────────┘
```

**What it shows:**
- **Balance**: Your account balance
- **Equity**: Balance + floating profit/loss
- **Floating P&L**: Current open positions profit/loss (green/red)
- **Today's Profit**: Closed trades profit today (green/red)
- **Month to Date**: Profit since start of month (green/red)
- **Year to Date**: Profit since start of year (green/red)

**Color coding:**
- Green = Profit
- Red = Loss

#### 3. Performance Card
```
┌──────────────┐
│ Performance  │
│ Win Rate: X% │  ← Percentage of winning trades
│ Total: X     │  ← Total trades executed
│ Today Wins:X │  ← Winning trades today (green)
│ Today Loss:X │  ← Losing trades today (red)
│ Open Pos: X  │  ← Currently open positions
└──────────────┘
```

**What it shows:**
- **Win Rate**: Percentage of profitable trades
- **Total Trades**: All trades executed
- **Today's Wins**: Number of winning trades today (green)
- **Today's Losses**: Number of losing trades today (red)
- **Open Positions**: Currently active trades

---

## ⚙️ Configuration Options

### How to Configure

1. Click "Configuration" tab
2. Adjust settings
3. Click "Save Configuration"
4. Restart bot if running

### Trading Symbols

**What it is:**
- Select which currency pairs/metals to trade

**Options:**
- XAUUSD (Gold)
- GBPUSD (British Pound)
- XAGUSD (Silver)
- EURUSD (Euro)
- USDJPY (Japanese Yen)

**How to choose:**
- Hold Ctrl and click to select multiple
- Recommended: Start with 1-2 symbols
- Gold (XAUUSD) is most popular

**Best practices:**
- Fewer symbols = more focused trading
- Test each symbol individually first
- Monitor performance per symbol

### Timeframe

**What it is:**
- How often the bot checks for trading signals

**Options:**
- **M1 (1 minute)** - Very fast, 100-200+ trades/day
- **M5 (5 minutes)** - Fast, 30-50 trades/day
- **M15 (15 minutes)** - Medium, 10-20 trades/day
- **M30 (30 minutes)** - Slower, 5-10 trades/day
- **H1 (1 hour)** - Slow, 2-5 trades/day

**How to choose:**
- M1: High-frequency scalping (requires monitoring)
- M5: Balanced day trading (recommended for beginners)
- M15+: Swing trading (less monitoring needed)

**Best practices:**
- Start with M5 or M15
- M1 requires constant monitoring
- Higher timeframes = fewer but larger trades

### Risk Per Trade (%)

**What it is:**
- Percentage of your account to risk per trade

**Options:**
- 0.1% - 5.0%
- Default: 0.3%

**Auto-Calculate:**
- ☑ Check "Auto" to use recommended value
- Auto adjusts based on timeframe
- M1: 0.3%, M5: 0.3%, M15: 0.4%, M30: 0.5%, H1: 0.5%

**How to choose:**
- Conservative: 0.1% - 0.2%
- Balanced: 0.3% - 0.5%
- Aggressive: 0.5% - 1.0%
- Very Aggressive: 1.0% - 2.0%

**Best practices:**
- Never risk more than 2% per trade
- Start with 0.3% and adjust
- Lower risk = slower growth but safer
- Higher risk = faster growth but riskier

**Example:**
- Account: $10,000
- Risk: 0.3%
- Risk per trade: $30
- If trade loses, you lose $30

### ATR Multiplier (Stop Loss)

**What it is:**
- How far away to place your stop loss
- Based on ATR (Average True Range - market volatility)

**Options:**
- 0.5 - 3.0
- Default: 0.8

**Auto-Calculate:**
- ☑ Check "Auto" to use recommended value
- M1: 0.8, M5: 1.0, M15: 1.2, M30: 1.5, H1: 1.8

**How to choose:**
- Tight stops (0.5-1.0): Less risk, more stop-outs
- Medium stops (1.0-1.5): Balanced
- Wide stops (1.5-3.0): More risk, fewer stop-outs

**Best practices:**
- Lower timeframes need tighter stops
- Higher timeframes need wider stops
- Use Auto for optimal values

**Example:**
- ATR = 10 pips
- Multiplier = 0.8
- Stop loss = 8 pips away

### Min Trade Confidence (%)

**What it is:**
- Minimum confidence level required to take a trade
- Bot calculates confidence based on indicators

**Options:**
- 20% - 80%
- Default: 40%

**Auto-Calculate:**
- ☑ Check "Auto" to use recommended value
- M1: 40%, M5: 45%, M15: 50%, M30: 55%, H1: 60%

**How to choose:**
- Low (20-40%): More trades, lower quality
- Medium (40-60%): Balanced
- High (60-80%): Fewer trades, higher quality

**Best practices:**
- Start with 40-50%
- Increase if too many losing trades
- Decrease if missing good opportunities

**Example:**
- Confidence: 40%
- Bot only trades when 40%+ confident
- Rejects trades below 40%

### Max Daily Loss (%)

**What it is:**
- Maximum loss allowed per day
- Bot stops trading when limit reached

**Options:**
- 1% - 10%
- Default: 5%

**How to choose:**
- Conservative: 1-3%
- Balanced: 3-5%
- Aggressive: 5-10%

**Best practices:**
- Protects your account from bad days
- Bot automatically stops at limit
- Resets at midnight

**Example:**
- Account: $10,000
- Max daily loss: 5%
- Bot stops after losing $500 in one day

### Scalping Max Hold (minutes)

**What it is:**
- Maximum time to hold a position
- For M1 scalping mode

**Options:**
- 10 - 60 minutes
- Default: 20 minutes

**Auto-Calculate:**
- ☑ Check "Auto" to use recommended value
- M1: 20, M5: 30, M15: 45, M30: 60, H1: 90

**How to choose:**
- Short (10-20): Quick scalping
- Medium (20-40): Balanced
- Long (40-60): Let trades develop

**Best practices:**
- Lower timeframes = shorter hold times
- Prevents holding losers too long
- Use Auto for optimal values

### Enable Adaptive Risk

**What it is:**
- Automatically adjusts position size based on market conditions

**Options:**
- **Yes (Recommended)**: Dynamic position sizing
- **No (Fixed Risk)**: Always use same risk %

**How it works:**
- Increases size in favorable conditions
- Decreases size in risky conditions
- Based on volatility, trend strength, recent performance

**When to use:**
- **Yes**: For most trading (recommended)
- **No**: For testing or consistent sizing

**Best practices:**
- Keep enabled for better risk management
- Disable only for backtesting

### Enable Trading Hours

**What it is:**
- Restrict trading to specific hours

**Options:**
- **No (24/7)**: Trade all day (default)
- **Yes**: Only trade during set hours

**How to choose:**
- 24/7: Maximum opportunities
- Restricted: Avoid specific hours (e.g., news times)

**Best practices:**
- Start with 24/7
- Restrict if certain hours are unprofitable
- Check Hourly Performance chart

---

## 📈 Charts & Analytics

### How to Access

1. Click "Charts & Analytics" tab
2. View 5 interactive charts
3. Hover over charts for details

### Chart 1: Profit by Symbol

**What it shows:**
- Total profit/loss per trading symbol
- Bar chart with green (profit) and red (loss) bars

**How to use:**
- Identify most profitable symbols
- Avoid unprofitable symbols
- Focus trading on winners

**Example:**
```
XAUUSD: $1,250 (green bar - profitable)
GBPUSD: $450 (green bar - profitable)
XAGUSD: -$200 (red bar - losing)
```

**Action:**
- Trade more XAUUSD and GBPUSD
- Avoid or reduce XAGUSD trading

### Chart 2: Win/Loss by Symbol

**What it shows:**
- Number of winning vs losing trades per symbol
- Stacked bar chart (green = wins, red = losses)

**How to use:**
- Compare win rates across symbols
- Identify consistent performers
- See which symbols have best win rate

**Example:**
```
XAUUSD: 15 wins, 5 losses (75% win rate)
GBPUSD: 10 wins, 8 losses (56% win rate)
```

**Action:**
- XAUUSD has better win rate
- Focus more on XAUUSD

### Chart 3: Daily Profit Trend

**What it shows:**
- Profit/loss for each day (last 7 days)
- Line chart showing trend

**How to use:**
- Identify profitable days
- Spot patterns (e.g., Mondays are bad)
- Track overall trend

**Example:**
```
Mon: $150
Tue: $200
Wed: -$50 (bad day)
Thu: $300
Fri: $250
```

**Action:**
- Investigate why Wednesday was bad
- Replicate what worked on Thursday

### Chart 4: Hourly Performance

**What it shows:**
- Profit/loss by hour of day
- Bar chart (green/red bars)

**How to use:**
- Find best trading hours
- Avoid unprofitable hours
- Optimize trading schedule

**Example:**
```
Best hours:
- 8:00 AM: $200
- 2:00 PM: $180
- 8:00 PM: $150

Worst hours:
- 7:00 PM: -$100 (avoid!)
- 11:00 PM: -$50
```

**Action:**
- Enable trading hours restriction
- Avoid 7:00 PM - 8:00 PM
- Focus on 8:00 AM, 2:00 PM, 8:00 PM

### Chart 5: Trade Distribution

**What it shows:**
- Percentage of trades per symbol
- Doughnut chart (colorful pie)

**How to use:**
- See trading focus
- Check diversification
- Balance symbol allocation

**Example:**
```
XAUUSD: 45% (68 trades)
GBPUSD: 35% (53 trades)
XAGUSD: 20% (30 trades)
```

**Action:**
- Good diversification
- Not over-concentrated in one symbol

---

## 📊 Trade Management

### Trade History Tab

**Features:**
- View all closed trades (last 7 days)
- Sort and filter trades
- Analyze performance

#### Sorting Options

**Sort By:**
- **Date (Newest First)**: Latest trades at top (default)
- **Date (Oldest First)**: Oldest trades at top
- **Profit (Highest First)**: Best trades first
- **Profit (Lowest First)**: Worst trades first
- **Amount (Highest First)**: Largest absolute profit/loss
- **Amount (Lowest First)**: Smallest absolute profit/loss

**How to use:**
- Find best/worst trades quickly
- Analyze recent activity
- Review specific periods

#### Filtering Options

**Filter By:**
- **All Trades**: Show everything (default)
- **Wins Only**: Only profitable trades
- **Losses Only**: Only losing trades
- **Today Only**: Only today's trades

**Symbol Filter:**
- **All Symbols**: Show all
- **XAUUSD**: Gold only
- **GBPUSD**: Pound only
- etc.

**How to use:**
- Focus on specific trade types
- Analyze wins vs losses separately
- Review symbol-specific performance

**Reset Button:**
- Click to clear all filters
- Returns to default view

#### Trade Table Columns

- **Time**: When trade closed
- **Symbol**: Trading pair
- **Type**: BUY or SELL (color-coded badge)
- **Volume**: Lot size
- **Price**: Exit price
- **Profit**: $ profit/loss (green/red)

### Open Positions Tab

**What it shows:**
- All currently open trades
- Real-time profit/loss
- Entry/current prices
- Stop loss and take profit levels

**Columns:**
- **Ticket**: Position ID
- **Symbol**: Trading pair
- **Type**: BUY or SELL
- **Volume**: Lot size
- **Entry**: Entry price
- **Current**: Current market price
- **SL**: Stop loss level
- **TP**: Take profit level
- **Profit**: Current $ profit/loss (green/red)

**How to use:**
- Monitor open trades
- Check if trades are profitable
- See stop loss and take profit levels

**Note:**
- Updates automatically every 5 seconds
- Shows "No open positions" if none

---

## 🤖 AI Recommendations

### How to Access

1. Click "AI Recommendations" tab
2. View priority-based suggestions
3. Implement recommendations

### What You'll See

**Each recommendation shows:**
- **Priority**: 1 (critical), 2 (important), 3 (optional)
- **Title**: What to fix
- **Description**: Why it matters
- **Impact**: Estimated $ savings
- **Action**: How to implement

**Example Recommendations:**

#### Priority 1: Tighten Stop Losses
```
Description: Your average loss is 332 pips. 
             Reduce ATR_MULTIPLIER_SL to 0.8
Impact: Potential savings: $2,525
Action: Update configuration
```

#### Priority 1: Avoid 19:00 Hour
```
Description: 100% of losses occurred at 19:00. 
             Enable trading hours filter.
Impact: Potential savings: $825
Action: Enable TRADING_HOURS
```

#### Priority 2: Cut Losers Faster
```
Description: Average hold time for losses is 35 minutes. 
             Reduce to 20 minutes.
Impact: Potential savings: $547
Action: Update SCALP_MAX_HOLD_MINUTES
```

### How to Use

1. **Review recommendations**
   - Start with Priority 1 items
   - Read description and impact

2. **Implement changes**
   - Go to Configuration tab
   - Adjust recommended settings
   - Save configuration

3. **Monitor results**
   - Check if performance improves
   - Review charts and stats
   - Adjust further if needed

---

## 💡 Best Practices

### For Beginners

1. **Start Conservative**
   - Use M5 or M15 timeframe
   - Risk 0.3% per trade
   - Enable adaptive risk
   - Use auto-calculate for all parameters

2. **Monitor Closely**
   - Check dashboard regularly
   - Review trade history daily
   - Analyze charts weekly

3. **Learn from Data**
   - Use Hourly Performance chart
   - Identify best trading hours
   - Focus on profitable symbols

4. **Implement Recommendations**
   - Follow AI suggestions
   - Start with Priority 1 items
   - Track improvements

### For Advanced Users

1. **Optimize Settings**
   - Test different timeframes
   - Adjust risk based on performance
   - Fine-tune confidence levels

2. **Use Charts Extensively**
   - Analyze all 5 charts
   - Identify patterns
   - Optimize based on data

3. **Custom Configurations**
   - Disable auto-calculate
   - Set custom values
   - Test and iterate

4. **Multi-Symbol Trading**
   - Trade 2-3 symbols
   - Monitor per-symbol performance
   - Adjust allocation based on results

### Risk Management

1. **Never risk more than 2% per trade**
2. **Set max daily loss limit (5% recommended)**
3. **Use stop losses always**
4. **Enable adaptive risk**
5. **Monitor equity, not just balance**

### Performance Monitoring

1. **Check Today's Profit daily**
2. **Review MTD and YTD weekly**
3. **Analyze charts weekly**
4. **Implement recommendations monthly**
5. **Adjust configuration based on data**

---

## 🎯 Quick Reference

### Configuration Presets

#### Conservative
```
Timeframe: M15
Risk: 0.2%
ATR: 1.2
Confidence: 60%
Max Daily Loss: 3%
Adaptive Risk: Yes
```

#### Balanced (Recommended)
```
Timeframe: M5
Risk: 0.3%
ATR: 1.0
Confidence: 45%
Max Daily Loss: 5%
Adaptive Risk: Yes
```

#### Aggressive
```
Timeframe: M1
Risk: 0.5%
ATR: 0.8
Confidence: 40%
Max Daily Loss: 7%
Adaptive Risk: Yes
```

### Common Tasks

**Start Trading:**
1. Configure settings
2. Click "Start Bot"
3. Monitor dashboard

**Stop Trading:**
1. Click "Stop Bot"
2. Wait for confirmation
3. Positions remain open

**Change Settings:**
1. Stop bot (if running)
2. Go to Configuration tab
3. Adjust settings
4. Save configuration
5. Start bot

**View Performance:**
1. Check Performance card
2. Go to Charts & Analytics tab
3. Review all 5 charts

**Filter Trades:**
1. Go to Trade History tab
2. Use Sort/Filter dropdowns
3. Click Reset to clear

---

## 📚 Additional Resources

- **REMOTE_ACCESS_GUIDE.md** - Access from other devices
- **DASHBOARD_ENHANCEMENTS_V2.md** - Technical details
- **WEB_DASHBOARD_GUIDE.md** - Complete documentation
- **TROUBLESHOOTING.md** - Common issues

---

## 🆘 Need Help?

### Common Questions

**Q: Bot not placing trades?**
A: Check min confidence level, may be too high

**Q: Too many losing trades?**
A: Increase min confidence, tighten stops

**Q: Missing opportunities?**
A: Lower min confidence, check filters

**Q: Dashboard not loading?**
A: Check if dashboard is running, verify URL

---

**Status:** ✅ USER GUIDE COMPLETE  
**Dashboard:** 💎 GEM Trading  
**Version:** 2.0  
**Date:** January 28, 2026

Happy trading! 💎📊🚀
