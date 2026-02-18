#!/usr/bin/env python3
"""
Test script for EMA Momentum Analyzer - Task 1.1
Tests EMA calculation, crossover detection, and momentum analysis
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add src to path
sys.path.append('src')

from ema_momentum_analyzer import EMAMomentumAnalyzer, EMASignal
from config import get_config

def create_ema_test_data(bars=100, trend_type='bullish_crossover'):
    """Create synthetic price data for EMA testing"""
    dates = pd.date_range(start=datetime.now() - timedelta(hours=bars), periods=bars, freq='h')
    
    base_price = 2000.0
    
    if trend_type == 'bullish_crossover':
        # Create data that will cause 20 EMA to cross above 50 EMA
        part1_len = bars//3
        part2_len = bars//3
        part3_len = bars - part1_len - part2_len  # Ensure exact length
        
        trend = np.concatenate([
            np.linspace(0, -20, part1_len),  # Initial downtrend
            np.linspace(-20, 50, part2_len),  # Strong uptrend for crossover
            np.linspace(50, 80, part3_len)   # Continued uptrend
        ])
    elif trend_type == 'bearish_crossover':
        # Create data that will cause 20 EMA to cross below 50 EMA
        part1_len = bars//3
        part2_len = bars//3
        part3_len = bars - part1_len - part2_len  # Ensure exact length
        
        trend = np.concatenate([
            np.linspace(0, 20, part1_len),   # Initial uptrend
            np.linspace(20, -50, part2_len), # Strong downtrend for crossover
            np.linspace(-50, -80, part3_len) # Continued downtrend
        ])
    elif trend_type == 'strong_uptrend':
        # Strong consistent uptrend
        trend = np.linspace(0, 100, bars)
    elif trend_type == 'consolidation':
        # Sideways movement with EMAs close together
        trend = np.sin(np.linspace(0, 4*np.pi, bars)) * 5
    else:
        trend = np.zeros(bars)
    
    noise = np.random.normal(0, 2, bars)  # Reduced noise for cleaner signals
    prices = base_price + trend + noise
    
    # Create OHLC data
    df = pd.DataFrame({
        'open': prices + np.random.normal(0, 0.5, bars),
        'high': prices + np.abs(np.random.normal(1, 0.5, bars)),
        'low': prices - np.abs(np.random.normal(1, 0.5, bars)),
        'close': prices,
        'volume': np.random.randint(1000, 5000, bars),
        'tick_volume': np.random.randint(100, 500, bars)
    }, index=dates)
    
    return df

def test_ema_calculation():
    """Test EMA calculation accuracy"""
    print("🔍 Testing EMA Calculation")
    print("-" * 40)
    
    config = get_config()
    analyzer = EMAMomentumAnalyzer(config)
    
    # Create test data
    df = create_ema_test_data(100, 'strong_uptrend')
    
    # Calculate EMAs
    df_with_emas = analyzer.calculate_emas(df)
    
    # Verify EMA columns were added
    assert f'ema_{analyzer.fast_period}' in df_with_emas.columns, "Fast EMA column missing"
    assert f'ema_{analyzer.slow_period}' in df_with_emas.columns, "Slow EMA column missing"
    assert 'ema_separation' in df_with_emas.columns, "EMA separation column missing"
    assert 'ema_fast_slope' in df_with_emas.columns, "Fast EMA slope column missing"
    assert 'ema_slow_slope' in df_with_emas.columns, "Slow EMA slope column missing"
    
    # Verify EMA values are reasonable
    fast_ema = df_with_emas[f'ema_{analyzer.fast_period}'].iloc[-1]
    slow_ema = df_with_emas[f'ema_{analyzer.slow_period}'].iloc[-1]
    current_price = df_with_emas['close'].iloc[-1]
    
    print(f"✅ EMA columns created successfully")
    print(f"   - Fast EMA ({analyzer.fast_period}): {fast_ema:.2f}")
    print(f"   - Slow EMA ({analyzer.slow_period}): {slow_ema:.2f}")
    print(f"   - Current Price: {current_price:.2f}")
    print(f"   - EMA Separation: {df_with_emas['ema_separation'].iloc[-1]:.2f}%")
    
    # In an uptrend, fast EMA should be above slow EMA
    assert fast_ema > slow_ema, f"In uptrend, fast EMA ({fast_ema:.2f}) should be above slow EMA ({slow_ema:.2f})"
    
    # EMAs should be between reasonable bounds relative to price
    price_range = df['close'].max() - df['close'].min()
    assert abs(fast_ema - current_price) < price_range, "Fast EMA too far from current price"
    assert abs(slow_ema - current_price) < price_range, "Slow EMA too far from current price"
    
    print("✅ EMA calculation validation passed")
    return True

def test_bullish_crossover_detection():
    """Test bullish crossover detection (20 EMA crossing above 50 EMA)"""
    print("\n🔍 Testing Bullish Crossover Detection")
    print("-" * 40)
    
    config = get_config()
    analyzer = EMAMomentumAnalyzer(config)
    
    # Create data with bullish crossover
    df = create_ema_test_data(150, 'bullish_crossover')
    
    # Get EMA signal
    signal = analyzer.get_ema_signal(df)
    
    assert signal is not None, "EMA signal should not be None"
    
    print(f"✅ EMA Signal Generated:")
    print(f"   - Signal Type: {signal.signal_type}")
    print(f"   - Fast EMA: {signal.fast_ema:.2f}")
    print(f"   - Slow EMA: {signal.slow_ema:.2f}")
    print(f"   - Separation: {signal.separation:.2f}%")
    print(f"   - Momentum Strength: {signal.momentum_strength:.3f}")
    print(f"   - Crossover Confirmed: {signal.crossover_confirmed}")
    
    # Verify bullish signal characteristics
    assert signal.fast_ema > signal.slow_ema, "In bullish crossover, fast EMA should be above slow EMA"
    assert signal.separation > 0, "Bullish crossover should have positive separation"
    
    # Check if signal type indicates bullish trend
    bullish_signals = ['bullish_cross', 'strong_bullish_cross', 'strong_bullish_trend', 'moderate_bullish_trend', 'weak_bullish']
    assert any(bs in signal.signal_type for bs in bullish_signals), f"Expected bullish signal, got: {signal.signal_type}"
    
    print("✅ Bullish crossover detection validated")
    return True

def test_bearish_crossover_detection():
    """Test bearish crossover detection (20 EMA crossing below 50 EMA)"""
    print("\n🔍 Testing Bearish Crossover Detection")
    print("-" * 40)
    
    config = get_config()
    analyzer = EMAMomentumAnalyzer(config)
    
    # Create data with bearish crossover
    df = create_ema_test_data(150, 'bearish_crossover')
    
    # Get EMA signal
    signal = analyzer.get_ema_signal(df)
    
    assert signal is not None, "EMA signal should not be None"
    
    print(f"✅ EMA Signal Generated:")
    print(f"   - Signal Type: {signal.signal_type}")
    print(f"   - Fast EMA: {signal.fast_ema:.2f}")
    print(f"   - Slow EMA: {signal.slow_ema:.2f}")
    print(f"   - Separation: {signal.separation:.2f}%")
    print(f"   - Momentum Strength: {signal.momentum_strength:.3f}")
    print(f"   - Crossover Confirmed: {signal.crossover_confirmed}")
    
    # Verify bearish signal characteristics
    assert signal.fast_ema < signal.slow_ema, "In bearish crossover, fast EMA should be below slow EMA"
    assert signal.separation < 0, "Bearish crossover should have negative separation"
    
    # Check if signal type indicates bearish trend
    bearish_signals = ['bearish_cross', 'strong_bearish_cross', 'strong_bearish_trend', 'moderate_bearish_trend', 'weak_bearish']
    assert any(bs in signal.signal_type for bs in bearish_signals), f"Expected bearish signal, got: {signal.signal_type}"
    
    print("✅ Bearish crossover detection validated")
    return True

def test_consolidation_detection():
    """Test consolidation detection when EMAs are close together"""
    print("\n🔍 Testing Consolidation Detection")
    print("-" * 40)
    
    config = get_config()
    analyzer = EMAMomentumAnalyzer(config)
    
    # Create consolidating market data
    df = create_ema_test_data(100, 'consolidation')
    
    # Get EMA signal
    signal = analyzer.get_ema_signal(df)
    
    assert signal is not None, "EMA signal should not be None"
    
    print(f"✅ EMA Signal Generated:")
    print(f"   - Signal Type: {signal.signal_type}")
    print(f"   - Fast EMA: {signal.fast_ema:.2f}")
    print(f"   - Slow EMA: {signal.slow_ema:.2f}")
    print(f"   - Separation: {signal.separation:.2f}%")
    print(f"   - Momentum Strength: {signal.momentum_strength:.3f}")
    
    # In consolidation, separation should be small
    assert abs(signal.separation) < 1.0, f"Consolidation should have small separation, got {signal.separation:.2f}%"
    
    # Signal type should indicate weak trend or consolidation
    consolidation_signals = ['consolidation', 'weak_bullish', 'weak_bearish']
    assert any(cs in signal.signal_type for cs in consolidation_signals), f"Expected consolidation signal, got: {signal.signal_type}"
    
    print("✅ Consolidation detection validated")
    return True

def test_ema_support_resistance():
    """Test EMA-based support/resistance level identification"""
    print("\n🔍 Testing EMA Support/Resistance Levels")
    print("-" * 40)
    
    config = get_config()
    analyzer = EMAMomentumAnalyzer(config)
    
    # Create uptrending data where EMAs act as support
    df = create_ema_test_data(100, 'strong_uptrend')
    
    # Identify support/resistance levels
    sr_levels = analyzer.identify_ema_support_resistance(df)
    
    assert len(sr_levels) > 0, "Should identify at least one support/resistance level"
    
    print(f"✅ Found {len(sr_levels)} EMA-based S/R levels:")
    for i, level in enumerate(sr_levels):
        print(f"   Level {i+1}:")
        print(f"     - Type: {level.level_type}")
        print(f"     - EMA Period: {level.ema_period}")
        print(f"     - Price Level: {level.price_level:.2f}")
        print(f"     - Strength: {level.strength:.3f}")
        print(f"     - Touches: {level.touches}")
        print(f"     - Active: {level.active}")
    
    # In an uptrend, EMAs should act as support
    current_price = df.iloc[-1]['close']
    support_levels = [level for level in sr_levels if level.level_type == 'support']
    
    assert len(support_levels) > 0, "Should identify at least one support level in uptrend"
    
    # Support levels should be below current price
    for level in support_levels:
        assert level.price_level <= current_price, f"Support level {level.price_level:.2f} should be below current price {current_price:.2f}"
    
    print("✅ EMA support/resistance identification validated")
    return True

def test_momentum_strength_calculation():
    """Test momentum strength calculation"""
    print("\n🔍 Testing Momentum Strength Calculation")
    print("-" * 40)
    
    config = get_config()
    analyzer = EMAMomentumAnalyzer(config)
    
    # Test different market conditions
    test_cases = [
        ('strong_uptrend', 'Strong uptrend should have high momentum'),
        ('bullish_crossover', 'Bullish crossover should have moderate to high momentum'),
        ('consolidation', 'Consolidation should have low momentum')
    ]
    
    for trend_type, description in test_cases:
        df = create_ema_test_data(100, trend_type)
        signal = analyzer.get_ema_signal(df)
        
        assert signal is not None, f"Signal should not be None for {trend_type}"
        
        print(f"✅ {description}:")
        print(f"   - Trend Type: {trend_type}")
        print(f"   - Signal Type: {signal.signal_type}")
        print(f"   - Momentum Strength: {signal.momentum_strength:.3f}")
        
        # Validate momentum strength is within valid range
        assert 0.0 <= signal.momentum_strength <= 1.0, f"Momentum strength {signal.momentum_strength} should be between 0.0 and 1.0"
        
        # Strong trends should have higher momentum than consolidation
        if trend_type == 'strong_uptrend':
            assert signal.momentum_strength > 0.3, f"Strong uptrend should have momentum > 0.3, got {signal.momentum_strength:.3f}"
        elif trend_type == 'consolidation':
            assert signal.momentum_strength < 0.8, f"Consolidation should have momentum < 0.8, got {signal.momentum_strength:.3f}"
    
    print("✅ Momentum strength calculation validated")
    return True

def test_ema_analysis_details():
    """Test detailed EMA analysis output"""
    print("\n🔍 Testing EMA Analysis Details")
    print("-" * 40)
    
    config = get_config()
    analyzer = EMAMomentumAnalyzer(config)
    
    # Create test data
    df = create_ema_test_data(100, 'bullish_crossover')
    
    # Get detailed analysis
    details = analyzer.get_ema_analysis_details(df)
    
    # Verify all expected fields are present
    expected_fields = [
        'fast_ema', 'slow_ema', 'separation_pct', 'fast_slope', 'slow_slope',
        'signal', 'support_resistance_levels', 'trend_direction', 'trend_strength'
    ]
    
    for field in expected_fields:
        assert field in details, f"Missing field in analysis details: {field}"
    
    print(f"✅ EMA Analysis Details:")
    print(f"   - Fast EMA: {details['fast_ema']:.2f}")
    print(f"   - Slow EMA: {details['slow_ema']:.2f}")
    print(f"   - Separation: {details['separation_pct']:.2f}%")
    print(f"   - Fast Slope: {details['fast_slope']:.4f}")
    print(f"   - Slow Slope: {details['slow_slope']:.4f}")
    print(f"   - Trend Direction: {details['trend_direction']}")
    print(f"   - Trend Strength: {details['trend_strength']:.3f}")
    print(f"   - S/R Levels: {len(details['support_resistance_levels'])}")
    
    # Validate trend direction consistency
    if details['fast_ema'] > details['slow_ema']:
        assert details['trend_direction'] == 'bullish', "Trend direction should be bullish when fast EMA > slow EMA"
    else:
        assert details['trend_direction'] == 'bearish', "Trend direction should be bearish when fast EMA < slow EMA"
    
    print("✅ EMA analysis details validated")
    return True

def run_all_ema_tests():
    """Run all EMA momentum analyzer tests"""
    print("🔍 EMA Momentum Analyzer Test Suite - Task 1.1")
    print("=" * 60)
    
    tests = [
        test_ema_calculation,
        test_bullish_crossover_detection,
        test_bearish_crossover_detection,
        test_consolidation_detection,
        test_ema_support_resistance,
        test_momentum_strength_calculation,
        test_ema_analysis_details
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test.__name__} FAILED: {str(e)}")
            failed += 1
    
    print("\n" + "=" * 60)
    print("📊 EMA TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {(passed / (passed + failed) * 100):.1f}%")
    
    if failed == 0:
        print("\n🎉 ALL EMA TESTS PASSED!")
        print("✅ EMA calculation working correctly")
        print("✅ Crossover detection functioning properly")
        print("✅ Momentum analysis validated")
        print("✅ Support/resistance identification working")
        print("\n🚀 Task 1.1 Requirements Met:")
        print("   ✅ 20-period and 50-period EMA calculations implemented")
        print("   ✅ EMA crossover signal detection (20 EMA crossing 50 EMA)")
        print("   ✅ Requirements 3.1, 3.2 satisfied")
        return True
    else:
        print(f"\n⚠️ {failed} EMA TESTS FAILED - REVIEW REQUIRED")
        return False

if __name__ == "__main__":
    success = run_all_ema_tests()
    sys.exit(0 if success else 1)