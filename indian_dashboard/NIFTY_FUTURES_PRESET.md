# NIFTY 50 Futures Preset Configuration

## Overview

The NIFTY 50 Futures preset is a pre-configured trading strategy optimized for trading NIFTY 50 index futures on the National Stock Exchange (NSE) of India. This preset implements a trend-following strategy with conservative risk management suitable for intraday trading.

## Strategy Details

### Core Strategy
- **Type**: Trend Following
- **Timeframe**: 15-minute candles
- **Market**: NIFTY 50 Futures (NFO)
- **Trading Style**: Intraday (positions closed before market close)

### Key Features
1. **Conservative Risk Management**: 1% risk per trade with 3% maximum daily loss limit
2. **Optimal Reward-Risk Ratio**: 2:1 (1.5% take profit vs 0.75% stop loss)
3. **Trailing Stop Loss**: Automatically locks in profits as the trade moves favorably
4. **Volume Filter**: Ensures sufficient liquidity with minimum volume requirement
5. **Volatility-Based Stops**: Uses ATR (Average True Range) for dynamic stop placement

## Configuration Parameters

### Risk Management
| Parameter | Value | Description |
|-----------|-------|-------------|
| Risk per Trade | 1.0% | Maximum capital risked on each trade |
| Max Positions | 2 | Maximum concurrent NIFTY positions |
| Max Daily Loss | 3.0% | Stop trading if daily loss reaches this limit |
| Position Sizing | Risk-based | Positions sized based on risk percentage |
| Base Position Size | ₹1,00,000 | Base capital allocated per position |

### Entry/Exit Rules
| Parameter | Value | Description |
|-----------|-------|-------------|
| Take Profit | 1.5% | Target profit level |
| Stop Loss | 0.75% | Maximum loss per trade |
| Trailing Stop | Enabled | Locks in profits automatically |
| Trailing Activation | 1.0% | Activates when trade is 1% in profit |
| Trailing Distance | 0.5% | Trails by 0.5% from highest point |

### Technical Indicators
| Parameter | Value | Description |
|-----------|-------|-------------|
| Indicator Period | 20 | Moving average period for trend detection |
| ATR Period | 14 | Period for volatility calculation |
| Min Volume | 100,000 | Minimum volume required for entry |

### Trading Hours
| Parameter | Value | Description |
|-----------|-------|-------------|
| Market Open | 09:15 IST | Start monitoring for trades |
| Position Close | 15:15 IST | Close all positions (15 min before market close) |
| Market Close | 15:30 IST | NSE market closing time |

### Instrument Configuration
| Parameter | Value | Description |
|-----------|-------|-------------|
| Symbol | NIFTY24JANFUT | Current month NIFTY futures contract |
| Exchange | NFO | National Stock Exchange F&O segment |
| Instrument Type | FUT | Futures contract |
| Lot Size | 50 | Standard NIFTY lot size |
| Tick Size | 0.05 | Minimum price movement |

## Why These Parameters?

### 1% Risk Per Trade
- Conservative approach suitable for futures trading
- Allows for multiple losing trades without significant drawdown
- Recommended by professional traders for retail accounts

### 2 Maximum Positions
- NIFTY futures require significant margin (₹1-1.5 lakh per lot)
- Prevents overexposure to single index
- Allows focus on quality setups rather than quantity

### 15-Minute Timeframe
- Balances between noise (lower timeframes) and missed opportunities (higher timeframes)
- Provides 25-26 candles per trading session
- Suitable for trend-following in liquid instruments

### 2:1 Reward-Risk Ratio
- Ensures profitability even with 40-50% win rate
- Compensates for transaction costs and slippage
- Industry standard for trend-following strategies

### Trailing Stop Loss
- Protects profits in trending markets
- Activates at 1% profit to ensure minimum gain
- Trails by 0.5% to avoid premature exits

### Volume Filter (100,000)
- NIFTY futures are highly liquid (typical volume > 1 million)
- Ensures tight spreads and minimal slippage
- Filters out low-liquidity periods (first/last 15 minutes)

## Expected Performance

### Realistic Expectations
- **Win Rate**: 40-50% (typical for trend-following)
- **Average Win**: 1.5% (take profit target)
- **Average Loss**: 0.75% (stop loss)
- **Expectancy**: Positive with 2:1 R:R ratio
- **Monthly Return**: 3-8% (highly variable, depends on market conditions)

### Best Market Conditions
- **Trending Markets**: Strategy performs best in clear uptrends or downtrends
- **High Volatility**: More opportunities in volatile markets
- **Avoid**: Choppy, sideways markets with no clear direction

## Usage Instructions

### 1. Load the Preset
```
1. Open the dashboard
2. Navigate to Configuration tab
3. Select "NIFTY 50 Futures" from preset dropdown
4. Click "Load Preset"
```

### 2. Customize (Optional)
You can adjust parameters based on your:
- **Risk Tolerance**: Increase/decrease risk_per_trade
- **Capital**: Adjust base_position_size
- **Trading Style**: Change timeframe or strategy
- **Market Conditions**: Modify indicator_period for different volatility

### 3. Update Instrument
The preset includes a sample instrument (NIFTY24JANFUT). You should:
1. Go to Instruments tab
2. Search for current month NIFTY futures
3. Select the active contract
4. Return to Configuration tab

### 4. Test with Paper Trading
- The preset starts with `paper_trading: True`
- Test the strategy for at least 2-4 weeks
- Monitor performance and adjust parameters
- Switch to live trading only after consistent results

### 5. Monitor and Adjust
- Review daily performance
- Track win rate and average R:R
- Adjust parameters based on market conditions
- Keep a trading journal

## Risk Warnings

⚠️ **Important Disclaimers**:

1. **Futures Trading is Risky**: You can lose more than your initial investment
2. **Past Performance ≠ Future Results**: No guarantee of profits
3. **Market Conditions Vary**: Strategy may underperform in certain conditions
4. **Leverage Risk**: Futures use leverage, amplifying both gains and losses
5. **Test First**: Always test with paper trading before risking real capital
6. **Capital Requirements**: Ensure you have sufficient margin (₹1.5-2 lakh recommended)
7. **Emotional Discipline**: Follow the rules strictly, avoid emotional trading

## Recommended Capital

### Minimum Capital
- **Paper Trading**: ₹50,000 (virtual)
- **Live Trading**: ₹2,00,000 (real)

### Optimal Capital
- **Conservative**: ₹5,00,000
- **Moderate**: ₹10,00,000
- **Aggressive**: ₹20,00,000+

**Note**: With 1% risk per trade and ₹2 lakh capital, you risk ₹2,000 per trade. With NIFTY lot size of 50, this translates to ₹40 per point movement, which is reasonable for stop loss placement.

## Modifications for Different Risk Profiles

### Conservative Trader
```python
risk_per_trade: 0.5%
max_positions: 1
max_daily_loss: 2.0%
take_profit: 1.0%
stop_loss: 0.5%
```

### Moderate Trader (Default)
```python
risk_per_trade: 1.0%
max_positions: 2
max_daily_loss: 3.0%
take_profit: 1.5%
stop_loss: 0.75%
```

### Aggressive Trader
```python
risk_per_trade: 2.0%
max_positions: 3
max_daily_loss: 5.0%
take_profit: 2.5%
stop_loss: 1.25%
```

## Frequently Asked Questions

### Q: Why only 2 positions?
A: NIFTY futures require significant margin. Two positions allow diversification (e.g., one long, one short) without overexposure.

### Q: Can I trade overnight?
A: This preset is designed for intraday trading. Overnight positions carry gap risk and require different risk management.

### Q: What if I have less capital?
A: Consider trading NIFTY options or equity cash instead. Futures require substantial capital for proper risk management.

### Q: How do I know if the strategy is working?
A: Track these metrics over 50+ trades:
- Win rate (should be 40-50%)
- Average R:R (should be close to 2:1)
- Maximum drawdown (should be < 10%)
- Profit factor (should be > 1.5)

### Q: When should I stop using this strategy?
A: Stop if:
- Consecutive losses exceed 5 trades
- Drawdown exceeds 10%
- Win rate drops below 30% for 50+ trades
- Market conditions change significantly (e.g., extended sideways movement)

## Support and Resources

### Learning Resources
- **NSE Website**: https://www.nseindia.com/
- **Zerodha Varsity**: https://zerodha.com/varsity/
- **TradingView**: https://www.tradingview.com/symbols/NSE-NIFTY/

### Broker Information
- **Kite Connect**: https://kite.trade/
- **API Documentation**: https://kite.trade/docs/connect/v3/

### Community
- Join trading communities to discuss strategies
- Share experiences with other traders
- Learn from successful traders

## Version History

- **v1.0** (2024-02-18): Initial NIFTY futures preset
  - Trend following strategy
  - 15-minute timeframe
  - Conservative risk management
  - Trailing stop loss feature
  - Volume and volatility filters

## Disclaimer

This preset is provided for educational purposes only. Trading in futures involves substantial risk of loss and is not suitable for all investors. Past performance is not indicative of future results. Always conduct your own research and consult with a financial advisor before trading.

The developers and maintainers of this software are not responsible for any trading losses incurred while using this preset or any other configuration.

**Trade at your own risk.**
