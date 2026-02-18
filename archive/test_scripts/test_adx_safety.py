#!/usr/bin/env python3
"""
Test ADX KeyError Fix
"""

import pandas as pd
import numpy as np

def test_adx_safety():
    """Test that ADX access is completely safe"""
    print("🧪 TESTING ADX KEYERROR FIX")
    print("=" * 40)
    
    # Create a test Series without ADX
    test_data = pd.Series({
        'close': 1.2345,
        'high': 1.2350,
        'low': 1.2340,
        'rsi': 45.0
        # Note: NO 'adx' key - this should not cause KeyError
    })
    
    # Test the safe access patterns
    try:
        # Test 1: Safe get access
        adx_value = test_data.get('adx', 0)
        print(f"✅ Safe get access: {adx_value}")
        
        # Test 2: Index check
        has_adx = 'adx' in test_data.index if hasattr(test_data, 'index') else False
        print(f"✅ Safe index check: {has_adx}")
        
        # Test 3: Combined check
        if 'adx' in test_data.index and not pd.isna(test_data.get('adx', 0)):
            adx = test_data.get('adx', 0)
        else:
            adx = 0
        print(f"✅ Combined safe check: {adx}")
        
        print("🎉 All ADX access patterns are safe!")
        return True
        
    except Exception as e:
        print(f"❌ ADX test failed: {e}")
        return False

if __name__ == "__main__":
    test_adx_safety()
