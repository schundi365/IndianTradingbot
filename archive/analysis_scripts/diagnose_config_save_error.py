#!/usr/bin/env python3
"""
Diagnose the configuration save error
"""

import requests
import json

def test_config_endpoint():
    """Test the configuration endpoint to see what's being returned"""
    
    base_url = "http://127.0.0.1:5000"
    
    # Test GET first
    print("Testing GET /api/config...")
    try:
        response = requests.get(f"{base_url}/api/config", timeout=10)
        print(f"GET Status: {response.status_code}")
        print(f"GET Headers: {dict(response.headers)}")
        print(f"GET Content: {response.text[:500]}...")
        
        if response.status_code == 200:
            try:
                config_data = response.json()
                print("✅ GET request successful - JSON response received")
            except json.JSONDecodeError as e:
                print(f"❌ GET request returned invalid JSON: {e}")
                print(f"Response content: {response.text}")
        
    except Exception as e:
        print(f"❌ GET request failed: {e}")
    
    print("\n" + "="*60 + "\n")
    
    # Test POST with minimal config
    print("Testing POST /api/config...")
    test_config = {
        "symbols": ["EURUSD"],
        "timeframe": 16385,
        "risk_percent": 1.0,
        "reward_ratio": 1.5
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/config",
            json=test_config,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"POST Status: {response.status_code}")
        print(f"POST Headers: {dict(response.headers)}")
        print(f"POST Content: {response.text}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print("✅ POST request successful - JSON response received")
                print(f"Result: {result}")
            except json.JSONDecodeError as e:
                print(f"❌ POST request returned invalid JSON: {e}")
                print("This is likely an HTML error page being returned")
                
                # Check if it's HTML
                if response.text.strip().startswith('<!'):
                    print("🔍 Response appears to be HTML - there's likely a server error")
                    # Extract error from HTML if possible
                    if "Traceback" in response.text:
                        print("🐛 Server traceback detected in HTML response")
        else:
            print(f"❌ POST request failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ POST request failed: {e}")

def check_dashboard_status():
    """Check if dashboard is running properly"""
    
    base_url = "http://127.0.0.1:5000"
    
    try:
        response = requests.get(base_url, timeout=5)
        print(f"Dashboard Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Dashboard is accessible")
        else:
            print(f"❌ Dashboard returned status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Dashboard not accessible: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("DIAGNOSING CONFIGURATION SAVE ERROR")
    print("=" * 60)
    
    check_dashboard_status()
    print("\n" + "="*60 + "\n")
    test_config_endpoint()