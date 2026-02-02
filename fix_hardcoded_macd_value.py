#!/usr/bin/env python3
"""
Fix Hardcoded MACD Value Issue
"""

import json
import requests
import time

def fix_hardcoded_macd():
    """Fix the hardcoded MACD value issue"""
    print("🔧 FIXING HARDCODED MACD VALUE ISSUE")
    print("=" * 50)
    
    # Step 1: Verify bot_config.json has correct value
    try:
        with open('bot_config.json', 'r') as f:
            config = json.load(f)
        
        macd_value = config.get('macd_min_histogram', 'NOT_FOUND')
        print(f"✅ bot_config.json MACD value: {macd_value}")
        
        if macd_value != 0.0003:
            print(f"⚠️ Updating bot_config.json to 0.0003...")
            config['macd_min_histogram'] = 0.0003
            with open('bot_config.json', 'w') as f:
                json.dump(config, f, indent=2)
            print("✅ bot_config.json updated")
        
    except Exception as e:
        print(f"❌ Error reading bot_config.json: {e}")
        return False
    
    # Step 2: Check config_manager.py default
    try:
        with open('src/config_manager.py', 'r') as f:
            config_manager_content = f.read()
        
        if "'macd_min_histogram': 0.0005" in config_manager_content:
            print("❌ config_manager.py still has hardcoded 0.0005")
            return False
        elif "'macd_min_histogram': 0.0003" in config_manager_content:
            print("✅ config_manager.py has correct default 0.0003")
        else:
            print("⚠️ Could not find MACD value in config_manager.py")
        
    except Exception as e:
        print(f"❌ Error reading config_manager.py: {e}")
    
    # Step 3: Force dashboard to reload configuration
    try:
        print("\n🔄 Forcing dashboard configuration reload...")
        
        # Get current config from dashboard
        response = requests.get("http://localhost:5000/api/config", timeout=5)
        if response.status_code == 200:
            current_config = response.json()
            dashboard_macd = current_config.get('macd_min_histogram', 'NOT_FOUND')
            print(f"📊 Dashboard current MACD: {dashboard_macd}")
            
            # Force update with correct value
            update_data = {
                'macd_min_histogram': 0.0003,
                'symbols': config.get('symbols', ['XAUUSD']),
                'timeframe': config.get('timeframe', 15),
                'risk_percent': config.get('risk_percent', 1.0),
                'min_trade_confidence': config.get('min_trade_confidence', 0.4)
            }
            
            response = requests.post("http://localhost:5000/api/config", 
                                   json=update_data, 
                                   timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    print("✅ Dashboard configuration updated successfully")
                    
                    # Verify the update
                    time.sleep(1)
                    response = requests.get("http://localhost:5000/api/config", timeout=5)
                    if response.status_code == 200:
                        updated_config = response.json()
                        new_macd = updated_config.get('macd_min_histogram', 'NOT_FOUND')
                        print(f"🔍 Dashboard updated MACD: {new_macd}")
                        
                        if new_macd == 0.0003:
                            print("🎉 MACD value successfully updated to 0.0003!")
                            return True
                        else:
                            print(f"❌ MACD still showing {new_macd} instead of 0.0003")
                            return False
                else:
                    print(f"❌ Dashboard update failed: {result.get('message', 'Unknown error')}")
                    return False
            else:
                print(f"❌ Dashboard API error: {response.status_code}")
                return False
        else:
            print(f"❌ Dashboard not responding: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating dashboard: {e}")
        return False

def verify_bot_logs():
    """Check if the bot is now using the correct MACD value"""
    print(f"\n🔍 CHECKING BOT LOGS FOR MACD VALUE:")
    print("-" * 40)
    
    try:
        with open('trading_bot.log', 'r') as f:
            log_content = f.read()
        
        # Look for recent MACD threshold logs
        import re
        macd_patterns = [
            r'MACD.*threshold.*0\.0003',
            r'MACD.*0\.0003',
            r'macd_min_histogram.*0\.0003'
        ]
        
        found_correct = False
        for pattern in macd_patterns:
            matches = re.findall(pattern, log_content, re.IGNORECASE)
            if matches:
                print(f"✅ Found correct MACD value in logs: {len(matches)} occurrences")
                found_correct = True
                break
        
        # Also check for the old value
        old_patterns = [
            r'MACD.*threshold.*0\.0005',
            r'MACD.*0\.0005',
            r'macd_min_histogram.*0\.0005'
        ]
        
        found_old = False
        for pattern in old_patterns:
            matches = re.findall(pattern, log_content, re.IGNORECASE)
            if matches:
                print(f"⚠️ Still found old MACD value in logs: {len(matches)} occurrences")
                found_old = True
                break
        
        if found_correct and not found_old:
            print("🎉 Bot is using correct MACD value!")
            return True
        elif found_old:
            print("❌ Bot may still be using old MACD value - restart required")
            return False
        else:
            print("ℹ️ No MACD values found in recent logs")
            return None
            
    except Exception as e:
        print(f"❌ Error reading logs: {e}")
        return False

if __name__ == "__main__":
    success = fix_hardcoded_macd()
    
    if success:
        print(f"\n🎉 HARDCODED MACD FIX COMPLETE!")
        print("The dashboard should now show 0.0003 as the MACD value")
        print("Restart the bot to ensure it uses the new value")
        
        # Check logs
        log_result = verify_bot_logs()
        if log_result is False:
            print("\n⚠️ RESTART REQUIRED:")
            print("The bot may still be using cached values")
            print("Please restart the bot to apply the new MACD value")
        
    else:
        print(f"\n❌ HARDCODED MACD FIX FAILED!")
        print("Manual intervention may be required")
        print("Check config_manager.py and restart the bot")