# Symbol Selection Quick Guide

**Quick reference for selecting trading symbols in the dashboard**

---

## Where to Find It

1. Open dashboard: http://localhost:5000
2. Click **Configuration** tab
3. Look for **"Trading Symbols"** dropdown (first setting)

---

## What You'll See

### Symbol Dropdown (29 symbols organized by category)

```
┌─────────────────────────────────────────┐
│ Trading Symbols                    [▼]  │
├─────────────────────────────────────────┤
│ 💰 Commodities - Metals                 │
│   ☑ XAUUSD (Gold)          ← Selected   │
│   ☑ XAGUSD (Silver)        ← Selected   │
│   ☐ XPTUSD (Platinum)                   │
│   ☐ XPDUSD (Palladium)                  │
│                                         │
│ 💱 Forex Majors                         │
│   ☐ EURUSD (Euro/USD)                   │
│   ☐ GBPUSD (Pound/USD)                  │
│   ☐ USDJPY (USD/Yen)                    │
│   ☐ USDCHF (USD/Franc)                  │
│   ☐ AUDUSD (Aussie/USD)                 │
│   ☐ USDCAD (USD/CAD)                    │
│   ☐ NZDUSD (Kiwi/USD)                   │
│                                         │
│ 💱 Forex Crosses                        │
│   ☐ EURJPY (Euro/Yen)                   │
│   ☐ GBPJPY (Pound/Yen)                  │
│   ☐ EURGBP (Euro/Pound)                 │
│   ☐ EURAUD (Euro/Aussie)                │
│   ☐ EURCAD (Euro/CAD)                   │
│   ☐ GBPAUD (Pound/Aussie)               │
│   ☐ GBPCAD (Pound/CAD)                  │
│                                         │
│ ⚡ Commodities - Energy                 │
│   ☐ XTIUSD (Crude Oil WTI)              │
│   ☐ XBRUSD (Crude Oil Brent)            │
│   ☐ XNGUSD (Natural Gas)                │
│                                         │
│ 📊 Indices                              │
│   ☐ US30 (Dow Jones)                    │
│   ☐ US500 (S&P 500)                     │
│   ☐ NAS100 (NASDAQ)                     │
│   ☐ UK100 (FTSE 100)                    │
│   ☐ GER40 (DAX 40)                      │
│   ☐ FRA40 (CAC 40)                      │
│   ☐ JPN225 (Nikkei)                     │
│   ☐ AUS200 (ASX 200)                    │
└─────────────────────────────────────────┘
Hold Ctrl/Cmd to select multiple
Default: Gold & Silver

[Metals Only] [+ Forex Majors] [Select All] [Clear All]
```

---

## Quick Selection Buttons

### 🥇 Metals Only (Recommended for Beginners)

**Click this button to select:**
- ✅ XAUUSD (Gold)
- ✅ XAGUSD (Silver)
- ✅ XPTUSD (Platinum)
- ✅ XPDUSD (Palladium)

**Total:** 4 symbols  
**Risk Level:** Conservative  
**Best for:** Beginners, proven strategy

---

### 💱 + Forex Majors (Recommended for Intermediate)

**Click this button to select:**
- ✅ All 4 metals (above)
- ✅ EURUSD (Euro/USD)
- ✅ GBPUSD (Pound/USD)
- ✅ USDJPY (USD/Yen)
- ✅ USDCHF (USD/Franc)
- ✅ AUDUSD (Aussie/USD)
- ✅ USDCAD (USD/CAD)
- ✅ NZDUSD (Kiwi/USD)

**Total:** 11 symbols  
**Risk Level:** Balanced  
**Best for:** Intermediate traders, diversification

---

### 🌐 Select All (Advanced)

**Click this button to select:**
- ✅ All 29 symbols

**Total:** 29 symbols  
**Risk Level:** Advanced  
**Best for:** Experienced traders with strong risk management

---

### ❌ Clear All

**Click this button to:**
- Deselect all symbols
- Start fresh
- Then manually pick symbols

---

## Manual Selection

### How to Select Multiple Symbols

**Windows:**
1. Hold **Ctrl** key
2. Click each symbol you want
3. Selected symbols will be highlighted

**Mac:**
1. Hold **Cmd** (⌘) key
2. Click each symbol you want
3. Selected symbols will be highlighted

**Example:**
```
Want to trade Gold, Euro, and Dow Jones?

1. Hold Ctrl/Cmd
2. Click "XAUUSD (Gold)"
3. Still holding Ctrl/Cmd, click "EURUSD (Euro/USD)"
4. Still holding Ctrl/Cmd, click "US30 (Dow Jones)"
5. Release Ctrl/Cmd
6. Scroll down and click "Save Configuration"
```

---

## Recommended Configurations

### 🟢 Conservative (Beginner)

**Symbols:** 2-4 symbols  
**Selection:** Metals Only  
**Example:**
```
✅ XAUUSD (Gold)
✅ XAGUSD (Silver)
```

**Why:**
- Proven profitable
- Easy to monitor
- Lower complexity
- Good for learning

---

### 🟡 Balanced (Intermediate)

**Symbols:** 5-10 symbols  
**Selection:** Metals + Forex Majors  
**Example:**
```
✅ XAUUSD (Gold)
✅ XAGUSD (Silver)
✅ EURUSD (Euro/USD)
✅ GBPUSD (Pound/USD)
✅ USDJPY (USD/Yen)
```

**Why:**
- Good diversification
- Multiple opportunities
- Different asset classes
- Professional approach

---

### 🔴 Advanced (Expert)

**Symbols:** 10-20 symbols  
**Selection:** Custom mix  
**Example:**
```
✅ XAUUSD, XAGUSD (Metals)
✅ EURUSD, GBPUSD, USDJPY (Forex Majors)
✅ EURJPY, GBPJPY (Forex Crosses)
✅ US30, NAS100 (Indices)
```

**Why:**
- Maximum diversification
- Many opportunities
- Full market coverage
- Requires strong risk management

---

## After Selection

### Save Your Configuration

1. Scroll to bottom of Configuration page
2. Click **"Save Configuration"** button
3. Wait for success message
4. Bot will restart with new symbols

### Verify It Worked

1. Check **Dashboard** tab
2. Look at **"Trading Symbols"** in Bot Status
3. Should show your selected symbols
4. Charts will update with new symbols

---

## Tips

### ✅ Do's

- ✅ Start with 2-4 symbols
- ✅ Use "Metals Only" if unsure
- ✅ Add symbols gradually
- ✅ Monitor performance per symbol
- ✅ Verify symbols with your broker

### ❌ Don'ts

- ❌ Don't select all 29 symbols immediately
- ❌ Don't trade symbols you don't understand
- ❌ Don't ignore risk management
- ❌ Don't forget to save configuration
- ❌ Don't trade unavailable symbols

---

## Verify Symbol Availability

**Before selecting symbols, verify they're available:**

```bash
python verify_symbols.py
```

**This will show:**
- ✅ Which symbols your broker offers
- 📊 Current spreads
- 💰 Current prices
- 📋 Recommended configuration

---

## Troubleshooting

### Can't See All Symbols?

**Solution:** Scroll down in the dropdown - it shows 8 symbols at a time

### Selection Not Working?

**Solution:** Make sure you're holding Ctrl (Windows) or Cmd (Mac)

### Symbols Not Trading?

**Solution:** 
1. Run `verify_symbols.py` to check availability
2. Enable symbols in MT5 Market Watch
3. Check account balance for margin

---

## Quick Reference

| Button | Symbols | Count | Level |
|--------|---------|-------|-------|
| Metals Only | Gold, Silver, Platinum, Palladium | 4 | Beginner |
| + Forex Majors | Metals + 7 Forex pairs | 11 | Intermediate |
| Select All | All available symbols | 29 | Advanced |
| Clear All | None | 0 | Manual |

---

## Summary

**29 symbols available:**
- 4 Metals (Gold, Silver, Platinum, Palladium)
- 7 Forex Majors (EUR, GBP, JPY, CHF, AUD, CAD, NZD)
- 7 Forex Crosses (EURJPY, GBPJPY, etc.)
- 3 Energy (Oil WTI, Oil Brent, Natural Gas)
- 8 Indices (Dow, S&P, NASDAQ, etc.)

**Quick selection:**
- Click button for instant selection
- Or manually pick with Ctrl/Cmd + Click
- Save configuration when done

**Default:** Gold & Silver (Conservative)

---

**Now go to the Configuration tab and select your trading symbols!** 🚀
