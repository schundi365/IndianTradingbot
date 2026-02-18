#!/usr/bin/env python3
"""
Test script to simulate form submission with max daily loss value
"""

import requests
import json

def test_max_daily_loss_form_submission():
    """Test max daily loss form submission like the dashboard would do"""
    
    print("="*80)
    print("TESTING MAX DAILY LOSS FORM SUBMISSION")
    print("="*80)
    
    # Get current config first
    try:
        response = requests.get('http://127.0.0.1:5000/api/config', timeout=10)
        if response.status_code != 200:
            print("❌ Failed to get current config")
            return
        
        current_config = response.json()
        print(f"Current max_daily_loss_percent: {current_config.get('max_daily_loss_percent')}")
        
    except Exception as e:
        print(f"❌ Error getting config: {e}")
        return
    
    # Test form submission with current daily loss value
    print("\n1. TESTING FORM SUBMISSION (5% daily loss):")
    
    # Simulate what the form would send
    form_data = current_config.copy()
    form_data['max_daily_loss_percent'] = 5  # Should work
    
    try:
        response = requests.post('http://127.0.0.1:5000/api/config', 
                               json=form_data, 
                               timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                print("   ✅ Form submission successful with 5% daily loss")
            else:
                print(f"   ❌ Form submission failed: {result.get('message')}")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test various daily loss percentages
    print("\n2. TESTING VARIOUS DAILY LOSS PERCENTAGES:")
    test_percentages = [1, 3, 5, 8, 10, 15, 20]
    
    for percentage in test_percentages:
        test_data = current_config.copy()
        test_data['max_daily_loss_percent'] = percentage
        
        try:
            response = requests.post('http://127.0.0.1:5000/api/config', 
                                   json=test_data, 
                                   timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    print(f"   ✅ {percentage}% daily loss accepted")
                else:
                    print(f"   ❌ {percentage}% daily loss rejected: {result.get('message')}")
            else:
                print(f"   ❌ {percentage}% HTTP error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ {percentage}% error: {e}")
    
    # Test edge cases that should fail
    print("\n3. TESTING EDGE CASES (should fail):")
    edge_percentages = [0, 0.5, 21, 25]
    
    for percentage in edge_percentages:
        test_data = current_config.copy()
        test_data['max_daily_loss_percent'] = percentage
        
        try:
            response = requests.post('http://127.0.0.1:5000/api/config', 
                                   json=test_data, 
                                   timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    print(f"   ❌ {percentage}% daily loss incorrectly accepted")
                else:
                    print(f"   ✅ {percentage}% daily loss correctly rejected: {result.get('message')}")
            else:
                print(f"   ❌ {percentage}% HTTP error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ {percentage}% error: {e}")
    
    print("\n" + "="*80)
    print("MAX DAILY LOSS FORM SUBMISSION TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    test_max_daily_loss_form_submission()