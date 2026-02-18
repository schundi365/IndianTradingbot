#!/usr/bin/env python3
"""
Test script to debug max daily loss validation issue
"""

import requests
import json

def test_max_daily_loss_validation():
    """Test max daily loss validation in dashboard"""
    
    print("="*80)
    print("TESTING MAX DAILY LOSS VALIDATION")
    print("="*80)
    
    # Test 1: Get current config
    print("\n1. GETTING CURRENT CONFIG:")
    try:
        response = requests.get('http://127.0.0.1:5000/api/config', timeout=10)
        if response.status_code == 200:
            config = response.json()
            
            # Check all possible daily loss field names
            max_daily_loss = config.get('max_daily_loss', 'NOT FOUND')
            max_daily_loss_percent = config.get('max_daily_loss_percent', 'NOT FOUND')
            
            print(f"   max_daily_loss: {max_daily_loss}")
            print(f"   max_daily_loss_percent: {max_daily_loss_percent}")
            
            # Check which one has a valid value
            if max_daily_loss_percent != 'NOT FOUND':
                current_value = max_daily_loss_percent
                field_name = 'max_daily_loss_percent'
                print(f"   Using field: {field_name} = {current_value}")
            elif max_daily_loss != 'NOT FOUND':
                current_value = max_daily_loss
                field_name = 'max_daily_loss'
                print(f"   Using field: {field_name} = {current_value}")
            else:
                print("   ❌ No daily loss field found")
                return
                
            # Check if it's in valid range
            if isinstance(current_value, (int, float)):
                if 1 <= current_value <= 20:
                    print(f"   ✅ Current value {current_value} is in valid range (1 to 20)")
                else:
                    print(f"   ❌ Current value {current_value} is outside valid range (1 to 20)")
            else:
                print(f"   ❌ Current value is not a number: {current_value}")
                
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
    
    # Test 3: Test specific daily loss values
    print("\n3. TESTING SPECIFIC DAILY LOSS VALUES:")
    test_values = [1, 3, 5, 10, 15, 20]
    
    for test_val in test_values:
        test_config = config.copy()
        test_config['max_daily_loss_percent'] = test_val
        
        try:
            response = requests.post('http://127.0.0.1:5000/api/config', 
                                   json=test_config, 
                                   timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    print(f"   ✅ Value {test_val}% accepted")
                else:
                    print(f"   ❌ Value {test_val}% rejected: {result.get('message')}")
            else:
                print(f"   ❌ Value {test_val}% HTTP error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Value {test_val}% error: {e}")
    
    # Test 4: Test edge cases
    print("\n4. TESTING EDGE CASES:")
    edge_values = [0.5, 21, 25, 0]
    
    for test_val in edge_values:
        test_config = config.copy()
        test_config['max_daily_loss_percent'] = test_val
        
        try:
            response = requests.post('http://127.0.0.1:5000/api/config', 
                                   json=test_config, 
                                   timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    print(f"   ❌ Edge value {test_val}% incorrectly accepted")
                else:
                    print(f"   ✅ Edge value {test_val}% correctly rejected: {result.get('message')}")
            else:
                print(f"   ❌ Edge value {test_val}% HTTP error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Edge value {test_val}% error: {e}")
    
    print("\n" + "="*80)
    print("MAX DAILY LOSS VALIDATION TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    test_max_daily_loss_validation()