# Options Trading Preset Configuration

## Overview

The Options Trading preset is designed for options selling strategies on NIFTY and BANKNIFTY with a focus on premium collection through credit spreads and iron condors. This preset implements a delta-neutral approach with comprehensive Greeks management and risk controls.

## Strategy Description

**Strategy Type**: Options Selling (Credit Spreads / Iron Condors)

**Target Market**: NIFTY and BANKNIFTY weekly options

**Approach**: 
- Sell out-of-the-money (OTM) options to collect premium
- Use credit spreads to define maximum risk
- Maintain delta-neutral portfolio
- Profit from time decay (theta)
- Manage Greeks (delta, vega, theta) actively

## Key Parameters

### Basic Configuration

| Parameter | Value | Description |
|-----------|-------|-------------|
| Strategy | options_selling | Options premium selling strategy |
| Timeframe | 15min | Monitor positions every 15 minutes |
| Broker | kite | Zerodha Kite Connect |
| Paper Trading | True | Start with paper trading for testing |

### Risk Management

| Parameter | Value | Description |
|-----------|-------|-------------|
| Risk per Trade | 2.0% | Risk 2% of capital per position |
| Max Positions | 3 | Maximum 3 option positions |
| Max Daily Loss | 5.0% | Stop trading if 5% daily loss reached |
| Base Position Size | ₹30,000 | Capital allocated per position |

### Trading Hours

| Parameter | Value | Description |
|-----------|-------|-------------|
| Start Time | 09:30 | Start after initial volatility settles |
| End Time | 15:00 | Close positions 30 min before expiry |

### Profit Targets & Stop Loss

| Parameter | Value | Description |
|-----------|-------|-------------|
| Take Profit | 50% | Close at 50% of premium collected |
| Stop Loss | 200% | Exit if loss reaches 200% of premium |
| Profit Target % | 50% | Close at 50% of max profit |

## Options-Specific Parameters

### Premium Selection

| Parameter | Value | Description |
|-----------|-------|-------------|
| Min Premium | ₹50 | Minimum premium to collect per lot |
| Max Premium | ₹200 | Maximum premium (avoid deep ITM) |
| Min Credit Received | ₹100 | Minimum credit for credit spreads |

### Expiry Management

| Parameter | Value | Description |
|-----------|-------|-------------|
| Min Days to Expiry | 0 | Can trade on expiry day |
| Max Days to Expiry | 7 | Focus on weekly options |
| Close Before Expiry | 60 min | Close positions 60 min before expiry |
| Roll Options | True | Roll profitable positions before expiry |
| Roll Days Before Expiry | 2 | Roll 2 days before expiry |

### Delta Management

| Parameter | Value | Description |
|-----------|-------|-------------|
| Delta Range | [0.15, 0.35] | Target delta for sold options (OTM) |
| Hedge Delta | True | Hedge delta exposure with futures |
| Delta Hedge Threshold | 0.3 | Hedge when portfolio delta exceeds ±0.3 |
| Max Portfolio Delta | ±0.5 | Maximum portfolio delta |

### Volatility (IV) Management

| Parameter | Value | Description |
|-----------|-------|-------------|
| IV Percentile Min | 30 | Minimum IV percentile for entry |
| IV Percentile Max | 100 | Maximum IV percentile |
| Max Vega Exposure | ₹10,000 | Maximum vega exposure |
| Max Portfolio Vega | ₹15,000 | Maximum portfolio vega |

### Theta Collection

| Parameter | Value | Description |
|-----------|-------|-------------|
| Max Theta Collection | ₹5,000 | Target theta collection per day |
| Target Theta | ₹3,000 | Daily theta collection target |

### Spread Configuration

| Parameter | Value | Description |
|-----------|-------|-------------|
| Strategy Type | credit_spread | Use credit spreads for defined risk |
| Spread Width | 100 points | Spread width (e.g., 21000-21100) |
| Max Loss per Spread | ₹5,000 | Maximum loss per spread |
| Max Spread Width % | 5% | Max spread width as % of underlying |

### Position Adjustments

| Parameter | Value | Description |
|-----------|-------|-------------|
| Adjustment Threshold | 150% | Adjust if loss reaches 150% of premium |
| Scale Out | True | Take partial profits |
| Scale Out Levels | [25%, 50%, 75%] | Profit taking levels |

### Underlying Monitoring

| Parameter | Value | Description |
|-----------|-------|-------------|
| Underlying Symbol | NIFTY | Primary underlying |
| Monitor Underlying | True | Monitor underlying price movement |
| Underlying Stop Loss | 3.0% | Exit if underlying moves 3% against |

### Greeks Calculation

| Parameter | Value | Description |
|-----------|-------|-------------|
| Greek Calculation Interval | 300s | Recalculate Greeks every 5 minutes |
| Rebalance Frequency | daily | Rebalance portfolio daily |

### Cost & Slippage

| Parameter | Value | Description |
|-----------|-------|-------------|
| Commission per Lot | ₹40 | Estimated commission per lot |
| Slippage % | 0.5% | Expected slippage |
| Margin Multiplier | 1.5x | Keep 1.5x margin as buffer |

## Instruments

The preset includes sample NIFTY options:

1. **NIFTY 21000 CE** (Call Option)
   - Exchange: NFO
   - Lot Size: 50
   - Strike: 21000

2. **NIFTY 21000 PE** (Put Option)
   - Exchange: NFO
   - Lot Size: 50
   - Strike: 21000

**Note**: These are example instruments. Update with current month expiry and appropriate strikes based on market conditions.

## Strategy Types Supported

### 1. Credit Spread
- Sell OTM option
- Buy further OTM option for protection
- Defined risk, limited profit
- Example: Sell 21000 CE, Buy 21100 CE

### 2. Iron Condor
- Sell OTM call spread + Sell OTM put spread
- Profit from range-bound market
- Defined risk on both sides
- Example: Sell 21000-21100 CE spread + Sell 20900-20800 PE spread

### 3. Naked Selling (Not Recommended)
- Sell OTM options without protection
- Unlimited risk
- Higher premium collection
- Only for experienced traders with large capital

## Risk Management Features

### Position-Level Risk
- Maximum loss per spread: ₹5,000
- Stop loss at 200% of premium collected
- Adjustment threshold at 150% of premium

### Portfolio-Level Risk
- Maximum 3 positions
- Maximum daily loss: 5%
- Portfolio delta limit: ±0.5
- Portfolio vega limit: ₹15,000

### Greeks Management
- Monitor delta, vega, theta continuously
- Hedge delta exposure when threshold exceeded
- Limit vega exposure to control volatility risk
- Target positive theta for time decay profit

## Entry Criteria

1. **IV Percentile**: Between 30-100 (prefer elevated IV)
2. **Delta Range**: 0.15-0.35 (OTM options)
3. **Premium**: Between ₹50-₹200 per lot
4. **Days to Expiry**: 0-7 days (weekly options)
5. **Credit Received**: Minimum ₹100 per spread

## Exit Criteria

1. **Profit Target**: Close at 50% of max profit
2. **Stop Loss**: Exit at 200% of premium collected
3. **Time-Based**: Close 60 min before expiry
4. **Underlying Movement**: Exit if underlying moves 3% against position
5. **Adjustment**: Adjust position if loss reaches 150% of premium

## Position Management

### Scaling Out
- Take 25% profit at 25% of max profit
- Take 50% profit at 50% of max profit
- Take remaining at 75% of max profit

### Rolling
- Roll positions 2 days before expiry if profitable
- Roll to next weekly expiry
- Maintain similar delta and premium

### Hedging
- Hedge delta when portfolio delta exceeds ±0.3
- Use NIFTY/BANKNIFTY futures for hedging
- Rebalance daily

## Capital Requirements

### Minimum Capital
- **Per Position**: ₹30,000
- **Total (3 positions)**: ₹90,000
- **Recommended**: ₹1,50,000 (with margin buffer)

### Margin Requirements
- Credit spreads: Lower margin (defined risk)
- Naked selling: Higher margin (unlimited risk)
- Keep 1.5x margin requirement as buffer

## Expected Returns

### Conservative Estimate
- **Monthly Return**: 3-5% of capital
- **Win Rate**: 70-80%
- **Average Win**: ₹2,000-₹3,000
- **Average Loss**: ₹3,000-₹5,000
- **Risk-Reward**: Defined by spread width

### Theta Decay
- **Daily Theta Collection**: ₹3,000 target
- **Weekly Theta**: ₹15,000-₹20,000
- **Monthly Theta**: ₹60,000-₹80,000

## Risks & Considerations

### Market Risks
1. **Gap Risk**: Large overnight gaps can cause losses
2. **Volatility Expansion**: IV spike can cause mark-to-market losses
3. **Trending Markets**: Directional moves can breach spreads
4. **Expiry Day**: High volatility and pin risk

### Strategy Risks
1. **Assignment Risk**: Early assignment on short options
2. **Liquidity Risk**: Wide spreads in illiquid options
3. **Margin Risk**: Margin calls if positions move against
4. **Greeks Risk**: Unmanaged Greeks can amplify losses

### Mitigation
- Use credit spreads for defined risk
- Monitor Greeks continuously
- Close positions before expiry
- Maintain adequate margin buffer
- Avoid earnings and major events

## Best Practices

1. **Start with Paper Trading**: Test strategy before live trading
2. **Small Position Sizes**: Start with 1 lot per position
3. **Avoid Expiry Day**: Close positions 60 min before expiry
4. **Monitor Greeks**: Check delta, vega, theta regularly
5. **Hedge When Needed**: Don't let delta exposure grow
6. **Take Profits**: Close at 50% profit, don't be greedy
7. **Cut Losses**: Exit at stop loss, don't hope for recovery
8. **Avoid Events**: Don't trade around RBI policy, budget, etc.
9. **Maintain Journal**: Track all trades and learn from them
10. **Continuous Learning**: Study options theory and Greeks

## Testing Checklist

Before going live with this preset:

- [ ] Verify all parameters are appropriate for your risk tolerance
- [ ] Test with paper trading for at least 2 weeks
- [ ] Understand options Greeks (delta, gamma, vega, theta)
- [ ] Know how to calculate margin requirements
- [ ] Understand assignment and exercise mechanics
- [ ] Have sufficient capital (minimum ₹1,50,000 recommended)
- [ ] Set up alerts for position monitoring
- [ ] Understand tax implications of options trading
- [ ] Have a plan for different market scenarios
- [ ] Know when to adjust, roll, or exit positions

## Customization

You can customize this preset by modifying:

1. **Underlying**: Change from NIFTY to BANKNIFTY or FINNIFTY
2. **Strategy Type**: Switch between credit spreads, iron condors, or naked selling
3. **Delta Range**: Adjust for more/less OTM options
4. **Spread Width**: Wider spreads = more risk, more premium
5. **Days to Expiry**: Trade monthly instead of weekly options
6. **Profit Target**: Adjust from 50% to 30% or 70%
7. **Position Size**: Increase/decrease based on capital

## Resources

- **Options Theory**: Learn about Greeks, IV, time decay
- **Broker Margin Calculator**: Calculate margin requirements
- **IV Rank/Percentile**: Check current IV levels
- **Options Chain**: Analyze strikes, premiums, OI
- **Greeks Calculator**: Calculate position Greeks
- **P&L Calculator**: Estimate profit/loss scenarios

## Disclaimer

Options trading involves substantial risk and is not suitable for all investors. The risk of loss in trading options can be substantial. You should carefully consider whether trading is appropriate for you in light of your experience, objectives, financial resources, and other relevant circumstances. This preset is for educational purposes only and does not constitute financial advice.

---

**Version**: 1.0.0  
**Last Updated**: 2024-02-18  
**Status**: Ready for Testing
