"""
Test NIFTY Futures Preset Configuration
Validates that the NIFTY futures preset has appropriate parameters
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from indian_dashboard.config import PRESET_CONFIGS


def test_nifty_preset_exists():
    """Test that NIFTY futures preset exists"""
    assert "nifty_futures" in PRESET_CONFIGS, "NIFTY futures preset not found"
    print("✓ NIFTY futures preset exists")


def test_nifty_preset_structure():
    """Test that NIFTY preset has all required fields"""
    preset = PRESET_CONFIGS["nifty_futures"]
    
    required_fields = [
        "name", "description", "broker", "instruments", "strategy",
        "timeframe", "risk_per_trade", "max_positions", "max_daily_loss",
        "trading_hours", "indicator_period", "position_sizing",
        "base_position_size", "take_profit", "stop_loss", "paper_trading",
        "log_level", "data_refresh_interval", "enable_notifications"
    ]
    
    for field in required_fields:
        assert field in preset, f"Missing required field: {field}"
    
    print(f"✓ NIFTY preset has all {len(required_fields)} required fields")


def test_nifty_preset_values():
    """Test that NIFTY preset has appropriate values"""
    preset = PRESET_CONFIGS["nifty_futures"]
    
    # Test name and description
    assert preset["name"] == "NIFTY 50 Futures"
    assert len(preset["description"]) > 50, "Description should be detailed"
    print("✓ Name and description are appropriate")
    
    # Test broker
    assert preset["broker"] in ["kite", "alice_blue", "angel_one", "upstox", "paper"]
    print(f"✓ Broker is valid: {preset['broker']}")
    
    # Test strategy
    assert preset["strategy"] in ["trend_following", "momentum", "mean_reversion"]
    print(f"✓ Strategy is valid: {preset['strategy']}")
    
    # Test timeframe
    assert preset["timeframe"] in ["1min", "5min", "15min", "1hour", "1day"]
    print(f"✓ Timeframe is valid: {preset['timeframe']}")
    
    # Test risk parameters
    assert 0 < preset["risk_per_trade"] <= 5, "Risk per trade should be between 0 and 5%"
    assert 0 < preset["max_daily_loss"] <= 10, "Max daily loss should be between 0 and 10%"
    assert preset["max_positions"] > 0, "Max positions should be positive"
    print(f"✓ Risk parameters are appropriate:")
    print(f"  - Risk per trade: {preset['risk_per_trade']}%")
    print(f"  - Max daily loss: {preset['max_daily_loss']}%")
    print(f"  - Max positions: {preset['max_positions']}")
    
    # Test trading hours
    assert "start" in preset["trading_hours"]
    assert "end" in preset["trading_hours"]
    assert preset["trading_hours"]["start"] == "09:15", "Market opens at 09:15"
    assert preset["trading_hours"]["end"] in ["15:15", "15:30"], "Should close before market close"
    print(f"✓ Trading hours are valid: {preset['trading_hours']['start']} - {preset['trading_hours']['end']}")
    
    # Test position sizing
    assert preset["position_sizing"] in ["fixed", "percentage", "risk_based"]
    assert preset["base_position_size"] > 0
    print(f"✓ Position sizing: {preset['position_sizing']} with base size ₹{preset['base_position_size']:,}")
    
    # Test take profit and stop loss
    assert preset["take_profit"] > 0
    assert preset["stop_loss"] > 0
    assert preset["take_profit"] > preset["stop_loss"], "Take profit should be greater than stop loss"
    reward_risk_ratio = preset["take_profit"] / preset["stop_loss"]
    print(f"✓ TP/SL configured: TP={preset['take_profit']}%, SL={preset['stop_loss']}% (R:R = {reward_risk_ratio:.2f}:1)")
    
    # Test paper trading
    assert isinstance(preset["paper_trading"], bool)
    print(f"✓ Paper trading: {preset['paper_trading']}")


def test_nifty_preset_instruments():
    """Test that NIFTY preset has instrument configuration"""
    preset = PRESET_CONFIGS["nifty_futures"]
    
    assert isinstance(preset["instruments"], list)
    
    if len(preset["instruments"]) > 0:
        # If instruments are pre-configured, validate structure
        instrument = preset["instruments"][0]
        assert "symbol" in instrument
        assert "exchange" in instrument
        assert instrument["exchange"] == "NFO", "NIFTY futures trade on NFO"
        assert instrument["instrument_type"] == "FUT", "Should be futures"
        
        if "lot_size" in instrument:
            assert instrument["lot_size"] > 0, "Lot size should be positive"
        
        print(f"✓ Instruments configured: {len(preset['instruments'])} instrument(s)")
        print(f"  - Symbol: {instrument['symbol']}")
        print(f"  - Exchange: {instrument['exchange']}")
        print(f"  - Type: {instrument['instrument_type']}")
        if "lot_size" in instrument:
            print(f"  - Lot size: {instrument['lot_size']}")
    else:
        print("✓ Instruments list is empty (will be populated dynamically)")


def test_nifty_preset_indian_market_specific():
    """Test NIFTY-specific parameters for Indian market"""
    preset = PRESET_CONFIGS["nifty_futures"]
    
    # NIFTY futures are highly liquid, so we should have appropriate settings
    assert preset["timeframe"] in ["5min", "15min"], "NIFTY futures work well with 5-15 min timeframes"
    assert preset["max_positions"] <= 3, "NIFTY futures require significant capital, limit positions"
    assert preset["risk_per_trade"] <= 2.0, "Conservative risk for futures trading"
    
    print("✓ NIFTY-specific parameters are appropriate for Indian market")


def test_nifty_preset_advanced_features():
    """Test advanced features if present"""
    preset = PRESET_CONFIGS["nifty_futures"]
    
    advanced_features = []
    
    if "min_volume" in preset:
        assert preset["min_volume"] > 0
        advanced_features.append(f"Min volume: {preset['min_volume']:,}")
    
    if "atr_period" in preset:
        assert preset["atr_period"] > 0
        advanced_features.append(f"ATR period: {preset['atr_period']}")
    
    if "trailing_stop" in preset:
        assert isinstance(preset["trailing_stop"], bool)
        advanced_features.append(f"Trailing stop: {preset['trailing_stop']}")
    
    if "trailing_stop_activation" in preset:
        assert preset["trailing_stop_activation"] > 0
        advanced_features.append(f"Trailing activation: {preset['trailing_stop_activation']}%")
    
    if "trailing_stop_distance" in preset:
        assert preset["trailing_stop_distance"] > 0
        advanced_features.append(f"Trailing distance: {preset['trailing_stop_distance']}%")
    
    if advanced_features:
        print("✓ Advanced features configured:")
        for feature in advanced_features:
            print(f"  - {feature}")
    else:
        print("✓ No advanced features (basic configuration)")


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("NIFTY FUTURES PRESET CONFIGURATION TESTS")
    print("=" * 70 + "\n")
    
    tests = [
        ("Preset Exists", test_nifty_preset_exists),
        ("Preset Structure", test_nifty_preset_structure),
        ("Preset Values", test_nifty_preset_values),
        ("Instruments Configuration", test_nifty_preset_instruments),
        ("Indian Market Specific", test_nifty_preset_indian_market_specific),
        ("Advanced Features", test_nifty_preset_advanced_features),
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
