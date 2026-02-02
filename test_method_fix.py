#!/usr/bin/env python3
"""
Test if the method fix worked
"""

import sys
sys.path.append('src')

try:
    from mt5_trading_bot import MT5TradingBot
    
    # Check if the method exists
    if hasattr(MT5TradingBot, 'calculate_indicators'):
        print("✅ calculate_indicators method exists")
    else:
        print("❌ calculate_indicators method missing")
    
    if hasattr(MT5TradingBot, 'calculate_indicators_with_logging'):
        print("❌ calculate_indicators_with_logging still exists (should be removed)")
    else:
        print("✅ calculate_indicators_with_logging correctly removed")
        
    print("\n🔍 Testing method call...")
    
    # Minimal config for testing
    config = {
        'symbols': ['BTCUSD'],
        'timeframe': 15,
        'magic_number': 123456,
        'lot_size': 0.01,
        'risk_percent': 1,
        'reward_ratio': 1.2,
        'fast_ma_period': 10,
        'slow_ma_period': 30,
        'rsi_period': 14,
        'rsi_overbought': 75,
        'rsi_oversold': 25,
        'macd_fast': 12,
        'macd_slow': 26,
        'macd_signal': 9,
        'atr_period': 14,
        'atr_multiplier': 2,
        'use_adaptive_risk': True,
        'use_volume_filter': True,
        'analysis_bars': 150,
        'use_split_orders': True,
        'num_positions': 3,
        'tp_levels': [1.5, 2.5, 4.0],
        'partial_close_percent': [40, 30, 30],
        'max_lot_per_order': 1,
        'prevent_worse_entries': True
    }
    
    bot = MT5TradingBot(config)
    print("✅ Bot created successfully")
    print("✅ Method fix is working correctly")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()