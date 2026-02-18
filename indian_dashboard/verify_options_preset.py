"""
Quick verification script for Options Trading Preset
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from indian_dashboard.config import PRESET_CONFIGS
import json


def verify_options_preset():
    """Verify options trading preset is properly configured"""
    
    print("\n" + "=" * 70)
    print("OPTIONS TRADING PRESET VERIFICATION")
    print("=" * 70 + "\n")
    
    # Check preset exists
    if "options_trading" not in PRESET_CONFIGS:
        print("❌ Options trading preset not found!")
        return False
    
    preset = PRESET_CONFIGS["options_trading"]
    print("✅ Options trading preset found\n")
    
    # Basic info
    print("BASIC INFORMATION:")
    print("-" * 70)
    print(f"Name: {preset['name']}")
    print(f"Strategy: {preset['strategy']}")
    print(f"Timeframe: {preset['timeframe']}")
    print(f"Broker: {preset['broker']}")
    print(f"Total Parameters: {len(preset)}")
    print()
    
    # Description
    print("DESCRIPTION:")
    print("-" * 70)
    print(preset['description'])
    print()
    
    # Risk parameters
    print("RISK MANAGEMENT:")
    print("-" * 70)
    print(f"Risk per Trade: {preset['risk_per_trade']}%")
    print(f"Max Positions: {preset['max_positions']}")
    print(f"Max Daily Loss: {preset['max_daily_loss']}%")
    print(f"Base Position Size: ₹{preset['base_position_size']:,}")
    print(f"Take Profit: {preset['take_profit']}%")
    print(f"Stop Loss: {preset['stop_loss']}%")
    print()
    
    # Options-specific
    print("OPTIONS-SPECIFIC PARAMETERS:")
    print("-" * 70)
    print(f"Option Type: {preset.get('option_type', 'N/A')}")
    print(f"Strategy Type: {preset.get('strategy_type', 'N/A')}")
    print(f"Min Premium: ₹{preset.get('min_premium', 'N/A')}")
    print(f"Max Premium: ₹{preset.get('max_premium', 'N/A')}")
    print(f"Delta Range: {preset.get('delta_range', 'N/A')}")
    print(f"IV Percentile Min: {preset.get('iv_percentile_min', 'N/A')}")
    print(f"Spread Width: {preset.get('spread_width', 'N/A')} points")
    print(f"Days to Expiry: {preset.get('min_days_to_expiry', 'N/A')}-{preset.get('max_days_to_expiry', 'N/A')}")
    print()
    
    # Greeks management
    print("GREEKS MANAGEMENT:")
    print("-" * 70)
    print(f"Max Vega Exposure: ₹{preset.get('max_vega_exposure', 'N/A'):,}")
    print(f"Max Theta Collection: ₹{preset.get('max_theta_collection', 'N/A'):,}")
    print(f"Target Theta: ₹{preset.get('target_theta', 'N/A'):,}/day")
    print(f"Max Portfolio Delta: ±{preset.get('max_portfolio_delta', 'N/A')}")
    print(f"Delta Hedge Threshold: {preset.get('delta_hedge_threshold', 'N/A')}")
    print(f"Hedge Delta: {preset.get('hedge_delta', 'N/A')}")
    print()
    
    # Instruments
    print("INSTRUMENTS:")
    print("-" * 70)
    if preset['instruments']:
        for i, inst in enumerate(preset['instruments'], 1):
            print(f"{i}. {inst['symbol']} ({inst['instrument_type']})")
            print(f"   Exchange: {inst['exchange']}")
            print(f"   Strike: {inst.get('strike', 'N/A')}")
            print(f"   Lot Size: {inst.get('lot_size', 'N/A')}")
    else:
        print("No instruments pre-configured (will be populated dynamically)")
    print()
    
    # Trading hours
    print("TRADING HOURS:")
    print("-" * 70)
    print(f"Start: {preset['trading_hours']['start']}")
    print(f"End: {preset['trading_hours']['end']}")
    print()
    
    # Position management
    print("POSITION MANAGEMENT:")
    print("-" * 70)
    print(f"Roll Options: {preset.get('roll_options', 'N/A')}")
    print(f"Roll Days Before Expiry: {preset.get('roll_days_before_expiry', 'N/A')}")
    print(f"Scale Out: {preset.get('scale_out', 'N/A')}")
    print(f"Scale Out Levels: {preset.get('scale_out_levels', 'N/A')}")
    print(f"Close Before Expiry: {preset.get('close_before_expiry_minutes', 'N/A')} minutes")
    print()
    
    # JSON serialization test
    print("JSON SERIALIZATION TEST:")
    print("-" * 70)
    try:
        json_str = json.dumps(preset, indent=2)
        print(f"✅ Successfully serialized to JSON ({len(json_str)} bytes)")
    except Exception as e:
        print(f"❌ Failed to serialize: {e}")
        return False
    print()
    
    # Validation test
    print("VALIDATION TEST:")
    print("-" * 70)
    errors = []
    
    # Check required fields
    required = ['name', 'description', 'broker', 'instruments', 'strategy', 'timeframe']
    for field in required:
        if field not in preset:
            errors.append(f"Missing required field: {field}")
    
    # Check risk parameters
    if not (0 < preset['risk_per_trade'] <= 100):
        errors.append("Invalid risk_per_trade")
    
    if not (preset['max_positions'] > 0):
        errors.append("Invalid max_positions")
    
    if errors:
        print(f"❌ Validation failed:")
        for error in errors:
            print(f"   - {error}")
        return False
    else:
        print("✅ All validations passed")
    print()
    
    print("=" * 70)
    print("✅ OPTIONS TRADING PRESET VERIFICATION COMPLETE")
    print("=" * 70 + "\n")
    
    return True


if __name__ == "__main__":
    success = verify_options_preset()
    sys.exit(0 if success else 1)
