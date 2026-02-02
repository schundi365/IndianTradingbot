#!/usr/bin/env python3
"""
Test the config manager directly to see where the validation error is coming from
"""

import sys
import os
sys.path.append('src')

from config_manager import get_config_manager

def test_config_manager():
    """Test config manager validation directly"""
    print("🧪 Testing Config Manager Directly...")
    print("="*50)
    
    config_manager = get_config_manager()
    
    # Test configuration with 60% confidence and $100 max daily loss
    test_config = {
        'risk_percent': 1.0,
        'min_trade_confidence': 0.6,  # 60% as decimal
        'max_daily_loss': 100,  # $100
        'symbols': ['BTCUSD'],
        'timeframe': 30,
        'use_volume_filter': True
    }
    
    print("Testing configuration:")
    for key, value in test_config.items():
        print(f"  {key}: {value}")
    
    print("\nCalling config_manager.update_config()...")
    
    try:
        result = config_manager.update_config(test_config)
        print(f"Result: {result}")
        
        if result:
            print("✅ Config manager accepted the configuration")
        else:
            print("❌ Config manager rejected the configuration")
            print("Check the console for error messages from the config manager")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test the validation method directly
    print("\nTesting _validate_config directly...")
    try:
        validation_result = config_manager._validate_config(test_config)
        print(f"Validation result: {validation_result}")
        
        if validation_result:
            print("✅ Direct validation passed")
        else:
            print("❌ Direct validation failed")
            
    except Exception as e:
        print(f"❌ Validation exception: {e}")

if __name__ == "__main__":
    print("🚀 Config Manager Direct Test")
    print("="*50)
    
    test_config_manager()
    
    print("="*50)
    print("💡 This test bypasses the web dashboard to test config manager directly")
    print("="*50)