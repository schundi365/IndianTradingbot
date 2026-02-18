#!/usr/bin/env python3
"""
Check which configuration source the bot is actually using
"""

import json
import requests

def check_bot_config_source():
    """Check if bot is using bot_config.json or dashboard config"""
    
    print("="*80)
    print("CHECKING BOT CONFIGURATION SOURCE")
    print("="*80)
    
    # Check bot_config.json file
    print("1. CHECKING bot_config.json FILE:")
    try:
        with open('bot_config.json', 'r') as f:
            file_config = json.load(f)
        
        print(f"   Timeframe: M{file_config.get('timeframe')}")
        print(f"   MACD Min Histogram: {file_config.get('macd_min_histogram')}")
        print(f"   Min Volume MA: {file_config.get('min_volume_ma')}")
        print(f"   Use ADX: {file_config.get('use_adx')}")
        print(f"   Use Trend Filter: {file_config.get('use_trend_filter')}")
        print(f"   Last Updated: {file_config.get('last_updated')}")
        
    except Exception as e:
        print(f"   ❌ Error reading bot_config.json: {e}")
        return
    
    # Check dashboard API config
    print("\n2. CHECKING DASHBOARD API CONFIG:")
    try:
        response = requests.get('http://127.0.0.1:5000/api/config', timeout=10)
        if response.status_code == 200:
            api_config = response.json()
            
            print(f"   Timeframe: M{api_config.get('timeframe')}")
            print(f"   MACD Min Histogram: {api_config.get('macd_min_histogram')}")
            print(f"   Min Volume MA: {api_config.get('min_volume_ma')}")
            print(f"   Use ADX: {api_config.get('use_adx')}")
            print(f"   Use Trend Filter: {api_config.get('use_trend_filter')}")
            
        else:
            print(f"   ❌ Dashboard API error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error accessing dashboard API: {e}")
    
    # Compare configurations
    print("\n3. CONFIGURATION COMPARISON:")
    
    if file_config.get('timeframe') != api_config.get('timeframe'):
        print(f"   ⚠️  TIMEFRAME MISMATCH:")
        print(f"      File: M{file_config.get('timeframe')}")
        print(f"      API:  M{api_config.get('timeframe')}")
    else:
        print(f"   ✅ Timeframe matches: M{file_config.get('timeframe')}")
    
    if file_config.get('macd_min_histogram') != api_config.get('macd_min_histogram'):
        print(f"   ⚠️  MACD THRESHOLD MISMATCH:")
        print(f"      File: {file_config.get('macd_min_histogram')}")
        print(f"      API:  {api_config.get('macd_min_histogram')}")
    else:
        print(f"   ✅ MACD threshold matches: {file_config.get('macd_min_histogram')}")
    
    if file_config.get('min_volume_ma') != api_config.get('min_volume_ma'):
        print(f"   ⚠️  VOLUME FILTER MISMATCH:")
        print(f"      File: {file_config.get('min_volume_ma')}")
        print(f"      API:  {api_config.get('min_volume_ma')}")
    else:
        print(f"   ✅ Volume filter matches: {file_config.get('min_volume_ma')}")
    
    # Check which config the bot is actually using based on logs
    print("\n4. CHECKING ACTUAL BOT BEHAVIOR:")
    try:
        with open('trading_bot.log', 'r') as f:
            log_content = f.read()
        
        # Look for recent timeframe mentions
        if "Timeframe: M30" in log_content[-5000:]:  # Check last 5000 chars
            print("   🔍 LOG ANALYSIS: Bot is using M30 timeframe")
            if file_config.get('timeframe') == 15:
                print("   ❌ PROBLEM: Bot not using updated bot_config.json!")
                print("   📝 LIKELY CAUSE: Bot is using dashboard config or hardcoded values")
            else:
                print("   ✅ Bot is using bot_config.json (both show M30)")
        elif "Timeframe: M15" in log_content[-5000:]:
            print("   🔍 LOG ANALYSIS: Bot is using M15 timeframe")
            print("   ✅ Bot is using updated bot_config.json")
        else:
            print("   ⚠️  Could not determine timeframe from recent logs")
            
    except Exception as e:
        print(f"   ❌ Error reading logs: {e}")
    
    print("\n5. DIAGNOSIS:")
    if file_config.get('timeframe') == 15 and "Timeframe: M30" in log_content[-5000:]:
        print("   🚨 ISSUE IDENTIFIED: Bot is NOT using the updated bot_config.json")
        print("   📋 POSSIBLE CAUSES:")
        print("      • Bot is using dashboard configuration instead")
        print("      • Bot has hardcoded configuration values")
        print("      • Configuration not reloaded after restart")
        print("      • Bot reading from different config file location")
        
        print("\n   🔧 RECOMMENDED ACTIONS:")
        print("      1. Update dashboard configuration to match bot_config.json")
        print("      2. Force restart bot with explicit config file")
        print("      3. Check if bot is using config manager vs direct file reading")
        
    else:
        print("   ✅ Bot appears to be using correct configuration source")
    
    print("\n" + "="*80)
    print("CONFIGURATION SOURCE CHECK COMPLETE")
    print("="*80)

if __name__ == "__main__":
    check_bot_config_source()