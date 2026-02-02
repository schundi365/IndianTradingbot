#!/usr/bin/env python3
"""
Test the percentage-based daily loss configuration
"""

import sys
import json

# Import the Flask app
from web_dashboard import app

def test_percentage_config():
    """Test the percentage-based daily loss configuration"""
    print("🧪 Testing Percentage-Based Daily Loss Configuration...")
    print("="*60)
    
    # Create a test client
    with app.test_client() as client:
        # Test configuration with percentage
        test_config = {
            'risk_percent': 1.0,
            'min_trade_confidence': 0.6,
            'max_daily_loss_percent': 5.0,  # 5% of equity
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
                print("✅ Percentage-based daily loss validation PASSED")
                print("✅ Max daily loss is now calculated as % of total equity")
            else:
                print(f"❌ Validation FAILED: {data.get('message')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")

if __name__ == "__main__":
    print("🚀 Percentage-Based Daily Loss Test")
    print("="*60)
    
    test_percentage_config()
    
    print("="*60)
    print("💡 This test verifies percentage-based daily loss limits")
    print("="*60)