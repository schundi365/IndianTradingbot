"""
MT5 Connection Test Script
Run this to verify your MT5 setup before starting the bot
"""

import MetaTrader5 as mt5
import sys


def test_mt5_connection():
    """Test MT5 connection and configuration"""
    
    print("=" * 60)
    print("MT5 CONNECTION TEST")
    print("=" * 60)
    print()
    
    # Test 1: Initialize MT5
    print("Test 1: Initializing MT5...")
    if not mt5.initialize():
        print("❌ FAILED: Could not initialize MT5")
        print("   Make sure MT5 is installed and running")
        return False
    print("✅ PASSED: MT5 initialized successfully")
    print()
    
    # Test 2: Check MT5 version
    print("Test 2: Checking MT5 version...")
    version = mt5.version()
    if version:
        print(f"✅ PASSED: MT5 version {version[0]}.{version[1]}.{version[2]}")
    else:
        print("❌ FAILED: Could not get MT5 version")
    print()
    
    # Test 3: Check account info
    print("Test 3: Checking account information...")
    account_info = mt5.account_info()
    if account_info is None:
        print("❌ FAILED: Could not get account info")
        print("   Make sure you're logged into an MT5 account")
        mt5.shutdown()
        return False
    
    print("✅ PASSED: Account connected")
    print(f"   Account: {account_info.login}")
    print(f"   Server: {account_info.server}")
    print(f"   Balance: {account_info.balance} {account_info.currency}")
    print(f"   Equity: {account_info.equity} {account_info.currency}")
    print(f"   Free Margin: {account_info.margin_free} {account_info.currency}")
    print(f"   Leverage: 1:{account_info.leverage}")
    print()
    
    # Test 4: Check trading permissions
    print("Test 4: Checking trading permissions...")
    if account_info.trade_allowed:
        print("✅ PASSED: Trading is allowed")
    else:
        print("❌ FAILED: Trading is not allowed")
        print("   Enable 'Allow algorithmic trading' in MT5 settings")
    print()
    
    # Test 5: Check symbols
    print("Test 5: Checking symbol availability...")
    symbols = ['XAUUSD', 'XAGUSD']
    all_symbols_ok = True
    
    for symbol in symbols:
        info = mt5.symbol_info(symbol)
        if info is None:
            print(f"❌ FAILED: {symbol} not found")
            print(f"   Your broker may use a different symbol name")
            all_symbols_ok = False
        elif not info.visible:
            print(f"⚠️  WARNING: {symbol} found but not visible in Market Watch")
            print(f"   Attempting to enable...")
            if mt5.symbol_select(symbol, True):
                print(f"✅ PASSED: {symbol} enabled successfully")
            else:
                print(f"❌ FAILED: Could not enable {symbol}")
                all_symbols_ok = False
        else:
            print(f"✅ PASSED: {symbol} is available")
            print(f"   Bid: {info.bid}, Ask: {info.ask}, Spread: {info.spread}")
    print()
    
    # Test 6: Check minimum lot size
    print("Test 6: Checking lot size requirements...")
    for symbol in symbols:
        info = mt5.symbol_info(symbol)
        if info:
            print(f"{symbol}:")
            print(f"   Min lot: {info.volume_min}")
            print(f"   Max lot: {info.volume_max}")
            print(f"   Lot step: {info.volume_step}")
    print()
    
    # Test 7: Test data retrieval
    print("Test 7: Testing historical data retrieval...")
    rates = mt5.copy_rates_from_pos('XAUUSD', mt5.TIMEFRAME_H1, 0, 100)
    if rates is None or len(rates) == 0:
        print("❌ FAILED: Could not retrieve historical data")
        all_symbols_ok = False
    else:
        print(f"✅ PASSED: Retrieved {len(rates)} bars of historical data")
    print()
    
    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    if all_symbols_ok and account_info.trade_allowed:
        print("✅ ALL TESTS PASSED - Ready to run the bot!")
        print()
        print("Next steps:")
        print("1. Review config.py settings")
        print("2. Start with demo account")
        print("3. Run: python run_bot.py")
    else:
        print("⚠️  SOME TESTS FAILED - Please fix issues before running bot")
        print()
        print("Common fixes:")
        print("- Enable 'Allow algorithmic trading' in MT5 Tools → Options")
        print("- Check symbol names with your broker")
        print("- Ensure MT5 is logged in and connected to server")
    
    print("=" * 60)
    
    # Cleanup
    mt5.shutdown()
    return all_symbols_ok and account_info.trade_allowed


if __name__ == "__main__":
    try:
        success = test_mt5_connection()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print("\nPlease ensure:")
        print("1. MT5 is installed and running")
        print("2. You have MetaTrader5 Python package installed")
        print("3. You're logged into an MT5 account")
        sys.exit(1)
