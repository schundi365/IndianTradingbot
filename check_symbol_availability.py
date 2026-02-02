#!/usr/bin/env python3
"""
Check which symbols from the configuration are actually available in MT5
"""

import json
import sys
import os

# Add src directory to path
sys.path.append('src')

try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    print("⚠️  MetaTrader5 not available - using mock data")
    MT5_AVAILABLE = False

def check_mt5_connection():
    """Check if MT5 is available and can connect"""
    if not MT5_AVAILABLE:
        return False
    
    try:
        if not mt5.initialize():
            print("❌ Failed to initialize MT5")
            return False
        
        account_info = mt5.account_info()
        if account_info is None:
            print("❌ Failed to get account info")
            return False
        
        print(f"✅ Connected to MT5 account: {account_info.login}")
        return True
        
    except Exception as e:
        print(f"❌ MT5 connection error: {str(e)}")
        return False

def check_symbol_availability():
    """Check availability of all configured symbols"""
    print("🔍 CHECKING SYMBOL AVAILABILITY IN MT5")
    print("=" * 60)
    
    # Load symbols from config
    try:
        with open('bot_config.json', 'r') as f:
            config = json.load(f)
        symbols = config.get('symbols', [])
    except Exception as e:
        print(f"❌ Error loading config: {str(e)}")
        return
    
    if not MT5_AVAILABLE:
        print("⚠️  Cannot check - MT5 not available")
        return
    
    if not check_mt5_connection():
        return
    
    print(f"📊 Checking {len(symbols)} symbols...")
    print()
    
    available_symbols = []
    unavailable_symbols = []
    invisible_symbols = []
    
    for i, symbol in enumerate(symbols, 1):
        try:
            # Get symbol info
            symbol_info = mt5.symbol_info(symbol)
            
            if symbol_info is None:
                print(f"  {i:2d}. {symbol:<10} ❌ NOT FOUND")
                unavailable_symbols.append(symbol)
            elif not symbol_info.visible:
                print(f"  {i:2d}. {symbol:<10} ⚠️  NOT VISIBLE (trying to enable...)")
                # Try to make it visible
                if mt5.symbol_select(symbol, True):
                    print(f"      {symbol:<10} ✅ ENABLED")
                    available_symbols.append(symbol)
                else:
                    print(f"      {symbol:<10} ❌ FAILED TO ENABLE")
                    invisible_symbols.append(symbol)
            else:
                print(f"  {i:2d}. {symbol:<10} ✅ AVAILABLE")
                available_symbols.append(symbol)
                
        except Exception as e:
            print(f"  {i:2d}. {symbol:<10} ❌ ERROR: {str(e)}")
            unavailable_symbols.append(symbol)
    
    print()
    print("📊 SUMMARY:")
    print(f"  ✅ Available:     {len(available_symbols)}")
    print(f"  ⚠️  Invisible:     {len(invisible_symbols)}")
    print(f"  ❌ Unavailable:   {len(unavailable_symbols)}")
    
    if unavailable_symbols:
        print(f"\n❌ UNAVAILABLE SYMBOLS:")
        for symbol in unavailable_symbols:
            print(f"  - {symbol}")
    
    if invisible_symbols:
        print(f"\n⚠️  INVISIBLE SYMBOLS:")
        for symbol in invisible_symbols:
            print(f"  - {symbol}")
    
    # Check if this matches the log analysis
    log_symbols = ['XAUUSD', 'XAGUSD', 'XPTUSD', 'XPDUSD', 'EURUSD', 'GBPUSD', 'AUDUSD', 'NZDUSD']
    missing_from_logs = set(symbols) - set(log_symbols)
    
    print(f"\n🔍 COMPARISON WITH LOG ANALYSIS:")
    print(f"  Symbols in logs:     {len(log_symbols)}")
    print(f"  Missing from logs:   {len(missing_from_logs)}")
    
    if missing_from_logs:
        print(f"\n📋 SYMBOLS MISSING FROM LOGS:")
        for symbol in sorted(missing_from_logs):
            if symbol in available_symbols:
                print(f"  - {symbol} (✅ Available but not processed)")
            elif symbol in invisible_symbols:
                print(f"  - {symbol} (⚠️  Was invisible)")
            elif symbol in unavailable_symbols:
                print(f"  - {symbol} (❌ Not available)")
    
    # Cleanup
    mt5.shutdown()

def main():
    """Main function"""
    print("🔧 SYMBOL AVAILABILITY CHECKER")
    print("=" * 40)
    
    check_symbol_availability()
    
    print("\n📋 RECOMMENDATIONS:")
    print("1. Remove unavailable symbols from configuration")
    print("2. Enable invisible symbols in MT5 Market Watch")
    print("3. Check broker's available instruments")
    print("4. Verify symbol names are correct for your broker")

if __name__ == "__main__":
    main()