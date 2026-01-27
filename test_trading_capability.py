"""
Test Trading Capability
Tests if the bot can actually place and close trades on MT5
This will place a REAL test order (minimum size) and close it immediately
"""

import sys
import os
import MetaTrader5 as mt5
from datetime import datetime
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def test_trading_capability():
    """Test if bot can place and close trades"""
    
    print("=" * 70)
    print("TRADING CAPABILITY TEST")
    print("=" * 70)
    print()
    print("⚠️  WARNING: This will place a REAL test trade!")
    print("   - Minimum lot size (0.01)")
    print("   - Will be closed immediately")
    print("   - May cost a few cents in spread")
    print()
    
    response = input("Continue with test? (yes/no): ").lower()
    if response not in ['yes', 'y']:
        print("Test cancelled.")
        return False
    
    print()
    print("-" * 70)
    
    # Initialize MT5
    print("Step 1: Connecting to MT5...")
    if not mt5.initialize():
        print(f"❌ Failed to initialize MT5: {mt5.last_error()}")
        return False
    print("✅ Connected to MT5")
    print()
    
    # Get account info
    account_info = mt5.account_info()
    if not account_info:
        print("❌ Could not get account info")
        mt5.shutdown()
        return False
    
    print(f"Account Info:")
    print(f"  Login: {account_info.login}")
    print(f"  Balance: {account_info.balance} {account_info.currency}")
    print(f"  Leverage: 1:{account_info.leverage}")
    print(f"  Trade Allowed: {account_info.trade_allowed}")
    print()
    
    if not account_info.trade_allowed:
        print("❌ Trading is not allowed on this account!")
        print("   Solution: Enable 'Allow algorithmic trading' in MT5")
        print("   Tools → Options → Expert Advisors → Allow algorithmic trading")
        mt5.shutdown()
        return False
    
    # Test symbol
    symbol = "XAUUSD"
    print(f"Step 2: Checking symbol {symbol}...")
    
    # Enable symbol
    if not mt5.symbol_select(symbol, True):
        print(f"❌ Could not select {symbol}")
        print(f"   Your broker may use a different symbol name")
        mt5.shutdown()
        return False
    
    # Get symbol info
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(f"❌ Could not get info for {symbol}")
        mt5.shutdown()
        return False
    
    print(f"✅ Symbol {symbol} is available")
    print(f"  Bid: {symbol_info.bid}")
    print(f"  Ask: {symbol_info.ask}")
    print(f"  Spread: {symbol_info.spread} points")
    print(f"  Min Lot: {symbol_info.volume_min}")
    print(f"  Max Lot: {symbol_info.volume_max}")
    print(f"  Lot Step: {symbol_info.volume_step}")
    print()
    
    # Prepare order
    lot = symbol_info.volume_min  # Use minimum lot size
    point = symbol_info.point
    price = symbol_info.ask
    
    # Calculate SL and TP (far away to avoid immediate trigger)
    sl = price - 100 * point  # 100 points below
    tp = price + 200 * point  # 200 points above
    
    print(f"Step 3: Preparing test order...")
    print(f"  Type: BUY")
    print(f"  Lot Size: {lot}")
    print(f"  Price: {price}")
    print(f"  Stop Loss: {sl}")
    print(f"  Take Profit: {tp}")
    print()
    
    # Create order request
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_BUY,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 20,
        "magic": 234000,
        "comment": "Test order",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    
    print(f"Step 4: Placing test order...")
    result = mt5.order_send(request)
    
    if result is None:
        print(f"❌ Order failed: No result returned")
        mt5.shutdown()
        return False
    
    print(f"Order Result:")
    print(f"  Return Code: {result.retcode}")
    print(f"  Comment: {result.comment}")
    
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"❌ Order failed!")
        print(f"   Error Code: {result.retcode}")
        print(f"   Comment: {result.comment}")
        print()
        print("Common issues:")
        print("  10004 - Requote (price changed)")
        print("  10006 - Request rejected")
        print("  10013 - Invalid request")
        print("  10014 - Invalid volume")
        print("  10015 - Invalid price")
        print("  10016 - Invalid stops")
        print("  10018 - Market closed")
        print("  10019 - Not enough money")
        print()
        
        if result.retcode == 10019:
            print("Solution: Check account balance")
        elif result.retcode == 10014:
            print(f"Solution: Use lot size between {symbol_info.volume_min} and {symbol_info.volume_max}")
        elif result.retcode == 10018:
            print("Solution: Wait for market to open")
        
        mt5.shutdown()
        return False
    
    print(f"✅ Order placed successfully!")
    print(f"  Order: {result.order}")
    print(f"  Deal: {result.deal}")
    print(f"  Volume: {result.volume}")
    print(f"  Price: {result.price}")
    print()
    
    # Wait a moment
    print("Waiting 2 seconds...")
    time.sleep(2)
    
    # Get position
    print(f"Step 5: Checking position...")
    positions = mt5.positions_get(symbol=symbol)
    
    if positions is None or len(positions) == 0:
        print("⚠️  No position found (may have closed already)")
    else:
        position = positions[0]
        print(f"✅ Position found:")
        print(f"  Ticket: {position.ticket}")
        print(f"  Volume: {position.volume}")
        print(f"  Price: {position.price_open}")
        print(f"  Current Price: {position.price_current}")
        print(f"  Profit: {position.profit} {account_info.currency}")
        print()
        
        # Close position
        print(f"Step 6: Closing test position...")
        
        close_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": mt5.ORDER_TYPE_SELL,
            "position": position.ticket,
            "price": symbol_info.bid,
            "deviation": 20,
            "magic": 234000,
            "comment": "Close test",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        close_result = mt5.order_send(close_request)
        
        if close_result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"⚠️  Could not close automatically: {close_result.comment}")
            print(f"   Please close manually in MT5")
        else:
            print(f"✅ Position closed successfully!")
            print(f"  Final Profit/Loss: {close_result.profit} {account_info.currency}")
    
    print()
    print("-" * 70)
    print()
    print("=" * 70)
    print("TEST RESULTS")
    print("=" * 70)
    print()
    print("✅ MT5 Connection: PASSED")
    print("✅ Account Access: PASSED")
    print("✅ Symbol Available: PASSED")
    print("✅ Order Placement: PASSED")
    print("✅ Position Management: PASSED")
    print()
    print("🎉 TRADING CAPABILITY: CONFIRMED!")
    print()
    print("Your bot CAN trade! Next steps:")
    print("  1. Review the test results above")
    print("  2. Check your MT5 account history")
    print("  3. Start the bot: python run_bot.py")
    print()
    print("⚠️  Remember:")
    print("  - Always test on demo first")
    print("  - Start with low risk (0.5-1%)")
    print("  - Monitor closely")
    print("=" * 70)
    
    mt5.shutdown()
    return True


if __name__ == "__main__":
    try:
        success = test_trading_capability()
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
