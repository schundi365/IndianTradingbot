# Indian Market Trading Configurations

This directory contains ready-to-use configuration files for trading Indian market instruments using the Kite Connect broker adapter.

## Available Configurations

### 1. NIFTY 50 Futures (`config_nifty_futures.json`)

**Best for:** Index futures trading with moderate volatility
- **Timeframe:** 30 minutes
- **Instruments:** NIFTY futures (current and next month)
- **Risk per trade:** 1.0%
- **Max daily loss:** 3.0%
- **Lot size:** 50 units
- **Max positions:** 2
- **Strategy:** Momentum-based with trend following

**Recommended capital:** ₹2,00,000 minimum

### 2. BANKNIFTY Futures (`config_banknifty_futures.json`)

**Best for:** High volatility index futures trading
- **Timeframe:** 15 minutes
- **Instruments:** BANKNIFTY futures (current and next month)
- **Risk per trade:** 0.75%
- **Max daily loss:** 2.5%
- **Lot size:** 25 units
- **Max positions:** 1
- **Strategy:** Momentum-based with tighter risk controls

**Recommended capital:** ₹3,00,000 minimum

### 3. Equity Intraday (`config_equity_intraday.json`)

**Best for:** Active intraday trading in liquid stocks
- **Timeframe:** 5 minutes
- **Instruments:** RELIANCE, TCS, INFY
- **Risk per trade:** 1.0%
- **Max daily loss:** 4.0%
- **Lot size:** 1 (no minimum)
- **Max positions:** 3 (one per stock)
- **Strategy:** Scalping and momentum with volume confirmation

**Recommended capital:** ₹1,00,000 minimum

## Quick Start Guide

### Step 1: Choose Your Configuration

Select the configuration that matches your:
- Trading capital
- Risk tolerance
- Time availability
- Market preference

### Step 2: Update API Credentials

Edit your chosen configuration file and update:

```json
{
  "kite_api_key": "YOUR_KITE_API_KEY_HERE",
  "kite_token_file": "kite_token.json"
}
```

Get your API key from: https://kite.trade

### Step 3: Update Contract Symbols (Futures Only)

For NIFTY and BANKNIFTY futures, update the symbols to the current month contract:

```json
{
  "symbols": ["NIFTY24JANFUT", "NIFTY24FEBFUT"]
}
```

Check current contract symbols at: https://www.nseindia.com/

### Step 4: Authenticate Daily

Run the authentication script every morning before market open:

```bash
python kite_login.py
```

This creates the `kite_token.json` file required for trading.

### Step 5: Start Trading

```bash
python src/indian_trading_bot.py --config config_nifty_futures.json
```

## Configuration Parameters Explained

### Broker Settings

- **broker:** Always "kite" for Zerodha Kite Connect
- **kite_api_key:** Your API key from Kite Connect
- **kite_token_file:** Path to daily access token file
- **default_exchange:** "NSE" for equities, "NFO" for futures/options

### Trading Parameters

- **symbols:** List of instruments to trade
- **timeframe:** Candle timeframe in minutes (5, 15, 30, 60)
- **magic_number:** Unique identifier for bot trades
- **product_type:** "MIS" for intraday, "NRML" for positional

### Risk Management

- **risk_percent:** Risk per trade as % of account balance
- **reward_ratio:** Target profit as multiple of risk
- **max_daily_loss_percent:** Maximum loss per day before stopping
- **max_drawdown_percent:** Maximum drawdown before stopping

### Indicator Settings

- **fast_ma_period:** Fast moving average period
- **slow_ma_period:** Slow moving average period
- **atr_period:** Average True Range period
- **atr_multiplier:** Stop loss distance in ATR units
- **macd_fast/slow/signal:** MACD indicator periods
- **rsi_period:** RSI indicator period

### Position Management

- **use_split_orders:** Enable partial profit booking
- **num_positions:** Number of partial positions
- **tp_levels:** Take profit levels as multiples of risk
- **partial_close_percent:** % to close at each TP level

### Trading Hours

```json
{
  "trading_hours": {
    "start": "09:15",
    "end": "15:30"
  }
}
```

NSE trading hours in IST (Indian Standard Time).

## Customization Tips

### For More Aggressive Trading

1. Increase `risk_percent` to 1.5-2.0%
2. Reduce `timeframe` to 5 or 15 minutes
3. Increase `max_trades_per_day`
4. Lower `adx_threshold` to 20

### For More Conservative Trading

1. Decrease `risk_percent` to 0.5%
2. Increase `timeframe` to 60 minutes
3. Increase `adx_threshold` to 30
4. Reduce `max_positions` to 1

### For Different Stocks

Replace symbols in equity config with other liquid NSE stocks:
- Large cap: HDFCBANK, ICICIBANK, SBIN, HINDUNILVR
- IT sector: WIPRO, TECHM, HCLTECH
- Auto sector: MARUTI, TATAMOTORS, M&M

**Important:** Always verify stock liquidity and average daily volume before trading.

## Risk Warnings

⚠️ **Important Risk Disclosures:**

1. **Futures Trading:** Futures involve leverage and can result in losses exceeding your initial investment
2. **Intraday Trading:** MIS positions are automatically squared off at 3:20 PM by the broker
3. **Capital Requirements:** Ensure you have sufficient margin for your chosen instruments
4. **Market Volatility:** Indian markets can be highly volatile, especially during news events
5. **Testing Required:** Always test configurations in paper trading mode first

## Lot Size Reference

| Instrument | Lot Size | Approx. Margin (MIS) |
|------------|----------|---------------------|
| NIFTY Futures | 50 | ₹75,000 - ₹1,00,000 |
| BANKNIFTY Futures | 25 | ₹1,00,000 - ₹1,50,000 |
| Equity Stocks | 1 | 20% of stock value |

*Margins vary based on volatility and broker policies*

## Daily Checklist

- [ ] Run `python kite_login.py` before 9:15 AM
- [ ] Verify `kite_token.json` created with today's date
- [ ] Check for market holidays
- [ ] Verify sufficient margin in trading account
- [ ] Update futures contract symbols if month changed
- [ ] Start bot with chosen configuration
- [ ] Monitor first few trades closely

## Troubleshooting

### "Token file not found" Error
**Solution:** Run `python kite_login.py` to authenticate

### "Token is from previous day" Error
**Solution:** Re-run `python kite_login.py` to get fresh token

### "Insufficient margin" Error
**Solution:** Reduce position size or add funds to account

### "Instrument token not found" Error
**Solution:** Verify symbol name matches NSE/NFO format exactly

### No Trades Being Placed
**Solution:** 
1. Check if market is open (9:15 AM - 3:30 PM IST)
2. Verify ADX threshold not too high
3. Check volume filter settings
4. Review logs for signal generation

## Support and Documentation

- **Kite Connect API Docs:** https://kite.trade/docs/connect/v3/
- **NSE Market Data:** https://www.nseindia.com/
- **Trading Bot Documentation:** See main README.md

## Version History

- **v1.0** - Initial release with NIFTY, BANKNIFTY, and equity configurations
- Validated against Requirements 11.2

---

**Disclaimer:** These configurations are provided as examples. Past performance does not guarantee future results. Always test thoroughly before live trading and never risk more than you can afford to lose.
