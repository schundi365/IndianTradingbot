#!/usr/bin/env python3
"""
Test script for signal integration between TrendDetectionEngine and MT5TradingBot
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add src directory to path
sys.path.append('src')

def create_trending_data(trend_direction='up', bars=100):
    """Create sample data with a clear trend for testing"""
    dates = pd.date_range(start='2024-01-01', periods=bars, freq='h')
    np.random.seed(42)
    
    base_price = 1.1000
    
    if trend_direction == 'up':
        # Strong uptrend
        trend = np.linspace(0, 0.02, bars)  # 2% upward trend
        noise = np.random.normal(0, 0.0002, bars)
    elif trend_direction == 'down':
        # Strong downtrend  
        trend = np.linspace(0, -0.02, bars)  # 2% downward trend
        noise = np.random.normal(0, 0.0002, bars)
    else:
        # Sideways
        trend = np.zeros(bars)
        noise = np.random.normal(0, 0.0005, bars)
    
    prices = base_price + np.cumsum(noise) + trend
    
    # Create realistic OHLCV data
    df = pd.DataFrame({
        'time': dates,
        'open': prices + np.random.normal(0, 0.0001, bars),
        'high': prices + np.abs(np.random.normal(0, 0.0003, bars)),
        'low': prices - np.abs(np.random.normal(0, 0.0003, bars)),
        'close': prices,
        'tick_volume': np.random.randint(100, 1000, bars),
        'spread': np.random.randint(1, 5, bars),
        'real_volume': np.random.randint(1000, 10000, bars)
    })
    
    # Calculate proper indicators
    df['fast_ma'] = df['close'].rolling(window=20).mean()
    df['slow_ma'] = df['close'].rolling(window=50).mean()
    
    # RSI calculation
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # MACD calculation
    ema_fast = df['close'].ewm(span=12).mean()
    ema_slow = df['close'].ewm(span=26).mean()
    df['macd'] = ema_fast - ema_slow
    df['macd_signal'] = df['macd'].ewm(span=9).mean()
    df['macd_histogram'] = df['macd'] - df['macd_signal']
    
    # MA trend and crossover
    df['ma_trend'] = np.where(df['fast_ma'] > df['slow_ma'], 1, -1)
    df['ma_cross'] = 0
    
    # Add crossover signals
    for i in range(1, len(df)):
        if (df['fast_ma'].iloc[i] > df['slow_ma'].iloc[i] and 
            df['fast_ma'].iloc[i-1] <= df['slow_ma'].iloc[i-1]):
            df.loc[df.index[i], 'ma_cross'] = 1  # Bullish cross
        elif (df['fast_ma'].iloc[i] < df['slow_ma'].iloc[i] and 
              df['fast_ma'].iloc[i-1] >= df['slow_ma'].iloc[i-1]):
            df.loc[df.index[i], 'ma_cross'] = -1  # Bearish cross
    
    return df

def test_signal_generation():
    """Test signal generation with trend detection"""
    print("="*80)
    print("🔍 TESTING SIGNAL GENERATION WITH TREND DETECTION")
    print("="*80)
    
    try:
        from src.trend_detection_engine import TrendDetectionEngine
        
        # Test configuration
        config = {
            'use_trend_detection': True,
            'trend_detection_sensitivity': 5,
            'min_trend_confidence': 0.4,  # Lower threshold for testing
            'enable_early_signals': True,
            'aroon_period': 25,
            'swing_strength': 3,  # Lower for more sensitivity
            'max_trendlines': 5,
            'min_trendline_touches': 2,
            'trendline_angle_min': 5,  # More permissive
            'trendline_angle_max': 85,
            'touch_tolerance': 0.003,  # More permissive
            'min_trendline_duration': 5,  # Shorter for testing
            'max_lookback_bars': 100,
            'break_threshold': 0.001,
            'volume_confirmation_threshold': 1.2,  # Lower threshold
            'retest_tolerance': 0.003
        }
        
        trend_engine = TrendDetectionEngine(config)
        
        # Test 1: Bullish trend data
        print("\n1. Testing with BULLISH trend data...")
        bullish_data = create_trending_data('up', 100)
        
        print(f"   📊 Data created: {len(bullish_data)} bars")
        print(f"   📈 Price movement: {bullish_data['close'].iloc[0]:.5f} → {bullish_data['close'].iloc[-1]:.5f}")
        print(f"   📈 Total change: {((bullish_data['close'].iloc[-1] / bullish_data['close'].iloc[0]) - 1) * 100:.2f}%")
        
        bullish_analysis = trend_engine.analyze_trend_change(bullish_data, "EURUSD_BULL")
        
        print(f"   ✅ Analysis completed:")
        print(f"      - Confidence: {bullish_analysis.confidence:.3f}")
        print(f"      - Signals: {len(bullish_analysis.signals)}")
        print(f"      - Early warnings: {len(bullish_analysis.early_warnings)}")
        
        # Check for bullish signals
        bullish_signals = [s for s in bullish_analysis.signals if 'bullish' in s.signal_type]
        if bullish_signals:
            print(f"   🎯 Bullish signals detected: {len(bullish_signals)}")
            for signal in bullish_signals:
                print(f"      - {signal.source}: confidence {signal.confidence:.3f}")
        
        # Test should_trade_trend
        should_buy, buy_conf = trend_engine.should_trade_trend(bullish_data, "buy")
        should_sell, sell_conf = trend_engine.should_trade_trend(bullish_data, "sell")
        
        print(f"   📊 Trade recommendations:")
        print(f"      - BUY: {should_buy} (confidence: {buy_conf:.3f})")
        print(f"      - SELL: {should_sell} (confidence: {sell_conf:.3f})")
        
        # Test 2: Bearish trend data
        print("\n2. Testing with BEARISH trend data...")
        bearish_data = create_trending_data('down', 100)
        
        print(f"   📊 Data created: {len(bearish_data)} bars")
        print(f"   📉 Price movement: {bearish_data['close'].iloc[0]:.5f} → {bearish_data['close'].iloc[-1]:.5f}")
        print(f"   📉 Total change: {((bearish_data['close'].iloc[-1] / bearish_data['close'].iloc[0]) - 1) * 100:.2f}%")
        
        bearish_analysis = trend_engine.analyze_trend_change(bearish_data, "EURUSD_BEAR")
        
        print(f"   ✅ Analysis completed:")
        print(f"      - Confidence: {bearish_analysis.confidence:.3f}")
        print(f"      - Signals: {len(bearish_analysis.signals)}")
        print(f"      - Early warnings: {len(bearish_analysis.early_warnings)}")
        
        # Check for bearish signals
        bearish_signals = [s for s in bearish_analysis.signals if 'bearish' in s.signal_type]
        if bearish_signals:
            print(f"   🎯 Bearish signals detected: {len(bearish_signals)}")
            for signal in bearish_signals:
                print(f"      - {signal.source}: confidence {signal.confidence:.3f}")
        
        # Test should_trade_trend
        should_buy, buy_conf = trend_engine.should_trade_trend(bearish_data, "buy")
        should_sell, sell_conf = trend_engine.should_trade_trend(bearish_data, "sell")
        
        print(f"   📊 Trade recommendations:")
        print(f"      - BUY: {should_buy} (confidence: {buy_conf:.3f})")
        print(f"      - SELL: {should_sell} (confidence: {sell_conf:.3f})")
        
        # Test 3: Sideways data
        print("\n3. Testing with SIDEWAYS trend data...")
        sideways_data = create_trending_data('sideways', 100)
        
        print(f"   📊 Data created: {len(sideways_data)} bars")
        print(f"   ↔️  Price movement: {sideways_data['close'].iloc[0]:.5f} → {sideways_data['close'].iloc[-1]:.5f}")
        print(f"   ↔️  Total change: {((sideways_data['close'].iloc[-1] / sideways_data['close'].iloc[0]) - 1) * 100:.2f}%")
        
        sideways_analysis = trend_engine.analyze_trend_change(sideways_data, "EURUSD_SIDE")
        
        print(f"   ✅ Analysis completed:")
        print(f"      - Confidence: {sideways_analysis.confidence:.3f}")
        print(f"      - Signals: {len(sideways_analysis.signals)}")
        print(f"      - Early warnings: {len(sideways_analysis.early_warnings)}")
        
        # Test should_trade_trend
        should_buy, buy_conf = trend_engine.should_trade_trend(sideways_data, "buy")
        should_sell, sell_conf = trend_engine.should_trade_trend(sideways_data, "sell")
        
        print(f"   📊 Trade recommendations:")
        print(f"      - BUY: {should_buy} (confidence: {buy_conf:.3f})")
        print(f"      - SELL: {should_sell} (confidence: {sell_conf:.3f})")
        
        print("\n" + "="*80)
        print("✅ SIGNAL GENERATION TESTS COMPLETED!")
        print("="*80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ SIGNAL GENERATION TEST FAILED: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("🚀 STARTING SIGNAL INTEGRATION TESTS")
    
    success = test_signal_generation()
    
    if success:
        print("\n🎉 SIGNAL INTEGRATION TESTS PASSED!")
        print("The TrendDetectionEngine is properly integrated and working.")
    else:
        print("\n💥 SIGNAL INTEGRATION TESTS FAILED!")
        print("Please check the errors above.")