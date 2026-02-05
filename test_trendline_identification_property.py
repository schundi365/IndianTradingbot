"""
Property-Based Test for Trendline Identification and Validation
Tests Property 5: Trendline Identification and Validation
Validates: Requirements 5.1, 5.4, 5.6
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
from src.config import get_config

class TestTrendlineIdentificationProperty:
    """Property-based tests for trendline identification and validation"""
    
    def setup_method(self):
        """Setup test environment"""
        self.config = get_config()
        self.analyzer = TrendlineAnalyzer(self.config)
    
    @given(
        data_length=st.integers(min_value=50, max_value=200),
        trend_strength=st.floats(min_value=0.001, max_value=0.01),
        noise_level=st.floats(min_value=0.0001, max_value=0.005),
        swing_count=st.integers(min_value=3, max_value=8)
    )
    @settings(max_examples=50, deadline=10000)
    def test_trendline_identification_consistency(self, data_length, trend_strength, noise_level, swing_count):
        """
        **Property 5: Trendline Identification and Validation**
        **Validates: Requirements 5.1, 5.4, 5.6**
        
        For any price data with identifiable swing points:
        - Trendlines SHALL connect at least 2 significant swing points
        - Trendlines SHALL be validated based on touch points and duration
        - Trendlines with angles too steep (>80°) or too flat (<10°) SHALL be filtered out
        - The system SHALL maintain a maximum number of active trendlines
        """
        # Generate synthetic price data with clear trend and swing points
        df = self._generate_trending_data_with_swings(
            length=data_length,
            trend_strength=trend_strength,
            noise_level=noise_level,
            swing_count=swing_count
        )
        
        # Test trendline identification
        trendlines = self.analyzer.identify_trendlines(df)
        
        # Property 1: Trendlines connect at least 2 significant swing points (Requirement 5.1)
        for trendline in trendlines:
            assert trendline.touch_points >= 2, \
                f"Trendline must connect at least 2 swing points, got {trendline.touch_points}"
        
        # Property 2: Maximum number of trendlines constraint (Requirement 5.6)
        max_allowed = self.analyzer.max_trendlines
        assert len(trendlines) <= max_allowed, \
            f"Number of trendlines ({len(trendlines)}) exceeds maximum ({max_allowed})"
        
        # Property 3: Angle filtering (Requirement 5.6)
        for trendline in trendlines:
            # Validate angle is within acceptable range
            angle_valid = self.analyzer.validate_trendline_angle(trendline)
            assert angle_valid, \
                f"Trendline angle validation failed for slope {trendline.slope}"
        
        # Property 4: Validation based on touch points and duration (Requirement 5.4)
        for trendline in trendlines:
            # All returned trendlines should pass validation
            is_valid = self.analyzer.validate_trendline(trendline, df)
            assert is_valid, \
                f"Returned trendline failed validation: strength={trendline.strength}, touches={trendline.touch_points}"
        
        # Property 5: Strength consistency
        for trendline in trendlines:
            assert 0.0 <= trendline.strength <= 1.0, \
                f"Trendline strength must be between 0 and 1, got {trendline.strength}"
        
        # Property 6: Touch points consistency
        min_touches = self.analyzer.min_trendline_touches
        for trendline in trendlines:
            assert trendline.touch_points >= min_touches, \
                f"Trendline touch points ({trendline.touch_points}) below minimum ({min_touches})"
    
    @given(
        data_length=st.integers(min_value=30, max_value=100),
        base_price=st.floats(min_value=1.0, max_value=100.0),
        volatility=st.floats(min_value=0.001, max_value=0.02)
    )
    @settings(max_examples=30, deadline=8000)
    def test_trendline_validation_properties(self, data_length, base_price, volatility):
        """
        Test trendline validation properties with various market conditions
        """
        # Generate random walk data
        df = self._generate_random_walk_data(data_length, base_price, volatility)
        
        # Identify trendlines
        trendlines = self.analyzer.identify_trendlines(df)
        
        # Test validation filtering
        if trendlines:
            # Test strength filtering
            strong_trendlines = self.analyzer.filter_trendlines_by_strength(trendlines, min_strength=0.6)
            for tl in strong_trendlines:
                assert tl.strength >= 0.6, f"Filtered trendline strength {tl.strength} below threshold"
            
            # Test overlap filtering
            non_overlapping = self.analyzer.filter_overlapping_trendlines(trendlines)
            assert len(non_overlapping) <= len(trendlines), \
                "Overlap filtering should not increase trendline count"
            
            # Test recency filtering
            recent_trendlines = self.analyzer.filter_trendlines_by_recency(trendlines, df)
            assert len(recent_trendlines) <= len(trendlines), \
                "Recency filtering should not increase trendline count"
    
    @given(
        swing_points=st.integers(min_value=2, max_value=6),
        price_range=st.floats(min_value=0.01, max_value=0.1),
        trend_direction=st.sampled_from(['up', 'down'])
    )
    @settings(max_examples=25, deadline=6000)
    def test_trendline_touch_point_validation(self, swing_points, price_range, trend_direction):
        """
        Test that trendlines correctly identify and validate touch points
        """
        # Generate data with known swing points
        df = self._generate_data_with_known_swings(
            swing_count=swing_points,
            price_range=price_range,
            trend_direction=trend_direction
        )
        
        # Identify trendlines
        trendlines = self.analyzer.identify_trendlines(df)
        
        if trendlines:
            for trendline in trendlines:
                # Validate touch points are reasonable
                assert trendline.touch_points >= 2, \
                    "Trendline must have at least 2 touch points"
                
                # Validate strength is reasonable for the number of touches
                expected_min_strength = 0.3 + (trendline.touch_points - 2) * 0.1
                assert trendline.strength >= expected_min_strength * 0.8, \
                    f"Trendline strength {trendline.strength} too low for {trendline.touch_points} touches"
    
    def test_trendline_angle_constraints(self):
        """
        Test that angle constraints are properly enforced
        """
        # Test with very steep trend (should be filtered out)
        steep_df = self._generate_steep_trend_data()
        steep_trendlines = self.analyzer.identify_trendlines(steep_df)
        
        # Test with very flat trend (should be filtered out)
        flat_df = self._generate_flat_trend_data()
        flat_trendlines = self.analyzer.identify_trendlines(flat_df)
        
        # All returned trendlines should have valid angles
        all_trendlines = steep_trendlines + flat_trendlines
        for trendline in all_trendlines:
            angle_valid = self.analyzer.validate_trendline_angle(trendline)
            assert angle_valid, f"Invalid angle for trendline with slope {trendline.slope}"
    
    def test_maximum_trendlines_constraint(self):
        """
        Test that maximum trendlines constraint is enforced
        """
        # Generate data with many potential trendlines
        df = self._generate_complex_data_with_many_swings()
        
        # Identify trendlines
        trendlines = self.analyzer.identify_trendlines(df)
        
        # Should not exceed maximum
        max_allowed = self.analyzer.max_trendlines
        assert len(trendlines) <= max_allowed, \
            f"Trendline count {len(trendlines)} exceeds maximum {max_allowed}"
        
        # If we have the maximum, they should be the strongest ones
        if len(trendlines) == max_allowed:
            # All should have reasonable strength
            for trendline in trendlines:
                assert trendline.strength >= 0.4, \
                    f"Weak trendline {trendline.strength} should not be in top {max_allowed}"
    
    def _generate_trending_data_with_swings(self, length: int, trend_strength: float, 
                                          noise_level: float, swing_count: int) -> pd.DataFrame:
        """Generate synthetic price data with clear trend and swing points"""
        np.random.seed(42)  # For reproducible tests
        
        # Create base trend
        trend = np.linspace(0, trend_strength * length, length)
        
        # Add swing points at regular intervals
        swing_positions = np.linspace(10, length - 10, swing_count, dtype=int)
        swing_magnitudes = np.random.uniform(-0.02, 0.02, swing_count)
        
        # Create price series
        prices = np.ones(length) * 1.0  # Base price of 1.0
        
        # Add trend
        prices += trend
        
        # Add swings
        for i, pos in enumerate(swing_positions):
            swing_width = 5
            for j in range(max(0, pos - swing_width), min(length, pos + swing_width)):
                distance = abs(j - pos)
                swing_effect = swing_magnitudes[i] * (1 - distance / swing_width)
                prices[j] += swing_effect
        
        # Add noise
        noise = np.random.normal(0, noise_level, length)
        prices += noise
        
        # Ensure positive prices
        prices = np.maximum(prices, 0.01)
        
        # Create OHLCV data
        data = []
        for i in range(length):
            base_price = prices[i]
            high = base_price * (1 + np.random.uniform(0, 0.005))
            low = base_price * (1 - np.random.uniform(0, 0.005))
            open_price = base_price * (1 + np.random.uniform(-0.002, 0.002))
            close = base_price
            volume = np.random.uniform(1000, 5000)
            
            data.append({
                'open': open_price,
                'high': high,
                'low': low,
                'close': close,
                'volume': volume
            })
        
        return pd.DataFrame(data)
    
    def _generate_random_walk_data(self, length: int, base_price: float, volatility: float) -> pd.DataFrame:
        """Generate random walk price data"""
        np.random.seed(42)
        
        prices = [base_price]
        for _ in range(length - 1):
            change = np.random.normal(0, volatility)
            new_price = prices[-1] * (1 + change)
            prices.append(max(0.01, new_price))  # Ensure positive prices
        
        data = []
        for i, price in enumerate(prices):
            high = price * (1 + np.random.uniform(0, 0.01))
            low = price * (1 - np.random.uniform(0, 0.01))
            open_price = price * (1 + np.random.uniform(-0.005, 0.005))
            
            data.append({
                'open': open_price,
                'high': high,
                'low': low,
                'close': price,
                'volume': np.random.uniform(1000, 5000)
            })
        
        return pd.DataFrame(data)
    
    def _generate_data_with_known_swings(self, swing_count: int, price_range: float, 
                                       trend_direction: str) -> pd.DataFrame:
        """Generate data with known swing points"""
        length = swing_count * 10 + 20  # Ensure enough data
        base_price = 1.0
        
        # Create swing points
        swing_positions = np.linspace(10, length - 10, swing_count, dtype=int)
        
        prices = np.ones(length) * base_price
        
        # Add trend
        if trend_direction == 'up':
            trend = np.linspace(0, price_range, length)
        else:
            trend = np.linspace(0, -price_range, length)
        
        prices += trend
        
        # Add alternating swings
        for i, pos in enumerate(swing_positions):
            swing_magnitude = price_range * 0.3 * (1 if i % 2 == 0 else -1)
            swing_width = 3
            
            for j in range(max(0, pos - swing_width), min(length, pos + swing_width)):
                distance = abs(j - pos)
                swing_effect = swing_magnitude * (1 - distance / swing_width)
                prices[j] += swing_effect
        
        # Ensure positive prices
        prices = np.maximum(prices, 0.01)
        
        # Create OHLCV data
        data = []
        for price in prices:
            high = price * (1 + np.random.uniform(0, 0.002))
            low = price * (1 - np.random.uniform(0, 0.002))
            open_price = price * (1 + np.random.uniform(-0.001, 0.001))
            
            data.append({
                'open': open_price,
                'high': high,
                'low': low,
                'close': price,
                'volume': np.random.uniform(1000, 3000)
            })
        
        return pd.DataFrame(data)
    
    def _generate_steep_trend_data(self) -> pd.DataFrame:
        """Generate data with very steep trend (should be filtered)"""
        length = 50
        base_price = 1.0
        
        # Very steep uptrend
        steep_trend = np.linspace(0, 0.5, length)  # 50% increase over 50 bars
        prices = np.ones(length) * base_price + steep_trend
        
        data = []
        for price in prices:
            data.append({
                'open': price,
                'high': price * 1.001,
                'low': price * 0.999,
                'close': price,
                'volume': 1000
            })
        
        return pd.DataFrame(data)
    
    def _generate_flat_trend_data(self) -> pd.DataFrame:
        """Generate data with very flat trend (should be filtered)"""
        length = 100
        base_price = 1.0
        
        # Very flat trend
        flat_trend = np.linspace(0, 0.001, length)  # 0.1% increase over 100 bars
        prices = np.ones(length) * base_price + flat_trend
        
        data = []
        for price in prices:
            data.append({
                'open': price,
                'high': price * 1.0005,
                'low': price * 0.9995,
                'close': price,
                'volume': 1000
            })
        
        return pd.DataFrame(data)
    
    def _generate_complex_data_with_many_swings(self) -> pd.DataFrame:
        """Generate complex data with many potential trendlines"""
        length = 150
        base_price = 1.0
        
        # Create multiple overlapping trends and swings
        prices = np.ones(length) * base_price
        
        # Add multiple trend components
        trend1 = np.sin(np.linspace(0, 4 * np.pi, length)) * 0.1
        trend2 = np.cos(np.linspace(0, 2 * np.pi, length)) * 0.05
        trend3 = np.linspace(0, 0.2, length)  # Overall uptrend
        
        prices += trend1 + trend2 + trend3
        
        # Add many swing points
        swing_positions = range(15, length - 15, 10)
        for i, pos in enumerate(swing_positions):
            swing_magnitude = 0.02 * (1 if i % 2 == 0 else -1)
            swing_width = 4
            
            for j in range(max(0, pos - swing_width), min(length, pos + swing_width)):
                distance = abs(j - pos)
                swing_effect = swing_magnitude * (1 - distance / swing_width)
                prices[j] += swing_effect
        
        # Ensure positive prices
        prices = np.maximum(prices, 0.01)
        
        # Create OHLCV data
        data = []
        for price in prices:
            high = price * (1 + np.random.uniform(0, 0.003))
            low = price * (1 - np.random.uniform(0, 0.003))
            open_price = price * (1 + np.random.uniform(-0.001, 0.001))
            
            data.append({
                'open': open_price,
                'high': high,
                'low': low,
                'close': price,
                'volume': np.random.uniform(1000, 4000)
            })
        
        return pd.DataFrame(data)

if __name__ == "__main__":
    # Run a simple test to verify the property
    test_instance = TestTrendlineIdentificationProperty()
    test_instance.setup_method()
    
    print("Running Trendline Identification Property Test...")
    
    # Test with sample data
    df = test_instance._generate_trending_data_with_swings(
        length=100, trend_strength=0.005, noise_level=0.002, swing_count=5
    )
    
    trendlines = test_instance.analyzer.identify_trendlines(df)
    print(f"Identified {len(trendlines)} trendlines")
    
    for i, tl in enumerate(trendlines):
        print(f"  Trendline {i+1}: {tl.line_type}, strength={tl.strength:.3f}, touches={tl.touch_points}")
    
    print("Property test completed successfully!")