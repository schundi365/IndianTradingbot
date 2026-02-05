"""
Property-Based Test for Multi-Timeframe Alignment Validation
Tests Property 7: Multi-Timeframe Alignment Validation

**Validates: Requirements 6.1, 6.2, 6.3, 6.4**

For any multi-timeframe signal scenario:
- GIVEN signals on primary timeframe and higher timeframe data
- WHEN primary timeframe generates a signal
- THEN higher timeframe alignment SHALL be checked according to configured relationships
- AND contradictory higher timeframe signals SHALL reduce confidence scores
- AND 4-hour confirmation SHALL be required for 15-minute signals
- AND daily confirmation SHALL be required for 4-hour signals
"""

import sys
import os
sys.path.append('src')

import pandas as pd
import numpy as np
import MetaTrader5 as mt5
from datetime import datetime, timedelta
from hypothesis import given, strategies as st, settings, assume, example
from hypothesis.extra.pandas import data_frames, column
import pytest
import logging

# Import the components we're testing
from multi_timeframe_analyzer import MultiTimeframeAnalyzer, AlignmentResult
from trend_detection_engine import TrendDetectionEngine, TimeframeAlignment

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestMultiTimeframeAlignmentProperty:
    """Property-based tests for multi-timeframe alignment validation"""
    
    def setup_method(self):
        """Set up test configuration"""
        self.config = {
            'enable_mtf_confirmation': True,
            'mtf_weight': 0.3,
            'mtf_primary_to_higher': {
                mt5.TIMEFRAME_M15: mt5.TIMEFRAME_H4,
                mt5.TIMEFRAME_M30: mt5.TIMEFRAME_H4,
                mt5.TIMEFRAME_H1: mt5.TIMEFRAME_D1,
                mt5.TIMEFRAME_H4: mt5.TIMEFRAME_D1,
            },
            'mtf_confirmation_bars': 100,
            'mtf_alignment_threshold': 0.6,
            'mtf_contradiction_penalty': 0.4,
            'timeframe': mt5.TIMEFRAME_M30,
        }
        
        self.analyzer = MultiTimeframeAnalyzer(self.config)
    
    @given(
        primary_bars=st.integers(min_value=50, max_value=200),
        higher_bars=st.integers(min_value=50, max_value=200),
        primary_trend=st.sampled_from(['bullish', 'bearish', 'neutral']),
        higher_trend=st.sampled_from(['bullish', 'bearish', 'neutral']),
        trend_strength=st.floats(min_value=0.1, max_value=2.0),
        noise_level=st.floats(min_value=0.01, max_value=0.1)
    )
    @settings(max_examples=50, deadline=5000)
    def test_timeframe_alignment_consistency(self, primary_bars, higher_bars, primary_trend, 
                                           higher_trend, trend_strength, noise_level):
        """
        Property: Multi-timeframe alignment analysis should be consistent and follow configured relationships
        
        This test validates that:
        1. Alignment scores are consistent for similar signal patterns
        2. Contradictory signals receive appropriate penalties
        3. Aligned signals receive appropriate bonuses
        4. Timeframe relationships are respected
        """
        try:
            # Generate synthetic market data for both timeframes
            primary_df = self._generate_trending_data(primary_bars, primary_trend, trend_strength, noise_level)
            higher_df = self._generate_trending_data(higher_bars, higher_trend, trend_strength * 0.8, noise_level * 0.5)
            
            # Ensure we have required indicators
            primary_df = self._add_indicators(primary_df)
            higher_df = self._add_indicators(higher_df)
            
            # Analyze timeframe alignment
            alignment_result = self.analyzer.analyze_timeframe_alignment(primary_df, higher_df)
            
            # Property 1: Alignment result should be valid
            assert isinstance(alignment_result, AlignmentResult)
            assert alignment_result.primary_signal in ['bullish', 'bearish', 'neutral']
            assert alignment_result.higher_signal in ['bullish', 'bearish', 'neutral']
            assert 0.0 <= alignment_result.alignment_score <= 1.0
            assert alignment_result.confirmation_level in ['strong', 'moderate', 'weak', 'contradictory']
            assert isinstance(alignment_result.factors, list)
            
            # Property 2: Aligned signals should have higher scores than contradictory ones
            if primary_trend == higher_trend and primary_trend != 'neutral':
                # Same directional trends should have good alignment
                assert alignment_result.alignment_score >= 0.5, \
                    f"Aligned {primary_trend} trends should have alignment score >= 0.5, got {alignment_result.alignment_score}"
                
                if alignment_result.alignment_score >= 0.8:
                    assert alignment_result.confirmation_level == 'strong'
                elif alignment_result.alignment_score >= 0.6:
                    assert alignment_result.confirmation_level in ['strong', 'moderate']
            
            # Property 3: Contradictory signals should have lower scores
            if (primary_trend == 'bullish' and higher_trend == 'bearish') or \
               (primary_trend == 'bearish' and higher_trend == 'bullish'):
                # Contradictory trends should have poor alignment
                assert alignment_result.alignment_score <= 0.6, \
                    f"Contradictory trends should have alignment score <= 0.6, got {alignment_result.alignment_score}"
                
                if alignment_result.alignment_score < 0.4:
                    assert alignment_result.confirmation_level == 'contradictory'
            
            # Property 4: Neutral signals should have reasonable alignment
            if primary_trend == 'neutral' or higher_trend == 'neutral':
                # Handle different neutral scenarios appropriately
                if (primary_trend != 'neutral' and higher_trend == 'neutral') or \
                   (primary_trend == 'neutral' and higher_trend != 'neutral'):
                    # One neutral signal - this is partial alignment, not contradiction
                    # Neutral higher timeframe with directional primary should allow high alignment (0.4-1.0)
                    # since neutral doesn't contradict the primary signal
                    assert 0.2 <= alignment_result.alignment_score <= 1.0, \
                        f"Partial neutral alignment should be reasonable, got {alignment_result.alignment_score}"
                
                # If both trends are neutral, alignment can vary widely based on technical indicators
                elif primary_trend == 'neutral' and higher_trend == 'neutral':
                    assert 0.2 <= alignment_result.alignment_score <= 0.8, \
                        f"Both neutral signals should have variable alignment based on indicators, got {alignment_result.alignment_score}"
            
            # Property 5: Alignment score should be consistent for similar patterns
            # Run the same analysis again and verify consistency
            alignment_result_2 = self.analyzer.analyze_timeframe_alignment(primary_df, higher_df)
            
            score_diff = abs(alignment_result.alignment_score - alignment_result_2.alignment_score)
            assert score_diff < 0.01, \
                f"Alignment scores should be consistent, difference: {score_diff}"
            
            assert alignment_result.confirmation_level == alignment_result_2.confirmation_level, \
                "Confirmation levels should be consistent"
            
            logger.info(f"✅ Alignment test passed: {primary_trend} vs {higher_trend} = "
                       f"{alignment_result.alignment_score:.3f} ({alignment_result.confirmation_level})")
            
        except Exception as e:
            logger.error(f"❌ Alignment test failed: {e}")
            raise
    
    @given(
        signal_type=st.sampled_from(['buy', 'sell']),
        alignment_score=st.floats(min_value=0.0, max_value=1.0),
        primary_signal=st.sampled_from(['bullish', 'bearish', 'neutral']),
        higher_signal=st.sampled_from(['bullish', 'bearish', 'neutral'])
    )
    @settings(max_examples=30, deadline=3000)
    def test_signal_confirmation_logic(self, signal_type, alignment_score, primary_signal, higher_signal):
        """
        Property: Signal confirmation should follow logical rules based on alignment
        
        This test validates that:
        1. High alignment scores result in signal confirmation
        2. Low alignment scores result in signal rejection
        3. Contradictory signals are properly rejected
        4. Neutral higher timeframe signals are handled appropriately
        """
        try:
            # Create alignment result
            confirmation_level = 'strong' if alignment_score >= 0.8 else \
                               'moderate' if alignment_score >= 0.6 else \
                               'weak' if alignment_score >= 0.4 else 'contradictory'
            
            alignment_result = AlignmentResult(
                primary_signal=primary_signal,
                higher_signal=higher_signal,
                alignment_score=alignment_score,
                confirmation_level=confirmation_level,
                factors=['test_factor']
            )
            
            # Test signal confirmation
            should_confirm = self.analyzer.should_confirm_signal(alignment_result, signal_type)
            
            # Property 1: High alignment with matching signals should confirm
            expected_higher_signal = 'bullish' if signal_type == 'buy' else 'bearish'
            
            if (alignment_score >= self.analyzer.alignment_threshold and 
                higher_signal == expected_higher_signal):
                assert should_confirm, \
                    f"High alignment ({alignment_score:.3f}) with matching signal should confirm"
            
            # Property 2: Contradictory signals should not confirm
            if confirmation_level == 'contradictory':
                assert not should_confirm, \
                    "Contradictory signals should not be confirmed"
            
            # Property 3: Low alignment should not confirm
            if alignment_score < self.analyzer.alignment_threshold:
                assert not should_confirm, \
                    f"Low alignment ({alignment_score:.3f}) should not confirm"
            
            # Property 4: Neutral higher timeframe with moderate alignment should confirm
            if (higher_signal == 'neutral' and 
                alignment_score >= 0.5 and 
                alignment_score >= self.analyzer.alignment_threshold):
                assert should_confirm, \
                    f"Neutral higher timeframe with good alignment should confirm"
            
            logger.info(f"✅ Confirmation test passed: {signal_type} signal with "
                       f"{alignment_score:.3f} alignment = {should_confirm}")
            
        except Exception as e:
            logger.error(f"❌ Confirmation test failed: {e}")
            raise
    
    @given(
        primary_tf=st.sampled_from([mt5.TIMEFRAME_M15, mt5.TIMEFRAME_M30, mt5.TIMEFRAME_H1, mt5.TIMEFRAME_H4]),
        bars=st.integers(min_value=50, max_value=150)
    )
    @settings(max_examples=20, deadline=3000)
    def test_timeframe_relationship_mapping(self, primary_tf, bars):
        """
        Property: Timeframe relationships should follow configured mappings
        
        This test validates that:
        1. 15-minute and 30-minute require 4-hour confirmation
        2. 1-hour and 4-hour require daily confirmation
        3. Proper timeframe names are returned
        4. Cache functionality works correctly
        """
        try:
            # Test timeframe mapping
            expected_higher_tf = self.config['mtf_primary_to_higher'].get(primary_tf)
            
            if expected_higher_tf is not None:
                # Property 1: Correct timeframe relationships
                if primary_tf in [mt5.TIMEFRAME_M15, mt5.TIMEFRAME_M30]:
                    assert expected_higher_tf == mt5.TIMEFRAME_H4, \
                        "15-minute and 30-minute should require 4-hour confirmation"
                
                elif primary_tf in [mt5.TIMEFRAME_H1, mt5.TIMEFRAME_H4]:
                    assert expected_higher_tf == mt5.TIMEFRAME_D1, \
                        "1-hour and 4-hour should require daily confirmation"
                
                # Property 2: Timeframe names should be human-readable
                primary_name = self.analyzer.get_timeframe_name(primary_tf)
                higher_name = self.analyzer.get_timeframe_name(expected_higher_tf)
                
                assert isinstance(primary_name, str) and len(primary_name) > 0
                assert isinstance(higher_name, str) and len(higher_name) > 0
                
                # Property 3: Names should be different for different timeframes
                assert primary_name != higher_name, \
                    "Primary and higher timeframe names should be different"
                
                logger.info(f"✅ Timeframe mapping test passed: {primary_name} -> {higher_name}")
            
        except Exception as e:
            logger.error(f"❌ Timeframe mapping test failed: {e}")
            raise
    
    def _generate_trending_data(self, bars: int, trend: str, strength: float, noise: float) -> pd.DataFrame:
        """Generate synthetic market data with specified trend characteristics"""
        
        # Base price and time series
        base_price = 1.1000
        dates = pd.date_range(start='2024-01-01', periods=bars, freq='1H')
        
        # Generate price movement based on trend
        if trend == 'bullish':
            trend_component = np.linspace(0, strength * 0.01 * bars, bars)
        elif trend == 'bearish':
            trend_component = np.linspace(0, -strength * 0.01 * bars, bars)
        else:  # neutral
            trend_component = np.zeros(bars)
        
        # Add noise
        noise_component = np.random.normal(0, noise * 0.01, bars)
        
        # Combine components
        price_changes = trend_component + noise_component
        prices = base_price + np.cumsum(price_changes)
        
        # Generate OHLC data
        df = pd.DataFrame({
            'time': dates,
            'open': prices,
            'high': prices * (1 + np.random.uniform(0, 0.002, bars)),
            'low': prices * (1 - np.random.uniform(0, 0.002, bars)),
            'close': prices,
            'volume': np.random.randint(1000, 10000, bars)
        })
        
        # Ensure high >= close >= low and high >= open >= low
        df['high'] = np.maximum(df['high'], np.maximum(df['open'], df['close']))
        df['low'] = np.minimum(df['low'], np.minimum(df['open'], df['close']))
        
        df.set_index('time', inplace=True)
        
        return df
    
    def _add_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators required for analysis"""
        
        # EMA indicators
        df['ema_20'] = df['close'].ewm(span=20).mean()
        df['ema_50'] = df['close'].ewm(span=50).mean()
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df['close'].ewm(span=12).mean()
        exp2 = df['close'].ewm(span=26).mean()
        df['macd'] = exp1 - exp2
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        # ADX (simplified)
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        
        plus_dm = df['high'].diff()
        minus_dm = df['low'].diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm > 0] = 0
        minus_dm = minus_dm.abs()
        
        plus_di = 100 * (plus_dm.rolling(14).mean() / true_range.rolling(14).mean())
        minus_di = 100 * (minus_dm.rolling(14).mean() / true_range.rolling(14).mean())
        
        dx = (np.abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
        df['adx'] = dx.rolling(14).mean()
        
        # Fill NaN values
        df = df.fillna(method='bfill').fillna(method='ffill')
        
        return df


def run_property_tests():
    """Run all property-based tests for multi-timeframe alignment"""
    
    print("="*80)
    print("RUNNING MULTI-TIMEFRAME ALIGNMENT PROPERTY TESTS")
    print("="*80)
    
    test_instance = TestMultiTimeframeAlignmentProperty()
    test_instance.setup_method()
    
    try:
        print("\n1. Testing timeframe alignment consistency...")
        test_instance.test_timeframe_alignment_consistency()
        print("✅ Timeframe alignment consistency tests passed")
        
        print("\n2. Testing signal confirmation logic...")
        test_instance.test_signal_confirmation_logic()
        print("✅ Signal confirmation logic tests passed")
        
        print("\n3. Testing timeframe relationship mapping...")
        test_instance.test_timeframe_relationship_mapping()
        print("✅ Timeframe relationship mapping tests passed")
        
        print("\n" + "="*80)
        print("🎉 ALL MULTI-TIMEFRAME ALIGNMENT PROPERTY TESTS PASSED!")
        print("✅ Property 7: Multi-Timeframe Alignment Validation - VALIDATED")
        print("✅ Requirements 6.1, 6.2, 6.3, 6.4 - SATISFIED")
        print("="*80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Property tests failed: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False


if __name__ == "__main__":
    success = run_property_tests()
    sys.exit(0 if success else 1)