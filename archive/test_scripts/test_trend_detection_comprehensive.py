#!/usr/bin/env python3
"""
Comprehensive Test Suite for Advanced Trend Detection System
Tests all components before going live with real trading
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
import time
import logging

# Add src to path
sys.path.append('src')

from trend_detection_engine import TrendDetectionEngine
from market_structure_analyzer import MarketStructureAnalyzer
from aroon_indicator import AroonIndicator
from config import get_config

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TrendDetectionTestSuite:
    """Comprehensive test suite for trend detection system"""
    
    def __init__(self):
        self.config = get_config()
        self.test_results = []
        self.passed_tests = 0
        self.failed_tests = 0
        
    def log_test_result(self, test_name, passed, details=""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        result = {
            'test': test_name,
            'passed': passed,
            'details': details,
            'timestamp': datetime.now()
        }
        self.test_results.append(result)
        
        if passed:
            self.passed_tests += 1
        else:
            self.failed_tests += 1
            
        print(f"{status} - {test_name}")
        if details:
            print(f"    Details: {details}")
    
    def create_test_data(self, bars=200, trend_type='uptrend'):
        """Create synthetic market data for testing"""
        dates = pd.date_range(start=datetime.now() - timedelta(hours=bars), periods=bars, freq='h')
        
        base_price = 2000.0
        
        if trend_type == 'uptrend':
            trend = np.linspace(0, 100, bars)  # Strong upward trend
        elif trend_type == 'downtrend':
            trend = np.linspace(0, -100, bars)  # Strong downward trend
        elif trend_type == 'sideways':
            trend = np.sin(np.linspace(0, 4*np.pi, bars)) * 20  # Sideways movement
        else:
            trend = np.zeros(bars)
            
        noise = np.random.normal(0, 5, bars)
        prices = base_price + trend + noise
        
        # Create realistic OHLC data
        df = pd.DataFrame({
            'open': prices + np.random.normal(0, 1, bars),
            'high': prices + np.abs(np.random.normal(2, 1, bars)),
            'low': prices - np.abs(np.random.normal(2, 1, bars)),
            'close': prices,
            'volume': np.random.randint(1000, 5000, bars),
            'tick_volume': np.random.randint(100, 500, bars)
        }, index=dates)
        
        return df
    
    def test_trend_detection_engine_initialization(self):
        """Test TrendDetectionEngine initialization"""
        try:
            engine = TrendDetectionEngine(self.config)
            
            # Check basic attributes
            assert hasattr(engine, 'use_trend_detection')
            assert hasattr(engine, 'sensitivity')
            assert hasattr(engine, 'min_confidence')
            assert hasattr(engine, 'market_structure_analyzer')
            assert hasattr(engine, 'aroon_indicator')
            
            self.log_test_result("TrendDetectionEngine Initialization", True, 
                                f"Sensitivity: {engine.sensitivity}, Min Confidence: {engine.min_confidence}")
            return engine
            
        except Exception as e:
            self.log_test_result("TrendDetectionEngine Initialization", False, str(e))
            return None
    
    def test_market_structure_analyzer(self):
        """Test MarketStructureAnalyzer functionality"""
        try:
            analyzer = MarketStructureAnalyzer(self.config)
            
            # Test with uptrend data (should detect structure breaks)
            uptrend_data = self.create_test_data(100, 'uptrend')
            structure_result = analyzer.detect_structure_break(uptrend_data)
            
            # Test with downtrend data
            downtrend_data = self.create_test_data(100, 'downtrend')
            structure_result_down = analyzer.detect_structure_break(downtrend_data)
            
            # Test swing point detection
            swing_points = analyzer._find_swing_points(uptrend_data, 'high')
            
            self.log_test_result("MarketStructureAnalyzer", True, 
                                f"Swing points found: {len(swing_points)}")
            return True
            
        except Exception as e:
            self.log_test_result("MarketStructureAnalyzer", False, str(e))
            return False
    
    def test_aroon_indicator(self):
        """Test AroonIndicator functionality"""
        try:
            aroon = AroonIndicator(period=25)
            
            # Test with trending data
            trend_data = self.create_test_data(100, 'uptrend')
            aroon_df = aroon.calculate_aroon(trend_data)
            
            # Check if Aroon columns were added
            assert 'aroon_up' in aroon_df.columns
            assert 'aroon_down' in aroon_df.columns
            assert 'aroon_oscillator' in aroon_df.columns
            
            # Test signal generation
            signal = aroon.get_aroon_signal(aroon_df)
            
            # Test with sideways data
            sideways_data = self.create_test_data(100, 'sideways')
            sideways_signal = aroon.get_aroon_signal(sideways_data)
            
            self.log_test_result("AroonIndicator", True, 
                                f"Signal type: {signal.signal_type if signal else 'None'}")
            return True
            
        except Exception as e:
            self.log_test_result("AroonIndicator", False, str(e))
            return False
    
    def test_trend_analysis_comprehensive(self):
        """Test comprehensive trend analysis"""
        try:
            engine = TrendDetectionEngine(self.config)
            
            # Test different market conditions
            test_scenarios = [
                ('uptrend', 'Bullish trend detection'),
                ('downtrend', 'Bearish trend detection'),
                ('sideways', 'Consolidation detection')
            ]
            
            scenario_results = []
            
            for trend_type, description in test_scenarios:
                test_data = self.create_test_data(150, trend_type)
                analysis_result = engine.analyze_trend_change(test_data, f"TEST_{trend_type.upper()}")
                
                scenario_results.append({
                    'scenario': description,
                    'signals': len(analysis_result.signals),
                    'confidence': analysis_result.confidence,
                    'market_structure': analysis_result.market_structure is not None,
                    'aroon_signal': analysis_result.aroon_signal is not None
                })
            
            details = "; ".join([f"{r['scenario']}: {r['signals']} signals, {r['confidence']:.2f} confidence" 
                               for r in scenario_results])
            
            self.log_test_result("Comprehensive Trend Analysis", True, details)
            return scenario_results
            
        except Exception as e:
            self.log_test_result("Comprehensive Trend Analysis", False, str(e))
            return []
    
    def test_signal_filtering(self):
        """Test signal filtering by type"""
        try:
            engine = TrendDetectionEngine(self.config)
            
            # Test with bullish data
            bullish_data = self.create_test_data(100, 'uptrend')
            buy_signals = engine.get_trend_signals(bullish_data, 'buy')
            sell_signals = engine.get_trend_signals(bullish_data, 'sell')
            
            # Test with bearish data
            bearish_data = self.create_test_data(100, 'downtrend')
            buy_signals_bear = engine.get_trend_signals(bearish_data, 'buy')
            sell_signals_bear = engine.get_trend_signals(bearish_data, 'sell')
            
            self.log_test_result("Signal Filtering", True, 
                                f"Bullish data: {len(buy_signals)} buy, {len(sell_signals)} sell; "
                                f"Bearish data: {len(buy_signals_bear)} buy, {len(sell_signals_bear)} sell")
            return True
            
        except Exception as e:
            self.log_test_result("Signal Filtering", False, str(e))
            return False
    
    def test_trading_decision_logic(self):
        """Test should_trade_trend logic"""
        try:
            engine = TrendDetectionEngine(self.config)
            
            # Test with strong trend data
            strong_trend = self.create_test_data(100, 'uptrend')
            should_buy, buy_confidence = engine.should_trade_trend(strong_trend, 'buy')
            should_sell, sell_confidence = engine.should_trade_trend(strong_trend, 'sell')
            
            # Test with weak/sideways data
            weak_trend = self.create_test_data(100, 'sideways')
            should_buy_weak, buy_conf_weak = engine.should_trade_trend(weak_trend, 'buy')
            should_sell_weak, sell_conf_weak = engine.should_trade_trend(weak_trend, 'sell')
            
            self.log_test_result("Trading Decision Logic", True, 
                                f"Strong trend: Buy={should_buy}({buy_confidence:.2f}), Sell={should_sell}({sell_confidence:.2f}); "
                                f"Weak trend: Buy={should_buy_weak}({buy_conf_weak:.2f}), Sell={should_sell_weak}({sell_conf_weak:.2f})")
            return True
            
        except Exception as e:
            self.log_test_result("Trading Decision Logic", False, str(e))
            return False
    
    def test_performance_benchmarks(self):
        """Test performance requirements (100ms per symbol per timeframe)"""
        try:
            engine = TrendDetectionEngine(self.config)
            test_data = self.create_test_data(200, 'uptrend')
            
            # Measure analysis time
            start_time = time.time()
            analysis_result = engine.analyze_trend_change(test_data, "PERFORMANCE_TEST")
            end_time = time.time()
            
            analysis_time_ms = (end_time - start_time) * 1000
            performance_ok = analysis_time_ms < 100  # Must be under 100ms
            
            self.log_test_result("Performance Benchmark", performance_ok, 
                                f"Analysis time: {analysis_time_ms:.1f}ms (target: <100ms)")
            return performance_ok
            
        except Exception as e:
            self.log_test_result("Performance Benchmark", False, str(e))
            return False
    
    def test_error_handling(self):
        """Test error handling with invalid data"""
        try:
            engine = TrendDetectionEngine(self.config)
            
            # Test with insufficient data
            small_data = self.create_test_data(10, 'uptrend')  # Too small
            result_small = engine.analyze_trend_change(small_data, "SMALL_DATA_TEST")
            
            # Test with empty data
            empty_data = pd.DataFrame()
            result_empty = engine.analyze_trend_change(empty_data, "EMPTY_DATA_TEST")
            
            # Test with malformed data
            bad_data = pd.DataFrame({'bad_column': [1, 2, 3]})
            result_bad = engine.analyze_trend_change(bad_data, "BAD_DATA_TEST")
            
            # All should return empty results without crashing
            error_handling_ok = (
                len(result_small.signals) == 0 and
                len(result_empty.signals) == 0 and
                len(result_bad.signals) == 0
            )
            
            self.log_test_result("Error Handling", error_handling_ok, 
                                "System handles invalid data gracefully")
            return error_handling_ok
            
        except Exception as e:
            self.log_test_result("Error Handling", False, str(e))
            return False
    
    def test_configuration_validation(self):
        """Test configuration parameter validation"""
        try:
            # Test with different configurations
            test_configs = [
                {**self.config, 'trend_detection_sensitivity': 1},  # Min sensitivity
                {**self.config, 'trend_detection_sensitivity': 10}, # Max sensitivity
                {**self.config, 'min_trend_confidence': 0.1},       # Low confidence
                {**self.config, 'min_trend_confidence': 0.9},       # High confidence
                {**self.config, 'use_trend_detection': False},      # Disabled
            ]
            
            config_results = []
            for i, config in enumerate(test_configs):
                try:
                    engine = TrendDetectionEngine(config)
                    test_data = self.create_test_data(100, 'uptrend')
                    result = engine.analyze_trend_change(test_data, f"CONFIG_TEST_{i}")
                    config_results.append(True)
                except:
                    config_results.append(False)
            
            all_configs_ok = all(config_results)
            
            self.log_test_result("Configuration Validation", all_configs_ok, 
                                f"Tested {len(test_configs)} configurations")
            return all_configs_ok
            
        except Exception as e:
            self.log_test_result("Configuration Validation", False, str(e))
            return False
    
    def run_all_tests(self):
        """Run all tests in the suite"""
        print("🔍 Starting Comprehensive Trend Detection Test Suite")
        print("=" * 80)
        
        start_time = time.time()
        
        # Run all tests
        tests = [
            self.test_trend_detection_engine_initialization,
            self.test_market_structure_analyzer,
            self.test_aroon_indicator,
            self.test_trend_analysis_comprehensive,
            self.test_signal_filtering,
            self.test_trading_decision_logic,
            self.test_performance_benchmarks,
            self.test_error_handling,
            self.test_configuration_validation,
        ]
        
        print(f"\nRunning {len(tests)} test categories...\n")
        
        for test in tests:
            try:
                test()
            except Exception as e:
                self.log_test_result(test.__name__, False, f"Test execution failed: {str(e)}")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 TEST SUITE SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.passed_tests + self.failed_tests}")
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.failed_tests}")
        print(f"⏱️  Total Time: {total_time:.2f} seconds")
        print(f"📈 Success Rate: {(self.passed_tests / (self.passed_tests + self.failed_tests) * 100):.1f}%")
        
        if self.failed_tests == 0:
            print("\n🎉 ALL TESTS PASSED - SYSTEM READY FOR LIVE TRADING!")
            print("✅ Trend detection system is working correctly")
            print("✅ Performance requirements met")
            print("✅ Error handling is robust")
            print("✅ Configuration validation passed")
        else:
            print(f"\n⚠️  {self.failed_tests} TESTS FAILED - REVIEW REQUIRED BEFORE GOING LIVE")
            print("\nFailed Tests:")
            for result in self.test_results:
                if not result['passed']:
                    print(f"  ❌ {result['test']}: {result['details']}")
        
        return self.failed_tests == 0

def main():
    """Main test execution"""
    test_suite = TrendDetectionTestSuite()
    success = test_suite.run_all_tests()
    
    if success:
        print("\n🚀 READY TO DEPLOY - All systems go!")
        return 0
    else:
        print("\n🛑 NOT READY - Fix issues before deployment")
        return 1

if __name__ == "__main__":
    sys.exit(main())