# M5 Indicator Settings - Complete Optimization

## 📊 All Indicators Adjusted for M5 Timeframe

All indicators have been optimized for 5-minute trading. Here's what changed:

---

## 🎯 Core Indicators

### 1. Moving Averages ✅
**Purpose:** Trend identification and entry signals

| Setting | H1 (Before) | M5 (Now) | Reason |
|---------|-------------|----------|--------|
| Fast MA | 20 periods | **10 periods** | Faster response (50 min) |
| Slow MA | 50 periods | **20 periods** | Faster response (100 min) |
| MA Type | SMA | **EMA** | Better for lower timeframes |

**What this means:**
- Fast MA: 10 × 5min = 50 minutes of data
- Slow MA: 20 × 5min = 100 minutes of data
- EMA reacts faster to price changes than SMA

---

### 2. ATR (Average True Range) ✅
**Purpose:** Volatility measurement for stop loss and trailing

| Setting | H1 (Before) | M5 (Now) | Reason |
|---------|-------------|----------|--------|
| ATR Period | 14 periods | **14 periods** | Standard (70 min) |
| ATR Multiplier SL | 2.0× | **1.5×** | Tighter stops for M5 |

**What this means:**
- ATR Period: 14 × 5min = 70 minutes of volatility data
- Stop Loss: 1.5× ATR (tighter than H1's 2.0×)
- More responsive to M5 volatility

---

### 3. Adaptive Risk Indicators ✅
**Purpose:** Market condition analysis for intelligent risk adjustment

| Setting | H1 (Before) | M5 (Now) | Reason |
|---------|-------------|----------|--------|
| Trend Strength Period | 50 | **30** | Faster trend analysis |
| ADX Strong Trend | 25 | **20** | Lower threshold for M5 |
| ADX Ranging | 20 | **15** | Lower threshold for M5 |
| Trend Consistency | 70% | **65%** | More realistic for M5 |
| Volatility High | 1.3 | **1.2** | Lower threshold for M5 |
| Min Confidence | 60% | **55%** | Slightly lower for M5 |

**What this means:**
- Trend Strength: 30 × 5min = 150 minutes (2.5 hours)
- ADX thresholds lowered for M5 noise
- Confidence threshold slightly lower (more trades)

---

### 4. Trailing Stop Indicators ✅
**Purpose:** Protect profits and let winners run

| Setting | H1 (Before) | M5 (Now) | Reason |
|---------|-------------|----------|--------|
| Trail Activation | 1.5× ATR | **1.0× ATR** | Activate sooner |
| Trail Distance | 1.0× ATR | **0.8× ATR** | Trail closer |
| Trail Percent | 2.0% | **1.5%** | Tighter trailing |
| Breakeven Activation | 100 pips | **50 pips** | Faster breakeven |
| Breakeven Plus | 10 pips | **5 pips** | Smaller lock-in |
| Trail Start | 150 pips | **75 pips** | Start trailing sooner |

**What this means:**
- Trailing activates faster (1.0× ATR vs 1.5×)
- Trails closer to price (0.8× ATR vs 1.0×)
- Breakeven protection kicks in sooner

---

### 5. Trend Filter ✅
**Purpose:** Only trade in direction of higher timeframe trend

| Setting | H1 (Before) | M5 (Now) | Reason |
|---------|-------------|----------|--------|
| Trend Timeframe | H4 | **H1** | Use H1 trend for M5 |
| Trend MA Period | 200 | **50** | Faster trend detection |

**What this means:**
- M5 trades follow H1 trend (not H4)
- 50-period MA on H1 = 50 hours trend
- More responsive to trend changes

---

### 6. Take Profit Levels ✅
**Purpose:** Multiple profit targets for split orders

| Setting | H1 (Before) | M5 (Now) | Reason |
|---------|-------------|----------|--------|
| TP Level 1 | 1.5× risk | **1.2× risk** | Quicker first profit |
| TP Level 2 | 2.5× risk | **1.8× risk** | More realistic |
| TP Level 3 | 4.0× risk | **2.5× risk** | Achievable target |

**What this means:**
- More realistic targets for M5
- Easier to hit first TP (1.2× vs 1.5×)
- Still allows for good profits

---

### 7. Position Management ✅
**Purpose:** Control number of open trades

| Setting | H1 (Before) | M5 (Now) | Reason |
|---------|-------------|----------|--------|
| Max Total Trades | 5 | **8** | More activity on M5 |
| Max Per Symbol | 1 | **2** | Allow multiple entries |

**What this means:**
- Can have up to 8 trades open
- Up to 2 trades per symbol (XAUUSD, XAGUSD)
- More flexibility for M5 activity

---

## 📈 Complete Settings Summary

### Timeframe & Basics
```python
TIMEFRAME = mt5.TIMEFRAME_M5  # 5 minutes
UPDATE_INTERVAL = 30          # Check every 30 seconds
```

### Moving Averages
```python
FAST_MA_PERIOD = 10           # 50 minutes
SLOW_MA_PERIOD = 20           # 100 minutes
MA_TYPE = 'EMA'               # Exponential
```

### ATR & Stop Loss
```python
ATR_PERIOD = 14               # 70 minutes
ATR_MULTIPLIER_SL = 1.5       # Tighter stops
```

### Risk Management
```python
RISK_PERCENT = 0.5            # 0.5% per trade
REWARD_RATIO = 1.5            # 1:1.5 R:R
```

### Adaptive Risk
```python
TREND_STRENGTH_PERIOD = 30    # 150 minutes
ADX_STRONG_TREND = 20         # Lower threshold
ADX_RANGING = 15              # Lower threshold
TREND_CONSISTENCY_HIGH = 65   # 65%
VOLATILITY_HIGH = 1.2         # Lower threshold
MIN_TRADE_CONFIDENCE = 0.55   # 55%
```

### Trailing Stops
```python
TRAIL_ACTIVATION_ATR = 1.0    # Activate sooner
TRAIL_DISTANCE_ATR = 0.8      # Trail closer
TRAIL_PERCENT = 1.5           # 1.5%
BREAKEVEN_ACTIVATION_PIPS = 50  # Faster BE
```

### Take Profit Levels
```python
TP_LEVELS = [1.2, 1.8, 2.5]   # More realistic
PARTIAL_CLOSE_PERCENT = [40, 30, 30]
```

### Trade Management
```python
MAX_TRADES_TOTAL = 8          # More trades
MAX_TRADES_PER_SYMBOL = 2     # 2 per symbol
MAX_DAILY_TRADES = 30         # Daily limit
```

### Trend Filter
```python
TREND_TIMEFRAME = mt5.TIMEFRAME_H1  # H1 trend
TREND_MA_PERIOD = 50          # 50-period MA
```

---

## 🎯 Why These Changes?

### 1. Faster Response
- Lower timeframe = faster price action
- Indicators need to respond quicker
- Shorter periods = more responsive

### 2. Tighter Risk Control
- M5 has more noise
- Tighter stops prevent large losses
- Closer trailing protects profits

### 3. Realistic Targets
- Lower TP levels more achievable
- M5 moves are smaller than H1
- Better win rate with realistic targets

### 4. More Activity
- M5 generates more signals
- Higher trade limits accommodate this
- More opportunities to profit

### 5. Better Filtering
- Lower confidence threshold (55% vs 60%)
- Adjusted ADX thresholds for M5 noise
- H1 trend filter instead of H4

---

## 📊 Expected Behavior

### Signal Generation
- **Frequency:** Every 5-15 minutes
- **Quality:** 55%+ confidence required
- **Filtering:** H1 trend + adaptive risk

### Trade Execution
- **Entry:** When MA cross + confirmation
- **Stop Loss:** 1.5× ATR from entry
- **Take Profit:** 3 levels (1.2×, 1.8×, 2.5×)
- **Position Size:** 0.5% risk per trade

### Trade Management
- **Trailing:** Activates at 1.0× ATR profit
- **Breakeven:** Moves at 50 pips profit
- **Partial Close:** 40% at TP1, 30% at TP2, 30% at TP3
- **Max Trades:** 8 total, 2 per symbol

---

## 🧪 Testing the Indicators

### Test 1: Check Configuration
```bash
python check_timeframe.py
```

Expected output:
```
Timeframe: M5 (5 minutes)
Fast MA: 10 periods
Slow MA: 20 periods
ATR Period: 14 periods
```

### Test 2: Verify Indicators Calculate
```bash
python examples/quick_test.py
```

Should show:
- Current price
- Fast MA value (10-period EMA)
- Slow MA value (20-period EMA)
- Signal status

### Test 3: Check Adaptive Risk
```bash
python examples/adaptive_risk_demo.py
```

Should show:
- Trend strength analysis
- Volatility assessment
- Confidence score
- Risk adjustments

---

## ⚠️ Important Notes

### 1. All Indicators Work Together
- MAs identify trend
- ATR sets stop loss
- Adaptive risk adjusts parameters
- Trailing protects profits
- Trend filter confirms direction

### 2. Optimized for M5
- Every setting adjusted for 5-minute bars
- Tested ratios and thresholds
- Balanced for activity vs quality

### 3. Still Conservative
- 0.5% risk per trade (low)
- 55% confidence minimum (selective)
- Tight stops (1.5× ATR)
- Realistic targets (1.2-2.5×)

### 4. Monitor Performance
- Track win rate (target: 45-55%)
- Watch spread costs
- Verify indicators working
- Adjust if needed

---

## 🔧 Fine-Tuning (Advanced)

If you want to adjust further:

### More Trades
```python
MIN_TRADE_CONFIDENCE = 0.50  # Lower threshold
MAX_DAILY_TRADES = 50        # Higher limit
```

### Fewer Trades
```python
MIN_TRADE_CONFIDENCE = 0.60  # Higher threshold
MAX_DAILY_TRADES = 20        # Lower limit
```

### Tighter Stops
```python
ATR_MULTIPLIER_SL = 1.2      # Even tighter
TRAIL_DISTANCE_ATR = 0.6     # Trail very close
```

### Wider Stops
```python
ATR_MULTIPLIER_SL = 2.0      # Wider stops
TRAIL_DISTANCE_ATR = 1.0     # Trail further
```

---

## ✅ Verification Checklist

Before running the bot:

- [ ] Timeframe set to M5
- [ ] Fast MA = 10 periods
- [ ] Slow MA = 20 periods
- [ ] MA Type = EMA
- [ ] ATR Period = 14
- [ ] ATR Multiplier = 1.5
- [ ] Risk = 0.5%
- [ ] Reward = 1.5
- [ ] Trail Activation = 1.0× ATR
- [ ] Trail Distance = 0.8× ATR
- [ ] TP Levels = [1.2, 1.8, 2.5]
- [ ] Max Trades = 8
- [ ] Trend Filter = H1
- [ ] All indicators optimized ✅

---

## 🎯 Summary

**All indicators have been optimized for M5 trading:**

✅ Moving Averages: Faster (10/20 EMA)  
✅ ATR: Tighter stops (1.5×)  
✅ Adaptive Risk: Adjusted thresholds  
✅ Trailing: Sooner activation (1.0× ATR)  
✅ Take Profit: Realistic targets (1.2-2.5×)  
✅ Trend Filter: H1 instead of H4  
✅ Position Limits: Increased for M5  

**Your bot is now fully optimized for M5 timeframe trading!** 🚀

---

*Last Updated: January 27, 2026*  
*Timeframe: M5 (5 minutes)*  
*All Indicators: Optimized ✅*
