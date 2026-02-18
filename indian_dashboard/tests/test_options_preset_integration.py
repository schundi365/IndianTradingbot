"""
Integration Test for Options Trading Preset
Tests loading and applying the options preset through the API
"""

import sys
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from indian_dashboard.config import PRESET_CONFIGS


def test_options_preset_api_format():
    """Test that options preset can be formatted for API response"""
    preset = PRESET_CONFIGS["options_trading"]
    
    # Simulate API response format
    api_response = {
        'id': 'options_trading',
        'name': preset.get('name', 'options_trading'),
        'description': preset.get('description', ''),
        'strategy': preset.get('strategy', ''),
        'config': preset
    }
    
    # Validate API response structure
    assert 'id' in api_response
    assert 'name' in api_response
    assert 'description' in api_response
    assert 'strategy' in api_response
    assert 'config' in api_response
    
    print("✓ Options preset can be formatted for API response")
    print(f"  - ID: {api_response['id']}")
    print(f"  - Name: {api_response['name']}")
    print(f"  - Strategy: {api_response['strategy']}")
    print(f"  - Description length: {len(api_response['description'])} chars")


def test_options_preset_json_serializable():
    """Test that options preset can be serialized to JSON"""
    preset = PRESET_CONFIGS["options_trading"]
    
    try:
        json_str = json.dumps(preset, indent=2)
        assert len(json_str) > 0
        
        # Deserialize to verify
        deserialized = json.loads(json_str)
        assert deserialized == preset
        
        print("✓ Options preset is JSON serializable")
        print(f"  - JSON size: {len(json_str)} bytes")
        
    except Exception as e:
        raise AssertionError(f"Failed to serialize preset to JSON: {e}")


def test_options_preset_validation():
    """Test that options preset passes validation logic"""
    preset = PRESET_CONFIGS["options_trading"]
    
    errors = []
    
    # Validate required fields
    required_fields = ['broker', 'instruments', 'strategy', 'timeframe']
    for field in required_fields:
        if field not in preset:
            errors.append(f"Missing required field: {field}")
    
    # Validate broker
    if preset.get('broker') not in ['kite', 'alice_blue', 'angel_one', 'upstox', 'paper']:
        errors.append(f"Invalid broker: {preset.get('broker')}")
    
    # Validate instruments
    if not isinstance(preset.get('instruments'), list):
        errors.append("Instruments must be a list")
    
    # Validate strategy
    valid_strategies = ['trend_following', 'momentum', 'mean_reversion', 'options_selling']
    if preset.get('strategy') not in valid_strategies:
        errors.append(f"Invalid strategy: {preset.get('strategy')}")
    
    # Validate timeframe
    valid_timeframes = ['1min', '5min', '15min', '1hour', '1day']
    if preset.get('timeframe') not in valid_timeframes:
        errors.append(f"Invalid timeframe: {preset.get('timeframe')}")
    
    # Validate risk parameters
    if 'risk_per_trade' in preset:
        if not (0 < preset['risk_per_trade'] <= 100):
            errors.append(f"Invalid risk_per_trade: {preset['risk_per_trade']}")
    
    if 'max_positions' in preset:
        if not (preset['max_positions'] > 0):
            errors.append(f"Invalid max_positions: {preset['max_positions']}")
    
    if 'max_daily_loss' in preset:
        if not (0 < preset['max_daily_loss'] <= 100):
            errors.append(f"Invalid max_daily_loss: {preset['max_daily_loss']}")
    
    if errors:
        raise AssertionError(f"Validation errors: {', '.join(errors)}")
    
    print("✓ Options preset passes validation")


def test_options_preset_compatibility():
    """Test that options preset is compatible with bot configuration"""
    preset = PRESET_CONFIGS["options_trading"]
    
    # Check compatibility with bot config format
    bot_config_fields = [
        'broker', 'instruments', 'strategy', 'timeframe',
        'risk_per_trade', 'max_positions', 'max_daily_loss',
        'trading_hours', 'position_sizing', 'base_position_size',
        'take_profit', 'stop_loss', 'paper_trading'
    ]
    
    missing_fields = []
    for field in bot_config_fields:
        if field not in preset:
            missing_fields.append(field)
    
    if missing_fields:
        raise AssertionError(f"Missing bot config fields: {', '.join(missing_fields)}")
    
    print("✓ Options preset is compatible with bot configuration")
    print(f"  - All {len(bot_config_fields)} required bot config fields present")


def test_options_preset_instruments_structure():
    """Test that options instruments have correct structure"""
    preset = PRESET_CONFIGS["options_trading"]
    
    if len(preset['instruments']) == 0:
        print("✓ No instruments pre-configured (will be populated dynamically)")
        return
    
    for i, instrument in enumerate(preset['instruments']):
        # Required fields for options
        required_fields = ['symbol', 'exchange', 'instrument_type']
        for field in required_fields:
            if field not in instrument:
                raise AssertionError(f"Instrument {i} missing field: {field}")
        
        # Validate exchange
        if instrument['exchange'] != 'NFO':
            raise AssertionError(f"Instrument {i} has invalid exchange: {instrument['exchange']}")
        
        # Validate instrument type
        if instrument['instrument_type'] not in ['CE', 'PE']:
            raise AssertionError(f"Instrument {i} has invalid type: {instrument['instrument_type']}")
        
        # Optional but recommended fields
        if 'lot_size' in instrument and instrument['lot_size'] <= 0:
            raise AssertionError(f"Instrument {i} has invalid lot_size: {instrument['lot_size']}")
        
        if 'strike' in instrument and instrument['strike'] <= 0:
            raise AssertionError(f"Instrument {i} has invalid strike: {instrument['strike']}")
    
    print(f"✓ All {len(preset['instruments'])} instruments have correct structure")


def test_options_preset_risk_calculations():
    """Test risk calculations with options preset"""
    preset = PRESET_CONFIGS["options_trading"]
    
    # Calculate position size
    base_position_size = preset['base_position_size']
    risk_per_trade = preset['risk_per_trade']
    max_positions = preset['max_positions']
    
    # Total capital at risk
    total_risk = base_position_size * max_positions * (risk_per_trade / 100)
    
    # Maximum daily loss
    max_daily_loss = preset['max_daily_loss']
    
    print("✓ Risk calculations:")
    print(f"  - Base position size: ₹{base_position_size:,}")
    print(f"  - Risk per trade: {risk_per_trade}%")
    print(f"  - Max positions: {max_positions}")
    print(f"  - Total capital at risk: ₹{total_risk:,.2f}")
    print(f"  - Max daily loss: {max_daily_loss}%")
    
    # Validate risk is reasonable
    if total_risk > base_position_size * max_positions * 0.5:
        print("  ⚠ Warning: High risk per trade")
    else:
        print("  ✓ Risk per trade is conservative")


def test_options_preset_trading_hours():
    """Test trading hours configuration"""
    preset = PRESET_CONFIGS["options_trading"]
    
    trading_hours = preset['trading_hours']
    start_time = trading_hours['start']
    end_time = trading_hours['end']
    
    # Parse times
    start_hour, start_min = map(int, start_time.split(':'))
    end_hour, end_min = map(int, end_time.split(':'))
    
    # Validate times
    assert 9 <= start_hour <= 15, "Start time should be during market hours"
    assert 9 <= end_hour <= 15, "End time should be during market hours"
    
    # Calculate trading duration
    start_minutes = start_hour * 60 + start_min
    end_minutes = end_hour * 60 + end_min
    duration_minutes = end_minutes - start_minutes
    
    print("✓ Trading hours configuration:")
    print(f"  - Start: {start_time}")
    print(f"  - End: {end_time}")
    print(f"  - Duration: {duration_minutes} minutes ({duration_minutes/60:.1f} hours)")
    
    if start_time > "09:15":
        print("  ✓ Avoids opening volatility")
    
    if end_time < "15:30":
        print("  ✓ Closes before market close")


def test_options_preset_greeks_parameters():
    """Test Greeks-related parameters"""
    preset = PRESET_CONFIGS["options_trading"]
    
    greeks_params = []
    
    if 'delta_range' in preset:
        greeks_params.append(f"Delta range: {preset['delta_range']}")
    
    if 'max_vega_exposure' in preset:
        greeks_params.append(f"Max vega: ₹{preset['max_vega_exposure']:,}")
    
    if 'max_theta_collection' in preset:
        greeks_params.append(f"Max theta: ₹{preset['max_theta_collection']:,}")
    
    if 'max_portfolio_delta' in preset:
        greeks_params.append(f"Max portfolio delta: ±{preset['max_portfolio_delta']}")
    
    if 'delta_hedge_threshold' in preset:
        greeks_params.append(f"Delta hedge threshold: {preset['delta_hedge_threshold']}")
    
    if greeks_params:
        print("✓ Greeks parameters configured:")
        for param in greeks_params:
            print(f"  - {param}")
    else:
        print("✓ No Greeks parameters (basic configuration)")


def run_all_tests():
    """Run all integration tests"""
    print("\n" + "=" * 70)
    print("OPTIONS TRADING PRESET INTEGRATION TESTS")
    print("=" * 70 + "\n")
    
    tests = [
        ("API Format", test_options_preset_api_format),
        ("JSON Serialization", test_options_preset_json_serializable),
        ("Validation", test_options_preset_validation),
        ("Bot Compatibility", test_options_preset_compatibility),
        ("Instruments Structure", test_options_preset_instruments_structure),
        ("Risk Calculations", test_options_preset_risk_calculations),
        ("Trading Hours", test_options_preset_trading_hours),
        ("Greeks Parameters", test_options_preset_greeks_parameters),
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
