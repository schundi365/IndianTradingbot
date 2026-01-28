# Testing Steps - Complete Guide

Follow these steps in order to test your MT5 Trading Bot.

## 📋 Testing Checklist

### Phase 1: Setup Validation (5 minutes)
- [ ] Python installed
- [ ] Dependencies installed
- [ ] Files organized
- [ ] Configuration loads

### Phase 2: MT5 Connection (5 minutes)
- [ ] MT5 running
- [ ] Account logged in
- [ ] Connection works
- [ ] Data retrieval works

### Phase 3: Trading Permissions (5 minutes)
- [ ] Trading allowed
- [ ] Symbols available
- [ ] Margin sufficient
- [ ] Market open

### Phase 4: Trading Capability (10 minutes)
- [ ] Can place orders
- [ ] Can close orders
- [ ] Orders execute correctly
- [ ] No errors

### Phase 5: Bot Functionality (30 minutes)
- [ ] Bot starts
- [ ] Signals detected
- [ ] Would place trades
- [ ] All features work

---

## Step-by-Step Testing

### Step 1: Validate Setup ✅

**What it tests:** Python, dependencies, file structure

**Command:**
```bash
python validate_setup.py
```

**Expected output:**
```
✅ Python 3.12.10
✅ MetaTrader5 installed
✅ pandas installed
✅ numpy installed
✅ All files present
✅ Configuration loaded
```

**If it fails:**
- Install missing dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version` (need 3.8+)

---

### Step 2: Test MT5 Connection ✅

**What it tests:** MT5 is running and logged in

**Command:**
```bash
python test_mt5_simple.py
```

**Expected output:**
```
✅ MT5 initialized successfully
✅ Account connected!
   Login: 10009302175
   Balance: 50000.0 GBP
```

**If it fails:**
- Make sure MT5 is running
- Login to your account in MT5
- Check you see account balance in MT5

---

### Step 3: Check Trading Permissions ✅

**What it tests:** Bot has permission to trade (NO actual trades)

**Command:**
```bash
python test_trading_permissions.py
```

**Expected output:**
```
✅ PASSED: Trading is allowed
✅ PASSED: Demo account
✅ PASSED: XAUUSD available
✅ PASSED: XAGUSD available
✅ PASSED: Margin calculation works
✅ PASSED: Market OPEN

🎉 ALL TESTS PASSED!
✅ Your bot CAN trade!
```

**What it checks:**
1. ✅ MT5 connection
2. ✅ Account accessible
3. ✅ Trading permission enabled
4. ✅ Account type (demo/real)
5. ✅ Symbols available
6. ✅ Margin sufficient
7. ✅ Market status

**If "Trading not allowed":**
1. In MT5: Tools → Options
2. Expert Advisors tab
3. Check: ✅ Allow algorithmic trading
4. Check: ✅ Allow DLL imports
5. Click OK
6. Run test again

**If "Symbol not available":**
- Check symbol name in MT5 (might be "GOLD" instead of "XAUUSD")
- Edit `src/config.py` with correct symbol names

---

### Step 4: Test Trading Capability ⚠️

**What it tests:** Bot can actually place and close trades (REAL test trade!)

**⚠️ WARNING:** This places a REAL order (minimum size, closed immediately)

**Command:**
```bash
python test_trading_capability.py
```

**What happens:**
1. Asks for confirmation
2. Places minimum lot size order (0.01)
3. Waits 2 seconds
4. Closes the order immediately
5. Shows profit/loss (usually a few cents)

**Expected output:**
```
✅ Order placed successfully!
   Order: 123456
   Volume: 0.01
   Price: 5094.83

✅ Position found
   Profit: -0.04 GBP

✅ Position closed successfully!
   Final Profit/Loss: -0.04 GBP

🎉 TRADING CAPABILITY: CONFIRMED!
```

**Cost:** Usually 0-10 cents (spread cost)

**If order fails:**
- Error 10019 (Not enough money): Check balance
- Error 10014 (Invalid volume): Check min lot size
- Error 10018 (Market closed): Wait for market to open
- Error 10016 (Invalid stops): SL/TP too close

**After this test:**
- Check MT5 account history
- Verify order was placed and closed
- Note the small cost (spread)

---

### Step 5: Test Bot Functionality ✅

**What it tests:** Bot can run and check for signals (NO trades)

**Command:**
```bash
python test_bot_live.py
```

**Expected output:**
```
✅ Connected to MT5
Account Balance: 50000.0 GBP

XAUUSD:
  Current Price: Bid=5094.79
  ✅ Retrieved 100 bars of data
  ✅ Data ready for analysis

✅ Bot is functioning correctly!
```

**What it checks:**
- Bot initializes
- Connects to MT5
- Retrieves market data
- Adaptive risk enabled
- Split orders enabled
- All features working

---

### Step 6: Quick Signal Test ✅

**What it tests:** Signal detection logic (NO trades)

**Command:**
```bash
python examples/quick_test.py
```

**Expected output:**
```
✅ MT5 connected

Checking for signals...
⏸️  No signal for XAUUSD
   Price: 5094.79, Fast MA: 5070.78, Slow MA: 5054.38
⏸️  No signal for XAGUSD
   Price: 108.41, Fast MA: 109.51, Slow MA: 107.92
```

**What it shows:**
- Current price
- Fast MA (20-period)
- Slow MA (50-period)
- Signal status (BUY/SELL/None)

---

## 🎯 Complete Testing Sequence

Run all tests in order:

```bash
# 1. Setup (1 minute)
python validate_setup.py

# 2. Connection (1 minute)
python test_mt5_simple.py

# 3. Permissions (1 minute) - SAFE
python test_trading_permissions.py

# 4. Trading capability (2 minutes) - PLACES 1 TEST TRADE
python test_trading_capability.py

# 5. Bot functionality (1 minute) - SAFE
python test_bot_live.py

# 6. Signal detection (1 minute) - SAFE
python examples/quick_test.py
```

**Total time:** ~7 minutes

---

## ✅ Success Criteria

After all tests, you should have:

- [x] All dependencies installed
- [x] MT5 connected
- [x] Account accessible
- [x] Trading allowed
- [x] Symbols available
- [x] Test order placed successfully
- [x] Test order closed successfully
- [x] Bot initializes correctly
- [x] Data retrieval works
- [x] Signals detected

**If all checked:** ✅ Ready to run the bot!

---

## 🚀 After Testing

### If All Tests Pass:

**Option 1: Start Bot (Demo)**
```bash
python run_bot.py
```
- Type 'yes' when prompted
- Bot will start trading
- Monitor closely
- Press Ctrl+C to stop

**Option 2: Continue Testing**
- Run bot for a few hours
- Check if it places trades
- Verify SL/TP are correct
- Test trailing stops
- Check split orders

**Option 3: Push to GitHub**
```bash
git add .
git commit -m "All tests passed - ready for deployment"
git push origin main
```

### If Any Test Fails:

1. **Read error message carefully**
2. **Check TROUBLESHOOTING.md**
3. **Fix the issue**
4. **Run test again**
5. **Don't proceed until all pass**

---

## 📊 Test Results Log

Keep track of your testing:

```
Date: _______________

Test 1 - Setup Validation:        [ ] Pass  [ ] Fail
Test 2 - MT5 Connection:           [ ] Pass  [ ] Fail
Test 3 - Trading Permissions:      [ ] Pass  [ ] Fail
Test 4 - Trading Capability:       [ ] Pass  [ ] Fail
Test 5 - Bot Functionality:        [ ] Pass  [ ] Fail
Test 6 - Signal Detection:         [ ] Pass  [ ] Fail

Notes:
_________________________________
_________________________________
_________________________________

Ready to proceed: [ ] Yes  [ ] No
```

---

## ⚠️ Important Notes

### About Test Trades

**test_trading_capability.py:**
- Places REAL order (minimum size)
- Costs a few cents (spread)
- Closed immediately
- Safe on demo account
- Use caution on real account

### About Demo vs Real

**Demo Account:**
- ✅ Safe for testing
- ✅ No real money risk
- ✅ Test all features
- ✅ Make mistakes safely

**Real Account:**
- ⚠️ Real money at risk
- ⚠️ Start with minimum risk
- ⚠️ Test on demo first
- ⚠️ Monitor closely

### Before Live Trading

**Minimum Requirements:**
- [ ] All tests passed on demo
- [ ] Ran bot for 2+ weeks on demo
- [ ] Understand all features
- [ ] Know how to stop bot
- [ ] Can manually close positions
- [ ] Have emergency plan
- [ ] Comfortable with risk

---

## 🆘 Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| MT5 not found | Install and run MT5 |
| Authorization failed | Login to MT5 account |
| Trading not allowed | Enable in MT5 settings |
| Symbol not found | Check symbol names |
| Not enough money | Check balance/reduce risk |
| Market closed | Wait for market hours |
| Order rejected | Check broker requirements |

**Full guide:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## 📞 Need Help?

1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Review test output carefully
3. Check `trading_bot.log`
4. Search GitHub Issues
5. Ask in GitHub Discussions

---

**Remember:** Take your time with testing. Better to find issues now than lose money later!

**Good luck! 🚀**
