"""
Check What Code is Actually Loaded

This script checks if the bot has the updated analysis_bars code loaded.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src')

def check_bot_code():
    """Check if bot has analysis_bars attribute"""
    print("=" * 80)
    print("CHECKING LOADED BOT CODE")
    print("=" * 80)
    print()
    
    try:
        from src.mt5_trading_bot import MT5TradingBot
        from src import config
        
        # Create a test bot instance
        test_config = config.get_config()
        test_config['analysis_bars'] = 123  # Unique test value
        
        print("Creating test bot instance...")
        bot = MT5TradingBot(test_config)
        
        # Check if bot has analysis_bars
        if hasattr(bot, 'analysis_bars'):
            print(f"✅ Bot HAS analysis_bars attribute")
            print(f"   Value: {bot.analysis_bars}")
            
            if bot.analysis_bars == 123:
                print(f"✅ Bot is using UPDATED code (reads from config)")
            else:
                print(f"❌ Bot has wrong value: {bot.analysis_bars}")
                print(f"   Expected: 123")
        else:
            print(f"❌ Bot DOES NOT have analysis_bars attribute")
            print(f"   This means OLD code is loaded!")
        
        print()
        
        # Check the run_strategy method source
        import inspect
        source = inspect.getsource(bot.run_strategy)
        
        if 'Requesting' in source and 'self.analysis_bars' in source:
            print("✅ run_strategy method has UPDATED logging")
            print("   Contains: 'Requesting {self.analysis_bars} bars'")
        else:
            print("❌ run_strategy method has OLD logging")
            print("   Missing: 'Requesting {self.analysis_bars} bars'")
        
        print()
        print("=" * 80)
        print("CONCLUSION")
        print("=" * 80)
        print()
        
        if hasattr(bot, 'analysis_bars') and 'self.analysis_bars' in source:
            print("✅ UPDATED CODE IS LOADED")
            print()
            print("If logs still show old format, the dashboard needs to be")
            print("completely restarted (not just stop/start bot).")
            print()
            print("SOLUTION:")
            print("  1. Close the dashboard terminal/window")
            print("  2. Wait 5 seconds")
            print("  3. Run: python web_dashboard.py")
            print("  4. Open browser and start bot")
        else:
            print("❌ OLD CODE IS STILL LOADED")
            print()
            print("The Python module cache has old code.")
            print()
            print("SOLUTION:")
            print("  1. Close ALL Python processes")
            print("  2. Close the dashboard")
            print("  3. Wait 10 seconds")
            print("  4. Run: python web_dashboard.py")
        
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_bot_code()
