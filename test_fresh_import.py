#!/usr/bin/env python3
"""
Test with completely fresh import
"""

import sys
import os
import importlib

# Clear any cached modules
modules_to_clear = [key for key in sys.modules.keys() if 'mt5_trading_bot' in key or 'config' in key]
for module in modules_to_clear:
    if module in sys.modules:
        del sys.modules[module]
        print(f"Cleared cached module: {module}")

# Add src to path
sys.path.insert(0, 'src')

def test_fresh_import():
    """Test with completely fresh import"""
    
    print("🧪 TESTING WITH FRESH IMPORT")
    print("=" * 50)
    
    try:
        # Fresh import
        from mt5_trading_bot import MT5TradingBot
        from config import get_config
        
        print("✅ Fresh import successful")
        
        # Get config
        config = get_config()
        print("✅ Loaded configuration")
        
        # Create bot instance
        bot = MT5TradingBot(config)
        print("✅ Created bot instance")
        
        # Check if the method exists and what it contains
        method = getattr(bot, 'calculate_indicators')
        print(f"✅ Method exists: {method}")
        
        # Try to get the source code
        import inspect
        try:
            source = inspect.getsource(method)
            if "🚨🚨🚨 CALCULATE_INDICATORS METHOD CALLED" in source:
                print("✅ Updated code detected in method source")
            else:
                print("❌ Updated code NOT detected in method source")
                print("First few lines of method:")
                print(source[:500])
        except Exception as e:
            print(f"Could not get source: {e}")
        
        # Test with sample data
        import pandas as pd
        import numpy as np
        
        # Create sample OHLC data
        dates = pd.date_range('2024-01-01', periods=50, freq='h')
        np.random.seed(42)
        
        # Generate realistic price data
        base_price = 2000.0
        price_changes = np.random.normal(0, 10, 50)
        prices = base_price + np.cumsum(price_changes)
        
        df = pd.DataFrame({
            'time': dates,
            'open': prices + np.random.normal(0, 2, 50),
            'high': prices + np.abs(np.random.normal(5, 3, 50)),
            'low': prices - np.abs(np.random.normal(5, 3, 50)),
            'close': prices,
            'tick_volume': np.random.randint(100, 1000, 50),
            'spread': np.random.randint(1, 5, 50),
            'real_volume': np.random.randint(1000, 10000, 50)
        })
        
        # Set time as index
        df.set_index('time', inplace=True)
        
        print("✅ Created sample data")
        
        # Test the calculate_indicators method directly
        print("\n🔍 Testing calculate_indicators method...")
        print("=" * 60)
        
        result_df = bot.calculate_indicators(df)
        
        print("=" * 60)
        print("✅ Method executed successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_fresh_import()
    
    if success:
        print("\n✅ FRESH IMPORT TEST PASSED!")
    else:
        print("\n❌ FRESH IMPORT TEST FAILED!")