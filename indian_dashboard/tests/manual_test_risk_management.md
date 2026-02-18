# Manual Testing Guide - Risk Management Section

## Prerequisites
- Dashboard server running on http://localhost:8080
- OR open test_risk_management.html directly in browser

## Test Scenarios

### Test 1: Slider Synchronization
**Steps:**
1. Open Configuration tab → Risk sub-tab
2. Move the "Risk Per Trade" slider
3. Observe the number input field

**Expected Result:**
- Number input updates to match slider value
- Updates happen smoothly in real-time

**Steps:**
4. Type a value in the number input (e.g., 2.5)
5. Observe the slider

**Expected Result:**
- Slider position updates to match input value

### Test 2: Metrics Calculation
**Steps:**
1. Set the following values:
   - Risk Per Trade: 2%
   - Max Positions: 3
   - Max Daily Loss: 5%
   - Base Position Size: ₹10,000
   - Stop Loss: 1%
   - Take Profit: 2%

2. Observe the Risk Metrics panel

**Expected Results:**
- Risk Per Trade (₹): ₹2,000
- Max Position Size (₹): ₹200,000
- Total Risk Exposure (₹): ₹6,000
- Max Daily Loss (₹): ₹5,000
- Capital Required: ₹30,000
- Risk/Reward Ratio: 2.00

### Test 3: Real-time Updates
**Steps:**
1. Slowly move the Risk Per Trade slider from 1% to 5%
2. Watch the metrics panel

**Expected Result:**
- All metrics update smoothly in real-time
- No lag or delay
- Values are formatted correctly with ₹ symbol

### Test 4: Color Coding
**Steps:**
1. Set Risk/Reward ratio to 2.0 (Take Profit: 2%, Stop Loss: 1%)
2. Observe Risk/Reward value color

**Expected Result:**
- Should be GREEN (positive)

**Steps:**
3. Set Risk/Reward ratio to 1.5 (Take Profit: 1.5%, Stop Loss: 1%)
4. Observe Risk/Reward value color

**Expected Result:**
- Should be YELLOW (warning)

**Steps:**
5. Set Risk/Reward ratio to 0.8 (Take Profit: 0.8%, Stop Loss: 1%)
6. Observe Risk/Reward value color

**Expected Result:**
- Should be RED (negative)

### Test 5: Max Daily Loss Slider
**Steps:**
1. Move the "Max Daily Loss" slider
2. Observe the number input and metrics

**Expected Result:**
- Number input updates
- Max Daily Loss (₹) metric updates
- Color coding may change based on value

### Test 6: Responsive Design
**Steps:**
1. Resize browser window to mobile size (< 768px)
2. Observe the Risk Management section

**Expected Result:**
- Metrics grid stacks vertically
- Sliders remain functional
- All text is readable
- No horizontal scrolling

### Test 7: Form Integration
**Steps:**
1. Set risk parameters
2. Click "Save Configuration"
3. Reload the page
4. Click "Load Configuration"

**Expected Result:**
- Risk parameters are saved
- Metrics recalculate on load
- All values are restored correctly

### Test 8: Validation
**Steps:**
1. Open browser console
2. Type: `RiskManagement.validateRiskParameters()`
3. Press Enter

**Expected Result:**
- Returns object with `valid` and `errors` properties
- If total risk > daily loss, shows error
- If risk/reward < 1, shows error

### Test 9: Capital Update
**Steps:**
1. Open browser console
2. Type: `RiskManagement.updateCapital(200000)`
3. Press Enter
4. Observe metrics panel

**Expected Result:**
- All metrics recalculate with new capital
- Values approximately double (if capital doubled)

### Test 10: Edge Cases
**Steps:**
1. Set Risk Per Trade to minimum (0.1%)
2. Observe metrics

**Expected Result:**
- Metrics calculate correctly
- No errors in console

**Steps:**
3. Set Risk Per Trade to maximum (10%)
4. Observe metrics

**Expected Result:**
- Metrics calculate correctly
- May show warning colors

## Quick Test Checklist
- [ ] Sliders move smoothly
- [ ] Slider ↔ Input synchronization works
- [ ] Metrics calculate correctly
- [ ] Metrics update in real-time
- [ ] Color coding applies
- [ ] Responsive on mobile
- [ ] Form save/load works
- [ ] No console errors
- [ ] Number formatting correct (₹ symbol, commas)
- [ ] All 6 metrics display

## Common Issues

### Issue: Metrics show "--"
**Solution:** Check that all required input fields have values

### Issue: Slider doesn't move
**Solution:** Check browser console for JavaScript errors

### Issue: Colors don't change
**Solution:** Verify CSS is loaded correctly

### Issue: Metrics don't update
**Solution:** Check that event listeners are attached

## Browser Compatibility
Test in:
- [ ] Chrome/Edge (Chromium)
- [ ] Firefox
- [ ] Safari (if available)

## Performance
- Metrics should update within 50ms of input change
- No visible lag when moving sliders
- Smooth animations

## Accessibility
- [ ] Can navigate with keyboard (Tab key)
- [ ] Sliders work with arrow keys
- [ ] Labels are clear and descriptive
- [ ] Help text provides context

## Success Criteria
All tests pass with no errors or unexpected behavior.
