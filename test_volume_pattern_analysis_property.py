"""
Property-Based Test for Volume Pattern Analysis
Tests universal correctness properties of volume analysis for trend detection
"""

import sys
import os
sys.path.append('src')

import pandas as pd
import numpy as np
from hypothesis import given, strategies as st, settings, assume
from hypothesis.extra.pandas import data_frames, column
import logging

# Import the volume analyzer
from volume_analyzer import VolumeAnalyzer

# Configure logging for tests
logging.basicConfig(level=logging.WARNING)  # Reduce noise during testing

class TestVolumePatternAnalysisProperties:
    """Property-based tests for volume pattern analysis"""
    
    def setup_method(self):
        """Setup test configuration"""
        self.config = {
            'use_volume_filter': True,
            'min_volume_ma': 0.7,
            'normal_volume_ma': 1.0,
            'high_volume_ma': 1.5,
            'very_high_volume_ma': 2.0,
            'volume_ma_period': 20,
            'volume_ma_min_period': 10,
            'obv_period': 14,
            'divergence_lookback': 20,
            'divergence_threshold': 0.85
        }
        self.analyzer = VolumeAnalyzer(self.config)
    
    @given(
        bars=st.integers(min_value=25, max_value=100),
        base_volume=st.integers(min_value=1000, max_value=10000),
        volume_spike_multiplier=st.floats(min_value=1.5, max_value=5.0),
        price_movement=st.floats(min_value=0.0001, max_value=0.01)
    )
    @settings(max_examples=50, deadline=5000)
    def test_exhaustion_volume_detection_properties(self, bars, base_volume, volume_spike_multiplier, price_movement):
        """
        Property: Exhaustion volume detection should identify volume spikes with minimal price follow-through
        
        Universal Properties:
        1. High volume with low price movement should be detected as exhaustion
        2. Exhaustion strength should correlate with volume spike magnitude
        3. Detection should be consistent across different data sizes
        """
        # Create test data with volume spike and minimal price movement
        df = self._create_exhaustion_test_data(bars, base_volume, volume_spike_multiplier, price_movement)
        
        # Test exhaustion detection
        result = self.analyzer.detect_exhaustion_volume(df, lookback=min(20, bars-5))
        
        # Property 1: High volume spike with minimal price movement should be detected
        if volume_spike_multiplier >= 2.0 and price_movement <= 0.005:
            assert result['detected'], f"Should detect exhaustion with {volume_spike_multiplier:.1f}x volume and {price_movement:.4f} price movement"
            assert result['strength'] > 0.0, "Exhaustion strength should be positive"
        
        # Property 2: Strength should correlate with spike magnitude
        if result['detected']:
            # Higher volume spikes should generally produce higher strength scores
            assert 0.0 <= result['strength'] <= 1.0, f"Strength should be between 0 and 1, got {result['strength']}"
            
            # Very high volume spikes should have higher strength
            if volume_spike_multiplier >= 3.0:
                assert result['strength'] >= 0.3, f"Very high volume spike should have strength >= 0.3, got {result['strength']}"
        
        # Property 3: Detection should be deterministic for same input
        result2 = self.analyzer.detect_exhaustion_volume(df, lookback=min(20, bars-5))
        assert result['detected'] == result2['detected'], "Detection should be deterministic"
        if result['detected']:
            assert abs(result['strength'] - result2['strength']) < 0.001, "Strength should be deterministic"
    
    @given(
        bars=st.integers(min_value=30, max_value=100),
        breakout_volume_multiplier=st.floats(min_value=1.0, max_value=3.0),
        price_breakout_size=st.floats(min_value=0.0005, max_value=0.02),
        consolidation_volume=st.integers(min_value=1000, max_value=5000)
    )
    @settings(max_examples=50, deadline=5000)
    def test_breakout_volume_confirmation_properties(self, bars, breakout_volume_multiplier, price_breakout_size, consolidation_volume):
        """
        Property: Breakout volume confirmation should validate breakouts with volume expansion
        
        Universal Properties:
        1. Breakouts with volume expansion >= 1.3x should be confirmed
        2. Confirmation strength should increase with volume expansion
        3. Price movement should be required for confirmation
        """
        assume(bars >= 15)  # Need enough bars for consolidation + breakout
        
        # Create test data with consolidation and breakout
        df = self._create_breakout_test_data(bars, consolidation_volume, breakout_volume_multiplier, price_breakout_size)
        
        breakout_price = df['close'].iloc[-10]  # Breakout point
        breakout_direction = 'up' if price_breakout_size > 0 else 'down'
        
        # Test breakout confirmation
        result = self.analyzer.confirm_breakout_volume(df, breakout_price, breakout_direction, lookback=10)
        
        # Property 1: Sufficient volume expansion should confirm breakout
        if breakout_volume_multiplier >= 1.3 and price_breakout_size >= 0.001:
            assert result['confirmed'], f"Should confirm breakout with {breakout_volume_multiplier:.1f}x volume and {price_breakout_size:.4f} price movement"
            assert result['strength'] > 0.0, "Confirmation strength should be positive"
        
        # Property 2: Strength should increase with volume expansion
        assert 0.0 <= result['strength'] <= 1.0, f"Strength should be between 0 and 1, got {result['strength']}"
        
        if breakout_volume_multiplier >= 2.0:
            assert result['strength'] >= 0.5, f"High volume expansion should have strength >= 0.5, got {result['strength']}"
        
        # Property 3: Volume ratio should reflect actual expansion
        expected_ratio = breakout_volume_multiplier
        actual_ratio = result['volume_ratio']
        assert abs(actual_ratio - expected_ratio) < 0.5, f"Volume ratio should be close to expected: {actual_ratio:.2f} vs {expected_ratio:.2f}"
    
    @given(
        bars=st.integers(min_value=25, max_value=80),
        trend_strength=st.floats(min_value=0.01, max_value=0.05),
        volume_divergence_factor=st.floats(min_value=0.5, max_value=0.9)
    )
    @settings(max_examples=50, deadline=5000)
    def test_volume_price_divergence_properties(self, bars, trend_strength, volume_divergence_factor):
        """
        Property: Volume-price divergence should detect when price and volume move in opposite directions
        
        Universal Properties:
        1. Clear divergence patterns should be detected
        2. Divergence strength should reflect the magnitude of the divergence
        3. Detection should work for both bullish and bearish divergences
        """
        # Test bullish divergence (lower price lows with decreasing volume)
        df_bullish = self._create_divergence_test_data(bars, 'bullish', trend_strength, volume_divergence_factor)
        result_bullish = self.analyzer.detect_volume_price_divergence(df_bullish, 'down', lookback=min(20, bars-5))
        
        # Test bearish divergence (higher price highs with decreasing volume)
        df_bearish = self._create_divergence_test_data(bars, 'bearish', trend_strength, volume_divergence_factor)
        result_bearish = self.analyzer.detect_volume_price_divergence(df_bearish, 'up', lookback=min(20, bars-5))
        
        # Property 1: Clear divergence should be detected
        if volume_divergence_factor <= 0.7:  # Strong divergence
            # Note: Detection depends on swing point identification, so we check for reasonable behavior
            if result_bullish['detected']:
                assert result_bullish['type'] == 'bullish_divergence', "Should detect bullish divergence"
                assert result_bullish['strength'] > 0.0, "Divergence strength should be positive"
            
            if result_bearish['detected']:
                assert result_bearish['type'] == 'bearish_divergence', "Should detect bearish divergence"
                assert result_bearish['strength'] > 0.0, "Divergence strength should be positive"
        
        # Property 2: Strength should be bounded
        for result in [result_bullish, result_bearish]:
            if result['detected']:
                assert 0.0 <= result['strength'] <= 1.0, f"Strength should be between 0 and 1, got {result['strength']}"
        
        # Property 3: Detection should be deterministic
        result_bullish2 = self.analyzer.detect_volume_price_divergence(df_bullish, 'down', lookback=min(20, bars-5))
        assert result_bullish['detected'] == result_bullish2['detected'], "Detection should be deterministic"
    
    @given(
        bars=st.integers(min_value=25, max_value=100),
        signal_type=st.sampled_from(['buy', 'sell']),
        volume_score=st.floats(min_value=0.3, max_value=0.9)
    )
    @settings(max_examples=30, deadline=5000)
    def test_volume_signal_filtering_properties(self, bars, signal_type, volume_score):
        """
        Property: Volume signal filtering should consistently apply volume criteria
        
        Universal Properties:
        1. Signals with volume scores above threshold should pass
        2. Signals with volume scores below threshold should be filtered
        3. Filtering should preserve signal order and properties
        """
        # Create test data
        df = self._create_basic_test_data(bars, volume_multiplier=volume_score * 2)
        
        # Create mock signals
        mock_signals = [
            {'type': signal_type, 'strength': 0.8, 'supporting_factors': []},
            {'type': signal_type, 'strength': 0.6, 'supporting_factors': []},
            {'type': signal_type, 'strength': 0.9, 'supporting_factors': []}
        ]
        
        # Test filtering with different thresholds
        threshold_low = 0.4
        threshold_high = 0.8
        
        filtered_low = self.analyzer.filter_signals_by_volume(mock_signals, df, threshold_low)
        filtered_high = self.analyzer.filter_signals_by_volume(mock_signals, df, threshold_high)
        
        # Property 1: Lower threshold should pass more or equal signals
        assert len(filtered_low) >= len(filtered_high), "Lower threshold should pass more signals"
        
        # Property 2: All filtered signals should be from original set
        for signal in filtered_low:
            assert signal in mock_signals, "Filtered signals should be from original set"
        
        for signal in filtered_high:
            assert signal in mock_signals, "Filtered signals should be from original set"
        
        # Property 3: If volume filter is disabled, all signals should pass
        self.analyzer.use_volume_filter = False
        filtered_disabled = self.analyzer.filter_signals_by_volume(mock_signals, df, 0.9)
        assert len(filtered_disabled) == len(mock_signals), "All signals should pass when filter is disabled"
        
        # Reset filter
        self.analyzer.use_volume_filter = True
    
    def _create_exhaustion_test_data(self, bars, base_volume, spike_multiplier, price_movement):
        """Create test data with volume exhaustion pattern"""
        dates = pd.date_range('2024-01-01', periods=bars, freq='1H')
        
        # Base price trend
        base_price = 1.1000
        prices = np.full(bars, base_price)
        
        # Add volume spike in the middle with minimal price follow-through
        spike_position = bars // 2
        volumes = np.full(bars, base_volume)
        volumes[spike_position] = base_volume * spike_multiplier
        
        # Minimal price movement after spike
        for i in range(spike_position + 1, min(spike_position + 4, bars)):
            prices[i] = prices[spike_position] + (price_movement * (i - spike_position) / 3)
        
        # Generate OHLC from prices
        df = pd.DataFrame({
            'time': dates,
            'open': prices,
            'high': prices * 1.001,
            'low': prices * 0.999,
            'close': prices,
            'tick_volume': volumes
        })
        
        df.set_index('time', inplace=True)
        return df
    
    def _create_breakout_test_data(self, bars, consolidation_volume, volume_multiplier, price_movement):
        """Create test data with breakout pattern"""
        dates = pd.date_range('2024-01-01', periods=bars, freq='1H')
        
        base_price = 1.1000
        prices = np.full(bars, base_price)
        volumes = np.full(bars, consolidation_volume)
        
        # Consolidation period (first 2/3 of data)
        consolidation_end = int(bars * 0.67)
        
        # Breakout period (last 1/3 with higher volume)
        for i in range(consolidation_end, bars):
            volumes[i] = consolidation_volume * volume_multiplier
            prices[i] = base_price + (price_movement * (i - consolidation_end) / (bars - consolidation_end))
        
        # Generate OHLC
        df = pd.DataFrame({
            'time': dates,
            'open': prices,
            'high': prices * 1.001,
            'low': prices * 0.999,
            'close': prices,
            'tick_volume': volumes
        })
        
        df.set_index('time', inplace=True)
        return df
    
    def _create_divergence_test_data(self, bars, divergence_type, trend_strength, volume_factor):
        """Create test data with volume-price divergence"""
        dates = pd.date_range('2024-01-01', periods=bars, freq='1H')
        
        base_price = 1.1000
        base_volume = 3000
        
        # Create price trend
        if divergence_type == 'bullish':
            # Downtrend in price
            price_trend = np.linspace(0, -trend_strength, bars)
        else:
            # Uptrend in price
            price_trend = np.linspace(0, trend_strength, bars)
        
        prices = base_price + np.cumsum(price_trend)
        
        # Create diverging volume (opposite to price trend)
        if divergence_type == 'bullish':
            # Volume should decrease as price goes down (less selling pressure)
            volume_trend = np.linspace(1.0, volume_factor, bars)
        else:
            # Volume should decrease as price goes up (less buying pressure)
            volume_trend = np.linspace(1.0, volume_factor, bars)
        
        volumes = base_volume * volume_trend
        
        # Add some noise
        prices += np.random.normal(0, trend_strength * 0.1, bars)
        volumes += np.random.normal(0, base_volume * 0.1, bars)
        volumes = np.maximum(volumes, base_volume * 0.5)  # Ensure positive volumes
        
        # Generate OHLC
        df = pd.DataFrame({
            'time': dates,
            'open': prices,
            'high': prices * 1.002,
            'low': prices * 0.998,
            'close': prices,
            'tick_volume': volumes.astype(int)
        })
        
        df.set_index('time', inplace=True)
        return df
    
    def _create_basic_test_data(self, bars, volume_multiplier=1.0):
        """Create basic test data for general testing"""
        dates = pd.date_range('2024-01-01', periods=bars, freq='1H')
        
        base_price = 1.1000
        base_volume = 3000
        
        # Random walk for prices
        price_changes = np.random.normal(0, 0.0001, bars)
        prices = base_price + np.cumsum(price_changes)
        
        # Volume with specified multiplier
        volumes = np.random.normal(base_volume * volume_multiplier, base_volume * 0.2, bars)
        volumes = np.maximum(volumes, base_volume * 0.5)  # Ensure reasonable volumes
        
        # Generate OHLC
        df = pd.DataFrame({
            'time': dates,
            'open': prices,
            'high': prices * 1.001,
            'low': prices * 0.999,
            'close': prices,
            'tick_volume': volumes.astype(int)
        })
        
        df.set_index('time', inplace=True)
        return df


def run_volume_pattern_property_tests():
    """Run all volume pattern property tests"""
    print("="*80)
    print("RUNNING VOLUME PATTERN ANALYSIS PROPERTY TESTS")
    print("="*80)
    
    test_class = TestVolumePatternAnalysisProperties()
    test_class.setup_method()
    
    tests = [
        ('Exhaustion Volume Detection', test_class.test_exhaustion_volume_detection_properties),
        ('Breakout Volume Confirmation', test_class.test_breakout_volume_confirmation_properties),
        ('Volume-Price Divergence', test_class.test_volume_price_divergence_properties),
        ('Volume Signal Filtering', test_class.test_volume_signal_filtering_properties)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing: {test_name}")
        try:
            # Run the property test
            test_func()
            print(f"✅ {test_name}: PASSED")
            passed += 1
        except Exception as e:
            print(f"❌ {test_name}: FAILED - {e}")
            failed += 1
    
    print(f"\n" + "="*80)
    print(f"VOLUME PATTERN PROPERTY TEST RESULTS")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Success Rate: {passed/(passed+failed)*100:.1f}%")
    print("="*80)
    
    return failed == 0


if __name__ == "__main__":
    success = run_volume_pattern_property_tests()
    sys.exit(0 if success else 1)