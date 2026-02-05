"""
EMA Momentum Analyzer for Advanced Trend Detection
Implements EMA calculation, crossover detection, and slope analysis for momentum confirmation
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class EMASignal:
    """Represents an EMA momentum signal"""
    signal_type: str  # 'bullish_cross', 'bearish_cross', 'strong_bullish', 'strong_bearish', 'consolidation'
    fast_ema: float
    slow_ema: float
    separation: float
    slope_fast: float
    slope_slow: float
    momentum_strength: float
    crossover_confirmed: bool

@dataclass
class EMASupportResistance:
    """Represents EMA-based support/resistance levels"""
    level_type: str  # 'support' or 'resistance'
    ema_period: int
    price_level: float
    strength: float
    touches: int
    active: bool

@dataclass
class EMABreachResult:
    """Represents an EMA level breach event"""
    breach_type: str  # 'support_break', 'resistance_break', 'support_retest', 'resistance_retest'
    ema_period: int
    breach_level: float
    current_price: float
    breach_magnitude: float  # How far price moved beyond the level
    volume_confirmed: bool
    volume_ratio: float
    confidence: float
    timestamp: datetime

class EMAMomentumAnalyzer:
    """
    EMA Momentum Analyzer for trend detection
    
    Implements:
    - EMA calculation with configurable periods
    - Crossover detection and confirmation
    - EMA slope analysis for momentum strength
    - Dynamic support/resistance levels using EMAs
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the EMA momentum analyzer
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Configuration parameters
        self.fast_period = config.get('ema_fast_period', 20)
        self.slow_period = config.get('ema_slow_period', 50)
        self.min_separation = config.get('ema_min_separation', 0.0005)  # 0.05% minimum separation
        self.slope_lookback = config.get('ema_slope_lookback', 5)  # Bars for slope calculation
        
        # Support/Resistance and breach detection parameters
        self.breach_threshold = config.get('ema_breach_threshold', 0.001)  # 0.1% breach threshold
        self.min_volume_confirmation = config.get('ema_min_volume_confirmation', 1.2)  # 1.2x average volume
        self.retest_tolerance = config.get('ema_retest_tolerance', 0.002)  # 0.2% tolerance for retests
        
        # Validation
        if self.fast_period >= self.slow_period:
            raise ValueError("Fast EMA period must be less than slow EMA period")
        
        self.logger.info(f"EMAMomentumAnalyzer initialized with periods {self.fast_period}/{self.slow_period}")
        self.logger.info(f"Breach detection: threshold={self.breach_threshold:.3f}, volume_min={self.min_volume_confirmation}x")
    
    def calculate_emas(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate fast and slow EMAs
        
        Args:
            df: Price data with close column
            
        Returns:
            DataFrame with EMA columns added
        """
        if len(df) < max(self.fast_period, self.slow_period) * 2:
            self.logger.warning(f"Insufficient data for EMA calculation (need {max(self.fast_period, self.slow_period) * 2}, got {len(df)})")
            return df.copy()
        
        try:
            df_copy = df.copy()
            
            # Calculate EMAs
            df_copy[f'ema_{self.fast_period}'] = df_copy['close'].ewm(span=self.fast_period, adjust=False).mean()
            df_copy[f'ema_{self.slow_period}'] = df_copy['close'].ewm(span=self.slow_period, adjust=False).mean()
            
            # Calculate EMA separation (percentage)
            df_copy['ema_separation'] = (df_copy[f'ema_{self.fast_period}'] - df_copy[f'ema_{self.slow_period}']) / df_copy[f'ema_{self.slow_period}'] * 100
            
            # Calculate EMA slopes
            df_copy['ema_fast_slope'] = self._calculate_slope(df_copy[f'ema_{self.fast_period}'], self.slope_lookback)
            df_copy['ema_slow_slope'] = self._calculate_slope(df_copy[f'ema_{self.slow_period}'], self.slope_lookback)
            
            self.logger.debug(f"EMA calculation completed for {len(df)} bars")
            return df_copy
            
        except Exception as e:
            self.logger.error(f"Error calculating EMAs: {e}")
            return df.copy()
    
    def get_ema_signal(self, df: pd.DataFrame) -> Optional[EMASignal]:
        """
        Get EMA momentum signal from price data
        
        Args:
            df: Price data (will calculate EMAs if not present)
            
        Returns:
            EMASignal object or None if insufficient data
        """
        try:
            # Calculate EMAs if not present
            if f'ema_{self.fast_period}' not in df.columns or f'ema_{self.slow_period}' not in df.columns:
                df = self.calculate_emas(df)
            
            if len(df) < 3:  # Need at least 3 bars for crossover detection
                return None
            
            # Get current and previous values
            current = df.iloc[-1]
            previous = df.iloc[-2]
            
            if (pd.isna(current[f'ema_{self.fast_period}']) or 
                pd.isna(current[f'ema_{self.slow_period}'])):
                return None
            
            fast_ema = current[f'ema_{self.fast_period}']
            slow_ema = current[f'ema_{self.slow_period}']
            separation = current['ema_separation']
            slope_fast = current['ema_fast_slope']
            slope_slow = current['ema_slow_slope']
            
            # Detect signal type
            signal_type = self._detect_ema_signal_type(df)
            
            # Calculate momentum strength
            momentum_strength = self._calculate_momentum_strength(df)
            
            # Check crossover confirmation
            crossover_confirmed = self._is_crossover_confirmed(df)
            
            return EMASignal(
                signal_type=signal_type,
                fast_ema=fast_ema,
                slow_ema=slow_ema,
                separation=separation,
                slope_fast=slope_fast,
                slope_slow=slope_slow,
                momentum_strength=momentum_strength,
                crossover_confirmed=crossover_confirmed
            )
            
        except Exception as e:
            self.logger.error(f"Error getting EMA signal: {e}")
            return None
    
    def _detect_ema_signal_type(self, df: pd.DataFrame) -> str:
        """
        Detect EMA signal type based on crossovers and slopes
        
        Args:
            df: DataFrame with EMA indicators
            
        Returns:
            Signal type string
        """
        if len(df) < 3:
            return 'insufficient_data'
        
        current = df.iloc[-1]
        previous = df.iloc[-2]
        
        fast_ema = current[f'ema_{self.fast_period}']
        slow_ema = current[f'ema_{self.slow_period}']
        prev_fast = previous[f'ema_{self.fast_period}']
        prev_slow = previous[f'ema_{self.slow_period}']
        
        separation = abs(current['ema_separation'])
        slope_fast = current['ema_fast_slope']
        slope_slow = current['ema_slow_slope']
        
        # 1. Check for crossovers
        if prev_fast <= prev_slow and fast_ema > slow_ema:
            # Bullish crossover
            if separation > 0.5 and slope_fast > 0:  # Strong crossover with good separation and positive slope
                return 'strong_bullish_cross'
            else:
                return 'bullish_cross'
                
        elif prev_fast >= prev_slow and fast_ema < slow_ema:
            # Bearish crossover
            if separation > 0.5 and slope_fast < 0:  # Strong crossover with good separation and negative slope
                return 'strong_bearish_cross'
            else:
                return 'bearish_cross'
        
        # 2. Check for strong trending conditions (no crossover but strong momentum)
        elif fast_ema > slow_ema and separation > 1.0:
            # Strong bullish trend
            if slope_fast > 0 and slope_slow > 0:
                return 'strong_bullish_trend'
            elif slope_fast > 0:
                return 'moderate_bullish_trend'
            else:
                return 'weakening_bullish_trend'
                
        elif fast_ema < slow_ema and separation > 1.0:
            # Strong bearish trend
            if slope_fast < 0 and slope_slow < 0:
                return 'strong_bearish_trend'
            elif slope_fast < 0:
                return 'moderate_bearish_trend'
            else:
                return 'weakening_bearish_trend'
        
        # 3. Check for consolidation
        elif separation < 0.2:  # EMAs very close together
            return 'consolidation'
        
        # 4. Default to current trend direction
        else:
            if fast_ema > slow_ema:
                return 'weak_bullish'
            else:
                return 'weak_bearish'
    
    def _calculate_momentum_strength(self, df: pd.DataFrame) -> float:
        """
        Calculate momentum strength based on EMA separation and slopes
        
        Args:
            df: DataFrame with EMA indicators
            
        Returns:
            Momentum strength (0.0 to 1.0)
        """
        if len(df) < 5:
            return 0.5
        
        current = df.iloc[-1]
        separation = abs(current['ema_separation'])
        slope_fast = current['ema_fast_slope']
        slope_slow = current['ema_slow_slope']
        
        # 1. Separation strength (wider separation = stronger momentum)
        separation_strength = min(1.0, separation / 2.0)  # Normalize to 2% max
        
        # 2. Enhanced slope alignment strength with momentum direction confirmation
        slope_alignment = self._calculate_slope_alignment_strength(slope_fast, slope_slow)
        
        # 3. Enhanced slope magnitude strength with acceleration detection
        slope_strength = self._calculate_slope_magnitude_strength(df)
        
        # 4. Slope consistency and acceleration analysis
        slope_consistency = self._calculate_slope_consistency(df)
        
        # 5. Momentum direction confirmation (slopes supporting trend direction)
        momentum_direction_score = self._calculate_momentum_direction_score(df)
        
        # Combine factors with enhanced weighting for slope analysis
        total_strength = (
            separation_strength * 0.25 +      # Reduced weight for separation
            slope_alignment * 0.25 +          # Enhanced slope alignment
            slope_strength * 0.25 +           # Enhanced slope magnitude
            slope_consistency * 0.15 +        # Slope consistency over time
            momentum_direction_score * 0.10   # Momentum direction confirmation
        )
        
        return min(1.0, total_strength)
    
    def _is_crossover_confirmed(self, df: pd.DataFrame) -> bool:
        """
        Check if crossover is confirmed by subsequent price action
        
        Args:
            df: DataFrame with EMA indicators
            
        Returns:
            True if crossover is confirmed
        """
        if len(df) < 5:
            return False
        
        # Check last 3 bars for confirmation
        recent_data = df.tail(3)
        fast_col = f'ema_{self.fast_period}'
        slow_col = f'ema_{self.slow_period}'
        
        # For bullish crossover, fast EMA should stay above slow EMA
        if recent_data[fast_col].iloc[0] > recent_data[slow_col].iloc[0]:
            return all(recent_data[fast_col] > recent_data[slow_col])
        # For bearish crossover, fast EMA should stay below slow EMA
        else:
            return all(recent_data[fast_col] < recent_data[slow_col])
    
    def _calculate_slope(self, series: pd.Series, lookback: int) -> pd.Series:
        """
        Calculate slope of a series over lookback periods
        
        Args:
            series: Price series
            lookback: Number of periods for slope calculation
            
        Returns:
            Series with slope values
        """
        slopes = []
        
        for i in range(len(series)):
            if i < lookback:
                slopes.append(np.nan)
            else:
                # Calculate slope using linear regression
                y_values = series.iloc[i-lookback+1:i+1].values
                x_values = np.arange(len(y_values))
                
                if len(y_values) > 1:
                    slope = np.polyfit(x_values, y_values, 1)[0]
                    # Normalize slope as percentage change per bar
                    slope_pct = (slope / y_values[-1]) * 100 if y_values[-1] != 0 else 0
                    slopes.append(slope_pct)
                else:
                    slopes.append(0.0)
        
        return pd.Series(slopes, index=series.index)
    
    def identify_ema_support_resistance(self, df: pd.DataFrame) -> List[EMASupportResistance]:
        """
        Identify support and resistance levels using EMAs
        
        Args:
            df: DataFrame with price and EMA data
            
        Returns:
            List of EMA-based support/resistance levels
        """
        if f'ema_{self.fast_period}' not in df.columns or f'ema_{self.slow_period}' not in df.columns:
            df = self.calculate_emas(df)
        
        if len(df) < 20:
            return []
        
        try:
            sr_levels = []
            
            # Use EMAs as dynamic support/resistance
            current_price = df.iloc[-1]['close']
            fast_ema = df.iloc[-1][f'ema_{self.fast_period}']
            slow_ema = df.iloc[-1][f'ema_{self.slow_period}']
            
            # Fast EMA as support/resistance
            if current_price > fast_ema:
                # Fast EMA acting as support
                touches = self._count_ema_touches(df, f'ema_{self.fast_period}', 'support')
                strength = min(1.0, touches / 5.0)  # Normalize to max 5 touches
                
                sr_levels.append(EMASupportResistance(
                    level_type='support',
                    ema_period=self.fast_period,
                    price_level=fast_ema,
                    strength=strength,
                    touches=touches,
                    active=True
                ))
            else:
                # Fast EMA acting as resistance
                touches = self._count_ema_touches(df, f'ema_{self.fast_period}', 'resistance')
                strength = min(1.0, touches / 5.0)
                
                sr_levels.append(EMASupportResistance(
                    level_type='resistance',
                    ema_period=self.fast_period,
                    price_level=fast_ema,
                    strength=strength,
                    touches=touches,
                    active=True
                ))
            
            # Slow EMA as support/resistance
            if current_price > slow_ema:
                # Slow EMA acting as support
                touches = self._count_ema_touches(df, f'ema_{self.slow_period}', 'support')
                strength = min(1.0, touches / 5.0)
                
                sr_levels.append(EMASupportResistance(
                    level_type='support',
                    ema_period=self.slow_period,
                    price_level=slow_ema,
                    strength=strength,
                    touches=touches,
                    active=True
                ))
            else:
                # Slow EMA acting as resistance
                touches = self._count_ema_touches(df, f'ema_{self.slow_period}', 'resistance')
                strength = min(1.0, touches / 5.0)
                
                sr_levels.append(EMASupportResistance(
                    level_type='resistance',
                    ema_period=self.slow_period,
                    price_level=slow_ema,
                    strength=strength,
                    touches=touches,
                    active=True
                ))
            
            return sr_levels
            
        except Exception as e:
            self.logger.error(f"Error identifying EMA support/resistance: {e}")
            return []
    
    def _calculate_slope_alignment_strength(self, slope_fast: float, slope_slow: float) -> float:
        """
        Calculate slope alignment strength with enhanced momentum direction confirmation
        
        Args:
            slope_fast: Fast EMA slope
            slope_slow: Slow EMA slope
            
        Returns:
            Alignment strength (0.0 to 1.0)
        """
        # Check if slopes are in same direction
        if slope_fast * slope_slow > 0:  # Same sign
            # Both slopes pointing in same direction
            slope_ratio = min(abs(slope_fast), abs(slope_slow)) / (max(abs(slope_fast), abs(slope_slow)) + 0.0001)
            # Higher ratio means more aligned slopes
            return 0.7 + (0.3 * slope_ratio)  # Base 0.7 + bonus for similar magnitudes
        elif abs(slope_fast) < 0.001 and abs(slope_slow) < 0.001:
            # Both slopes near zero (flat)
            return 0.3
        else:
            # Slopes in opposite directions - check if this indicates momentum change
            stronger_slope = max(abs(slope_fast), abs(slope_slow))
            if stronger_slope > 0.005:  # Significant opposing slope
                return 0.2  # Low alignment but not zero (might be momentum shift)
            else:
                return 0.4  # Mild opposing slopes
    
    def _calculate_slope_magnitude_strength(self, df: pd.DataFrame) -> float:
        """
        Calculate slope magnitude strength with acceleration detection
        
        Args:
            df: DataFrame with EMA slope data
            
        Returns:
            Slope magnitude strength (0.0 to 1.0)
        """
        if len(df) < 3:
            return 0.5
        
        current = df.iloc[-1]
        slope_fast = current['ema_fast_slope']
        slope_slow = current['ema_slow_slope']
        
        # 1. Current slope magnitude
        avg_slope = (abs(slope_fast) + abs(slope_slow)) / 2
        magnitude_strength = min(1.0, avg_slope / 0.015)  # Normalize to 1.5% max slope
        
        # 2. Slope acceleration (is momentum increasing?)
        if len(df) >= 3:
            prev_fast_slope = df.iloc[-2]['ema_fast_slope']
            prev_slow_slope = df.iloc[-2]['ema_slow_slope']
            
            # Calculate acceleration (change in slope)
            fast_acceleration = slope_fast - prev_fast_slope
            slow_acceleration = slope_slow - prev_slow_slope
            
            # Positive acceleration in trend direction adds strength
            if slope_fast > 0 and fast_acceleration > 0:  # Bullish acceleration
                magnitude_strength *= 1.2
            elif slope_fast < 0 and fast_acceleration < 0:  # Bearish acceleration
                magnitude_strength *= 1.2
            elif abs(fast_acceleration) > 0.002:  # Significant deceleration
                magnitude_strength *= 0.8
        
        return min(1.0, magnitude_strength)
    
    def _calculate_slope_consistency(self, df: pd.DataFrame) -> float:
        """
        Calculate slope consistency over recent periods
        
        Args:
            df: DataFrame with EMA slope data
            
        Returns:
            Slope consistency score (0.0 to 1.0)
        """
        if len(df) < 5:
            return 0.5
        
        # Analyze last 5-10 periods for consistency
        lookback = min(10, len(df))
        recent_data = df.tail(lookback)
        
        fast_slopes = recent_data['ema_fast_slope'].values
        slow_slopes = recent_data['ema_slow_slope'].values
        
        # 1. Direction consistency (how often slopes point in same direction)
        direction_consistency = 0.0
        same_direction_count = 0
        
        for i in range(len(fast_slopes)):
            if not (pd.isna(fast_slopes[i]) or pd.isna(slow_slopes[i])):
                if fast_slopes[i] * slow_slopes[i] > 0:  # Same sign
                    same_direction_count += 1
        
        if len(fast_slopes) > 0:
            direction_consistency = same_direction_count / len(fast_slopes)
        
        # 2. Magnitude consistency (low standard deviation = more consistent)
        fast_slope_std = np.std(fast_slopes[~pd.isna(fast_slopes)])
        slow_slope_std = np.std(slow_slopes[~pd.isna(slow_slopes)])
        
        # Normalize standard deviation (lower std = higher consistency)
        fast_consistency = max(0.0, 1.0 - (fast_slope_std / 0.01))  # Normalize to 1% std
        slow_consistency = max(0.0, 1.0 - (slow_slope_std / 0.01))
        
        magnitude_consistency = (fast_consistency + slow_consistency) / 2
        
        # Combine direction and magnitude consistency
        total_consistency = (direction_consistency * 0.6 + magnitude_consistency * 0.4)
        
        return min(1.0, total_consistency)
    
    def _calculate_momentum_direction_score(self, df: pd.DataFrame) -> float:
        """
        Calculate momentum direction confirmation score
        
        Args:
            df: DataFrame with EMA and slope data
            
        Returns:
            Momentum direction score (0.0 to 1.0)
        """
        if len(df) < 3:
            return 0.5
        
        current = df.iloc[-1]
        fast_ema = current[f'ema_{self.fast_period}']
        slow_ema = current[f'ema_{self.slow_period}']
        slope_fast = current['ema_fast_slope']
        slope_slow = current['ema_slow_slope']
        
        # Determine current trend direction from EMA positioning
        if fast_ema > slow_ema:
            trend_direction = 'bullish'
        else:
            trend_direction = 'bearish'
        
        # Check if slopes confirm the trend direction
        score = 0.5  # Base score
        
        if trend_direction == 'bullish':
            # In bullish trend, positive slopes confirm momentum
            if slope_fast > 0:
                score += 0.25
            if slope_slow > 0:
                score += 0.15
            # Bonus if fast slope is steeper than slow (accelerating momentum)
            if slope_fast > slope_slow:
                score += 0.10
        else:  # bearish trend
            # In bearish trend, negative slopes confirm momentum
            if slope_fast < 0:
                score += 0.25
            if slope_slow < 0:
                score += 0.15
            # Bonus if fast slope is steeper downward than slow (accelerating momentum)
            if slope_fast < slope_slow:
                score += 0.10
        
        return min(1.0, score)
    
    def get_slope_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get detailed slope analysis for momentum confirmation
        
        Args:
            df: DataFrame with EMA data
            
        Returns:
            Dictionary with slope analysis details
        """
        if f'ema_{self.fast_period}' not in df.columns or f'ema_{self.slow_period}' not in df.columns:
            df = self.calculate_emas(df)
        
        if len(df) < 5:
            return {'error': 'insufficient_data'}
        
        current = df.iloc[-1]
        slope_fast = current['ema_fast_slope']
        slope_slow = current['ema_slow_slope']
        
        # Calculate enhanced slope metrics
        slope_alignment = self._calculate_slope_alignment_strength(slope_fast, slope_slow)
        slope_magnitude = self._calculate_slope_magnitude_strength(df)
        slope_consistency = self._calculate_slope_consistency(df)
        momentum_direction = self._calculate_momentum_direction_score(df)
        
        # Determine slope-based momentum strength
        slope_momentum_strength = (
            slope_alignment * 0.3 +
            slope_magnitude * 0.3 +
            slope_consistency * 0.2 +
            momentum_direction * 0.2
        )
        
        # Determine momentum direction and strength category
        if slope_fast > 0 and slope_slow > 0:
            momentum_direction_text = 'bullish'
            if slope_momentum_strength > 0.7:
                momentum_category = 'strong_bullish'
            elif slope_momentum_strength > 0.5:
                momentum_category = 'moderate_bullish'
            else:
                momentum_category = 'weak_bullish'
        elif slope_fast < 0 and slope_slow < 0:
            momentum_direction_text = 'bearish'
            if slope_momentum_strength > 0.7:
                momentum_category = 'strong_bearish'
            elif slope_momentum_strength > 0.5:
                momentum_category = 'moderate_bearish'
            else:
                momentum_category = 'weak_bearish'
        else:
            momentum_direction_text = 'mixed'
            momentum_category = 'consolidation'
        
        return {
            'fast_slope': slope_fast,
            'slow_slope': slope_slow,
            'slope_alignment_strength': slope_alignment,
            'slope_magnitude_strength': slope_magnitude,
            'slope_consistency': slope_consistency,
            'momentum_direction_score': momentum_direction,
            'overall_slope_momentum': slope_momentum_strength,
            'momentum_direction': momentum_direction_text,
            'momentum_category': momentum_category,
            'slope_analysis_summary': {
                'slopes_aligned': slope_fast * slope_slow > 0,
                'momentum_accelerating': self._is_momentum_accelerating(df),
                'trend_confirmed_by_slopes': momentum_direction > 0.6
            }
        }
    
    def _is_momentum_accelerating(self, df: pd.DataFrame) -> bool:
        """
        Check if momentum is accelerating based on slope changes
        
        Args:
            df: DataFrame with slope data
            
        Returns:
            True if momentum is accelerating
        """
        if len(df) < 3:
            return False
        
        current = df.iloc[-1]
        previous = df.iloc[-2]
        
        current_fast_slope = current['ema_fast_slope']
        current_slow_slope = current['ema_slow_slope']
        prev_fast_slope = previous['ema_fast_slope']
        prev_slow_slope = previous['ema_slow_slope']
        
        if pd.isna(current_fast_slope) or pd.isna(prev_fast_slope):
            return False
        
        # Check if slopes are increasing in magnitude in the same direction
        fast_acceleration = abs(current_fast_slope) > abs(prev_fast_slope)
        slow_acceleration = abs(current_slow_slope) > abs(prev_slow_slope)
        
        # Both slopes should be accelerating in the same direction
        same_direction = current_fast_slope * current_slow_slope > 0
        
        return same_direction and (fast_acceleration or slow_acceleration)
    
    def _count_ema_touches(self, df: pd.DataFrame, ema_column: str, level_type: str) -> int:
        """
        Count how many times price has touched the EMA level
        
        Args:
            df: DataFrame with price and EMA data
            ema_column: EMA column name
            level_type: 'support' or 'resistance'
            
        Returns:
            Number of touches
        """
        if len(df) < 10:
            return 0
        
        touches = 0
        tolerance = 0.001  # 0.1% tolerance
        
        # Look at recent data (last 50 bars or available data)
        recent_data = df.tail(min(50, len(df)))
        
        for i in range(1, len(recent_data)):
            current_price = recent_data.iloc[i]['close']
            ema_value = recent_data.iloc[i][ema_column]
            
            if pd.isna(ema_value):
                continue
            
            price_diff = abs(current_price - ema_value) / ema_value
            
            if price_diff <= tolerance:
                # Price is touching the EMA
                if level_type == 'support' and current_price >= ema_value:
                    touches += 1
                elif level_type == 'resistance' and current_price <= ema_value:
                    touches += 1
        
        return touches
    
    def detect_ema_breaches(self, df: pd.DataFrame, volume_analyzer=None) -> List[EMABreachResult]:
        """
        Detect EMA level breaches with volume confirmation
        
        Args:
            df: DataFrame with price and EMA data
            volume_analyzer: Optional VolumeAnalyzer instance for volume confirmation
            
        Returns:
            List of EMA breach results
        """
        if f'ema_{self.fast_period}' not in df.columns or f'ema_{self.slow_period}' not in df.columns:
            df = self.calculate_emas(df)
        
        if len(df) < 10:
            return []
        
        try:
            breaches = []
            current = df.iloc[-1]
            previous = df.iloc[-2] if len(df) > 1 else current
            
            current_price = current['close']
            current_time = current.get('time', datetime.now())
            
            # Get volume confirmation if available
            volume_confirmed = False
            volume_ratio = 1.0
            
            if volume_analyzer is not None:
                volume_ratio = volume_analyzer.get_volume_ratio(df)
                volume_confirmed = volume_ratio >= self.min_volume_confirmation
            
            # Check fast EMA breaches
            fast_ema_current = current[f'ema_{self.fast_period}']
            fast_ema_previous = previous[f'ema_{self.fast_period}']
            
            if not (pd.isna(fast_ema_current) or pd.isna(fast_ema_previous)):
                breach = self._check_level_breach(
                    current_price, previous['close'],
                    fast_ema_current, fast_ema_previous,
                    self.fast_period, volume_confirmed, volume_ratio, current_time
                )
                if breach:
                    breaches.append(breach)
            
            # Check slow EMA breaches
            slow_ema_current = current[f'ema_{self.slow_period}']
            slow_ema_previous = previous[f'ema_{self.slow_period}']
            
            if not (pd.isna(slow_ema_current) or pd.isna(slow_ema_previous)):
                breach = self._check_level_breach(
                    current_price, previous['close'],
                    slow_ema_current, slow_ema_previous,
                    self.slow_period, volume_confirmed, volume_ratio, current_time
                )
                if breach:
                    breaches.append(breach)
            
            return breaches
            
        except Exception as e:
            self.logger.error(f"Error detecting EMA breaches: {e}")
            return []
    
    def _check_level_breach(self, current_price: float, previous_price: float,
                           ema_current: float, ema_previous: float,
                           ema_period: int, volume_confirmed: bool,
                           volume_ratio: float, timestamp: datetime) -> Optional[EMABreachResult]:
        """
        Check if price has breached an EMA level
        
        Args:
            current_price: Current price
            previous_price: Previous price
            ema_current: Current EMA value
            ema_previous: Previous EMA value
            ema_period: EMA period
            volume_confirmed: Whether volume confirms the breach
            volume_ratio: Volume ratio vs average
            timestamp: Breach timestamp
            
        Returns:
            EMABreachResult if breach detected, None otherwise
        """
        # Calculate breach threshold
        breach_threshold_abs = ema_current * self.breach_threshold
        
        # Determine if this was support or resistance
        if previous_price > ema_previous:
            # EMA was acting as support
            if current_price < (ema_current - breach_threshold_abs):
                # Support broken
                breach_magnitude = (ema_current - current_price) / ema_current
                confidence = self._calculate_breach_confidence(
                    breach_magnitude, volume_confirmed, volume_ratio, 'support_break'
                )
                
                return EMABreachResult(
                    breach_type='support_break',
                    ema_period=ema_period,
                    breach_level=ema_current,
                    current_price=current_price,
                    breach_magnitude=breach_magnitude,
                    volume_confirmed=volume_confirmed,
                    volume_ratio=volume_ratio,
                    confidence=confidence,
                    timestamp=timestamp
                )
        else:
            # EMA was acting as resistance
            if current_price > (ema_current + breach_threshold_abs):
                # Resistance broken
                breach_magnitude = (current_price - ema_current) / ema_current
                confidence = self._calculate_breach_confidence(
                    breach_magnitude, volume_confirmed, volume_ratio, 'resistance_break'
                )
                
                return EMABreachResult(
                    breach_type='resistance_break',
                    ema_period=ema_period,
                    breach_level=ema_current,
                    current_price=current_price,
                    breach_magnitude=breach_magnitude,
                    volume_confirmed=volume_confirmed,
                    volume_ratio=volume_ratio,
                    confidence=confidence,
                    timestamp=timestamp
                )
        
        # Check for retests
        retest_tolerance_abs = ema_current * self.retest_tolerance
        
        if abs(current_price - ema_current) <= retest_tolerance_abs:
            # Price is retesting the EMA level
            if previous_price > ema_previous and current_price > ema_current:
                # Retesting from above (former resistance now support)
                confidence = self._calculate_breach_confidence(
                    abs(current_price - ema_current) / ema_current,
                    volume_confirmed, volume_ratio, 'support_retest'
                )
                
                return EMABreachResult(
                    breach_type='support_retest',
                    ema_period=ema_period,
                    breach_level=ema_current,
                    current_price=current_price,
                    breach_magnitude=abs(current_price - ema_current) / ema_current,
                    volume_confirmed=volume_confirmed,
                    volume_ratio=volume_ratio,
                    confidence=confidence,
                    timestamp=timestamp
                )
            elif previous_price < ema_previous and current_price < ema_current:
                # Retesting from below (former support now resistance)
                confidence = self._calculate_breach_confidence(
                    abs(current_price - ema_current) / ema_current,
                    volume_confirmed, volume_ratio, 'resistance_retest'
                )
                
                return EMABreachResult(
                    breach_type='resistance_retest',
                    ema_period=ema_period,
                    breach_level=ema_current,
                    current_price=current_price,
                    breach_magnitude=abs(current_price - ema_current) / ema_current,
                    volume_confirmed=volume_confirmed,
                    volume_ratio=volume_ratio,
                    confidence=confidence,
                    timestamp=timestamp
                )
        
        return None
    
    def _calculate_breach_confidence(self, breach_magnitude: float, volume_confirmed: bool,
                                   volume_ratio: float, breach_type: str) -> float:
        """
        Calculate confidence score for EMA breach
        
        Args:
            breach_magnitude: Magnitude of the breach (percentage)
            volume_confirmed: Whether volume confirms the breach
            volume_ratio: Volume ratio vs average
            breach_type: Type of breach
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        confidence = 0.5  # Base confidence
        
        # 1. Breach magnitude factor (larger breaches = higher confidence)
        magnitude_factor = min(1.0, breach_magnitude / 0.01)  # Normalize to 1% max
        confidence += magnitude_factor * 0.2
        
        # 2. Volume confirmation factor
        if volume_confirmed:
            volume_factor = min(1.0, (volume_ratio - 1.0) / 2.0)  # Normalize to 3x volume max
            confidence += volume_factor * 0.2
        else:
            confidence -= 0.1  # Penalty for no volume confirmation
        
        # 3. Breach type factor
        if 'break' in breach_type:
            confidence += 0.1  # Breaks are more significant than retests
        
        return max(0.0, min(1.0, confidence))
    
    def get_dynamic_support_resistance_analysis(self, df: pd.DataFrame, volume_analyzer=None) -> Dict[str, Any]:
        """
        Get comprehensive dynamic support/resistance analysis using EMAs
        
        Args:
            df: DataFrame with price and EMA data
            volume_analyzer: Optional VolumeAnalyzer for volume confirmation
            
        Returns:
            Dictionary with comprehensive S/R analysis
        """
        if f'ema_{self.fast_period}' not in df.columns or f'ema_{self.slow_period}' not in df.columns:
            df = self.calculate_emas(df)
        
        if len(df) < 20:
            return {'error': 'insufficient_data'}
        
        try:
            # Get current support/resistance levels
            sr_levels = self.identify_ema_support_resistance(df)
            
            # Detect recent breaches
            breaches = self.detect_ema_breaches(df, volume_analyzer)
            
            # Analyze current price position relative to EMAs
            current = df.iloc[-1]
            current_price = current['close']
            fast_ema = current[f'ema_{self.fast_period}']
            slow_ema = current[f'ema_{self.slow_period}']
            
            # Determine key levels and their strength
            key_levels = []
            
            for level in sr_levels:
                distance = abs(current_price - level.price_level) / current_price
                key_levels.append({
                    'type': level.level_type,
                    'period': level.ema_period,
                    'price': level.price_level,
                    'strength': level.strength,
                    'distance_pct': distance * 100,
                    'touches': level.touches,
                    'active': level.active
                })
            
            # Sort by distance to current price
            key_levels.sort(key=lambda x: x['distance_pct'])
            
            # Analyze breach implications
            breach_analysis = self._analyze_breach_implications(breaches, current_price)
            
            # Determine overall S/R context
            sr_context = self._determine_sr_context(current_price, fast_ema, slow_ema, breaches)
            
            return {
                'current_price': current_price,
                'fast_ema': fast_ema,
                'slow_ema': slow_ema,
                'key_levels': key_levels,
                'recent_breaches': [
                    {
                        'type': breach.breach_type,
                        'period': breach.ema_period,
                        'level': breach.breach_level,
                        'magnitude': breach.breach_magnitude,
                        'volume_confirmed': breach.volume_confirmed,
                        'confidence': breach.confidence
                    } for breach in breaches
                ],
                'breach_analysis': breach_analysis,
                'sr_context': sr_context,
                'nearest_support': self._find_nearest_level(key_levels, 'support'),
                'nearest_resistance': self._find_nearest_level(key_levels, 'resistance'),
                'trading_implications': self._get_trading_implications(sr_context, breach_analysis, key_levels)
            }
            
        except Exception as e:
            self.logger.error(f"Error in dynamic S/R analysis: {e}")
            return {'error': str(e)}
    
    def _analyze_breach_implications(self, breaches: List[EMABreachResult], current_price: float) -> Dict[str, Any]:
        """
        Analyze the implications of recent EMA breaches
        
        Args:
            breaches: List of recent breaches
            current_price: Current price
            
        Returns:
            Dictionary with breach analysis
        """
        if not breaches:
            return {
                'has_recent_breaches': False,
                'breach_count': 0,
                'dominant_direction': 'neutral',
                'confidence': 0.5
            }
        
        # Categorize breaches
        support_breaks = [b for b in breaches if b.breach_type == 'support_break']
        resistance_breaks = [b for b in breaches if b.breach_type == 'resistance_break']
        retests = [b for b in breaches if 'retest' in b.breach_type]
        
        # Determine dominant direction
        if len(resistance_breaks) > len(support_breaks):
            dominant_direction = 'bullish'
        elif len(support_breaks) > len(resistance_breaks):
            dominant_direction = 'bearish'
        else:
            dominant_direction = 'neutral'
        
        # Calculate overall confidence
        avg_confidence = sum(b.confidence for b in breaches) / len(breaches)
        volume_confirmed_pct = sum(1 for b in breaches if b.volume_confirmed) / len(breaches)
        
        overall_confidence = (avg_confidence + volume_confirmed_pct) / 2
        
        return {
            'has_recent_breaches': True,
            'breach_count': len(breaches),
            'support_breaks': len(support_breaks),
            'resistance_breaks': len(resistance_breaks),
            'retests': len(retests),
            'dominant_direction': dominant_direction,
            'confidence': overall_confidence,
            'volume_confirmation_rate': volume_confirmed_pct
        }
    
    def _determine_sr_context(self, current_price: float, fast_ema: float, 
                             slow_ema: float, breaches: List[EMABreachResult]) -> Dict[str, Any]:
        """
        Determine the overall support/resistance context
        
        Args:
            current_price: Current price
            fast_ema: Fast EMA value
            slow_ema: Slow EMA value
            breaches: Recent breaches
            
        Returns:
            Dictionary with S/R context
        """
        # Determine price position relative to EMAs
        above_fast = current_price > fast_ema
        above_slow = current_price > slow_ema
        
        if above_fast and above_slow:
            base_context = 'bullish_above_both'
            description = 'Price above both EMAs - bullish context'
        elif not above_fast and not above_slow:
            base_context = 'bearish_below_both'
            description = 'Price below both EMAs - bearish context'
        elif above_slow and not above_fast:
            base_context = 'mixed_between_emas'
            description = 'Price between EMAs - mixed context'
        else:
            base_context = 'transitional'
            description = 'Price in transitional zone'
        
        # Modify context based on recent breaches
        recent_breaks = [b for b in breaches if 'break' in b.breach_type]
        if recent_breaks:
            if any(b.breach_type == 'resistance_break' for b in recent_breaks):
                base_context += '_with_breakout'
                description += ' with recent breakout'
            elif any(b.breach_type == 'support_break' for b in recent_breaks):
                base_context += '_with_breakdown'
                description += ' with recent breakdown'
        
        return {
            'context': base_context,
            'description': description,
            'above_fast_ema': above_fast,
            'above_slow_ema': above_slow,
            'ema_separation': abs(fast_ema - slow_ema) / slow_ema * 100,
            'trend_alignment': 'bullish' if fast_ema > slow_ema else 'bearish'
        }
    
    def _find_nearest_level(self, key_levels: List[Dict], level_type: str) -> Optional[Dict]:
        """
        Find the nearest support or resistance level
        
        Args:
            key_levels: List of key levels
            level_type: 'support' or 'resistance'
            
        Returns:
            Nearest level of specified type or None
        """
        matching_levels = [level for level in key_levels if level['type'] == level_type]
        return matching_levels[0] if matching_levels else None
    
    def _get_trading_implications(self, sr_context: Dict, breach_analysis: Dict, 
                                 key_levels: List[Dict]) -> Dict[str, Any]:
        """
        Get trading implications based on S/R analysis
        
        Args:
            sr_context: Support/resistance context
            breach_analysis: Breach analysis results
            key_levels: Key support/resistance levels
            
        Returns:
            Dictionary with trading implications
        """
        implications = {
            'bias': 'neutral',
            'strength': 'weak',
            'key_levels_nearby': False,
            'breakout_potential': False,
            'retest_opportunity': False,
            'risk_level': 'medium'
        }
        
        # Determine bias from context and breaches
        if sr_context['context'].startswith('bullish'):
            implications['bias'] = 'bullish'
        elif sr_context['context'].startswith('bearish'):
            implications['bias'] = 'bearish'
        
        # Adjust bias based on recent breaches
        if breach_analysis['has_recent_breaches']:
            if breach_analysis['dominant_direction'] != 'neutral':
                implications['bias'] = breach_analysis['dominant_direction']
                implications['strength'] = 'strong' if breach_analysis['confidence'] > 0.7 else 'moderate'
        
        # Check for key levels nearby (within 1%)
        nearby_levels = [level for level in key_levels if level['distance_pct'] < 1.0]
        implications['key_levels_nearby'] = len(nearby_levels) > 0
        
        # Assess breakout potential
        if implications['key_levels_nearby'] and breach_analysis['confidence'] > 0.6:
            implications['breakout_potential'] = True
        
        # Check for retest opportunities
        retests = breach_analysis.get('retests', 0)
        if retests > 0 and breach_analysis['volume_confirmation_rate'] > 0.5:
            implications['retest_opportunity'] = True
        
        # Determine risk level
        if implications['key_levels_nearby'] and not implications['breakout_potential']:
            implications['risk_level'] = 'high'  # Near key levels without clear direction
        elif implications['strength'] == 'strong' and breach_analysis['volume_confirmation_rate'] > 0.7:
            implications['risk_level'] = 'low'  # Strong, volume-confirmed moves
        
        return implications
    
    def get_ema_analysis_details(self, df: pd.DataFrame, volume_analyzer=None) -> Dict[str, Any]:
        """
        Get detailed EMA analysis information including enhanced slope analysis and breach detection
        
        Args:
            df: DataFrame with EMA data
            volume_analyzer: Optional VolumeAnalyzer for volume confirmation
            
        Returns:
            Dictionary with detailed analysis
        """
        if f'ema_{self.fast_period}' not in df.columns or f'ema_{self.slow_period}' not in df.columns:
            df = self.calculate_emas(df)
        
        if len(df) < 5:
            return {'error': 'insufficient_data'}
        
        current = df.iloc[-1]
        signal = self.get_ema_signal(df)
        sr_levels = self.identify_ema_support_resistance(df)
        slope_analysis = self.get_slope_analysis(df)
        
        # Get dynamic support/resistance analysis with breach detection
        dynamic_sr_analysis = self.get_dynamic_support_resistance_analysis(df, volume_analyzer)
        
        return {
            'fast_ema': current[f'ema_{self.fast_period}'],
            'slow_ema': current[f'ema_{self.slow_period}'],
            'separation_pct': current['ema_separation'],
            'fast_slope': current['ema_fast_slope'],
            'slow_slope': current['ema_slow_slope'],
            'signal': signal,
            'support_resistance_levels': sr_levels,
            'trend_direction': 'bullish' if current[f'ema_{self.fast_period}'] > current[f'ema_{self.slow_period}'] else 'bearish',
            'trend_strength': signal.momentum_strength if signal else 0.0,
            'slope_analysis': slope_analysis,
            'dynamic_sr_analysis': dynamic_sr_analysis,
            'momentum_confirmation': {
                'slope_momentum_strength': slope_analysis.get('overall_slope_momentum', 0.0),
                'momentum_category': slope_analysis.get('momentum_category', 'unknown'),
                'slopes_confirm_trend': slope_analysis.get('slope_analysis_summary', {}).get('trend_confirmed_by_slopes', False),
                'momentum_accelerating': slope_analysis.get('slope_analysis_summary', {}).get('momentum_accelerating', False)
            }
        }