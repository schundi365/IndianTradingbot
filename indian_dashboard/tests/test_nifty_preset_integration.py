"""
Integration test for NIFTY Futures Preset
Tests loading and using the preset through the API
"""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from indian_dashboard.config import PRESET_CONFIGS


def test_preset_can_be_serialized():
    """Test that preset can be serialized to JSON"""
    preset = PRESET_CONFIGS["nifty_futures"]
    
    try:
        json_str = json.dumps(preset, indent=2)
        assert len(json_str) > 0
        print("✓ Preset can be serialized to JSON")
        print(f"  JSON size: {len(json_str)} bytes")
        return json_str
    except Exception as e:
        print(f"✗ Failed to serialize preset: {e}")
        raise


def test_preset_can_be_deserialized(json_str):
    """Test that preset can be deserialized from JSON"""
    try:
        preset = json.loads(json_str)
        assert isinstance(preset, dict)
        assert "name" in preset
        assert "strategy" in preset
        print("✓ Preset can be deserialized from JSON")
        return preset
    except Exception as e:
        print(f"✗ Failed to deserialize preset: {e}")
        raise


def test_preset_validation():
    """Test that preset passes validation"""
    preset = PRESET_CONFIGS["nifty_futures"]
    
    # Import validation function
    from indian_dashboard.api.config import validate_configuration
    
    errors = validate_configuration(preset)
    
    if errors:
        print(f"✗ Preset validation failed with {len(errors)} error(s):")
        for error in errors:
            print(f"  - {error}")
        raise AssertionError("Preset validation failed")
    else:
        print("✓ Preset passes validation")


def test_preset_api_format():
    """Test that preset matches expected API format"""
    preset = PRESET_CONFIGS["nifty_futures"]
    
    # Expected format for API response
    api_format = {
        'id': 'nifty_futures',
        'name': preset.get('name', 'nifty_futures'),
        'description': preset.get('description', ''),
        'strategy': preset.get('strategy', ''),
        'config': preset
    }
    
    assert api_format['id'] == 'nifty_futures'
    assert api_format['name'] == 'NIFTY 50 Futures'
    assert len(api_format['description']) > 0
    assert api_format['strategy'] == 'trend_following'
    assert isinstance(api_format['config'], dict)
    
    print("✓ Preset matches expected API format")
    print(f"  ID: {api_format['id']}")
    print(f"  Name: {api_format['name']}")
    print(f"  Strategy: {api_format['strategy']}")


def test_preset_can_be_saved():
    """Test that preset can be saved as a configuration file"""
    preset = PRESET_CONFIGS["nifty_futures"]
    
    # Create a test config directory
    test_dir = Path(__file__).parent / "test_configs"
    test_dir.mkdir(exist_ok=True)
    
    try:
        # Save preset
        config_file = test_dir / "nifty_test.json"
        with open(config_file, 'w') as f:
            json.dump(preset, f, indent=2)
        
        # Verify file exists
        assert config_file.exists()
        
        # Load and verify
        with open(config_file, 'r') as f:
            loaded = json.load(f)
        
        assert loaded['name'] == preset['name']
        assert loaded['strategy'] == preset['strategy']
        
        print("✓ Preset can be saved and loaded from file")
        print(f"  File: {config_file}")
        
        # Cleanup
        config_file.unlink()
        test_dir.rmdir()
        
    except Exception as e:
        print(f"✗ Failed to save/load preset: {e}")
        # Cleanup on error
        if config_file.exists():
            config_file.unlink()
        if test_dir.exists():
            test_dir.rmdir()
        raise


def test_preset_instruments_format():
    """Test that instruments are in correct format"""
    preset = PRESET_CONFIGS["nifty_futures"]
    instruments = preset.get("instruments", [])
    
    if len(instruments) == 0:
        print("⚠ No instruments configured (will be populated dynamically)")
        return
    
    for i, instrument in enumerate(instruments):
        # Check required fields
        assert "symbol" in instrument, f"Instrument {i} missing 'symbol'"
        assert "exchange" in instrument, f"Instrument {i} missing 'exchange'"
        assert "instrument_type" in instrument, f"Instrument {i} missing 'instrument_type'"
        
        # Validate values
        assert instrument["exchange"] == "NFO", "NIFTY futures should be on NFO"
        assert instrument["instrument_type"] == "FUT", "Should be futures"
        
        if "lot_size" in instrument:
            assert instrument["lot_size"] > 0, "Lot size should be positive"
        
        print(f"✓ Instrument {i+1} format is correct:")
        print(f"  Symbol: {instrument['symbol']}")
        print(f"  Exchange: {instrument['exchange']}")
        print(f"  Type: {instrument['instrument_type']}")


def test_preset_risk_calculations():
    """Test risk calculations with preset parameters"""
    preset = PRESET_CONFIGS["nifty_futures"]
    
    # Sample calculations
    capital = 200000  # ₹2 lakh
    risk_per_trade = preset["risk_per_trade"]
    max_positions = preset["max_positions"]
    
    # Calculate risk per trade
    risk_amount = capital * (risk_per_trade / 100)
    print(f"✓ Risk calculations:")
    print(f"  Capital: ₹{capital:,}")
    print(f"  Risk per trade: {risk_per_trade}% = ₹{risk_amount:,.2f}")
    
    # Calculate maximum risk
    max_risk = risk_amount * max_positions
    max_risk_pct = (max_risk / capital) * 100
    print(f"  Max concurrent risk: ₹{max_risk:,.2f} ({max_risk_pct:.1f}%)")
    
    # Calculate position size
    stop_loss_pct = preset["stop_loss"]
    position_size = risk_amount / (stop_loss_pct / 100)
    print(f"  Position size (for {stop_loss_pct}% SL): ₹{position_size:,.2f}")
    
    # Verify reasonable values
    assert risk_amount > 0
    assert max_risk_pct <= 5.0, "Max concurrent risk should be reasonable"
    assert position_size > 0


def test_preset_reward_risk_ratio():
    """Test reward-risk ratio"""
    preset = PRESET_CONFIGS["nifty_futures"]
    
    take_profit = preset["take_profit"]
    stop_loss = preset["stop_loss"]
    
    rr_ratio = take_profit / stop_loss
    
    print(f"✓ Reward-Risk ratio:")
    print(f"  Take Profit: {take_profit}%")
    print(f"  Stop Loss: {stop_loss}%")
    print(f"  R:R Ratio: {rr_ratio:.2f}:1")
    
    # Verify ratio is favorable
    assert rr_ratio >= 1.5, "R:R ratio should be at least 1.5:1"
    
    # Calculate breakeven win rate
    breakeven_wr = 1 / (1 + rr_ratio)
    print(f"  Breakeven win rate: {breakeven_wr*100:.1f}%")


def run_all_tests():
    """Run all integration tests"""
    print("\n" + "=" * 70)
    print("NIFTY FUTURES PRESET INTEGRATION TESTS")
    print("=" * 70 + "\n")
    
    tests = [
        ("Serialization", test_preset_can_be_serialized),
        ("Validation", test_preset_validation),
        ("API Format", test_preset_api_format),
        ("File Save/Load", test_preset_can_be_saved),
        ("Instruments Format", test_preset_instruments_format),
        ("Risk Calculations", test_preset_risk_calculations),
        ("Reward-Risk Ratio", test_preset_reward_risk_ratio),
    ]
    
    passed = 0
    failed = 0
    json_str = None
    
    for test_name, test_func in tests:
        try:
            print(f"\n{test_name}:")
            print("-" * 70)
            
            # Special handling for serialization test
            if test_name == "Serialization":
                json_str = test_func()
            # Special handling for deserialization test
            elif test_name == "Deserialization" and json_str:
                test_func(json_str)
            else:
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
