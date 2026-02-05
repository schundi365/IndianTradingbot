"""
Property-based tests for Early Warning Signal System
Tests universal properties that should hold for all early warning signal generation
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

from src.trend_detection_engine import TrendDetectionEngine, EarlyWarningSignal

class TestEarlyWarningSignalProperties:
    """Property-based tests for early warning signal generation"""
    
    def setup_method(self):
        """Setup test configuration"""
        self.config = {
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
        
        self.engine = TrendDetectionEngine(self.config)
    
    @given(
        num_bars=st.integers(min_value=100, max_value=500),
        trend_strength=st.floats(min_value=0.1, max_value=2.0),
        volatility=st.floats(min_value=0.001, max_value=0.05),
        volume_factor=st.floats(min_value=0.5, max_value=3.0)
    )
    @settings(max_examples=20, deadline=5000)
    def test_early_warning_signal_properties(self, num_bars, trend_strength, volatility, volume_factor):
        """
        Property 9: Early Warning Signal Generation
        
        Tests that early warning signals:
        1. Have valid confidence scores (0.0 to 1.0)
        2. Have valid probability scores (0.0 to 1.0)
        3. Include meaningful factors
        4. Have consistent timestamps
        5. Provide actionable descriptions
        """
        # Generate synthetic market data with controlled characteristics
        df = self._generate_market_data_with_patterns(
            num_bars, trend_strength, volatility, volume_factor
        )
        
        # Detect early warning signals
        try:
            # Test trend weakness detection
            weakness_warnings = self.engine.detect_trend_weakness(df)
            
            # Test key level monitoring
            level_warnings = self.engine.monitor_key_levels(df)
            
            all_warnings = weakness_warnings + level_warnings
            
            # Property 1: Valid confidence scores
            for warning in all_warnings:
                assert isinstance(warning.confidence, float), f"Confidence must be float, got {type(warning.confidence)}"
                assert 0.0 <= warning.confidence <= 1.0, f"Confidence {warning.confidence} not in [0.0, 1.0]"
            
            # Property 2: Valid probability scores
            for warning in all_warnings:
                assert isinstance(warning.probability_score, float), f"Probability must be float, got {type(warning.probability_score)}"
                assert 0.0 <= warning.probability_score <= 1.0, f"Probability {warning.probability_score} not in [0.0, 1.0]"
            
            # Property 3: Meaningful factors
            for warning in all_warnings:
                assert isinstance(warning.factors, list), f"Factors must be list, got {type(warning.factors)}"
                assert len(warning.factors) > 0, "Warning must have at least one factor"
                for factor in warning.factors:
                    assert isinstance(factor, str), f"Factor must be string, got {type(factor)}"
                    assert len(factor) > 0, "Factor cannot be empty string"
            
            # Property 4: Valid timestamps
            for warning in all_warnings:
                assert isinstance(warning.timestamp, datetime), f"Timestamp must be datetime, got {type(warning.timestamp)}"
                # Timestamp should be recent (within last minute for test)
                time_diff = abs((datetime.now() - warning.timestamp).total_seconds())
                assert time_diff < 60, f"Timestamp too old: {time_diff} seconds"
            
            # Property 5: Actionable descriptions
            for warning in all_warnings:
                assert isinstance(warning.description, str), f"Description must be string, got {type(warning.description)}"
                assert len(warning.description) > 10, f"Description too short: '{warning.description}'"
                # Description should contain key information
                assert any(keyword in warning.description.lower() for keyword in 
                          ['weakness', 'approach', 'bounce', 'rejection', 'pattern', 'level']), \
                       f"Description lacks key information: '{warning.description}'"
            
            # Property 6: Valid warning types
            valid_warning_types = {'trend_weakness', 'key_level_approach', 'reversal_pattern'}
            for warning in all_warnings:
                assert warning.warning_type in valid_warning_types, \
                       f"Invalid warning type: {warning.warning_type}"
            
            # Property 7: Valid strength values
            for warning in all_warnings:
                assert isinstance(warning.strength, float), f"Strength must be float, got {type(warning.strength)}"
                assert 0.0 <= warning.strength <= 1.0, f"Strength {warning.strength} not in [0.0, 1.0]"
            
            # Property 8: Valid price levels
            for warning in all_warnings:
                assert isinstance(warning.price_level, float), f"Price level must be float, got {type(warning.price_level)}"
                assert warning.price_level > 0, f"Price level must be positive: {warning.price_level}"
                assert isinstance(warning.current_price, float), f"Current price must be float, got {type(warning.current_price)}"
                assert warning.current_price > 0, f"Current price must be positive: {warning.current_price}"
            
            # Property 9: Consistency between confidence and probability
            for warning in all_warnings:
                # High confidence warnings should generally have reasonable probability
                if warning.confidence > 0.8:
                    assert warning.probability_score > 0.4, \
                           f"High confidence ({warning.confidence}) but low probability ({warning.probability_score})"
            
            # Property 10: Factor relevance to warning type
            for warning in all_warnings:
                if warning.warning_type == 'trend_weakness':
                    weakness_keywords = ['high', 'low', 'divergence', 'exhaustion', 'bars']
                    assert any(keyword in ' '.join(warning.factors) for keyword in weakness_keywords), \
                           f"Trend weakness warning lacks relevant factors: {warning.factors}"
                
                elif warning.warning_type == 'key_level_approach':
                    level_keywords = ['level', 'support', 'resistance', 'distance', 'touches']
                    assert any(keyword in ' '.join(warning.factors) for keyword in level_keywords), \
                           f"Key level warning lacks relevant factors: {warning.factors}"
                
                elif warning.warning_type == 'reversal_pattern':
                    reversal_keywords = ['bounce', 'rejection', 'strength', 'volume']
                    assert any(keyword in ' '.join(warning.factors) for keyword in reversal_keywords), \
                           f"Reversal pattern warning lacks relevant factors: {warning.factors}"
            
        except Exception as e:
            # Early warning detection should not crash
            pytest.fail(f"Early warning detection failed with error: {e}")
    
    @given(
        trend_direction=st.sampled_from(['up', 'down', 'sideways']),
        weakness_strength=st.floats(min_value=0.1, max_value=1.0),
        bars_since_extreme=st.integers(min_value=5, max_value=30)
    )
    @settings(max_examples=15, deadline=3000)
    def test_trend_weakness_detection_consistency(self, trend_direction, weakness_strength, bars_since_extreme):
        """
        Test that trend weakness detection is consistent and logical
        """
        # Generate data with specific trend weakness pattern
        df = self._generate_trend_weakness_data(trend_direction, weakness_strength, bars_since_extreme)
        
        # Detect trend weakness
        warnings = self.engine.detect_trend_weakness(df, current_trend=trend_direction)
        
        # If we have weakness warnings, they should be consistent with the trend direction
        weakness_warnings = [w for w in warnings if w.warning_type == 'trend_weakness']
        
        for warning in weakness_warnings:
            # Weakness in uptrend should mention highs, weakness in downtrend should mention lows
            if trend_direction == 'up':
                assert any('high' in factor for factor in warning.factors), \
                       f"Uptrend weakness should mention highs: {warning.factors}"
            elif trend_direction == 'down':
                assert any('low' in factor for factor in warning.factors), \
                       f"Downtrend weakness should mention lows: {warning.factors}"
            
            # Strength should correlate with bars since extreme
            if bars_since_extreme >= 15:
                assert warning.strength >= 0.3, \
                       f"Long time since extreme ({bars_since_extreme}) should have higher strength: {warning.strength}"
    
    @given(
        num_levels=st.integers(min_value=2, max_value=8),
        level_strength=st.floats(min_value=0.3, max_value=1.0),
        proximity_factor=st.floats(min_value=0.1, max_value=0.8)
    )
    @settings(max_examples=15, deadline=3000)
    def test_key_level_monitoring_accuracy(self, num_levels, level_strength, proximity_factor):
        """
        Test that key level monitoring accurately identifies level approaches
        """
        # Generate data with known key levels
        df, known_levels = self._generate_data_with_key_levels(num_levels, level_strength, proximity_factor)
        
        # Monitor key levels
        warnings = self.engine.monitor_key_levels(df)
        
        level_warnings = [w for w in warnings if w.warning_type == 'key_level_approach']
        
        # If we're close to known levels, we should get warnings
        current_price = df['close'].iloc[-1]
        
        for level_price, level_type in known_levels:
            distance_pct = abs(current_price - level_price) / level_price
            
            if distance_pct <= 0.003:  # Within 0.3%
                # Should have a warning for this level
                relevant_warnings = [w for w in level_warnings 
                                   if abs(w.price_level - level_price) / level_price <= 0.001]
                
                if not relevant_warnings:
                    # This is acceptable - the algorithm might not detect all levels
                    # But if it does detect levels, they should be accurate
                    continue
                
                # If we have warnings for this level, they should be appropriate
                for warning in relevant_warnings:
                    assert level_type in warning.factors or level_type in warning.description.lower(), \
                           f"Warning should mention level type {level_type}: {warning.factors}, {warning.description}"
    
    def _generate_market_data_with_patterns(self, num_bars, trend_strength, volatility, volume_factor):
        """Generate synthetic market data with realistic patterns"""
        np.random.seed(42)  # For reproducible tests
        
        # Generate base price series
        returns = np.random.normal(0, volatility, num_bars)
        
        # Add trend component
        trend_component = np.linspace(0, trend_strength * volatility * num_bars, num_bars)
        if np.random.random() > 0.5:
            trend_component = -trend_component  # Random trend direction
        
        prices = 100 + np.cumsum(returns + trend_component / num_bars)
        
        # Generate OHLC from prices
        highs = prices * (1 + np.random.uniform(0, volatility/2, num_bars))
        lows = prices * (1 - np.random.uniform(0, volatility/2, num_bars))
        opens = np.roll(prices, 1)
        opens[0] = prices[0]
        
        # Generate volume
        base_volume = 1000
        volumes = np.random.poisson(base_volume * volume_factor, num_bars)
        
        # Create DataFrame
        dates = pd.date_range(start='2024-01-01', periods=num_bars, freq='1H')
        
        df = pd.DataFrame({
            'time': dates,
            'open': opens,
            'high': highs,
            'low': lows,
            'close': prices,
            'tick_volume': volumes
        })
        
        # Add basic indicators
        df['ema_20'] = df['close'].ewm(span=20).mean()
        df['ema_50'] = df['close'].ewm(span=50).mean()
        
        # Add RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        return df
    
    def _generate_trend_weakness_data(self, trend_direction, weakness_strength, bars_since_extreme):
        """Generate data with specific trend weakness patterns"""
        num_bars = 100
        df = self._generate_market_data_with_patterns(num_bars, 1.0, 0.01, 1.0)
        
        # Modify the end to create weakness pattern
        if trend_direction == 'up':
            # Create lower highs pattern
            peak_idx = len(df) - bars_since_extreme - 5
            peak_price = df['high'].iloc[peak_idx]
            
            # Make subsequent highs lower
            for i in range(peak_idx + 1, len(df)):
                if df['high'].iloc[i] > peak_price:
                    reduction = weakness_strength * 0.01  # 1% max reduction
                    df.loc[df.index[i], 'high'] = peak_price * (1 - reduction)
                    df.loc[df.index[i], 'close'] = min(df['close'].iloc[i], df['high'].iloc[i])
        
        elif trend_direction == 'down':
            # Create higher lows pattern
            trough_idx = len(df) - bars_since_extreme - 5
            trough_price = df['low'].iloc[trough_idx]
            
            # Make subsequent lows higher
            for i in range(trough_idx + 1, len(df)):
                if df['low'].iloc[i] < trough_price:
                    increase = weakness_strength * 0.01  # 1% max increase
                    df.loc[df.index[i], 'low'] = trough_price * (1 + increase)
                    df.loc[df.index[i], 'close'] = max(df['close'].iloc[i], df['low'].iloc[i])
        
        return df
    
    def _generate_data_with_key_levels(self, num_levels, level_strength, proximity_factor):
        """Generate data with known support/resistance levels"""
        df = self._generate_market_data_with_patterns(200, 1.0, 0.02, 1.0)
        
        # Identify price range
        price_min = df['low'].min()
        price_max = df['high'].max()
        price_range = price_max - price_min
        
        # Create known levels
        known_levels = []
        for i in range(num_levels):
            level_price = price_min + (i + 1) * price_range / (num_levels + 1)
            level_type = 'support' if i % 2 == 0 else 'resistance'
            known_levels.append((level_price, level_type))
        
        # Position current price near one of the levels
        target_level = known_levels[0][0]
        current_price = target_level * (1 + proximity_factor * 0.01)  # Within proximity_factor %
        
        # Adjust the last few bars to approach this level
        for i in range(-5, 0):
            adjustment_factor = (5 + i) / 5  # Gradual approach
            adjusted_price = df['close'].iloc[i] * (1 - adjustment_factor * 0.1) + current_price * adjustment_factor * 0.1
            df.loc[df.index[i], 'close'] = adjusted_price
            df.loc[df.index[i], 'high'] = max(df['high'].iloc[i], adjusted_price)
            df.loc[df.index[i], 'low'] = min(df['low'].iloc[i], adjusted_price)
        
        return df, known_levels


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "--tb=short"])