#!/usr/bin/env python3
"""
Test script to debug confidence validation issue
"""

import requests
import json

def test_confidence_validation():
    """Test confidence validation in dashboard"""
    
    print("="*80)
    print("TESTING CONFIDENCE VALIDATION")
    print("="*80)
    
    # Test 1: Get current config
    print("\n1. GETTING CURRENT CONFIG:")
    try:
        response = requests.get('http://127.0.0.1:5000/api/config', timeout=10)
        if response.status_code == 200:
            config = response.json()
            current_confidence = config.get('min_trade_confidence', 'NOT FOUND')
            print(f"   Current min_trade_confidence: {current_confidence}")
            print(f"   Type: {type(current_confidence)}")
            
            # Check if it's in valid range
            if isinstance(current_confidence, (int, float)):
                if 0.2 <= current_confidence <= 0.9:
                    print("   ✅ Current value is in valid range (0.2 to 0.9)")
                else:
                    print(f"   ❌ Current value {current_confidence} is outside valid range (0.2 to 0.9)")
            else:
                print(f"   ❌ Current value is not a number: {current_confidence}")
        else:
            print(f"   ❌ Failed to get config: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Test 2: Try to save the same config (should work)
    print("\n2. TESTING SAVE WITH CURRENT VALUES:")
    try:
        response = requests.post('http://127.0.0.1:5000/api/config', 
                               json=config, 
                               timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                print("   ✅ Successfully saved current config")
            else:
                print(f"   ❌ Failed to save: {result.get('message', 'Unknown error')}")
                print(f"   Full response: {result}")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Test specific confidence values
    print("\n3. TESTING SPECIFIC CONFIDENCE VALUES:")
    test_values = [0.2, 0.5, 0.6, 0.7, 0.9]
    
    for test_val in test_values:
        test_config = config.copy()
        test_config['min_trade_confidence'] = test_val
        
        try:
            response = requests.post('http://127.0.0.1:5000/api/config', 
                                   json=test_config, 
                                   timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    print(f"   ✅ Value {test_val} ({test_val*100}%) accepted")
                else:
                    print(f"   ❌ Value {test_val} ({test_val*100}%) rejected: {result.get('message')}")
            else:
                print(f"   ❌ Value {test_val} HTTP error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Value {test_val} error: {e}")
    
    # Test 4: Test edge cases
    print("\n4. TESTING EDGE CASES:")
    edge_values = [0.19, 0.91, 60, 0.60]  # Include common mistake values
    
    for test_val in edge_values:
        test_config = config.copy()
        test_config['min_trade_confidence'] = test_val
        
        try:
            response = requests.post('http://127.0.0.1:5000/api/config', 
                                   json=test_config, 
                                   timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    print(f"   ✅ Edge value {test_val} accepted")
                else:
                    print(f"   ❌ Edge value {test_val} rejected: {result.get('message')}")
            else:
                print(f"   ❌ Edge value {test_val} HTTP error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Edge value {test_val} error: {e}")
    
    print("\n" + "="*80)
    print("CONFIDENCE VALIDATION TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    test_confidence_validation()