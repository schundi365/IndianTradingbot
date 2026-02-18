#!/usr/bin/env python3
"""
Test script to check what values the dashboard form is actually sending
"""

import requests
import json

def test_dashboard_form_values():
    """Test what values the dashboard form would send"""
    
    print("="*80)
    print("TESTING DASHBOARD FORM VALUES")
    print("="*80)
    
    # Get current config
    try:
        response = requests.get('http://127.0.0.1:5000/api/config', timeout=10)
        if response.status_code != 200:
            print("❌ Failed to get current config")
            return
        
        current_config = response.json()
        
        print("CURRENT CONFIG VALUES:")
        print(f"   min_trade_confidence: {current_config.get('min_trade_confidence')}")
        print(f"   max_daily_loss_percent: {current_config.get('max_daily_loss_percent')}")
        print(f"   macd_min_histogram: {current_config.get('macd_min_histogram')}")
        print(f"   rsi_overbought: {current_config.get('rsi_overbought')}")
        print(f"   rsi_oversold: {current_config.get('rsi_oversold')}")
        
    except Exception as e:
        print(f"❌ Error getting config: {e}")
        return
    
    # Simulate form submission with typical form values
    print("\n1. SIMULATING FORM SUBMISSION:")
    
    # Create a form-like submission (simulating what JavaScript would send)
    form_submission = {
        'symbols': current_config.get('symbols', ['BTCUSD']),
        'timeframe': current_config.get('timeframe', 30),
        'risk_percent': current_config.get('risk_percent', 1.0),
        'min_trade_confidence': current_config.get('min_trade_confidence', 0.6),
        'max_daily_loss_percent': current_config.get('max_daily_loss_percent', 5),
        'macd_min_histogram': current_config.get('macd_min_histogram', 0.0005),
        'rsi_overbought': current_config.get('rsi_overbought', 75),
        'rsi_oversold': current_config.get('rsi_oversold', 25),
        'reward_ratio': current_config.get('reward_ratio', 2.0),
        'fast_ma_period': current_config.get('fast_ma_period', 10),
        'slow_ma_period': current_config.get('slow_ma_period', 30),
        'use_rsi': current_config.get('use_rsi', True),
        'use_macd': current_config.get('use_macd', True),
        'use_adx': current_config.get('use_adx', True)
    }
    
    print("FORM SUBMISSION VALUES:")
    for key, value in form_submission.items():
        print(f"   {key}: {value} ({type(value).__name__})")
    
    # Test the submission
    try:
        response = requests.post('http://127.0.0.1:5000/api/config', 
                               json=form_submission, 
                               timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                print("\n✅ Form submission successful")
            else:
                print(f"\n❌ Form submission failed: {result.get('message')}")
                print(f"Full response: {result}")
        else:
            print(f"\n❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    # Test with problematic values that might be sent by form
    print("\n2. TESTING POTENTIALLY PROBLEMATIC VALUES:")
    
    # Test with string values (common form issue)
    problematic_submission = form_submission.copy()
    problematic_submission['macd_min_histogram'] = "0.0005"  # String instead of float
    
    try:
        response = requests.post('http://127.0.0.1:5000/api/config', 
                               json=problematic_submission, 
                               timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                print("   ✅ String MACD value accepted (converted to float)")
            else:
                print(f"   ❌ String MACD value rejected: {result.get('message')}")
        else:
            print(f"   ❌ String MACD HTTP error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ String MACD error: {e}")
    
    # Test with empty/null values
    empty_submission = form_submission.copy()
    empty_submission['macd_min_histogram'] = None
    
    try:
        response = requests.post('http://127.0.0.1:5000/api/config', 
                               json=empty_submission, 
                               timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                print("   ✅ Null MACD value accepted")
            else:
                print(f"   ❌ Null MACD value rejected: {result.get('message')}")
        else:
            print(f"   ❌ Null MACD HTTP error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Null MACD error: {e}")
    
    print("\n" + "="*80)
    print("DASHBOARD FORM VALUES TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    test_dashboard_form_values()