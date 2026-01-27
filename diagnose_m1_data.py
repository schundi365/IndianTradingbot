"""
Diagnose M1 Data Issues
Checks if M1 data is available and identifies problems
"""

import MetaTrader5 as mt5
import sys
from datetime import datetime


def diagnose_m1_data():
    """Diagnose M1 data availability"""
    
    print("=" * 70)
    print("M1 DATA DIAGNOSTICS")
    print("=" * 70)
    print()
    
    # Initialize MT5
    print("Step 1: Connecting to MT5...")
    if not mt5.initialize():
        print(f"❌ Failed to initialize MT5: {mt5.last_error()}")
        return False
    print("✅ Connected to MT5")
    print()
    
    # Check symbols
    symbols = ['XAUUSD', 'XAGUSD']
    
    for symbol in symbols:
        print(f"Checking {symbol}:")
        print("-" * 70)
        
        # Check if symbol exists
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            print(f"❌ Symbol {symbol} not found")
            print(f"   Your broker may use a different name")
            continue
        
        print(f"✅ Symbol found")
        print(f"   Bid: {symbol_info.bid}")
        print(f"   Ask: {symbol_info.ask}")
        print(f"   Visible: {symbol_info.visible}")
        print()
        
        # Try different timeframes
        timeframes = [
            (mt5.TIMEFRAME_M1, "M1 (1 minute)"),
            (mt5.TIMEFRAME_M5, "M5 (5 minutes)"),
            (mt5.TIMEFRAME_M15, "M15 (15 minutes)"),
            (mt5.TIMEFRAME_H1, "H1 (1 hour)"),
        ]
        
        print(f"Testing data availability for {symbol}:")
        
        for tf, name in timeframes:
            # Try to get data
            rates = mt5.copy_rates_from_pos(symbol, tf, 0, 100)
            
            if rates is None or len(rates) == 0:
                error = mt5.last_error()
                print(f"   ❌ {name:20} - No data (Error: {error})")
            else:
                print(f"   ✅ {name:20} - {len(rates)} bars available")
                
                # Show latest bar info for M1
                if tf == mt5.TIMEFRAME_M1:
                    latest = rates[-1]
                    time_str = datetime.fromtimestamp(latest['time']).strftime('%Y-%m-%d %H:%M:%S')
                    print(f"      Latest M1 bar: {time_str}")
                    print(f"      Close: {latest['close']}")
        
        print()
    
    print("=" * 70)
    print("DIAGNOSIS COMPLETE")
    print("=" * 70)
    print()
    
    # Recommendations
    print("Recommendations:")
    print()
    
    # Check if M1 data is available
    rates_m1 = mt5.copy_rates_from_pos('XAUUSD', mt5.TIMEFRAME_M1, 0, 100)
    
    if rates_m1 is None or len(rates_m1) == 0:
        print("⚠️  M1 DATA NOT AVAILABLE")
        print()
        print("Possible reasons:")
        print("1. Broker doesn't provide M1 data")
        print("2. Market is closed")
        print("3. Symbol not enabled in Market Watch")
        print("4. MT5 needs to download M1 history")
        print()
        print("Solutions:")
        print("1. In MT5, open a M1 chart for XAUUSD")
        print("2. Wait for history to download (may take a few minutes)")
        print("3. Check if market is open")
        print("4. Try M5 or M15 timeframe instead")
        print()
        print("To change to M5:")
        print("   Edit src/config.py")
        print("   Change: TIMEFRAME = mt5.TIMEFRAME_M5")
    else:
        print("✅ M1 DATA IS AVAILABLE")
        print()
        print(f"Retrieved {len(rates_m1)} M1 bars for XAUUSD")
        print("Bot should work correctly")
        print()
        print("If bot still fails:")
        print("1. Check trading_bot.log for details")
        print("2. Verify MT5 is still connected")
        print("3. Try restarting MT5")
        print("4. Run: python test_bot_live.py")
    
    print("=" * 70)
    
    mt5.shutdown()
    return True


if __name__ == "__main__":
    try:
        diagnose_m1_data()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        mt5.shutdown()
