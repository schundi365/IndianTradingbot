#!/usr/bin/env python3
"""
Emergency Bot Restart with Error Monitoring
"""

import requests
import time

def restart_bot_safely():
    """Restart bot and monitor for errors"""
    print("EMERGENCY BOT RESTART")
    print("=" * 40)
    
    try:
        # Stop bot via API
        print("Stopping bot...")
        response = requests.post("http://localhost:5000/api/bot/stop", timeout=10)
        if response.status_code == 200:
            print("Bot stopped successfully")
        else:
            print("Bot stop API call failed, continuing...")
        
        time.sleep(3)
        
        # Start bot via API
        print("Starting bot...")
        response = requests.post("http://localhost:5000/api/bot/start", timeout=10)
        if response.status_code == 200:
            print("Bot started successfully")
            
            # Monitor for errors
            print("Monitoring for errors...")
            time.sleep(10)
            
            # Check recent logs
            response = requests.get("http://localhost:5000/api/logs?lines=50", timeout=5)
            if response.status_code == 200:
                logs = response.text
                if "KeyError: 'adx'" in logs:
                    print("ERROR: ADX KeyError still present!")
                elif "name 'logger' is not defined" in logs:
                    print("ERROR: Logger NameError still present!")
                else:
                    print("SUCCESS: No critical errors detected in recent logs")
            
            return True
        else:
            print("ERROR: Bot start failed")
            return False
            
    except Exception as e:
        print(f"ERROR during restart: {e}")
        return False

if __name__ == "__main__":
    restart_bot_safely()