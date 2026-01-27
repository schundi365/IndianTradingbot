"""
Quick Test Script
Run a single iteration of the bot to test functionality
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import get_config
from mt5_trading_bot import MT5TradingBot
import MetaTrader5 as mt5


def quick_test():
    """Run one iteration of the bot"""
    print("=" * 60)
    print("QUICK TEST - Single Iteration")
    print("=" * 60)
    print()
    
    # Initialize MT5
    if not mt5.initialize():
        print("❌ Failed to initialize MT5")
        return
    
    print("✅ MT5 connected")
    print()
    
    # Load config
    config = get_config()
    print(f"Testing with: {config['symbols']}")
    print(f"Timeframe: {config['timeframe']}")
    print()
    
    # Create bot
    bot = MT5TradingBot(config)
    
    # Run one check
    print("Checking for signals...")
    for symbol in config['symbols']:
        signal = bot.check_entry_signal_for_symbol(symbol)
        if signal == 1:
            print(f"📈 BUY signal detected for {symbol}")
        elif signal == -1:
            print(f"📉 SELL signal detected for {symbol}")
        else:
            print(f"⏸️  No signal for {symbol}")
    
    print()
    print("Test complete!")
    
    mt5.shutdown()


if __name__ == "__main__":
    try:
        quick_test()
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
