# 💎 GEM Trading Bot - Beta Testing Guide

## 🎯 Welcome Beta Testers!

Thank you for helping test GEM Trading Bot. This guide will help you test all the new features.

---

## 🚀 Quick Start

### 1. Access Dashboard
Open your browser and go to:
- **Local:** http://localhost:5000
- **Network:** http://gemtrading:5000
- **IP Address:** http://192.168.5.39:5000

### 2. First Time Setup
You'll see a **Risk Warning & Disclaimer** modal:
- Read the warning carefully
- Check the "I understand" box
- Click "I Understand - Continue"
- This only shows once (stored in browser)

---

## 🧪 Testing Checklist

### ✅ Test 1: Disclaimer Modal
**What to test:**
- [ ] Modal appears on first visit
- [ ] Cannot continue without checking box
- [ ] "I Understand" button is disabled until box checked
- [ ] After accepting, modal doesn't show again
- [ ] Clear browser data → Modal shows again

**Expected Result:** Professional disclaimer, must accept to continue

---

### ✅ Test 2: MT5 Connection Test
**What to test:**
- [ ] Click "Test MT5" button
- [ ] Button shows spinner while testing
- [ ] If MT5 running: Shows green "Connected" with account details
- [ ] If MT5not running: Shows red "Disconnected" with error
- [ ] Start Bot button is disabled when disconnected
- [ ] Toast notification shows connection result

**Expected Result:** Clear connection status, can't start bot without MT5

---

### ✅ Test 3: Configuration Validation
**What to test:**

#### Risk Per Trade
- [ ] Enter 0.05% → Should show error (too low)
- [ ] Enter 10% → Should show error (too high)
- [ ] Enter 2% → Should show warning (risky)
- [ ] Enter 0.5% → Should be OK (no warning)

#### Min Confidence
- [ ] Enter 25% → Should show warning (low confidence)
- [ ] Enter 50% → Should be OK

#### Max Daily Loss
- [ ] Enter 15% → Should show warning (very risky)
- [ ] Enter 5% → Should be OK

**Expected Result:** Warnings appear below inputs, errors prevent saving

---

### ✅ Test 4: Save Configuration
**What to test:**
- [ ] Enter valid values
- [ ] Click "Save Configuration"
- [ ] Button shows spinner
- [ ] Green toast: "Configuration saved successfully!"
- [ ] Enter invalid values
- [ ] Try to save
- [ ] Red toast: "Please fix validation errors"

**Expected Result:** Can't save invalid config, clear feedback

---

### ✅ Test 5: Start Bot
**What to test:**

#### Without MT5
- [ ] Disconnect MT5 or don't start it
- [ ] Click "Start Bot"
- [ ] Red toast: "Cannot start bot: MT5 not connected"

#### With MT5 but Risky Settings
- [ ] Connect MT5
- [ ] Set risk to 2%
- [ ] Click "Start Bot"
- [ ] Confirmation dialog: "Risk above 1%, continue?"
- [ ] Click Cancel → Bot doesn't start
- [ ] Click OK → Bot starts

#### Normal Start
- [ ] Connect MT5
- [ ] Use safe settings (risk ≤ 1%)
- [ ] Click "Start Bot"
- [ ] Button shows spinner
- [ ] Green toast: "Bot started successfully"
- [ ] Status changes to "Running" with green indicator

**Expected Result:** Multiple safety checks, clear feedback

---

### ✅ Test 6: Stop Bot
**What to test:**
- [ ] Click "Stop Bot"
- [ ] Confirmation dialog: "Stop the trading bot?"
- [ ] Click Cancel → Bot keeps running
- [ ] Click OK → Bot stops
- [ ] Button shows spinner
- [ ] Green toast: "Bot stopped successfully"
- [ ] Status changes to "Stopped" with red indicator

**Expected Result:** Confirmation required, smooth stop

---

### ✅ Test 7: System Logs
**What to test:**
- [ ] Click "System Logs" tab
- [ ] Logs display in monospace font
- [ ] Shows timestamps and messages
- [ ] Click "Refresh Logs" → Updates
- [ ] Click "Download Logs" → Downloads file
- [ ] Blue toast: "Downloading logs..."
- [ ] File named "gem_trading_logs.txt"

**Expected Result:** Easy to view and download logs

---

### ✅ Test 8: Toast Notifications
**What to test:**
- [ ] Perform various actions
- [ ] Toast appears top-right
- [ ] Correct color for type (green/red/orange/blue)
- [ ] Auto-dismisses after 3 seconds
- [ ] Smooth slide-in animation
- [ ] Multiple toasts stack properly

**Expected Result:** Professional, non-intrusive notifications

---

### ✅ Test 9: Auto-Calculate
**What to test:**
- [ ] Check "Auto" for Risk
- [ ] Input becomes disabled and grayed
- [ ] Change timeframe
- [ ] Risk value updates automatically
- [ ] Uncheck "Auto"
- [ ] Input becomes editable again
- [ ] Test for ATR, Confidence, Scalp Hold

**Expected Result:** Auto-calculate still works with validation

---

### ✅ Test 10: All Tabs
**What to test:**
- [ ] Configuration tab → All inputs work
- [ ] Charts & Analytics → 5 charts display
- [ ] Trade History → Sorting and filtering work
- [ ] Open Positions → Shows current positions
- [ ] AI Recommendations → Shows suggestions
- [ ] System Logs → Shows recent activity

**Expected Result:** All tabs functional, data loads correctly

---

### ✅ Test 11: Mobile Responsiveness
**What to test:**
- [ ] Open on phone/tablet
- [ ] All cards stack vertically
- [ ] Buttons are touch-friendly
- [ ] Charts resize properly
- [ ] Tables scroll horizontally
- [ ] Modal fits screen
- [ ] Toast notifications visible

**Expected Result:** Works well on all devices

---

### ✅ Test 12: Error Scenarios
**What to test:**

#### MT5 Disconnects While Running
- [ ] Start bot
- [ ] Close MT5
- [ ] Check logs for error
- [ ] Bot should handle gracefully

#### Invalid Symbol
- [ ] Select symbol not in MT5
- [ ] Try to start bot
- [ ] Should show error

#### Network Issues
- [ ] Disconnect internet briefly
- [ ] Dashboard should show errors
- [ ] Reconnect → Should recover

**Expected Result:** Graceful error handling, clear messages

---

## 🐛 Bug Reporting

If you find any issues, please report:

### Required Information
1. **What were you doing?** (Step by step)
2. **What happened?** (Actual result)
3. **What should have happened?** (Expected result)
4. **Error message?** (If any)
5. **Browser?** (Chrome, Firefox, etc.)
6. **Device?** (Desktop, mobile, tablet)
7. **Screenshot?** (If possible)

### Where to Report
- Email: [your-email]
- Discord: [your-discord]
- GitHub Issues: [your-repo]

---

## 💡 Feature Feedback

We'd love to hear:
- What do you like?
- What's confusing?
- What's missing?
- What would make it better?
- Any suggestions?

---

## ⚠️ Important Notes

### Safety First
- **Always test on DEMO account first**
- Start with conservative settings
- Monitor the bot regularly
- Don't risk more than you can afford to lose

### Known Limitations
- Bot requires MT5 to be running
- Dashboard must stay open
- Internet connection required
- Windows only (for now)

### Best Practices
- Check logs regularly
- Test MT5 connection before starting
- Use adaptive risk (recommended)
- Set reasonable daily loss limit
- Monitor performance

---

## 📊 What to Focus On

### High Priority
1. **Safety Features** - Do they prevent mistakes?
2. **Error Messages** - Are they clear and helpful?
3. **User Experience** - Is it intuitive?
4. **Performance** - Does it run smoothly?
5. **Reliability** - Does it work consistently?

### Medium Priority
1. Charts accuracy
2. Trade history filtering
3. Configuration options
4. Mobile experience
5. Visual design

### Low Priority
1. Minor UI tweaks
2. Color preferences
3. Layout suggestions
4. Nice-to-have features

---

## 🎯 Success Criteria

The bot is ready for release if:
- ✅ No critical bugs
- ✅ Safety features work perfectly
- ✅ Error handling is robust
- ✅ User experience is smooth
- ✅ Documentation is clear
- ✅ Performance is good
- ✅ Mobile works well

---

## 📞 Support

### Need Help?
- Check USER_GUIDE.md
- Check TROUBLESHOOTING.md
- Check System Logs tab
- Contact support

### Emergency?
- Stop the bot immediately
- Close all positions manually in MT5
- Report the issue
- Save logs for analysis

---

## 🙏 Thank You!

Your feedback is invaluable. Every bug you find, every suggestion you make, helps make GEM Trading Bot better for everyone.

**Happy Testing!** 💎

---

## 📝 Testing Log Template

```
Date: ___________
Tester: ___________
Browser: ___________
Device: ___________

Tests Completed:
[ ] Disclaimer Modal
[ ] MT5 Connection
[ ] Configuration Validation
[ ] Save Configuration
[ ] Start Bot
[ ] Stop Bot
[ ] System Logs
[ ] Toast Notifications
[ ] Auto-Calculate
[ ] All Tabs
[ ] Mobile Responsive
[ ] Error Scenarios

Bugs Found: ___________

Features Liked: ___________

Suggestions: ___________

Overall Rating: ___/10
```

---

*GEM Trading Bot - Beta Testing Guide v1.0* 💎
