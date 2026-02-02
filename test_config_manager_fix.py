#!/usr/bin/env python3
"""
Test the ConfigManager fix to ensure it loads all 18 symbols correctly
"""

import sys
import json
sys.path.append('src')

from config_manager import ConfigManager

def test_config_manager():
    """Test the ConfigManager to see what symbols it loads"""
    print("🔍 TESTING CONFIG MANAGER")
    print("=" * 40)
    
    # Test direct JSON loading
    print("1. Direct JSON file loading:")
    try:
        with open('bot_config.json', 'r') as f:
            json_config = json.load(f)
        
        json_symbols = json_config.get('symbols', [])
        print(f"   ✅ JSON file has {len(json_symbols)} symbols")
        print(f"   📋 First 5: {', '.join(json_symbols[:5])}")
        print(f"   📋 Last 5:  {', '.join(json_symbols[-5:])}")
        
    except Exception as e:
        print(f"   ❌ Error loading JSON: {str(e)}")
        return
    
    # Test ConfigManager loading
    print("\n2. ConfigManager loading:")
    try:
        config_manager = ConfigManager()
        config = config_manager.get_config()
        
        cm_symbols = config.get('symbols', [])
        print(f"   ✅ ConfigManager has {len(cm_symbols)} symbols")
        print(f"   📋 First 5: {', '.join(cm_symbols[:5])}")
        print(f"   📋 Last 5:  {', '.join(cm_symbols[-5:])}")
        
        # Compare
        if len(json_symbols) == len(cm_symbols):
            print(f"   ✅ Symbol count matches!")
        else:
            print(f"   ❌ Symbol count mismatch: JSON={len(json_symbols)}, CM={len(cm_symbols)}")
        
        # Check if all JSON symbols are in CM config
        missing_symbols = set(json_symbols) - set(cm_symbols)
        extra_symbols = set(cm_symbols) - set(json_symbols)
        
        if missing_symbols:
            print(f"   ❌ Missing from CM: {', '.join(missing_symbols)}")
        
        if extra_symbols:
            print(f"   ⚠️  Extra in CM: {', '.join(extra_symbols)}")
        
        if not missing_symbols and not extra_symbols:
            print(f"   ✅ All symbols match perfectly!")
            
    except Exception as e:
        print(f"   ❌ Error with ConfigManager: {str(e)}")
        import traceback
        traceback.print_exc()

def test_bot_initialization():
    """Test bot initialization with ConfigManager"""
    print("\n3. Bot initialization test:")
    try:
        # Import without initializing MT5
        import mt5_trading_bot
        
        # Mock MT5 connection
        original_connect = mt5_trading_bot.MT5TradingBot.connect
        mt5_trading_bot.MT5TradingBot.connect = lambda self: True
        
        # Create config manager and bot
        config_manager = ConfigManager()
        config = config_manager.get_config()
        
        print(f"   📊 Config for bot: {len(config.get('symbols', []))} symbols")
        
        # Create bot instance
        bot = mt5_trading_bot.MT5TradingBot(config)
        
        print(f"   📊 Bot initialized with: {len(bot.symbols)} symbols")
        print(f"   📋 Bot symbols: {', '.join(bot.symbols[:5])}{'...' if len(bot.symbols) > 5 else ''}")
        
        # Restore original method
        mt5_trading_bot.MT5TradingBot.connect = original_connect
        
        if len(bot.symbols) == 18:
            print(f"   ✅ Bot has all 18 symbols!")
            return True
        else:
            print(f"   ❌ Bot only has {len(bot.symbols)} symbols")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing bot: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    test_config_manager()
    success = test_bot_initialization()
    
    if success:
        print(f"\n✅ CONFIG MANAGER FIX SUCCESSFUL!")
        print(f"   The bot should now process all 18 symbols")
    else:
        print(f"\n❌ CONFIG MANAGER FIX FAILED!")
        print(f"   Further investigation needed")

if __name__ == "__main__":
    main()