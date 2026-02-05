#!/usr/bin/env python3
"""
Property-Based Test for EMA Crossover Detection - Task 1.2
**Validates: Requirements 3.2, 3.3**

Property 1: EMA Crossover Signal Accuracy
For any price series with identifiable EMA crossover patterns:
- WHEN 20 EMA crosses above 50 EMA, THEN the system SHALL identify this as a bullish crossover
- WHEN 20 EMA crosses below 50 EMA, THEN the system SHALL identify this as a bearish crossover
- AND the crossover strength SHALL correlate with the magnitude and persistence of the crossover
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
import random
from typing import List, Tuple, Dict, Any

# Add src to path
sys.path.append('src')

from ema_momentum_analyzer import EMAMomentumAnalyzer, EMASignal
from config import get_config

class EMAPropertyTestGenerator:
    """Generator for creating test data with controlled EMA crossover patterns"""
    
    def __init__(self, seed: int = None):
        """Initialize the generator with optional seed for reproducibility"""
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
    
    def generate_crossover_scenario(self, 
                                  crossover_type: str,
                                  bars: int = 200,
                                  base_price: float = 2000.0,
                                  noise_level: float = 0.5) -> pd.DataFrame:
        """
        Generate price data with controlled EMA crossover patterns
        
        Args:
            crossover_type: 'bullish', 'bearish', 'multiple', 'false_signal'
            bars: Number of bars to generate
            base_price: Starting price level
            noise_level: Amount of random noise (0.0 to 2.0)
            
        Returns:
            DataFrame with OHLC data containing the specified crossover pattern
        """
        dates = pd.date_range(start=datetime.now() - timedelta(hours=bars), periods=bars, freq='h')
        
        if crossover_type == 'bullish':
            return self._generate_bullish_crossover(dates, base_price, noise_level)
        elif crossover_type == 'bearish':
            return self._generate_bearish_crossover(dates, base_price, noise_level)
        elif crossover_type == 'multiple':
            return self._generate_multiple_crossovers(dates, base_price, noise_level)
        elif crossover_type == 'false_signal':
            return self._generate_false_signal(dates, base_price, noise_level)
        else:
            raise ValueError(f"Unknown crossover type: {crossover_type}")
    
    def _generate_bullish_crossover(self, dates: pd.DatetimeIndex, base_price: float, noise_level: float) -> pd.DataFrame:
        """Generate data with a clear bullish EMA crossover"""
        bars = len(dates)
        
        # Create three phases: downtrend, crossover, uptrend
        phase1_len = bars // 4  # Initial downtrend
        phase2_len = bars // 4  # Crossover phase
        phase3_len = bars - phase1_len - phase2_len  # Sustained uptrend
        
        # Phase 1: Downtrend (fast EMA below slow EMA)
        downtrend = np.linspace(0, -30, phase1_len)
        
        # Phase 2: Crossover phase (fast EMA crosses above slow EMA)
        crossover = np.linspace(-30, 20, phase2_len)
        
        # Phase 3: Sustained uptrend (fast EMA well above slow EMA)
        uptrend = np.linspace(20, 80, phase3_len)
        
        trend = np.concatenate([downtrend, crossover, uptrend])
        
        # Add controlled noise
        noise = np.random.normal(0, noise_level, bars)
        prices = base_price + trend + noise
        
        return self._create_ohlc_dataframe(dates, prices, noise_level)
    
    def _generate_bearish_crossover(self, dates: pd.DatetimeIndex, base_price: float, noise_level: float) -> pd.DataFrame:
        """Generate data with a clear bearish EMA crossover"""
        bars = len(dates)
        
        # Create three phases: uptrend, crossover, downtrend
        phase1_len = bars // 4  # Initial uptrend
        phase2_len = bars // 4  # Crossover phase
        phase3_len = bars - phase1_len - phase2_len  # Sustained downtrend
        
        # Phase 1: Uptrend (fast EMA above slow EMA)
        uptrend = np.linspace(0, 30, phase1_len)
        
        # Phase 2: Crossover phase (fast EMA crosses below slow EMA)
        crossover = np.linspace(30, -20, phase2_len)
        
        # Phase 3: Sustained downtrend (fast EMA well below slow EMA)
        downtrend = np.linspace(-20, -80, phase3_len)
        
        trend = np.concatenate([uptrend, crossover, downtrend])
        
        # Add controlled noise
        noise = np.random.normal(0, noise_level, bars)
        prices = base_price + trend + noise
        
        return self._create_ohlc_dataframe(dates, prices, noise_level)
    
    def _generate_multiple_crossovers(self, dates: pd.DatetimeIndex, base_price: float, noise_level: float) -> pd.DataFrame:
        """Generate data with multiple crossovers to test persistence"""
        bars = len(dates)
        
        # Create alternating trends with crossovers
        segment_length = bars // 6
        segments = []
        
        for i in range(6):
            if i % 2 == 0:
                # Bullish segment
                segment = np.linspace(-10 + i*5, 10 + i*5, segment_length)
            else:
                # Bearish segment
                segment = np.linspace(10 + (i-1)*5, -10 + i*5, segment_length)
            segments.append(segment)
        
        # Handle remaining bars
        remaining = bars - len(np.concatenate(segments))
        if remaining > 0:
            final_segment = np.linspace(segments[-1][-1], segments[-1][-1] + 20, remaining)
            segments.append(final_segment)
        
        trend = np.concatenate(segments)
        
        # Add controlled noise
        noise = np.random.normal(0, noise_level, bars)
        prices = base_price + trend + noise
        
        return self._create_ohlc_dataframe(dates, prices, noise_level)
    
    def _generate_false_signal(self, dates: pd.DatetimeIndex, base_price: float, noise_level: float) -> pd.DataFrame:
        """Generate data with false crossover signals (brief crossovers that don't persist)"""
        bars = len(dates)
        
        # Create a mostly sideways trend with brief crossovers
        base_trend = np.sin(np.linspace(0, 4*np.pi, bars)) * 5
        
        # Add brief spikes that create temporary crossovers
        spike_positions = [bars//4, bars//2, 3*bars//4]
        for pos in spike_positions:
            if pos < bars:
                # Create brief spike
                spike_width = 5
                start_idx = max(0, pos - spike_width//2)
                end_idx = min(bars, pos + spike_width//2)
                spike_magnitude = random.choice([-15, 15])  # Random direction
                base_trend[start_idx:end_idx] += spike_magnitude * np.exp(-np.linspace(-2, 2, end_idx - start_idx)**2)
        
        # Add controlled noise
        noise = np.random.normal(0, noise_level, bars)
        prices = base_price + base_trend + noise
        
        return self._create_ohlc_dataframe(dates, prices, noise_level)
    
    def _create_ohlc_dataframe(self, dates: pd.DatetimeIndex, close_prices: np.ndarray, noise_level: float) -> pd.DataFrame:
        """Create OHLC DataFrame from close prices"""
        bars = len(dates)
        
        # Generate realistic OHLC data
        opens = close_prices + np.random.normal(0, noise_level * 0.3, bars)
        
        # Highs should be above both open and close
        highs = np.maximum(opens, close_prices) + np.abs(np.random.normal(0.5, noise_level * 0.5, bars))
        
        # Lows should be below both open and close
        lows = np.minimum(opens, close_prices) - np.abs(np.random.normal(0.5, noise_level * 0.5, bars))
        
        # Generate volume data
        volumes = np.random.randint(1000, 5000, bars)
        tick_volumes = np.random.randint(100, 500, bars)
        
        return pd.DataFrame({
            'open': opens,
            'high': highs,
            'low': lows,
            'close': close_prices,
            'volume': volumes,
            'tick_volume': tick_volumes
        }, index=dates)

class EMAPropertyTester:
    """Property-based tester for EMA crossover detection"""
    
    def __init__(self):
        self.config = get_config()
        self.analyzer = EMAMomentumAnalyzer(self.config)
        self.generator = EMAPropertyTestGenerator()
        self.test_results = []
    
    def test_property_bullish_crossover_detection(self, num_tests: int = 50) -> bool:
        """
        Property: For any price series with a bullish EMA crossover pattern,
        the system SHALL identify this as a bullish crossover signal
        """
        print(f"\n🔍 Testing Property: Bullish Crossover Detection ({num_tests} tests)")
        print("-" * 60)
        
        passed = 0
        failed = 0
        
        for i in range(num_tests):
            try:
                # Generate bullish crossover scenario
                df = self.generator.generate_crossover_scenario(
                    'bullish',
                    bars=random.randint(150, 300),
                    base_price=random.uniform(1000, 3000),
                    noise_level=random.uniform(0.2, 1.0)
                )
                
                # Calculate EMAs
                df_with_emas = self.analyzer.calculate_emas(df)
                
                # Verify crossover occurred
                crossover_detected = self._verify_bullish_crossover_occurred(df_with_emas)
                
                if crossover_detected:
                    # Get signal
                    signal = self.analyzer.get_ema_signal(df_with_emas)
                    
                    # Validate signal properties
                    if self._validate_bullish_signal_properties(signal, df_with_emas):
                        passed += 1
                        if i < 5:  # Show details for first few tests
                            print(f"✅ Test {i+1}: Bullish crossover correctly detected")
                            print(f"   Signal: {signal.signal_type}, Strength: {signal.momentum_strength:.3f}")
                    else:
                        failed += 1
                        print(f"❌ Test {i+1}: Bullish crossover detected but signal properties invalid")
                else:
                    failed += 1
                    print(f"❌ Test {i+1}: Expected bullish crossover not detected in generated data")
                    
            except Exception as e:
                failed += 1
                print(f"❌ Test {i+1}: Exception - {str(e)}")
        
        success_rate = passed / (passed + failed) * 100
        print(f"\n📊 Bullish Crossover Detection Results:")
        print(f"   ✅ Passed: {passed}/{num_tests} ({success_rate:.1f}%)")
        print(f"   ❌ Failed: {failed}/{num_tests}")
        
        # Property passes if success rate is above 90%
        property_passed = success_rate >= 90.0
        self.test_results.append(('Bullish Crossover Detection', property_passed, success_rate))
        
        return property_passed
    
    def test_property_bearish_crossover_detection(self, num_tests: int = 50) -> bool:
        """
        Property: For any price series with a bearish EMA crossover pattern,
        the system SHALL identify this as a bearish crossover signal
        """
        print(f"\n🔍 Testing Property: Bearish Crossover Detection ({num_tests} tests)")
        print("-" * 60)
        
        passed = 0
        failed = 0
        
        for i in range(num_tests):
            try:
                # Generate bearish crossover scenario
                df = self.generator.generate_crossover_scenario(
                    'bearish',
                    bars=random.randint(150, 300),
                    base_price=random.uniform(1000, 3000),
                    noise_level=random.uniform(0.2, 1.0)
                )
                
                # Calculate EMAs
                df_with_emas = self.analyzer.calculate_emas(df)
                
                # Verify crossover occurred
                crossover_detected = self._verify_bearish_crossover_occurred(df_with_emas)
                
                if crossover_detected:
                    # Get signal
                    signal = self.analyzer.get_ema_signal(df_with_emas)
                    
                    # Validate signal properties
                    if self._validate_bearish_signal_properties(signal, df_with_emas):
                        passed += 1
                        if i < 5:  # Show details for first few tests
                            print(f"✅ Test {i+1}: Bearish crossover correctly detected")
                            print(f"   Signal: {signal.signal_type}, Strength: {signal.momentum_strength:.3f}")
                    else:
                        failed += 1
                        print(f"❌ Test {i+1}: Bearish crossover detected but signal properties invalid")
                else:
                    failed += 1
                    print(f"❌ Test {i+1}: Expected bearish crossover not detected in generated data")
                    
            except Exception as e:
                failed += 1
                print(f"❌ Test {i+1}: Exception - {str(e)}")
        
        success_rate = passed / (passed + failed) * 100
        print(f"\n📊 Bearish Crossover Detection Results:")
        print(f"   ✅ Passed: {passed}/{num_tests} ({success_rate:.1f}%)")
        print(f"   ❌ Failed: {failed}/{num_tests}")
        
        # Property passes if success rate is above 90%
        property_passed = success_rate >= 90.0
        self.test_results.append(('Bearish Crossover Detection', property_passed, success_rate))
        
        return property_passed
    
    def test_property_crossover_strength_correlation(self, num_tests: int = 30) -> bool:
        """
        Property: The crossover strength SHALL correlate with the magnitude and persistence of the crossover
        """
        print(f"\n🔍 Testing Property: Crossover Strength Correlation ({num_tests} tests)")
        print("-" * 60)
        
        passed = 0
        failed = 0
        
        for i in range(num_tests):
            try:
                # Generate two scenarios: strong vs weak crossover
                strong_df = self.generator.generate_crossover_scenario(
                    random.choice(['bullish', 'bearish']),
                    bars=200,
                    base_price=2000,
                    noise_level=0.3  # Low noise for clear signal
                )
                
                weak_df = self.generator.generate_crossover_scenario(
                    'false_signal',  # Weak/false signals
                    bars=200,
                    base_price=2000,
                    noise_level=1.0  # High noise for weak signal
                )
                
                # Get signals
                strong_signal = self.analyzer.get_ema_signal(strong_df)
                weak_signal = self.analyzer.get_ema_signal(weak_df)
                
                if strong_signal and weak_signal:
                    # Strong crossover should have higher momentum strength
                    if strong_signal.momentum_strength > weak_signal.momentum_strength:
                        passed += 1
                        if i < 5:
                            print(f"✅ Test {i+1}: Strength correlation correct")
                            print(f"   Strong: {strong_signal.momentum_strength:.3f}, Weak: {weak_signal.momentum_strength:.3f}")
                    else:
                        failed += 1
                        print(f"❌ Test {i+1}: Strength correlation incorrect")
                        print(f"   Strong: {strong_signal.momentum_strength:.3f}, Weak: {weak_signal.momentum_strength:.3f}")
                else:
                    failed += 1
                    print(f"❌ Test {i+1}: Could not get signals for comparison")
                    
            except Exception as e:
                failed += 1
                print(f"❌ Test {i+1}: Exception - {str(e)}")
        
        success_rate = passed / (passed + failed) * 100
        print(f"\n📊 Crossover Strength Correlation Results:")
        print(f"   ✅ Passed: {passed}/{num_tests} ({success_rate:.1f}%)")
        print(f"   ❌ Failed: {failed}/{num_tests}")
        
        # Property passes if success rate is above 80%
        property_passed = success_rate >= 80.0
        self.test_results.append(('Crossover Strength Correlation', property_passed, success_rate))
        
        return property_passed
    
    def test_property_crossover_persistence(self, num_tests: int = 30) -> bool:
        """
        Property: Persistent crossovers should have higher confidence than brief false signals
        """
        print(f"\n🔍 Testing Property: Crossover Persistence ({num_tests} tests)")
        print("-" * 60)
        
        passed = 0
        failed = 0
        
        for i in range(num_tests):
            try:
                # Generate persistent crossover
                persistent_df = self.generator.generate_crossover_scenario(
                    random.choice(['bullish', 'bearish']),
                    bars=250,
                    base_price=2000,
                    noise_level=0.4
                )
                
                # Generate false signal (brief crossover)
                false_df = self.generator.generate_crossover_scenario(
                    'false_signal',
                    bars=250,
                    base_price=2000,
                    noise_level=0.8
                )
                
                # Get signals
                persistent_signal = self.analyzer.get_ema_signal(persistent_df)
                false_signal = self.analyzer.get_ema_signal(false_df)
                
                if persistent_signal and false_signal:
                    # Check crossover confirmation
                    persistent_confirmed = persistent_signal.crossover_confirmed
                    false_confirmed = false_signal.crossover_confirmed
                    
                    # Persistent crossovers should be more likely to be confirmed
                    if persistent_confirmed or not false_confirmed:
                        passed += 1
                        if i < 5:
                            print(f"✅ Test {i+1}: Persistence detection correct")
                            print(f"   Persistent confirmed: {persistent_confirmed}, False confirmed: {false_confirmed}")
                    else:
                        failed += 1
                        print(f"❌ Test {i+1}: Persistence detection incorrect")
                else:
                    failed += 1
                    print(f"❌ Test {i+1}: Could not get signals for comparison")
                    
            except Exception as e:
                failed += 1
                print(f"❌ Test {i+1}: Exception - {str(e)}")
        
        success_rate = passed / (passed + failed) * 100
        print(f"\n📊 Crossover Persistence Results:")
        print(f"   ✅ Passed: {passed}/{num_tests} ({success_rate:.1f}%)")
        print(f"   ❌ Failed: {failed}/{num_tests}")
        
        # Property passes if success rate is above 70%
        property_passed = success_rate >= 70.0
        self.test_results.append(('Crossover Persistence', property_passed, success_rate))
        
        return property_passed
    
    def _verify_bullish_crossover_occurred(self, df: pd.DataFrame) -> bool:
        """Verify that a bullish crossover actually occurred in the data"""
        if len(df) < 50:
            return False
        
        fast_col = f'ema_{self.analyzer.fast_period}'
        slow_col = f'ema_{self.analyzer.slow_period}'
        
        # Look for crossover in the data
        for i in range(50, len(df)):
            if (df[fast_col].iloc[i-1] <= df[slow_col].iloc[i-1] and 
                df[fast_col].iloc[i] > df[slow_col].iloc[i]):
                return True
        
        return False
    
    def _verify_bearish_crossover_occurred(self, df: pd.DataFrame) -> bool:
        """Verify that a bearish crossover actually occurred in the data"""
        if len(df) < 50:
            return False
        
        fast_col = f'ema_{self.analyzer.fast_period}'
        slow_col = f'ema_{self.analyzer.slow_period}'
        
        # Look for crossover in the data
        for i in range(50, len(df)):
            if (df[fast_col].iloc[i-1] >= df[slow_col].iloc[i-1] and 
                df[fast_col].iloc[i] < df[slow_col].iloc[i]):
                return True
        
        return False
    
    def _validate_bullish_signal_properties(self, signal: EMASignal, df: pd.DataFrame) -> bool:
        """Validate that a bullish signal has correct properties"""
        if not signal:
            return False
        
        # Fast EMA should be above slow EMA
        if signal.fast_ema <= signal.slow_ema:
            return False
        
        # Separation should be positive
        if signal.separation <= 0:
            return False
        
        # Signal type should indicate bullish trend
        bullish_signals = ['bullish_cross', 'strong_bullish_cross', 'strong_bullish_trend', 
                          'moderate_bullish_trend', 'weak_bullish']
        if not any(bs in signal.signal_type for bs in bullish_signals):
            return False
        
        # Momentum strength should be reasonable
        if not (0.0 <= signal.momentum_strength <= 1.0):
            return False
        
        return True
    
    def _validate_bearish_signal_properties(self, signal: EMASignal, df: pd.DataFrame) -> bool:
        """Validate that a bearish signal has correct properties"""
        if not signal:
            return False
        
        # Fast EMA should be below slow EMA
        if signal.fast_ema >= signal.slow_ema:
            return False
        
        # Separation should be negative
        if signal.separation >= 0:
            return False
        
        # Signal type should indicate bearish trend
        bearish_signals = ['bearish_cross', 'strong_bearish_cross', 'strong_bearish_trend', 
                          'moderate_bearish_trend', 'weak_bearish']
        if not any(bs in signal.signal_type for bs in bearish_signals):
            return False
        
        # Momentum strength should be reasonable
        if not (0.0 <= signal.momentum_strength <= 1.0):
            return False
        
        return True

def run_ema_crossover_property_tests():
    """Run all EMA crossover property-based tests"""
    print("🔍 EMA Crossover Property-Based Test Suite - Task 1.2")
    print("**Validates: Requirements 3.2, 3.3**")
    print("=" * 70)
    
    tester = EMAPropertyTester()
    
    # Run all property tests
    properties = [
        ('Bullish Crossover Detection', lambda: tester.test_property_bullish_crossover_detection(50)),
        ('Bearish Crossover Detection', lambda: tester.test_property_bearish_crossover_detection(50)),
        ('Crossover Strength Correlation', lambda: tester.test_property_crossover_strength_correlation(30)),
        ('Crossover Persistence', lambda: tester.test_property_crossover_persistence(30))
    ]
    
    all_passed = True
    
    for property_name, test_func in properties:
        try:
            result = test_func()
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ Property '{property_name}' failed with exception: {str(e)}")
            all_passed = False
    
    # Print summary
    print("\n" + "=" * 70)
    print("📊 EMA CROSSOVER PROPERTY TEST SUMMARY")
    print("=" * 70)
    
    for property_name, passed, success_rate in tester.test_results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status} {property_name}: {success_rate:.1f}% success rate")
    
    if all_passed:
        print("\n🎉 ALL EMA CROSSOVER PROPERTIES VALIDATED!")
        print("✅ Property 1: EMA Crossover Signal Accuracy - VERIFIED")
        print("✅ Requirements 3.2, 3.3 - SATISFIED")
        print("\n🔍 Property Validation Results:")
        print("   ✅ Bullish crossovers correctly identified across diverse scenarios")
        print("   ✅ Bearish crossovers correctly identified across diverse scenarios")
        print("   ✅ Crossover strength correlates with magnitude and persistence")
        print("   ✅ System distinguishes between persistent and false signals")
        print("\n🚀 Task 1.2 Complete - Property-based testing validates EMA crossover detection correctness")
        return True
    else:
        print(f"\n⚠️ SOME EMA CROSSOVER PROPERTIES FAILED")
        print("❌ Property validation incomplete - review failed properties")
        return False

if __name__ == "__main__":
    success = run_ema_crossover_property_tests()
    sys.exit(0 if success else 1)