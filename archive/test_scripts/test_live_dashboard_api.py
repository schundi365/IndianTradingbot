#!/usr/bin/env python3
"""
Test script to check the live dashboard API
"""

import requests
import json

def test_live_dashboard_api():
    """Test the live dashboard API endpoint"""
    
    print("="*80)
    print("TESTING LIVE DASHBOARD API")
    print("="*80)
    
    try:
        # Test the config API endpoint
        response = requests.get('http://127.0.0.1:5000/api/config', timeout=10)
        
        if response.status_code == 200:
            config = response.json()
            
            print("\n✅ API RESPONSE SUCCESSFUL")
            print(f"   RSI Overbought: {config.get('rsi_overbought', 'NOT FOUND')}")
            print(f"   RSI Oversold: {config.get('rsi_oversold', 'NOT FOUND')}")
            print(f"   MACD Min Histogram: {config.get('macd_min_histogram', 'NOT FOUND')}")
            print(f"   Min Trade Confidence: {config.get('min_trade_confidence', 'NOT FOUND')}")
            print(f"   Volume MA Threshold: {config.get('min_volume_ma', 'NOT FOUND')}")
            
            # Check if values are correct
            rsi_overbought = config.get('rsi_overbought')
            rsi_oversold = config.get('rsi_oversold')
            macd_histogram = config.get('macd_min_histogram')
            
            print("\n📊 VALIDATION:")
            if rsi_overbought == 75:
                print("   ✅ RSI Overbought is CORRECT (75)")
            else:
                print(f"   ❌ RSI Overbought is WRONG ({rsi_overbought}) - should be 75")
            
            if rsi_oversold == 25:
                print("   ✅ RSI Oversold is CORRECT (25)")
            else:
                print(f"   ❌ RSI Oversold is WRONG ({rsi_oversold}) - should be 25")
            
            if macd_histogram == 0.0005:
                print("   ✅ MACD Min Histogram is CORRECT (0.0005)")
            else:
                print(f"   ❌ MACD Min Histogram is WRONG ({macd_histogram}) - should be 0.0005")
                
        else:
            print(f"❌ API ERROR: Status {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR: Dashboard server not running or not accessible")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    test_live_dashboard_api()