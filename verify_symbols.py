"""
Verify Current Symbols Configuration
Checks if XAUUSD and GBPUSD are available
"""

import sys
sys.path.insert(0, 'src')
from config import get_config
import MetaTrader5 as mt5


def verify_symbols():
    """Verify configured symbols are available"""
    
    print("=" * 70)
    print("SYMBOL VERIFICATION")
    print("=" * 70)
    print()
    
    # Initialize MT5
    if not mt5.initialize():
        print(f"❌ Failed to initialize MT5: {mt5.last_error()}")
        return False
    
    # Get config
    config = get_config()
    symbols = config['symbols']
    
    print(f"Configured Symbols: {symbols}")
    print()
    
    all_ok = True
    
    for symbol in symbols:
        print(f"Checking {symbol}:")
        print("-" * 70)
        
        # Check if symbol exists
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            print(f"❌ {symbol} NOT FOUND")
            print(f"   Your broker may use a different name")
            all_ok = False
            continue
        
        # Enable symbol if not visible
        if not symbol_info.visible:
            if mt5.symbol_select(symbol, True):
                print(f"✅ {symbol} enabled in Market Watch")
            else:
                print(f"⚠️  Could not enable {symbol}")
        
        # Get symbol info
        print(f"✅ {symbol} is available")
        print(f"   Bid: {symbol_info.bid}")
        print(f"   Ask: {symbol_info.ask}")
        print(f"   Spread: {symbol_info.spread} points")
        print(f"   Min Lot: {symbol_info.volume_min}")
        print(f"   Max Lot: {symbol_info.volume_max}")
        print(f"   Lot Step: {symbol_info.volume_step}")
        
        # Test M1 data
        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 100)
        if rates is None or len(rates) == 0:
            print(f"   ⚠️  M1 data not available")
            all_ok = False
        else:
            print(f"   ✅ M1 data available ({len(rates)} bars)")
        
        print()
    
    print("=" * 70)
    
    if all_ok:
        print("✅ ALL SYMBOLS VERIFIED!")
        print()
        print("Your bot is configured to trade:")
        for symbol in symbols:
            print(f"  • {symbol}")
        print()
        print("Ready to run: python run_bot.py")
    else:
        print("⚠️  SOME SYMBOLS HAVE ISSUES")
        print()
        print("Please fix the issues above before running the bot.")
    
    print("=" * 70)
    
    mt5.shutdown()
    return all_ok


if __name__ == "__main__":
    try:
        success = verify_symbols()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        mt5.shutdown()
        sys.exit(1)
