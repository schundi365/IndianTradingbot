#!/usr/bin/env python3
"""
Test configuration validation to debug the confidence issue
"""

import requests
import json

def test_config_validation():
    """Test the configuration validation with different confidence values"""
    base_url = "http://127.0.0.1:5000"
    
    print("🧪 Testing Configuration Validation...")
    print("="*60)
    
    # Test different confidence values
    test_cases = [
        {"value": 0.6, "description": "60% as decimal (0.6)"},
        {"value": 60, "description": "60% as integer (60)"},
        {"value": 0.2, "description": "20% as decimal (0.2)"},
        {"value": 0.9, "description": "90% as decimal (0.9)"},
        {"value": 0.5, "description": "50% as decimal (0.5)"},
    ]
    
    for test_case in test_cases:
        print(f"\nTesting {test_case['description']}:")
        
        config = {
            "risk_percent": 1.0,
            "min_trade_confidence": test_case["value"],
            "logging_level": "detailed",
            "symbols": ["BTCUSD"],
            "timeframe": 30,
            "max_daily_loss": 100,
            "use_volume_filter": True
        }
        
        try:
            response = requests.post(
                f"{base_url}/api/config",
                json=config,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    print(f"  ✅ SUCCESS: Configuration accepted")
                else:
                    print(f"  ❌ ERROR: {data.get('message', 'Unknown error')}")
            else:
                print(f"  ❌ HTTP ERROR: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"  Error message: {error_data.get('message', 'No message')}")
                except:
                    print(f"  Response text: {response.text[:200]}")
                    
        except Exception as e:
            print(f"  ❌ EXCEPTION: {e}")
    
    # Test what the frontend actually sends
    print(f"\n🔍 Testing Frontend Logic Simulation:")
    print("Simulating what happens when user enters 60% in the form:")
    
    # Simulate frontend conversion: user enters 60, frontend divides by 100
    user_input = 60
    frontend_value = user_input / 100  # This should be 0.6
    
    print(f"  User enters: {user_input}%")
    print(f"  Frontend sends: {frontend_value}")
    print(f"  Should be valid: {0.2 <= frontend_value <= 0.9}")

if __name__ == "__main__":
    print("🚀 Configuration Validation Test")
    print("="*60)
    
    test_config_validation()
    
    print("\n" + "="*60)
    print("💡 If 0.6 fails validation, there's a bug in the backend")
    print("💡 If 60 fails validation, there's a bug in the frontend")
    print("="*60)