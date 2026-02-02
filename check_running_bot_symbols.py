#!/usr/bin/env python3
"""
Check what symbols the currently running bot actually has
"""

import requests
import json

def check_bot_symbols():
    """Check the symbols in the running bot via API"""
    print("🔍 CHECKING RUNNING BOT SYMBOLS")
    print("=" * 40)
    
    try:
        # Get bot configuration via API
        response = requests.get('http://localhost:5000/api/config', timeout=5)
        
        if response.status_code == 200:
            config = response.json()
            symbols = config.get('symbols', [])
            
            print(f"✅ API Response received")
            print(f"📊 Symbols in running bot: {len(symbols)}")
            
            if len(symbols) > 0:
                print(f"\n📋 ALL SYMBOLS:")
                for i, symbol in enumerate(symbols, 1):
                    print(f"  {i:2d}. {symbol}")
                
                if len(symbols) == 18:
                    print(f"\n✅ SUCCESS: Bot has all 18 symbols!")
                    return True
                else:
                    print(f"\n⚠️  Bot only has {len(symbols)} symbols, expected 18")
                    return False
            else:
                print(f"❌ No symbols found in bot configuration")
                return False
                
        else:
            print(f"❌ API request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking bot symbols: {str(e)}")
        return False

def check_dashboard_status():
    """Check if dashboard is running and responsive"""
    print("\n🌐 CHECKING DASHBOARD STATUS")
    print("=" * 40)
    
    try:
        response = requests.get('http://localhost:5000/api/bot/status', timeout=5)
        
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Dashboard is responsive")
            print(f"📊 Bot running: {status.get('running', False)}")
            print(f"📊 Bot status: {status.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ Dashboard not responsive: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Dashboard not accessible: {str(e)}")
        return False

def main():
    """Main check function"""
    dashboard_ok = check_dashboard_status()
    
    if dashboard_ok:
        symbols_ok = check_bot_symbols()
        
        if symbols_ok:
            print(f"\n🎉 EXCELLENT: Bot is running with all 18 symbols!")
            print(f"   The symbol processing issue should be resolved.")
        else:
            print(f"\n⚠️  ISSUE PERSISTS: Bot still doesn't have all symbols")
            print(f"   Further investigation needed.")
    else:
        print(f"\n❌ Cannot check bot symbols - dashboard not accessible")

if __name__ == "__main__":
    main()