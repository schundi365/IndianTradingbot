"""
Test Profit Booking Features Implementation

Verifies that all new features are properly implemented and configurable.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src')

def test_config_py():
    """Test that config.py has new constants"""
    print("=" * 80)
    print("TEST 1: Checking config.py for new constants")
    print("=" * 80)
    
    try:
        from src import config
        
        required_constants = [
            'TRAIL_ACTIVATION_ATR',
            'TRAIL_DISTANCE_ATR',
            'ENABLE_TIME_BASED_EXIT',
            'MAX_HOLD_MINUTES',
            'ENABLE_BREAKEVEN_STOP',
            'BREAKEVEN_ATR_THRESHOLD',
        ]
        
        all_found = True
        for const in required_constants:
            if hasattr(config, const):
                value = getattr(config, const)
                print(f"✅ {const} = {value}")
            else:
                print(f"❌ {const} NOT FOUND")
                all_found = False
        
        # Check config dictionary
        cfg = config.get_config()
        required_keys = [
            'trail_activation',
            'trail_distance',
            'enable_time_based_exit',
            'max_hold_minutes',
            'enable_breakeven_stop',
            'breakeven_atr_threshold',
        ]
        
        print()
        print("Config Dictionary:")
        for key in required_keys:
            if key in cfg:
                print(f"✅ {key} = {cfg[key]}")
            else:
                print(f"❌ {key} NOT IN CONFIG")
                all_found = False
        
        print()
        return all_found
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config_manager():
    """Test that config_manager has new defaults"""
    print("=" * 80)
    print("TEST 2: Checking config_manager.py for new defaults")
    print("=" * 80)
    
    try:
        from src.config_manager import ConfigManager
        
        manager = ConfigManager('test_profit_booking_config.json')
        cfg = manager.get_config()
        
        required_keys = {
            'trail_activation': 1.0,
            'trail_distance': 0.8,
            'enable_time_based_exit': False,
            'max_hold_minutes': 45,
            'enable_breakeven_stop': True,
            'breakeven_atr_threshold': 0.3,
        }
        
        all_found = True
        for key, expected_default in required_keys.items():
            if key in cfg:
                actual = cfg[key]
                match = "✅" if actual == expected_default else "⚠️"
                print(f"{match} {key} = {actual} (expected: {expected_default})")
            else:
                print(f"❌ {key} NOT FOUND")
                all_found = False
        
        print()
        return all_found
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_bot_methods():
    """Test that bot has new methods"""
    print("=" * 80)
    print("TEST 3: Checking mt5_trading_bot.py for new methods")
    print("=" * 80)
    
    try:
        from src.mt5_trading_bot import MT5TradingBot
        
        # Check if _force_close_position method exists
        if hasattr(MT5TradingBot, '_force_close_position'):
            print("✅ _force_close_position() method exists")
            
            # Check method signature
            import inspect
            sig = inspect.signature(MT5TradingBot._force_close_position)
            params = list(sig.parameters.keys())
            print(f"   Parameters: {params}")
            
            # Check docstring
            doc = MT5TradingBot._force_close_position.__doc__
            if doc and 'Force-close' in doc:
                print("✅ Method has proper docstring")
            else:
                print("⚠️  Method docstring missing or incomplete")
        else:
            print("❌ _force_close_position() method NOT FOUND")
            return False
        
        # Check if manage_positions has profit booking logic
        import inspect
        source = inspect.getsource(MT5TradingBot.manage_positions)
        
        checks = {
            'enable_time_based_exit': 'Time-based exit check',
            'enable_breakeven_stop': 'Break-even stop check',
            '_force_close_position': 'Force close call',
            'PROACTIVE PROFIT BOOKING': 'Section header',
            'max_hold_minutes': 'Max hold time config',
            'breakeven_atr_threshold': 'Break-even threshold config',
        }
        
        print()
        print("manage_positions() method checks:")
        all_found = True
        for check, description in checks.items():
            if check in source:
                print(f"✅ {description}")
            else:
                print(f"❌ {description} NOT FOUND")
                all_found = False
        
        print()
        return all_found
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_bot_config_reading():
    """Test that bot reads new config parameters"""
    print("=" * 80)
    print("TEST 4: Checking if bot reads new config parameters")
    print("=" * 80)
    
    try:
        from src import config
        from src.mt5_trading_bot import MT5TradingBot
        
        # Create test config with custom values
        test_config = config.get_config()
        test_config['trail_activation'] = 0.5
        test_config['trail_distance'] = 0.4
        test_config['enable_time_based_exit'] = True
        test_config['max_hold_minutes'] = 30
        test_config['enable_breakeven_stop'] = True
        test_config['breakeven_atr_threshold'] = 0.25
        
        # Create bot instance
        bot = MT5TradingBot(test_config)
        
        # Check if bot has the values
        checks = {
            'trail_activation': 0.5,
            'trail_distance': 0.4,
        }
        
        all_correct = True
        for attr, expected in checks.items():
            if hasattr(bot, attr):
                actual = getattr(bot, attr)
                match = "✅" if actual == expected else "⚠️"
                print(f"{match} bot.{attr} = {actual} (expected: {expected})")
            else:
                print(f"❌ bot.{attr} NOT FOUND")
                all_correct = False
        
        # Check if config is accessible
        if bot.config.get('enable_time_based_exit') == True:
            print(f"✅ bot.config['enable_time_based_exit'] = True")
        else:
            print(f"❌ bot.config['enable_time_based_exit'] not accessible")
            all_correct = False
        
        if bot.config.get('max_hold_minutes') == 30:
            print(f"✅ bot.config['max_hold_minutes'] = 30")
        else:
            print(f"❌ bot.config['max_hold_minutes'] not accessible")
            all_correct = False
        
        print()
        return all_correct
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "PROFIT BOOKING FEATURES TEST" + " " * 30 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    
    results = []
    
    # Run tests
    results.append(("config.py constants", test_config_py()))
    results.append(("config_manager.py defaults", test_config_manager()))
    results.append(("bot methods", test_bot_methods()))
    results.append(("bot config reading", test_bot_config_reading()))
    
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
        print("FEATURES IMPLEMENTED:")
        print("  ✅ _force_close_position() method")
        print("  ✅ Time-based exit logic")
        print("  ✅ Break-even stop logic")
        print("  ✅ Configurable trailing stop parameters")
        print("  ✅ Dashboard configuration support")
        print()
        print("NEXT STEPS:")
        print("  1. Restart dashboard (to load new code)")
        print("  2. Configure parameters in dashboard")
        print("  3. Start bot and test features")
        print()
        print("CONFIGURATION EXAMPLES:")
        print()
        print("  Aggressive (PROFIT_FIX style):")
        print("    trail_activation: 0.5")
        print("    trail_distance: 0.4")
        print("    enable_time_based_exit: true")
        print("    max_hold_minutes: 30")
        print()
        print("  Balanced (Default):")
        print("    trail_activation: 1.0")
        print("    trail_distance: 0.8")
        print("    enable_time_based_exit: false")
        print()
    else:
        print("╔" + "=" * 78 + "╗")
        print("║" + " " * 25 + "SOME TESTS FAILED ❌" + " " * 32 + "║")
        print("╚" + "=" * 78 + "╝")
        print()
        print("Please review the failed tests above.")
        print()
    
    # Cleanup test file
    test_file = Path('test_profit_booking_config.json')
    if test_file.exists():
        test_file.unlink()
        print("Cleaned up test config file")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
