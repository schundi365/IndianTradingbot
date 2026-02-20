# Deployment Instructions - Full Strategy Recommendations

## What Was Fixed

### 1. Strategy Recommendations Panel
- Replaced simple test version with full recommendations module
- Now shows complete technical indicators, risk management, and trading tips for each strategy
- Removed duplicate inline script that was causing confusion

### 2. Monitor Tab 404 Errors
- Added detailed logging to diagnose Paper Trading connection issues
- Logs will show exactly where the connection chain breaks

## How to Deploy

### Step 1: Restart Dashboard

Run the restart script:
```powershell
.\restart_dashboard.ps1
```

This will:
- Stop any running Flask processes
- Start the dashboard in a new window
- Dashboard will be available at http://127.0.0.1:8080

### Step 2: Clear Browser Cache

IMPORTANT: You MUST clear browser cache to see the changes!

Option A - Incognito Mode (Recommended):
- Press Ctrl+Shift+N to open incognito window
- Go to http://127.0.0.1:8080
- No cache issues!

Option B - Clear Cache:
- Press Ctrl+Shift+Delete
- Select "Cached images and files"
- Select "All time"
- Click "Clear data"
- Refresh the page (F5)

### Step 3: Test Strategy Recommendations

1. Go to Configuration tab
2. Select a strategy from the dropdown:
   - Breakout
   - Mean Reversion
   - Trend Following
   - Scalping

3. You should see a comprehensive panel with:
   - 📊 Technical Indicators (10 indicators with values, ranges, descriptions)
   - 🛡️ Risk Management (4 parameters with recommendations)
   - 💭 Trading Tips (4-5 specific tips per strategy)
   - ✨ Apply Recommended Settings button
   - ✕ Close button

### Step 4: Check Monitor Tab (Paper Trading)

1. Connect to Paper Trading (if not already connected)
2. Go to Monitor tab
3. Check browser console (F12) for any errors
4. Check dashboard logs for detailed diagnostic information:
   - Look for "=== GET ACCOUNT INFO REQUEST ===" messages
   - Will show broker connection status, adapter type, etc.

## What You Should See

### Strategy Recommendations Example (Mean Reversion)

```
💡 Mean Reversion Strategy - Recommended Settings
Trades price returns to average after extreme moves

📊 Technical Indicators
┌─────────────────────┬────────┬──────────┬────────────────────────────┐
│ RSI Period          │ 14     │ 10-20    │ Overbought/oversold detect │
│ RSI Overbought      │ 75     │ 70-80    │ Extreme overbought         │
│ RSI Oversold        │ 25     │ 20-30    │ Extreme oversold           │
│ MACD Fast           │ 12     │ 10-15    │ Divergence detection       │
│ MACD Slow           │ 26     │ 20-30    │ Trend baseline             │
│ MACD Signal         │ 9      │ 7-12     │ Reversal signal            │
│ ADX Period          │ 14     │ 10-20    │ Avoid strong trends        │
│ ADX Threshold       │ 20     │ 15-25    │ Trade in ranging markets   │
│ Bollinger Period    │ 20     │ 15-25    │ Mean reversion bands       │
│ Bollinger Std Dev   │ 2.0    │ 2.0-2.5  │ Wider bands for extremes   │
└─────────────────────┴────────┴──────────┴────────────────────────────┘

🛡️ Risk Management
┌─────────────────────┬────────────┬──────────┬────────────────────────┐
│ Take Profit         │ 1.5        │ 1.0-2.0  │ Quick profits          │
│ Stop Loss           │ 1.0        │ 0.8-1.2  │ Tight stops            │
│ Position Sizing     │ percentage │          │ Fixed percentage       │
│ Max Positions       │ 5          │ 3-7      │ More trades in ranging │
└─────────────────────┴────────────┴──────────┴────────────────────────┘

💭 Trading Tips
• Trade when ADX < 20 (ranging market)
• Enter when price touches Bollinger Bands
• Exit when price returns to middle band
• Avoid trading during strong trends

[✨ Apply Recommended Settings]  [✕ Close]
```

## Troubleshooting

### Recommendations Not Showing
1. Clear browser cache completely (Ctrl+Shift+Delete → All time)
2. Try incognito mode (Ctrl+Shift+N)
3. Check browser console (F12) for JavaScript errors
4. Verify files exist:
   - `indian_dashboard/static/js/strategy-recommendations.js`
   - `indian_dashboard/static/css/strategy-recommendations.css`

### Monitor Tab 404 Errors
1. Check dashboard logs for diagnostic messages
2. Look for "=== GET ACCOUNT INFO REQUEST ===" entries
3. Verify broker_manager shows as connected
4. Check if adapter.is_connected() returns True
5. Share the log output for further diagnosis

### Still Seeing Test Message
If you still see "✅ Recommendations panel is working!" instead of full recommendations:
1. Hard refresh: Ctrl+F5
2. Clear cache again
3. Close all browser windows and reopen
4. Try different browser

## Files Modified

1. `indian_dashboard/templates/dashboard.html`
   - Changed script include from `strategy-recommendations-simple.js` to `strategy-recommendations.js`
   - Removed inline test script

2. `indian_dashboard/api/bot.py`
   - Added detailed logging to `/api/bot/account` endpoint
   - Helps diagnose Paper Trading connection issues

## Verification

Run this command to verify deployment:
```powershell
# Check script include
Select-String -Path "indian_dashboard/templates/dashboard.html" -Pattern "strategy-recommendations.js"

# Should show: strategy-recommendations.js (NOT strategy-recommendations-simple.js)
```

---

**Status**: ✅ Ready to deploy
**Next**: Run `.\restart_dashboard.ps1` and test!
