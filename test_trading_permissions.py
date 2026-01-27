"""
Test Trading Permissions (Dry Run)
Checks if the bot has permission to trade WITHOUT placing actual orders
Safe to run - no real trades will be placed
"""

import sys
import os
import MetaTrader5 as mt5

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def test_trading_permissions():
    """Test trading permissions without placing orders"""
    
    print("=" * 70)
    print("TRADING PERMISSIONS TEST (DRY RUN)")
    print("=" * 70)
    print()
    print("✅ Safe test - NO real trades will be placed")
    print("   This only checks if trading is allowed")
    print()
    print("-" * 70)
    print()
    
    # Initialize MT5
    print("Test 1: MT5 Connection...")
    if not mt5.initialize():
        error = mt5.last_error()
        print(f"❌ FAILED: {error}")
        return False
    print("✅ PASSED: MT5 connected")
    print()
    
    # Check account
    print("Test 2: Account Information...")
    account_info = mt5.account_info()
    if not account_info:
        print("❌ FAILED: Could not get account info")
        mt5.shutdown()
        return False
    
    print("✅ PASSED: Account accessible")
    print(f"   Login: {account_info.login}")
    print(f"   Server: {account_info.server}")
    print(f"   Balance: {account_info.balance} {account_info.currency}")
    print(f"   Equity: {account_info.equity} {account_info.currency}")
    print(f"   Margin Free: {account_info.margin_free} {account_info.currency}")
    print(f"   Leverage: 1:{account_info.leverage}")
    print()
    
    # Check trading permission
    print("Test 3: Trading Permission...")
    if not account_info.trade_allowed:
        print("❌ FAILED: Trading is NOT allowed")
        print()
        print("SOLUTION:")
        print("1. In MT5, go to Tools → Options")
        print("2. Click 'Expert Advisors' tab")
        print("3. Check these boxes:")
        print("   ✅ Allow algorithmic trading")
        print("   ✅ Allow DLL imports")
        print("4. Click OK")
        print("5. Look for green 'AutoTrading' button in top-right")
        print("6. Run this test again")
        mt5.shutdown()
        return False
    
    print("✅ PASSED: Trading is allowed")
    print()
    
    # Check trade mode
    print("Test 4: Account Trade Mode...")
    trade_mode = account_info.trade_mode
    if trade_mode == mt5.ACCOUNT_TRADE_MODE_DEMO:
        print("✅ PASSED: Demo account (safe for testing)")
    elif trade_mode == mt5.ACCOUNT_TRADE_MODE_REAL:
        print("⚠️  WARNING: REAL account (use caution!)")
    elif trade_mode == mt5.ACCOUNT_TRADE_MODE_CONTEST:
        print("✅ PASSED: Contest account")
    else:
        print("⚠️  UNKNOWN: Trade mode not recognized")
    print()
    
    # Check symbols
    print("Test 5: Symbol Availability...")
    symbols = ['XAUUSD', 'XAGUSD']
    all_symbols_ok = True
    
    for symbol in symbols:
        # Try to select symbol
        if not mt5.symbol_select(symbol, True):
            print(f"❌ FAILED: {symbol} - Could not select")
            all_symbols_ok = False
            continue
        
        # Get symbol info
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            print(f"❌ FAILED: {symbol} - Not available")
            all_symbols_ok = False
            continue
        
        # Check if trading is allowed for this symbol
        if not symbol_info.trade_mode == mt5.SYMBOL_TRADE_MODE_FULL:
            print(f"⚠️  WARNING: {symbol} - Trading restricted")
        
        print(f"✅ PASSED: {symbol}")
        print(f"   Bid: {symbol_info.bid}")
        print(f"   Ask: {symbol_info.ask}")
        print(f"   Spread: {symbol_info.spread} points")
        print(f"   Min Lot: {symbol_info.volume_min}")
        print(f"   Max Lot: {symbol_info.volume_max}")
        print(f"   Lot Step: {symbol_info.volume_step}")
        print(f"   Trade Mode: {'FULL' if symbol_info.trade_mode == mt5.SYMBOL_TRADE_MODE_FULL else 'RESTRICTED'}")
        print()
    
    if not all_symbols_ok:
        print("⚠️  Some symbols are not available")
        print("   Check symbol names with your broker")
        print()
    
    # Check margin requirements
    print("Test 6: Margin Calculation...")
    symbol = 'XAUUSD'
    lot = 0.01  # Minimum lot
    
    # Calculate required margin
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info:
        margin = mt5.order_calc_margin(
            mt5.ORDER_TYPE_BUY,
            symbol,
            lot,
            symbol_info.ask
        )
        
        if margin is None:
            print(f"⚠️  WARNING: Could not calculate margin")
        else:
            print(f"✅ PASSED: Margin calculation works")
            print(f"   Required margin for {lot} lot: {margin:.2f} {account_info.currency}")
            print(f"   Available margin: {account_info.margin_free:.2f} {account_info.currency}")
            
            if margin > account_info.margin_free:
                print(f"   ⚠️  WARNING: Not enough margin!")
            else:
                print(f"   ✅ Sufficient margin available")
    print()
    
    # Check market hours
    print("Test 7: Market Status...")
    for symbol in symbols:
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info:
            if symbol_info.trade_mode == mt5.SYMBOL_TRADE_MODE_FULL:
                print(f"✅ {symbol}: Market OPEN")
            elif symbol_info.trade_mode == mt5.SYMBOL_TRADE_MODE_CLOSEONLY:
                print(f"⚠️  {symbol}: Close only (market closing)")
            elif symbol_info.trade_mode == mt5.SYMBOL_TRADE_MODE_DISABLED:
                print(f"❌ {symbol}: Market CLOSED")
            else:
                print(f"⚠️  {symbol}: Status unknown")
    print()
    
    # Summary
    print("-" * 70)
    print()
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print()
    
    if account_info.trade_allowed and all_symbols_ok:
        print("🎉 ALL TESTS PASSED!")
        print()
        print("✅ Your bot CAN trade!")
        print()
        print("Next steps:")
        print("  1. Run actual trade test: python test_trading_capability.py")
        print("  2. Or start the bot: python run_bot.py")
        print()
        print("⚠️  Remember:")
        if trade_mode == mt5.ACCOUNT_TRADE_MODE_REAL:
            print("  - You're on a REAL account!")
            print("  - Start with VERY low risk (0.5%)")
            print("  - Consider testing on demo first")
        else:
            print("  - You're on a demo account (safe)")
            print("  - Test thoroughly before going live")
            print("  - Start with low risk (1%)")
    else:
        print("⚠️  SOME TESTS FAILED")
        print()
        print("Issues found:")
        if not account_info.trade_allowed:
            print("  ❌ Trading not allowed - Enable in MT5 settings")
        if not all_symbols_ok:
            print("  ❌ Some symbols unavailable - Check symbol names")
        print()
        print("Fix the issues above and run this test again")
    
    print("=" * 70)
    
    mt5.shutdown()
    return account_info.trade_allowed and all_symbols_ok


if __name__ == "__main__":
    try:
        success = test_trading_permissions()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        mt5.shutdown()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        mt5.shutdown()
        sys.exit(1)
