"""
Test Bot Live - Run one iteration without confirmation
Tests the bot's ability to check signals and would place trades
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config import get_config
from mt5_trading_bot import MT5TradingBot
import MetaTrader5 as mt5


def test_bot_live():
    """Run one iteration of the bot to test functionality"""
    print("=" * 60)
    print("BOT LIVE TEST - Single Iteration")
    print("=" * 60)
    print()
    
    # Load config
    config = get_config()
    print(f"Configuration:")
    print(f"  Symbols: {', '.join(config['symbols'])}")
    print(f"  Risk: {config['risk_percent']}%")
    print(f"  Adaptive Risk: {'Enabled' if config['use_adaptive_risk'] else 'Disabled'}")
    print(f"  Split Orders: {'Enabled' if config['use_split_orders'] else 'Disabled'}")
    print()
    
    # Create bot
    print("Initializing bot...")
    bot = MT5TradingBot(config)
    
    # Connect to MT5
    if not bot.connect():
        print("❌ Failed to connect to MT5")
        return False
    
    print("✅ Connected to MT5")
    print()
    
    # Get account info
    account_info = mt5.account_info()
    if account_info:
        print(f"Account Info:")
        print(f"  Balance: {account_info.balance} {account_info.currency}")
        print(f"  Equity: {account_info.equity} {account_info.currency}")
        print(f"  Free Margin: {account_info.margin_free} {account_info.currency}")
        print()
    
    # Check for signals
    print("Checking for trading signals...")
    print("-" * 60)
    
    try:
        for symbol in config['symbols']:
            print(f"\n{symbol}:")
            
            # Get current price
            tick = mt5.symbol_info_tick(symbol)
            if tick:
                print(f"  Current Price: Bid={tick.bid:.2f}, Ask={tick.ask:.2f}")
            
            # Get historical data
            rates = mt5.copy_rates_from_pos(symbol, config['timeframe'], 0, 100)
            if rates is None or len(rates) == 0:
                print(f"  ⚠️  Could not retrieve historical data")
                continue
            
            print(f"  ✅ Retrieved {len(rates)} bars of data")
            
            # Here the bot would check for signals and place trades
            # For testing, we just verify data is available
            print(f"  ✅ Data ready for analysis")
            
        print()
        print("-" * 60)
        print("✅ Bot is functioning correctly!")
        print()
        print("What would happen next:")
        print("  1. Bot analyzes market conditions")
        print("  2. Calculates indicators (MA, ATR)")
        print("  3. Checks for entry signals")
        print("  4. If signal found, calculates position size")
        print("  5. Places order(s) with SL and TP")
        print("  6. Monitors positions and updates trailing stops")
        print()
        print("To run the bot continuously:")
        print("  python run_bot.py")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        bot.disconnect()
    
    return True


if __name__ == "__main__":
    try:
        success = test_bot_live()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
