# Dashboard TP/SL Controls - User Guide

## Quick Access

1. Open dashboard: **http://localhost:5000**
2. Click **"Configuration"** tab
3. Scroll to **"TP/SL Calculation Method"** section (orange/red gradient box)

## What You'll See

### The Control Panel

```
🎯 TP/SL Calculation Method
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ CRITICAL: Both SL and TP must use the same calculation method!
Mixing methods causes SL > TP (negative risk/reward)

Stop Loss Method
┌─────────────────────────────────────────┐
│ [Dropdown: ATR-Based / Pip-Based]       │
└─────────────────────────────────────────┘

Stop Loss (Pips)                    [Only shown if Pip-Based selected]
┌─────────────────────────────────────────┐
│ [50]                                    │
└─────────────────────────────────────────┘
Distance from entry in pips

Take Profit Method
┌─────────────────────────────────────────┐
│ [Dropdown: Ratio-Based / Pip-Based]     │
└─────────────────────────────────────────┘

Take Profit Base (Pips)             [Only shown if Pip-Based selected]
┌─────────────────────────────────────────┐
│ [100]                                   │
└─────────────────────────────────────────┘
Base TP distance (multiplied by TP levels)

[Status Indicator - Red or Green]
```

## Status Indicators

### ❌ Red Warning (Inconsistent)
```
❌ WARNING: Inconsistent Methods!
SL and TP use different calculation methods. This can cause SL > TP!
```

**What it means:** You've selected different methods for SL and TP. This will cause problems!

**How to fix:** Change both dropdowns to the same method.

### ✓ Green OK (Consistent)
```
✓ Methods Consistent
Both use pip-based calculation:
SL: 50 pips | TP1: 150 pips | TP2: 250 pips | TP3: 400 pips
```

**What it means:** Your configuration is correct and will work properly.

## Configuration Options

### Option 1: Pip-Based (Recommended)

**When to use:**
- You want predictable, consistent distances
- Trading multiple symbols with different volatilities
- You prefer fixed risk/reward ratios

**Settings:**
- Stop Loss Method: **Pip-Based**
- Stop Loss (Pips): **50** (adjust to your preference)
- Take Profit Method: **Pip-Based**
- Take Profit Base (Pips): **100** (adjust to your preference)

**Result:**
- SL always 50 pips from entry
- TP1: 150 pips (100 × 1.5)
- TP2: 250 pips (100 × 2.5)
- TP3: 400 pips (100 × 4.0)

### Option 2: ATR-Based (Adaptive)

**When to use:**
- You want distances to adapt to market volatility
- Trading single symbol with varying volatility
- You prefer dynamic risk management

**Settings:**
- Stop Loss Method: **ATR-Based**
- Take Profit Method: **Ratio-Based**

**Result:**
- SL: ATR × 2.0 (varies by market conditions)
- TP: SL × reward_ratio × tp_level (scales with SL)

## Step-by-Step Setup

### For Pip-Based (Most Common)

1. **Set Stop Loss Method**
   - Click dropdown
   - Select "Pip-Based (Fixed distance)"
   - Input field appears below

2. **Set Stop Loss Pips**
   - Enter desired pip distance (e.g., 50)
   - Range: 10-500 pips

3. **Set Take Profit Method**
   - Click dropdown
   - Select "Pip-Based (Fixed distance)"
   - Input field appears below

4. **Set Take Profit Base Pips**
   - Enter desired pip distance (e.g., 100)
   - Range: 20-1000 pips
   - Must be greater than SL pips

5. **Check Status**
   - Should show green "✓ Methods Consistent"
   - Should display calculated pip distances

6. **Save Configuration**
   - Scroll to bottom
   - Click "Save Configuration"
   - Wait for success message

7. **Restart Bot**
   - Stop bot if running
   - Start bot again
   - New settings will be applied

## Common Mistakes

### ❌ Mistake 1: Mixing Methods
```
Stop Loss Method: ATR-Based
Take Profit Method: Pip-Based
```
**Problem:** SL can be 200+ pips, TP only 100 pips = negative risk/reward

**Fix:** Set both to the same method

### ❌ Mistake 2: TP Less Than SL
```
Stop Loss (Pips): 100
Take Profit Base (Pips): 50
```
**Problem:** TP closer than SL = guaranteed losses

**Fix:** TP must be greater than SL (e.g., SL: 50, TP: 100)

### ❌ Mistake 3: Extreme Values
```
Stop Loss (Pips): 5
Take Profit Base (Pips): 2000
```
**Problem:** SL too tight, TP unrealistic

**Fix:** Use reasonable values (SL: 30-100, TP: 60-300)

## Validation Messages

### Success Messages
- ✓ "Configuration saved successfully"
- ✓ "Methods Consistent"

### Error Messages
- ❌ "TP and SL must use the same calculation method!"
- ❌ "SL pips must be between 10 and 500"
- ❌ "TP pips must be between 20 and 1000"
- ❌ "TP base must be greater than SL"

## Recommended Settings by Trading Style

### Conservative (Low Risk)
```
Stop Loss Method: Pip-Based
Stop Loss (Pips): 30
Take Profit Method: Pip-Based
Take Profit Base (Pips): 90
```
Result: 1:3 risk/reward minimum

### Balanced (Medium Risk)
```
Stop Loss Method: Pip-Based
Stop Loss (Pips): 50
Take Profit Method: Pip-Based
Take Profit Base (Pips): 100
```
Result: 1:2 risk/reward minimum

### Aggressive (High Risk)
```
Stop Loss Method: Pip-Based
Stop Loss (Pips): 80
Take Profit Method: Pip-Based
Take Profit Base (Pips): 160
```
Result: 1:2 risk/reward minimum, larger distances

### Scalping (Very Short Term)
```
Stop Loss Method: Pip-Based
Stop Loss (Pips): 15
Take Profit Method: Pip-Based
Take Profit Base (Pips): 30
```
Result: 1:2 risk/reward, tight stops

## FAQ

**Q: Can I use different methods for SL and TP?**
A: No! This causes SL > TP problems. Always use the same method for both.

**Q: What's the difference between pip-based and ATR-based?**
A: Pip-based uses fixed distances. ATR-based adapts to market volatility.

**Q: Which method is better?**
A: Pip-based is more predictable. ATR-based is more adaptive. Choose based on your strategy.

**Q: Do I need to restart the bot after changing settings?**
A: Yes, the bot needs to be restarted to apply new configuration.

**Q: What if I see a red warning?**
A: Change both methods to match (both pip-based or both ATR-based).

**Q: Can I change these settings while the bot is running?**
A: Yes, but changes won't apply until you restart the bot.

**Q: What are TP levels (1.5, 2.5, 4.0)?**
A: These multiply your base TP. With TP base 100: TP1=150, TP2=250, TP3=400 pips.

## Troubleshooting

### Problem: Can't save configuration
**Solution:** Check for red warning messages. Fix validation errors first.

### Problem: Settings not applying
**Solution:** Restart the bot after saving configuration.

### Problem: Dashboard not loading
**Solution:** Make sure dashboard is running: `python web_dashboard.py`

### Problem: Still seeing old behavior
**Solution:** 
1. Clear cache: `python clear_all_cache.py`
2. Restart dashboard
3. Restart bot

## Support

If you encounter issues:
1. Check the validation messages
2. Review this guide
3. Check `bot_config.json` for saved values
4. Run test: `python test_dashboard_tpsl_controls.py`

---

**Remember:** Always use the same calculation method for both SL and TP!
