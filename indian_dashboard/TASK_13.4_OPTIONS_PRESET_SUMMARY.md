# Task 13.4: Options Trading Preset - Implementation Summary

## Task Overview

Created a comprehensive options trading preset configuration for NIFTY/BANKNIFTY options with advanced Greeks management, risk controls, and strategy parameters.

## Implementation Details

### 1. Preset Configuration (config.py)

Updated the `options_trading` preset in `indian_dashboard/config.py` with:

**Basic Parameters:**
- Strategy: options_selling
- Timeframe: 15min
- Risk per trade: 2.0%
- Max positions: 3
- Max daily loss: 5.0%
- Base position size: ₹30,000

**Options-Specific Parameters:**
- Option type: both (CE and PE)
- Strategy type: credit_spread
- Min/Max premium: ₹50-₹200
- Days to expiry: 0-7 (weekly options)
- Delta range: [0.15, 0.35] (OTM options)
- IV percentile: 30-100
- Spread width: 100 points
- Max loss per spread: ₹5,000

**Greeks Management:**
- Max vega exposure: ₹10,000
- Max theta collection: ₹5,000/day
- Target theta: ₹3,000/day
- Max portfolio delta: ±0.5
- Delta hedge threshold: 0.3
- Greek calculation interval: 300s (5 min)

**Risk Management:**
- Profit target: 50% of max profit
- Stop loss: 200% of premium
- Adjustment threshold: 150% of premium
- Close before expiry: 60 minutes
- Underlying stop loss: 3.0%
- Margin multiplier: 1.5x
- Commission per lot: ₹40
- Slippage: 0.5%

**Position Management:**
- Roll options: True (2 days before expiry)
- Scale out: True (at 25%, 50%, 75%)
- Hedge delta: True
- Monitor underlying: True
- Rebalance frequency: daily

**Sample Instruments:**
- NIFTY 21000 CE (Call Option)
- NIFTY 21000 PE (Put Option)

### 2. Unit Tests (test_options_preset.py)

Created comprehensive unit tests covering:

1. **Preset Exists**: Verify preset is defined
2. **Preset Structure**: Validate all required fields present
3. **Preset Values**: Check parameter values are appropriate
4. **Instruments Configuration**: Validate option instruments structure
5. **Indian Market Specific**: Verify market-specific parameters
6. **Advanced Features**: Test options-specific features
7. **Greeks Management**: Validate Greeks parameters
8. **Risk Management**: Check risk management features

**Test Results**: ✅ 8/8 tests passed

### 3. Integration Tests (test_options_preset_integration.py)

Created integration tests covering:

1. **API Format**: Verify preset can be formatted for API
2. **JSON Serialization**: Test JSON serialization/deserialization
3. **Validation**: Validate preset passes validation logic
4. **Bot Compatibility**: Check compatibility with bot config
5. **Instruments Structure**: Validate instruments have correct structure
6. **Risk Calculations**: Test risk calculation logic
7. **Trading Hours**: Verify trading hours configuration
8. **Greeks Parameters**: Test Greeks-related parameters

**Test Results**: ✅ 8/8 tests passed

### 4. Documentation (OPTIONS_TRADING_PRESET.md)

Created comprehensive documentation including:

**Sections:**
- Overview and strategy description
- Key parameters table
- Options-specific parameters
- Strategy types (credit spreads, iron condors, naked selling)
- Risk management features
- Entry and exit criteria
- Position management (scaling, rolling, hedging)
- Capital requirements
- Expected returns
- Risks and considerations
- Best practices
- Testing checklist
- Customization options
- Resources and disclaimer

**Content:**
- 300+ lines of detailed documentation
- Parameter tables with descriptions
- Risk management guidelines
- Greeks management explanation
- Position sizing examples
- Testing checklist
- Best practices for options trading

## Files Created/Modified

### Modified Files:
1. `indian_dashboard/config.py` - Updated options_trading preset

### Created Files:
1. `indian_dashboard/tests/test_options_preset.py` - Unit tests (350+ lines)
2. `indian_dashboard/tests/test_options_preset_integration.py` - Integration tests (300+ lines)
3. `indian_dashboard/OPTIONS_TRADING_PRESET.md` - Documentation (400+ lines)
4. `indian_dashboard/TASK_13.4_OPTIONS_PRESET_SUMMARY.md` - This summary

## Key Features

### 1. Comprehensive Options Parameters
- 40+ options-specific parameters
- Greeks management (delta, vega, theta)
- IV percentile-based entry
- Delta-neutral approach
- Spread configuration

### 2. Advanced Risk Management
- Position-level risk controls
- Portfolio-level risk limits
- Greeks exposure limits
- Margin buffer requirements
- Commission and slippage modeling

### 3. Position Management
- Automatic rolling before expiry
- Scaling out at profit targets
- Delta hedging when threshold exceeded
- Underlying monitoring
- Daily rebalancing

### 4. Strategy Flexibility
- Credit spreads (defined risk)
- Iron condors (range-bound)
- Naked selling (experienced traders)
- Configurable spread width
- Adjustable profit targets

## Testing Results

### Unit Tests
```
✅ Preset Exists
✅ Preset Structure (19 required fields)
✅ Preset Values (all parameters valid)
✅ Instruments Configuration (2 sample options)
✅ Indian Market Specific (appropriate for NSE/BSE)
✅ Advanced Features (18 options-specific features)
✅ Greeks Management (4 Greeks parameters)
✅ Risk Management (7 risk features)

Result: 8/8 tests passed
```

### Integration Tests
```
✅ API Format (can be served via API)
✅ JSON Serialization (2503 bytes)
✅ Validation (passes all validation rules)
✅ Bot Compatibility (13 required fields present)
✅ Instruments Structure (correct NFO options format)
✅ Risk Calculations (conservative risk levels)
✅ Trading Hours (5.5 hours, avoids volatility)
✅ Greeks Parameters (5 Greeks parameters configured)

Result: 8/8 tests passed
```

## Risk Calculations

**Per Position:**
- Base size: ₹30,000
- Risk: 2.0% = ₹600
- Max loss per spread: ₹5,000

**Portfolio:**
- Max positions: 3
- Total capital at risk: ₹1,800
- Max daily loss: 5.0%
- Recommended capital: ₹1,50,000

**Greeks Limits:**
- Max portfolio delta: ±0.5
- Max vega exposure: ₹10,000
- Max portfolio vega: ₹15,000
- Target theta: ₹3,000/day

## Strategy Highlights

### Entry Criteria
1. IV percentile: 30-100 (elevated IV)
2. Delta range: 0.15-0.35 (OTM)
3. Premium: ₹50-₹200 per lot
4. Days to expiry: 0-7 days
5. Min credit: ₹100 per spread

### Exit Criteria
1. Profit target: 50% of max profit
2. Stop loss: 200% of premium
3. Time-based: 60 min before expiry
4. Underlying move: 3% against position
5. Adjustment: 150% of premium

### Position Management
1. Roll 2 days before expiry
2. Scale out at 25%, 50%, 75%
3. Hedge delta at ±0.3 threshold
4. Monitor underlying continuously
5. Rebalance daily

## Comparison with Other Presets

| Feature | NIFTY Futures | BANKNIFTY Futures | Equity Intraday | Options Trading |
|---------|---------------|-------------------|-----------------|-----------------|
| Risk/Trade | 1.0% | 1.5% | 0.5% | 2.0% |
| Max Positions | 2 | 2 | 5 | 3 |
| Max Daily Loss | 3.0% | 4.0% | 2.0% | 5.0% |
| Timeframe | 15min | 15min | 5min | 15min |
| Strategy | Trend Following | Momentum | Mean Reversion | Options Selling |
| Complexity | Medium | Medium | Low | High |
| Capital Required | ₹1L | ₹75k | ₹1L | ₹1.5L |
| Greeks Management | No | No | No | Yes |
| Defined Risk | No | No | No | Yes (spreads) |

## Usage Instructions

### 1. Load Preset in Dashboard
```javascript
// In dashboard, select "Options Trading" from preset dropdown
// Preset will populate all configuration fields
```

### 2. Customize Parameters
- Update instrument strikes based on current market
- Adjust delta range for more/less OTM
- Modify spread width for risk tolerance
- Change profit target percentage

### 3. Verify Configuration
- Check margin requirements
- Verify Greeks limits are appropriate
- Ensure capital is sufficient
- Review risk parameters

### 4. Start with Paper Trading
- Enable paper_trading: true
- Test for 2+ weeks
- Monitor Greeks behavior
- Verify position management

### 5. Go Live
- Disable paper trading
- Start with 1 lot per position
- Monitor closely
- Adjust based on experience

## Best Practices

1. **Understand Options**: Learn Greeks, IV, time decay
2. **Start Small**: Begin with 1 lot per position
3. **Paper Trade First**: Test for at least 2 weeks
4. **Monitor Greeks**: Check delta, vega, theta regularly
5. **Take Profits**: Close at 50% profit target
6. **Cut Losses**: Exit at stop loss, don't hope
7. **Avoid Events**: Don't trade around major announcements
8. **Maintain Buffer**: Keep 1.5x margin requirement
9. **Close Before Expiry**: Exit 60 min before expiry
10. **Keep Learning**: Study options theory continuously

## Risks and Warnings

⚠️ **High Risk**: Options trading involves substantial risk
⚠️ **Capital Loss**: You can lose your entire investment
⚠️ **Complexity**: Requires understanding of Greeks
⚠️ **Margin Calls**: Positions can move against you quickly
⚠️ **Assignment Risk**: Short options can be assigned early
⚠️ **Gap Risk**: Overnight gaps can cause large losses
⚠️ **Volatility Risk**: IV expansion can cause mark-to-market losses

## Next Steps

1. ✅ Preset configuration created
2. ✅ Unit tests implemented and passing
3. ✅ Integration tests implemented and passing
4. ✅ Documentation created
5. ⏭️ Test preset loading in dashboard UI
6. ⏭️ Verify API endpoint returns preset correctly
7. ⏭️ Test with paper trading adapter
8. ⏭️ Create video tutorial for options trading

## Verification Checklist

- [x] Preset exists in PRESET_CONFIGS
- [x] All required fields present
- [x] Options-specific parameters configured
- [x] Greeks management parameters set
- [x] Risk management features implemented
- [x] Sample instruments included
- [x] Unit tests created and passing (8/8)
- [x] Integration tests created and passing (8/8)
- [x] Documentation created (400+ lines)
- [x] Parameter descriptions provided
- [x] Risk calculations documented
- [x] Best practices documented
- [x] Testing checklist provided
- [x] Disclaimer included

## Conclusion

The options trading preset has been successfully implemented with:
- ✅ Comprehensive configuration (40+ parameters)
- ✅ Advanced Greeks management
- ✅ Robust risk controls
- ✅ Flexible strategy options
- ✅ Complete test coverage (16/16 tests passing)
- ✅ Detailed documentation (400+ lines)

The preset is ready for testing and can be loaded through the dashboard UI. Users should start with paper trading and thoroughly understand options mechanics before going live.

---

**Status**: ✅ Complete  
**Tests**: ✅ 16/16 Passing  
**Documentation**: ✅ Complete  
**Ready for**: Testing in Dashboard UI
