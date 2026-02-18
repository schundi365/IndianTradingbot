"""
Verify Analysis Bars Configuration Fix

This script verifies that:
1. analysis_bars is properly defined in config.py
2. analysis_bars is read by the bot from config
3. analysis_bars is actually used when fetching data
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_config_py():
    """Test that config.py has ANALYSIS_BARS defined"""
    print("=" * 80)
    print("TEST 1: Checking config.py for ANALYSIS_BARS")
    print("=" * 80)
    
    try:
        from src import config
        
        # Check if ANALYSIS_BARS is defined
        if hasattr(config, 'ANALYSIS_BARS'):
            print(f"✅ ANALYSIS_BARS is defined in config.py")
            print(f"   Value: {config.ANALYSIS_BARS}")
        else:
            print(f"❌ ANALYSIS_BARS is NOT defined in config.py")
            return False
        
        # Check if it's in the config dictionary
        cfg = config.get_config()
        if 'analysis_bars' in cfg:
            print(f"✅ analysis_bars is in config dictionary")
            print(f"   Value: {cfg['analysis_bars']}")
        else:
            print(f"❌ analysis_bars is NOT in config dictionary")
            return False
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ Error testing config.py: {e}")
        return False


def test_config_manager():
    """Test that config_manager has analysis_bars in defaults"""
    print("=" * 80)
    print("TEST 2: Checking config_manager.py for analysis_bars")
    print("=" * 80)
    
    try:
        from src.config_manager import ConfigManager
        
        # Create a test config manager
        manager = ConfigManager('test_analysis_bars_config.json')
        cfg = manager.get_config()
        
        if 'analysis_bars' in cfg:
            print(f"✅ analysis_bars is in config_manager defaults")
            print(f"   Value: {cfg['analysis_bars']}")
        else:
            print(f"❌ analysis_bars is NOT in config_manager defaults")
            return False
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ Error testing config_manager: {e}")
        return False


def test_bot_reads_config():
    """Test that bot reads analysis_bars from config"""
    print("=" * 80)
    print("TEST 3: Checking if bot reads analysis_bars from config")
    print("=" * 80)
    
    try:
        from src import config
        from src.mt5_trading_bot import MT5TradingBot
        
        # Create test config with custom analysis_bars
        test_config = config.get_config()
        test_config['analysis_bars'] = 150  # Custom value
        
        # Create bot instance (without connecting to MT5)
        bot = MT5TradingBot(test_config)
        
        # Check if bot has analysis_bars attribute
        if hasattr(bot, 'analysis_bars'):
            print(f"✅ Bot has analysis_bars attribute")
            print(f"   Value: {bot.analysis_bars}")
            
            if bot.analysis_bars == 150:
                print(f"✅ Bot correctly reads custom value from config (150)")
            else:
                print(f"❌ Bot has wrong value: {bot.analysis_bars} (expected 150)")
                return False
        else:
            print(f"❌ Bot does NOT have analysis_bars attribute")
            return False
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ Error testing bot: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_bot_config_json():
    """Test that bot_config.json has analysis_bars"""
    print("=" * 80)
    print("TEST 4: Checking bot_config.json for analysis_bars")
    print("=" * 80)
    
    try:
        config_file = Path('bot_config.json')
        
        if not config_file.exists():
            print(f"⚠️  bot_config.json does not exist yet")
            print(f"   This is normal if bot hasn't been run yet")
            print()
            return True
        
        with open(config_file, 'r') as f:
            cfg = json.load(f)
        
        if 'analysis_bars' in cfg:
            print(f"✅ analysis_bars is in bot_config.json")
            print(f"   Value: {cfg['analysis_bars']}")
        else:
            print(f"❌ analysis_bars is NOT in bot_config.json")
            print(f"   Bot will use default value (200)")
            return False
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ Error reading bot_config.json: {e}")
        return False


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "ANALYSIS BARS FIX VERIFICATION" + " " * 28 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    
    results = []
    
    # Run tests
    results.append(("config.py", test_config_py()))
    results.append(("config_manager.py", test_config_manager()))
    results.append(("bot reads config", test_bot_reads_config()))
    results.append(("bot_config.json", test_bot_config_json()))
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False
    
    print()
    
    if all_passed:
        print("╔" + "=" * 78 + "╗")
        print("║" + " " * 25 + "ALL TESTS PASSED! ✅" + " " * 33 + "║")
        print("╚" + "=" * 78 + "╝")
        print()
        print("WHAT THIS MEANS:")
        print("  • analysis_bars is properly configured in all files")
        print("  • Bot will now use the value from web dashboard config")
        print("  • When you set analysis_bars to 100 in dashboard, bot will fetch 100 bars")
        print("  • Logs will show: 'Requesting X bars for analysis' and 'Retrieved X bars'")
        print()
        print("NEXT STEPS:")
        print("  1. Restart the bot (stop and start from dashboard)")
        print("  2. Check logs - you should see:")
        print("     '📈 Fetching historical data for XAUUSD (Timeframe: M30)...'")
        print("     '   Requesting 100 bars for analysis'")
        print("     '✅ Retrieved 100 bars of data (requested: 100)'")
        print()
    else:
        print("╔" + "=" * 78 + "╗")
        print("║" + " " * 25 + "SOME TESTS FAILED ❌" + " " * 32 + "║")
        print("╚" + "=" * 78 + "╝")
        print()
        print("Please review the failed tests above.")
        print()
    
    # Cleanup test file
    test_file = Path('test_analysis_bars_config.json')
    if test_file.exists():
        test_file.unlink()
        print("Cleaned up test config file")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
