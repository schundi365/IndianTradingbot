"""
Symbol Availability Checker for MT5 Trading Bot
Verifies which symbols are available with your broker
"""

import MetaTrader5 as mt5
from datetime import datetime

# Import symbol lists from config
import sys
sys.path.append('src')
from config import FOREX_MAJORS, FOREX_CROSSES, COMMODITIES_METALS, COMMODITIES_ENERGY, INDICES

def check_symbol_availability():
    """Check which symbols are available with your broker"""
    
    print("=" * 80)
    print("MT5 SYMBOL AVAILABILITY CHECKER")
    print("=" * 80)
    print()
    
    # Initialize MT5
    if not mt5.initialize():
        print("❌ Failed to initialize MT5")
        print(f"Error: {mt5.last_error()}")
        return
    
    print("✅ MT5 Connected")
    
    # Get account info
    account_info = mt5.account_info()
    if account_info:
        print(f"📊 Account: {account_info.login}")
        print(f"💰 Balance: ${account_info.balance:.2f}")
        print(f"🏢 Broker: {account_info.company}")
    print()
    
    # Check all symbol categories
    categories = {
        'Forex Majors': FOREX_MAJORS,
        'Forex Crosses': FOREX_CROSSES,
        'Commodities (Metals)': COMMODITIES_METALS,
        'Commodities (Energy)': COMMODITIES_ENERGY,
        'Indices': INDICES
    }
    
    all_available = []
    all_unavailable = []
    
    for category_name, symbols in categories.items():
        print(f"{'=' * 80}")
        print(f"{category_name.upper()}")
        print(f"{'=' * 80}")
        
        available = []
        unavailable = []
        
        for symbol in symbols:
            info = mt5.symbol_info(symbol)
            
            if info is None:
                print(f"❌ {symbol:12} - NOT AVAILABLE")
                unavailable.append(symbol)
                all_unavailable.append(symbol)
            else:
                # Check if symbol is visible
                if not info.visible:
                    # Try to make it visible
                    if mt5.symbol_select(symbol, True):
                        info = mt5.symbol_info(symbol)
                
                spread = info.spread
                spread_pips = spread * info.point
                
                # Get current price
                tick = mt5.symbol_info_tick(symbol)
                if tick:
                    bid = tick.bid
                    ask = tick.ask
                    print(f"✅ {symbol:12} - Spread: {spread:4} ({spread_pips:.5f}) | Bid: {bid:.5f} | Ask: {ask:.5f}")
                else:
                    print(f"✅ {symbol:12} - Spread: {spread:4} ({spread_pips:.5f}) | (No tick data)")
                
                available.append(symbol)
                all_available.append(symbol)
        
        print()
        print(f"Available: {len(available)}/{len(symbols)}")
        if unavailable:
            print(f"Unavailable: {', '.join(unavailable)}")
        print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"✅ Total Available: {len(all_available)}")
    print(f"❌ Total Unavailable: {len(all_unavailable)}")
    print()
    
    if all_available:
        print("Available Symbols:")
        print("-" * 80)
        # Group by category for easy copying
        for i in range(0, len(all_available), 5):
            symbols_line = ', '.join(f"'{s}'" for s in all_available[i:i+5])
            print(f"    {symbols_line},")
        print()
    
    if all_unavailable:
        print("Unavailable Symbols:")
        print("-" * 80)
        for symbol in all_unavailable:
            print(f"  - {symbol}")
        print()
        print("💡 Tip: Some symbols may need to be enabled in MT5 Market Watch")
        print("   Right-click Market Watch → Symbols → Find symbol → Show")
        print()
    
    # Recommended configuration
    print("=" * 80)
    print("RECOMMENDED CONFIGURATION")
    print("=" * 80)
    print()
    
    if len(all_available) >= 2:
        print("Copy this to src/config.py:")
        print("-" * 80)
        print("SYMBOLS = [")
        for symbol in all_available[:10]:  # Show first 10
            print(f"    '{symbol}',")
        if len(all_available) > 10:
            print(f"    # ... and {len(all_available) - 10} more available")
        print("]")
        print()
    else:
        print("⚠️  Warning: Very few symbols available")
        print("   Check your broker's symbol list")
        print()
    
    # Shutdown
    mt5.shutdown()
    print("=" * 80)
    print("✅ Check Complete!")
    print("=" * 80)


if __name__ == "__main__":
    try:
        check_symbol_availability()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        mt5.shutdown()
    except Exception as e:
        print(f"\n\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        mt5.shutdown()
