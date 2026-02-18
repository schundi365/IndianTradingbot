# Manual Test Checklist - Task 7.8

## Prerequisites
- Dashboard is running: `python indian_dashboard.py`
- Browser is open to: `http://localhost:8080`

## Test 1: Save Configuration Dialog

### Steps:
1. Navigate to Configuration tab
2. Fill in some configuration values:
   - Select a timeframe
   - Select a strategy
   - Set risk per trade to 2%
   - Set max positions to 5
3. Click "Save Configuration" button

### Expected Results:
- ✅ Modal dialog appears
- ✅ Name input is focused
- ✅ Description field is visible
- ✅ Cancel and Save buttons are visible

### Test 1a: Empty Name Validation
1. Leave name field empty
2. Click Save

### Expected:
- ✅ Error message appears: "Configuration name is required"
- ✅ Dialog stays open

### Test 1b: Invalid Name Validation
1. Enter name: `test@config!`
2. Click Save

### Expected:
- ✅ Error message appears about invalid characters
- ✅ Dialog stays open

### Test 1c: Valid Save
1. Enter name: `My Test Config`
2. Enter description: `This is a test configuration`
3. Click Save

### Expected:
- ✅ Success notification appears
- ✅ Dialog closes
- ✅ Configuration is saved

## Test 2: Load Configuration Dialog

### Steps:
1. Click "Load Configuration" button

### Expected Results:
- ✅ Modal dialog appears
- ✅ Loading indicator shows briefly
- ✅ Configuration list appears
- ✅ "My Test Config" is in the list
- ✅ Configuration card shows:
  - Name: "My Test Config"
  - Description: "This is a test configuration"
  - Broker badge (if set)
  - Strategy badge (if set)
  - Instrument count (if any)
- ✅ Load button is visible
- ✅ Delete button is visible

## Test 3: Load Configuration

### Steps:
1. In Load Configuration dialog
2. Click "Load" button on "My Test Config"

### Expected Results:
- ✅ Success notification appears
- ✅ Dialog closes
- ✅ Form is populated with saved values
- ✅ Configuration tab is active

## Test 4: Delete Configuration

### Steps:
1. Click "Load Configuration" button
2. Click "Delete" button on "My Test Config"
3. Confirm deletion in browser dialog

### Expected Results:
- ✅ Confirmation dialog appears
- ✅ After confirming, success notification appears
- ✅ Configuration card is removed from list
- ✅ If list is now empty, empty state message appears

## Test 5: Multiple Configurations

### Steps:
1. Save 3 different configurations:
   - "NIFTY Strategy"
   - "BANKNIFTY Strategy"
   - "Equity Intraday"
2. Open Load Configuration dialog

### Expected Results:
- ✅ All 3 configurations appear in list
- ✅ Configurations are sorted alphabetically
- ✅ Each has Load and Delete buttons
- ✅ Metadata is displayed correctly

## Test 6: Overwrite Configuration

### Steps:
1. Save a configuration named "Test Overwrite"
2. Change some form values
3. Save again with same name "Test Overwrite"
4. Load "Test Overwrite"

### Expected Results:
- ✅ Configuration is overwritten (not duplicated)
- ✅ Loaded values match the second save

## Test 7: Cancel Operations

### Steps:
1. Click "Save Configuration"
2. Enter a name
3. Click Cancel

### Expected:
- ✅ Dialog closes
- ✅ Configuration is NOT saved

### Steps:
1. Click "Load Configuration"
2. Click Close button

### Expected:
- ✅ Dialog closes
- ✅ No configuration is loaded

## Test 8: Keyboard Navigation

### Steps:
1. Click "Save Configuration"
2. Press Tab key multiple times
3. Press Enter on Save button
4. Press Escape key

### Expected:
- ✅ Tab moves focus through fields
- ✅ Enter submits form (if valid)
- ✅ Escape closes dialog

## Test 9: Mobile Responsiveness

### Steps:
1. Resize browser to mobile width (< 768px)
2. Open Save Configuration dialog
3. Open Load Configuration dialog

### Expected:
- ✅ Dialogs are responsive
- ✅ Buttons stack vertically on mobile
- ✅ Text is readable
- ✅ All functionality works

## Test 10: Error Handling

### Steps:
1. Stop the Flask server
2. Try to save a configuration
3. Try to load configurations

### Expected:
- ✅ Error notifications appear
- ✅ Error messages are user-friendly
- ✅ Dialogs handle errors gracefully

## Test 11: Integration with Validation

### Steps:
1. Leave required fields empty in form
2. Click "Save Configuration"

### Expected:
- ✅ Validation error notification appears
- ✅ Save dialog does NOT open
- ✅ User is prompted to fix errors first

## Test 12: Integration with Presets

### Steps:
1. Select a preset from dropdown
2. Click "Save Configuration"
3. Save with a custom name
4. Load the saved configuration

### Expected:
- ✅ Preset values are saved
- ✅ Loaded configuration matches preset values

## Summary

Total Tests: 12
- [ ] All tests passed
- [ ] Issues found (list below):

### Issues Found:
(List any issues discovered during testing)

### Notes:
(Add any additional observations)

---

**Tester Name**: _______________
**Date**: _______________
**Browser**: _______________
**Dashboard Version**: _______________
