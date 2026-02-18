#!/usr/bin/env python3
"""
Test configuration save functionality after fixing logger issues
"""

import requests
import json

def test_config_endpoints():
    """Test both GET and POST config endpoints"""
    
    base_url = "http://127.0.0.1:5000"
    
    print("🧪 Testing Configuration API Endpoints...")
    print("=" * 50)
    
    # Test GET config
    try:
        print("1️⃣ Testing GET /api/config...")
        response = requests.get(f"{base_url}/api/config", timeout=10)
        print(f"   Status Code: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")
        
        if response.status_code == 200:
            config_data = response.json()
            print(f"   ✅ GET config successful - got {len(config_data)} config items")
            
            # Test POST config with a small update
            print("\n2️⃣ Testing POST /api/config...")
            
            # Make a small change to test saving
            test_config = config_data.copy()
            test_config['risk_percent'] = 1.5  # Safe test value
            
            post_response = requests.post(
                f"{base_url}/api/config",
                headers={'Content-Type': 'application/json'},
                json=test_config,
                timeout=10
            )
            
            print(f"   Status Code: {post_response.status_code}")
            print(f"   Content-Type: {post_response.headers.get('content-type', 'unknown')}")
            
            if post_response.status_code == 200:
                result = post_response.json()
                print(f"   ✅ POST config successful: {result.get('message', 'No message')}")
                print(f"   Status: {result.get('status', 'unknown')}")
            else:
                print(f"   ❌ POST failed with status {post_response.status_code}")
                print(f"   Response: {post_response.text[:200]}...")
                
        else:
            print(f"   ❌ GET failed with status {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to dashboard. Make sure it's running on port 5000")
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test performance endpoint too
    print("\n3️⃣ Testing GET /api/analysis/performance...")
    try:
        perf_response = requests.get(f"{base_url}/api/analysis/performance", timeout=10)
        print(f"   Status Code: {perf_response.status_code}")
        print(f"   Content-Type: {perf_response.headers.get('content-type', 'unknown')}")
        
        if perf_response.status_code == 200:
            perf_data = perf_response.json()
            print(f"   ✅ Performance API successful - got {len(perf_data)} metrics")
        else:
            print(f"   ❌ Performance API failed with status {perf_response.status_code}")
            print(f"   Response: {perf_response.text[:200]}...")
            
    except Exception as e:
        print(f"   ❌ Performance API error: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")

if __name__ == "__main__":
    test_config_endpoints()