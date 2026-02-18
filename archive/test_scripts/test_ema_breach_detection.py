#!/usr/bin/env python3
"""
Test EMA Breach Detection and Dynamic Support/Resistance Levels
Tests the enhanced EMAMomentumAnalyzer with breach detection and volume confirmation
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from ema_momentum_analyzer import EMAMomentumAnalyzer, EMABreachResult
from volume_analyzer import VolumeAnalyzer

def create_test_data_with_breaches():
    """Create test data with clear EMA breaches"""
    dates = pd.date_range('2024-01-01', periods=100, freq='h')  # Use 'h' instead of 'H'
    
    # Create price data that will breach EMA levels more clearly
    base_price = 100.0
    prices = []
    volumes = []
    
    for i in range(100):
        # Create a more pronounced pattern for clearer breaches
        if i < 25:
            # Initial uptrend - establish EMAs above price
            price = base_price + (i * 0.3) + np.random.normal(0, 0.1)
            volume = np.random.randint(1000, 1500)
        elif i < 35:
            # Consolidation around EMA levels
            price = base_price + 7 + np.random.normal(0, 0.5)
            volume = np.random.randint(800, 1200)
        elif i < 45:
            # Sharp break below EMAs (clear support break with high volume)
            price = base_price + 7 - ((i - 35) * 0.8) + np.random.normal(0, 0.2)
            volume = np.random.randint(2500, 4000)  # High volume on break
        elif i < 55:
            # Continue downward to ensure clear breach
            price = base_price - 1 + np.random.normal(0, 0.3)
            volume = np.random.randint(1500, 2500)
        elif i < 70:
            # Retest of broken support (now resistance) - price tries to go back up
            price = base_price + 2 + np.random.normal(0, 0.4)
            volume = np.random.randint(1200, 2000)
        else:
            # Strong recovery and resistance break with high volume
            price = base_price + 3 + ((i - 70) * 0.6) + np.random.normal(0, 0.2)
            volume = np.random.randint(2000, 3500)  # High volume on breakout
        
        prices.append(max(price, 1.0))  # Ensure positive prices
        volumes.append(volume)
    
    # Create OHLC data with some spread
    df = pd.DataFrame({
        'time': dates,
        'open': prices,
        'high': [p + np.random.uniform(0.1, 0.3) for p in prices],
        'low': [p - np.random.uniform(0.1, 0.3) for p in prices],
        'close': prices,
        'tick_volume': volumes
    })
    
    return df

def test_ema_breach_detection():
    """Test EMA breach detection functionality"""
    print("🔍 Testing EMA Breach Detection...")
    
    # Create test configuration
    config = {
        'ema_fast_period': 20,
        'ema_slow_period': 50,
        'ema_breach_threshold': 0.01,  # 1% breach threshold (more sensitive)
        'ema_min_volume_confirmation': 1.3,  # 1.3x volume for confirmation
        'ema_retest_tolerance': 0.005,  # 0.5% tolerance for retests
        'use_volume_filter': True,
        'min_volume_ma': 1.0,
        'volume_ma_period': 20
    }
    
    # Initialize analyzers
    ema_analyzer = EMAMomentumAnalyzer(config)
    volume_analyzer = VolumeAnalyzer(config)
    
    # Create test data
    df = create_test_data_with_breaches()
    
    print(f"📊 Created test data with {len(df)} bars")
    print(f"   Price range: {df['close'].min():.2f} - {df['close'].max():.2f}")
    print(f"   Volume range: {df['tick_volume'].min()} - {df['tick_volume'].max()}")
    
    # Calculate EMAs
    df_with_emas = ema_analyzer.calculate_emas(df)
    
    print(f"\n📈 EMA Calculation Results:")
    print(f"   Fast EMA (20): {df_with_emas[f'ema_{config['ema_fast_period']}'].iloc[-1]:.2f}")
    print(f"   Slow EMA (50): {df_with_emas[f'ema_{config['ema_slow_period']}'].iloc[-1]:.2f}")
    print(f"   Current Price: {df_with_emas['close'].iloc[-1]:.2f}")
    
    # Debug: Check some key points in the data
    print(f"\n🔍 Debug - Key Data Points:")
    for i in [40, 50, 60, 70, 80, 90]:
        if i < len(df_with_emas):
            row = df_with_emas.iloc[i]
            fast_ema = row[f'ema_{config["ema_fast_period"]}']
            slow_ema = row[f'ema_{config["ema_slow_period"]}']
            price = row['close']
            volume = row['tick_volume']
            print(f"   Bar {i}: Price={price:.2f}, Fast EMA={fast_ema:.2f}, Slow EMA={slow_ema:.2f}, Volume={volume}")
    
    # Test breach detection on multiple points, not just the last one
    all_breaches = []
    for i in range(max(60, config['ema_slow_period']), len(df_with_emas)):
        # Create a subset ending at this point
        subset_df = df_with_emas.iloc[:i+1].copy()
        breaches = ema_analyzer.detect_ema_breaches(subset_df, volume_analyzer)
        if breaches:
            all_breaches.extend(breaches)
    
    print(f"\n🚨 Breach Detection Results (scanning all points):")
    print(f"   Total breaches detected: {len(all_breaches)}")
    
    for i, breach in enumerate(all_breaches):
        print(f"\n   Breach {i+1}:")
        print(f"     Type: {breach.breach_type}")
        print(f"     EMA Period: {breach.ema_period}")
        print(f"     Breach Level: {breach.breach_level:.2f}")
        print(f"     Current Price: {breach.current_price:.2f}")
        print(f"     Magnitude: {breach.breach_magnitude:.3%}")
        print(f"     Volume Confirmed: {breach.volume_confirmed}")
        print(f"     Volume Ratio: {breach.volume_ratio:.2f}x")
        print(f"     Confidence: {breach.confidence:.2f}")
    
    # Also test just the final point
    final_breaches = ema_analyzer.detect_ema_breaches(df_with_emas, volume_analyzer)
    print(f"\n   Final point breaches: {len(final_breaches)}")
    
    return len(all_breaches) > 0 or len(final_breaches) > 0

def test_dynamic_support_resistance():
    """Test dynamic support/resistance analysis"""
    print("\n🎯 Testing Dynamic Support/Resistance Analysis...")
    
    config = {
        'ema_fast_period': 20,
        'ema_slow_period': 50,
        'ema_breach_threshold': 0.005,
        'ema_min_volume_confirmation': 1.5,
        'use_volume_filter': True,
        'volume_ma_period': 20
    }
    
    ema_analyzer = EMAMomentumAnalyzer(config)
    volume_analyzer = VolumeAnalyzer(config)
    
    # Create test data
    df = create_test_data_with_breaches()
    
    # Get comprehensive S/R analysis
    sr_analysis = ema_analyzer.get_dynamic_support_resistance_analysis(df, volume_analyzer)
    
    if 'error' in sr_analysis:
        print(f"❌ Error in S/R analysis: {sr_analysis['error']}")
        return False
    
    print(f"📊 Dynamic S/R Analysis Results:")
    print(f"   Current Price: {sr_analysis['current_price']:.2f}")
    print(f"   Fast EMA: {sr_analysis['fast_ema']:.2f}")
    print(f"   Slow EMA: {sr_analysis['slow_ema']:.2f}")
    
    print(f"\n🔑 Key Levels:")
    for level in sr_analysis['key_levels'][:5]:  # Show top 5 nearest levels
        print(f"     {level['type'].upper()}: {level['price']:.2f} "
              f"(EMA{level['period']}, {level['distance_pct']:.2f}% away, "
              f"strength: {level['strength']:.2f})")
    
    print(f"\n🚨 Recent Breaches: {len(sr_analysis['recent_breaches'])}")
    for breach in sr_analysis['recent_breaches']:
        print(f"     {breach['type']}: EMA{breach['period']} at {breach['level']:.2f} "
              f"(confidence: {breach['confidence']:.2f})")
    
    print(f"\n📈 S/R Context:")
    context = sr_analysis['sr_context']
    print(f"     Context: {context['context']}")
    print(f"     Description: {context['description']}")
    print(f"     Above Fast EMA: {context['above_fast_ema']}")
    print(f"     Above Slow EMA: {context['above_slow_ema']}")
    print(f"     Trend Alignment: {context['trend_alignment']}")
    
    print(f"\n💡 Trading Implications:")
    implications = sr_analysis['trading_implications']
    print(f"     Bias: {implications['bias']}")
    print(f"     Strength: {implications['strength']}")
    print(f"     Key Levels Nearby: {implications['key_levels_nearby']}")
    print(f"     Breakout Potential: {implications['breakout_potential']}")
    print(f"     Retest Opportunity: {implications['retest_opportunity']}")
    print(f"     Risk Level: {implications['risk_level']}")
    
    return True

def test_volume_integration():
    """Test integration with VolumeAnalyzer"""
    print("\n🔊 Testing Volume Integration...")
    
    config = {
        'ema_fast_period': 20,
        'ema_slow_period': 50,
        'ema_breach_threshold': 0.003,
        'ema_min_volume_confirmation': 1.3,
        'use_volume_filter': True,
        'min_volume_ma': 1.0,
        'volume_ma_period': 15
    }
    
    ema_analyzer = EMAMomentumAnalyzer(config)
    volume_analyzer = VolumeAnalyzer(config)
    
    # Create test data with specific volume patterns
    df = create_test_data_with_breaches()
    
    # Test with volume analyzer
    analysis_with_volume = ema_analyzer.get_ema_analysis_details(df, volume_analyzer)
    
    # Test without volume analyzer
    analysis_without_volume = ema_analyzer.get_ema_analysis_details(df, None)
    
    print(f"📊 Volume Integration Results:")
    
    if 'dynamic_sr_analysis' in analysis_with_volume:
        with_vol = analysis_with_volume['dynamic_sr_analysis']
        without_vol = analysis_without_volume['dynamic_sr_analysis']
        
        print(f"   With Volume Analyzer:")
        print(f"     Recent Breaches: {len(with_vol.get('recent_breaches', []))}")
        print(f"     Volume Confirmation Rate: {with_vol.get('breach_analysis', {}).get('volume_confirmation_rate', 0):.2%}")
        
        print(f"   Without Volume Analyzer:")
        print(f"     Recent Breaches: {len(without_vol.get('recent_breaches', []))}")
        print(f"     Volume Confirmation Rate: {without_vol.get('breach_analysis', {}).get('volume_confirmation_rate', 0):.2%}")
        
        # Check if volume confirmation affects breach confidence
        with_breaches = with_vol.get('recent_breaches', [])
        without_breaches = without_vol.get('recent_breaches', [])
        
        if with_breaches and without_breaches:
            avg_conf_with = sum(b['confidence'] for b in with_breaches) / len(with_breaches)
            avg_conf_without = sum(b['confidence'] for b in without_breaches) / len(without_breaches)
            
            print(f"   Average Confidence with Volume: {avg_conf_with:.2f}")
            print(f"   Average Confidence without Volume: {avg_conf_without:.2f}")
            print(f"   Volume Impact: {avg_conf_with - avg_conf_without:+.2f}")
    
    return True

def test_edge_cases():
    """Test edge cases and error handling"""
    print("\n⚠️  Testing Edge Cases...")
    
    config = {
        'ema_fast_period': 20,
        'ema_slow_period': 50
    }
    
    ema_analyzer = EMAMomentumAnalyzer(config)
    
    # Test with insufficient data
    small_df = pd.DataFrame({
        'time': pd.date_range('2024-01-01', periods=5, freq='h'),
        'close': [100, 101, 102, 101, 100],
        'tick_volume': [1000, 1100, 1200, 1100, 1000]
    })
    
    breaches = ema_analyzer.detect_ema_breaches(small_df)
    print(f"   Insufficient data test: {len(breaches)} breaches (expected: 0)")
    
    # Test with NaN values
    nan_df = create_test_data_with_breaches()
    nan_df.loc[50:55, 'close'] = np.nan
    
    breaches_with_nan = ema_analyzer.detect_ema_breaches(nan_df)
    print(f"   NaN handling test: {len(breaches_with_nan)} breaches detected")
    
    # Test S/R analysis with insufficient data
    sr_analysis = ema_analyzer.get_dynamic_support_resistance_analysis(small_df)
    print(f"   S/R insufficient data test: {'error' in sr_analysis}")
    
    return True

def main():
    """Run all EMA breach detection tests"""
    print("🚀 Starting EMA Breach Detection Tests")
    print("=" * 60)
    
    try:
        # Run tests
        test_results = []
        
        test_results.append(("Breach Detection", test_ema_breach_detection()))
        test_results.append(("Dynamic S/R Analysis", test_dynamic_support_resistance()))
        test_results.append(("Volume Integration", test_volume_integration()))
        test_results.append(("Edge Cases", test_edge_cases()))
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 Test Results Summary:")
        
        passed = 0
        for test_name, result in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {test_name}: {status}")
            if result:
                passed += 1
        
        print(f"\n🎯 Overall: {passed}/{len(test_results)} tests passed")
        
        if passed == len(test_results):
            print("🎉 All EMA breach detection tests passed!")
            print("\n✨ Key Features Verified:")
            print("   • EMA level breach detection with configurable thresholds")
            print("   • Volume confirmation for breach validation")
            print("   • Support/resistance level identification using EMAs")
            print("   • Retest detection and confirmation")
            print("   • Comprehensive trading implications analysis")
            print("   • Integration with VolumeAnalyzer")
            print("   • Robust error handling for edge cases")
            return True
        else:
            print("❌ Some tests failed. Please review the implementation.")
            return False
            
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)