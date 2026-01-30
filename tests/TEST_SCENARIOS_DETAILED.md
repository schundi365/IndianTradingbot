# GEM Trading Bot - Detailed Test Scenarios

## Test Scenario Categories

1. Core Trading Engine Tests
2. Adaptive Risk Management Tests
3. Dynamic TP/SL Tests
4. Configuration Management Tests
5. Dashboard Tests
6. Integration Tests
7. Performance Tests
8. Error Handling Tests

---

## 1. Core Trading Engine Tests

### Scenario 1.1: Bot Initialization and Startup
**Objective:** Verify bot initializes correctly and connects to MT5

**Test Steps:**
1. Ensure MT5 is running and logged in
2. Ensure bot_config.json exists
3. Run `python run_bot.py`
4. Observe console output and logs

**Expected Results:**
- Bot loads configuration successfully
- MT5 connection established
- All modules initialized
- Trading loop starts
- Log message: "Trading bot started"

**Pass Criteria:**
- No errors in logs
- Bot status shows "Running"
- MT5 connection confirmed

---

### Scenario 1.2: Signal Generation - Bullish Crossover
**Objective:** Verify bot generates BUY signal on bullish MA crossover

**Preconditions:**
- Bot running
- Fast MA about to cross above Slow MA

**Test Steps:**
1. Monitor price action until Fast MA crosses above Slow MA
2. Check logs for signal detection
3. Verify all filters pass
4. Check if trade is executed

**Expected Results:**
- Crossover detected and logged
- Signal type: BUY
- Confidence score calculated
- Filters checked (RSI, MACD, ADX, Volume)
- Trade executed if all conditions met

**Pass Criteria:**
- Log shows: "✅ BULLISH CROSSOVER DETECTED"
- Signal confidence > min_confidence
- Position opened with correct direction

---

### Scenario 1.3: Signal Generation - Bearish Crossover
**Objective:** Verify bot generates SELL signal on bearish MA crossover

**Preconditions:**
- Bot running
- Fast MA about to cross below Slow MA

**Test Steps:**
1. Monitor price action until Fast MA crosses below Slow MA
2. Check logs for signal detection
3. Verify all filters pass
4. Check if trade is executed

**Expected Results:**
- Crossover detected and logged
- Signal type: SELL
- Confidence score calculated
- Filters checked
- Trade executed if all conditions met

**Pass Criteria:**
- Log shows: "✅ BEARISH CROSSOVER DETECTED"
- Signal confidence > min_confidence
- Position opened with correct direction

---

### Scenario 1.4: Filter Rejection - RSI Overbought
**Objective:** Verify RSI filter rejects BUY signals when overbought

**Preconditions:**
- Bot running
- use_rsi = true
- RSI > rsi_overbought (75)

**Test Steps:**
1. Wait for BUY signal when RSI > 75
2. Check logs for filter check
3. Verify signal is rejected

**Expected Results:**
- Signal generated
- RSI filter check performed
- Log shows: "❌ RSI filter: REJECTED (RSI: XX.X > 75)"
- Trade NOT executed

**Pass Criteria:**
- Signal rejected due to RSI
- No position opened
- Bot continues monitoring

---

### Scenario 1.5: Split Position Execution
**Objective:** Verify bot opens 3 split positions with different TPs

**Preconditions:**
- Bot running
- use_split_orders = true
- num_positions = 3
- Valid signal generated

**Test Steps:**
1. Wait for valid signal
2. Check trade execution
3. Verify 3 positions opened
4. Check TP levels for each position

**Expected Results:**
- 3 positions opened simultaneously
- All positions have same entry price and SL
- Position 1: TP at 1.5x risk (40% of total size)
- Position 2: TP at 2.5x risk (30% of total size)
- Position 3: TP at 4.0x risk (30% of total size)
- Group ID assigned to all positions

**Pass Criteria:**
- Exactly 3 positions opened
- TPs match configured levels
- Total lot size distributed correctly
- All positions tracked in same group

---

## 2. Adaptive Risk Management Tests

### Scenario 2.1: Strong Trend Detection
**Objective:** Verify adaptive risk detects strong trending market

**Preconditions:**
- Bot running
- use_adaptive_risk = true
- Market in strong trend (ADX > 30, consistency > 80%)

**Test Steps:**
1. Wait for signal in strong trending market
2. Check logs for market analysis
3. Verify risk multiplier adjustment
4. Check position size

**Expected Results:**
- Market classified as "strong_trend"
- Risk multiplier increased (1.2x - 2.0x)
- Wider stops applied (2.5x - 3.0x ATR)
- Wider TPs applied
- Log shows: "Market Type: strong_trend"

**Pass Criteria:**
- Market correctly classified
- Risk multiplier > 1.0
- Position size larger than standard
- Wider SL/TP than normal

---

### Scenario 2.2: Ranging Market Detection
**Objective:** Verify adaptive risk detects ranging market

**Preconditions:**
- Bot running
- use_adaptive_risk = true
- Market ranging (ADX < 20, low consistency)

**Test Steps:**
1. Wait for signal in ranging market
2. Check logs for market analysis
3. Verify risk multiplier adjustment
4. Check position size

**Expected Results:**
- Market classified as "ranging"
- Risk multiplier decreased (0.5x - 0.8x)
- Tighter stops applied
- Tighter TPs applied
- Log shows: "Market Type: ranging"

**Pass Criteria:**
- Market correctly classified
- Risk multiplier < 1.0
- Position size smaller than standard
- Tighter SL/TP than normal

---

## 3. Dynamic TP/SL Tests

### Scenario 3.1: Dynamic TP Extension on Trend Acceleration
**Objective:** Verify TP extends when trend accelerates

**Preconditions:**
- Bot running
- use_dynamic_tp = true
- Position open and profitable
- Trend accelerating

**Test Steps:**
1. Open position
2. Wait for trend to accelerate
3. Monitor TP updates
4. Check logs for extension

**Expected Results:**
- Trend acceleration detected
- TP extended by 1.5x
- Log shows: "Dynamic TP extended"
- Log shows reason: "Strong trend continuation"
- New TP further from entry than original

**Pass Criteria:**
- TP extended at least once
- Extension reason logged
- TP only moves away from entry
- Position remains open

---

### Scenario 3.2: Dynamic SL Tightening on Trend Reversal
**Objective:** Verify SL tightens when trend reverses

**Preconditions:**
- Bot running
- use_dynamic_sl = true
- Position open
- Trend reversing

**Test Steps:**
1. Open position
2. Wait for trend reversal
3. Monitor SL updates
4. Check logs for tightening

**Expected Results:**
- Trend reversal detected
- SL tightened to current - 0.5x ATR
- Log shows: "Dynamic SL updated"
- Log shows reason: "Trend reversal detected"
- New SL closer to current price

**Pass Criteria:**
- SL tightened at least once
- Tightening reason logged
- SL moves closer to protect profit
- SL never crosses current price

---

## 4. Configuration Management Tests

### Scenario 4.1: Configuration Loading
**Objective:** Verify configuration loads correctly on startup

**Preconditions:**
- bot_config.json exists with valid values

**Test Steps:**
1. Start bot
2. Check logs for config loading
3. Verify all values loaded

**Expected Results:**
- Config file found and loaded
- All required keys present
- Values match file contents
- Log shows: "Configuration loaded from bot_config.json"

**Pass Criteria:**
- No config errors
- All settings applied
- Bot uses loaded values

---

### Scenario 4.2: Configuration Saving from Dashboard
**Objective:** Verify configuration saves when changed in dashboard

**Preconditions:**
- Dashboard running
- Bot running or stopped

**Test Steps:**
1. Open dashboard
2. Go to Settings
3. Change a value (e.g., risk_percent)
4. Click Save
5. Check bot_config.json
6. Check config_backups folder

**Expected Results:**
- Settings saved to bot_config.json
- Backup created in config_backups/
- Success message displayed
- Bot reloads config on next cycle

**Pass Criteria:**
- File updated with new values
- Backup created with timestamp
- No errors in dashboard
- Bot uses new values

---

## 5. Dashboard Tests

### Scenario 5.1: Real-Time Position Updates
**Objective:** Verify dashboard shows real-time position updates

**Preconditions:**
- Dashboard running
- Bot running
- Positions open

**Test Steps:**
1. Open dashboard
2. Observe positions table
3. Wait for price movement
4. Check if profit/loss updates

**Expected Results:**
- Positions table populated
- Profit/loss updates every 2 seconds
- Current price updates
- Floating P&L calculated correctly

**Pass Criteria:**
- Updates occur automatically
- Values match MT5
- No refresh needed
- Smooth updates without flickering

---

### Scenario 5.2: Bot Start/Stop Control
**Objective:** Verify dashboard can start and stop bot

**Preconditions:**
- Dashboard running
- Bot stopped

**Test Steps:**
1. Open dashboard
2. Click "Start Bot" button
3. Verify bot starts
4. Click "Stop Bot" button
5. Verify bot stops

**Expected Results:**
- Start button triggers bot startup
- Status changes to "Running"
- Stop button triggers bot shutdown
- Status changes to "Stopped"
- Buttons enable/disable appropriately

**Pass Criteria:**
- Bot responds to commands
- Status updates correctly
- No errors in console
- Clean start/stop

---

## 6. Integration Tests

### Scenario 6.1: Complete Trade Lifecycle
**Objective:** Verify complete trade from signal to close

**Preconditions:**
- Bot running with all features enabled

**Test Steps:**
1. Wait for signal generation
2. Monitor trade execution
3. Observe position management
4. Wait for position close
5. Check trade history

**Expected Results:**
- Signal generated with all checks
- Adaptive risk analyzes market
- Position opened with optimal parameters
- Dynamic TP/SL adjust during trade
- Trailing stop activates
- Position closes at TP or SL
- Trade logged in history

**Pass Criteria:**
- All stages complete successfully
- No errors throughout lifecycle
- Trade profitable or loss within limits
- All features function correctly

---

### Scenario 6.2: All Adaptive Features Working Together
**Objective:** Verify all adaptive features work harmoniously

**Preconditions:**
- use_adaptive_risk = true
- use_dynamic_tp = true
- use_dynamic_sl = true

**Test Steps:**
1. Generate signal
2. Monitor adaptive risk analysis
3. Open position
4. Monitor dynamic TP extensions
5. Monitor dynamic SL adjustments
6. Verify no conflicts

**Expected Results:**
- Adaptive risk sets optimal entry
- Dynamic TP extends when appropriate
- Dynamic SL tightens when appropriate
- No conflicts between features
- All work together to optimize trade

**Pass Criteria:**
- All features active
- No errors or conflicts
- Trade optimized at every stage
- Logs show all adaptive actions

---

## 7. Performance Tests

### Scenario 7.1: Multi-Symbol Performance
**Objective:** Verify bot handles 16 symbols efficiently

**Preconditions:**
- 16 symbols configured
- Bot running

**Test Steps:**
1. Start bot
2. Monitor cycle time
3. Check CPU usage
4. Check memory usage
5. Verify all symbols analyzed

**Expected Results:**
- All 16 symbols analyzed each cycle
- Cycle completes within 60 seconds
- CPU usage < 10%
- Memory usage < 300 MB
- No performance degradation

**Pass Criteria:**
- Cycle time acceptable
- Resource usage reasonable
- All symbols processed
- No lag or delays

---

### Scenario 7.2: High Position Count Performance
**Objective:** Verify bot handles many open positions

**Preconditions:**
- Bot running
- Ability to open many positions

**Test Steps:**
1. Open 50+ positions
2. Monitor position management
3. Check update speed
4. Check resource usage

**Expected Results:**
- All positions managed correctly
- Updates complete within 5 seconds
- No performance issues
- Memory usage acceptable

**Pass Criteria:**
- All positions updated
- No slowdown
- No errors
- Acceptable performance

---

## 8. Error Handling Tests

### Scenario 8.1: MT5 Connection Loss
**Objective:** Verify bot handles MT5 disconnection gracefully

**Preconditions:**
- Bot running
- MT5 connected

**Test Steps:**
1. Disconnect MT5 (close platform)
2. Observe bot behavior
3. Reconnect MT5
4. Verify bot recovers

**Expected Results:**
- Bot detects disconnection
- Error logged
- Bot attempts reconnection
- Bot resumes when MT5 available
- No crash or data loss

**Pass Criteria:**
- Graceful error handling
- Automatic recovery
- No data corruption
- Bot continues after recovery

---

### Scenario 8.2: Invalid Configuration
**Objective:** Verify bot handles invalid configuration

**Preconditions:**
- bot_config.json with invalid values

**Test Steps:**
1. Set invalid value (e.g., risk_percent = 100)
2. Try to start bot or save config
3. Observe error handling

**Expected Results:**
- Validation error detected
- Clear error message
- Bot doesn't start with invalid config
- User prompted to fix

**Pass Criteria:**
- Invalid config rejected
- Clear error message
- No crash
- Safe fallback behavior

---

## Test Execution Guidelines

### Priority Levels
- **High:** Critical functionality, must pass
- **Medium:** Important features, should pass
- **Low:** Nice-to-have, can be deferred

### Test Status
- **Not Tested:** Test not yet executed
- **Pass:** Test passed all criteria
- **Fail:** Test failed one or more criteria
- **Blocked:** Cannot test due to dependency
- **Skip:** Test not applicable

### Reporting
- Document all test results
- Include screenshots for dashboard tests
- Capture logs for failed tests
- Note any unexpected behavior
- Track defects found

---

## Conversion to Excel

This document can be converted to Excel with these sheets:
1. **Test Cases Master** - All test cases in table format
2. **Detailed Scenarios** - Full scenario descriptions
3. **Test Results** - Execution results and status
4. **Defects** - Issues found during testing
5. **Coverage Matrix** - Feature vs test case mapping

---

**Document Version:** 1.0  
**Last Updated:** January 30, 2026  
**Total Test Cases:** 100
