#!/usr/bin/env python3
"""
Sync dashboard configuration with optimized bot_config.json
"""

import json
import requests

def sync_dashboard_config():
    """Update dashboard config to match optimized bot_config.json"""
    
    print("="*80)
    print("SYNCING DASHBOARD WITH OPTIMIZED CONFIG")
    print("="*80)
    
    # Read optimized bot_config.json
    try:
        with open('bot_config.json', 'r') as f:
            optimized_config = json.load(f)
        
        print("OPTIMIZED CONFIG VALUES:")
        print(f"   Timeframe: M{optimized_config.get('timeframe')}")
        print(f"   MACD Min Histogram: {optimized_config.get('macd_min_histogram')}")
        print(f"   Min Volume MA: {optimized_config.get('min_volume_ma')}")
        print(f"   Use ADX: {optimized_config.get('use_adx')}")
        print(f"   Use Trend Filter: {optimized_config.get('use_trend_filter')}")
        
    except Exception as e:
        print(f"❌ Error reading bot_config.json: {e}")
        return
    
    # Update dashboard configuration
    print("\nUPDATING DASHBOARD CONFIGURATION:")
    try:
        response = requests.post('http://127.0.0.1:5000/api/config', 
                               json=optimized_config, 
                               timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                print("✅ Dashboard configuration updated successfully!")
                
                # Verify the update
                verify_response = requests.get('http://127.0.0.1:5000/api/config', timeout=10)
                if verify_response.status_code == 200:
                    updated_config = verify_response.json()
                    
                    print("\nVERIFICATION - DASHBOARD NOW SHOWS:")
                    print(f"   Timeframe: M{updated_config.get('timeframe')}")
                    print(f"   MACD Min Histogram: {updated_config.get('macd_min_histogram')}")
                    print(f"   Min Volume MA: {updated_config.get('min_volume_ma')}")
                    print(f"   Use ADX: {updated_config.get('use_adx')}")
                    print(f"   Use Trend Filter: {updated_config.get('use_trend_filter')}")
                    
                    # Check if values match
                    if (updated_config.get('timeframe') == optimized_config.get('timeframe') and
                        updated_config.get('macd_min_histogram') == optimized_config.get('macd_min_histogram') and
                        updated_config.get('min_volume_ma') == optimized_config.get('min_volume_ma')):
                        print("\n🎉 SUCCESS: Dashboard and bot_config.json are now synchronized!")
                        print("\n📋 NEXT STEPS:")
                        print("   1. Bot should automatically pick up new config on next cycle")
                        print("   2. Monitor logs for M15 timeframe and improved signal generation")
                        print("   3. Check for 'SIGNAL GENERATED' messages in next few minutes")
                    else:
                        print("\n⚠️  WARNING: Some values still don't match")
                        
            else:
                print(f"❌ Failed to update dashboard: {result.get('message')}")
                
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error updating dashboard: {e}")
    
    print("\n" + "="*80)
    print("DASHBOARD SYNC COMPLETE")
    print("="*80)

if __name__ == "__main__":
    sync_dashboard_config()