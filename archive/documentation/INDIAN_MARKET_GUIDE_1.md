# 🇮🇳 Indian Stock Market Trading Bot - MT5 Alternatives

## 📊 PLATFORMS FOR ALGO TRADING IN INDIA

### ⭐ Top 3 Recommendations (Best to Worst)

---

## 1. 🥇 ZERODHA KITE CONNECT (BEST OPTION)

### Why This Is The Best:
- ✅ **Most popular** - 60%+ Indian retail traders use Zerodha
- ✅ **Official API** - Kite Connect API for algo trading
- ✅ **Python support** - Full Python library (`kiteconnect`)
- ✅ **Low cost** - ₹2,000/month API fees (₹24,000/year)
- ✅ **NSE/BSE** - Trade stocks, F&O, commodities, currency
- ✅ **Great documentation** - Excellent tutorials and examples
- ✅ **WebSocket support** - Real-time data streaming
- ✅ **Backtesting** - Can use historical data

### What You Get:
- Stock trading (NSE/BSE)
- Futures & Options
- Currency derivatives
- Commodities (MCX)
- Real-time market data
- Historical data API
- Order management API

### Pricing:
```
Brokerage: ₹0 for delivery, ₹20 per order for intraday/F&O
API charges: ₹2,000/month
Account opening: ₹300 (one-time)
AMC: ₹300/year
```

### API Capabilities:
```python
# Place orders
kite.place_order(variety=kite.VARIETY_REGULAR,
                 exchange=kite.EXCHANGE_NSE,
                 tradingsymbol="RELIANCE",
                 transaction_type=kite.TRANSACTION_TYPE_BUY,
                 quantity=1,
                 order_type=kite.ORDER_TYPE_MARKET)

# Get live market data
kite.quote(["NSE:RELIANCE", "NSE:TCS"])

# Historical data (M1, M5, M15, M30, H1, Day)
kite.historical_data(instrument_token, 
                     from_date, to_date, 
                     interval="30minute")

# Real-time streaming
kws = KiteTicker(api_key, access_token)
kws.on_ticks = on_ticks
kws.connect()
```

### How To Adapt Your Bot:
✅ Replace MT5 calls with Kite Connect
✅ Use same indicators (RSI, MACD, EMA) - Python libraries work
✅ Similar order types (Market, Limit, SL, SL-M)
✅ Same risk management logic
✅ Websocket for real-time data (like MT5 tick data)

### Registration Steps:
1. Open Zerodha account: https://zerodha.com
2. Complete KYC (Aadhaar + PAN)
3. Get Kite Connect API: https://kite.trade
4. Generate API key + secret
5. Start coding!

### Links:
- Website: https://zerodha.com
- Kite Connect: https://kite.trade
- Documentation: https://kite.trade/docs/connect/v3/
- Python library: `pip install kiteconnect`
- GitHub examples: https://github.com/zerodha/pykiteconnect

---

## 2. 🥈 ALICE BLUE ANT API (GOOD ALTERNATIVE)

### Why This Works:
- ✅ **Lower API cost** - ₹999/month (vs Zerodha ₹2,000)
- ✅ **Python support** - `alice_blue` Python library
- ✅ **NSE/BSE/MCX** - All segments
- ✅ **REST API + WebSocket** - Real-time data
- ✅ **Good for small traders** - Lower monthly cost

### Pricing:
```
Brokerage: ₹0 delivery, ₹15 per order F&O
API charges: ₹999/month
Account opening: ₹0
AMC: ₹0
```

### API Example:
```python
from alice_blue import *

alice = AliceBlue(user_id, api_key)
alice.get_session_id()

# Place order
alice.place_order(transaction_type=TransactionType.Buy,
                  instrument=alice.get_instrument_by_symbol('NSE', 'RELIANCE'),
                  quantity=1,
                  order_type=OrderType.Market,
                  product_type=ProductType.Intraday)

# Get historical data
alice.get_historical(instrument, from_date, to_date, interval='30')
```

### Links:
- Website: https://aliceblueonline.com
- API docs: https://v2api.aliceblueonline.com
- Python library: `pip install alice_blue`

---

## 3. 🥉 ANGEL ONE SMARTAPI (BUDGET OPTION)

### Why Consider:
- ✅ **FREE API** - No monthly charges!
- ✅ **Python SDK** - `smartapi-python`
- ✅ **NSE/BSE/MCX** - All segments
- ✅ **Good for testing** - No ongoing cost

### Pricing:
```
Brokerage: ₹0 delivery, ₹20 per order F&O
API charges: FREE! (with trading account)
Account opening: ₹0
AMC: ₹0
```

### API Example:
```python
from SmartApi import SmartConnect

obj = SmartConnect(api_key)
data = obj.generateSession(client_code, password, totp)

# Place order
obj.placeOrder({
    "variety": "NORMAL",
    "tradingsymbol": "RELIANCE-EQ",
    "symboltoken": "2885",
    "transactiontype": "BUY",
    "exchange": "NSE",
    "ordertype": "MARKET",
    "producttype": "INTRADAY",
    "duration": "DAY",
    "quantity": "1"
})
```

### Limitation:
- Less mature API than Zerodha
- Fewer code examples available
- Historical data has some limitations

### Links:
- Website: https://www.angelone.in
- SmartAPI: https://smartapi.angelbroking.com
- Python SDK: `pip install smartapi-python`

---

## 4. 🔄 OTHER OPTIONS

### ICICI Direct APIs
- **Cost:** High (₹50,000+ annual)
- **For:** Institutional/HNI clients
- **Skip unless:** You have ₹50L+ capital

### Upstox API
- **Cost:** ₹2,000/month (same as Zerodha)
- **Status:** Good alternative to Zerodha
- **Python:** `upstox-python` library available
- **Link:** https://upstox.com/developer/api

### 5Paisa APIs
- **Cost:** Free with trading account
- **Quality:** Average documentation
- **Better for:** Cost-conscious traders
- **Link:** https://www.5paisa.com/developerapi

---

## 📊 COMPARISON TABLE

| Platform | API Cost/Month | Brokerage (F&O) | Python Library | Real-time Data | Historical Data | Recommendation |
|----------|---------------|-----------------|----------------|----------------|-----------------|----------------|
| **Zerodha Kite** | ₹2,000 | ₹20/order | ⭐⭐⭐⭐⭐ | ✅ WebSocket | ✅ Excellent | **BEST** |
| **Alice Blue** | ₹999 | ₹15/order | ⭐⭐⭐⭐ | ✅ WebSocket | ✅ Good | **Good value** |
| **Angel One** | FREE | ₹20/order | ⭐⭐⭐ | ✅ WebSocket | ⚠️ Limited | **Budget** |
| **Upstox** | ₹2,000 | ₹20/order | ⭐⭐⭐⭐ | ✅ WebSocket | ✅ Good | Alternative |
| **5Paisa** | FREE | ₹20/order | ⭐⭐ | ✅ | ⚠️ Basic | Budget |
| **ICICI Direct** | ₹50,000+ | Tiered | ⭐⭐⭐⭐ | ✅ | ✅ | HNI only |

---

## 🔄 HOW TO CONVERT YOUR MT5 BOT TO KITE CONNECT

### Architecture Comparison:

| MT5 | Kite Connect |
|-----|--------------|
| `mt5.initialize()` | `kite = KiteConnect(api_key)` |
| `mt5.copy_rates_from_pos()` | `kite.historical_data()` |
| `mt5.symbol_info_tick()` | `kite.quote()` or WebSocket |
| `mt5.order_send()` | `kite.place_order()` |
| `mt5.positions_get()` | `kite.positions()` |
| `mt5.TIMEFRAME_M30` | `interval="30minute"` |

### Code Conversion Example:

#### OLD (MT5):
```python
import MetaTrader5 as mt5

mt5.initialize()
rates = mt5.copy_rates_from_pos("XAUUSD", mt5.TIMEFRAME_M30, 0, 100)
df = pd.DataFrame(rates)

# Calculate indicators (same)
df['rsi'] = calculate_rsi(df['close'])

# Place order
request = {
    "action": mt5.TRADE_ACTION_DEAL,
    "symbol": "XAUUSD",
    "volume": 0.1,
    "type": mt5.ORDER_TYPE_BUY,
    "price": mt5.symbol_info_tick("XAUUSD").ask
}
result = mt5.order_send(request)
```

#### NEW (Kite Connect):
```python
from kiteconnect import KiteConnect
import pandas as pd
from datetime import datetime, timedelta

kite = KiteConnect(api_key=your_api_key)
kite.set_access_token(your_access_token)

# Get historical data
instrument_token = 256265  # RELIANCE token
to_date = datetime.now()
from_date = to_date - timedelta(days=30)
data = kite.historical_data(instrument_token, from_date, to_date, "30minute")
df = pd.DataFrame(data)

# Calculate indicators (SAME as MT5!)
df['rsi'] = calculate_rsi(df['close'])

# Place order
order_id = kite.place_order(
    variety=kite.VARIETY_REGULAR,
    exchange=kite.EXCHANGE_NSE,
    tradingsymbol="RELIANCE",
    transaction_type=kite.TRANSACTION_TYPE_BUY,
    quantity=1,
    order_type=kite.ORDER_TYPE_MARKET,
    product=kite.PRODUCT_MIS  # Intraday
)
```

---

## 🔧 WHAT NEEDS TO CHANGE IN YOUR BOT

### ✅ STAYS THE SAME (90% of code):
- All indicator calculations (RSI, MACD, EMA, ADX, ATR, BB)
- Signal detection logic (MA crossover, momentum, pullback)
- Risk management (position sizing, stop loss, take profit)
- Trailing stop logic
- Time-based exits
- Break-even stops
- ML model (if trained)
- Configuration management
- All your fixes (profit booking, signal detection, scalping)

### ⚠️ NEEDS ADAPTATION (10% of code):
1. **Connection** - Replace MT5 init with Kite Connect
2. **Data fetching** - Replace `copy_rates` with `historical_data`
3. **Order placement** - Replace MT5 order syntax with Kite syntax
4. **Symbol names** - "XAUUSD" → "RELIANCE", "EURUSD" → "USDINR"
5. **Position tracking** - Replace `positions_get` with Kite API
6. **Real-time data** - Replace MT5 tick with WebSocket

---

## 🇮🇳 INDIAN MARKET DIFFERENCES

### Trading Hours:
```
NSE Equity: 9:15 AM - 3:30 PM IST (6 hours)
F&O: 9:15 AM - 3:30 PM IST
Currency: 9:00 AM - 5:00 PM IST
Commodities: 9:00 AM - 11:30 PM IST (MCX)
```

Your **dead hours filter** would be:
```json
{
  "dead_hours": [0, 1, 2, 3, 4, 5, 6, 7, 8, 16, 17, 18, 19, 20, 21, 22, 23],
  "golden_hours": [9, 10, 11, 12, 13, 14, 15]
}
```

### Market Segments:
1. **Cash/Equity** - Buy stocks for delivery
2. **Intraday (MIS)** - Square off same day (5x-20x leverage)
3. **Futures** - NIFTY, BANKNIFTY, stock futures
4. **Options** - CE/PE on indices and stocks
5. **Currency** - USDINR, EURINR, etc.

### Best Instruments for Algo Trading:
```python
# Highly liquid (like XAUUSD in Forex):
"NIFTY"      # Index futures - very liquid
"BANKNIFTY"  # Bank Nifty futures - very liquid
"RELIANCE"   # Top stock - good liquidity
"TCS"        # IT sector leader
"INFY"       # Infosys
"HDFCBANK"   # Bank sector
"ICICIBANK"  # Bank sector

# Options (high leverage, but need different strategy):
"NIFTY 18500 CE"  # Call option
"BANKNIFTY 43000 PE"  # Put option
```

---

## 💰 COST COMPARISON: MT5 vs INDIAN BROKERS

### MT5 Forex (Current):
```
Account: Demo/Live
Spread: Variable (2-10 pips typical)
Leverage: 1:100 - 1:500
Data: Free real-time
API: Free (comes with MT5)
Regulation: International brokers (ASIC, FCA, CySEC)
```

### Zerodha (Recommended):
```
Account: Real money (min ₹0)
Brokerage: ₹0 delivery, ₹20 per F&O order
Leverage: 
  - Intraday stocks: 5x
  - Futures: Based on margin (typically 10-20x)
  - Options: Full premium upfront
Data: Real-time included
API: ₹2,000/month
Regulation: SEBI (India)
```

### Monthly Cost Comparison (100 trades/month):
```
MT5 Forex:
  Spread cost: ~₹5,000 (varies)
  API: ₹0
  Total: ~₹5,000

Zerodha:
  Brokerage: ₹2,000 (100 × ₹20)
  API: ₹2,000
  Total: ₹4,000

→ Zerodha can be CHEAPER if trading F&O!
```

---

## 🎯 RECOMMENDED SETUP FOR INDIAN MARKETS

### Best Platform: **Zerodha Kite Connect**

### Best Instruments to Start:
1. **NIFTY Futures** - Like EURUSD (very liquid, tight spreads)
2. **BANKNIFTY Futures** - Like GBPUSD (volatile, good for scalping)
3. **RELIANCE** - Top stock, good liquidity

### Best Timeframe:
- **M15** or **M30** (same as your current bot)
- Indian markets are only 6 hours, so M5 can work too

### Capital Required:
```
For Stock Futures (MIS - Intraday):
  NIFTY: ~₹70,000 margin per lot
  BANKNIFTY: ~₹1,00,000 margin per lot
  
For Stocks (Intraday MIS):
  RELIANCE: ₹10,000 for 20 shares (5x leverage)
  TCS: ₹5,000 for 5 shares

Recommended starting capital: ₹2,00,000
  - ₹1,50,000 for trading
  - ₹50,000 buffer
```

### Risk Management:
```json
{
  "risk_percent": 0.5,
  "max_loss_per_trade": 2000,
  "max_daily_loss": 10000,
  "max_positions": 3
}
```

---

## 📝 STEP-BY-STEP MIGRATION PLAN

### Week 1: Setup
- [ ] Open Zerodha account
- [ ] Complete KYC
- [ ] Fund account (₹2,00,000 recommended)
- [ ] Get Kite Connect API access
- [ ] Install `kiteconnect`: `pip install kiteconnect`

### Week 2: Code Conversion
- [ ] Create new `kite_trading_bot.py`
- [ ] Replace MT5 connection with Kite Connect
- [ ] Replace data fetching functions
- [ ] Replace order placement functions
- [ ] Test on paper trading / small lots

### Week 3: Backtesting
- [ ] Download historical data from Kite
- [ ] Run your indicators on NIFTY/BANKNIFTY data
- [ ] Verify signals make sense
- [ ] Calculate expected win rate and R:R

### Week 4: Paper Trading
- [ ] Run bot in simulation mode (no real orders)
- [ ] Log all signals
- [ ] Track what WOULD have happened
- [ ] Tune parameters for Indian market

### Week 5: Live (Small)
- [ ] Start with 1 lot NIFTY or small stock
- [ ] Monitor every trade
- [ ] Verify TP/SL working correctly
- [ ] Check hour filters working

### Week 6+: Scale Up
- [ ] Gradually increase position size
- [ ] Add more instruments
- [ ] Monitor performance daily
- [ ] Compare to forex results

---

## 🔧 CODE TEMPLATE (Kite Connect Bot)

I can provide you with a complete converted version of your bot that works with Kite Connect. Would you like me to:

1. ✅ Convert your entire MT5 bot to Kite Connect
2. ✅ Keep all your fixes (profit booking, signals, scalp TP)
3. ✅ Add Indian market specifics (trading hours, instruments)
4. ✅ Include example configuration for NSE/BSE

Let me know and I'll create the complete `kite_trading_bot.py` for you!

---

## 🎯 BOTTOM LINE

**Best choice for Indian algo trading: ZERODHA KITE CONNECT**

### Why:
- ✅ Most popular (60% market share)
- ✅ Best documentation and community
- ✅ Reliable API with Python library
- ✅ All market segments (equity, F&O, currency, commodity)
- ✅ Your entire bot logic can be reused (90% same code)

### Cost:
- ₹2,000/month API + ₹20 per F&O trade
- Cheaper than MT5 forex spreads if trading 100+ times/month

### Timeline:
- 1 week to open account and get API access
- 2-3 weeks to convert and test bot
- Start live trading in 1 month

**Want me to convert your bot to Kite Connect? Just say yes!** 🚀
