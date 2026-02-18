#!/usr/bin/env python3
"""
Force Dashboard Configuration Reload
"""

import json
import requests
import time

def force_dashboard_reload():
    """Force dashboard to reload configuration from bot_config.json"""
    print("🔄 FORCING DASHBOARD CONFIGURATION RELOAD")
    print("=" * 50)
    
    # Read the current bot_config.json
    try:
        with open('bot_config.json', 'r') as f:
            bot_config = json.load(f)
        
        print(f"✅ Bot config MACD histogram: {bot_config.get('macd_min_histogram', 'NOT_FOUND')}")
        print(f"✅ Bot config 24/7 trading: {not bot_config.get('enable_trading_hours', True)}")
        print(f"✅ Bot config max trades: {bot_config.get('max_daily_trades', 'NOT_FOUND')}")
        
    except Exception as e:
        print(f"❌ Error reading bot_config.json: {e}")
        return False
    
    # Try to update dashboard configuration via API
    try:
        # First get current config
        response = requests.get("http://localhost:5000/api/config", timeout=5)
        if response.status_code != 200:
            print(f"❌ Dashboard API not responding: {response.status_code}")
            return False
        
        current_config = response.json()
        print(f"📊 Current dashboard MACD: {current_config.get('macd_min_histogram', 'NOT_FOUND')}")
        
        # Update with correct values from bot_config.json
        update_data = {
            'macd_min_histogram': bot_config.get('macd_min_histogram', 0.0005),
            'enable_trading_hours': bot_config.get('enable_trading_hours', False),
            'max_daily_trades': bot_config.get('max_daily_trades', 999),
            'min_trade_confidence': bot_config.get('min_trade_confidence', 0.5),
            'min_volume_ma': bot_config.get('min_volume_ma', 0.7),
            'symbols': bot_config.get('symbols', ['XAUUSD', 'XAGUSD']),
            'timeframe': bot_config.get('timeframe', 15)
        }
        
        print("🔄 Updating dashboard configuration...")
        response = requests.post("http://localhost:5000/api/config", 
                               json=update_data, 
                               timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                print("✅ Dashboard configuration updated successfully!")
                
                # Verify the update
                time.sleep(1)
                response = requests.get("http://localhost:5000/api/config", timeout=5)
                if response.status_code == 200:
                    updated_config = response.json()
                    macd_value = updated_config.get('macd_min_histogram', 'NOT_FOUND')
                    trading_hours = updated_config.get('enable_trading_hours', True)
                    max_trades = updated_config.get('max_daily_trades', 0)
                    
                    print(f"🔍 Verification - MACD histogram: {macd_value}")
                    print(f"🔍 Verification - 24/7 trading: {not trading_hours}")
                    print(f"🔍 Verification - Max trades: {max_trades}")
                    
                    if macd_value == 0.0005:
                        print("🎉 MACD PRECISION FIX SUCCESSFUL!")
                    else:
                        print(f"⚠️ MACD still incorrect: {macd_value}")
                        
                    return macd_value == 0.0005
                else:
                    print("❌ Failed to verify update")
                    return False
            else:
                print(f"❌ Update failed: {result.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ API update failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating dashboard: {e}")
        return False

if __name__ == "__main__":
    success = force_dashboard_reload()
    if success:
        print("\n🎉 DASHBOARD CONFIGURATION RELOAD COMPLETE!")
    else:
        print("\n❌ DASHBOARD CONFIGURATION RELOAD FAILED!")
        print("   Try restarting the dashboard: python web_dashboard.py")