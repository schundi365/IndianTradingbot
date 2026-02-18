#!/usr/bin/env python3
"""
Test the web dashboard validation by importing the function directly
"""

import sys
import json

# Import the Flask app
from web_dashboard import app

def test_web_validation():
    """Test the web dashboard validation directly"""
    print("🧪 Testing Web Dashboard Validation...")
    print("="*50)
    
    # Create a test client
    with app.test_client() as client:
        # Test configuration
        test_config = {
            'risk_percent': 1.0,
            'min_trade_confidence': 0.6,  # 60% as decimal
            'max_daily_loss': 100,  # $100
            'symbols': ['BTCUSD'],
            'timeframe': 30,
            'use_volume_filter': True,
            'logging_level': 'detailed'
        }
        
        print("Testing configuration:")
        for key, value in test_config.items():
            print(f"  {key}: {value}")
        
        print("\nSending POST request to /api/config...")
        
        response = client.post(
            '/api/config',
            data=json.dumps(test_config),
            content_type='application/json'
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.get_json()
            print(f"Response: {data}")
            
            if data.get('status') == 'success':
                print("✅ Web dashboard validation PASSED")
            else:
                print(f"❌ Web dashboard validation FAILED: {data.get('message')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.get_data(as_text=True)}")

if __name__ == "__main__":
    print("🚀 Web Dashboard Validation Test")
    print("="*50)
    
    test_web_validation()
    
    print("="*50)
    print("💡 This test uses Flask test client to test validation directly")
    print("="*50)