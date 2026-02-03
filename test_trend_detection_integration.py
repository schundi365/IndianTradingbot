#!/usr/bin/env python3
"""
Test script for Trend Detection Engine integration
Tests the basic functionality of the trend detection system
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add src to path
sys.path.append('src')

from trend_detection_engine import TrendDetectionEngine
from config import get_config

def create_test_data(bars=100):
    """Create synthetic price data for testing"""
    dates = pd.date_range(start=datetime.now() - timedelta(hours=bars), periods=bars, freq='H')
    
    # Create synthetic price data with trend
    base_price = 2000.0
    trend = np.linspace(0, 50, bars)  # Upward trend
    noise = np.random.normal(0, 5, bars)  # Random noise
    
    prices = base_price + trend + noise
    
    # Create OHLC data
    df = pd.DataFrame({
        'open': prices + np.random.normal(0, 1, bars),
        'high': prices + np.abs(np.random.normal(2, 1, bars)),
        'low': prices - np.abs(np.random.normal(2, 1, bars)),
        'close': prices,
        'volume': np.random.randint(1000, 5000, bars),
        'tick_volume': np.random.randint(100, 500, bars)
    }, index=dates)
    
    return df

def test_trend_detection_engine():
    """Test the TrendDetectionEngine functionality"""
    print("🔍 Testing Trend Detection Engine Integration")
    print("=" * 60)
    
    try:
        # Get configuration
        config = get_config()
        print(f"✅ Configuration loaded successfully")
        
        # Initialize trend detection engine
        engine = TrendDetectionEngine(config)
        print(f"✅ TrendDetectionEngine initialized")
        print(f"   - Use trend detection: {engine.use_trend_detection}")
        print(f"   - Sensitivity: {engine.sensitivity}")
        print(f"   - Min confidence: {engine.min_confidence}")
        
        # Create test data
        df = create_test_data(100)
        print(f"✅ Test data created: {len(df)} bars")
        print(f"   - Price range: {df['low'].min():.2f} - {df['high'].max():.2f}")
        
        # Test trend analysis
        print("\n🔍 Testing trend analysis...")
        analysis_result = engine.analyze_trend_change(df, "TESTPAIR")
        
        print(f"✅ Trend analysis completed")
        print(f"   - Signals found: {len(analysis_result.signals)}")
        print(f"   - Overall confidence: {analysis_result.confidence:.3f}")
        print(f"   - Market structure: {'Yes' if analysis_result.market_structure else 'No'}")
        print(f"   - Aroon signal: {'Yes' if analysis_result.aroon_signal else 'No'}")
        
        # Test signal generation
        print("\n🔍 Testing signal generation...")
        buy_signals = engine.get_trend_signals(df, "buy")
        sell_signals = engine.get_trend_signals(df, "sell")
        
        print(f"✅ Signal generation completed")
        print(f"   - Buy signals: {len(buy_signals)}")
        print(f"   - Sell signals: {len(sell_signals)}")
        
        # Test trading decision
        print("\n🔍 Testing trading decision logic...")
        should_buy, buy_confidence = engine.should_trade_trend(df, "buy")
        should_sell, sell_confidence = engine.should_trade_trend(df, "sell")
        
        print(f"✅ Trading decision logic completed")
        print(f"   - Should buy: {should_buy} (confidence: {buy_confidence:.3f})")
        print(f"   - Should sell: {should_sell} (confidence: {sell_confidence:.3f})")
        
        # Display detailed signal information
        if analysis_result.signals:
            print("\n📊 Signal Details:")
            for i, signal in enumerate(analysis_result.signals):
                print(f"   Signal {i+1}:")
                print(f"     - Type: {signal.signal_type}")
                print(f"     - Source: {signal.source}")
                print(f"     - Strength: {signal.strength:.3f}")
                print(f"     - Confidence: {signal.confidence:.3f}")
                print(f"     - Supporting factors: {', '.join(signal.supporting_factors)}")
        
        # Display Aroon signal details
        if analysis_result.aroon_signal:
            aroon = analysis_result.aroon_signal
            print(f"\n📈 Aroon Signal Details:")
            print(f"   - Aroon Up: {aroon.aroon_up:.2f}")
            print(f"   - Aroon Down: {aroon.aroon_down:.2f}")
            print(f"   - Oscillator: {aroon.oscillator:.2f}")
            print(f"   - Signal Type: {aroon.signal_type}")
            print(f"   - Trend Strength: {aroon.trend_strength:.3f}")
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED - Trend Detection Integration Working!")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_trend_detection_engine()
    sys.exit(0 if success else 1)