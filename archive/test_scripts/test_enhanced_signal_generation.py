#!/usr/bin/env python3
"""
Test Enhanced Signal Generation

This script tests the new signal generation methods to ensure
they're working correctly and generating more signals.
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime

# Add src directory to path
sys.path.append('src')

def test_signal_generation():
    """Test the enhanced signal generation methods"""
    print("🧪 Testing Enhanced Signal Generation...")
    print("="*60)
    
    try:
        # Import the trading bot
        from mt5_trading_bot import MT5TradingBot
        from config import config
        
        # Create bot instance
        bot = MT5TradingBot(config)
        
        # Create sample data that should trigger different signal types
        print("📊 Creating test market data...")
        
        # Test data with various market conditions
        dates = pd.date_range(start='2024-01-01', periods=50, freq='30T')
        
        # Scenario 1: Momentum signal (RSI recovery + MACD improvement)
        print("\n🔍 Test 1: Momentum Signal Scenario")
        df1 = pd.DataFrame({
            'time': dates,
            'open': np.linspace(1.8600, 1.8650, 50),
            'high': np.linspace(1.8610, 1.8660, 50),
            'low': np.linspace(1.8590, 1.8640, 50),
            'close': np.linspace(1.8605, 1.8655, 50),
            'tick_volume': np.random.randint(1000, 5000, 50)
        })
        
        # Add indicators that should trigger momentum signal
        df1['fast_ma'] = df1['close'].rolling(10).mean()
        df1['slow_ma'] = df1['close'].rolling(30).mean()
        df1['rsi'] = np.linspace(35, 55, 50)  # RSI recovering from oversold
        df1['macd'] = np.linspace(-0.001, 0.001, 50)
        df1['macd_signal'] = df1['macd'].rolling(9).mean()
        df1['macd_histogram'] = df1['macd'] - df1['macd_signal']
        df1['atr'] = 0.001
        df1['ma_cross'] = 0  # No crossover
        df1['ma_trend'] = 1   # Bullish trend
        
        # Fill NaN values
        df1 = df1.fillna(method='bfill')
        
        print(f"   RSI: {df1.iloc[-1]['rsi']:.2f} (recovering)")
        print(f"   MACD Histogram: {df1.iloc[-1]['macd_histogram']:.6f}")
        print(f"   Price vs Fast MA: {'Above' if df1.iloc[-1]['close'] > df1.iloc[-1]['fast_ma'] else 'Below'}")
        
        signal1 = bot.check_entry_signal(df1)
        print(f"   Result: {'BUY' if signal1 == 1 else 'SELL' if signal1 == -1 else 'NO SIGNAL'}")
        
        # Scenario 2: Pullback signal (Price near MA in trend)
        print("\n🔍 Test 2: Pullback Signal Scenario")
        df2 = pd.DataFrame({
            'time': dates,
            'open': [1.8650] * 50,
            'high': [1.8660] * 50,
            'low': [1.8640] * 50,
            'close': [1.8652] * 50,  # Price very close to fast MA
            'tick_volume': np.random.randint(1000, 5000, 50)
        })
        
        # Set up pullback scenario
        df2['fast_ma'] = 1.8651  # Price very close to fast MA
        df2['slow_ma'] = 1.8640  # Slow MA below (uptrend)
        df2['rsi'] = 50
        df2['macd'] = 0.0001
        df2['macd_signal'] = 0.0001
        df2['macd_histogram'] = 0.0001
        df2['atr'] = 0.001
        df2['ma_cross'] = 0
        df2['ma_trend'] = 1
        
        print(f"   Price: {df2.iloc[-1]['close']:.5f}")
        print(f"   Fast MA: {df2.iloc[-1]['fast_ma']:.5f}")
        print(f"   Distance: {((df2.iloc[-1]['close'] - df2.iloc[-1]['fast_ma']) / df2.iloc[-1]['fast_ma'] * 100):+.3f}%")
        
        signal2 = bot.check_entry_signal(df2)
        print(f"   Result: {'BUY' if signal2 == 1 else 'SELL' if signal2 == -1 else 'NO SIGNAL'}")
        
        # Scenario 3: Breakout signal (Price breaks recent high)
        print("\n🔍 Test 3: Breakout Signal Scenario")
        
        # Create data with recent consolidation then breakout
        consolidation_price = 1.8600
        breakout_price = 1.8620
        
        df3 = pd.DataFrame({
            'time': dates,
            'open': [consolidation_price] * 40 + [breakout_price] * 10,
            'high': [consolidation_price + 0.0005] * 40 + [breakout_price + 0.0005] * 10,
            'low': [consolidation_price - 0.0005] * 40 + [breakout_price - 0.0005] * 10,
            'close': [consolidation_price] * 40 + [breakout_price] * 10,
            'tick_volume': np.random.randint(1000, 5000, 50)
        })
        
        df3['fast_ma'] = df3['close'].rolling(10).mean()
        df3['slow_ma'] = df3['close'].rolling(30).mean()
        df3['rsi'] = 60
        df3['macd'] = 0.0001
        df3['macd_signal'] = 0.0001
        df3['macd_histogram'] = 0.0001
        df3['atr'] = 0.001
        df3['ma_cross'] = 0
        df3['ma_trend'] = 1
        
        # Fill NaN values
        df3 = df3.fillna(method='bfill')
        
        recent_high = df3.tail(10)['high'].max()
        current_price = df3.iloc[-1]['close']
        
        print(f"   Recent High: {recent_high:.5f}")
        print(f"   Current Price: {current_price:.5f}")
        print(f"   Breakout: {'Yes' if current_price > recent_high else 'No'}")
        
        signal3 = bot.check_entry_signal(df3)
        print(f"   Result: {'BUY' if signal3 == 1 else 'SELL' if signal3 == -1 else 'NO SIGNAL'}")
        
        # Summary
        print("\n📊 SIGNAL GENERATION TEST RESULTS:")
        print("="*60)
        print(f"Test 1 (Momentum):  {'✅ PASS' if signal1 != 0 else '❌ FAIL'}")
        print(f"Test 2 (Pullback):  {'✅ PASS' if signal2 != 0 else '❌ FAIL'}")
        print(f"Test 3 (Breakout):  {'✅ PASS' if signal3 != 0 else '❌ FAIL'}")
        
        signals_generated = sum([1 for s in [signal1, signal2, signal3] if s != 0])
        print(f"\nSignals Generated: {signals_generated}/3")
        
        if signals_generated >= 2:
            print("✅ ENHANCED SIGNAL GENERATION IS WORKING!")
            print("The bot should now generate more trading opportunities.")
        else:
            print("⚠️ Signal generation may need further adjustment.")
            
        return signals_generated >= 2
        
    except Exception as e:
        print(f"❌ Error testing signal generation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Enhanced Signal Generation Test")
    print("="*60)
    
    success = test_signal_generation()
    
    if success:
        print("\n🎉 TEST COMPLETED SUCCESSFULLY!")
        print("The enhanced signal generation is working correctly.")
        print("Restart the bot to start generating more signals!")
    else:
        print("\n❌ TEST FAILED!")
        print("Please check the implementation.")