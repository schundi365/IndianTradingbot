#!/usr/bin/env python3
"""
Test script to verify detailed logging is working in the trading bot
"""

import sys
import os
import logging

# Add src directory to path
sys.path.insert(0, 'src')  # Insert at beginning to prioritize

# Import the trading bot
import importlib
import mt5_trading_bot
print(f"Importing from: {mt5_trading_bot.__file__}")
importlib.reload(mt5_trading_bot)  # Force reload
from mt5_trading_bot import MT5TradingBot

# Setup logging to console for testing
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

def test_detailed_logging():
    """Test if detailed logging is working"""
    print("Testing detailed logging in MT5 Trading Bot...")
    
    # Create a bot instance (without connecting to MT5)
    config = {
        'symbols': ['XAUUSD'],
        'timeframe': 30,
        'risk_percent': 1.0,
        'fast_ma_period': 10,
        'slow_ma_period': 20,
        'atr_period': 14,
        'atr_multiplier': 2.0,
        'reward_ratio': 1.2,
        'lot_size': 0.1,
        'magic_number': 123456,
        'macd_fast': 12,
        'macd_slow': 26,
        'macd_signal': 9
    }
    
    bot = MT5TradingBot(config)
    
    # Create some dummy data to test calculate_indicators
    import pandas as pd
    import numpy as np
    
    # Generate dummy OHLC data
    dates = pd.date_range(start='2026-01-01', periods=100, freq='30T')
    np.random.seed(42)
    
    # Generate realistic price data
    base_price = 2000.0
    price_changes = np.random.normal(0, 5, 100)
    prices = base_price + np.cumsum(price_changes)
    
    df = pd.DataFrame({
        'open': prices + np.random.normal(0, 1, 100),
        'high': prices + np.abs(np.random.normal(2, 1, 100)),
        'low': prices - np.abs(np.random.normal(2, 1, 100)),
        'close': prices,
        'volume': np.random.randint(1000, 10000, 100)
    }, index=dates)
    
    print("\n" + "="*80)
    print("TESTING CALCULATE_INDICATORS METHOD")
    print("="*80)
    
    # Test the calculate_indicators method
    try:
        print("Calling bot.calculate_indicators(df)...")
        print(f"Method object: {bot.calculate_indicators}")
        print(f"Method type: {type(bot.calculate_indicators)}")
        print(f"Method __name__: {getattr(bot.calculate_indicators, '__name__', 'NO NAME')}")
        print(f"Method __module__: {getattr(bot.calculate_indicators, '__module__', 'NO MODULE')}")
        
        # Try to get the source code of the method
        import inspect
        try:
            source = inspect.getsource(bot.calculate_indicators)
            print(f"Method source (first 500 chars):")
            print(source[:500])
            print("...")
            
            # Check if our debug print is in the source
            if "🚨 CRITICAL DEBUG" in source:
                print("✅ Debug code found in source!")
            else:
                print("❌ Debug code NOT found in source!")
                
        except Exception as e:
            print(f"Could not get source: {e}")
        
        result_df = bot.calculate_indicators(df)
        print(f"\n✅ calculate_indicators completed successfully!")
        print(f"   Input rows: {len(df)}")
        print(f"   Output rows: {len(result_df)}")
        print(f"   New columns added: {set(result_df.columns) - set(df.columns)}")
        
        # Check if the detailed logging actually ran by looking for specific columns
        expected_columns = ['fast_ma', 'slow_ma', 'atr', 'rsi', 'macd']
        missing_columns = [col for col in expected_columns if col not in result_df.columns]
        if missing_columns:
            print(f"   ⚠️ Missing expected columns: {missing_columns}")
        else:
            print(f"   ✅ All expected columns present: {expected_columns}")
        
    except Exception as e:
        print(f"\n❌ calculate_indicators failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)
    print("TESTING CALCULATE_POSITION_SIZE METHOD")
    print("="*80)
    
    # Test calculate_position_size (this will fail without MT5 connection, but we can see the logging)
    try:
        lot_size = bot.calculate_position_size('XAUUSD', 2000.0, 1980.0)
        print(f"\n✅ calculate_position_size completed: {lot_size}")
    except Exception as e:
        print(f"\n⚠️ calculate_position_size failed (expected without MT5): {e}")
    
    print("\n" + "="*80)
    print("TEST COMPLETED")
    print("="*80)

if __name__ == "__main__":
    test_detailed_logging()