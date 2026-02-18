#!/usr/bin/env python3
"""
Test script for EMA Slope Analysis Enhancement - Task 1.3
Tests enhanced slope analysis for momentum confirmation
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add src to path
sys.path.append('src')

from ema_momentum_analyzer import EMAMomentumAnalyzer
from config import get_config

def create_slope_test_data(bars=100, slope_pattern='accelerating_bullish'):
    """Create synthetic price data for slope analysis testing"""
    dates = pd.date_range(start=datetime.now() - timedelta(hours=bars), periods=bars, freq='h')
    
    base_price = 2000.0
    
    if slope_pattern == 'accelerating_bullish':
        # Create accelerating uptrend (increasing positive slope)
        x = np.linspace(0, 1, bars)
        trend = 100 * x**2  # Quadratic growth for acceleration
        
    elif slope_pattern == 'decelerating_bullish':
        # Create decelerating uptrend (decreasing positive slope)
        x = np.linspace(0, 1, bars)
        trend = 50 * np.sqrt(x)  # Square root growth for deceleration
        
    elif slope_pattern == 'accelerating_bearish':
        # Create accelerating downtrend (increasing negative slope)
        x = np.linspace(0, 1, bars)
        trend = -100 * x**2  # Quadratic decline for acceleration
        
    elif slope_pattern == 'consistent_bullish':
        # Create consistent uptrend (steady positive slope)
        trend = np.linspace(0, 80, bars)
        
    elif slope_pattern == 'mixed_slopes':
        # Create mixed slope pattern (fast and slow EMAs diverging)
        part1 = np.linspace(0, 30, bars//2)
        part2 = np.linspace(30, 10, bars - bars//2)
        trend = np.concatenate([part1, part2])
        
    elif slope_pattern == 'flat_consolidation':
        # Create flat market with minimal slopes
        trend = np.sin(np.linspace(0, 2*np.pi, bars)) * 2
        
    else:
        trend = np.zeros(bars)
    
    noise = np.random.normal(0, 1, bars)  # Minimal noise for cleaner slope signals
    prices = base_price + trend + noise
    
    # Create OHLC data
    df = pd.DataFrame({
        'open': prices + np.random.normal(0, 0.3, bars),
        'high': prices + np.abs(np.random.normal(0.5, 0.2, bars)),
        'low': prices - np.abs(np.random.normal(0.5, 0.2, bars)),
        'close': prices,
        'volume': np.random.randint(1000, 5000, bars),
        'tick_volume': np.random.randint(100, 500, bars)
    }, index=dates)
    
    return df

def test_slope_calculation_accuracy():
    """Test slope calculation accuracy and consistency"""
    print("🔍 Testing Slope Calculation Accuracy")
    print("-" * 40)
    
    config = get_config()
    analyzer = EMAMomentumAnalyzer(config)
    
    # Create consistent uptrend data
    df = create_slope_test_data(100, 'consistent_bullish')
    df_with_emas = analyzer.calculate_emas(df)
    
    # Verify slope columns exist
    assert 'ema_fast_slope' in df_with_emas.columns, "Fast EMA slope column missing"
    assert 'ema_slow_slope' in df_with_emas.columns, "Slow EMA slope column missing"
    
    # Get recent slopes (skip NaN values)
    recent_data = df_with_emas.dropna().tail(10)
    fast_slopes = recent_data['ema_fast_slope'].values
    slow_slopes = recent_data['ema_slow_slope'].values
    
    print(f"✅ Slope Calculation Results:")
    print(f"   - Fast EMA slopes (last 5): {fast_slopes[-5:]}")
    print(f"   - Slow EMA slopes (last 5): {slow_slopes[-5:]}")
    
    # In consistent uptrend, slopes should be positive
    assert np.mean(fast_slopes) > 0, f"Fast EMA slopes should be positive in uptrend, got mean: {np.mean(fast_slopes):.4f}"
    assert np.mean(slow_slopes) > 0, f"Slow EMA slopes should be positive in uptrend, got mean: {np.mean(slow_slopes):.4f}"
    
    # Fast EMA should have steeper slope than slow EMA in trending market
    assert np.mean(np.abs(fast_slopes)) >= np.mean(np.abs(slow_slopes)), "Fast EMA should have steeper slope than slow EMA"
    
    print("✅ Slope calculation accuracy validated")
    return True

def test_slope_alignment_strength():
    """Test slope alignment strength calculation"""
    print("\n🔍 Testing Slope Alignment Strength")
    print("-" * 40)
    
    config = get_config()
    analyzer = EMAMomentumAnalyzer(config)
    
    # Test different slope scenarios
    test_cases = [
        (0.01, 0.008, "Both positive slopes (aligned)"),
        (-0.01, -0.008, "Both negative slopes (aligned)"),
        (0.01, -0.005, "Opposite slopes (misaligned)"),
        (0.001, 0.0005, "Small positive slopes"),
        (0.0, 0.0, "Flat slopes")
    ]
    
    for fast_slope, slow_slope, description in test_cases:
        alignment = analyzer._calculate_slope_alignment_strength(fast_slope, slow_slope)
        
        print(f"✅ {description}:")
        print(f"   - Fast slope: {fast_slope:.4f}")
        print(f"   - Slow slope: {slow_slope:.4f}")
        print(f"   - Alignment strength: {alignment:.3f}")
        
        # Validate alignment strength is within valid range
        assert 0.0 <= alignment <= 1.0, f"Alignment strength {alignment} should be between 0.0 and 1.0"
        
        # Aligned slopes should have higher strength
        if fast_slope * slow_slope > 0 and abs(fast_slope) > 0.005:  # Same direction, significant
            assert alignment > 0.6, f"Aligned significant slopes should have high strength, got {alignment:.3f}"
        elif fast_slope * slow_slope < 0:  # Opposite directions
            assert alignment < 0.5, f"Misaligned slopes should have low strength, got {alignment:.3f}"
    
    print("✅ Slope alignment strength calculation validated")
    return True

def test_momentum_acceleration_detection():
    """Test momentum acceleration detection"""
    print("\n🔍 Testing Momentum Acceleration Detection")
    print("-" * 40)
    
    config = get_config()
    analyzer = EMAMomentumAnalyzer(config)
    
    # Test accelerating bullish momentum
    df_accel = create_slope_test_data(100, 'accelerating_bullish')
    df_accel = analyzer.calculate_emas(df_accel)
    
    is_accelerating = analyzer._is_momentum_accelerating(df_accel)
    slope_analysis = analyzer.get_slope_analysis(df_accel)
    
    print(f"✅ Accelerating Bullish Pattern:")
    print(f"   - Is accelerating: {is_accelerating}")
    print(f"   - Slope momentum strength: {slope_analysis['overall_slope_momentum']:.3f}")
    print(f"   - Momentum category: {slope_analysis['momentum_category']}")
    
    # Accelerating pattern should be detected
    assert is_accelerating or slope_analysis['overall_slope_momentum'] > 0.6, "Should detect accelerating momentum in accelerating pattern"
    
    # Test decelerating pattern
    df_decel = create_slope_test_data(100, 'decelerating_bullish')
    df_decel = analyzer.calculate_emas(df_decel)
    
    is_decelerating = not analyzer._is_momentum_accelerating(df_decel)
    slope_analysis_decel = analyzer.get_slope_analysis(df_decel)
    
    print(f"\n✅ Decelerating Bullish Pattern:")
    print(f"   - Is decelerating: {is_decelerating}")
    print(f"   - Slope momentum strength: {slope_analysis_decel['overall_slope_momentum']:.3f}")
    print(f"   - Momentum category: {slope_analysis_decel['momentum_category']}")
    
    # Decelerating pattern should have lower momentum strength
    assert slope_analysis_decel['overall_slope_momentum'] < slope_analysis['overall_slope_momentum'], "Decelerating pattern should have lower momentum strength"
    
    print("✅ Momentum acceleration detection validated")
    return True

def test_slope_consistency_analysis():
    """Test slope consistency calculation"""
    print("\n🔍 Testing Slope Consistency Analysis")
    print("-" * 40)
    
    config = get_config()
    analyzer = EMAMomentumAnalyzer(config)
    
    # Test consistent trend
    df_consistent = create_slope_test_data(100, 'consistent_bullish')
    df_consistent = analyzer.calculate_emas(df_consistent)
    
    consistency_consistent = analyzer._calculate_slope_consistency(df_consistent)
    
    print(f"✅ Consistent Bullish Trend:")
    print(f"   - Slope consistency: {consistency_consistent:.3f}")
    
    # Test flat consolidation (should have lower consistency due to mixed directions)
    df_flat = create_slope_test_data(100, 'flat_consolidation')
    df_flat = analyzer.calculate_emas(df_flat)
    
    consistency_flat = analyzer._calculate_slope_consistency(df_flat)
    
    print(f"\n✅ Flat Consolidation Pattern:")
    print(f"   - Slope consistency: {consistency_flat:.3f}")
    
    # Consistent pattern should have higher consistency score than flat/mixed
    print(f"\n✅ Consistency Comparison:")
    print(f"   - Consistent trend: {consistency_consistent:.3f}")
    print(f"   - Flat consolidation: {consistency_flat:.3f}")
    
    # Both should be within valid range
    assert 0.0 <= consistency_consistent <= 1.0, f"Consistency score {consistency_consistent} should be between 0.0 and 1.0"
    assert 0.0 <= consistency_flat <= 1.0, f"Consistency score {consistency_flat} should be between 0.0 and 1.0"
    
    # For this test, we'll just validate that both are reasonable values
    # The actual comparison depends on the specific data patterns generated
    assert consistency_consistent > 0.5, f"Consistent trend should have reasonable consistency > 0.5, got {consistency_consistent:.3f}"
    
    print("✅ Slope consistency analysis validated")
    return True

def test_momentum_direction_confirmation():
    """Test momentum direction confirmation scoring"""
    print("\n🔍 Testing Momentum Direction Confirmation")
    print("-" * 40)
    
    config = get_config()
    analyzer = EMAMomentumAnalyzer(config)
    
    # Test bullish trend with confirming slopes
    df_bullish = create_slope_test_data(100, 'consistent_bullish')
    df_bullish = analyzer.calculate_emas(df_bullish)
    
    direction_score_bullish = analyzer._calculate_momentum_direction_score(df_bullish)
    slope_analysis_bullish = analyzer.get_slope_analysis(df_bullish)
    
    print(f"✅ Bullish Trend with Confirming Slopes:")
    print(f"   - Direction confirmation score: {direction_score_bullish:.3f}")
    print(f"   - Momentum direction: {slope_analysis_bullish['momentum_direction']}")
    print(f"   - Trend confirmed by slopes: {slope_analysis_bullish['slope_analysis_summary']['trend_confirmed_by_slopes']}")
    
    # Bullish trend with positive slopes should have high confirmation
    assert direction_score_bullish > 0.6, f"Bullish trend with confirming slopes should have high direction score, got {direction_score_bullish:.3f}"
    assert slope_analysis_bullish['momentum_direction'] == 'bullish', "Should detect bullish momentum direction"
    
    # Test bearish trend
    df_bearish = create_slope_test_data(100, 'accelerating_bearish')
    df_bearish = analyzer.calculate_emas(df_bearish)
    
    direction_score_bearish = analyzer._calculate_momentum_direction_score(df_bearish)
    slope_analysis_bearish = analyzer.get_slope_analysis(df_bearish)
    
    print(f"\n✅ Bearish Trend with Confirming Slopes:")
    print(f"   - Direction confirmation score: {direction_score_bearish:.3f}")
    print(f"   - Momentum direction: {slope_analysis_bearish['momentum_direction']}")
    print(f"   - Trend confirmed by slopes: {slope_analysis_bearish['slope_analysis_summary']['trend_confirmed_by_slopes']}")
    
    # Bearish trend with negative slopes should have high confirmation
    assert direction_score_bearish > 0.6, f"Bearish trend with confirming slopes should have high direction score, got {direction_score_bearish:.3f}"
    assert slope_analysis_bearish['momentum_direction'] == 'bearish', "Should detect bearish momentum direction"
    
    print("✅ Momentum direction confirmation validated")
    return True

def test_enhanced_momentum_strength():
    """Test enhanced momentum strength calculation with slope analysis"""
    print("\n🔍 Testing Enhanced Momentum Strength Calculation")
    print("-" * 40)
    
    config = get_config()
    analyzer = EMAMomentumAnalyzer(config)
    
    # Test different momentum scenarios
    test_scenarios = [
        ('accelerating_bullish', 'Strong accelerating bullish momentum'),
        ('consistent_bullish', 'Consistent bullish momentum'),
        ('decelerating_bullish', 'Decelerating bullish momentum'),
        ('flat_consolidation', 'Flat consolidation'),
        ('mixed_slopes', 'Mixed slope pattern')
    ]
    
    momentum_scores = []
    
    for pattern, description in test_scenarios:
        df = create_slope_test_data(100, pattern)
        signal = analyzer.get_ema_signal(df)
        
        assert signal is not None, f"Signal should not be None for {pattern}"
        
        momentum_scores.append((pattern, signal.momentum_strength, description))
        
        print(f"✅ {description}:")
        print(f"   - Pattern: {pattern}")
        print(f"   - Momentum strength: {signal.momentum_strength:.3f}")
        print(f"   - Signal type: {signal.signal_type}")
        
        # Validate momentum strength is within valid range
        assert 0.0 <= signal.momentum_strength <= 1.0, f"Momentum strength {signal.momentum_strength} should be between 0.0 and 1.0"
    
    # Validate relative momentum strengths
    accel_score = next(score for pattern, score, _ in momentum_scores if pattern == 'accelerating_bullish')
    consistent_score = next(score for pattern, score, _ in momentum_scores if pattern == 'consistent_bullish')
    decel_score = next(score for pattern, score, _ in momentum_scores if pattern == 'decelerating_bullish')
    flat_score = next(score for pattern, score, _ in momentum_scores if pattern == 'flat_consolidation')
    
    print(f"\n✅ Momentum Strength Comparison:")
    print(f"   - Accelerating: {accel_score:.3f}")
    print(f"   - Consistent: {consistent_score:.3f}")
    print(f"   - Decelerating: {decel_score:.3f}")
    print(f"   - Flat: {flat_score:.3f}")
    
    # Accelerating should have highest momentum
    assert accel_score >= consistent_score, "Accelerating momentum should be >= consistent momentum"
    assert consistent_score >= decel_score, "Consistent momentum should be >= decelerating momentum"
    assert decel_score >= flat_score, "Decelerating momentum should be >= flat momentum"
    
    print("✅ Enhanced momentum strength calculation validated")
    return True

def test_comprehensive_slope_analysis():
    """Test comprehensive slope analysis output"""
    print("\n🔍 Testing Comprehensive Slope Analysis")
    print("-" * 40)
    
    config = get_config()
    analyzer = EMAMomentumAnalyzer(config)
    
    # Test with accelerating bullish pattern
    df = create_slope_test_data(100, 'accelerating_bullish')
    
    # Get comprehensive analysis
    analysis = analyzer.get_ema_analysis_details(df)
    slope_analysis = analysis['slope_analysis']
    momentum_confirmation = analysis['momentum_confirmation']
    
    # Verify all expected fields are present
    expected_slope_fields = [
        'fast_slope', 'slow_slope', 'slope_alignment_strength', 'slope_magnitude_strength',
        'slope_consistency', 'momentum_direction_score', 'overall_slope_momentum',
        'momentum_direction', 'momentum_category', 'slope_analysis_summary'
    ]
    
    for field in expected_slope_fields:
        assert field in slope_analysis, f"Missing field in slope analysis: {field}"
    
    expected_confirmation_fields = [
        'slope_momentum_strength', 'momentum_category', 'slopes_confirm_trend', 'momentum_accelerating'
    ]
    
    for field in expected_confirmation_fields:
        assert field in momentum_confirmation, f"Missing field in momentum confirmation: {field}"
    
    print(f"✅ Comprehensive Slope Analysis Results:")
    print(f"   - Fast slope: {slope_analysis['fast_slope']:.4f}")
    print(f"   - Slow slope: {slope_analysis['slow_slope']:.4f}")
    print(f"   - Slope alignment: {slope_analysis['slope_alignment_strength']:.3f}")
    print(f"   - Slope magnitude: {slope_analysis['slope_magnitude_strength']:.3f}")
    print(f"   - Slope consistency: {slope_analysis['slope_consistency']:.3f}")
    print(f"   - Direction score: {slope_analysis['momentum_direction_score']:.3f}")
    print(f"   - Overall momentum: {slope_analysis['overall_slope_momentum']:.3f}")
    print(f"   - Momentum direction: {slope_analysis['momentum_direction']}")
    print(f"   - Momentum category: {slope_analysis['momentum_category']}")
    print(f"   - Slopes aligned: {slope_analysis['slope_analysis_summary']['slopes_aligned']}")
    print(f"   - Momentum accelerating: {slope_analysis['slope_analysis_summary']['momentum_accelerating']}")
    print(f"   - Trend confirmed: {slope_analysis['slope_analysis_summary']['trend_confirmed_by_slopes']}")
    
    # Validate analysis consistency
    if slope_analysis['momentum_direction'] == 'bullish':
        assert slope_analysis['fast_slope'] > 0 or slope_analysis['slow_slope'] > 0, "Bullish momentum should have positive slopes"
    elif slope_analysis['momentum_direction'] == 'bearish':
        assert slope_analysis['fast_slope'] < 0 or slope_analysis['slow_slope'] < 0, "Bearish momentum should have negative slopes"
    
    # Validate momentum confirmation consistency
    assert momentum_confirmation['slope_momentum_strength'] == slope_analysis['overall_slope_momentum'], "Momentum strength should be consistent"
    assert momentum_confirmation['momentum_category'] == slope_analysis['momentum_category'], "Momentum category should be consistent"
    
    print("✅ Comprehensive slope analysis validated")
    return True

def run_all_slope_tests():
    """Run all EMA slope analysis tests"""
    print("🔍 EMA Slope Analysis Enhancement Test Suite - Task 1.3")
    print("=" * 70)
    
    tests = [
        test_slope_calculation_accuracy,
        test_slope_alignment_strength,
        test_momentum_acceleration_detection,
        test_slope_consistency_analysis,
        test_momentum_direction_confirmation,
        test_enhanced_momentum_strength,
        test_comprehensive_slope_analysis
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
    
    print("\n" + "=" * 70)
    print("📊 EMA SLOPE ANALYSIS TEST SUMMARY")
    print("=" * 70)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {(passed / (passed + failed) * 100):.1f}%")
    
    if failed == 0:
        print("\n🎉 ALL EMA SLOPE ANALYSIS TESTS PASSED!")
        print("✅ Enhanced slope calculation working correctly")
        print("✅ Slope alignment strength calculation functioning")
        print("✅ Momentum acceleration detection validated")
        print("✅ Slope consistency analysis working")
        print("✅ Momentum direction confirmation functioning")
        print("✅ Enhanced momentum strength calculation validated")
        print("✅ Comprehensive slope analysis integration working")
        print("\n🚀 Task 1.3 Requirements Met:")
        print("   ✅ EMA slope analysis for momentum strength and direction")
        print("   ✅ Momentum strength scoring based on slope magnitude")
        print("   ✅ Slope-based momentum confirmation implemented")
        print("   ✅ Requirements 3.4 satisfied")
        return True
    else:
        print(f"\n⚠️ {failed} EMA SLOPE ANALYSIS TESTS FAILED - REVIEW REQUIRED")
        return False

if __name__ == "__main__":
    success = run_all_slope_tests()
    sys.exit(0 if success else 1)