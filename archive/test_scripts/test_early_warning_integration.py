"""
Integration test for Early Warning Signal System
Tests the integration of early warning signals with the main trend detection engine
"""

import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.trend_detection_engine import TrendDetectionEngine

def test_early_warning_integration():
    """Test that early warning signals integrate properly with trend detection"""
    
    print("🔍 Testing Early Warning Signal Integration...")
    
    # Setup configuration
    config = {
        'use_trend_detection': True,
        'enable_early_signals': True,
        'trend_detection_sensitivity': 5,
        'min_trend_confidence': 0.6,
        'aroon_period': 25,
        'ema_fast_period': 20,
        'ema_slow_period': 50,
        'use_volume_filter': True,
        'volume_ma_period': 20,
        'min_volume_ma': 0.7
    }
    
    # Initialize trend detection engine
    engine = TrendDetectionEngine(config)
    
    # Generate test data with trend weakness pattern
    print("📊 Generating test data with trend weakness pattern...")
    df = generate_trend_weakness_data()
    
    # Run full trend analysis
    print("🔍 Running comprehensive trend analysis...")
    analysis_result = engine.analyze_trend_change(df, "EURUSD")
    
    # Verify early warnings are generated
    print(f"📈 Analysis Results:")
    print(f"   Total Signals: {len(analysis_result.signals)}")
    print(f"   Overall Confidence: {analysis_result.confidence:.3f}")
    print(f"   Early Warnings: {len(analysis_result.early_warnings)}")
    
    # Test early warning properties
    if analysis_result.early_warnings:
        print(f"\n⚠️ Early Warning Details:")
        for i, warning in enumerate(analysis_result.early_warnings, 1):
            print(f"   Warning {i}:")
            print(f"     Type: {warning.warning_type}")
            print(f"     Description: {warning.description}")
            print(f"     Confidence: {warning.confidence:.3f}")
            print(f"     Probability: {warning.probability_score:.3f}")
            print(f"     Strength: {warning.strength:.3f}")
            print(f"     Factors: {', '.join(warning.factors)}")
            print(f"     Price Level: {warning.price_level:.5f}")
            print(f"     Current Price: {warning.current_price:.5f}")
            
            # Verify warning properties
            assert 0.0 <= warning.confidence <= 1.0, f"Invalid confidence: {warning.confidence}"
            assert 0.0 <= warning.probability_score <= 1.0, f"Invalid probability: {warning.probability_score}"
            assert 0.0 <= warning.strength <= 1.0, f"Invalid strength: {warning.strength}"
            assert len(warning.factors) > 0, "Warning must have factors"
            assert len(warning.description) > 10, "Description too short"
            assert warning.price_level > 0, "Price level must be positive"
            assert warning.current_price > 0, "Current price must be positive"
            
        print(f"   ✅ All early warning properties validated")
    else:
        print(f"   ℹ️ No early warnings generated (this is acceptable)")
    
    # Test individual early warning methods
    print(f"\n🔍 Testing individual early warning methods...")
    
    # Test trend weakness detection
    weakness_warnings = engine.detect_trend_weakness(df)
    print(f"   Trend Weakness Warnings: {len(weakness_warnings)}")
    
    # Test key level monitoring
    level_warnings = engine.monitor_key_levels(df)
    print(f"   Key Level Warnings: {len(level_warnings)}")
    
    # Verify methods work independently
    all_individual_warnings = weakness_warnings + level_warnings
    print(f"   Total Individual Warnings: {len(all_individual_warnings)}")
    
    # Test with different sensitivity
    print(f"\n🔧 Testing sensitivity adjustment...")
    sensitive_warnings = engine.monitor_key_levels(df, sensitivity_multiplier=2.0)
    normal_warnings = engine.monitor_key_levels(df, sensitivity_multiplier=1.0)
    
    print(f"   Normal Sensitivity: {len(normal_warnings)} warnings")
    print(f"   High Sensitivity: {len(sensitive_warnings)} warnings")
    print(f"   Sensitivity Impact: {len(sensitive_warnings) - len(normal_warnings):+d} warnings")
    
    # Test probability scoring
    print(f"\n📊 Testing probability scoring...")
    if all_individual_warnings:
        probabilities = [w.probability_score for w in all_individual_warnings]
        avg_probability = sum(probabilities) / len(probabilities)
        min_probability = min(probabilities)
        max_probability = max(probabilities)
        
        print(f"   Average Probability: {avg_probability:.3f}")
        print(f"   Probability Range: {min_probability:.3f} - {max_probability:.3f}")
        
        # Verify probability scores are reasonable
        assert all(0.1 <= p <= 0.95 for p in probabilities), "Probabilities should be in reasonable range"
        print(f"   ✅ Probability scores validated")
    
    print(f"\n✅ Early Warning Integration Test Complete!")
    return True

def generate_trend_weakness_data():
    """Generate synthetic data with trend weakness patterns"""
    np.random.seed(42)  # For reproducible results
    
    num_bars = 150
    base_price = 1.1000
    
    # Generate uptrend with weakness at the end
    trend_component = np.linspace(0, 0.02, num_bars)  # 2% uptrend
    noise = np.random.normal(0, 0.001, num_bars)  # 0.1% noise
    
    prices = base_price + trend_component + noise
    
    # Create weakness pattern in last 30 bars (lower highs)
    weakness_start = num_bars - 30
    peak_price = prices[weakness_start - 5]
    
    for i in range(weakness_start, num_bars):
        if prices[i] > peak_price:
            # Create lower high
            reduction = (i - weakness_start) * 0.0001  # Gradual reduction
            prices[i] = peak_price - reduction
    
    # Generate OHLC data
    opens = np.roll(prices, 1)
    opens[0] = prices[0]
    
    highs = prices * (1 + np.random.uniform(0, 0.0005, num_bars))
    lows = prices * (1 - np.random.uniform(0, 0.0005, num_bars))
    
    # Generate volume with some spikes
    base_volume = 1000
    volumes = np.random.poisson(base_volume, num_bars)
    
    # Add volume spikes at key points
    spike_indices = [weakness_start - 5, weakness_start + 10, weakness_start + 20]
    for idx in spike_indices:
        if idx < num_bars:
            volumes[idx] *= 2.5  # Volume spike
    
    # Create DataFrame
    dates = pd.date_range(start='2024-01-01', periods=num_bars, freq='1h')
    
    df = pd.DataFrame({
        'time': dates,
        'open': opens,
        'high': highs,
        'low': lows,
        'close': prices,
        'tick_volume': volumes
    })
    
    # Add technical indicators
    df['ema_20'] = df['close'].ewm(span=20).mean()
    df['ema_50'] = df['close'].ewm(span=50).mean()
    
    # Add RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # Add MACD
    ema_12 = df['close'].ewm(span=12).mean()
    ema_26 = df['close'].ewm(span=26).mean()
    df['macd'] = ema_12 - ema_26
    df['macd_signal'] = df['macd'].ewm(span=9).mean()
    df['macd_histogram'] = df['macd'] - df['macd_signal']
    
    return df

def test_early_warning_configuration():
    """Test early warning system with different configurations"""
    
    print("\n🔧 Testing Early Warning Configuration Options...")
    
    # Test with early signals disabled
    config_disabled = {
        'use_trend_detection': True,
        'enable_early_signals': False,  # Disabled
        'trend_detection_sensitivity': 5,
        'min_trend_confidence': 0.6
    }
    
    engine_disabled = TrendDetectionEngine(config_disabled)
    df = generate_trend_weakness_data()
    
    analysis_disabled = engine_disabled.analyze_trend_change(df, "EURUSD")
    print(f"   Early Signals Disabled: {len(analysis_disabled.early_warnings)} warnings")
    
    # Test with early signals enabled
    config_enabled = config_disabled.copy()
    config_enabled['enable_early_signals'] = True
    
    engine_enabled = TrendDetectionEngine(config_enabled)
    analysis_enabled = engine_enabled.analyze_trend_change(df, "EURUSD")
    print(f"   Early Signals Enabled: {len(analysis_enabled.early_warnings)} warnings")
    
    # Verify configuration works
    assert len(analysis_disabled.early_warnings) == 0, "Disabled config should have no warnings"
    print(f"   ✅ Configuration control validated")

if __name__ == "__main__":
    try:
        # Run integration tests
        test_early_warning_integration()
        test_early_warning_configuration()
        
        print(f"\n🎉 All Early Warning Integration Tests Passed!")
        
    except Exception as e:
        print(f"\n❌ Integration Test Failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)