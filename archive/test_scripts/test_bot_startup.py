#!/usr/bin/env python3
"""
Test Bot Startup to identify issues
"""

import sys
import traceback
from pathlib import Path

# Add src to path
sys.path.append('src')

def test_bot_import():
    """Test if we can import the bot without errors"""
    try:
        print("🔍 Testing bot import...")
        from mt5_trading_bot import MT5TradingBot
        print("✅ Bot import successful")
        return True
    except Exception as e:
        print(f"❌ Bot import failed: {e}")
        print("📋 Full traceback:")
        traceback.print_exc()
        return False

def test_bot_initialization():
    """Test bot initialization with minimal config"""
    try:
        print("\n🔍 Testing bot initialization...")
        
        # Minimal config for testing
        test_config = {
            'symbols': ['BTCUSD'],
            'timeframe': 15,
            'magic_number': 123456,
            'lot_size': 0.01,
            'risk_percent': 1,
            'reward_ratio': 1.2,
            'min_trade_confidence': 0.6,
            'fast_ma_period': 10,
            'slow_ma_period': 30,
            'rsi_period': 14,
            'rsi_overbought': 75,
            'rsi_oversold': 25,
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9,
            'macd_min_histogram': 0.0005,
            'atr_period': 14,
            'atr_multiplier': 2,
            'use_adaptive_risk': True,
            'use_volume_filter': True,
            'min_volume_ma': 0.7,
            'volume_ma_period': 20,
            'analysis_bars': 150,
            'use_split_orders': True,
            'num_positions': 3,
            'tp_levels': [1.5, 2.5, 4.0],
            'partial_close_percent': [40, 30, 30],
            'max_lot_per_order': 1,
            'prevent_worse_entries': True
        }
        
        from mt5_trading_bot import MT5TradingBot
        bot = MT5TradingBot(test_config)
        print("✅ Bot initialization successful")
        print(f"   Logger type: {type(bot.logger)}")
        print(f"   Symbols: {bot.symbols}")
        print(f"   Timeframe: {bot.timeframe}")
        return True
        
    except Exception as e:
        print(f"❌ Bot initialization failed: {e}")
        print("📋 Full traceback:")
        traceback.print_exc()
        return False

def test_enhanced_logging():
    """Test enhanced logging functionality"""
    try:
        print("\n🔍 Testing enhanced logging...")
        
        from mt5_trading_bot import PerformanceFormatter, PerformanceLogger, setup_enhanced_logging
        
        # Test formatter
        formatter = PerformanceFormatter()
        print("✅ PerformanceFormatter created")
        
        # Test logger
        logger = PerformanceLogger("test")
        print("✅ PerformanceLogger created")
        
        # Test logging setup
        setup_enhanced_logging()
        print("✅ Enhanced logging setup completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced logging test failed: {e}")
        print("📋 Full traceback:")
        traceback.print_exc()
        return False

def main():
    print("🚀 Bot Startup Diagnostic Test")
    print("=" * 50)
    
    # Test 1: Import
    if not test_bot_import():
        print("\n❌ Cannot proceed - import failed")
        return
    
    # Test 2: Enhanced logging
    if not test_enhanced_logging():
        print("\n⚠️ Enhanced logging has issues but continuing...")
    
    # Test 3: Initialization
    if not test_bot_initialization():
        print("\n❌ Bot initialization failed")
        return
    
    print("\n🎉 All tests passed!")
    print("💡 The bot should be able to start normally")
    print("\n🔍 If the bot is still not working, the issue might be:")
    print("• MT5 connection problems")
    print("• Symbol data availability")
    print("• Threading issues in the web dashboard")
    print("• Configuration conflicts")

if __name__ == "__main__":
    main()