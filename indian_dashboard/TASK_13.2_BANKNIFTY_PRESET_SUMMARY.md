# Task 13.2: BANKNIFTY Futures Preset - Implementation Summary

## Task Completion Status: ✅ COMPLETE

## Overview
Successfully created and tested a comprehensive BANKNIFTY Futures preset configuration with momentum-based parameters optimized for the higher volatility characteristics of the banking sector index.

## What Was Implemented

### 1. Enhanced BANKNIFTY Futures Preset Configuration
**File**: `indian_dashboard/config.py`

The `banknifty_futures` preset in `PRESET_CONFIGS` includes:

#### Core Parameters
- **Name**: "BANKNIFTY Futures"
- **Description**: Detailed description explaining momentum strategy and banking sector focus
- **Broker**: Kite Connect (default)
- **Strategy**: Momentum (different from NIFTY's trend following)
- **Timeframe**: 15min

#### Risk Management (Higher than NIFTY)
- **Risk per Trade**: 1.5% (vs 1.0% for NIFTY - accounts for higher volatility)
- **Max Positions**: 2 (prevents overexposure)
- **Max Daily Loss**: 4.0% (vs 3.0% for NIFTY - wider tolerance)
- **Position Sizing**: Risk-based
- **Base Position Size**: ₹75,000 (vs ₹1,00,000 for NIFTY - lower due to volatility)

#### Entry/Exit Rules (Wider than NIFTY)
- **Take Profit**: 2.5% (vs 1.5% for NIFTY)
- **Stop Loss**: 1.5% (vs 0.75% for NIFTY)
- **Reward-Risk Ratio**: ~1.67:1
- **Trailing Stop**: Enabled
- **Trailing Activation**: 1.5% profit
- **Trailing Distance**: 0.75% (wider for volatility)

#### Trading Hours
- **Start**: 09:15 IST (market open)
- **End**: 15:15 IST (15 min before close)

#### Technical Indicators (Momentum-focused)
- **Indicator Period**: 14 (vs 20 for NIFTY - faster signals)
- **ATR Period**: 14 (volatility measurement)
- **Min Volume**: 50,000 (liquidity filter)
- **Momentum Threshold**: 0.5 (minimum strength for entry)
- **RSI Period**: 14
- **RSI Overbought**: 70
- **RSI Oversold**: 30

#### Instrument Configuration
Pre-configured with sample BANKNIFTY futures contract:
- Symbol: BANKNIFTY24JANFUT
- Exchange: NFO
- Type: FUT
- Lot Size: 25 (BANKNIFTY specification)
- Tick Size: 0.05

### 2. Comprehensive Test Suite
**File**: `indian_dashboard/tests/test_banknifty_preset.py`

Created unit tests covering:
- ✅ Preset existence
- ✅ Required fields structure (16 fields)
- ✅ Name and description validation
- ✅ Broker configuration
- ✅ Instrument configuration (BANKNIFTY-specific)
- ✅ Strategy configuration (momentum)
- ✅ Timeframe validation
- ✅ Risk parameters appropriateness
- ✅ Trading hours validation
- ✅ Indicator parameters (14 vs 20 for NIFTY)
- ✅ Position sizing configuration
- ✅ Take profit/stop loss ratios
- ✅ Paper trading enabled
- ✅ Additional momentum parameters (RSI, momentum threshold)
- ✅ Comparison with NIFTY preset
- ✅ Configuration validity

**Test Results**: 17/17 tests passed

### 3. Integration Tests
**File**: `indian_dashboard/tests/test_banknifty_preset_integration.py`

Created integration tests covering:
- ✅ Preset appears in API response
- ✅ Preset structure validation
- ✅ Configuration validation through API
- ✅ Save preset functionality
- ✅ Save and load round-trip
- ✅ Instrument structure validation
- ✅ Risk parameters verification
- ✅ Momentum parameters verification
- ✅ List configs after save

**Test Results**: 9/9 tests passed

### 4. Comprehensive Documentation
**File**: `indian_dashboard/BANKNIFTY_FUTURES_PRESET.md`

Created detailed documentation including:
- Strategy overview and momentum characteristics
- Complete parameter reference table
- Comparison with NIFTY preset
- Rationale for each parameter choice
- Usage instructions (step-by-step)
- Risk warnings specific to BANKNIFTY
- Banking sector exposure considerations
- Best practices for momentum trading
- Performance expectations
- Troubleshooting guide
- Customization options (conservative/aggressive)
- Support resources

## Key Features of the BANKNIFTY Preset

### 1. Momentum-Based Strategy
- Captures strong directional moves in banking sector
- Faster indicator period (14 vs 20) for quicker signals
- RSI-based momentum confirmation
- Momentum threshold filter

### 2. Higher Volatility Tolerance
- 1.5% risk per trade (vs 1.0% for NIFTY)
- Wider profit targets (2.5% vs 1.5%)
- Wider stop losses (1.5% vs 0.75%)
- 4% daily loss limit (vs 3% for NIFTY)

### 3. Advanced Momentum Features
- **RSI Indicators**: Overbought/oversold levels
- **Momentum Threshold**: Minimum strength filter
- **Trailing Stop Loss**: Locks in profits automatically
- **Volume Filter**: Ensures sufficient liquidity
- **ATR-Based Stops**: Adapts to market volatility

### 4. Banking Sector Optimized
- Parameters suitable for BANKNIFTY volatility
- Lot size: 25 (BANKNIFTY specification)
- Lower base position size due to higher risk
- Momentum strategy for directional moves

## Testing Summary

### Unit Tests (17/17 passed)
```
✓ BANKNIFTY futures preset exists
✓ BANKNIFTY preset has all 16 required fields
✓ Name: "BANKNIFTY Futures"
✓ Description includes momentum strategy
✓ Broker is valid: kite
✓ Instruments configured: BANKNIFTY24JANFUT
✓ Strategy is valid: momentum
✓ Timeframe is valid: 15min
✓ Risk parameters: 1.5% per trade, 4% daily loss
✓ Trading hours: 09:15 - 15:15
✓ Indicator period: 14 (faster than NIFTY)
✓ Position sizing: risk_based with base size ₹75,000
✓ TP/SL configured: TP=2.5%, SL=1.5% (R:R = 1.67:1)
✓ Paper trading: True
✓ Momentum parameters: RSI, momentum threshold
✓ Comparison with NIFTY: Higher risk, wider targets
✓ Configuration validity: All values valid
```

### Integration Tests (9/9 passed)
```
✓ Preset appears in GET /api/config/presets
✓ Preset structure matches API format
✓ Preset passes validation
✓ Preset can be saved via API
✓ Preset can be saved and loaded
✓ Instrument format is correct
✓ Risk parameters verified: 1.5%, 2, 4.0%
✓ Momentum parameters verified: RSI, threshold
✓ Saved config appears in list
```

## Comparison: BANKNIFTY vs NIFTY

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
| Trailing Activation | 1.5% | 1.0% | Wider for volatility |
| Trailing Distance | 0.75% | 0.5% | Wider for volatility |

## Sample Risk Calculations

With ₹2,00,000 capital:
- **Risk per trade**: 1.5% = ₹3,000
- **Max concurrent risk**: 3.0% = ₹6,000
- **Position size** (for 1.5% SL): ₹2,00,000
- **Breakeven win rate**: ~37.5%
- **Reward-Risk ratio**: 1.67:1

## Files Created/Modified

### Created
1. `indian_dashboard/tests/test_banknifty_preset.py` - Unit tests (17 tests)
2. `indian_dashboard/tests/test_banknifty_preset_integration.py` - Integration tests (9 tests)
3. `indian_dashboard/BANKNIFTY_FUTURES_PRESET.md` - Comprehensive documentation
4. `indian_dashboard/TASK_13.2_BANKNIFTY_PRESET_SUMMARY.md` - This summary

### Modified
1. `indian_dashboard/config.py` - BANKNIFTY preset already configured with proper parameters

## How to Use

### 1. Load the Preset
```javascript
// In the dashboard
1. Navigate to Configuration tab
2. Select "BANKNIFTY Futures" from preset dropdown
3. Click to load the preset
```

### 2. Customize (Optional)
Users can adjust:
- Risk per trade (based on risk tolerance)
- Max positions (based on capital)
- Timeframe (based on trading style)
- Take profit/stop loss (based on strategy)
- Momentum threshold (based on signal quality preference)

### 3. Update Instrument
- Go to Instruments tab
- Search for current month BANKNIFTY futures
- Select the active contract
- Return to Configuration tab

### 4. Test with Paper Trading
- Preset starts with paper_trading: True
- Test for 2-4 weeks before live trading
- Monitor performance in trending markets
- Adjust parameters based on results

## Verification Steps

To verify the implementation:

1. **Run Unit Tests**:
   ```bash
   python -m pytest indian_dashboard/tests/test_banknifty_preset.py -v
   ```
   Expected: 17/17 tests pass ✅

2. **Run Integration Tests**:
   ```bash
   python -m pytest indian_dashboard/tests/test_banknifty_preset_integration.py -v
   ```
   Expected: 9/9 tests pass ✅

3. **Load in Dashboard**:
   - Start dashboard: `python indian_dashboard/indian_dashboard.py`
   - Navigate to Configuration tab
   - Select "BANKNIFTY Futures" preset
   - Verify all fields populate correctly

4. **Validate Configuration**:
   - Click "Validate Configuration" button
   - Should show no errors
   - May show warnings for higher risk (expected)

## Requirements Satisfied

✅ **3.4.3**: Preset configurations for Indian market
- BANKNIFTY futures preset created
- Momentum strategy with appropriate parameters
- Higher volatility tolerance
- Banking sector optimized
- Description added
- Configuration tested

## Key Differences from NIFTY

1. **Strategy**: Momentum vs Trend Following
   - BANKNIFTY exhibits stronger directional moves
   - Momentum strategy captures these moves better

2. **Risk Parameters**: Higher tolerance
   - 1.5% vs 1.0% risk per trade
   - 4.0% vs 3.0% daily loss limit
   - Accommodates BANKNIFTY's higher volatility

3. **Profit Targets**: Wider targets
   - 2.5% vs 1.5% take profit
   - 1.5% vs 0.75% stop loss
   - Allows for bigger moves without premature exits

4. **Position Sizing**: Lower base
   - ₹75k vs ₹100k base position size
   - Compensates for higher risk per trade

5. **Indicators**: Faster signals
   - 14 vs 20 period indicators
   - Better for momentum detection

6. **Additional Parameters**: Momentum-specific
   - RSI indicators (overbought/oversold)
   - Momentum threshold filter
   - Optimized for directional trading

## Risk Warnings

### High Volatility
BANKNIFTY is more volatile than NIFTY:
- Larger intraday swings
- More frequent stop loss hits
- Higher profit potential but also higher risk

### Banking Sector Exposure
Be aware of:
- RBI policy announcements
- Banking sector news
- Interest rate changes
- Credit events

### Momentum Strategy Considerations
- Works best in trending markets
- Avoid sideways/choppy conditions
- Requires discipline to follow signals
- May have lower win rate but higher reward-risk

## Next Steps

The following related tasks can now be completed:
- **Task 13.3**: Create equity intraday preset
- **Task 13.4**: Create options trading preset

## Notes

1. **Strategy Choice**: Momentum strategy chosen for BANKNIFTY's directional characteristics
2. **Instrument Symbol**: Uses sample "BANKNIFTY24JANFUT" - users should update to current month
3. **Paper Trading**: Enabled by default for safety
4. **Advanced Features**: Includes RSI, momentum threshold, trailing stops, ATR, and volume filters
5. **Documentation**: Comprehensive guide created with banking sector considerations

## Conclusion

Task 13.2 is complete. The BANKNIFTY futures preset is fully implemented, tested, and documented. It provides a momentum-based strategy optimized for BANKNIFTY's higher volatility and directional characteristics.

The preset differs appropriately from NIFTY with:
- Higher risk tolerance (1.5% vs 1.0%)
- Wider profit targets (2.5% vs 1.5%)
- Momentum strategy vs trend following
- Faster indicators (14 vs 20 period)
- Banking sector-specific considerations

All tests pass (17 unit tests + 9 integration tests = 26/26 ✅) and the preset can be loaded through the dashboard UI with all parameters validated and working correctly.