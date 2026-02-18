#!/usr/bin/env python3
"""
Test script to verify MACD precision in dashboard
"""

import requests
import json

def test_macd_precision():
    """Test that MACD min histogram can handle precise decimal values"""
    
    print("="*80)
    print("TESTING MACD PRECISION IN DASHBOARD")
    print("="*80)
    
    # Test 1: Get current config
    print("\n1. GETTING CURRENT CONFIG:")
    try:
        response = requests.get('http://127.0.0.1:5000/api/config', timeout=10)
        if response.status_code == 200:
            config = response.json()
            current_macd = config.get('macd_min_histogram', 'NOT FOUND')
            print(f"   Current MACD Min Histogram: {current_macd}")
        else:
            print(f"   ❌ Failed to get config: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Test 2: Try to save precise MACD value
    print("\n2. TESTING PRECISE MACD VALUE (0.0005):")
    test_config = config.copy()
    test_config['macd_min_histogram'] = 0.0005
    
    try:
        response = requests.post('http://127.0.0.1:5000/api/config', 
                               json=test_config, 
                               timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                print("   ✅ Successfully saved MACD value 0.0005")
            else:
                print(f"   ❌ Failed to save: {result.get('message', 'Unknown error')}")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Verify the value was saved correctly
    print("\n3. VERIFYING SAVED VALUE:")
    try:
        response = requests.get('http://127.0.0.1:5000/api/config', timeout=10)
        if response.status_code == 200:
            config = response.json()
            saved_macd = config.get('macd_min_histogram', 'NOT FOUND')
            print(f"   Saved MACD Min Histogram: {saved_macd}")
            
            if saved_macd == 0.0005:
                print("   ✅ MACD precision test PASSED!")
            else:
                print(f"   ❌ MACD precision test FAILED - expected 0.0005, got {saved_macd}")
        else:
            print(f"   ❌ Failed to verify: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Test other precise values
    print("\n4. TESTING OTHER PRECISE VALUES:")
    test_values = [0.0001, 0.0003, 0.0007, 0.001, 0.005]
    
    for test_val in test_values:
        test_config['macd_min_histogram'] = test_val
        try:
            response = requests.post('http://127.0.0.1:5000/api/config', 
                                   json=test_config, 
                                   timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    print(f"   ✅ Value {test_val} accepted")
                else:
                    print(f"   ❌ Value {test_val} rejected: {result.get('message')}")
            else:
                print(f"   ❌ Value {test_val} HTTP error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Value {test_val} error: {e}")
    
    # Restore original value
    print(f"\n5. RESTORING ORIGINAL VALUE ({current_macd}):")
    test_config['macd_min_histogram'] = current_macd
    try:
        response = requests.post('http://127.0.0.1:5000/api/config', 
                               json=test_config, 
                               timeout=10)
        if response.status_code == 200:
            print("   ✅ Original value restored")
        else:
            print("   ❌ Failed to restore original value")
    except Exception as e:
        print(f"   ❌ Error restoring: {e}")
    
    print("\n" + "="*80)
    print("MACD PRECISION TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    test_macd_precision()