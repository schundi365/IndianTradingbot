# Configuration Quick Reference Card

## 🎯 Presets at a Glance

| Preset | Timeframe | Risk | Confidence | Trades/Day | Win Rate | Best For |
|--------|-----------|------|------------|------------|----------|----------|
| **Profitable Balanced** ✅ | H1 (1h) | 0.5% | 70% | 5-15 | 55-65% | Most traders |
| **Conservative** 🛡️ | H4 (4h) | 0.3% | 75% | 2-8 | 60-70% | Safety first |
| **Aggressive** ⚡ | M30 (30m) | 1.0% | 60% | 15-50 | 50-60% | Experienced |

## 📊 Parameter Categories (43 Total)

### Basic Settings (6)
```
✓ Symbols          - Which pairs to trade
✓ Timeframe        - Chart period (H1 recommended)
✓ Risk %           - Per trade risk (0.5% recommended)
✓ Reward Ratio     - Risk:Reward (2.0 recommended)
✓ Confidence       - Min signal quality (70% recommended)
✓ Max Daily Loss   - Stop trading at X% loss (3% recommended)
```

### Indicators (12)
```
📈 Moving Averages
   • Fast MA: 20 (short-term trend)
   • Slow MA: 50 (long-term trend)

📊 RSI (Momentum)
   • Period: 14
   • Overbought: 70 (don't buy above)
   • Oversold: 30 (don't sell below)

📉 MACD (Momentum)
   • Fast: 12
   • Slow: 26
   • Signal: 9
   • Min Histogram: 0.5 (strength)

📏 ATR (Volatility)
   • Period: 14
   • Multiplier: 2.0 (stop loss distance)

💪 ADX (Trend Strength)
   • Min: 25 (only trade when strong)
```

### Filters (9)
```
🛡️ Signal Filters
   • RSI Filter: ✓ Enabled
   • MACD Filter: ✓ Enabled
   • ADX Filter: ✓ Enabled
   • Trend Filter: ✓ Enabled (H4)

⏰ Time Filters
   • Trading Hours: 8:00 - 16:00 UTC
   • News Avoidance: 60 min buffer
```

### Position Management (10)
```
💼 Order Management
   • Split Orders: ✓ Enabled
   • Positions: 3 (multiple TPs)
   • TP1: 1.5R (40% close)
   • TP2: 2.5R (30% close)
   • TP3: 4.0R (30% close)

📊 Trade Limits
   • Max Total: 10 trades
   • Max Per Symbol: 3 trades

🎯 Trailing Stop
   • Activation: 1.5 ATR profit
   • Distance: 1.0 ATR behind
```

### Risk Management (5)
```
⚠️ Adaptive Risk
   • Enabled: ✓ Yes
   • Max Multiplier: 1.5x (good conditions)
   • Min Multiplier: 0.5x (bad conditions)

🚨 Safety Limits
   • Max Drawdown: 10%
   • Max Daily Trades: 20
```

## 🎨 Customization Workflow

```
1. SELECT PRESET
   ↓
2. EXPAND SECTIONS (optional)
   ↓
3. ADJUST PARAMETERS
   ↓
4. VALIDATE (automatic)
   ↓
5. SAVE CONFIGURATION
   ↓
6. TEST ON DEMO
   ↓
7. MONITOR & ADJUST
```

## ⚡ Quick Actions

### Change Risk Level
```
Conservative: 0.3%
Moderate:     0.5% ← Recommended
Aggressive:   1.0%
```

### Change Trade Frequency
```
Fewer Trades:  Increase confidence (70%+)
More Trades:   Decrease confidence (50-60%)
```

### Change Timeframe
```
Long-term:  H4, D1 (2-8 trades/day)
Medium:     H1 ← Recommended (5-15 trades/day)
Short-term: M30, M15 (15-50 trades/day)
```

## 🚨 Warning Thresholds

| Parameter | Safe | Warning | Danger |
|-----------|------|---------|--------|
| Risk % | ≤0.5% | 0.5-1% | >1% |
| Confidence | ≥70% | 50-70% | <50% |
| Daily Loss | ≤3% | 3-5% | >5% |
| Drawdown | ≤10% | 10-15% | >15% |
| ATR Mult | 1.5-2.5 | 1-1.5 or 2.5-3 | <1 or >3 |

## 💡 Pro Tips

### Tip #1: Start Conservative
```
✓ Use "Profitable Balanced" preset
✓ Don't change anything for 1 week
✓ Monitor on demo account
✓ Learn what each setting does
```

### Tip #2: One Change at a Time
```
✓ Adjust one parameter
✓ Test for 3-7 days
✓ Measure impact
✓ Keep or revert
```

### Tip #3: Match Your Style
```
Patient Trader:    Conservative preset
Balanced Trader:   Profitable preset
Active Trader:     Aggressive preset
```

### Tip #4: Market Conditions
```
Trending Market:   Enable trend filter
Ranging Market:    Increase confidence
Volatile Market:   Increase ATR multiplier
Quiet Market:      Decrease confidence
```

## 🔧 Common Adjustments

### Too Many Trades
```
→ Increase confidence (70% → 75%)
→ Enable more filters
→ Use higher timeframe (H1 → H4)
```

### Too Few Trades
```
→ Decrease confidence (70% → 60%)
→ Disable some filters
→ Use lower timeframe (H1 → M30)
```

### Losing Money
```
→ STOP TRADING
→ Switch to Conservative preset
→ Increase confidence to 75%+
→ Enable all filters
→ Test on demo
```

### Winning but Want More
```
→ Increase risk slightly (0.5% → 0.7%)
→ Add more symbols
→ Decrease confidence slightly (70% → 65%)
→ Test changes on demo first
```

## 📈 Performance Metrics to Track

```
✓ Win Rate (target: >55%)
✓ Average Win vs Average Loss (target: >2:1)
✓ Max Drawdown (target: <10%)
✓ Profit Factor (target: >1.5)
✓ Trades per Day (target: 5-15)
✓ Monthly Return (target: 5-15%)
```

## 🎯 Validation Rules

```
✓ Risk: 0.1% - 5%
✓ Confidence: 20% - 90%
✓ Fast MA < Slow MA
✓ RSI Oversold < Overbought
✓ MACD Fast < Slow
✓ TP1 < TP2 < TP3
✓ Min Risk Mult < Max Risk Mult
✓ At least 1 symbol selected
```

## 🚀 Getting Started Checklist

```
□ Open dashboard (http://localhost:5000)
□ Accept risk disclaimer
□ Select "Profitable Balanced" preset
□ Review all settings
□ Click "Save Configuration"
□ Test MT5 connection
□ Start bot on DEMO account
□ Monitor for 1 week
□ Review performance
□ Adjust if needed
□ Only then go LIVE
```

## 📞 Need Help?

```
Dashboard Issues:  Check Logs tab
Config Questions:  Read DASHBOARD_CONFIGURATION_GUIDE.md
Trading Help:      Check AI Recommendations tab
Technical Support: Review TROUBLESHOOTING.md
```

## 🎓 Learning Path

```
Week 1: Use default "Profitable Balanced"
Week 2: Learn what each indicator does
Week 3: Make small adjustments
Week 4: Test different timeframes
Week 5: Optimize for your style
Week 6: Fine-tune risk management
```

---

## 🌟 Golden Rules

1. **Always test on demo first** 🎮
2. **Keep risk low (≤0.5%)** 💰
3. **One change at a time** 🔧
4. **Monitor daily** 👀
5. **Be patient** ⏰

---

**Print this card and keep it handy!** 📄

Last Updated: January 28, 2026
Version: 2.0
