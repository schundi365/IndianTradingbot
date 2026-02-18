#!/usr/bin/env python3
"""
Test script to simulate form submission with confidence value
"""

import requests
import json

def test_confidence_form_submission():
    """Test confidence form submission like the dashboard would do"""
    
    print("="*80)
    print("TESTING CONFIDENCE FORM SUBMISSION")
    print("="*80)
    
    # Get current config first
    try:
        response = requests.get('http://127.0.0.1:5000/api/config', timeout=10)
        if response.status_code != 200:
            print("❌ Failed to get current config")
            return
        
        current_config = response.json()
        print(f"Current min_trade_confidence: {current_config.get('min_trade_confidence')}")
        
    except Exception as e:
        print(f"❌ Error getting config: {e}")
        return
    
    # Test form submission with confidence as percentage (like the form would send)
    print("\n1. TESTING FORM SUBMISSION (60% confidence):")
    
    # Simulate what the form would send
    form_data = current_config.copy()
    form_data['min_trade_confidence'] = 60 / 100  # Convert 60% to 0.6
    
    try:
        response = requests.post('http://127.0.0.1:5000/api/config', 
                               json=form_data, 
                               timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                print("   ✅ Form submission successful with 60% confidence")
            else:
                print(f"   ❌ Form submission failed: {result.get('message')}")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test various confidence percentages
    print("\n2. TESTING VARIOUS CONFIDENCE PERCENTAGES:")
    test_percentages = [20, 30, 50, 60, 70, 80, 90]
    
    for percentage in test_percentages:
        test_data = current_config.copy()
        test_data['min_trade_confidence'] = percentage / 100  # Convert to decimal
        
        try:
            response = requests.post('http://127.0.0.1:5000/api/config', 
                                   json=test_data, 
                                   timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    print(f"   ✅ {percentage}% confidence accepted")
                else:
                    print(f"   ❌ {percentage}% confidence rejected: {result.get('message')}")
            else:
                print(f"   ❌ {percentage}% HTTP error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ {percentage}% error: {e}")
    
    # Test edge cases that should fail
    print("\n3. TESTING EDGE CASES (should fail):")
    edge_percentages = [10, 95, 100]
    
    for percentage in edge_percentages:
        test_data = current_config.copy()
        test_data['min_trade_confidence'] = percentage / 100
        
        try:
            response = requests.post('http://127.0.0.1:5000/api/config', 
                                   json=test_data, 
                                   timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    print(f"   ❌ {percentage}% confidence incorrectly accepted")
                else:
                    print(f"   ✅ {percentage}% confidence correctly rejected: {result.get('message')}")
            else:
                print(f"   ❌ {percentage}% HTTP error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ {percentage}% error: {e}")
    
    print("\n" + "="*80)
    print("CONFIDENCE FORM SUBMISSION TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    test_confidence_form_submission()