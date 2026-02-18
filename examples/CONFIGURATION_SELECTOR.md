# Configuration Selector - Choose the Right Setup

This guide helps you select the appropriate configuration based on your trading profile, capital, and experience level.

## Quick Decision Tree

```
START HERE
    |
    ├─ How much capital do you have?
    |   |
    |   ├─ Less than ₹1,00,000
    |   |   └─> Use: config_equity_intraday.json
    |   |       (Start with 1-2 stocks, small position sizes)
    |   |
    |   ├─ ₹1,00,000 - ₹2,00,000
    |   |   └─> Choose based on experience:
    |   |       ├─ Beginner: config_equity_intraday.json
    |   |       └─ Experienced: config_options_trading.json
    |   |
    |   ├─ ₹2,00,000 - ₹5,00,000
    |   |   └─> Choose based on risk tolerance:
    |   |       ├─ Conservative: config_nifty_futures.json
    |   |       ├─ Moderate: config_equity_intraday.json (multiple stocks)
    |   |       └─ Aggressive: config_options_trading.json
    |   |
    |   └─ More than ₹5,00,000
    |       └─> Choose based on trading style:
    |           ├─ Stable returns: config_nifty_futures.json
    |           ├─ Active trading: config_banknifty_futures.json
    |           ├─ Diversified: config_equity_intraday.json
    |           └─ High risk/reward: config_options_trading.json
    |
    └─ What's your experience level?
        |
        ├─ Beginner (< 6 months)
        |   └─> Recommended: config_nifty_futures.json
        |       - Start with paper trading
        |       - Use 0.5% risk per trade
        |       - Focus on learning
        |
        ├─ Intermediate (6 months - 2 years)
        |   └─> Choose based on preference:
        |       ├─ Index trading: config_nifty_futures.json
        |       ├─ Stock trading: config_equity_intraday.json
        |       └─ Active trading: config_banknifty_futures.json
        |
        └─ Advanced (2+ years)
            └─> Any configuration based on strategy:
                ├─ Conservative: config_nifty_futures.json
                ├─ Aggressive: config_banknifty_futures.json
                ├─ Diversified: config_equity_intraday.json
                └─ Speculative: config_options_trading.json
```

---

## Profile-Based Recommendations

### Profile 1: Conservative Beginner
**Capital:** ₹2,00,000 - ₹5,00,000  
**Experience:** < 6 months  
**Risk Tolerance:** Low  
**Time Available:** 2-3 hours/day

**Recommended Configuration:** `config_nifty_futures.json`

**Modifications:**
```json
{
  "risk_percent": 0.5,              // Start very conservative
  "max_positions": 1,               // One position at a time
  "max_trades_per_day": 3,          // Limit daily trades
  "timeframe": 30,                  // Stick with 30-minute
  "use_adaptive_risk": true,        // Let bot adjust risk
  "paper_trading": true             // Start with paper trading
}
```

**Expected Results:**
- Win Rate: 45-55%
- Monthly Return: 3-5%
- Drawdown: 2-4%
- Trades/Day: 1-3

---

### Profile 2: Active Intermediate Trader
**Capital:** ₹3,00,000 - ₹7,00,000  
**Experience:** 1-2 years  
**Risk Tolerance:** Medium-High  
**Time Available:** 4-6 hours/day

**Recommended Configuration:** `config_banknifty_futures.json`

**Modifications:**
```json
{
  "risk_percent": 1.0,              // Standard risk
  "max_positions": 1,               // Focus on one good trade
  "max_trades_per_day": 5,          // Active but controlled
  "timeframe": 15,                  // Good for BANKNIFTY
  "trail_activation": 1.5,          // Tighter trailing
  "use_volume_filter": true         // Ensure liquidity
}
```

**Expected Results:**
- Win Rate: 40-50%
- Monthly Return: 8-12%
- Drawdown: 5-8%
- Trades/Day: 3-5

---

### Profile 3: Diversified Stock Trader
**Capital:** ₹1,00,000 - ₹3,00,000  
**Experience:** 6 months - 2 years  
**Risk Tolerance:** Medium  
**Time Available:** 3-5 hours/day

**Recommended Configuration:** `config_equity_intraday.json`

**Modifications:**
```json
{
  "symbols": ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"],
  "risk_percent": 1.0,              // 1% per stock
  "max_positions": 3,               // Diversify across 3 stocks
  "max_trades_per_day": 10,         // Multiple opportunities
  "timeframe": 5,                   // Active intraday
  "min_volume_ratio": 1.5,          // Ensure good liquidity
  "use_split_orders": true          // Book profits systematically
}
```

**Expected Results:**
- Win Rate: 45-55%
- Monthly Return: 6-10%
- Drawdown: 4-7%
- Trades/Day: 5-10

---

### Profile 4: Aggressive Options Trader
**Capital:** ₹1,50,000 - ₹3,00,000  
**Experience:** 2+ years  
**Risk Tolerance:** High  
**Time Available:** Full day monitoring

**Recommended Configuration:** `config_options_trading.json`

**Modifications:**
```json
{
  "symbols": [
    "NIFTY24JAN21000CE",
    "NIFTY24JAN21000PE"
  ],
  "risk_percent": 2.0,              // Higher risk for options
  "reward_ratio": 1.5,              // Quick profit targets
  "max_positions": 2,               // CE and PE
  "max_trades_per_day": 8,          // Active options trading
  "timeframe": 5,                   // Fast moves
  "trail_activation": 1.0,          // Quick trailing
  "trail_distance": 0.5,            // Tight trailing
  "tp_levels": [1.0, 1.5],         // Quick exits
  "partial_close_percent": [70, 30] // Book most at first TP
}
```

**Expected Results:**
- Win Rate: 35-45%
- Monthly Return: 15-25%
- Drawdown: 10-15%
- Trades/Day: 5-10

---

### Profile 5: Part-Time Trader
**Capital:** ₹1,00,000 - ₹2,00,000  
**Experience:** Any  
**Risk Tolerance:** Low-Medium  
**Time Available:** 1-2 hours/day

**Recommended Configuration:** `config_nifty_futures.json`

**Modifications:**
```json
{
  "risk_percent": 0.75,             // Conservative
  "max_positions": 1,               // Simple management
  "max_trades_per_day": 2,          // Limited time
  "timeframe": 60,                  // Longer timeframe
  "use_split_orders": false,        // Simpler exits
  "trading_hours": {
    "start": "09:30",               // Skip opening volatility
    "end": "11:30"                  // Trade only morning
  }
}
```

**Expected Results:**
- Win Rate: 50-60%
- Monthly Return: 3-6%
- Drawdown: 2-3%
- Trades/Day: 1-2

---

## Capital Allocation Guide

### Small Capital (< ₹1,00,000)

**Best Choice:** Equity Intraday

**Allocation Strategy:**
```
Total Capital: ₹75,000
├─ Trading Capital: ₹50,000 (67%)
├─ Reserve/Margin: ₹20,000 (27%)
└─ Emergency Buffer: ₹5,000 (6%)

Per Trade Risk: ₹500 (1% of ₹50,000)
Max Positions: 2-3 stocks
Position Size: ₹15,000-20,000 per stock
```

**Recommended Stocks:**
- RELIANCE (high liquidity)
- TCS (stable moves)
- INFY (good volume)

---

### Medium Capital (₹1,00,000 - ₹3,00,000)

**Best Choice:** Equity Intraday or NIFTY Futures

**Allocation Strategy:**
```
Total Capital: ₹2,00,000
├─ Trading Capital: ₹1,50,000 (75%)
├─ Reserve/Margin: ₹40,000 (20%)
└─ Emergency Buffer: ₹10,000 (5%)

Per Trade Risk: ₹1,500 (1% of ₹1,50,000)
Max Positions: 2-3
Position Size: ₹50,000-75,000 per position
```

**Options:**
1. **NIFTY Futures:** 1 lot (₹1,00,000 margin)
2. **Equity:** 3-4 stocks (₹40,000-50,000 each)
3. **Mix:** 1 NIFTY lot + 2 equity stocks

---

### Large Capital (₹3,00,000 - ₹10,00,000)

**Best Choice:** BANKNIFTY Futures or Diversified Portfolio

**Allocation Strategy:**
```
Total Capital: ₹5,00,000
├─ Trading Capital: ₹4,00,000 (80%)
├─ Reserve/Margin: ₹80,000 (16%)
└─ Emergency Buffer: ₹20,000 (4%)

Per Trade Risk: ₹4,000 (1% of ₹4,00,000)
Max Positions: 3-4
Position Size: ₹1,00,000-1,50,000 per position
```

**Portfolio Options:**

**Option A: Futures Focus**
- 2 NIFTY lots (₹2,00,000)
- 1 BANKNIFTY lot (₹1,50,000)
- Reserve: ₹1,50,000

**Option B: Diversified**
- 1 NIFTY lot (₹1,00,000)
- 5 equity stocks (₹40,000 each)
- Reserve: ₹1,00,000

**Option C: Options Trading**
- 4-6 option positions (₹50,000-80,000 each)
- Reserve: ₹1,50,000

---

## Risk Level Selector

### Conservative (Preserve Capital)
```json
{
  "risk_percent": 0.5,
  "reward_ratio": 2.5,
  "max_daily_loss_percent": 2.0,
  "max_drawdown_percent": 5.0,
  "atr_multiplier": 2.5,
  "adx_threshold": 30,
  "use_adaptive_risk": true
}
```
**Target:** 3-5% monthly return, <3% drawdown

---

### Moderate (Balanced Approach)
```json
{
  "risk_percent": 1.0,
  "reward_ratio": 2.0,
  "max_daily_loss_percent": 3.0,
  "max_drawdown_percent": 8.0,
  "atr_multiplier": 2.0,
  "adx_threshold": 25,
  "use_adaptive_risk": true
}
```
**Target:** 6-10% monthly return, 4-7% drawdown

---

### Aggressive (Growth Focus)
```json
{
  "risk_percent": 2.0,
  "reward_ratio": 1.5,
  "max_daily_loss_percent": 5.0,
  "max_drawdown_percent": 12.0,
  "atr_multiplier": 1.5,
  "adx_threshold": 20,
  "use_adaptive_risk": true
}
```
**Target:** 12-20% monthly return, 8-15% drawdown

---

## Time Availability Guide

### Full-Time Monitoring (6+ hours)
**Best Configurations:**
- BANKNIFTY Futures (15-min)
- Options Trading (5-min)
- Multiple Equity Stocks (5-min)

**Settings:**
```json
{
  "timeframe": 5,
  "max_trades_per_day": 10,
  "max_positions": 4
}
```

---

### Part-Time Monitoring (2-4 hours)
**Best Configurations:**
- NIFTY Futures (30-min)
- Equity Intraday (15-min)

**Settings:**
```json
{
  "timeframe": 30,
  "max_trades_per_day": 5,
  "max_positions": 2,
  "trading_hours": {
    "start": "09:30",
    "end": "12:00"
  }
}
```

---

### Minimal Monitoring (1-2 hours)
**Best Configurations:**
- NIFTY Futures (60-min)

**Settings:**
```json
{
  "timeframe": 60,
  "max_trades_per_day": 2,
  "max_positions": 1,
  "use_split_orders": false
}
```

---

## Configuration Testing Checklist

Before going live with any configuration:

- [ ] Tested in paper trading mode for minimum 5 days
- [ ] Win rate is acceptable (>40%)
- [ ] Drawdown is within tolerance
- [ ] Signals are generated regularly
- [ ] Stop losses are not too tight (frequent stop-outs)
- [ ] Capital allocation is appropriate
- [ ] Risk per trade is comfortable
- [ ] Timeframe matches monitoring availability
- [ ] Symbols are current (not expired)
- [ ] API credentials are configured
- [ ] Daily authentication is working
- [ ] Margin requirements are understood
- [ ] Emergency stop procedures are clear

---

## Common Questions

### Q: Can I mix configurations?
**A:** Yes! You can run multiple bots with different configs:
```bash
# Terminal 1: NIFTY Futures
python run_bot.py --config config_nifty_futures.json

# Terminal 2: Equity Intraday
python run_bot.py --config config_equity_intraday.json
```

### Q: How do I know if my configuration is working?
**A:** Track these metrics:
- Win rate should be >40%
- Profit factor should be >1.5
- Max drawdown should be <10%
- Signals should generate regularly

### Q: When should I change my configuration?
**A:** Consider changing if:
- Consistent losses for 2+ weeks
- Win rate drops below 35%
- Drawdown exceeds limits
- Market conditions change significantly

### Q: Can I automate configuration selection?
**A:** Not yet, but you can:
- Use adaptive risk (adjusts automatically)
- Monitor performance metrics
- Switch configs based on market volatility

---

## Next Steps

1. **Choose your configuration** based on this guide
2. **Copy the config file** to `my_config.json`
3. **Modify parameters** to match your profile
4. **Test in paper trading** for 5-7 days
5. **Review results** and adjust if needed
6. **Go live** with small position sizes
7. **Scale up gradually** as you gain confidence

---

**Remember:** The best configuration is one that:
- Matches your capital
- Fits your risk tolerance
- Suits your time availability
- Aligns with your experience level
- Generates consistent results

Start conservative, test thoroughly, and scale up gradually!
