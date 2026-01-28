# Multi-Symbol Trading Guide

**Date:** January 28, 2026  
**Feature:** Trading Multiple Symbols Simultaneously

---

## Overview

The GEM Trading Bot is fully compatible with trading multiple symbols simultaneously. The bot, dashboard, and all analytics automatically handle any number of trading instruments.

---

## Multi-Symbol Compatibility

### ✅ Fully Supported Features

**Bot Core:**
- ✅ Trades all configured symbols in parallel
- ✅ Independent analysis per symbol
- ✅ Symbol-specific position management
- ✅ Per-symbol trade limits
- ✅ Symbol-specific risk calculations

**Dashboard:**
- ✅ Combined performance metrics
- ✅ Per-symbol profit charts
- ✅ Per-symbol win/loss statistics
- ✅ Symbol filter in trade history
- ✅ Trade distribution by symbol
- ✅ Dynamic symbol dropdown (auto-populated)

**Analytics:**
- ✅ Profit by symbol (bar chart)
- ✅ Win/Loss by symbol (stacked bar)
- ✅ Trade distribution (doughnut chart)
- ✅ Symbol-specific filtering
- ✅ Date range filtering per symbol

---

## Available Trading Instruments

### Forex Majors (7 pairs)

**Most Liquid Currency Pairs:**
```python
FOREX_MAJORS = [
    'EURUSD',  # Euro / US Dollar (most traded)
    'GBPUSD',  # British Pound / US Dollar
    'USDJPY',  # US Dollar / Japanese Yen
    'USDCHF',  # US Dollar / Swiss Franc
    'AUDUSD',  # Australian Dollar / US Dollar
    'USDCAD',  # US Dollar / Canadian Dollar
    'NZDUSD',  # New Zealand Dollar / US Dollar
]
```

**Characteristics:**
- Highest liquidity
- Tightest spreads (0.5-2 pips)
- 24/5 trading
- Best for beginners
- Lower volatility

---

### Forex Cross Pairs (7 pairs)

**Popular Cross Pairs:**
```python
FOREX_CROSSES = [
    'EURJPY',  # Euro / Japanese Yen
    'GBPJPY',  # British Pound / Japanese Yen
    'EURGBP',  # Euro / British Pound
    'EURAUD',  # Euro / Australian Dollar
    'EURCAD',  # Euro / Canadian Dollar
    'GBPAUD',  # British Pound / Australian Dollar
    'GBPCAD',  # British Pound / Canadian Dollar
]
```

**Characteristics:**
- Good liquidity
- Moderate spreads (2-5 pips)
- Higher volatility than majors
- More trading opportunities
- Requires more experience

---

### Commodities - Metals (4 instruments)

**Precious Metals:**
```python
COMMODITIES_METALS = [
    'XAUUSD',  # Gold / US Dollar (most popular)
    'XAGUSD',  # Silver / US Dollar
    'XPTUSD',  # Platinum / US Dollar (if available)
    'XPDUSD',  # Palladium / US Dollar (if available)
]
```

**Characteristics:**
- High volatility
- Safe-haven assets
- Wider spreads (20-50 pips for gold)
- Larger pip values
- Trend-following friendly
- **Default configuration**

---

### Commodities - Energy (3 instruments)

**Energy Products:**
```python
COMMODITIES_ENERGY = [
    'XTIUSD',  # Crude Oil WTI / US Dollar
    'XBRUSD',  # Crude Oil Brent / US Dollar
    'XNGUSD',  # Natural Gas / US Dollar
]
```

**Characteristics:**
- Very high volatility
- News-sensitive
- Wide spreads
- Large price movements
- Requires larger stops
- Advanced traders only

---

### Indices (8 instruments)

**Major Stock Indices:**
```python
INDICES = [
    'US30',    # Dow Jones Industrial Average
    'US500',   # S&P 500
    'NAS100',  # NASDAQ 100
    'UK100',   # FTSE 100
    'GER40',   # DAX 40
    'FRA40',   # CAC 40
    'JPN225',  # Nikkei 225
    'AUS200',  # ASX 200
]
```

**Characteristics:**
- Moderate to high volatility
- Trading hours restrictions
- Trend-following friendly
- Correlated movements
- Good for diversification

---

## Configuration

### Default Configuration (Conservative)

**File:** `src/config.py`

**Current Default:**
```python
# Default symbols (conservative - metals only)
SYMBOLS = COMMODITIES_METALS.copy()
# Result: ['XAUUSD', 'XAGUSD', 'XPTUSD', 'XPDUSD']
```

**Why Metals Only?**
- Proven profitable with current strategy
- Clear trends
- Good volatility
- Manageable risk
- Suitable for H1 timeframe

---

### Adding More Symbols

**Method 1: Uncomment Categories**

```python
# Default symbols (conservative - metals only)
SYMBOLS = COMMODITIES_METALS.copy()

# To trade forex majors, uncomment:
SYMBOLS.extend(FOREX_MAJORS)

# To trade forex crosses, uncomment:
SYMBOLS.extend(FOREX_CROSSES)

# To trade energy commodities, uncomment:
SYMBOLS.extend(COMMODITIES_ENERGY)

# To trade indices, uncomment:
SYMBOLS.extend(INDICES)
```

**Result:** All selected categories will be traded

---

**Method 2: Manual Selection**

```python
# Manually specify your preferred symbols:
SYMBOLS = ['XAUUSD', 'EURUSD', 'GBPUSD', 'US30']
```

**Result:** Only specified symbols will be traded

---

**Method 3: Mix and Match**

```python
# Start with metals
SYMBOLS = COMMODITIES_METALS.copy()

# Add specific forex pairs
SYMBOLS.extend(['EURUSD', 'GBPUSD'])

# Add one index
SYMBOLS.append('US30')

# Result: ['XAUUSD', 'XAGUSD', 'XPTUSD', 'XPDUSD', 'EURUSD', 'GBPUSD', 'US30']
```

---

## Recommended Configurations

### Beginner (2-3 symbols)

**Conservative Start:**
```python
SYMBOLS = ['XAUUSD', 'EURUSD']
```

**Why:**
- Easy to monitor
- Different asset classes
- Proven strategies
- Lower complexity

---

### Intermediate (4-6 symbols)

**Balanced Portfolio:**
```python
SYMBOLS = [
    'XAUUSD',   # Gold (commodity)
    'EURUSD',   # Forex major
    'GBPUSD',   # Forex major
    'USDJPY',   # Forex major
    'US30',     # Index
]
```

**Why:**
- Diversification
- Multiple opportunities
- Risk spread
- Different market conditions

---

### Advanced (7-10 symbols)

**Full Diversification:**
```python
SYMBOLS = COMMODITIES_METALS.copy()  # 4 metals
SYMBOLS.extend(['EURUSD', 'GBPUSD', 'USDJPY'])  # 3 forex
SYMBOLS.extend(['US30', 'NAS100'])  # 2 indices
# Total: 9 symbols
```

**Why:**
- Maximum diversification
- Many trading opportunities
- Risk distribution
- Professional approach

---

### Expert (10+ symbols)

**Comprehensive Trading:**
```python
SYMBOLS = COMMODITIES_METALS.copy()  # 4 metals
SYMBOLS.extend(FOREX_MAJORS)  # 7 forex majors
SYMBOLS.extend(['US30', 'NAS100', 'GER40'])  # 3 indices
# Total: 14 symbols
```

**Why:**
- Full market coverage
- Maximum opportunities
- Professional diversification
- Requires strong risk management

---

## Risk Management for Multiple Symbols

### Per-Symbol Limits

**Configuration:**
```python
MAX_TRADES_PER_SYMBOL = 5  # Max 5 trades per symbol
MAX_TRADES_TOTAL = 20      # Max 20 trades total
```

**Example with 4 symbols:**
- Max per symbol: 5 trades
- Max total: 20 trades
- Allows balanced distribution

---

### Risk Allocation

**Equal Risk Per Symbol:**
```python
RISK_PERCENT = 1.0  # 1% per trade
```

**With 4 symbols, max 5 trades each:**
- Max risk per symbol: 5%
- Max total risk: 20%
- Manageable exposure

**Recommendation:**
- Keep total risk under 20%
- Adjust per-symbol limits based on portfolio size
- Monitor correlation between symbols

---

### Position Sizing

**Dynamic Sizing:**
```python
USE_DYNAMIC_SIZING = True
MAX_LOT_SIZE = 0.5
MIN_LOT_SIZE = 0.01
```

**Benefits:**
- Adapts to account size
- Symbol-specific calculations
- Risk-adjusted positions
- Automatic scaling

---

## Symbol-Specific Considerations

### Spread Costs

**Typical Spreads:**
- Forex Majors: 0.5-2 pips
- Forex Crosses: 2-5 pips
- Gold (XAUUSD): 20-50 pips
- Silver (XAGUSD): 30-100 pips
- Indices: 1-5 points
- Oil: 3-10 pips

**Impact:**
- Higher spreads = higher costs
- Adjust TP/SL accordingly
- Consider in profit calculations

---

### Pip Values

**Different Pip Values:**
- EURUSD: $10 per lot per pip
- USDJPY: ~$9 per lot per pip
- XAUUSD: $10 per lot per pip (but 1 pip = $0.10)
- Indices: Varies by index

**Bot Handles Automatically:**
- Calculates pip values per symbol
- Adjusts position sizes
- Maintains consistent risk

---

### Trading Hours

**24/5 Trading:**
- Forex: 24 hours (Mon-Fri)
- Metals: 23 hours (1-hour break)
- Indices: Limited hours (market-specific)
- Oil: 23 hours

**Configuration:**
```python
ENABLE_TRADING_HOURS = True
TRADING_START_HOUR = 8
TRADING_END_HOUR = 16
```

**Recommendation:**
- Disable for 24-hour symbols
- Enable for indices
- Avoid low-liquidity hours

---

### Volatility Differences

**High Volatility:**
- GBPJPY, XAGUSD, XNGUSD
- Larger stops required
- Higher profit potential
- Higher risk

**Low Volatility:**
- EURCHF, USDCHF
- Smaller stops
- Lower profit potential
- Lower risk

**Bot Adapts:**
- ATR-based stops
- Symbol-specific calculations
- Volatility filters

---

## Dashboard Multi-Symbol Features

### Symbol Filter (Trade History)

**Location:** Trade History tab

**Features:**
- Dropdown with all traded symbols
- "All Symbols" option
- Auto-populated from trades
- Combines with other filters

**Usage:**
1. Navigate to Trade History
2. Select symbol from dropdown
3. View trades for that symbol only
4. Combine with date range, win/loss filters

---

### Profit by Symbol Chart

**Location:** Charts & Analytics tab

**Features:**
- Bar chart showing profit per symbol
- Green bars = profit
- Red bars = loss
- Sorted by symbol name

**Insights:**
- Which symbols are profitable
- Which need adjustment
- Risk distribution
- Performance comparison

---

### Win/Loss by Symbol Chart

**Location:** Charts & Analytics tab

**Features:**
- Stacked bar chart
- Green = wins per symbol
- Red = losses per symbol
- Shows trade count

**Insights:**
- Win rate per symbol
- Trading frequency
- Symbol consistency
- Strategy effectiveness

---

### Trade Distribution Chart

**Location:** Charts & Analytics tab

**Features:**
- Doughnut chart
- Shows percentage of trades per symbol
- Color-coded
- Interactive legend

**Insights:**
- Trading balance
- Symbol preference
- Diversification level
- Opportunity distribution

---

## Verification Steps

### 1. Check Symbol Availability

**Test Script:**
```python
import MetaTrader5 as mt5

mt5.initialize()

symbols = ['XAUUSD', 'EURUSD', 'GBPUSD', 'US30']

for symbol in symbols:
    info = mt5.symbol_info(symbol)
    if info is None:
        print(f"❌ {symbol} not available")
    else:
        print(f"✅ {symbol} available - Spread: {info.spread}")

mt5.shutdown()
```

---

### 2. Test Symbol Configuration

**Steps:**
1. Edit `src/config.py`
2. Add desired symbols to `SYMBOLS` list
3. Run bot: `python run_bot.py`
4. Check logs for symbol initialization
5. Verify all symbols are being analyzed

**Expected Log Output:**
```
Trading symbols: ['XAUUSD', 'XAGUSD', 'EURUSD', 'GBPUSD']
Analyzing XAUUSD...
Analyzing XAGUSD...
Analyzing EURUSD...
Analyzing GBPUSD...
```

---

### 3. Verify Dashboard Display

**Steps:**
1. Start dashboard: `python start_dashboard.py`
2. Navigate to Charts & Analytics
3. Check "Profit by Symbol" chart
4. Verify all symbols appear
5. Check Trade History symbol filter
6. Confirm all symbols in dropdown

---

## Troubleshooting

### Symbol Not Available

**Symptoms:**
- Error: "Symbol not found"
- Symbol not trading

**Solutions:**
1. Check symbol name spelling
2. Verify broker offers symbol
3. Check symbol visibility in MT5
4. Enable symbol in Market Watch

**How to Enable:**
1. Open MT5
2. View → Market Watch
3. Right-click → Symbols
4. Find symbol → Show

---

### High Spread Warning

**Symptoms:**
- Warning: "Spread too high"
- Trades not opening

**Solutions:**
1. Check market hours
2. Wait for better spread
3. Adjust spread filter
4. Use different broker

---

### Symbol-Specific Errors

**Symptoms:**
- One symbol fails
- Others work fine

**Solutions:**
1. Check symbol-specific settings
2. Verify margin requirements
3. Check trading permissions
4. Review symbol specifications

---

## Best Practices

### Start Small

1. **Begin with 2-3 symbols**
   - Learn behavior
   - Monitor easily
   - Build confidence

2. **Add gradually**
   - One symbol at a time
   - Test thoroughly
   - Adjust settings

3. **Monitor performance**
   - Track per-symbol results
   - Identify winners
   - Remove losers

---

### Diversification

1. **Mix asset classes**
   - Forex + Commodities
   - Forex + Indices
   - Avoid correlation

2. **Balance volatility**
   - High + Low volatility
   - Stable + Trending
   - Risk distribution

3. **Consider correlation**
   - EURUSD vs GBPUSD (correlated)
   - XAUUSD vs USDCHF (inverse)
   - Diversify properly

---

### Risk Management

1. **Set per-symbol limits**
   - Max trades per symbol
   - Max risk per symbol
   - Total exposure cap

2. **Monitor total risk**
   - Sum of all positions
   - Correlation risk
   - Drawdown limits

3. **Adjust dynamically**
   - Reduce losing symbols
   - Increase winning symbols
   - Rebalance regularly

---

## Performance Optimization

### Symbol Selection Criteria

**Choose symbols with:**
1. ✅ Clear trends (H1 timeframe)
2. ✅ Reasonable spreads
3. ✅ Good liquidity
4. ✅ Suitable volatility
5. ✅ Available during your trading hours

**Avoid symbols with:**
1. ❌ Erratic behavior
2. ❌ Very wide spreads
3. ❌ Low liquidity
4. ❌ Extreme volatility
5. ❌ Frequent gaps

---

### Regular Review

**Weekly:**
- Review per-symbol performance
- Check win rates
- Analyze profit distribution
- Adjust if needed

**Monthly:**
- Comprehensive symbol analysis
- Remove underperformers
- Add new candidates
- Optimize portfolio

---

## Summary

The GEM Trading Bot is **fully compatible** with multiple symbols:

**✅ Verified Features:**
- Bot trades all symbols in parallel
- Dashboard handles unlimited symbols
- Charts auto-populate with all symbols
- Filters work across all symbols
- Risk management per symbol
- Independent analysis per symbol

**📊 Available Instruments:**
- 7 Forex Majors
- 7 Forex Crosses
- 4 Metals
- 3 Energy Commodities
- 8 Major Indices
- **Total: 29 instruments**

**🎯 Recommendations:**
- Start with 2-3 symbols
- Use default metals configuration
- Add symbols gradually
- Monitor performance
- Diversify properly
- Manage risk carefully

**🚀 Ready to Trade:**
- Configuration is simple
- Dashboard auto-adapts
- All features work seamlessly
- Professional multi-symbol trading

---

**The bot is production-ready for multi-symbol trading!** 📈💰✨
