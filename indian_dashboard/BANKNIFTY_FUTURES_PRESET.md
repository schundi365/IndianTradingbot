# BANKNIFTY Futures Preset Configuration

## Overview

The BANKNIFTY Futures preset is designed for trading BANKNIFTY futures contracts using a momentum-based strategy. This preset is optimized for the higher volatility and liquidity characteristics of the banking sector index.

## Key Characteristics

### Strategy Type
- **Momentum Trading**: Captures strong directional moves in BANKNIFTY
- **Timeframe**: 15-minute charts for balanced signal quality and trade frequency
- **Indicator Period**: 14 periods for faster momentum detection

### Risk Profile
- **Risk per Trade**: 1.5% (higher than NIFTY due to volatility)
- **Max Positions**: 2 concurrent positions
- **Max Daily Loss**: 4.0% (stop trading if reached)
- **Base Position Size**: ₹75,000 per position

### Profit Targets
- **Take Profit**: 2.5% (wider target for volatility)
- **Stop Loss**: 1.5% (wider stop for volatility)
- **Reward-Risk Ratio**: ~1.67:1

## Instrument Configuration

### Default Instrument
```json
{
  "symbol": "BANKNIFTY24JANFUT",
  "name": "BANKNIFTY JAN FUT",
  "exchange": "NFO",
  "instrument_type": "FUT",
  "lot_size": 25,
  "tick_size": 0.05
}
```

**Note**: Update the symbol to the current month's contract before trading.

## Trading Hours

- **Start**: 09:15 IST (Market open)
- **End**: 15:15 IST (Close positions 15 minutes before market close)

## Advanced Features

### Trailing Stop Loss
- **Enabled**: Yes
- **Activation**: 1.5% profit
- **Trail Distance**: 0.75% (wider for volatility)

### Volume Filter
- **Minimum Volume**: 50,000 contracts
- Ensures sufficient liquidity for entry/exit

### Momentum Indicators
- **Momentum Threshold**: 0.5 (minimum strength for entry)
- **RSI Period**: 14
- **RSI Overbought**: 70
- **RSI Oversold**: 30

### Volatility Management
- **ATR Period**: 14
- Used for dynamic stop loss adjustment

## Comparison with NIFTY Preset

| Parameter | BANKNIFTY | NIFTY | Reason |
|-----------|-----------|-------|--------|
| Strategy | Momentum | Trend Following | BANKNIFTY has stronger directional moves |
| Risk per Trade | 1.5% | 1.0% | Higher volatility requires wider stops |
| Max Daily Loss | 4.0% | 3.0% | Accommodates volatility |
| Take Profit | 2.5% | 1.5% | Wider targets for bigger moves |
| Stop Loss | 1.5% | 0.75% | Prevents premature stops |
| Base Position Size | ₹75k | ₹100k | Lower capital per position due to risk |
| Indicator Period | 14 | 20 | Faster signals for momentum |
| Lot Size | 25 | 50 | BANKNIFTY contract specification |

## Usage Instructions

### 1. Load the Preset

In the dashboard:
1. Navigate to the **Configuration** tab
2. Click on **Load Preset**
3. Select **BANKNIFTY Futures**
4. Review and adjust parameters if needed

### 2. Update Instrument Symbol

**Important**: Update the futures contract symbol to the current month:
- January: BANKNIFTY24JANFUT
- February: BANKNIFTY24FEBFUT
- March: BANKNIFTY24MARFUT
- etc.

### 3. Adjust Risk Parameters (Optional)

Consider your risk tolerance:
- **Conservative**: Reduce risk_per_trade to 1.0%, max_daily_loss to 3.0%
- **Aggressive**: Increase to 2.0% and 5.0% respectively (not recommended for beginners)

### 4. Enable Paper Trading First

The preset defaults to paper trading mode. Test the strategy for at least 1-2 weeks before going live.

### 5. Monitor Performance

Key metrics to watch:
- Win rate (target: >50%)
- Average profit per trade
- Maximum drawdown
- Sharpe ratio

## Risk Warnings

### High Volatility
BANKNIFTY is more volatile than NIFTY. Expect:
- Larger intraday swings
- More frequent stop loss hits
- Higher profit potential but also higher risk

### Leverage Risk
Futures trading involves leverage. A 1.5% move in BANKNIFTY can result in significant P&L.

### Banking Sector Exposure
BANKNIFTY tracks banking stocks. Be aware of:
- RBI policy announcements
- Banking sector news
- Interest rate changes
- Credit events

### Liquidity Considerations
While BANKNIFTY is highly liquid:
- Avoid trading during first 15 minutes (high volatility)
- Be cautious near expiry dates
- Monitor bid-ask spreads

## Best Practices

### 1. Market Conditions
This momentum strategy works best in:
- Trending markets (up or down)
- High volatility environments
- Clear directional moves

Avoid trading in:
- Sideways/choppy markets
- Low volume days
- Major event days (budget, policy announcements)

### 2. Position Management
- Never override max positions limit
- Respect stop losses (no manual intervention)
- Close all positions before market close
- Don't add to losing positions

### 3. Risk Management
- Never risk more than 4% in a single day
- Take breaks after 2 consecutive losses
- Review and adjust parameters monthly
- Keep a trading journal

### 4. Technical Setup
- Ensure stable internet connection
- Have backup power supply
- Monitor system logs regularly
- Test broker connectivity before market open

## Performance Expectations

### Realistic Targets
- **Win Rate**: 45-55%
- **Average Win**: 2.0-2.5%
- **Average Loss**: 1.0-1.5%
- **Monthly Return**: 5-10% (highly variable)

### Drawdown Expectations
- **Normal Drawdown**: 5-10%
- **Maximum Drawdown**: 15-20%
- **Recovery Time**: 2-4 weeks typically

## Troubleshooting

### No Trades Generated
- Check if market is trending (momentum strategy needs trends)
- Verify volume filter isn't too restrictive
- Review RSI levels (may be in neutral zone)

### Frequent Stop Losses
- Market may be too choppy for momentum strategy
- Consider widening stop loss slightly (1.75-2.0%)
- Reduce position size instead of widening stops

### Large Losses
- Verify max_daily_loss is being respected
- Check if stop losses are being executed
- Review broker connectivity logs

## Customization Guide

### For More Conservative Trading
```json
{
  "risk_per_trade": 1.0,
  "max_positions": 1,
  "max_daily_loss": 3.0,
  "take_profit": 2.0,
  "stop_loss": 1.25
}
```

### For More Aggressive Trading
```json
{
  "risk_per_trade": 2.0,
  "max_positions": 3,
  "max_daily_loss": 5.0,
  "take_profit": 3.0,
  "stop_loss": 2.0
}
```

### For Shorter Timeframe (5-min)
```json
{
  "timeframe": "5min",
  "indicator_period": 10,
  "take_profit": 1.5,
  "stop_loss": 1.0
}
```

## Support and Resources

### Documentation
- [User Guide](USER_GUIDE.md)
- [Risk Management Guide](indian_dashboard/TASK_7.3_SUMMARY.md)
- [Configuration Guide](indian_dashboard/TASK_7.8_SUMMARY.md)

### Testing
- Unit tests: `tests/test_banknifty_preset.py`
- Integration tests: `tests/test_banknifty_preset_integration.py`

### Getting Help
- Review logs in `logs/dashboard.log`
- Check broker adapter status
- Verify configuration validation

## Version History

### v1.0.0 (Current)
- Initial BANKNIFTY futures preset
- Momentum strategy with 15-min timeframe
- Risk per trade: 1.5%
- Comprehensive momentum indicators (RSI, ATR)
- Trailing stop loss enabled
- Paper trading enabled by default

## License and Disclaimer

This preset is provided for educational purposes. Trading involves risk of loss. Past performance does not guarantee future results. Always test strategies in paper trading mode before deploying real capital.

**Use at your own risk. The developers are not responsible for any trading losses.**
