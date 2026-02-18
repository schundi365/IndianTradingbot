#!/usr/bin/env python3
"""
Test script for TrendDetectionEngine integration with MT5TradingBot
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add src directory to path
sys.path.append('src')

def test_trend_detection_engine():
    """Test TrendDetectionEngine initialization and basic functionality"""
    print("="*80)
    print("🔍 TESTING TREND DETECTION ENGINE INTEGRATION")
    print("="*80)
    
    try:
        # Test 1: Import TrendDetectionEngine
        print("1. Testing TrendDetectionEngine import...")
        from src.trend_detection_engine import TrendDetectionEngine
        print("   ✅ TrendDetectionEngine imported successfully")
        
        # Test 2: Initialize with basic config
        print("\n2. Testing TrendDetectionEngine initialization...")
        config = {
            'use_trend_detection': True,
            'trend_detection_sensitivity': 5,
            'min_trend_confidence': 0.6,
            'enable_early_signals': True,
            'aroon_period': 25,
            'swing_strength': 5,
            'max_trendlines': 5,
            'min_trendline_touches': 2,
            'trendline_angle_min': 10,
            'trendline_angle_max': 80,
            'touch_tolerance': 0.002,
            'min_trendline_duration': 10,
            'max_lookback_bars': 100,
            'break_threshold': 0.001,
            'volume_confirmation_threshold': 1.5,
            'retest_tolerance': 0.003
        }
        
        trend_engine = TrendDetectionEngine(config)
        print("   ✅ TrendDetectionEngine initialized successfully")
        
        # Test 3: Create sample data
        print("\n3. Creating sample market data...")
        dates = pd.date_range(start='2024-01-01', periods=100, freq='H')
        np.random.seed(42)  # For reproducible results
        
        # Generate realistic price data with trend
        base_price = 1.1000
        price_changes = np.random.normal(0, 0.0005, 100)
        trend = np.linspace(0, 0.01, 100)  # Upward trend
        
        prices = base_price + np.cumsum(price_changes) + trend
        
        # Create OHLCV data
        df = pd.DataFrame({
            'time': dates,
            'open': prices + np.random.normal(0, 0.0001, 100),
            'high': prices + np.abs(np.random.normal(0, 0.0003, 100)),
            'low': prices - np.abs(np.random.normal(0, 0.0003, 100)),
            'close': prices,
            'tick_volume': np.random.randint(100, 1000, 100),
            'spread': np.random.randint(1, 5, 100),
            'real_volume': np.random.randint(1000, 10000, 100)
        })
        
        # Add basic indicators
        df['fast_ma'] = df['close'].rolling(window=20).mean()
        df['slow_ma'] = df['close'].rolling(window=50).mean()
        df['rsi'] = 50 + np.random.normal(0, 10, 100)  # Mock RSI
        df['macd'] = np.random.normal(0, 0.0001, 100)  # Mock MACD
        df['macd_signal'] = df['macd'].rolling(window=9).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        print(f"   ✅ Sample data created: {len(df)} bars")
        print(f"   📊 Price range: {df['close'].min():.5f} - {df['close'].max():.5f}")
        
        # Test 4: Run trend analysis
        print("\n4. Testing trend analysis...")
        analysis_result = trend_engine.analyze_trend_change(df, "EURUSD_TEST")
        
        print(f"   ✅ Trend analysis completed")
        print(f"   📊 Results:")
        print(f"      - Overall confidence: {analysis_result.confidence:.3f}")
        print(f"      - Signals generated: {len(analysis_result.signals)}")
        print(f"      - Early warnings: {len(analysis_result.early_warnings)}")
        
        if analysis_result.signals:
            print(f"      - Signal types:")
            for signal in analysis_result.signals:
                print(f"        * {signal.source}: {signal.signal_type} (confidence: {signal.confidence:.3f})")
        
        # Test 5: Test signal filtering
        print("\n5. Testing signal filtering...")
        filtered_signals = trend_engine.apply_comprehensive_signal_filtering(analysis_result.signals)
        print(f"   ✅ Signal filtering completed")
        print(f"   📊 Filtered signals: {len(filtered_signals)}/{len(analysis_result.signals)}")
        
        # Test 6: Test confidence calculation
        print("\n6. Testing confidence calculation...")
        confidence = trend_engine.calculate_trend_confidence(filtered_signals)
        print(f"   ✅ Confidence calculation completed: {confidence:.3f}")
        
        # Test 7: Test should_trade_trend
        print("\n7. Testing trade decision logic...")
        should_trade_buy, buy_confidence = trend_engine.should_trade_trend(df, "buy")
        should_trade_sell, sell_confidence = trend_engine.should_trade_trend(df, "sell")
        
        print(f"   ✅ Trade decision logic completed")
        print(f"   📊 Buy signal: {should_trade_buy} (confidence: {buy_confidence:.3f})")
        print(f"   📊 Sell signal: {should_trade_sell} (confidence: {sell_confidence:.3f})")
        
        print("\n" + "="*80)
        print("✅ ALL TREND DETECTION ENGINE TESTS PASSED!")
        print("="*80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_mt5_integration():
    """Test MT5TradingBot integration with TrendDetectionEngine"""
    print("\n" + "="*80)
    print("🔍 TESTING MT5TRADINGBOT INTEGRATION")
    print("="*80)
    
    try:
        # Test 1: Import MT5TradingBot
        print("1. Testing MT5TradingBot import...")
        from src.mt5_trading_bot import MT5TradingBot
        print("   ✅ MT5TradingBot imported successfully")
        
        # Test 2: Initialize with trend detection enabled
        print("\n2. Testing MT5TradingBot initialization with trend detection...")
        
        # Mock config for testing
        config = {
            'use_trend_detection': True,
            'trend_detection_sensitivity': 5,
            'min_trend_confidence': 0.6,
            'enable_early_signals': True,
            'symbols': ['EURUSD'],
            'timeframe': 30,  # M30
            'fast_ma_period': 20,
            'slow_ma_period': 50,
            'atr_period': 14,
            'atr_multiplier': 2.0,
            'reward_ratio': 2.0,
            'risk_percent': 1.0,
            'lot_size': 0.1,
            'max_positions': 3,
            'rsi_overbought': 70,
            'rsi_oversold': 30,
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9,
            'use_adx': True,
            'adx_period': 14,
            'adx_min_strength': 25
        }
        
        # Note: We can't actually initialize MT5TradingBot without MT5 connection
        # But we can test the trend analysis methods
        print("   ✅ Configuration prepared for MT5TradingBot")
        
        # Test 3: Test trend analysis method structure
        print("\n3. Testing trend analysis method availability...")
        
        # Check if the methods exist in the class
        import inspect
        mt5_methods = [method for method in dir(MT5TradingBot) if not method.startswith('_')]
        
        required_methods = ['get_trend_analysis', 'get_trend_summary']
        for method in required_methods:
            if method in mt5_methods:
                print(f"   ✅ Method '{method}' found in MT5TradingBot")
            else:
                print(f"   ❌ Method '{method}' NOT found in MT5TradingBot")
                return False
        
        print("\n" + "="*80)
        print("✅ MT5TRADINGBOT INTEGRATION TESTS PASSED!")
        print("   Note: Full integration test requires MT5 connection")
        print("="*80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ INTEGRATION TEST FAILED: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("🚀 STARTING TREND DETECTION INTEGRATION TESTS")
    print("="*80)
    
    # Run tests
    engine_test_passed = test_trend_detection_engine()
    integration_test_passed = test_mt5_integration()
    
    # Summary
    print("\n" + "="*80)
    print("📋 TEST SUMMARY")
    print("="*80)
    print(f"TrendDetectionEngine Tests: {'✅ PASSED' if engine_test_passed else '❌ FAILED'}")
    print(f"MT5TradingBot Integration:  {'✅ PASSED' if integration_test_passed else '❌ FAILED'}")
    
    if engine_test_passed and integration_test_passed:
        print("\n🎉 ALL TESTS PASSED! Trend Detection Engine is ready for use.")
        exit(0)
    else:
        print("\n💥 SOME TESTS FAILED! Please check the errors above.")
        exit(1)