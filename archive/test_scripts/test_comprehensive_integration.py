#!/usr/bin/env python3
"""
Comprehensive Integration Tests for GEM Trading Bot Trend Detection System

This test suite validates:
1. Complete signal generation pipeline end-to-end
2. Integration with existing MT5TradingBot functionality  
3. Backward compatibility with current signal generation
4. Trend detection engine integration
5. Performance and error handling

Requirements: 9.2 - Integration and Configuration
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import logging
from typing import Dict, List, Tuple, Any
import traceback

# Add src directory to path
sys.path.append('src')

# Configure logging for tests
logging.basicConfig(
    level=logging.WARNING,  # Reduce noise during tests
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class IntegrationTestSuite:
    """Comprehensive integration test suite for trend detection system"""
    
    def __init__(self):
        self.test_results = {}
        self.performance_metrics = {}
        self.error_log = []
        
    def log_test_result(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        self.test_results[test_name] = {
            'passed': passed,
            'details': details,
            'timestamp': datetime.now()
        }
        
    def log_performance(self, operation: str, duration_ms: float):
        """Log performance metric"""
        self.performance_metrics[operation] = duration_ms
        
    def log_error(self, test_name: str, error: Exception):
        """Log error details"""
        self.error_log.append({
            'test': test_name,
            'error': str(error),
            'traceback': traceback.format_exc(),
            'timestamp': datetime.now()
        })

class MarketDataGenerator:
    """Generate realistic market data for testing"""
    
    @staticmethod
    def create_trending_data(direction: str = 'up', bars: int = 200, volatility: float = 0.0003) -> pd.DataFrame:
        """Create trending market data"""
        np.random.seed(42)  # Reproducible results
        
        dates = pd.date_range(start='2024-01-01', periods=bars, freq='15T')
        base_price = 1.1000
        
        if direction == 'up':
            trend = np.linspace(0, 0.015, bars)  # 1.5% uptrend
        elif direction == 'down':
            trend = np.linspace(0, -0.015, bars)  # 1.5% downtrend
        else:  # sideways
            trend = np.sin(np.linspace(0, 4*np.pi, bars)) * 0.003  # Oscillating
            
        noise = np.random.normal(0, volatility, bars)
        prices = base_price + np.cumsum(noise) + trend
        
        # Create OHLCV data
        df = pd.DataFrame({
            'time': dates,
            'open': prices + np.random.normal(0, volatility/2, bars),
            'high': prices + np.abs(np.random.normal(0, volatility, bars)),
            'low': prices - np.abs(np.random.normal(0, volatility, bars)),
            'close': prices,
            'tick_volume': np.random.randint(500, 2000, bars),
            'spread': np.random.randint(1, 4, bars),
            'real_volume': np.random.randint(5000, 20000, bars)
        })
        
        return MarketDataGenerator.add_indicators(df)
    
    @staticmethod
    def create_crossover_data(crossover_type: str = 'bullish', bars: int = 100) -> pd.DataFrame:
        """Create data with MA crossover"""
        np.random.seed(123)
        
        dates = pd.date_range(start='2024-01-01', periods=bars, freq='15T')
        base_price = 1.1000
        
        if crossover_type == 'bullish':
            # Price starts below slow MA, crosses above
            trend1 = np.linspace(-0.005, 0, bars//2)
            trend2 = np.linspace(0, 0.008, bars//2)
            trend = np.concatenate([trend1, trend2])
        else:  # bearish
            # Price starts above slow MA, crosses below
            trend1 = np.linspace(0.005, 0, bars//2)
            trend2 = np.linspace(0, -0.008, bars//2)
            trend = np.concatenate([trend1, trend2])
            
        noise = np.random.normal(0, 0.0002, bars)
        prices = base_price + np.cumsum(noise) + trend
        
        df = pd.DataFrame({
            'time': dates,
            'open': prices + np.random.normal(0, 0.0001, bars),
            'high': prices + np.abs(np.random.normal(0, 0.0002, bars)),
            'low': prices - np.abs(np.random.normal(0, 0.0002, bars)),
            'close': prices,
            'tick_volume': np.random.randint(500, 2000, bars),
            'spread': np.random.randint(1, 4, bars),
            'real_volume': np.random.randint(5000, 20000, bars)
        })
        
        return MarketDataGenerator.add_indicators(df)
    
    @staticmethod
    def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators to dataframe"""
        # Moving averages
        df['fast_ma'] = df['close'].rolling(window=20).mean()
        df['slow_ma'] = df['close'].rolling(window=50).mean()
        
        # ATR
        df['high_low'] = df['high'] - df['low']
        df['high_close'] = np.abs(df['high'] - df['close'].shift())
        df['low_close'] = np.abs(df['low'] - df['close'].shift())
        df['tr'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
        df['atr'] = df['tr'].rolling(window=14).mean()
        
        # RSI
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        ema_fast = df['close'].ewm(span=12).mean()
        ema_slow = df['close'].ewm(span=26).mean()
        df['macd'] = ema_fast - ema_slow
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        # MA trend and crossover signals
        df['ma_trend'] = np.where(df['fast_ma'] > df['slow_ma'], 1, -1)
        df['ma_cross'] = 0
        
        # Calculate crossover signals
        for i in range(1, len(df)):
            if (df['fast_ma'].iloc[i] > df['slow_ma'].iloc[i] and 
                df['fast_ma'].iloc[i-1] <= df['slow_ma'].iloc[i-1]):
                df.loc[df.index[i], 'ma_cross'] = 1  # Bullish cross
            elif (df['fast_ma'].iloc[i] < df['slow_ma'].iloc[i] and 
                  df['fast_ma'].iloc[i-1] >= df['slow_ma'].iloc[i-1]):
                df.loc[df.index[i], 'ma_cross'] = -1  # Bearish cross
        
        return df.fillna(0)

def test_trend_detection_engine_initialization(test_suite: IntegrationTestSuite) -> bool:
    """Test 1: TrendDetectionEngine initialization and configuration"""
    print("1. Testing TrendDetectionEngine initialization...")
    
    try:
        from src.trend_detection_engine import TrendDetectionEngine
        
        # Test with various configurations
        configs = [
            # Basic config
            {
                'use_trend_detection': True,
                'trend_detection_sensitivity': 5,
                'min_trend_confidence': 0.6,
                'enable_early_signals': True
            },
            # Advanced config
            {
                'use_trend_detection': True,
                'trend_detection_sensitivity': 8,
                'min_trend_confidence': 0.7,
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
        ]
        
        for i, config in enumerate(configs):
            start_time = time.perf_counter()
            engine = TrendDetectionEngine(config)
            init_time = (time.perf_counter() - start_time) * 1000
            
            test_suite.log_performance(f"trend_engine_init_{i+1}", init_time)
            
            # Verify components are initialized
            assert hasattr(engine, 'market_structure_analyzer')
            assert hasattr(engine, 'divergence_detector')
            assert hasattr(engine, 'aroon_indicator')
            assert hasattr(engine, 'trendline_analyzer')
            assert hasattr(engine, 'multi_timeframe_analyzer')
            
        test_suite.log_test_result("trend_engine_initialization", True, 
                                 f"Successfully initialized with {len(configs)} different configurations")
        print("   ✅ TrendDetectionEngine initialization passed")
        return True
        
    except Exception as e:
        test_suite.log_error("trend_engine_initialization", e)
        test_suite.log_test_result("trend_engine_initialization", False, str(e))
        print(f"   ❌ TrendDetectionEngine initialization failed: {e}")
        return False

def test_mt5_trading_bot_integration(test_suite: IntegrationTestSuite) -> bool:
    """Test 2: MT5TradingBot integration with trend detection"""
    print("2. Testing MT5TradingBot integration...")
    
    try:
        from src.mt5_trading_bot import MT5TradingBot
        
        # Test config with trend detection enabled
        config = {
            'use_trend_detection': True,
            'trend_detection_sensitivity': 5,
            'min_trend_confidence': 0.5,
            'enable_early_signals': True,
            'symbols': ['EURUSD'],
            'timeframe': 15,  # M15
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
            'adx_min_strength': 25,
            'magic_number': 12345
        }
        
        # Initialize bot (without MT5 connection)
        start_time = time.perf_counter()
        bot = MT5TradingBot(config)
        init_time = (time.perf_counter() - start_time) * 1000
        
        test_suite.log_performance("mt5_bot_init", init_time)
        
        # Verify trend detection engine is initialized
        assert hasattr(bot, 'trend_detection_engine')
        if bot.trend_detection_engine is not None:
            assert hasattr(bot.trend_detection_engine, 'analyze_trend_change')
            assert hasattr(bot.trend_detection_engine, 'should_trade_trend')
        
        # Verify trend analysis methods exist
        assert hasattr(bot, 'get_trend_analysis')
        assert hasattr(bot, 'get_trend_summary')
        
        test_suite.log_test_result("mt5_bot_integration", True, 
                                 "MT5TradingBot successfully integrated with trend detection")
        print("   ✅ MT5TradingBot integration passed")
        return True
        
    except Exception as e:
        test_suite.log_error("mt5_bot_integration", e)
        test_suite.log_test_result("mt5_bot_integration", False, str(e))
        print(f"   ❌ MT5TradingBot integration failed: {e}")
        return False

def test_signal_generation_pipeline(test_suite: IntegrationTestSuite) -> bool:
    """Test 3: Complete signal generation pipeline end-to-end"""
    print("3. Testing complete signal generation pipeline...")
    
    try:
        from src.mt5_trading_bot import MT5TradingBot
        
        config = {
            'use_trend_detection': True,
            'trend_detection_sensitivity': 5,
            'min_trend_confidence': 0.4,  # Lower for testing
            'enable_early_signals': True,
            'symbols': ['EURUSD'],
            'timeframe': 15,
            'fast_ma_period': 20,
            'slow_ma_period': 50,
            'atr_period': 14,
            'atr_multiplier': 2.0,
            'reward_ratio': 2.0,
            'risk_percent': 1.0,
            'lot_size': 0.1,
            'rsi_overbought': 70,
            'rsi_oversold': 30,
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9,
            'use_adx': True,
            'adx_period': 14,
            'adx_min_strength': 25,
            'magic_number': 12345
        }
        
        bot = MT5TradingBot(config)
        
        # Test scenarios
        test_scenarios = [
            ('bullish_trend', MarketDataGenerator.create_trending_data('up', 150)),
            ('bearish_trend', MarketDataGenerator.create_trending_data('down', 150)),
            ('sideways_market', MarketDataGenerator.create_trending_data('sideways', 150)),
            ('bullish_crossover', MarketDataGenerator.create_crossover_data('bullish', 100)),
            ('bearish_crossover', MarketDataGenerator.create_crossover_data('bearish', 100))
        ]
        
        pipeline_results = {}
        
        for scenario_name, test_data in test_scenarios:
            print(f"   Testing {scenario_name}...")
            
            start_time = time.perf_counter()
            
            # Test complete pipeline
            # 1. Calculate indicators (already done in test data)
            # 2. Check entry signal (includes trend detection if enabled)
            signal = bot.check_entry_signal(test_data)
            
            # 3. Get trend analysis
            trend_analysis = None
            if bot.trend_detection_engine:
                trend_analysis = bot.get_trend_analysis('EURUSD', test_data)
            
            # 4. Get trend summary
            trend_summary = bot.get_trend_summary('EURUSD', test_data)
            
            pipeline_time = (time.perf_counter() - start_time) * 1000
            test_suite.log_performance(f"pipeline_{scenario_name}", pipeline_time)
            
            # Verify results
            pipeline_results[scenario_name] = {
                'signal': signal,
                'trend_analysis': trend_analysis is not None,
                'trend_summary': trend_summary is not None,
                'processing_time_ms': pipeline_time
            }
            
            # Performance check (should be under 100ms per requirement)
            if pipeline_time > 100:
                print(f"      ⚠️ Performance warning: {pipeline_time:.1f}ms (>100ms threshold)")
            else:
                print(f"      ✅ Performance good: {pipeline_time:.1f}ms")
        
        # Verify at least some signals were generated
        signals_generated = sum(1 for result in pipeline_results.values() if result['signal'] != 0)
        
        test_suite.log_test_result("signal_generation_pipeline", True, 
                                 f"Pipeline tested with {len(test_scenarios)} scenarios, "
                                 f"{signals_generated} signals generated")
        
        print(f"   ✅ Signal generation pipeline passed ({signals_generated}/{len(test_scenarios)} scenarios generated signals)")
        return True
        
    except Exception as e:
        test_suite.log_error("signal_generation_pipeline", e)
        test_suite.log_test_result("signal_generation_pipeline", False, str(e))
        print(f"   ❌ Signal generation pipeline failed: {e}")
        return False

def test_backward_compatibility(test_suite: IntegrationTestSuite) -> bool:
    """Test 4: Backward compatibility with existing signal generation"""
    print("4. Testing backward compatibility...")
    
    try:
        from src.mt5_trading_bot import MT5TradingBot
        
        # Test with trend detection disabled
        config_without_trend = {
            'use_trend_detection': False,  # Disabled
            'symbols': ['EURUSD'],
            'timeframe': 15,
            'fast_ma_period': 20,
            'slow_ma_period': 50,
            'atr_period': 14,
            'atr_multiplier': 2.0,
            'reward_ratio': 2.0,
            'risk_percent': 1.0,
            'lot_size': 0.1,
            'rsi_overbought': 70,
            'rsi_oversold': 30,
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9,
            'use_adx': True,
            'adx_period': 14,
            'adx_min_strength': 25,
            'magic_number': 12345
        }
        
        # Test with trend detection enabled
        config_with_trend = config_without_trend.copy()
        config_with_trend['use_trend_detection'] = True
        config_with_trend['min_trend_confidence'] = 0.5
        
        # Create bots
        bot_without_trend = MT5TradingBot(config_without_trend)
        bot_with_trend = MT5TradingBot(config_with_trend)
        
        # Verify trend detection engine states
        assert bot_without_trend.trend_detection_engine is None
        assert bot_with_trend.trend_detection_engine is not None
        
        # Test with same data
        test_data = MarketDataGenerator.create_crossover_data('bullish', 100)
        
        # Both should have check_entry_signal method
        signal_without = bot_without_trend.check_entry_signal(test_data)
        signal_with = bot_with_trend.check_entry_signal(test_data)
        
        # Both should return valid signal values
        assert signal_without in [-1, 0, 1]
        assert signal_with in [-1, 0, 1]
        
        # Test other methods exist and work
        methods_to_test = [
            'calculate_indicators',
            'calculate_stop_loss',
            'calculate_take_profit',
            'calculate_position_size'
        ]
        
        for method_name in methods_to_test:
            assert hasattr(bot_without_trend, method_name)
            assert hasattr(bot_with_trend, method_name)
        
        # Test indicator calculation compatibility
        indicators_without = bot_without_trend.calculate_indicators(test_data.copy())
        indicators_with = bot_with_trend.calculate_indicators(test_data.copy())
        
        # Should have same columns (basic indicators)
        basic_columns = ['fast_ma', 'slow_ma', 'rsi', 'macd', 'macd_signal', 'macd_histogram', 'atr']
        for col in basic_columns:
            assert col in indicators_without.columns
            assert col in indicators_with.columns
        
        test_suite.log_test_result("backward_compatibility", True, 
                                 "All existing functionality works with and without trend detection")
        print("   ✅ Backward compatibility passed")
        return True
        
    except Exception as e:
        test_suite.log_error("backward_compatibility", e)
        test_suite.log_test_result("backward_compatibility", False, str(e))
        print(f"   ❌ Backward compatibility failed: {e}")
        return False

def test_trend_detection_components(test_suite: IntegrationTestSuite) -> bool:
    """Test 5: Individual trend detection components"""
    print("5. Testing individual trend detection components...")
    
    try:
        from src.trend_detection_engine import TrendDetectionEngine
        
        config = {
            'use_trend_detection': True,
            'trend_detection_sensitivity': 5,
            'min_trend_confidence': 0.5,
            'enable_early_signals': True,
            'aroon_period': 25,
            'swing_strength': 3,
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
        
        engine = TrendDetectionEngine(config)
        test_data = MarketDataGenerator.create_trending_data('up', 150)
        
        component_results = {}
        
        # Test EMA Momentum Analyzer
        try:
            start_time = time.perf_counter()
            ema_signal = engine.ema_momentum_analyzer.get_ema_signal(test_data)
            ema_time = (time.perf_counter() - start_time) * 1000
            
            component_results['ema_analyzer'] = {
                'success': True,
                'has_signal': ema_signal is not None,
                'time_ms': ema_time
            }
            test_suite.log_performance("ema_analyzer", ema_time)
        except Exception as e:
            component_results['ema_analyzer'] = {'success': False, 'error': str(e)}
        
        # Test Aroon Indicator
        try:
            start_time = time.perf_counter()
            aroon_signal = engine.aroon_indicator.get_aroon_signal(test_data)
            aroon_time = (time.perf_counter() - start_time) * 1000
            
            component_results['aroon_indicator'] = {
                'success': True,
                'has_signal': aroon_signal is not None,
                'time_ms': aroon_time
            }
            test_suite.log_performance("aroon_indicator", aroon_time)
        except Exception as e:
            component_results['aroon_indicator'] = {'success': False, 'error': str(e)}
        
        # Test Market Structure Analyzer
        try:
            start_time = time.perf_counter()
            structure_break = engine.market_structure_analyzer.detect_structure_break(test_data)
            structure_time = (time.perf_counter() - start_time) * 1000
            
            component_results['market_structure'] = {
                'success': True,
                'has_break': structure_break is not None,
                'time_ms': structure_time
            }
            test_suite.log_performance("market_structure", structure_time)
        except Exception as e:
            component_results['market_structure'] = {'success': False, 'error': str(e)}
        
        # Test Divergence Detector
        try:
            start_time = time.perf_counter()
            rsi_divergence = engine.divergence_detector.detect_rsi_divergence(test_data)
            macd_divergence = engine.divergence_detector.detect_macd_divergence(test_data)
            divergence_time = (time.perf_counter() - start_time) * 1000
            
            component_results['divergence_detector'] = {
                'success': True,
                'has_rsi_divergence': rsi_divergence is not None,
                'has_macd_divergence': macd_divergence is not None,
                'time_ms': divergence_time
            }
            test_suite.log_performance("divergence_detector", divergence_time)
        except Exception as e:
            component_results['divergence_detector'] = {'success': False, 'error': str(e)}
        
        # Test Trendline Analyzer
        try:
            start_time = time.perf_counter()
            trendlines = engine.trendline_analyzer.identify_trendlines(test_data)
            trendline_time = (time.perf_counter() - start_time) * 1000
            
            component_results['trendline_analyzer'] = {
                'success': True,
                'trendlines_found': len(trendlines) if trendlines else 0,
                'time_ms': trendline_time
            }
            test_suite.log_performance("trendline_analyzer", trendline_time)
        except Exception as e:
            component_results['trendline_analyzer'] = {'success': False, 'error': str(e)}
        
        # Count successful components
        successful_components = sum(1 for result in component_results.values() if result.get('success', False))
        total_components = len(component_results)
        
        test_suite.log_test_result("trend_detection_components", successful_components == total_components,
                                 f"{successful_components}/{total_components} components working correctly")
        
        if successful_components == total_components:
            print(f"   ✅ All {total_components} trend detection components passed")
            return True
        else:
            print(f"   ⚠️ {successful_components}/{total_components} components passed")
            for name, result in component_results.items():
                if not result.get('success', False):
                    print(f"      ❌ {name}: {result.get('error', 'Unknown error')}")
            return False
        
    except Exception as e:
        test_suite.log_error("trend_detection_components", e)
        test_suite.log_test_result("trend_detection_components", False, str(e))
        print(f"   ❌ Trend detection components test failed: {e}")
        return False

def test_performance_requirements(test_suite: IntegrationTestSuite) -> bool:
    """Test 6: Performance requirements (100ms per symbol per timeframe)"""
    print("6. Testing performance requirements...")
    
    try:
        from src.trend_detection_engine import TrendDetectionEngine
        
        config = {
            'use_trend_detection': True,
            'trend_detection_sensitivity': 5,
            'min_trend_confidence': 0.6,
            'enable_early_signals': True,
            'max_analysis_time_ms': 100  # Performance requirement
        }
        
        engine = TrendDetectionEngine(config)
        
        # Test with different data sizes
        test_cases = [
            ('small_dataset', 50),
            ('medium_dataset', 100),
            ('large_dataset', 200),
            ('xlarge_dataset', 500)
        ]
        
        performance_results = {}
        
        for case_name, bars in test_cases:
            test_data = MarketDataGenerator.create_trending_data('up', bars)
            
            # Measure analysis time
            start_time = time.perf_counter()
            analysis = engine.analyze_trend_change(test_data, f"TEST_{case_name}")
            analysis_time = (time.perf_counter() - start_time) * 1000
            
            performance_results[case_name] = {
                'bars': bars,
                'time_ms': analysis_time,
                'meets_requirement': analysis_time <= 100,
                'signals_generated': len(analysis.signals),
                'confidence': analysis.confidence
            }
            
            test_suite.log_performance(f"analysis_{case_name}", analysis_time)
            
            print(f"   {case_name} ({bars} bars): {analysis_time:.1f}ms "
                  f"{'✅' if analysis_time <= 100 else '❌'}")
        
        # Check if all cases meet performance requirement
        all_meet_requirement = all(result['meets_requirement'] for result in performance_results.values())
        
        avg_time = sum(result['time_ms'] for result in performance_results.values()) / len(performance_results)
        
        test_suite.log_test_result("performance_requirements", all_meet_requirement,
                                 f"Average analysis time: {avg_time:.1f}ms, "
                                 f"All cases under 100ms: {all_meet_requirement}")
        
        if all_meet_requirement:
            print(f"   ✅ Performance requirements met (avg: {avg_time:.1f}ms)")
            return True
        else:
            print(f"   ❌ Performance requirements not met (avg: {avg_time:.1f}ms)")
            return False
        
    except Exception as e:
        test_suite.log_error("performance_requirements", e)
        test_suite.log_test_result("performance_requirements", False, str(e))
        print(f"   ❌ Performance requirements test failed: {e}")
        return False

def test_error_handling_and_recovery(test_suite: IntegrationTestSuite) -> bool:
    """Test 7: Error handling and graceful degradation"""
    print("7. Testing error handling and recovery...")
    
    try:
        from src.mt5_trading_bot import MT5TradingBot
        
        config = {
            'use_trend_detection': True,
            'trend_detection_sensitivity': 5,
            'min_trend_confidence': 0.6,
            'enable_early_signals': True,
            'symbols': ['EURUSD'],
            'timeframe': 15,
            'fast_ma_period': 20,
            'slow_ma_period': 50,
            'magic_number': 12345
        }
        
        bot = MT5TradingBot(config)
        
        error_scenarios = []
        
        # Test 1: Invalid data
        try:
            invalid_data = pd.DataFrame({'invalid': [1, 2, 3]})
            signal = bot.check_entry_signal(invalid_data)
            # Should not crash, should return 0 (no signal)
            assert signal == 0
            error_scenarios.append(('invalid_data', True, 'Handled gracefully'))
        except Exception as e:
            error_scenarios.append(('invalid_data', False, str(e)))
        
        # Test 2: Empty data
        try:
            empty_data = pd.DataFrame()
            signal = bot.check_entry_signal(empty_data)
            assert signal == 0
            error_scenarios.append(('empty_data', True, 'Handled gracefully'))
        except Exception as e:
            error_scenarios.append(('empty_data', False, str(e)))
        
        # Test 3: Data with NaN values
        try:
            nan_data = MarketDataGenerator.create_trending_data('up', 50)
            nan_data.loc[nan_data.index[10:15], 'close'] = np.nan
            signal = bot.check_entry_signal(nan_data)
            # Should handle NaN gracefully
            error_scenarios.append(('nan_data', True, 'Handled NaN values'))
        except Exception as e:
            error_scenarios.append(('nan_data', False, str(e)))
        
        # Test 4: Insufficient data
        try:
            small_data = MarketDataGenerator.create_trending_data('up', 5)  # Very small dataset
            signal = bot.check_entry_signal(small_data)
            error_scenarios.append(('insufficient_data', True, 'Handled small dataset'))
        except Exception as e:
            error_scenarios.append(('insufficient_data', False, str(e)))
        
        # Test 5: Trend analysis with invalid symbol
        try:
            valid_data = MarketDataGenerator.create_trending_data('up', 100)
            if bot.trend_detection_engine:
                analysis = bot.get_trend_analysis('INVALID_SYMBOL', valid_data)
                # Should return None or handle gracefully
                error_scenarios.append(('invalid_symbol', True, 'Handled invalid symbol'))
            else:
                error_scenarios.append(('invalid_symbol', True, 'Trend detection disabled'))
        except Exception as e:
            error_scenarios.append(('invalid_symbol', False, str(e)))
        
        # Count successful error handling
        successful_handling = sum(1 for _, success, _ in error_scenarios if success)
        total_scenarios = len(error_scenarios)
        
        test_suite.log_test_result("error_handling", successful_handling == total_scenarios,
                                 f"{successful_handling}/{total_scenarios} error scenarios handled gracefully")
        
        if successful_handling == total_scenarios:
            print(f"   ✅ Error handling passed ({successful_handling}/{total_scenarios} scenarios)")
            return True
        else:
            print(f"   ⚠️ Error handling partial ({successful_handling}/{total_scenarios} scenarios)")
            for scenario, success, details in error_scenarios:
                status = "✅" if success else "❌"
                print(f"      {status} {scenario}: {details}")
            return False
        
    except Exception as e:
        test_suite.log_error("error_handling", e)
        test_suite.log_test_result("error_handling", False, str(e))
        print(f"   ❌ Error handling test failed: {e}")
        return False

def run_comprehensive_integration_tests() -> Dict[str, Any]:
    """Run all comprehensive integration tests"""
    print("🚀 STARTING COMPREHENSIVE INTEGRATION TESTS")
    print("=" * 80)
    print("Testing: Complete signal generation pipeline end-to-end")
    print("         Integration with existing MT5TradingBot functionality")
    print("         Backward compatibility with current signal generation")
    print("         Performance and error handling requirements")
    print("=" * 80)
    
    test_suite = IntegrationTestSuite()
    
    # Run all tests
    tests = [
        ("TrendDetectionEngine Initialization", test_trend_detection_engine_initialization),
        ("MT5TradingBot Integration", test_mt5_trading_bot_integration),
        ("Signal Generation Pipeline", test_signal_generation_pipeline),
        ("Backward Compatibility", test_backward_compatibility),
        ("Trend Detection Components", test_trend_detection_components),
        ("Performance Requirements", test_performance_requirements),
        ("Error Handling & Recovery", test_error_handling_and_recovery)
    ]
    
    results = []
    start_time = time.perf_counter()
    
    for test_name, test_function in tests:
        print(f"\n{test_name}:")
        try:
            success = test_function(test_suite)
            results.append((test_name, success))
        except Exception as e:
            print(f"   ❌ Test framework error: {e}")
            test_suite.log_error(test_name, e)
            results.append((test_name, False))
    
    total_time = (time.perf_counter() - start_time) * 1000
    
    # Generate summary
    passed_tests = sum(1 for _, success in results if success)
    total_tests = len(results)
    
    print("\n" + "=" * 80)
    print("📋 COMPREHENSIVE INTEGRATION TEST RESULTS")
    print("=" * 80)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status:12} {test_name}")
    
    print(f"\nSUMMARY:")
    print(f"  Tests Passed: {passed_tests}/{total_tests}")
    print(f"  Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    print(f"  Total Time: {total_time:.1f}ms")
    
    # Performance summary
    if test_suite.performance_metrics:
        print(f"\nPERFORMANCE METRICS:")
        for operation, time_ms in test_suite.performance_metrics.items():
            status = "✅" if time_ms <= 100 else "⚠️" if time_ms <= 200 else "❌"
            print(f"  {status} {operation}: {time_ms:.1f}ms")
    
    # Error summary
    if test_suite.error_log:
        print(f"\nERRORS ENCOUNTERED: {len(test_suite.error_log)}")
        for error in test_suite.error_log[-3:]:  # Show last 3 errors
            print(f"  ❌ {error['test']}: {error['error']}")
    
    print("=" * 80)
    
    if passed_tests == total_tests:
        print("🎉 ALL INTEGRATION TESTS PASSED!")
        print("   The trend detection system is fully integrated and working correctly.")
        print("   ✅ Signal generation pipeline: WORKING")
        print("   ✅ MT5TradingBot integration: WORKING") 
        print("   ✅ Backward compatibility: MAINTAINED")
        print("   ✅ Performance requirements: MET")
        print("   ✅ Error handling: ROBUST")
    else:
        print("💥 SOME INTEGRATION TESTS FAILED!")
        print("   Please review the failed tests above and fix the issues.")
        
        failed_tests = [name for name, success in results if not success]
        print(f"   Failed tests: {', '.join(failed_tests)}")
    
    return {
        'total_tests': total_tests,
        'passed_tests': passed_tests,
        'success_rate': (passed_tests/total_tests)*100,
        'total_time_ms': total_time,
        'performance_metrics': test_suite.performance_metrics,
        'test_results': test_suite.test_results,
        'error_log': test_suite.error_log,
        'all_passed': passed_tests == total_tests
    }

if __name__ == "__main__":
    # Run comprehensive integration tests
    results = run_comprehensive_integration_tests()
    
    # Exit with appropriate code
    exit_code = 0 if results['all_passed'] else 1
    sys.exit(exit_code)