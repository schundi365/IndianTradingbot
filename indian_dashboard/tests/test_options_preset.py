"""
Test Options Trading Preset Configuration
Validates that the options trading preset has appropriate parameters
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from indian_dashboard.config import PRESET_CONFIGS


def test_options_preset_exists():
    """Test that options trading preset exists"""
    assert "options_trading" in PRESET_CONFIGS, "Options trading preset not found"
    print("✓ Options trading preset exists")


def test_options_preset_structure():
    """Test that options preset has all required fields"""
    preset = PRESET_CONFIGS["options_trading"]
    
    required_fields = [
        "name", "description", "broker", "instruments", "strategy",
        "timeframe", "risk_per_trade", "max_positions", "max_daily_loss",
        "trading_hours", "indicator_period", "position_sizing",
        "base_position_size", "take_profit", "stop_loss", "paper_trading",
        "log_level", "data_refresh_interval", "enable_notifications"
    ]
    
    for field in required_fields:
        assert field in preset, f"Missing required field: {field}"
    
    print(f"✓ Options preset has all {len(required_fields)} required fields")


def test_options_preset_values():
    """Test that options preset has appropriate values"""
    preset = PRESET_CONFIGS["options_trading"]
    
    # Test name and description
    assert preset["name"] == "Options Trading"
    assert len(preset["description"]) > 50, "Description should be detailed"
    print("✓ Name and description are appropriate")
    
    # Test broker
    assert preset["broker"] in ["kite", "alice_blue", "angel_one", "upstox", "paper"]
    print(f"✓ Broker is valid: {preset['broker']}")
    
    # Test strategy
    assert preset["strategy"] in ["trend_following", "momentum", "mean_reversion", "options_selling"]
    print(f"✓ Strategy is valid: {preset['strategy']}")
    
    # Test timeframe
    assert preset["timeframe"] in ["1min", "5min", "15min", "1hour", "1day"]
    print(f"✓ Timeframe is valid: {preset['timeframe']}")
    
    # Test risk parameters
    assert 0 < preset["risk_per_trade"] <= 10, "Risk per trade should be between 0 and 10%"
    assert 0 < preset["max_daily_loss"] <= 15, "Max daily loss should be between 0 and 15%"
    assert preset["max_positions"] > 0, "Max positions should be positive"
    print(f"✓ Risk parameters are appropriate:")
    print(f"  - Risk per trade: {preset['risk_per_trade']}%")
    print(f"  - Max daily loss: {preset['max_daily_loss']}%")
    print(f"  - Max positions: {preset['max_positions']}")
    
    # Test trading hours
    assert "start" in preset["trading_hours"]
    assert "end" in preset["trading_hours"]
    assert preset["trading_hours"]["start"] >= "09:15", "Should start after market open"
    assert preset["trading_hours"]["end"] <= "15:30", "Should close before market close"
    print(f"✓ Trading hours are valid: {preset['trading_hours']['start']} - {preset['trading_hours']['end']}")
    
    # Test position sizing
    assert preset["position_sizing"] in ["fixed", "percentage", "risk_based"]
    assert preset["base_position_size"] > 0
    print(f"✓ Position sizing: {preset['position_sizing']} with base size ₹{preset['base_position_size']:,}")
    
    # Test take profit and stop loss (options have different dynamics)
    assert preset["take_profit"] > 0
    assert preset["stop_loss"] > 0
    # For options, stop loss can be higher than take profit (e.g., 50% profit, 200% loss)
    print(f"✓ TP/SL configured: TP={preset['take_profit']}%, SL={preset['stop_loss']}%")
    
    # Test paper trading
    assert isinstance(preset["paper_trading"], bool)
    print(f"✓ Paper trading: {preset['paper_trading']}")


def test_options_preset_instruments():
    """Test that options preset has instrument configuration"""
    preset = PRESET_CONFIGS["options_trading"]
    
    assert isinstance(preset["instruments"], list)
    
    if len(preset["instruments"]) > 0:
        # Validate option instrument structure
        for instrument in preset["instruments"]:
            assert "symbol" in instrument
            assert "exchange" in instrument
            assert instrument["exchange"] == "NFO", "Options trade on NFO"
            assert instrument["instrument_type"] in ["CE", "PE"], "Should be call or put option"
            
            if "lot_size" in instrument:
                assert instrument["lot_size"] > 0, "Lot size should be positive"
            
            if "strike" in instrument:
                assert instrument["strike"] > 0, "Strike price should be positive"
            
            if "expiry" in instrument:
                assert len(instrument["expiry"]) > 0, "Expiry date should be specified"
        
        print(f"✓ Instruments configured: {len(preset['instruments'])} instrument(s)")
        for i, instrument in enumerate(preset["instruments"], 1):
            print(f"  {i}. {instrument['symbol']} ({instrument['instrument_type']})")
            print(f"     Exchange: {instrument['exchange']}")
            if "strike" in instrument:
                print(f"     Strike: {instrument['strike']}")
            if "lot_size" in instrument:
                print(f"     Lot size: {instrument['lot_size']}")
    else:
        print("✓ Instruments list is empty (will be populated dynamically)")


def test_options_preset_indian_market_specific():
    """Test options-specific parameters for Indian market"""
    preset = PRESET_CONFIGS["options_trading"]
    
    # Options trading requires specific risk management
    assert preset["max_positions"] <= 5, "Limit options positions for risk management"
    assert preset["risk_per_trade"] <= 5.0, "Conservative risk for options trading"
    
    # Trading hours should avoid extreme volatility
    assert preset["trading_hours"]["start"] >= "09:30", "Avoid opening volatility"
    
    print("✓ Options-specific parameters are appropriate for Indian market")


def test_options_preset_advanced_features():
    """Test options-specific advanced features"""
    preset = PRESET_CONFIGS["options_trading"]
    
    advanced_features = []
    
    # Options-specific parameters
    if "option_type" in preset:
        assert preset["option_type"] in ["CE", "PE", "both"]
        advanced_features.append(f"Option type: {preset['option_type']}")
    
    if "strategy_type" in preset:
        assert preset["strategy_type"] in ["credit_spread", "iron_condor", "naked_selling", "covered_call"]
        advanced_features.append(f"Strategy type: {preset['strategy_type']}")
    
    if "min_premium" in preset:
        assert preset["min_premium"] > 0
        advanced_features.append(f"Min premium: ₹{preset['min_premium']}")
    
    if "max_premium" in preset:
        assert preset["max_premium"] > preset.get("min_premium", 0)
        advanced_features.append(f"Max premium: ₹{preset['max_premium']}")
    
    if "min_days_to_expiry" in preset:
        assert preset["min_days_to_expiry"] >= 0
        advanced_features.append(f"Min days to expiry: {preset['min_days_to_expiry']}")
    
    if "max_days_to_expiry" in preset:
        assert preset["max_days_to_expiry"] > preset.get("min_days_to_expiry", 0)
        advanced_features.append(f"Max days to expiry: {preset['max_days_to_expiry']}")
    
    if "delta_range" in preset:
        assert isinstance(preset["delta_range"], list)
        assert len(preset["delta_range"]) == 2
        assert 0 <= preset["delta_range"][0] < preset["delta_range"][1] <= 1
        advanced_features.append(f"Delta range: {preset['delta_range']}")
    
    if "iv_percentile_min" in preset:
        assert 0 <= preset["iv_percentile_min"] <= 100
        advanced_features.append(f"IV percentile min: {preset['iv_percentile_min']}")
    
    if "spread_width" in preset:
        assert preset["spread_width"] > 0
        advanced_features.append(f"Spread width: {preset['spread_width']} points")
    
    if "max_loss_per_spread" in preset:
        assert preset["max_loss_per_spread"] > 0
        advanced_features.append(f"Max loss per spread: ₹{preset['max_loss_per_spread']:,}")
    
    if "profit_target_percent" in preset:
        assert 0 < preset["profit_target_percent"] <= 100
        advanced_features.append(f"Profit target: {preset['profit_target_percent']}%")
    
    if "close_before_expiry_minutes" in preset:
        assert preset["close_before_expiry_minutes"] > 0
        advanced_features.append(f"Close before expiry: {preset['close_before_expiry_minutes']} min")
    
    if "hedge_delta" in preset:
        assert isinstance(preset["hedge_delta"], bool)
        advanced_features.append(f"Hedge delta: {preset['hedge_delta']}")
    
    if "delta_hedge_threshold" in preset:
        assert 0 < preset["delta_hedge_threshold"] <= 1
        advanced_features.append(f"Delta hedge threshold: {preset['delta_hedge_threshold']}")
    
    if "roll_options" in preset:
        assert isinstance(preset["roll_options"], bool)
        advanced_features.append(f"Roll options: {preset['roll_options']}")
    
    if "underlying_symbol" in preset:
        assert preset["underlying_symbol"] in ["NIFTY", "BANKNIFTY", "FINNIFTY"]
        advanced_features.append(f"Underlying: {preset['underlying_symbol']}")
    
    if "max_portfolio_delta" in preset:
        assert 0 < preset["max_portfolio_delta"] <= 1
        advanced_features.append(f"Max portfolio delta: ±{preset['max_portfolio_delta']}")
    
    if "target_theta" in preset:
        assert preset["target_theta"] > 0
        advanced_features.append(f"Target theta: ₹{preset['target_theta']:,}/day")
    
    if advanced_features:
        print("✓ Options-specific advanced features configured:")
        for feature in advanced_features:
            print(f"  - {feature}")
    else:
        print("✓ No advanced features (basic configuration)")


def test_options_preset_greeks_management():
    """Test Greeks management parameters"""
    preset = PRESET_CONFIGS["options_trading"]
    
    greeks_features = []
    
    if "max_vega_exposure" in preset:
        assert preset["max_vega_exposure"] > 0
        greeks_features.append(f"Max vega: ₹{preset['max_vega_exposure']:,}")
    
    if "max_theta_collection" in preset:
        assert preset["max_theta_collection"] > 0
        greeks_features.append(f"Max theta collection: ₹{preset['max_theta_collection']:,}")
    
    if "max_portfolio_vega" in preset:
        assert preset["max_portfolio_vega"] > 0
        greeks_features.append(f"Max portfolio vega: ₹{preset['max_portfolio_vega']:,}")
    
    if "greek_calculation_interval" in preset:
        assert preset["greek_calculation_interval"] > 0
        greeks_features.append(f"Greeks calc interval: {preset['greek_calculation_interval']}s")
    
    if greeks_features:
        print("✓ Greeks management configured:")
        for feature in greeks_features:
            print(f"  - {feature}")
    else:
        print("✓ No Greeks management (will use defaults)")


def test_options_preset_risk_management():
    """Test options-specific risk management"""
    preset = PRESET_CONFIGS["options_trading"]
    
    risk_features = []
    
    if "adjustment_threshold" in preset:
        assert preset["adjustment_threshold"] > 0
        risk_features.append(f"Adjustment threshold: {preset['adjustment_threshold']}%")
    
    if "max_spread_width_percent" in preset:
        assert 0 < preset["max_spread_width_percent"] <= 10
        risk_features.append(f"Max spread width: {preset['max_spread_width_percent']}%")
    
    if "underlying_stop_loss_percent" in preset:
        assert preset["underlying_stop_loss_percent"] > 0
        risk_features.append(f"Underlying SL: {preset['underlying_stop_loss_percent']}%")
    
    if "margin_requirement_multiplier" in preset:
        assert preset["margin_requirement_multiplier"] >= 1.0
        risk_features.append(f"Margin multiplier: {preset['margin_requirement_multiplier']}x")
    
    if "use_stop_loss_orders" in preset:
        assert isinstance(preset["use_stop_loss_orders"], bool)
        risk_features.append(f"Use SL orders: {preset['use_stop_loss_orders']}")
    
    if "commission_per_lot" in preset:
        assert preset["commission_per_lot"] > 0
        risk_features.append(f"Commission: ₹{preset['commission_per_lot']}/lot")
    
    if "slippage_percent" in preset:
        assert preset["slippage_percent"] >= 0
        risk_features.append(f"Slippage: {preset['slippage_percent']}%")
    
    if risk_features:
        print("✓ Risk management features:")
        for feature in risk_features:
            print(f"  - {feature}")


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("OPTIONS TRADING PRESET CONFIGURATION TESTS")
    print("=" * 70 + "\n")
    
    tests = [
        ("Preset Exists", test_options_preset_exists),
        ("Preset Structure", test_options_preset_structure),
        ("Preset Values", test_options_preset_values),
        ("Instruments Configuration", test_options_preset_instruments),
        ("Indian Market Specific", test_options_preset_indian_market_specific),
        ("Advanced Features", test_options_preset_advanced_features),
        ("Greeks Management", test_options_preset_greeks_management),
        ("Risk Management", test_options_preset_risk_management),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"\n{test_name}:")
            print("-" * 70)
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"✗ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ ERROR: {e}")
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 70 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
