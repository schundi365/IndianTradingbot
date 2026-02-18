# Indian Market Web Dashboard - Frequently Asked Questions (FAQ)

## General Questions

### Q1: What is the Indian Market Web Dashboard?
**A:** The Indian Market Web Dashboard is a web-based interface for configuring and monitoring an automated trading bot for Indian stock markets (NSE, BSE, NFO). It provides a visual way to select instruments, configure trading strategies, and monitor your bot's performance in real-time.

### Q2: Do I need programming knowledge to use this dashboard?
**A:** No! The dashboard is designed for traders without programming experience. Everything is done through a visual interface with forms, dropdowns, and buttons.

### Q3: Is this dashboard free to use?
**A:** Yes, the dashboard software itself is free and open-source. However, you'll need an active broker account for live trading, which may have associated costs.

### Q4: Which operating systems are supported?
**A:** The dashboard runs on Windows, macOS, and Linux. You need Python 3.8 or higher installed.

### Q5: Can I use this for live trading?
**A:** Yes, but we strongly recommend starting with Paper Trading to test your strategies before risking real money.

---

## Installation & Setup

### Q6: How do I install the dashboard?
**A:** 
1. Install Python 3.8 or higher
2. Run: `pip install -r requirements.txt`
3. Set environment variables (FLASK_SECRET_KEY, ENCRYPTION_KEY)
4. Run: `python indian_dashboard/indian_dashboard.py`
5. Access at `http://localhost:8080`

See the USER_GUIDE.md for detailed instructions.

### Q7: What are the system requirements?
**A:**
- Python 3.8 or higher
- 2GB RAM minimum
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection
- 100MB free disk space

### Q8: I get an error "Port 8080 already in use". What should I do?
**A:** Either:
- Stop the application using port 8080
- Or run the dashboard on a different port: `python indian_dashboard.py --port 8081`

### Q9: What are FLASK_SECRET_KEY and ENCRYPTION_KEY?
**A:** These are security keys:
- **FLASK_SECRET_KEY**: Secures your session data
- **ENCRYPTION_KEY**: Encrypts your broker credentials

Generate random strings (32+ characters) for both. Never share these keys!

Example:
```bash
# Windows
set FLASK_SECRET_KEY=your-random-secret-key-here-32-chars-min
set ENCRYPTION_KEY=your-random-encryption-key-32-chars-min

# Linux/Mac
export FLASK_SECRET_KEY=your-random-secret-key-here-32-chars-min
export ENCRYPTION_KEY=your-random-encryption-key-32-chars-min
```

---

## Broker Connection

### Q10: Which brokers are supported?
**A:** Currently supported:
- Kite Connect (Zerodha)
- Alice Blue
- Angel One
- Upstox
- Paper Trading (for testing)

### Q11: How do I get API credentials for my broker?
**A:**
- **Kite Connect**: Visit https://kite.trade/, create an app
- **Alice Blue**: Contact Alice Blue support
- **Angel One**: Use your trading account credentials + enable TOTP
- **Upstox**: Visit https://api.upstox.com/, create an app

### Q12: Is it safe to enter my broker credentials?
**A:** Yes, credentials are:
- Encrypted using industry-standard encryption (Fernet)
- Stored locally on your computer
- Never sent to any third-party servers
- Only used to connect to your broker's official API

### Q13: What is OAuth and should I use it?
**A:** OAuth is a secure authentication method where you log in directly on your broker's website (not in the dashboard). It's more secure than entering API keys. Use it if your broker supports it (like Kite Connect).

### Q14: My broker connection keeps failing. What should I check?
**A:**
1. Verify credentials are correct
2. Check if your broker account is active
3. Ensure you have API access enabled
4. Check broker's API status page
5. Verify internet connection
6. For Kite: Check if access token expired (re-authenticate)

### Q15: Can I connect to multiple brokers simultaneously?
**A:** No, you can only connect to one broker at a time. To switch brokers, disconnect from the current one first.

---

## Instrument Selection

### Q16: How many instruments can I select?
**A:** There's no hard limit, but we recommend:
- 1-3 instruments for beginners
- 3-5 instruments for intermediate traders
- 5-10 instruments maximum (to avoid API rate limits)

### Q17: Can I trade both stocks and F&O instruments together?
**A:** Yes, you can select a mix of equity (EQ), futures (FUT), and options (CE/PE) instruments.

### Q18: Why don't I see any instruments in the list?
**A:**
1. Ensure broker is connected
2. Click "Refresh Instruments" button
3. Check browser console for errors (F12)
4. Verify broker API is working

### Q19: How often is the instrument list updated?
**A:** Instruments are cached for 24 hours. Click "Refresh Instruments" to update manually. This is especially important around F&O expiry dates.

### Q20: Can I search for instruments by ISIN or token?
**A:** Currently, search works by symbol and company name only. Use filters (Exchange, Type) to narrow down results.

---

## Configuration

### Q21: What's the difference between strategies?
**A:**
- **Trend Following**: Trades in direction of trend (moving averages)
- **Mean Reversion**: Trades when price deviates from average
- **Breakout**: Trades when price breaks support/resistance
- **Momentum**: Trades based on price momentum indicators

### Q22: What timeframe should I use?
**A:**
- **1min**: Very active, many signals (high risk)
- **5min**: Active intraday trading
- **15min**: Moderate intraday trading (recommended for beginners)
- **1hour**: Swing trading
- **1day**: Positional trading

### Q23: How much should I risk per trade?
**A:**
- **Conservative**: 1-1.5% per trade
- **Moderate**: 2-2.5% per trade
- **Aggressive**: 3-4% per trade
- **Never exceed 5%** - this is a hard limit for safety

### Q24: What is "Max Daily Loss" and why is it important?
**A:** Max Daily Loss is the maximum percentage of your capital you're willing to lose in a single day. When this limit is hit, the bot stops trading for the day. This protects you from catastrophic losses on bad days.

Recommended: 3-5% of capital.

### Q25: Can I modify configuration while the bot is running?
**A:** No, you must stop the bot first, modify the configuration, save it, and then restart the bot.

### Q26: What are configuration presets?
**A:** Presets are pre-configured settings for common trading scenarios:
- **NIFTY Futures**: Optimized for NIFTY index futures
- **BANKNIFTY Futures**: Optimized for BANKNIFTY futures
- **Equity Intraday**: For stock intraday trading
- **Options Trading**: For options strategies

You can load a preset and customize it.

### Q27: Where are my configurations saved?
**A:** Configurations are saved as JSON files in the `configs/` directory. You can backup this folder to preserve your configurations.

---

## Bot Operation

### Q28: How do I start the bot?
**A:**
1. Connect to broker
2. Select instruments
3. Configure strategy
4. Save configuration
5. Go to Monitor tab
6. Click "Start Bot"

### Q29: What happens when I start the bot?
**A:** The bot:
1. Validates configuration
2. Connects to broker
3. Starts monitoring selected instruments
4. Calculates indicators
5. Generates trading signals
6. Executes trades based on your strategy
7. Manages open positions

### Q30: Can I leave the bot running overnight?
**A:** The bot will continue running, but Indian markets are closed overnight. The bot won't trade outside market hours (09:15-15:30 IST by default).

### Q31: What happens if my internet disconnects?
**A:** The bot will attempt to reconnect. If reconnection fails after several attempts, the bot will pause. Open positions remain open (not auto-closed). Restart the bot once internet is restored.

### Q32: Can I close positions manually?
**A:** Yes, in the Monitor tab, click the "Close" button next to any open position. This will close the position at market price.

### Q33: Will the bot close all positions at end of day?
**A:** This depends on your strategy configuration. Most intraday strategies will close positions before market close (15:30 IST). Check your strategy settings.

### Q34: How do I stop the bot?
**A:** Go to Monitor tab and click "Stop Bot". The bot will finish its current iteration and then stop. Open positions are NOT automatically closed.

---

## Monitoring & Performance

### Q35: How often does the dashboard update?
**A:** The Monitor tab auto-refreshes every 5 seconds by default. You can also manually refresh anytime.

### Q36: What is "Unrealized P&L"?
**A:** Unrealized P&L is the profit or loss on your open positions if you were to close them at current market price. It's not actual profit/loss until you close the position.

### Q37: What is "Realized P&L"?
**A:** Realized P&L is the actual profit or loss from closed positions. This is real money gained or lost.

### Q38: Where can I see my trade history?
**A:** Go to the Trades tab. You can filter by date range and export to CSV/Excel.

### Q39: Can I export my trading data?
**A:** Yes, in the Trades tab, click "Export to CSV" or "Export to Excel". This exports all trades in the current date range.

### Q40: How do I calculate my win rate?
**A:** Win rate is shown in the Trades tab statistics. It's calculated as:
```
Win Rate = (Number of Winning Trades / Total Trades) × 100
```

---

## Paper Trading

### Q41: What is Paper Trading?
**A:** Paper Trading simulates real trading without using real money. It's perfect for:
- Testing strategies
- Learning the platform
- Practicing without risk

### Q42: Is Paper Trading data realistic?
**A:** Paper Trading uses real market data but simulates order execution. Execution may be more optimistic than real trading (no slippage, instant fills).

### Q43: Can I switch from Paper Trading to live trading?
**A:** Yes:
1. Stop the bot
2. Disconnect from Paper Trading
3. Connect to your real broker
4. Verify configuration
5. Start bot with real broker

### Q44: Does Paper Trading have any limitations?
**A:** Paper Trading:
- Uses simulated balance (default ₹1,00,000)
- May not reflect real market conditions (slippage, liquidity)
- Doesn't account for brokerage fees
- Orders always fill at market price

---

## Risk Management

### Q45: What is position sizing?
**A:** Position sizing determines how much capital to allocate to each trade. Methods:
- **Fixed**: Same amount for every trade
- **Risk-Based**: Size based on stop loss distance
- **Percentage**: Fixed percentage of capital

### Q46: What is a Stop Loss?
**A:** Stop Loss is a price level where you exit a losing trade to limit losses. Always use stop losses!

Example: Buy at ₹100, Stop Loss at ₹98 = Maximum loss of ₹2 per share.

### Q47: What is a Take Profit?
**A:** Take Profit is a price level where you exit a winning trade to lock in profits.

Example: Buy at ₹100, Take Profit at ₹105 = Target profit of ₹5 per share.

### Q48: What is a Trailing Stop Loss?
**A:** A trailing stop loss moves up as price moves in your favor, locking in profits while giving room for further gains.

Example: Buy at ₹100, Trailing Stop 2%
- Price moves to ₹105 → Stop moves to ₹102.90
- Price moves to ₹110 → Stop moves to ₹107.80

### Q49: How do I protect my capital?
**A:**
1. Never risk more than 2% per trade
2. Set max daily loss limit (3-5%)
3. Limit number of concurrent positions
4. Always use stop losses
5. Start with Paper Trading
6. Don't trade with money you can't afford to lose

### Q50: What should I do if I'm losing money?
**A:**
1. Stop the bot immediately
2. Review your trades in Trades tab
3. Analyze what went wrong
4. Adjust strategy or risk parameters
5. Test changes in Paper Trading
6. Consider reducing position sizes
7. Seek advice from experienced traders

---

## Technical Issues

### Q51: The dashboard is very slow. What can I do?
**A:**
1. Reduce auto-refresh frequency
2. Limit number of selected instruments
3. Clear browser cache
4. Close other browser tabs
5. Check system resources (CPU, RAM)
6. Restart the dashboard

### Q52: I see "Session expired" error. What does this mean?
**A:** Your login session timed out (default: 1 hour of inactivity). Reconnect to your broker to continue.

### Q53: What does "Rate limit exceeded" mean?
**A:** You've made too many API calls to your broker in a short time. Wait a few minutes and try again. To avoid this:
- Use longer timeframes (15min instead of 1min)
- Reduce number of instruments
- Increase refresh interval

### Q54: Where are the log files?
**A:**
- Dashboard logs: `logs/dashboard.log`
- Bot logs: `logs/bot.log`

Check these for detailed error messages.

### Q55: How do I report a bug?
**A:**
1. Check if issue is already reported on GitHub
2. Gather information:
   - Error message
   - Steps to reproduce
   - Log files
   - System info (OS, Python version)
3. Create a GitHub issue with details

---

## Security & Privacy

### Q56: Is my data secure?
**A:** Yes:
- All data stored locally on your computer
- Credentials encrypted with industry-standard encryption
- No data sent to third-party servers
- Only communicates with your broker's official API

### Q57: Can someone hack my broker account through this dashboard?
**A:** The dashboard uses your broker's official API with the same security as their mobile apps. Follow best practices:
- Use strong encryption keys
- Don't share your API credentials
- Keep your computer secure
- Disconnect when not trading

### Q58: Should I share my configuration files?
**A:** Configuration files (JSON) don't contain credentials, so they're safe to share. However, they reveal your trading strategy, so share only if you want others to know your approach.

### Q59: What happens to my credentials when I disconnect?
**A:** Credentials remain encrypted on disk. They're only decrypted when you reconnect. To completely remove credentials, delete the `credentials/` directory.

---

## Advanced Topics

### Q60: Can I run multiple bots simultaneously?
**A:** Not with a single dashboard instance. You could run multiple dashboard instances on different ports with different configurations, but this is not recommended for beginners.

### Q61: Can I customize the trading strategy?
**A:** The dashboard uses predefined strategies. To create custom strategies, you'll need to modify the bot's Python code directly.

### Q62: Can I backtest my strategy?
**A:** Backtesting is not currently available in the dashboard. This is a planned feature for future versions.

### Q63: Can I use this for options strategies (spreads, straddles)?
**A:** The current version supports simple directional options trading. Complex multi-leg strategies are not yet supported.

### Q64: Can I integrate this with other tools?
**A:** The dashboard provides a REST API that could be integrated with other tools. See API_DOCUMENTATION.md for details.

### Q65: Is there a mobile app?
**A:** Not currently. The web dashboard is mobile-responsive, so you can access it from your phone's browser, but a native mobile app is not available.

---

## Getting Help

### Q66: Where can I find more documentation?
**A:**
- **USER_GUIDE.md**: Complete user guide
- **QUICK_REFERENCE.md**: Quick reference for common tasks
- **VISUAL_WORKFLOW_GUIDE.md**: Visual diagrams of workflows
- **API_DOCUMENTATION.md**: API reference
- **README.md**: Project overview

### Q67: How do I get support?
**A:**
1. Check this FAQ
2. Review the USER_GUIDE.md
3. Check log files for errors
4. Search GitHub issues
5. Create a new GitHub issue if needed

### Q68: Can I contribute to the project?
**A:** Yes! The project is open-source. You can:
- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation
- Help other users

### Q69: Is there a community forum?
**A:** Check the project's GitHub repository for links to community channels (Discord, Telegram, etc.).

### Q70: How often is the dashboard updated?
**A:** Check the GitHub repository for the latest releases and changelog. Updates may include:
- Bug fixes
- New features
- Performance improvements
- Security patches

---

## Best Practices

### Q71: What are the best practices for using this dashboard?
**A:**
1. **Start with Paper Trading** - Test before risking real money
2. **Use Stop Losses** - Always protect your capital
3. **Limit Risk** - Never risk more than 2% per trade
4. **Monitor Regularly** - Check your bot frequently
5. **Keep Logs** - Review trade history to improve
6. **Stay Informed** - Keep up with market news
7. **Backup Configs** - Save your configurations
8. **Update Regularly** - Keep dashboard up to date

### Q72: How should I test a new strategy?
**A:**
1. Configure strategy in dashboard
2. Test with Paper Trading for at least 1 week
3. Analyze results (win rate, P&L, drawdown)
4. Adjust parameters if needed
5. Test again with Paper Trading
6. Start with small position sizes in live trading
7. Gradually increase size as confidence grows

### Q73: What should I monitor daily?
**A:**
- Bot status (running/stopped)
- Open positions and P&L
- Daily loss limit
- Broker connection status
- Any error messages
- Market news and events

### Q74: When should I stop trading?
**A:**
- Daily loss limit hit
- Unusual market conditions
- Major news events
- Technical issues
- Emotional stress
- End of trading day

### Q75: How do I improve my trading performance?
**A:**
1. Keep a trading journal
2. Review all trades (wins and losses)
3. Identify patterns in losses
4. Adjust strategy based on data
5. Test changes in Paper Trading
6. Learn from experienced traders
7. Stay disciplined with risk management

---

**Still have questions?** Check the USER_GUIDE.md or create an issue on GitHub.

**Version**: 1.0.0  
**Last Updated**: 2024-02-18
