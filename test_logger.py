#!/usr/bin/env python3
"""
Test if the enhanced logging is working
"""

import sys
sys.path.append('src')

from mt5_trading_bot import MT5TradingBot

# Minimal config for testing
config = {
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

print("🔍 Testing enhanced logging...")

try:
    bot = MT5TradingBot(config)
    print("✅ Bot created successfully")
    
    if hasattr(bot, 'logger'):
        print(f"✅ Logger exists: {type(bot.logger)}")
        
        # Test the logger
        bot.logger.info("🧪 Testing enhanced logging functionality")
        print("✅ Logger test completed")
    else:
        print("❌ Logger not found")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()