#!/usr/bin/env python3
"""
Test script to debug MACD min histogram validation issue
"""

import requests
import json

def test_macd_form_submission():
    """Test MACD min histogram form submission"""
    
    print("="*80)
    print("TESTING MACD MIN HISTOGRAM FORM SUBMISSION")
    print("="*80)
    
    # Get current config first
    try:
        response = requests.get('http://127.0.0.1:5000/api/config', timeout=10)
        if response.status_code != 200:
            print("❌ Failed to get current config")
            return
        
        current_config = response.json()
        current_macd = current_config.get('macd_min_histogram', 'NOT FOUND')
        print(f"Current macd_min_histogram: {current_macd}")
        print(f"Type: {type(current_macd)}")
        
    except Exception as e:
        print(f"❌ Error getting config: {e}")
        return
    
    # Test 1: Try to save current config
    print("\n1. TESTING SAVE WITH CURRENT VALUES:")
    try:
        response = requests.post('http://127.0.0.1:5000/api/config', 
                               json=current_config, 
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
    
    # Test 2: Test specific MACD values
    print("\n2. TESTING SPECIFIC MACD VALUES:")
    test_values = [0.0001, 0.0005, 0.001, 0.005, 0.01]
    
    for test_val in test_values:
        test_config = current_config.copy()
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
    
    # Test 3: Test edge cases that should fail
    print("\n3. TESTING EDGE CASES (should fail):")
    edge_values = [0, 0.00005, 0.02, 0.1, 1.0]
    
    for test_val in edge_values:
        test_config = current_config.copy()
        test_config['macd_min_histogram'] = test_val
        
        try:
            response = requests.post('http://127.0.0.1:5000/api/config', 
                                   json=test_config, 
                                   timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    print(f"   ❌ Edge value {test_val} incorrectly accepted")
                else:
                    print(f"   ✅ Edge value {test_val} correctly rejected: {result.get('message')}")
            else:
                print(f"   ❌ Edge value {test_val} HTTP error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Edge value {test_val} error: {e}")
    
    # Test 4: Check if there are any missing fields causing issues
    print("\n4. CHECKING FOR MISSING FIELDS:")
    required_fields = ['symbols', 'timeframe', 'risk_percent', 'min_trade_confidence', 'max_daily_loss_percent']
    
    for field in required_fields:
        if field not in current_config:
            print(f"   ⚠️  Missing field: {field}")
        else:
            print(f"   ✅ Field present: {field} = {current_config[field]}")
    
    print("\n" + "="*80)
    print("MACD FORM SUBMISSION TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    test_macd_form_submission()