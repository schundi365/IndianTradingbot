#!/usr/bin/env python3
"""
Restart the trading bot to pick up the detailed logging changes
"""

import requests
import time
import sys

def restart_bot():
    """Restart the trading bot via the web API"""
    base_url = "http://localhost:5000"
    
    try:
        print("🔄 Stopping the trading bot...")
        
        # Stop the bot
        response = requests.post(f"{base_url}/api/bot/stop", timeout=10)
        if response.status_code == 200:
            print("✅ Bot stopped successfully")
        else:
            print(f"⚠️ Stop request returned status {response.status_code}: {response.text}")
        
        # Wait a moment for the bot to fully stop
        print("⏳ Waiting 3 seconds for bot to fully stop...")
        time.sleep(3)
        
        print("🚀 Starting the trading bot...")
        
        # Start the bot
        response = requests.post(f"{base_url}/api/bot/start", timeout=10)
        if response.status_code == 200:
            print("✅ Bot started successfully")
            print("🎉 Bot restarted! The detailed logging should now be active.")
            print("📋 Check the trading_bot.log file for detailed indicator calculations.")
        else:
            print(f"❌ Start request returned status {response.status_code}: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the web dashboard at http://localhost:5000")
        print("   Make sure the web dashboard is running with: python web_dashboard.py")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("❌ Request timed out. The web dashboard might be unresponsive.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🔧 RESTARTING TRADING BOT FOR DETAILED LOGGING")
    print("=" * 50)
    restart_bot()
    print("=" * 50)
    print("✅ RESTART COMPLETE")