"""
Property-Based Test for Trendline Break Detection
Tests Property 6: Trendline Break Detection with Volume Confirmation
Validates: Requirements 5.2, 5.3
"""

import pytest
import pandas as pd
import numpy as np
from hypothesis import given, strategies as st, settings, assume
from datetime import datetime, timedelta
import sys
import os

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.trendline_analyzer import TrendlineAnalyzer
from src.trend_detection_engine import Trendline, TrendlineBreak
from src.config import get_config

class TestTrendlineBreakProperty:
    """Property-based tests for trendline break detection with volume confirmation"""
    
    def setup_method(self):
        """Setup test environment"""
        self.config = get_config()
        self.analyzer = TrendlineAnalyzer(self.config)
    
    @given(
        break_magnitude=st.floats(min_value=0.002, max_value=0.02),
        volume_multiplier=st.floats(min_value=0.5, max_value=3.0),
        data_length=st.integers(min_value=50, max_value=100),
        trendline_type=st.sampled_from(['support', 'resistance'])
    )
    @settings(max_examples=5, deadline=8000)
    def test_trendline_break_detection_with_volume_confirmation(self, break_magnitude, volume_multiplier, 
                                                              data_length, trendline_type):
        """
        **Property 6: Trendline Break Detection with Volume Confirmation**
        **Validates: Requirements 5.2, 5.3**
        
        For any trendline break scenario:
        - WHEN price breaches the trendline with volume above average
        - THEN the system SHALL generate a trendline break signal
        - AND WHEN price retests the broken trendline and holds
        - THEN the system SHALL generate a retest confirmation signal
        - AND break signals without volume confirmation SHALL have reduced confidence
        """
        # Generate data with a clear trendline and subsequent break
        df, trendline = self._generate_data_with_trendline_break(
            length=data_length,
            break_magnitude=break_magnitude,
            volume_multiplier=volume_multiplier,
            trendline_type=trendline_type
        )
        
        # Test break detection
        breaks = self.analyzer.detect_trendline_breaks(df, [trendline])
        
        # Property 1: Break detection with sufficient volume (Requirement 5.2)
        if volume_multiplier >= self.analyzer.volume_confirmation_threshold:
            # Should detect break with volume confirmation
            assert len(breaks) > 0, \
                f"Should detect break with volume multiplier {volume_multiplier:.2f} >= threshold {self.analyzer.volume_confirmation_threshold}"
            
            break_found = breaks[0]
            assert break_found.volume_confirmation, \
                f"Break should be volume confirmed with multiplier {volume_multiplier:.2f}"
            
            # Property 2: Break strength should be reasonable for volume-confirmed breaks
            assert break_found.break_strength >= 0.5, \
                f"Volume-confirmed break strength {break_found.break_strength:.3f} should be >= 0.5"
        
        else:
            # May or may not detect break, but if detected, should have lower confidence
            if breaks:
                break_found = breaks[0]
                if not break_found.volume_confirmation:
                    # Non-volume-confirmed breaks should have reduced strength
                    assert break_found.break_strength <= 0.7, \
                        f"Non-volume-confirmed break strength {break_found.break_strength:.3f} should be <= 0.7"
        
        # Property 3: Break magnitude correlation (Requirement 5.2)
        if breaks:
            break_found = breaks[0]
            # Larger breaks should generally have higher strength
            if break_magnitude > 0.01:  # 1% break
                assert break_found.break_strength >= 0.4, \
                    f"Large break ({break_magnitude:.3f}) should have strength >= 0.4, got {break_found.break_strength:.3f}"
        
        # Property 4: Trendline type consistency
        if breaks:
            break_found = breaks[0]
            assert break_found.trendline.line_type == trendline_type, \
                f"Break trendline type should match original: expected {trendline_type}, got {break_found.trendline.line_type}"
    
    @given(
        retest_distance=st.floats(min_value=0.001, max_value=0.005),
        retest_volume=st.floats(min_value=0.8, max_value=2.0),
        hold_strength=st.floats(min_value=0.5, max_value=1.0)
    )
    @settings(max_examples=5, deadline=6000)
    def test_trendline_retest_confirmation(self, retest_distance, retest_volume, hold_strength):
        """
        Test trendline retest confirmation properties
        """
        # Generate data with trendline break and subsequent retest
        df, trendline = self._generate_data_with_retest_pattern(
            retest_distance=retest_distance,
            retest_volume=retest_volume,
            hold_strength=hold_strength
        )
        
        # Test retest detection
        retest_confirmed = self.analyzer.detect_retest(df, trendline)
        
        # Property 1: Retest detection based on distance and hold strength
        if retest_distance <= self.analyzer.retest_tolerance and hold_strength > 0.7:
            # Should detect retest when price approaches and holds
            assert retest_confirmed, \
                f"Should detect retest with distance {retest_distance:.4f} <= tolerance {self.analyzer.retest_tolerance} and hold strength {hold_strength:.2f}"
        
        # Property 2: Volume influence on retest confirmation
        if retest_volume >= 1.2 and retest_distance <= self.analyzer.retest_tolerance:
            # Higher volume should increase retest detection probability
            # This is probabilistic, so we test the enhanced method
            enhanced_retest = self.analyzer._check_enhanced_retest_confirmation(
                df, trendline.start_point[1], trendline.line_type
            )
            # Enhanced method should be at least as good as basic method
            assert enhanced_retest >= retest_confirmed, \
                "Enhanced retest detection should be at least as good as basic method"
    
    @given(
        data_length=st.integers(min_value=40, max_value=80),
        break_sustainability=st.floats(min_value=0.3, max_value=1.0),
        volume_pattern=st.sampled_from(['increasing', 'decreasing', 'stable'])
    )
    @settings(max_examples=5, deadline=5000)
    def test_break_sustainability_and_volume_patterns(self, data_length, break_sustainability, volume_pattern):
        """
        Test break sustainability and volume pattern analysis
        """
        # Generate data with specific sustainability and volume patterns
        df, trendline = self._generate_data_with_sustainability_pattern(
            length=data_length,
            sustainability=break_sustainability,
            volume_pattern=volume_pattern
        )
        
        # Test enhanced break detection
        breaks = self.analyzer.detect_enhanced_trendline_breaks(df, [trendline])
        
        if breaks:
            break_found = breaks[0]
            
            # Property 1: Sustainability correlation with break strength
            if break_sustainability > 0.8:
                # Highly sustainable breaks should have higher strength
                assert break_found.break_strength >= 0.6, \
                    f"Sustainable break ({break_sustainability:.2f}) should have strength >= 0.6, got {break_found.break_strength:.3f}"
            
            # Property 2: Volume pattern influence
            if volume_pattern == 'increasing':
                # Increasing volume should boost confidence
                assert break_found.break_strength >= 0.5, \
                    f"Break with increasing volume should have strength >= 0.5, got {break_found.break_strength:.3f}"
    
    def test_volume_confirmation_threshold_consistency(self):
        """
        Test that volume confirmation threshold is consistently applied
        """
        # Test with known volume ratios
        test_cases = [
            (1.0, False),   # Below threshold
            (1.4, False),   # Just below threshold (1.5)
            (1.5, True),    # At threshold
            (2.0, True),    # Above threshold
            (3.0, True)     # Well above threshold
        ]
        
        for volume_ratio, expected_confirmation in test_cases:
            df = self._generate_data_with_specific_volume_ratio(volume_ratio)
            
            # Test volume confirmation
            volume_confirmed = self.analyzer._check_volume_confirmation_for_break(df)
            
            assert volume_confirmed == expected_confirmation, \
                f"Volume ratio {volume_ratio} should result in confirmation={expected_confirmation}, got {volume_confirmed}"
    
    def test_break_detection_edge_cases(self):
        """
        Test break detection edge cases and boundary conditions
        """
        # Test case 1: Minimal data
        minimal_df = self._generate_minimal_data()
        minimal_trendline = self._create_simple_trendline()
        
        breaks = self.analyzer.detect_trendline_breaks(minimal_df, [minimal_trendline])
        # Should handle minimal data gracefully
        assert isinstance(breaks, list), "Should return list even with minimal data"
        
        # Test case 2: No volume data
        no_volume_df = self._generate_data_without_volume()
        breaks_no_vol = self.analyzer.detect_trendline_breaks(no_volume_df, [minimal_trendline])
        
        if breaks_no_vol:
            # Without volume data, volume_confirmation should be False
            assert not breaks_no_vol[0].volume_confirmation, \
                "Break without volume data should not be volume confirmed"
        
        # Test case 3: Extreme price movements
        extreme_df = self._generate_data_with_extreme_movements()
        breaks_extreme = self.analyzer.detect_trendline_breaks(extreme_df, [minimal_trendline])
        
        if breaks_extreme:
            # Extreme movements should be detected but with appropriate strength
            assert 0.0 <= breaks_extreme[0].break_strength <= 1.0, \
                f"Break strength should be normalized: {breaks_extreme[0].break_strength}"
    
    def _generate_data_with_trendline_break(self, length: int, break_magnitude: float,
                                          volume_multiplier: float, trendline_type: str) -> tuple:
        """Generate synthetic data with a clear trendline and subsequent break"""
        np.random.seed(42)  # For reproducible tests
        
        base_price = 1.0
        prices = np.ones(length) * base_price
        volumes = np.ones(length) * 1000  # Base volume
        
        # Create trendline pattern
        if trendline_type == 'support':
            # Create uptrend with support line
            trend = np.linspace(0, 0.05, length // 2)  # 5% uptrend
            prices[:length//2] += trend
            
            # Add support touches
            support_level = base_price + 0.01
            touch_positions = [length//4, length//3]
            for pos in touch_positions:
                if pos < length//2:
                    prices[pos] = support_level
            
            # Create break in second half - but make sure it's at the END
            break_start = length - 5  # Break in last 5 bars
            break_price = support_level - (support_level * break_magnitude)
            prices[break_start:] = break_price
            
            # Add volume spike during break - at the END where break detection looks
            volumes[break_start:] *= volume_multiplier
            
            # Create trendline object
            trendline = Trendline(
                start_point=(datetime.now(), support_level),
                end_point=(datetime.now() + timedelta(hours=length//2), support_level + 0.01),
                slope=0.0001,
                touch_points=3,
                strength=0.7,
                line_type='support'
            )
        
        else:  # resistance
            # Create downtrend with resistance line
            trend = np.linspace(0, -0.05, length // 2)  # 5% downtrend
            prices[:length//2] += trend
            
            # Add resistance touches
            resistance_level = base_price + 0.02
            touch_positions = [length//4, length//3]
            for pos in touch_positions:
                if pos < length//2:
                    prices[pos] = resistance_level
            
            # Create break in second half - but make sure it's at the END
            break_start = length - 5  # Break in last 5 bars
            break_price = resistance_level + (resistance_level * break_magnitude)
            prices[break_start:] = break_price
            
            # Add volume spike during break - at the END where break detection looks
            volumes[break_start:] *= volume_multiplier
            
            # Create trendline object
            trendline = Trendline(
                start_point=(datetime.now(), resistance_level),
                end_point=(datetime.now() + timedelta(hours=length//2), resistance_level - 0.01),
                slope=-0.0001,
                touch_points=3,
                strength=0.7,
                line_type='resistance'
            )
        
        # Ensure positive prices
        prices = np.maximum(prices, 0.01)
        
        # Create OHLCV DataFrame
        data = []
        for i in range(length):
            price = prices[i]
            data.append({
                'open': price * (1 + np.random.uniform(-0.001, 0.001)),
                'high': price * (1 + np.random.uniform(0, 0.002)),
                'low': price * (1 - np.random.uniform(0, 0.002)),
                'close': price,
                'volume': volumes[i]
            })
        
        df = pd.DataFrame(data)
        return df, trendline
    
    def _generate_data_with_retest_pattern(self, retest_distance: float, retest_volume: float,
                                         hold_strength: float) -> tuple:
        """Generate data with trendline break and retest pattern"""
        length = 60
        base_price = 1.0
        
        # Create initial trend and break
        df, trendline = self._generate_data_with_trendline_break(
            length=40, break_magnitude=0.01, volume_multiplier=2.0, trendline_type='support'
        )
        
        # Add retest pattern
        trendline_value = trendline.start_point[1]
        retest_price = trendline_value * (1 + retest_distance)
        
        # Create retest bars
        retest_data = []
        for i in range(20):
            if i < 5:  # Approach the level
                price = df.iloc[-1]['close'] + (retest_price - df.iloc[-1]['close']) * (i / 5)
            elif i < 10:  # Touch and test the level
                price = retest_price * (1 + np.random.uniform(-retest_distance/2, retest_distance/2))
            else:  # Hold or reject based on hold_strength
                if np.random.random() < hold_strength:
                    # Hold below (for former support now resistance)
                    price = trendline_value * (1 - retest_distance/2)
                else:
                    # Weak hold
                    price = trendline_value * (1 + retest_distance/4)
            
            volume = 1000 * retest_volume if i < 10 else 1000  # Higher volume during retest
            
            retest_data.append({
                'open': price * (1 + np.random.uniform(-0.001, 0.001)),
                'high': price * (1 + np.random.uniform(0, 0.001)),
                'low': price * (1 - np.random.uniform(0, 0.001)),
                'close': price,
                'volume': volume
            })
        
        # Combine original data with retest data
        retest_df = pd.DataFrame(retest_data)
        combined_df = pd.concat([df, retest_df], ignore_index=True)
        
        return combined_df, trendline
    
    def _generate_data_with_sustainability_pattern(self, length: int, sustainability: float,
                                                 volume_pattern: str) -> tuple:
        """Generate data with specific sustainability and volume patterns"""
        base_price = 1.0
        prices = np.ones(length) * base_price
        volumes = np.ones(length) * 1000
        
        # Create break pattern
        break_start = length // 2
        break_magnitude = 0.015  # 1.5% break
        
        # Apply sustainability
        for i in range(break_start, length):
            if np.random.random() < sustainability:
                # Sustain the break
                prices[i] = base_price * (1 - break_magnitude)
            else:
                # Partial reversion
                prices[i] = base_price * (1 - break_magnitude * 0.5)
        
        # Apply volume pattern
        if volume_pattern == 'increasing':
            volume_trend = np.linspace(1.0, 2.0, length - break_start)
            volumes[break_start:] *= volume_trend
        elif volume_pattern == 'decreasing':
            volume_trend = np.linspace(2.0, 0.8, length - break_start)
            volumes[break_start:] *= volume_trend
        # 'stable' keeps volumes unchanged
        
        # Create trendline
        trendline = Trendline(
            start_point=(datetime.now(), base_price),
            end_point=(datetime.now() + timedelta(hours=length//2), base_price),
            slope=0.0,
            touch_points=2,
            strength=0.6,
            line_type='support'
        )
        
        # Create DataFrame
        data = []
        for i in range(length):
            price = prices[i]
            data.append({
                'open': price,
                'high': price * 1.001,
                'low': price * 0.999,
                'close': price,
                'volume': volumes[i]
            })
        
        df = pd.DataFrame(data)
        return df, trendline
    
    def _generate_data_with_specific_volume_ratio(self, volume_ratio: float) -> pd.DataFrame:
        """Generate data with specific volume ratio for testing thresholds"""
        length = 25
        base_volume = 1000
        
        data = []
        for i in range(length):
            if i >= length - 3:  # Last 3 bars have the specified volume ratio
                volume = base_volume * volume_ratio
            else:
                volume = base_volume
            
            price = 1.0 + np.random.uniform(-0.01, 0.01)
            data.append({
                'open': price,
                'high': price * 1.001,
                'low': price * 0.999,
                'close': price,
                'volume': volume
            })
        
        return pd.DataFrame(data)
    
    def _generate_minimal_data(self) -> pd.DataFrame:
        """Generate minimal data for edge case testing"""
        data = []
        for i in range(3):  # Very minimal data
            price = 1.0
            data.append({
                'open': price,
                'high': price,
                'low': price,
                'close': price,
                'volume': 1000
            })
        
        return pd.DataFrame(data)
    
    def _generate_data_without_volume(self) -> pd.DataFrame:
        """Generate data without volume column"""
        data = []
        for i in range(20):
            price = 1.0 + np.random.uniform(-0.01, 0.01)
            data.append({
                'open': price,
                'high': price * 1.001,
                'low': price * 0.999,
                'close': price
                # No volume column
            })
        
        return pd.DataFrame(data)
    
    def _generate_data_with_extreme_movements(self) -> pd.DataFrame:
        """Generate data with extreme price movements"""
        data = []
        base_price = 1.0
        
        for i in range(30):
            if i < 15:
                price = base_price
            else:
                # Extreme movement
                price = base_price * 1.5  # 50% jump
            
            data.append({
                'open': price,
                'high': price * 1.01,
                'low': price * 0.99,
                'close': price,
                'volume': 1000
            })
        
        return pd.DataFrame(data)
    
    def _create_simple_trendline(self) -> Trendline:
        """Create a simple trendline for testing"""
        return Trendline(
            start_point=(datetime.now(), 1.0),
            end_point=(datetime.now() + timedelta(hours=10), 1.01),
            slope=0.001,
            touch_points=2,
            strength=0.5,
            line_type='support'
        )

if __name__ == "__main__":
    # Run a simple test to verify the property
    test_instance = TestTrendlineBreakProperty()
    test_instance.setup_method()
    
    print("Running Trendline Break Detection Property Test...")
    
    # Test with sample data
    df, trendline = test_instance._generate_data_with_trendline_break(
        length=60, break_magnitude=0.01, volume_multiplier=2.0, trendline_type='support'
    )
    
    breaks = test_instance.analyzer.detect_trendline_breaks(df, [trendline])
    print(f"Detected {len(breaks)} trendline breaks")
    
    if breaks:
        break_info = breaks[0]
        print(f"  Break strength: {break_info.break_strength:.3f}")
        print(f"  Volume confirmed: {break_info.volume_confirmation}")
        print(f"  Retest confirmed: {break_info.retest_confirmed}")
    
    print("Property test completed successfully!")