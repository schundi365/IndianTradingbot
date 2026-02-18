# Migration Guide: MT5 Forex Bot → Indian Market Bot

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Step-by-Step Migration Process](#step-by-step-migration-process)
4. [Configuration Mapping](#configuration-mapping)
5. [Symbol Mapping](#symbol-mapping)
6. [Testing and Validation](#testing-and-validation)
7. [Troubleshooting](#troubleshooting)
8. [Daily Operations](#daily-operations)
9. [Rollback Plan](#rollback-plan)

---

## Overview

This guide helps you migrate your existing MT5 forex trading bot to trade Indian markets using the Kite Connect (Zerodha) broker API. The migration preserves **90% of your existing trading logic** (indicators, signals, risk management) while replacing only the **10% that is broker-specific** (connection, data fetching, order placement).

### What Changes

- **Broker connection**: MT5 → Kite Connect API
- **Market data source**: MT5 data feed → Kite historical data API
- **Order placement**: MT5 orders → Kite orders
- **Position tracking**: MT5 positions → Kite positions
- **Trading hours**: 24/5 forex → 9:15 AM - 3:30 PM IST
- **Instruments**: Forex pairs → Indian stocks/futures

### What Stays the Same

✅ All technical indicators (RSI, MACD, EMA, ATR, ADX, Bollinger Bands)
✅ Signal generation logic (MA crossovers, momentum, pullback, breakout)
✅ Risk management (position sizing, stop loss, take profit)
✅ Trailing stop logic
✅ Split order management
✅ Adaptive risk management
✅ ML integration
✅ Volume analysis
✅ Trend detection

---

## Prerequisites

### 1. Zerodha Trading Account


- Open a Zerodha trading account at https://zerodha.com
- Complete KYC verification
- Fund your account with minimum capital (recommended: ₹1,00,000 for equity, ₹2,00,000 for futures)

### 2. Kite Connect API Access

- Register for Kite Connect at https://kite.trade
- Create a new app to get your API credentials
- Note down your **API Key** and **API Secret**
- Set redirect URL to: `http://127.0.0.1:5000/`

### 3. Software Requirements

```bash
# Python 3.8 or higher
python --version

# Install required packages
pip install kiteconnect pandas numpy pytz flask
```

### 4. Minimum Capital Requirements

| Trading Type | Minimum Capital | Recommended |
|--------------|----------------|-------------|
| Equity Intraday | ₹50,000 | ₹1,00,000 |
| NIFTY Futures | ₹1,00,000 | ₹2,00,000 |
| BANKNIFTY Futures | ₹1,50,000 | ₹3,00,000 |

---

## Step-by-Step Migration Process

### Step 1: Setup Kite Connect Authentication

#### 1.1 Configure API Credentials

Edit `kite_login.py` and update your credentials:

```python
API_KEY    = "your_api_key_here"      # From https://developers.kite.trade
API_SECRET = "your_api_secret_here"   # From https://developers.kite.trade
TOKEN_FILE = "kite_token.json"
```

#### 1.2 Run Initial Authentication

```bash
python kite_login.py
```

**What happens:**
1. Browser opens automatically
2. Log in with your Zerodha credentials
3. Enter TOTP (Time-based OTP from authenticator app)
4. Script captures the token automatically
5. Creates `kite_token.json` with today's access token

**Expected output:**
```
✅ Login successful!
   Access token saved to kite_token.json
   Token (first 10 chars): AbCdEfGhIj...
   
   You can now run your trading bot!
```

#### 1.3 Verify Token File

Check that `kite_token.json` was created:

```bash
cat kite_token.json
```

Should contain:
```json
{
  "access_token": "your_access_token_here",
  "date": "2024-01-15",
  "time": "2024-01-15T09:00:00"
}
```

⚠️ **Important:** Kite tokens expire daily at 6:00 AM. You must re-authenticate every trading day.

---

### Step 2: Migrate Your Configuration


#### 2.1 Copy Your MT5 Configuration

Start with your existing MT5 bot configuration file. We'll modify only the broker-specific sections.

#### 2.2 Update Broker Settings

**Before (MT5):**
```json
{
  "broker": "mt5",
  "mt5_login": 12345678,
  "mt5_password": "password",
  "mt5_server": "MetaQuotes-Demo"
}
```

**After (Kite):**
```json
{
  "broker": "kite",
  "kite_api_key": "your_api_key_here",
  "kite_token_file": "kite_token.json",
  "default_exchange": "NSE"
}
```

#### 2.3 Update Trading Instruments

**Before (MT5 Forex):**
```json
{
  "symbols": ["XAUUSD", "XAGUSD", "EURUSD"]
}
```

**After (Indian Markets):**
```json
{
  "symbols": ["RELIANCE", "TCS", "INFY"]
}
```

See [Symbol Mapping](#symbol-mapping) section for detailed conversions.

#### 2.4 Update Trading Hours

**Before (MT5 - 24/5 trading):**
```json
{
  "trading_hours": {
    "start": "00:00",
    "end": "23:59"
  }
}
```

**After (Indian Markets - NSE hours):**
```json
{
  "trading_hours": {
    "start": "09:15",
    "end": "15:30"
  }
}
```

#### 2.5 Add Product Type (Indian Market Specific)

```json
{
  "product_type": "MIS"
}
```

- **MIS** (Margin Intraday Square-off): Intraday trading with 5x leverage, auto-squared at 3:20 PM
- **NRML** (Normal): Delivery/carry forward, lower leverage, can hold overnight

#### 2.6 Keep All Other Parameters Unchanged

✅ All indicator parameters stay the same:
```json
{
  "fast_ma_period": 10,
  "slow_ma_period": 21,
  "atr_period": 14,
  "atr_multiplier": 2.0,
  "macd_fast": 12,
  "macd_slow": 26,
  "macd_signal": 9,
  "rsi_period": 14
}
```

✅ All risk parameters stay the same:
```json
{
  "risk_percent": 1.0,
  "reward_ratio": 2.0,
  "max_daily_loss_percent": 5.0,
  "max_drawdown_percent": 10.0
}
```

✅ All feature flags stay the same:
```json
{
  "use_split_orders": true,
  "use_adaptive_risk": true,
  "ml_enabled": false,
  "use_volume_filter": true,
  "use_trend_detection": true
}
```

#### 2.7 Complete Configuration Example

See the ready-to-use configurations in the repository:
- `config_equity_intraday.json` - For stock trading
- `config_nifty_futures.json` - For NIFTY futures
- `config_banknifty_futures.json` - For BANKNIFTY futures

---

### Step 3: Update Your Bot Code


#### 3.1 Replace MT5 Imports

**Before:**
```python
import MetaTrader5 as mt5
```

**After:**
```python
from src.broker_adapter import BrokerAdapter
from src.kite_adapter import KiteAdapter
```

#### 3.2 Replace Bot Initialization

**Before:**
```python
# Initialize MT5
if not mt5.initialize():
    print("MT5 initialization failed")
    quit()

# Login to MT5
if not mt5.login(login, password, server):
    print("MT5 login failed")
    quit()

# Create bot
bot = MT5TradingBot(config)
```

**After:**
```python
# Create Kite adapter
broker = KiteAdapter(config)

# Create bot with broker adapter
bot = IndianTradingBot(config, broker)

# Connect to broker
if not bot.connect():
    print("Broker connection failed")
    quit()
```

#### 3.3 Replace Data Fetching

**Before:**
```python
# Get MT5 data
rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 200)
df = pd.DataFrame(rates)
```

**After:**
```python
# Get data through broker adapter
df = bot.get_historical_data(symbol, timeframe, 200)
```

The data format remains the same (time, open, high, low, close, volume), so all your indicator calculations work unchanged!

#### 3.4 Replace Order Placement

**Before:**
```python
# Place MT5 order
request = {
    "action": mt5.TRADE_ACTION_DEAL,
    "symbol": symbol,
    "volume": lot_size,
    "type": mt5.ORDER_TYPE_BUY,
    "price": price,
    "sl": stop_loss,
    "tp": take_profit,
    "magic": magic_number
}
result = mt5.order_send(request)
```

**After:**
```python
# Place order through broker adapter
order_id = bot.broker.place_order(
    symbol=symbol,
    direction=1,  # 1 for buy, -1 for sell
    quantity=quantity,
    order_type="MARKET",
    stop_loss=stop_loss,
    take_profit=take_profit,
    product_type="MIS"
)
```

#### 3.5 Replace Position Tracking

**Before:**
```python
# Get MT5 positions
positions = mt5.positions_get(symbol=symbol)
```

**After:**
```python
# Get positions through broker adapter
positions = bot.broker.get_positions(symbol=symbol)
```

---

## Configuration Mapping

### Complete MT5 → Kite Configuration Mapping

| MT5 Parameter | Kite Parameter | Notes |
|---------------|----------------|-------|
| `broker: "mt5"` | `broker: "kite"` | Broker selection |
| `mt5_login` | `kite_api_key` | Authentication |
| `mt5_password` | (removed) | Not needed |
| `mt5_server` | `default_exchange: "NSE"` | Exchange selection |
| - | `kite_token_file` | New: daily token file |
| - | `product_type: "MIS"` | New: intraday/delivery |
| `symbols: ["XAUUSD"]` | `symbols: ["GOLD"]` | See symbol mapping |
| `timeframe: mt5.TIMEFRAME_M30` | `timeframe: 30` | Minutes as integer |
| `trading_hours: "00:00-23:59"` | `trading_hours: {"start": "09:15", "end": "15:30"}` | NSE hours |

### Timeframe Conversion

| MT5 Constant | MT5 Value | Kite Value | Kite String |
|--------------|-----------|------------|-------------|
| `TIMEFRAME_M1` | 1 | 1 | "minute" |
| `TIMEFRAME_M5` | 5 | 5 | "5minute" |
| `TIMEFRAME_M15` | 15 | 15 | "15minute" |
| `TIMEFRAME_M30` | 30 | 30 | "30minute" |
| `TIMEFRAME_H1` | 60 | 60 | "60minute" |
| `TIMEFRAME_D1` | 1440 | - | "day" |

**In your config:** Just use the integer value (5, 15, 30, 60). The adapter handles conversion automatically.

---

## Symbol Mapping


### Forex → Indian Market Equivalents

#### Precious Metals

| MT5 Symbol | Description | Indian Equivalent | Type | Exchange |
|------------|-------------|-------------------|------|----------|
| XAUUSD | Gold vs USD | GOLD | Futures | MCX |
| XAGUSD | Silver vs USD | SILVER | Futures | MCX |

**Note:** MCX (Multi Commodity Exchange) requires separate API access. For NSE/BSE only, consider gold ETFs like GOLDBEES.

#### Indices

| MT5 Symbol | Description | Indian Equivalent | Type | Exchange |
|------------|-------------|-------------------|------|----------|
| US30 | Dow Jones | NIFTY 50 | Index Futures | NSE (NFO) |
| SPX500 | S&P 500 | NIFTY 50 | Index Futures | NSE (NFO) |
| NAS100 | NASDAQ | BANKNIFTY | Index Futures | NSE (NFO) |

**Contract naming:**
- Current month: `NIFTY24JANFUT` (January 2024)
- Next month: `NIFTY24FEBFUT` (February 2024)
- Check current contracts at: https://www.nseindia.com/

#### Currency Pairs → Indian Stocks

Since direct forex trading isn't available on NSE, map to liquid Indian stocks:

| MT5 Symbol | Volatility | Indian Stock | Sector | Characteristics |
|------------|------------|--------------|--------|-----------------|
| EURUSD | Low-Medium | TCS | IT | Stable, low volatility |
| GBPUSD | Medium | RELIANCE | Energy | High liquidity, medium volatility |
| USDJPY | Low | HDFCBANK | Banking | Large cap, stable |
| AUDUSD | Medium | INFY | IT | Good for swing trading |
| NZDUSD | Medium-High | TATAMOTORS | Auto | Higher volatility |

### Popular Indian Instruments by Category

#### Large Cap Stocks (High Liquidity)
```json
{
  "symbols": ["RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK"]
}
```
- **Best for:** Beginners, lower risk
- **Lot size:** 1 (no minimum)
- **Typical spread:** ₹0.05 - ₹0.10

#### Index Futures (Moderate Liquidity)
```json
{
  "symbols": ["NIFTY24JANFUT", "NIFTY24FEBFUT"]
}
```
- **Best for:** Index trading, lower volatility than BANKNIFTY
- **Lot size:** 50 units
- **Margin:** ₹75,000 - ₹1,00,000 (MIS)

#### Bank Index Futures (High Volatility)
```json
{
  "symbols": ["BANKNIFTY24JANFUT", "BANKNIFTY24FEBFUT"]
}
```
- **Best for:** Experienced traders, high volatility
- **Lot size:** 25 units
- **Margin:** ₹1,00,000 - ₹1,50,000 (MIS)

#### IT Sector Stocks
```json
{
  "symbols": ["TCS", "INFY", "WIPRO", "TECHM", "HCLTECH"]
}
```
- **Best for:** Sector-focused trading
- **Characteristics:** Correlated movements, export-oriented

### Symbol Naming Conventions

#### Equity (NSE/BSE)
- Format: `SYMBOL` (uppercase)
- Examples: `RELIANCE`, `TCS`, `INFY`
- Exchange: NSE (default) or BSE

#### Futures (NFO)
- Format: `SYMBOL[YY][MMM]FUT`
- Examples: `NIFTY24JANFUT`, `RELIANCE24FEBFUT`
- Exchange: NFO (NSE Futures & Options)

#### Options (NFO)
- Format: `SYMBOL[YY][MMM][STRIKE][CE/PE]`
- Examples: `NIFTY2431821500CE`, `BANKNIFTY2431845000PE`
- Exchange: NFO

**Important:** Always verify exact symbol names at https://www.nseindia.com/ before trading.

---

## Testing and Validation

### Phase 1: Paper Trading Setup


#### 1.1 Enable Paper Trading Mode

Add to your configuration:
```json
{
  "paper_trading": true,
  "log_simulated_orders": true
}
```

#### 1.2 Run Validation Script

```bash
python validate_setup.py
```

**Checks performed:**
- ✅ Kite token file exists and is valid
- ✅ Broker connection successful
- ✅ Historical data fetching works
- ✅ All configured symbols are valid
- ✅ Account info retrieval works
- ✅ Instrument info retrieval works

#### 1.3 Test Data Fetching

```bash
python test_data_fetch.py --symbol RELIANCE --timeframe 30 --bars 200
```

**Verify:**
- Data has 200 rows
- Columns: time, open, high, low, close, volume
- No missing values
- Time column is datetime format
- Price columns are float format

#### 1.4 Run Bot in Paper Trading Mode

```bash
python src/indian_trading_bot.py --config config_equity_intraday.json --paper-trading
```

**Monitor for one full trading day (9:15 AM - 3:30 PM):**
- [ ] Bot starts successfully
- [ ] Market hours detected correctly
- [ ] Data fetches every minute
- [ ] Indicators calculate correctly
- [ ] Signals generate (if market conditions allow)
- [ ] Simulated orders logged
- [ ] No errors in logs

### Phase 2: Small Position Testing

#### 2.1 Start with Minimum Position Sizes

Update your configuration:
```json
{
  "paper_trading": false,
  "risk_percent": 0.25,
  "max_positions": 1,
  "max_trades_per_day": 2,
  "symbols": ["RELIANCE"]
}
```

**Why these settings:**
- `risk_percent: 0.25` → Risk only 0.25% per trade (very conservative)
- `max_positions: 1` → Only one position at a time
- `max_trades_per_day: 2` → Limit exposure
- Single liquid stock → Easy to monitor

#### 2.2 Run Live with Small Size

```bash
python src/indian_trading_bot.py --config config_test_small.json
```

#### 2.3 Monitor First Trades Closely

**For each trade, verify:**
- [ ] Signal generated correctly
- [ ] Position size calculated correctly
- [ ] Order placed successfully
- [ ] Order ID received
- [ ] Position appears in Kite app
- [ ] Stop loss set correctly
- [ ] Take profit set correctly
- [ ] Position tracked in bot logs

#### 2.4 Verify Position Tracking

After first trade opens:
```bash
python check_positions.py
```

**Compare:**
- Bot's position data vs Kite app position data
- Entry price matches
- Quantity matches
- P&L matches
- Stop loss matches

### Phase 3: Gradual Scale-Up

#### 3.1 Week 1: Single Stock, Small Size
```json
{
  "risk_percent": 0.5,
  "max_positions": 1,
  "symbols": ["RELIANCE"]
}
```

#### 3.2 Week 2: Multiple Stocks, Small Size
```json
{
  "risk_percent": 0.5,
  "max_positions": 2,
  "symbols": ["RELIANCE", "TCS"]
}
```

#### 3.3 Week 3: Normal Risk, Multiple Stocks
```json
{
  "risk_percent": 1.0,
  "max_positions": 3,
  "symbols": ["RELIANCE", "TCS", "INFY"]
}
```

#### 3.4 Week 4+: Full Configuration
```json
{
  "risk_percent": 1.0,
  "max_positions": 3,
  "max_trades_per_day": 8,
  "symbols": ["RELIANCE", "TCS", "INFY"]
}
```

### Validation Checklist

Before going fully live, ensure:

**Authentication & Connection**
- [ ] Daily authentication process is smooth
- [ ] Token file created successfully every day
- [ ] Broker connection stable throughout trading day
- [ ] No disconnection issues

**Data & Indicators**
- [ ] Historical data fetches correctly for all symbols
- [ ] Data format matches expected format
- [ ] All indicators calculate correctly
- [ ] Indicator values match MT5 bot values (for same data)

**Signal Generation**
- [ ] Signals generate at expected times
- [ ] Signal logic matches MT5 bot logic
- [ ] No false signals due to data issues

**Order Execution**
- [ ] Orders place successfully
- [ ] Order IDs received and tracked
- [ ] Stop loss orders work correctly
- [ ] Take profit orders work correctly
- [ ] Order modifications work
- [ ] Order cancellations work

**Position Management**
- [ ] Positions tracked accurately
- [ ] P&L calculations correct
- [ ] Trailing stops work correctly
- [ ] Split orders work correctly (if enabled)
- [ ] Positions close at expected levels

**Risk Management**
- [ ] Position sizes calculated correctly
- [ ] Lot size compliance enforced
- [ ] Margin limits respected
- [ ] Daily loss limits enforced
- [ ] Maximum positions limit enforced

**Market Hours & Holidays**
- [ ] Trading only during 9:15 AM - 3:30 PM IST
- [ ] No trading on weekends
- [ ] No trading on market holidays
- [ ] MIS positions auto-squared at 3:20 PM

**Error Handling**
- [ ] Authentication errors handled gracefully
- [ ] Network errors retry correctly
- [ ] Rate limit errors handled with backoff
- [ ] Invalid order errors logged clearly
- [ ] Data fetch errors don't crash bot

**Logging & Monitoring**
- [ ] All trades logged with details
- [ ] All errors logged with context
- [ ] Performance metrics tracked
- [ ] Easy to review daily activity

---

## Troubleshooting


### Authentication Issues

#### Problem: "Token file not found"

**Error message:**
```
Token file not found: kite_token.json
Please run kite_login.py to authenticate
```

**Solution:**
```bash
python kite_login.py
```

**Root cause:** You haven't authenticated yet, or the token file was deleted.

---

#### Problem: "Token is from previous day"

**Error message:**
```
Token is from 2024-01-14, need today's token
Please run kite_login.py to re-authenticate
```

**Solution:**
```bash
python kite_login.py
```

**Root cause:** Kite tokens expire daily at 6:00 AM. You must re-authenticate every trading day.

**Prevention:** Set up a daily reminder or automated task to run `kite_login.py` before 9:15 AM.

---

#### Problem: "Invalid API key or secret"

**Error message:**
```
KiteException: Invalid API key or secret
```

**Solution:**
1. Verify your API key and secret at https://developers.kite.trade
2. Check for typos in `kite_login.py`
3. Ensure no extra spaces or quotes
4. Regenerate API secret if needed

---

#### Problem: Browser doesn't open during login

**Solution:**
1. Manually open the URL shown in terminal
2. Complete login in browser
3. Script will detect the redirect automatically

**Alternative:** Copy the URL and paste in any browser.

---

### Connection Issues

#### Problem: "Rate limit exceeded"

**Error message:**
```
KiteException: Too many requests
```

**Solution:**
- Wait 1-2 minutes before retrying
- The bot implements automatic exponential backoff
- Reduce data fetch frequency if this happens often

**Root cause:** Kite API has rate limits (3 requests/second). The bot should handle this automatically.

---

#### Problem: "Network timeout"

**Error message:**
```
ConnectionError: Connection timeout
```

**Solution:**
1. Check your internet connection
2. Verify Kite API status at https://kite.trade/status
3. Retry after a few minutes
4. Check firewall settings

---

### Data Issues

#### Problem: "Instrument token not found"

**Error message:**
```
Instrument token not found for RELIANCE
```

**Solution:**
1. Verify symbol name is correct (uppercase, no spaces)
2. Check symbol exists on NSE: https://www.nseindia.com/
3. For futures, verify contract month is current
4. Restart bot to reload instrument cache

**Common mistakes:**
- `Reliance` → Should be `RELIANCE`
- `NIFTY 50` → Should be `NIFTY` or `NIFTY24JANFUT`
- `TCS.NS` → Should be `TCS`

---

#### Problem: "Insufficient historical data"

**Error message:**
```
Failed to fetch data for RELIANCE: Insufficient data
```

**Solution:**
1. Check if market is open (data only available during trading hours)
2. For newly listed stocks, reduce `bars` parameter
3. Verify instrument is actively traded
4. Try a different timeframe

---

#### Problem: "Data format mismatch"

**Error message:**
```
KeyError: 'close'
```

**Solution:**
1. Check if data fetch was successful
2. Verify broker adapter is returning correct format
3. Check logs for data fetch errors
4. Restart bot to clear any cached data

---

### Order Issues

#### Problem: "Insufficient margin"

**Error message:**
```
KiteException: Insufficient funds. Required margin: ₹50,000, Available: ₹30,000
```

**Solution:**
1. Add funds to your trading account
2. Reduce position size in configuration
3. Reduce `risk_percent` parameter
4. Trade smaller lot size instruments

**Prevention:** Always maintain 2x the required margin for your strategy.

---

#### Problem: "Order rejected - price out of range"

**Error message:**
```
KiteException: Price is out of the allowed range
```

**Solution:**
1. For limit orders, ensure price is within ±20% of LTP
2. Use market orders for immediate execution
3. Check if circuit breaker is triggered
4. Verify tick size compliance

---

#### Problem: "Order rejected - invalid quantity"

**Error message:**
```
KiteException: Invalid quantity
```

**Solution:**
1. Verify quantity is a multiple of lot size
2. For futures, ensure minimum lot size is met
3. Check instrument info for correct lot size
4. Round quantity to nearest lot size

**Example:**
```python
# NIFTY futures lot size = 50
quantity = 75  # ❌ Invalid
quantity = 50  # ✅ Valid
quantity = 100 # ✅ Valid
```

---

#### Problem: "Position not found"

**Error message:**
```
Position not found for RELIANCE
```

**Solution:**
1. Check if order was actually executed
2. Verify order ID in Kite app
3. Check if position was auto-squared (MIS at 3:20 PM)
4. Ensure you're checking correct symbol name

---

### Market Hours Issues

#### Problem: Bot not trading during market hours

**Checklist:**
- [ ] Current time is between 9:15 AM - 3:30 PM IST
- [ ] Today is not Saturday/Sunday
- [ ] Today is not a market holiday
- [ ] Bot is running (check process)
- [ ] No errors in logs

**Check market holidays:** https://www.nseindia.com/regulations/holiday-list

---

#### Problem: MIS positions auto-squared unexpectedly

**Explanation:** This is normal behavior. MIS (intraday) positions are automatically closed by the broker at 3:20 PM.

**Solution:**
- Use NRML product type if you want to hold overnight
- Ensure bot closes positions before 3:20 PM
- Monitor positions closely after 3:00 PM

---

### Performance Issues

#### Problem: Bot is slow or lagging

**Possible causes:**
1. Too many symbols configured
2. Too frequent data fetching
3. Insufficient system resources
4. Network latency

**Solutions:**
- Reduce number of symbols
- Increase data fetch interval
- Close other applications
- Check internet speed
- Use a VPS with good connectivity

---

#### Problem: High memory usage

**Solution:**
1. Reduce number of historical bars fetched
2. Clear old log files
3. Restart bot daily
4. Disable ML features if not needed

---

### Indicator Issues

#### Problem: Indicator values don't match MT5

**Possible causes:**
1. Different data (Indian markets vs forex)
2. Different timeframe
3. Different number of bars
4. Data quality issues

**Solution:**
1. Verify you're comparing same timeframe
2. Check data quality (no missing values)
3. Ensure sufficient historical bars (200+)
4. Compare calculation logic

**Note:** Some difference is expected due to different markets and data sources.

---

### Configuration Issues

#### Problem: "Invalid configuration parameter"

**Solution:**
1. Validate JSON syntax (use https://jsonlint.com/)
2. Check for missing commas
3. Verify all required parameters present
4. Check parameter types (string vs number)

**Common mistakes:**
```json
{
  "risk_percent": "1.0"  // ❌ Should be number, not string
  "risk_percent": 1.0    // ✅ Correct
}
```

---

#### Problem: Futures contract expired

**Error message:**
```
Instrument token not found for NIFTY24JANFUT
```

**Solution:**
1. Update symbol to current month contract
2. Check expiry dates at https://www.nseindia.com/
3. Futures expire on last Thursday of every month

**Example:**
```json
{
  "symbols": ["NIFTY24FEBFUT"]  // Update from JANFUT to FEBFUT
}
```

---

### Logging Issues

#### Problem: Can't find log files

**Default log location:** `logs/trading_bot_YYYY-MM-DD.log`

**Solution:**
```bash
# List log files
ls -la logs/

# View today's log
tail -f logs/trading_bot_$(date +%Y-%m-%d).log

# Search for errors
grep ERROR logs/trading_bot_*.log
```

---

#### Problem: Logs too verbose

**Solution:**
Update log level in configuration:
```json
{
  "log_level": "INFO"  // Change from DEBUG to INFO or WARNING
}
```

---

### Emergency Procedures

#### Problem: Bot placing wrong orders

**Immediate action:**
1. **STOP THE BOT IMMEDIATELY** (Ctrl+C or kill process)
2. Log into Kite app/web
3. Cancel all pending orders
4. Close all open positions manually
5. Review logs to identify issue
6. Fix configuration/code
7. Test in paper trading mode before resuming

---

#### Problem: Bot not responding

**Solution:**
1. Check if process is running: `ps aux | grep indian_trading_bot`
2. Check system resources: `top` or `htop`
3. Check logs for errors
4. Kill and restart if frozen: `kill -9 <PID>`

---

#### Problem: Unexpected losses

**Investigation steps:**
1. Review all trades in logs
2. Compare with Kite trade history
3. Check if stop losses were hit
4. Verify position sizing was correct
5. Check for slippage issues
6. Review market conditions during trades

**Prevention:**
- Always use stop losses
- Start with small position sizes
- Monitor first few days closely
- Keep risk per trade low (0.5-1%)

---

## Daily Operations


### Morning Routine (Before 9:15 AM)

#### 1. Authenticate with Kite (5 minutes)

```bash
python kite_login.py
```

- Browser opens automatically
- Log in with Zerodha credentials
- Enter TOTP from authenticator app
- Verify `kite_token.json` created

#### 2. Check Market Status (2 minutes)

- [ ] Verify today is not a holiday
- [ ] Check for any special market announcements
- [ ] Review overnight global market movements
- [ ] Check if any futures contracts expired (last Thursday)

**Market holiday calendar:** https://www.nseindia.com/regulations/holiday-list

#### 3. Update Configuration if Needed (2 minutes)

- [ ] Update futures contract symbols if month changed
- [ ] Adjust risk parameters if needed
- [ ] Review and update symbol list
- [ ] Check margin requirements

#### 4. Pre-Market Checks (3 minutes)

```bash
# Verify setup
python validate_setup.py

# Check account balance
python check_account.py

# Verify no open positions from previous day (if using NRML)
python check_positions.py
```

#### 5. Start the Bot (1 minute)

```bash
# Start bot
python src/indian_trading_bot.py --config config_equity_intraday.json

# Or run in background
nohup python src/indian_trading_bot.py --config config_equity_intraday.json > bot.log 2>&1 &
```

**Total time: ~15 minutes**

---

### During Market Hours (9:15 AM - 3:30 PM)

#### Active Monitoring (First Week)

**Every 30 minutes:**
- [ ] Check bot is still running
- [ ] Review recent log entries
- [ ] Verify positions match Kite app
- [ ] Check P&L

```bash
# Check if bot is running
ps aux | grep indian_trading_bot

# View recent logs
tail -n 50 logs/trading_bot_$(date +%Y-%m-%d).log

# Check current positions
python check_positions.py
```

#### Passive Monitoring (After First Week)

**Every 2 hours:**
- [ ] Quick log review
- [ ] Position check
- [ ] P&L review

**Set up alerts for:**
- Bot stopped/crashed
- Daily loss limit reached
- Unusual number of trades
- Order rejections

---

### End of Day (After 3:30 PM)

#### 1. Verify All Positions Closed (5 minutes)

```bash
# Check positions
python check_positions.py

# Should show: No open positions (if using MIS)
```

**For MIS:** All positions auto-squared at 3:20 PM
**For NRML:** Positions carry forward to next day

#### 2. Review Daily Performance (10 minutes)

```bash
# Generate daily report
python generate_daily_report.py --date $(date +%Y-%m-%d)
```

**Review:**
- [ ] Total trades executed
- [ ] Win rate
- [ ] Total P&L
- [ ] Largest win/loss
- [ ] Any errors or issues
- [ ] Risk metrics

#### 3. Backup Logs (2 minutes)

```bash
# Backup today's logs
cp logs/trading_bot_$(date +%Y-%m-%d).log backups/

# Backup token file
cp kite_token.json backups/kite_token_$(date +%Y-%m-%d).json
```

#### 4. Update Trading Journal (5 minutes)

Document:
- Market conditions today
- Bot performance
- Any manual interventions
- Issues encountered
- Lessons learned

---

### Weekly Maintenance

#### Sunday Evening (30 minutes)

**1. Review Weekly Performance**
- Total P&L for the week
- Win rate and average win/loss
- Best and worst days
- Strategy effectiveness

**2. Update Configuration**
- Adjust risk parameters based on performance
- Update symbol list if needed
- Review and optimize indicator parameters

**3. Check for Updates**
- Bot software updates
- Kite API changes
- Market regulation changes

**4. Plan for Next Week**
- Check upcoming holidays
- Review economic calendar
- Identify potential trading opportunities
- Set weekly goals

---

### Monthly Maintenance

#### End of Month (1 hour)

**1. Update Futures Contracts**

Futures expire on last Thursday of every month. Update symbols:

```json
{
  "symbols": [
    "NIFTY24FEBFUT",  // Update from JANFUT
    "BANKNIFTY24FEBFUT"
  ]
}
```

**2. Performance Review**
- Monthly P&L
- Sharpe ratio
- Maximum drawdown
- Strategy performance by symbol
- Compare with benchmark (NIFTY)

**3. Risk Assessment**
- Review risk parameters
- Adjust position sizing if needed
- Update stop loss strategies
- Review margin utilization

**4. System Maintenance**
- Clear old log files (keep last 3 months)
- Backup configuration files
- Update dependencies if needed
- Test disaster recovery procedures

---

### Automation Tips

#### Automate Daily Authentication (Linux/Mac)

Create a cron job to remind you:

```bash
# Edit crontab
crontab -e

# Add reminder at 9:00 AM on weekdays
0 9 * * 1-5 notify-send "Trading Bot" "Run kite_login.py before market opens!"
```

#### Automate Bot Startup (After Manual Authentication)

```bash
# Create startup script: start_bot.sh
#!/bin/bash
cd /path/to/bot
source venv/bin/activate
python src/indian_trading_bot.py --config config_equity_intraday.json > logs/bot_$(date +%Y-%m-%d).log 2>&1 &
echo "Bot started with PID: $!"
```

#### Automate Daily Reports

```bash
# Add to crontab for 4:00 PM on weekdays
0 16 * * 1-5 /path/to/bot/generate_daily_report.sh
```

---

## Rollback Plan

### When to Rollback

Consider rolling back to MT5 if:
- Consistent technical issues with Kite API
- Bot performance significantly worse than MT5
- Regulatory changes affecting Indian markets
- Personal preference for forex trading

### Rollback Procedure

#### Step 1: Stop Indian Market Bot

```bash
# Find bot process
ps aux | grep indian_trading_bot

# Stop bot
kill <PID>

# Or if running in foreground
Ctrl+C
```

#### Step 2: Close All Open Positions

1. Log into Kite app/web
2. Close all open positions manually
3. Cancel all pending orders
4. Verify account is flat

#### Step 3: Backup Indian Market Configuration

```bash
# Backup configuration
cp config_equity_intraday.json backups/config_indian_backup.json

# Backup logs
cp -r logs/ backups/logs_indian_$(date +%Y-%m-%d)/
```

#### Step 4: Restore MT5 Configuration

```bash
# Restore MT5 config
cp backups/config_mt5_backup.json config.json

# Restore MT5 bot code
git checkout main  # Or your MT5 branch
```

#### Step 5: Restart MT5 Bot

```bash
# Initialize MT5
python mt5_trading_bot.py --config config.json
```

#### Step 6: Verify MT5 Bot Working

- [ ] MT5 connection successful
- [ ] Data fetching works
- [ ] Indicators calculate correctly
- [ ] Test order placement (paper trading)
- [ ] Monitor for one full day

---

### Hybrid Approach

You can run both bots simultaneously:

**MT5 Bot:** Trade forex during 24/5 hours
**Indian Bot:** Trade Indian markets during 9:15 AM - 3:30 PM IST

**Benefits:**
- Diversification across markets
- 24-hour trading coverage
- Compare performance
- Gradual transition

**Configuration:**
- Use different magic numbers
- Separate log files
- Separate risk allocations
- Independent monitoring

---

## Additional Resources

### Documentation

- **Kite Connect API Docs:** https://kite.trade/docs/connect/v3/
- **NSE Market Data:** https://www.nseindia.com/
- **Indian Market Regulations:** https://www.sebi.gov.in/
- **Trading Bot GitHub:** [Your repository URL]

### Tools

- **Kite Web:** https://kite.zerodha.com/
- **Kite Mobile App:** iOS/Android
- **Market Watch:** https://www.moneycontrol.com/
- **Economic Calendar:** https://www.investing.com/economic-calendar/

### Support

- **Zerodha Support:** https://support.zerodha.com/
- **Kite Connect Forum:** https://kite.trade/forum/
- **Trading Bot Issues:** [Your GitHub issues URL]

### Learning Resources

- **Indian Market Basics:** https://zerodha.com/varsity/
- **Technical Analysis:** https://www.investopedia.com/
- **Risk Management:** https://www.babypips.com/learn/forex/risk-management

---

## Frequently Asked Questions

### General Questions

**Q: Can I trade both forex (MT5) and Indian markets simultaneously?**
A: Yes! You can run both bots in parallel. Use different configurations and magic numbers.

**Q: How much capital do I need to start?**
A: Minimum ₹50,000 for equity intraday, ₹2,00,000 for futures. Start small and scale up.

**Q: Do I need to re-authenticate every day?**
A: Yes, Kite tokens expire daily at 6:00 AM. Run `kite_login.py` every morning before 9:15 AM.

**Q: Can I automate the daily authentication?**
A: No, Kite requires manual login with TOTP for security. This takes only 2-3 minutes.

**Q: What happens if I forget to authenticate?**
A: Bot will fail to connect and show an error. Simply run `kite_login.py` and restart the bot.

### Trading Questions

**Q: Can I hold positions overnight?**
A: Yes, use `product_type: "NRML"` instead of `"MIS"`. Note: Lower leverage, higher margin required.

**Q: What happens to MIS positions at end of day?**
A: Broker automatically squares off all MIS positions at 3:20 PM.

**Q: Can I trade options?**
A: Yes, but options require additional logic for strike selection and expiry management. Start with equity/futures first.

**Q: How do I trade commodities (gold, silver)?**
A: Commodities trade on MCX, which requires separate API access. Contact Zerodha for MCX activation.

### Technical Questions

**Q: Why are my indicator values different from MT5?**
A: Different markets, data sources, and trading hours. Some variation is normal. Verify calculation logic is correct.

**Q: Can I use my existing MT5 indicators?**
A: Yes! All indicator calculations remain the same. Only data source changes.

**Q: How do I add a new broker (Alice Blue, Upstox)?**
A: Create a new adapter class implementing `BrokerAdapter` interface. See design document for details.

**Q: Can I backtest strategies on Indian market data?**
A: Yes, fetch historical data using Kite API and run your backtesting framework.

### Performance Questions

**Q: What's a good win rate to expect?**
A: Depends on strategy. 40-60% is typical for trend-following strategies. Focus on risk-reward ratio.

**Q: How many trades per day is normal?**
A: Varies by timeframe and strategy. 2-5 trades per day is typical for 30-minute timeframe.

**Q: Should I trade every day?**
A: No. Only trade when your strategy generates valid signals. Some days have no trades.

**Q: How do I improve performance?**
A: Focus on risk management, position sizing, and strategy optimization. Keep detailed logs and review regularly.

---

## Conclusion

Congratulations on migrating your MT5 forex bot to Indian markets! 

### Key Takeaways

✅ **90% of your trading logic remains unchanged** - All indicators, signals, and risk management work the same way

✅ **Only broker-specific code changes** - Connection, data fetching, and order placement adapted for Kite Connect

✅ **Start small and scale gradually** - Begin with paper trading, then small positions, then full size

✅ **Daily authentication required** - Run `kite_login.py` every morning (takes 2-3 minutes)

✅ **Monitor closely initially** - First week requires active monitoring, then can be more passive

✅ **Keep detailed logs** - Essential for troubleshooting and performance improvement

### Next Steps

1. **Complete Phase 1 testing** - Run in paper trading mode for at least 3-5 days
2. **Start with minimum positions** - Risk only 0.25-0.5% per trade initially
3. **Monitor and adjust** - Review performance daily, adjust parameters weekly
4. **Scale gradually** - Increase position sizes only after consistent profitability
5. **Keep learning** - Indian markets have unique characteristics, learn continuously

### Success Metrics

Track these metrics to measure migration success:
- **Uptime:** Bot runs successfully every trading day
- **Win rate:** Comparable to MT5 bot (±5%)
- **Risk-reward:** Maintained or improved
- **Drawdown:** Within acceptable limits
- **Sharpe ratio:** Positive and improving

### Support

If you encounter issues not covered in this guide:
1. Check logs for detailed error messages
2. Review troubleshooting section
3. Consult Kite Connect documentation
4. Reach out to Zerodha support
5. Open an issue on GitHub

**Happy trading! 🚀**

---

*Last updated: January 2024*
*Version: 1.0*
*Validates: Requirements 11.1*

