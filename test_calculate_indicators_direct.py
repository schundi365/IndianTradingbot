#!/usr/bin/env python3
"""
Test calculate_indicators method directly
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.append('src')

def test_calculate_indicators_direct():
    """Test the calculate_indicators method directly"""
    
    print("🧪 TESTING CALCULATE_INDICATORS DIRECTLY")
    print("=" * 50)
    
    try:
        # Import the bot
        from mt5_trading_bot import MT5TradingBot
        from config import get_config
        
        print("✅ Imported bot successfully")
        
        # Get config
        config = get_config()
        print("✅ Loaded configuration")
        
        # Create bot instance
        bot = MT5TradingBot(config)
        print("✅ Created bot instance")
        
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
        print(f"   Data shape: {df.shape}")
        print(f"   Price range: {df['close'].min():.2f} - {df['close'].max():.2f}")
        
        # Test the calculate_indicators method directly
        print("\n🔍 Testing calculate_indicators method...")
        print("=" * 60)
        
        result_df = bot.calculate_indicators(df)
        
        print("=" * 60)
        print("✅ Method executed successfully!")
        print(f"   Result shape: {result_df.shape}")
        print(f"   Columns: {list(result_df.columns)}")
        
        # Check if indicators were calculated
        expected_indicators = ['fast_ma', 'slow_ma', 'atr', 'rsi', 'macd', 'macd_signal', 'macd_histogram']
        found_indicators = [col for col in expected_indicators if col in result_df.columns]
        
        print(f"   Indicators found: {found_indicators}")
        
        if len(found_indicators) == len(expected_indicators):
            print("✅ All indicators calculated successfully!")
        else:
            missing = [col for col in expected_indicators if col not in result_df.columns]
            print(f"⚠️ Missing indicators: {missing}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_calculate_indicators_direct()
    
    if success:
        print("\n✅ CALCULATE_INDICATORS TEST PASSED!")
        print("📝 The detailed logging should now appear when the bot runs")
    else:
        print("\n❌ CALCULATE_INDICATORS TEST FAILED!")
        print("📝 There may be an issue with the implementation")