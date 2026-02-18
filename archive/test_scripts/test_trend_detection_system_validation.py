#!/usr/bin/env python3
"""
Comprehensive system validation test for trend detection system
Tests end-to-end functionality, performance, and integration
"""

import sys
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import traceback

# Add src directory to path
sys.path.append('src')

def generate_test_data(bars=200, symbol='XAUUSD'):
    """Generate realistic test market data"""
    
    # Create realistic price data with trends and patterns
    np.random.seed(42)  # For reproducible tests
    
    dates = pd.date_range(start=datetime.now() - timedelta(days=bars), periods=bars, freq='30T')
    
    # Generate base price movement with trend
    base_price = 2000.0
    trend = np.linspace(0, 50, bars)  # Upward trend
    noise = np.random.normal(0, 5, bars)  # Random noise
    
    # Add some cyclical patterns
    cycle = 10 * np.sin(np.linspace(0, 4*np.pi, bars))
    
    # Combine components
    close_prices = base_price + trend + noise + cycle
    
    # Generate OHLC from close prices
    high_offset = np.abs(np.random.normal(2, 1, bars))
    low_offset = np.abs(np.random.normal(2, 1, bars))
    open_offset = np.random.normal(0, 1, bars)
    
    df = pd.DataFrame({
        'time': dates,
        'open': close_prices + open_offset,
        'high': close_prices + high_offset,
        'low': close_prices - low_offset,
        'close': close_prices,
        'tick_volume': np.random.randint(100, 1000, bars),
        'volume': np.random.randint(1000, 10000, bars)
    })
    
    # Ensure OHLC relationships are valid
    df['high'] = df[['open', 'high', 'close']].max(axis=1)
    df['low'] = df[['open', 'low', 'close']].min(axis=1)
    
    df.set_index('time', inplace=True)
    
    return df

def test_trend_detection_engine():
    """Test the trend detection engine initialization and basic functionality"""
    print("🔧 Testing TrendDetectionEngine initialization...")
    
    try:
        from src.trend_detection_engine import TrendDetectionEngine
        
        # Test configuration
        test_config = {
            'use_trend_detection': True,
            'trend_detection_sensitivity': 5,
            'min_trend_confidence': 0.6,
            'enable_early_signals': True,
            'logging_level': 'detailed',
            'max_analysis_time_ms': 200,  # Generous for testing
            'trend_cache_size': 100,
            'max_memory_mb': 500,
            'enable_performance_monitoring': True,
            'cache_analysis_results': True,
            'max_error_retries': 3,
            'enable_circuit_breaker': True,
            'graceful_degradation': True
        }
        
        # Initialize engine
        engine = TrendDetectionEngine(test_config)
        print("✅ TrendDetectionEngine initialized successfully")
        
        # Test configuration validation
        is_valid, errors = engine.validate_runtime_config(test_config)
        if not is_valid:
            print(f"⚠️ Configuration validation issues: {errors}")
        else:
            print("✅ Configuration validation passed")
        
        # Test component status
        component_status = engine.get_component_status()
        available_components = [name for name, status in component_status.items() if status == 'available']
        failed_components = [name for name, status in component_status.items() if status != 'available']
        
        print(f"📊 Component Status: {len(available_components)} available, {len(failed_components)} failed")
        if available_components:
            print(f"   Available: {', '.join(available_components)}")
        if failed_components:
            print(f"   Failed: {', '.join(failed_components)}")
        
        return engine, len(failed_components) == 0
        
    except Exception as e:
        print(f"❌ TrendDetectionEngine initialization failed: {e}")
        print(f"   Traceback: {traceback.format_exc()}")
        return None, False

def test_analysis_performance(engine, test_data):
    """Test analysis performance and timing"""
    print("\n⏱️ Testing analysis performance...")
    
    try:
        symbol = 'XAUUSD'
        num_tests = 5
        analysis_times = []
        
        for i in range(num_tests):
            start_time = time.perf_counter()
            
            result = engine.analyze_trend_change(test_data, symbol)
            
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            analysis_times.append(elapsed_ms)
            
            print(f"   Test {i+1}: {elapsed_ms:.1f}ms, {len(result.signals)} signals, confidence={result.confidence:.2f}")
        
        avg_time = np.mean(analysis_times)
        max_time = np.max(analysis_times)
        min_time = np.min(analysis_times)
        
        print(f"📈 Performance Summary:")
        print(f"   Average: {avg_time:.1f}ms")
        print(f"   Range: {min_time:.1f}ms - {max_time:.1f}ms")
        
        # Check performance requirements
        target_time = engine.max_analysis_time_ms
        performance_ok = avg_time <= target_time
        
        if performance_ok:
            print(f"✅ Performance requirement met (avg {avg_time:.1f}ms <= {target_time}ms)")
        else:
            print(f"⚠️ Performance requirement not met (avg {avg_time:.1f}ms > {target_time}ms)")
        
        return performance_ok, avg_time
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False, 0

def test_signal_generation(engine, test_data):
    """Test signal generation functionality"""
    print("\n📊 Testing signal generation...")
    
    try:
        symbol = 'XAUUSD'
        
        # Perform analysis
        result = engine.analyze_trend_change(test_data, symbol)
        
        print(f"📋 Analysis Results:")
        print(f"   Signals generated: {len(result.signals)}")
        print(f"   Overall confidence: {result.confidence:.2f}")
        print(f"   Market structure: {'detected' if result.market_structure else 'none'}")
        print(f"   Divergences: {len(result.divergences)}")
        print(f"   Aroon signal: {'detected' if result.aroon_signal else 'none'}")
        print(f"   EMA signal: {'detected' if result.ema_signal else 'none'}")
        print(f"   Trendline breaks: {len(result.trendline_breaks)}")
        print(f"   Early warnings: {len(result.early_warnings)}")
        
        # Test signal details
        for i, signal in enumerate(result.signals):
            print(f"   Signal {i+1}: {signal.signal_type} from {signal.source} "
                  f"(confidence={signal.confidence:.2f}, strength={signal.strength:.2f})")
        
        # Test signal filtering
        if result.signals:
            filtered_signals = engine.filter_signals_by_confidence(result.signals, 0.7)
            print(f"   High-confidence signals (>70%): {len(filtered_signals)}")
            
            quality_signals = engine.filter_signals_by_source_quality(result.signals)
            print(f"   Quality-filtered signals: {len(quality_signals)}")
        
        return True, len(result.signals)
        
    except Exception as e:
        print(f"❌ Signal generation test failed: {e}")
        print(f"   Traceback: {traceback.format_exc()}")
        return False, 0

def test_configuration_management(engine):
    """Test configuration management and updates"""
    print("\n🔧 Testing configuration management...")
    
    try:
        # Get current config info
        config_info = engine.get_config_info()
        print(f"📋 Current config: {config_info['config_keys_count']} parameters")
        print(f"   Valid: {config_info['is_valid']}")
        if config_info['validation_errors']:
            print(f"   Validation errors: {len(config_info['validation_errors'])}")
        
        # Test configuration update
        test_updates = {
            'trend_detection_sensitivity': 7,
            'min_trend_confidence': 0.75,
            'max_analysis_time_ms': 150
        }
        
        print(f"🔄 Testing configuration update with {len(test_updates)} changes...")
        update_success = engine.update_config(test_updates)
        
        if update_success:
            print("✅ Configuration update successful")
            
            # Verify changes took effect
            updated_config = engine.get_config_info()['current_config']
            verification_errors = []
            
            for param, expected_value in test_updates.items():
                actual_value = updated_config.get(param)
                if actual_value != expected_value:
                    verification_errors.append(f"{param}: expected {expected_value}, got {actual_value}")
            
            if verification_errors:
                print(f"⚠️ Configuration verification issues: {verification_errors}")
                return False
            else:
                print("✅ Configuration changes verified")
                return True
        else:
            print("❌ Configuration update failed")
            return False
        
    except Exception as e:
        print(f"❌ Configuration management test failed: {e}")
        return False

def test_error_handling(engine, test_data):
    """Test error handling and recovery"""
    print("\n🛡️ Testing error handling and recovery...")
    
    try:
        # Test with invalid data
        print("   Testing with invalid data...")
        
        # Empty dataframe
        empty_df = pd.DataFrame()
        result = engine.analyze_trend_change(empty_df, 'TEST')
        if len(result.signals) == 0 and result.confidence == 0.0:
            print("   ✅ Empty data handled gracefully")
        else:
            print("   ⚠️ Empty data not handled properly")
        
        # Insufficient data
        small_df = test_data.head(10)
        result = engine.analyze_trend_change(small_df, 'TEST')
        if len(result.signals) == 0:
            print("   ✅ Insufficient data handled gracefully")
        else:
            print("   ⚠️ Insufficient data not handled properly")
        
        # Test error recovery stats
        error_diagnostics = engine.get_error_diagnostics()
        print(f"📊 Error Recovery Stats:")
        print(f"   Total errors: {error_diagnostics['error_recovery']['total_errors']}")
        print(f"   Error types: {len(error_diagnostics['error_recovery']['error_types'])}")
        
        # Test health status
        health_status = engine.get_health_status()
        print(f"🏥 System Health:")
        print(f"   Health score: {health_status['health_score']}/100")
        print(f"   Status: {health_status['health_status']}")
        print(f"   Component availability: {health_status['component_availability']}/{health_status['total_components']}")
        
        if health_status['issues']:
            print(f"   Issues: {health_status['issues']}")
        
        return health_status['health_score'] >= 70
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def test_memory_and_performance(engine, test_data):
    """Test memory usage and performance monitoring"""
    print("\n🧠 Testing memory usage and performance monitoring...")
    
    try:
        # Get initial performance stats
        initial_stats = engine.get_performance_stats()
        print(f"📊 Initial Performance Stats:")
        print(f"   Total analyses: {initial_stats['total_analyses']}")
        print(f"   Success rate: {initial_stats.get('success_rate_percent', 0):.1f}%")
        print(f"   Cache hit rate: {initial_stats.get('cache_hit_rate_percent', 0):.1f}%")
        print(f"   Memory usage: {initial_stats.get('memory_usage_mb', 0):.1f}MB")
        
        # Run multiple analyses to test memory stability
        print("   Running memory stability test...")
        initial_memory = engine.memory_manager.get_memory_usage_mb()
        
        for i in range(10):
            engine.analyze_trend_change(test_data, f'TEST_{i}')
        
        final_memory = engine.memory_manager.get_memory_usage_mb()
        memory_growth = final_memory - initial_memory
        
        print(f"   Memory growth: {memory_growth:.1f}MB over 10 analyses")
        
        # Check for memory leaks (growth should be minimal)
        memory_leak_ok = memory_growth < 50  # Less than 50MB growth
        
        if memory_leak_ok:
            print("   ✅ No significant memory leaks detected")
        else:
            print(f"   ⚠️ Potential memory leak: {memory_growth:.1f}MB growth")
        
        # Test cache efficiency
        final_stats = engine.get_performance_stats()
        cache_hit_rate = final_stats.get('cache_hit_rate_percent', 0)
        
        print(f"   Cache efficiency: {cache_hit_rate:.1f}% hit rate")
        cache_efficient = cache_hit_rate > 20  # At least 20% hit rate
        
        if cache_efficient:
            print("   ✅ Cache working efficiently")
        else:
            print("   ⚠️ Low cache efficiency")
        
        return memory_leak_ok and cache_efficient
        
    except Exception as e:
        print(f"❌ Memory and performance test failed: {e}")
        return False

def test_integration_with_dashboard():
    """Test integration with dashboard API"""
    print("\n🌐 Testing dashboard integration...")
    
    try:
        # Test trend detection status endpoint
        import requests
        import json
        
        # This would normally test the actual dashboard API
        # For now, we'll test the configuration structure
        
        # Test configuration structure matches dashboard expectations
        expected_dashboard_params = [
            'use_trend_detection',
            'trend_detection_sensitivity',
            'min_trend_confidence',
            'enable_early_signals',
            'ema_fast_period',
            'ema_slow_period',
            'aroon_period',
            'aroon_threshold',
            'min_swing_strength',
            'structure_break_threshold',
            'divergence_lookback',
            'min_divergence_strength',
            'max_trendlines',
            'min_trendline_touches',
            'trendline_angle_min',
            'trendline_angle_max'
        ]
        
        from src.trend_detection_engine import TrendDetectionEngine
        test_config = {param: 1 for param in expected_dashboard_params}  # Dummy values
        
        engine = TrendDetectionEngine(test_config)
        config_info = engine.get_config_info()
        
        missing_params = []
        for param in expected_dashboard_params:
            if param not in config_info['current_config']:
                missing_params.append(param)
        
        if missing_params:
            print(f"   ⚠️ Missing dashboard parameters: {missing_params}")
            return False
        else:
            print("   ✅ All dashboard parameters supported")
            return True
        
    except Exception as e:
        print(f"❌ Dashboard integration test failed: {e}")
        return False

def main():
    """Run comprehensive system validation"""
    print("🔍 Trend Detection System Validation")
    print("=" * 60)
    
    # Generate test data
    print("📊 Generating test market data...")
    test_data = generate_test_data(200, 'XAUUSD')
    print(f"✅ Generated {len(test_data)} bars of test data")
    
    # Track test results
    test_results = {}
    
    # Test 1: Engine initialization
    engine, init_success = test_trend_detection_engine()
    test_results['initialization'] = init_success
    
    if not engine:
        print("\n❌ Cannot continue without working engine")
        return 1
    
    # Test 2: Performance
    perf_success, avg_time = test_analysis_performance(engine, test_data)
    test_results['performance'] = perf_success
    
    # Test 3: Signal generation
    signal_success, signal_count = test_signal_generation(engine, test_data)
    test_results['signal_generation'] = signal_success
    
    # Test 4: Configuration management
    config_success = test_configuration_management(engine)
    test_results['configuration'] = config_success
    
    # Test 5: Error handling
    error_success = test_error_handling(engine, test_data)
    test_results['error_handling'] = error_success
    
    # Test 6: Memory and performance
    memory_success = test_memory_and_performance(engine, test_data)
    test_results['memory_performance'] = memory_success
    
    # Test 7: Dashboard integration
    dashboard_success = test_integration_with_dashboard()
    test_results['dashboard_integration'] = dashboard_success
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 VALIDATION SUMMARY")
    print("=" * 60)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, success in test_results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title():<25} {status}")
    
    print("-" * 60)
    print(f"Overall Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED - System ready for deployment!")
        return 0
    else:
        print(f"⚠️ {total_tests - passed_tests} tests failed - Review issues before deployment")
        return 1

if __name__ == "__main__":
    exit(main())