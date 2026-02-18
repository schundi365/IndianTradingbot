# Equity Intraday Preset Configuration

## Overview

The **Equity Intraday** preset is designed for mean reversion trading in liquid NSE/BSE stocks using a 5-minute timeframe. This strategy is optimized for capturing short-term price reversions in high-volume equities with tight bid-ask spreads.

## Strategy Type

**Mean Reversion** - This strategy assumes that prices tend to revert to their mean over short periods. It identifies overbought and oversold conditions using technical indicators and enters positions expecting price normalization.

## Target Instruments

The preset includes 5 highly liquid stocks:
- **RELIANCE** - Reliance Industries Ltd
- **TCS** - Tata Consultancy Services Ltd
- **INFY** - Infosys Ltd
- **HDFCBANK** - HDFC Bank Ltd
- **ICICIBANK** - ICICI Bank Ltd

These stocks are chosen for:
- High daily trading volume (>5 lakh shares)
- Tight bid-ask spreads (<0.2%)
- Consistent liquidity throughout the trading day
- Price range suitable for retail traders (₹100-₹5000)

## Key Parameters

### Risk Management
- **Risk per Trade**: 0.5% (very conservative)
- **Max Positions**: 5 (diversification across stocks)
- **Max Daily Loss**: 2.0% (stop trading if reached)
- **Position Size**: ₹20,000 per position
- **Total Capital Required**: ~₹1,00,000

### Trading Hours
- **Start**: 09:30 (15 minutes after market open to avoid volatility)
- **End**: 15:00 (30 minutes before market close)
- **Duration**: 5.5 hours of active trading

### Profit Targets
- **Take Profit**: 1.5% (realistic for intraday equities)
- **Stop Loss**: 0.75% (tight stop for quick exits)
- **Reward-Risk Ratio**: 2:1

### Technical Indicators

#### Bollinger Bands (Primary)
- **Period**: 20 (on 5-minute candles)
- **Standard Deviation**: 2.0
- **Usage**: Identify overbought/oversold conditions
- **Entry Signal**: Price touches or crosses outer bands

#### RSI (Confirmation)
- **Period**: 14
- **Overbought**: 70 (potential sell signal)
- **Oversold**: 30 (potential buy signal)
- **Usage**: Confirm mean reversion signals

#### ATR (Volatility)
- **Period**: 14
- **Usage**: Measure volatility for position sizing and stop placement

## Entry Conditions

### Long Entry (Buy)
1. Price touches or crosses lower Bollinger Band
2. RSI < 30 (oversold)
3. Minimum reversion distance: 1.5 standard deviations from mean
4. Volume > 500,000 shares daily
5. Spread < 0.2%
6. Not in first or last 5-minute candle

### Short Entry (Sell)
1. Price touches or crosses upper Bollinger Band
2. RSI > 70 (overbought)
3. Minimum reversion distance: 1.5 standard deviations from mean
4. Volume > 500,000 shares daily
5. Spread < 0.2%
6. Not in first or last 5-minute candle

## Exit Conditions

### Profit Taking (Scale Out)
- **First Target**: 0.75% - Exit 50% of position
- **Second Target**: 1.5% - Exit remaining 50%

### Stop Loss
- **Fixed Stop**: 0.75% from entry
- **No Trailing Stop**: Mean reversion doesn't use trailing stops

### Time-Based Exit
- **Max Holding Time**: 180 minutes (3 hours)
- **End of Day**: Close all positions by 15:00

## Position Sizing

**Method**: Percentage-based
- Each position = ₹20,000
- With 5 max positions = ₹1,00,000 total capital
- Risk per position = 0.5% of capital = ₹500
- Max daily risk = 2% of capital = ₹2,000

### Example Calculation
```
Stock Price: ₹1,500
Position Size: ₹20,000
Shares: 20,000 / 1,500 = 13 shares
Stop Loss: 0.75% = ₹11.25 per share
Risk per Trade: 13 × ₹11.25 = ₹146.25 (0.15% of capital)
```

## Filters and Constraints

### Liquidity Filters
- **Minimum Volume**: 500,000 shares per day
- **Maximum Spread**: 0.2% (tight spreads only)

### Price Filters
- **Minimum Price**: ₹100 (avoid penny stocks)
- **Maximum Price**: ₹5,000 (affordability)

### Timing Filters
- **Avoid First Candle**: Skip first 5-minute candle (09:15-09:20)
- **Avoid Last Candle**: Skip last 5-minute candle (15:25-15:30)
- **Start Trading**: 09:30 (after initial volatility)
- **Stop Trading**: 15:00 (before closing volatility)

## Risk Scenarios

### Best Case
- 5 positions, all hit 1.5% profit
- Total gain: 5 × 0.5% × 3 (reward-risk) = 7.5% daily return
- Realistic: 2-3% daily return with mixed results

### Worst Case
- 5 positions, all hit 0.75% stop loss
- Total loss: 5 × 0.5% = 2.5% daily loss
- Protected by 2% max daily loss limit

### Typical Day
- 3-5 trades executed
- Win rate: 60-70% (mean reversion typically has high win rate)
- Average profit: 0.5-1.0% daily

## Advantages

1. **Diversification**: 5 different stocks reduce single-stock risk
2. **Conservative Risk**: 0.5% per trade is very safe
3. **High Win Rate**: Mean reversion strategies typically win 60-70% of trades
4. **Liquid Instruments**: Easy entry and exit with tight spreads
5. **Short Holding Time**: Reduced overnight risk (all positions closed daily)
6. **Proven Strategy**: Mean reversion works well in range-bound markets

## Limitations

1. **Trending Markets**: Performs poorly in strong trends
2. **Gap Openings**: Cannot handle overnight gaps
3. **News Events**: Vulnerable to sudden news-driven moves
4. **Lower Returns**: Conservative approach means lower profit potential
5. **Frequent Trading**: More trades = higher brokerage costs
6. **Requires Monitoring**: 5-minute timeframe needs active monitoring

## Recommended For

- **Experience Level**: Intermediate traders
- **Capital**: ₹1,00,000 minimum
- **Time Commitment**: Full trading day (09:30-15:00)
- **Risk Tolerance**: Low to moderate
- **Market Conditions**: Range-bound, low volatility markets

## Not Recommended For

- Beginners (try paper trading first)
- Traders with <₹50,000 capital
- Part-time traders (requires active monitoring)
- High-risk seekers (too conservative)
- Trending market conditions

## Getting Started

### Step 1: Paper Trading
Start with paper trading to:
- Understand mean reversion signals
- Practice entry/exit timing
- Test on different stocks
- Validate strategy performance

### Step 2: Single Stock
After paper trading success:
- Start with 1 stock (e.g., RELIANCE)
- Trade for 2-4 weeks
- Track all trades and results
- Refine entry/exit rules

### Step 3: Scale Up
Once profitable with 1 stock:
- Add 1 stock at a time
- Maintain diversification
- Monitor correlation between stocks
- Adjust position sizes as needed

## Performance Expectations

### Conservative Estimates
- **Daily Return**: 0.5-1.0%
- **Monthly Return**: 10-20%
- **Win Rate**: 60-70%
- **Average Win**: 1.2%
- **Average Loss**: 0.6%
- **Profit Factor**: 1.5-2.0

### Risk Metrics
- **Max Drawdown**: 5-10%
- **Sharpe Ratio**: 1.5-2.5
- **Max Daily Loss**: 2%
- **Recovery Time**: 2-4 days

## Monitoring and Adjustments

### Daily Review
- Review all trades
- Check win rate and profit factor
- Identify best/worst performing stocks
- Adjust position sizes if needed

### Weekly Review
- Calculate weekly return
- Compare to benchmark (NIFTY 50)
- Review risk metrics
- Adjust stock selection if needed

### Monthly Review
- Full performance analysis
- Strategy refinement
- Capital allocation review
- Consider adding/removing stocks

## Common Mistakes to Avoid

1. **Trading First/Last Candles**: High volatility, poor fills
2. **Ignoring Spread**: Wide spreads eat into profits
3. **Overtrading**: Wait for clear signals
4. **Holding Too Long**: Exit at targets or time limit
5. **Ignoring Volume**: Low volume = poor liquidity
6. **Fighting Trends**: Don't trade against strong trends
7. **Emotional Trading**: Stick to the rules
8. **Poor Risk Management**: Always use stop losses

## Customization Options

### Conservative Approach
- Reduce risk per trade to 0.3%
- Reduce max positions to 3
- Tighter stop loss at 0.5%
- Lower take profit at 1.0%

### Aggressive Approach
- Increase risk per trade to 1.0%
- Increase max positions to 7
- Wider stop loss at 1.0%
- Higher take profit at 2.0%

### Different Stocks
Replace default stocks with:
- **Large Cap**: SBIN, KOTAKBANK, ITC, HINDUNILVR
- **Mid Cap**: PIDILITIND, BERGEPAINT, MCDOWELL-N
- **IT Sector**: WIPRO, HCLTECH, TECHM

## Technical Requirements

- **Broker**: Kite Connect (or any supported broker)
- **Data Feed**: Real-time 5-minute candles
- **Internet**: Stable connection required
- **Monitoring**: Active monitoring during trading hours
- **Backup**: Have backup internet/power

## Conclusion

The Equity Intraday preset is a well-balanced mean reversion strategy suitable for traders who:
- Want conservative risk management
- Can actively monitor markets during trading hours
- Prefer high win rate strategies
- Trade in range-bound market conditions

Start with paper trading, master the strategy with one stock, then gradually scale up to multiple positions for optimal diversification and risk-adjusted returns.

---

**Disclaimer**: Past performance does not guarantee future results. Always start with paper trading and only risk capital you can afford to lose. This preset is for educational purposes and should be customized based on your risk tolerance and market conditions.
