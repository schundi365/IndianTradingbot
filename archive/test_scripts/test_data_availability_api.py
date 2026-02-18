#!/usr/bin/env python3
"""
Test script for the Symbol Data Availability API endpoint
"""

import requests
import json
import sys

def test_data_availability_api():
    """Test the /api/symbols/data-availability endpoint"""
    
    # API endpoint
    url = "http://localhost:5000/api/symbols/data-availability"
    
    # Test data
    test_data = {
        "symbols": ["XAUUSD", "XAGUSD", "EURUSD", "BTCUSD"],
        "bars": 200,
        "timeframe": 16385  # H1
    }
    
    print("🔍 Testing Symbol Data Availability API")
    print("=" * 50)
    print(f"URL: {url}")
    print(f"Test Data: {json.dumps(test_data, indent=2)}")
    print("=" * 50)
    
    try:
        # Make POST request
        response = requests.post(url, json=test_data, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print("=" * 50)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API Response:")
            print(json.dumps(data, indent=2))
            
            if data.get('status') == 'success':
                print("\n📊 Summary:")
                summary = data.get('summary', {})
                print(f"Total Symbols: {summary.get('total_symbols', 0)}")
                print(f"Available Symbols: {summary.get('available_symbols', 0)}")
                print(f"Requested Bars: {summary.get('requested_bars', 0)}")
                print(f"Timeframe: {summary.get('timeframe', 0)}")
                
                print("\n📋 Individual Results:")
                for result in data.get('results', []):
                    status = "✅" if result['available'] else "❌"
                    symbol = result['symbol']
                    bars = result['bars_available']
                    error = result.get('error', '')
                    print(f"{status} {symbol}: {bars} bars available {f'({error})' if error else ''}")
                
                print("\n🎉 Test PASSED - API working correctly!")
                return True
            else:
                print(f"❌ API returned error: {data.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Dashboard server not running")
        print("💡 Start the dashboard first: python web_dashboard.py")
        return False
    except requests.exceptions.Timeout:
        print("❌ Timeout Error: Request took too long")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")
        return False

def test_invalid_data():
    """Test API with invalid data"""
    print("\n🧪 Testing Invalid Data Handling")
    print("=" * 50)
    
    url = "http://localhost:5000/api/symbols/data-availability"
    
    # Test cases
    test_cases = [
        {
            "name": "Empty symbols",
            "data": {"symbols": [], "bars": 200, "timeframe": 16385}
        },
        {
            "name": "Invalid symbols",
            "data": {"symbols": ["INVALID123", "FAKE456"], "bars": 200, "timeframe": 16385}
        },
        {
            "name": "Extreme bar count",
            "data": {"symbols": ["XAUUSD"], "bars": 10000, "timeframe": 16385}
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🔬 Test: {test_case['name']}")
        try:
            response = requests.post(url, json=test_case['data'], timeout=10)
            data = response.json()
            print(f"Status: {data.get('status', 'unknown')}")
            if data.get('status') == 'error':
                print(f"Error Message: {data.get('message', 'No message')}")
            else:
                print(f"Results: {len(data.get('results', []))} symbols processed")
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    print("🚀 Symbol Data Availability API Test Suite")
    print("=" * 60)
    
    # Test main functionality
    success = test_data_availability_api()
    
    if success:
        # Test edge cases
        test_invalid_data()
        print("\n✅ All tests completed!")
    else:
        print("\n❌ Main test failed - skipping additional tests")
        sys.exit(1)