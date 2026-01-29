"""
Enable Debug Logging for GEM Trading Bot
Run this to get detailed debug information for troubleshooting
"""

import logging
import sys
import os

def setup_debug_logging():
    """Setup comprehensive debug logging"""
    
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Configure root logger
    logging.basicConfig(
        level=logging.DEBUG,  # Changed from INFO to DEBUG
        format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        handlers=[
            logging.FileHandler('logs/debug.log', encoding='utf-8'),
            logging.FileHandler('trading_bot.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific loggers to DEBUG
    loggers = [
        'src.mt5_trading_bot',
        'src.config_manager',
        'src.volume_analyzer',
        'web_dashboard',
        '__main__'
    ]
    
    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
    
    print("=" * 80)
    print("DEBUG LOGGING ENABLED")
    print("=" * 80)
    print()
    print("Log files:")
    print("  - logs/debug.log (detailed debug info)")
    print("  - trading_bot.log (standard log)")
    print()
    print("What will be logged:")
    print("  ✓ MT5 connection attempts and errors")
    print("  ✓ Configuration loading and validation")
    print("  ✓ Every signal check and filter result")
    print("  ✓ Volume analysis details")
    print("  ✓ Trade decision reasoning")
    print("  ✓ All API calls and responses")
    print()
    print("=" * 80)
    print()

if __name__ == "__main__":
    setup_debug_logging()
    
    # Test MT5 connection with debug info
    print("Testing MT5 connection with debug logging...")
    print()
    
    try:
        import MetaTrader5 as mt5
        
        print("Step 1: Attempting MT5 initialization...")
        if not mt5.initialize():
            error = mt5.last_error()
            print(f"❌ MT5 initialization failed!")
            print(f"   Error code: {error[0] if error else 'Unknown'}")
            print(f"   Error message: {error[1] if error and len(error) > 1 else 'Unknown'}")
            print()
            print("Troubleshooting:")
            print("  1. Is MT5 running?")
            print("  2. Are you logged into an account?")
            print("  3. Is algo trading enabled? (Tools > Options > Expert Advisors)")
            print()
            sys.exit(1)
        
        print("✓ MT5 initialized successfully")
        print()
        
        # Get version info
        version = mt5.version()
        print(f"Step 2: MT5 Version Information")
        print(f"   Version: {version}")
        print()
        
        # Get terminal info
        terminal_info = mt5.terminal_info()
        if terminal_info:
            print(f"Step 3: Terminal Information")
            print(f"   Build: {terminal_info.build}")
            print(f"   Company: {terminal_info.company}")
            print(f"   Name: {terminal_info.name}")
            print(f"   Path: {terminal_info.path}")
            print(f"   Data path: {terminal_info.data_path}")
            print(f"   Connected: {terminal_info.connected}")
            print(f"   Trade allowed: {terminal_info.trade_allowed}")
            print()
        
        # Get account info
        account_info = mt5.account_info()
        if account_info:
            print(f"Step 4: Account Information")
            print(f"   Login: {account_info.login}")
            print(f"   Server: {account_info.server}")
            print(f"   Name: {account_info.name}")
            print(f"   Balance: {account_info.balance}")
            print(f"   Equity: {account_info.equity}")
            print(f"   Margin free: {account_info.margin_free}")
            print(f"   Leverage: {account_info.leverage}")
            print(f"   Trade allowed: {account_info.trade_allowed}")
            print(f"   Trade expert: {account_info.trade_expert}")
            print()
        else:
            print("❌ Cannot get account info!")
            print("   Make sure you're logged into MT5")
            print()
        
        # Test symbol access
        print(f"Step 5: Testing Symbol Access")
        test_symbols = ['XAUUSD', 'EURUSD', 'GBPUSD']
        for symbol in test_symbols:
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info:
                print(f"   ✓ {symbol}: Available (spread: {symbol_info.spread})")
            else:
                print(f"   ✗ {symbol}: Not available")
        print()
        
        # Test data retrieval
        print(f"Step 6: Testing Data Retrieval")
        rates = mt5.copy_rates_from_pos('XAUUSD', mt5.TIMEFRAME_M30, 0, 10)
        if rates is not None and len(rates) > 0:
            print(f"   ✓ Successfully retrieved {len(rates)} bars of XAUUSD M30 data")
            print(f"   Latest close: {rates[-1]['close']}")
        else:
            error = mt5.last_error()
            print(f"   ✗ Failed to retrieve data")
            print(f"   Error: {error}")
        print()
        
        mt5.shutdown()
        
        print("=" * 80)
        print("✅ MT5 CONNECTION TEST COMPLETE")
        print("=" * 80)
        print()
        print("MT5 is working correctly!")
        print()
        print("Next steps:")
        print("  1. Start the bot: python web_dashboard.py")
        print("  2. Check logs/debug.log for detailed information")
        print("  3. Look for 'DEBUG' level messages")
        print()
        
    except ImportError:
        print("❌ MetaTrader5 module not found!")
        print("   Install it: pip install MetaTrader5")
        print()
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        print()

