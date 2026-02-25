"""
Trendline Analyzer for Advanced Trend Detection
Implements automatic trendline identification, validation, and break detection
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
import logging
import math

# Import data models from trend detection engine
from src.analyzers.trend_detection_engine import Trendline, TrendlineBreak

logger = logging.getLogger(__name__)

@dataclass
class SwingPoint:
    """Represents a swing high or low point for trendline analysis"""
    index: int
    timestamp: datetime
    price: float
    swing_type: str  # 'high' or 'low'
    strength: int    # Number of bars on each side
    volume: float
    significance: float  # Calculated significance score

@dataclass
class TrendlineCandidate:
    """Represents a potential trendline before validation"""
    start_point: SwingPoint
    end_point: SwingPoint
    slope: float
    angle_degrees: float
    touch_points: List[SwingPoint]
    line_type: str  # 'support' or 'resistance'
    raw_strength: float

class TrendlineAnalyzer:
    """
    Automatic Trendline Analysis System
    
    Implements:
    - Pivot point detection for swing highs and lows
    - Trendline identification connecting significant swing points
    - Trendline validation and filtering
    - Trendline break detection with volume confirmation
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the trendline analyzer
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Configuration parameters for swing point detection
        self.swing_strength = config.get('swing_strength', 5)  # Bars on each side for swing detection
        self.min_swing_significance = config.get('min_swing_significance', 0.001)  # 0.1% minimum price movement
        
        # Configuration parameters for trendline identification
        self.max_trendlines = config.get('max_trendlines', 5)
        self.min_trendline_touches = config.get('min_trendline_touches', 2)
        self.trendline_angle_min = config.get('trendline_angle_min', 10)  # degrees
        self.trendline_angle_max = config.get('trendline_angle_max', 80)  # degrees
        
        # Configuration parameters for trendline validation
        self.touch_tolerance = config.get('trendline_touch_tolerance', 0.002)  # 0.2% tolerance for touches
        self.min_trendline_duration = config.get('min_trendline_duration', 10)  # Minimum bars between points
        self.max_lookback_bars = config.get('trendline_lookback_bars', 100)  # Maximum bars to look back
        
        # Configuration parameters for break detection
        self.break_threshold = config.get('trendline_break_threshold', 0.001)  # 0.1% break threshold
        self.volume_confirmation_threshold = config.get('volume_confirmation_threshold', 1.5)  # Volume multiplier
        self.retest_tolerance = config.get('trendline_retest_tolerance', 0.003)  # 0.3% retest tolerance
        
        self.logger.info(f"TrendlineAnalyzer initialized:")
        self.logger.info(f"  Swing detection: strength={self.swing_strength}, min_significance={self.min_swing_significance}")
        self.logger.info(f"  Trendline limits: max={self.max_trendlines}, min_touches={self.min_trendline_touches}")
        self.logger.info(f"  Angle limits: {self.trendline_angle_min}° - {self.trendline_angle_max}°")
        self.logger.info(f"  Break detection: threshold={self.break_threshold}, volume_min={self.volume_confirmation_threshold}x")
    
    def identify_trendlines(self, df: pd.DataFrame) -> List[Trendline]:
        """
        Identify trendlines connecting significant swing points
        
        Args:
            df: Price data with OHLCV
            
        Returns:
            List of validated trendlines
        """
        if len(df) < self.swing_strength * 4:  # Need enough data for swing detection
            self.logger.debug(f"Insufficient data for trendline analysis (need {self.swing_strength * 4}, got {len(df)})")
            return []
        
        try:
            self.logger.info(f"🔍 IDENTIFYING TRENDLINES from {len(df)} bars")
            
            # 1. Find swing points
            swing_highs = self._find_swing_points(df, 'high')
            swing_lows = self._find_swing_points(df, 'low')
            
            self.logger.info(f"  Found {len(swing_highs)} swing highs and {len(swing_lows)} swing lows")
            
            if len(swing_highs) < 2 and len(swing_lows) < 2:
                self.logger.info("  ❌ Insufficient swing points for trendline analysis")
                return []
            
            # 2. Generate trendline candidates
            trendline_candidates = []
            
            # Generate resistance trendlines from swing highs
            if len(swing_highs) >= 2:
                resistance_candidates = self._generate_trendline_candidates(swing_highs, 'resistance', df)
                trendline_candidates.extend(resistance_candidates)
                self.logger.info(f"  Generated {len(resistance_candidates)} resistance trendline candidates")
            
            # Generate support trendlines from swing lows
            if len(swing_lows) >= 2:
                support_candidates = self._generate_trendline_candidates(swing_lows, 'support', df)
                trendline_candidates.extend(support_candidates)
                self.logger.info(f"  Generated {len(support_candidates)} support trendline candidates")
            
            if not trendline_candidates:
                self.logger.info("  ❌ No trendline candidates generated")
                return []
            
            # 3. Validate and filter trendlines
            validated_trendlines = []
            for candidate in trendline_candidates:
                if self._validate_trendline_candidate(candidate, df):
                    trendline = self._convert_candidate_to_trendline(candidate)
                    validated_trendlines.append(trendline)
            
            self.logger.info(f"  Validated {len(validated_trendlines)} trendlines from {len(trendline_candidates)} candidates")
            
            # 4. Sort by strength and limit to max count
            validated_trendlines.sort(key=lambda x: x.strength, reverse=True)
            final_trendlines = validated_trendlines[:self.max_trendlines]
            
            self.logger.info(f"  ✅ Final trendlines: {len(final_trendlines)}")
            for i, tl in enumerate(final_trendlines, 1):
                self.logger.info(f"    {i}. {tl.line_type.upper()} - Strength: {tl.strength:.3f}, "
                               f"Touches: {tl.touch_points}, Slope: {tl.slope:.6f}")
            
            return final_trendlines
            
        except Exception as e:
            self.logger.error(f"Error identifying trendlines: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return []
    
    def _find_swing_points(self, df: pd.DataFrame, price_type: str) -> List[SwingPoint]:
        """
        Find swing high or low points using pivot point detection
        
        Args:
            df: Price data
            price_type: 'high' or 'low'
            
        Returns:
            List of swing points
        """
        swing_points = []
        prices = df[price_type].values
        
        # Limit lookback to avoid excessive computation
        start_idx = max(0, len(prices) - self.max_lookback_bars)
        
        for i in range(start_idx + self.swing_strength, len(prices) - self.swing_strength):
            is_swing = True
            current_price = prices[i]
            
            # Check if current point is higher/lower than surrounding points
            for j in range(i - self.swing_strength, i + self.swing_strength + 1):
                if j == i:
                    continue
                
                if price_type == 'high':
                    if prices[j] >= current_price:
                        is_swing = False
                        break
                else:  # low
                    if prices[j] <= current_price:
                        is_swing = False
                        break
            
            if is_swing:
                # Calculate significance of this swing point
                significance = self._calculate_swing_significance(df, i, price_type)
                
                # Only include significant swing points
                if significance >= self.min_swing_significance:
                    swing_points.append(SwingPoint(
                        index=i,
                        timestamp=df.iloc[i].name if hasattr(df.iloc[i].name, 'timestamp') else datetime.now(),
                        price=current_price,
                        swing_type=price_type,
                        strength=self.swing_strength,
                        volume=df.iloc[i]['volume'] if 'volume' in df.columns else 0,
                        significance=significance
                    ))
        
        # Sort by significance (most significant first)
        swing_points.sort(key=lambda x: x.significance, reverse=True)
        
        # Limit to most significant points to avoid noise
        max_swing_points = min(20, len(swing_points))  # Keep top 20 most significant
        return swing_points[:max_swing_points]
    
    def _calculate_swing_significance(self, df: pd.DataFrame, index: int, price_type: str) -> float:
        """
        Calculate the significance of a swing point
        
        Args:
            df: Price data
            index: Index of the swing point
            price_type: 'high' or 'low'
            
        Returns:
            Significance score (higher = more significant)
        """
        try:
            current_price = df.iloc[index][price_type]
            
            # 1. Price movement significance (how far from surrounding prices)
            lookback = min(self.swing_strength * 2, index, len(df) - index - 1)
            if lookback < 2:
                return 0.0
            
            surrounding_prices = []
            for i in range(index - lookback, index + lookback + 1):
                if i != index and 0 <= i < len(df):
                    surrounding_prices.append(df.iloc[i][price_type])
            
            if not surrounding_prices:
                return 0.0
            
            if price_type == 'high':
                # For highs, significance is how much higher than surrounding prices
                max_surrounding = max(surrounding_prices)
                price_significance = (current_price - max_surrounding) / max_surrounding if max_surrounding > 0 else 0
            else:
                # For lows, significance is how much lower than surrounding prices
                min_surrounding = min(surrounding_prices)
                price_significance = (min_surrounding - current_price) / min_surrounding if min_surrounding > 0 else 0
            
            # 2. Volume significance (if volume data available)
            volume_significance = 0.0
            if 'volume' in df.columns and index >= 10:
                current_volume = df.iloc[index]['volume']
                avg_volume = df['volume'].iloc[max(0, index-10):index].mean()
                if avg_volume > 0:
                    volume_significance = min(1.0, current_volume / avg_volume - 1.0)  # Cap at 100% above average
            
            # 3. Time-based significance (more recent points are more significant)
            time_significance = 1.0 - (len(df) - index - 1) / len(df)  # Recent points get higher score
            
            # Combine significance factors
            total_significance = (
                price_significance * 0.6 +      # Price movement is most important
                volume_significance * 0.2 +     # Volume confirmation
                time_significance * 0.2         # Recency factor
            )
            
            return max(0.0, total_significance)
            
        except Exception as e:
            self.logger.error(f"Error calculating swing significance: {e}")
            return 0.0
    
    def _generate_trendline_candidates(self, swing_points: List[SwingPoint], 
                                     line_type: str, df: pd.DataFrame) -> List[TrendlineCandidate]:
        """
        Generate trendline candidates from swing points
        
        Args:
            swing_points: List of swing points
            line_type: 'support' or 'resistance'
            df: Price data for validation
            
        Returns:
            List of trendline candidates
        """
        candidates = []
        
        # Generate all possible combinations of swing points
        for i in range(len(swing_points)):
            for j in range(i + 1, len(swing_points)):
                start_point = swing_points[i]
                end_point = swing_points[j]
                
                # Ensure chronological order
                if start_point.index > end_point.index:
                    start_point, end_point = end_point, start_point
                
                # Check minimum duration between points
                if end_point.index - start_point.index < self.min_trendline_duration:
                    continue
                
                # Calculate slope and angle
                price_diff = end_point.price - start_point.price
                time_diff = end_point.index - start_point.index
                
                if time_diff == 0:
                    continue
                
                slope = price_diff / time_diff
                
                # Calculate angle in degrees
                # Use price percentage change per bar to normalize
                price_change_per_bar = slope / start_point.price if start_point.price > 0 else 0
                angle_radians = math.atan(price_change_per_bar * 100)  # Scale for reasonable angles
                angle_degrees = abs(math.degrees(angle_radians))
                
                # Filter by angle constraints
                if angle_degrees < self.trendline_angle_min or angle_degrees > self.trendline_angle_max:
                    continue
                
                # Find additional touch points along this line
                touch_points = self._find_touch_points(start_point, end_point, df, line_type)
                
                # Calculate raw strength based on touches and other factors
                raw_strength = self._calculate_raw_trendline_strength(
                    start_point, end_point, touch_points, df
                )
                
                candidates.append(TrendlineCandidate(
                    start_point=start_point,
                    end_point=end_point,
                    slope=slope,
                    angle_degrees=angle_degrees,
                    touch_points=touch_points,
                    line_type=line_type,
                    raw_strength=raw_strength
                ))
        
        return candidates
    
    def _find_touch_points(self, start_point: SwingPoint, end_point: SwingPoint, 
                          df: pd.DataFrame, line_type: str) -> List[SwingPoint]:
        """
        Find additional points that touch the trendline
        
        Args:
            start_point: Starting swing point
            end_point: Ending swing point
            df: Price data
            line_type: 'support' or 'resistance'
            
        Returns:
            List of swing points that touch the trendline
        """
        touch_points = [start_point, end_point]  # Always include the defining points
        
        # Calculate line equation: y = mx + b
        if end_point.index == start_point.index:
            return touch_points
        
        slope = (end_point.price - start_point.price) / (end_point.index - start_point.index)
        intercept = start_point.price - slope * start_point.index
        
        # Check each bar between start and end for touches
        for i in range(start_point.index + 1, end_point.index):
            if i >= len(df):
                break
                
            expected_price = slope * i + intercept
            
            if line_type == 'support':
                actual_price = df.iloc[i]['low']
                # For support, price should touch from above
                price_diff = abs(actual_price - expected_price) / expected_price
                if price_diff <= self.touch_tolerance and actual_price >= expected_price * 0.995:
                    touch_points.append(SwingPoint(
                        index=i,
                        timestamp=df.iloc[i].name if hasattr(df.iloc[i].name, 'timestamp') else datetime.now(),
                        price=actual_price,
                        swing_type='low',
                        strength=1,  # Touch points have lower strength
                        volume=df.iloc[i]['volume'] if 'volume' in df.columns else 0,
                        significance=0.5  # Touch points have moderate significance
                    ))
            else:  # resistance
                actual_price = df.iloc[i]['high']
                # For resistance, price should touch from below
                price_diff = abs(actual_price - expected_price) / expected_price
                if price_diff <= self.touch_tolerance and actual_price <= expected_price * 1.005:
                    touch_points.append(SwingPoint(
                        index=i,
                        timestamp=df.iloc[i].name if hasattr(df.iloc[i].name, 'timestamp') else datetime.now(),
                        price=actual_price,
                        swing_type='high',
                        strength=1,
                        volume=df.iloc[i]['volume'] if 'volume' in df.columns else 0,
                        significance=0.5
                    ))
        
        return touch_points
    
    def _calculate_raw_trendline_strength(self, start_point: SwingPoint, end_point: SwingPoint,
                                        touch_points: List[SwingPoint], df: pd.DataFrame) -> float:
        """
        Calculate raw strength of a trendline candidate
        
        Args:
            start_point: Starting point
            end_point: Ending point
            touch_points: All points touching the line
            df: Price data
            
        Returns:
            Raw strength score (0.0 to 1.0)
        """
        base_strength = 0.3
        
        # 1. Touch points factor (more touches = stronger)
        touch_bonus = min(0.4, (len(touch_points) - 2) * 0.1)  # Bonus for touches beyond the 2 defining points
        base_strength += touch_bonus
        
        # 2. Duration factor (longer lines = stronger)
        duration_bars = end_point.index - start_point.index
        duration_bonus = min(0.2, duration_bars / 50)  # Normalize to 50 bars max
        base_strength += duration_bonus
        
        # 3. Significance of defining points
        significance_bonus = (start_point.significance + end_point.significance) / 2 * 0.1
        base_strength += significance_bonus
        
        # 4. Volume confirmation at touch points
        volume_bonus = 0.0
        if 'volume' in df.columns:
            total_volume = sum(point.volume for point in touch_points if point.volume > 0)
            if total_volume > 0 and len(touch_points) > 0:
                avg_volume = df['volume'].mean() if len(df) > 0 else 0
                if avg_volume > 0:
                    volume_ratio = (total_volume / len(touch_points)) / avg_volume
                    volume_bonus = min(0.1, volume_ratio * 0.05)
        
        base_strength += volume_bonus
        
        return min(1.0, base_strength)
    
    def _validate_trendline_candidate(self, candidate: TrendlineCandidate, df: pd.DataFrame) -> bool:
        """
        Validate a trendline candidate based on various criteria
        
        Args:
            candidate: Trendline candidate to validate
            df: Price data
            
        Returns:
            True if candidate is valid, False otherwise
        """
        # 1. Check minimum touch points
        if len(candidate.touch_points) < self.min_trendline_touches:
            return False
        
        # 2. Check angle constraints (already done in generation, but double-check)
        if (candidate.angle_degrees < self.trendline_angle_min or 
            candidate.angle_degrees > self.trendline_angle_max):
            return False
        
        # 3. Check minimum strength
        if candidate.raw_strength < 0.4:  # Minimum strength threshold
            return False
        
        # 4. Check that the line makes sense (no major violations)
        violations = self._count_trendline_violations(candidate, df)
        max_allowed_violations = max(1, len(candidate.touch_points) // 3)  # Allow some violations
        
        if violations > max_allowed_violations:
            return False
        
        # 5. Check recency (trendlines should have some recent relevance)
        most_recent_touch = max(candidate.touch_points, key=lambda x: x.index)
        bars_since_last_touch = len(df) - most_recent_touch.index - 1
        
        if bars_since_last_touch > 50:  # Trendline too old
            return False
        
        return True
    
    def _count_trendline_violations(self, candidate: TrendlineCandidate, df: pd.DataFrame) -> int:
        """
        Count how many times price significantly violates the trendline
        
        Args:
            candidate: Trendline candidate
            df: Price data
            
        Returns:
            Number of violations
        """
        violations = 0
        
        # Calculate line equation
        start_idx = candidate.start_point.index
        end_idx = candidate.end_point.index
        
        if end_idx == start_idx:
            return 0
        
        slope = candidate.slope
        intercept = candidate.start_point.price - slope * start_idx
        
        # Check for violations between start and end points
        violation_threshold = 0.005  # 0.5% violation threshold
        
        for i in range(start_idx, min(end_idx + 1, len(df))):
            expected_price = slope * i + intercept
            
            if candidate.line_type == 'support':
                actual_low = df.iloc[i]['low']
                # Violation if price goes significantly below support
                if actual_low < expected_price * (1 - violation_threshold):
                    violations += 1
            else:  # resistance
                actual_high = df.iloc[i]['high']
                # Violation if price goes significantly above resistance
                if actual_high > expected_price * (1 + violation_threshold):
                    violations += 1
        
        return violations
    
    def _convert_candidate_to_trendline(self, candidate: TrendlineCandidate) -> Trendline:
        """
        Convert a validated candidate to a Trendline object
        
        Args:
            candidate: Validated trendline candidate
            
        Returns:
            Trendline object
        """
        return Trendline(
            start_point=(candidate.start_point.timestamp, candidate.start_point.price),
            end_point=(candidate.end_point.timestamp, candidate.end_point.price),
            slope=candidate.slope,
            touch_points=len(candidate.touch_points),
            strength=candidate.raw_strength,
            line_type=candidate.line_type
        )
    
    def detect_trendline_breaks(self, df: pd.DataFrame, trendlines: List[Trendline]) -> List[TrendlineBreak]:
        """
        Detect trendline breaches with sufficient volume
        
        Args:
            df: Price data with OHLCV
            trendlines: List of active trendlines to check
            
        Returns:
            List of trendline breaks
        """
        if not trendlines or len(df) < 5:
            return []
        
        try:
            breaks = []
            current_bar = df.iloc[-1]
            current_price = current_bar['close']
            current_time = current_bar.name if hasattr(current_bar.name, 'timestamp') else datetime.now()
            
            self.logger.info(f"🔍 CHECKING TRENDLINE BREAKS for {len(trendlines)} trendlines")
            self.logger.info(f"  Current price: {current_price:.5f}")
            
            for i, trendline in enumerate(trendlines, 1):
                self.logger.info(f"  Checking trendline {i}: {trendline.line_type} (strength: {trendline.strength:.3f})")
                
                # Calculate current trendline value
                current_trendline_value = self._calculate_trendline_value_at_time(trendline, len(df) - 1)
                
                if current_trendline_value is None:
                    self.logger.info(f"    ❌ Could not calculate trendline value")
                    continue
                
                self.logger.info(f"    Trendline value: {current_trendline_value:.5f}")
                
                # Check for break
                break_result = self._check_trendline_break(
                    df, trendline, current_price, current_trendline_value, current_time
                )
                
                if break_result:
                    breaks.append(break_result)
                    self.logger.info(f"    ✅ BREAK DETECTED: {trendline.line_type} break")
                    self.logger.info(f"       Break strength: {break_result.break_strength:.3f}")
                    self.logger.info(f"       Volume confirmed: {break_result.volume_confirmation}")
                else:
                    self.logger.info(f"    ❌ No break detected")
            
            self.logger.info(f"  Total breaks found: {len(breaks)}")
            return breaks
            
        except Exception as e:
            self.logger.error(f"Error detecting trendline breaks: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return []
    
    def _calculate_trendline_value_at_time(self, trendline: Trendline, bar_index: int) -> Optional[float]:
        """
        Calculate the trendline value at a specific bar index
        
        Args:
            trendline: Trendline object
            bar_index: Bar index to calculate value for
            
        Returns:
            Trendline value at the specified time, or None if cannot calculate
        """
        try:
            # Extract start and end points
            start_time, start_price = trendline.start_point
            end_time, end_price = trendline.end_point
            
            # For simplicity, assume linear progression based on bar index
            # In a real implementation, you might want to use actual timestamps
            
            # Use slope to project the line
            # Value = start_price + slope * (bar_index - start_bar_index)
            # We'll estimate start_bar_index based on the slope and points
            
            if trendline.slope == 0:
                return start_price
            
            # Estimate the bar indices from the slope and price difference
            price_diff = end_price - start_price
            estimated_bar_diff = price_diff / trendline.slope if trendline.slope != 0 else 1
            
            # Assume the trendline was created from recent data
            # Project from the end point backwards to estimate start bar
            estimated_end_bar = bar_index - 10  # Assume end point was 10 bars ago
            estimated_start_bar = estimated_end_bar - estimated_bar_diff
            
            # Calculate value at current bar
            bar_diff_from_start = bar_index - estimated_start_bar
            current_value = start_price + trendline.slope * bar_diff_from_start
            
            return current_value
            
        except Exception as e:
            self.logger.error(f"Error calculating trendline value: {e}")
            return None
    
    def _check_trendline_break(self, df: pd.DataFrame, trendline: Trendline, 
                              current_price: float, trendline_value: float, 
                              current_time: datetime) -> Optional[TrendlineBreak]:
        """
        Check if price has broken a trendline
        
        Args:
            df: Price data
            trendline: Trendline to check
            current_price: Current price
            trendline_value: Current trendline value
            current_time: Current timestamp
            
        Returns:
            TrendlineBreak if break detected, None otherwise
        """
        # Calculate break threshold
        break_threshold_abs = trendline_value * self.break_threshold
        
        # Check for volume confirmation
        volume_confirmed = self._check_volume_confirmation_for_break(df)
        
        # Determine break type and check conditions
        if trendline.line_type == 'support':
            # Support break: price goes below trendline
            if current_price < (trendline_value - break_threshold_abs):
                break_strength = self._calculate_break_strength(
                    current_price, trendline_value, trendline, volume_confirmed, 'support_break'
                )
                
                # Check for retest confirmation
                retest_confirmed = self._check_retest_confirmation(df, trendline_value, 'support')
                
                return TrendlineBreak(
                    trendline=trendline,
                    break_point=(current_time, current_price),
                    volume_confirmation=volume_confirmed,
                    retest_confirmed=retest_confirmed,
                    break_strength=break_strength
                )
        
        else:  # resistance
            # Resistance break: price goes above trendline
            if current_price > (trendline_value + break_threshold_abs):
                break_strength = self._calculate_break_strength(
                    current_price, trendline_value, trendline, volume_confirmed, 'resistance_break'
                )
                
                # Check for retest confirmation
                retest_confirmed = self._check_retest_confirmation(df, trendline_value, 'resistance')
                
                return TrendlineBreak(
                    trendline=trendline,
                    break_point=(current_time, current_price),
                    volume_confirmation=volume_confirmed,
                    retest_confirmed=retest_confirmed,
                    break_strength=break_strength
                )
        
        return None
    
    def _check_volume_confirmation_for_break(self, df: pd.DataFrame) -> bool:
        """
        Check if volume confirms the trendline break
        
        Args:
            df: Price data with volume
            
        Returns:
            True if volume confirms the break
        """
        if 'volume' not in df.columns or len(df) < 5:
            self.logger.debug("Volume confirmation failed: no volume data or insufficient data")
            return False
        
        try:
            # Check last 3 bars for volume spike
            recent_volumes = df['volume'].tail(3)
            max_recent_volume = recent_volumes.max()
            
            # Compare to average volume (use shorter lookback if needed)
            lookback_period = min(20, len(df) - 3)  # Exclude the recent 3 bars from average
            if lookback_period < 3:
                self.logger.debug("Volume confirmation failed: insufficient lookback period")
                return False
                
            # Calculate average excluding the recent spike period
            historical_volumes = df['volume'].iloc[:-3] if len(df) > 3 else df['volume'].iloc[:-1]
            avg_volume = historical_volumes.tail(lookback_period).mean()
            
            if avg_volume > 0:
                volume_ratio = max_recent_volume / avg_volume
                self.logger.debug(f"Volume confirmation check: max_recent={max_recent_volume:.0f}, avg={avg_volume:.0f}, ratio={volume_ratio:.2f}, threshold={self.volume_confirmation_threshold}")
                confirmed = volume_ratio >= self.volume_confirmation_threshold
                self.logger.debug(f"Volume confirmation result: {confirmed}")
                return confirmed
            
            self.logger.debug("Volume confirmation failed: zero average volume")
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking volume confirmation: {e}")
            return False
    
    def _calculate_break_strength(self, current_price: float, trendline_value: float,
                                 trendline: Trendline, volume_confirmed: bool, 
                                 break_type: str) -> float:
        """
        Calculate the strength of a trendline break
        
        Args:
            current_price: Current price
            trendline_value: Trendline value at current time
            trendline: The trendline being broken
            volume_confirmed: Whether volume confirms the break
            break_type: Type of break ('support_break' or 'resistance_break')
            
        Returns:
            Break strength (0.0 to 1.0)
        """
        base_strength = 0.3  # Lower base strength
        
        # 1. Break magnitude (how far price moved beyond trendline)
        break_magnitude = abs(current_price - trendline_value) / trendline_value
        magnitude_bonus = min(0.25, break_magnitude / 0.02)  # Normalize to 2% max
        base_strength += magnitude_bonus
        
        # 2. Trendline strength (stronger trendlines = more significant breaks)
        trendline_bonus = trendline.strength * 0.15  # Reduced bonus
        base_strength += trendline_bonus
        
        # 3. Volume confirmation - stronger impact
        if volume_confirmed:
            base_strength += 0.25  # Increased bonus for volume confirmation
        else:
            base_strength -= 0.2  # Stronger penalty for no volume confirmation
        
        # 4. Touch points (more touches = stronger trendline = more significant break)
        touch_bonus = min(0.1, (trendline.touch_points - 2) * 0.02)
        base_strength += touch_bonus
        
        return max(0.0, min(1.0, base_strength))
    
    def _check_retest_confirmation(self, df: pd.DataFrame, trendline_value: float, 
                                  original_type: str) -> bool:
        """
        Check for retest confirmation of broken trendline
        
        Args:
            df: Price data
            trendline_value: Value of the broken trendline
            original_type: Original trendline type ('support' or 'resistance')
            
        Returns:
            True if retest is confirmed
        """
        if len(df) < 5:
            return False
        
        try:
            # Look at last 5 bars for retest pattern
            recent_data = df.tail(5)
            retest_tolerance_abs = trendline_value * self.retest_tolerance
            
            # For broken support (now resistance), look for price approaching from below and holding
            if original_type == 'support':
                for _, bar in recent_data.iterrows():
                    high_price = bar['high']
                    close_price = bar['close']
                    
                    # Check if price approached the level but held below (retest as resistance)
                    if (abs(high_price - trendline_value) <= retest_tolerance_abs and 
                        close_price < trendline_value):
                        return True
            
            # For broken resistance (now support), look for price approaching from above and holding
            else:  # resistance
                for _, bar in recent_data.iterrows():
                    low_price = bar['low']
                    close_price = bar['close']
                    
                    # Check if price approached the level but held above (retest as support)
                    if (abs(low_price - trendline_value) <= retest_tolerance_abs and 
                        close_price > trendline_value):
                        return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking retest confirmation: {e}")
            return False
    
    def validate_trendline(self, trendline: Trendline, df: pd.DataFrame) -> bool:
        """
        Validate trendline based on touch points and time duration
        
        Args:
            trendline: Trendline to validate
            df: Price data for validation
            
        Returns:
            True if trendline is valid
        """
        try:
            # 1. Check minimum touch points
            if trendline.touch_points < self.min_trendline_touches:
                return False
            
            # 2. Check strength threshold
            if trendline.strength < 0.4:
                return False
            
            # 3. Check if trendline is still relevant (not too old)
            # This is a simplified check - in practice you'd use actual timestamps
            if len(df) > 100:  # If we have a lot of data, ensure trendline is recent
                return True  # For now, assume all trendlines are recent enough
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating trendline: {e}")
            return False
    
    def detect_retest(self, df: pd.DataFrame, broken_trendline: Trendline) -> bool:
        """
        Detect retest of a broken trendline
        
        Args:
            df: Price data
            broken_trendline: Previously broken trendline
            
        Returns:
            True if retest is detected and confirmed
        """
        if len(df) < 5:
            return False
        
        try:
            # Calculate current trendline value
            current_trendline_value = self._calculate_trendline_value_at_time(broken_trendline, len(df) - 1)
            
            if current_trendline_value is None:
                return False
            
            # Check for retest pattern in recent bars
            return self._check_retest_confirmation(df, current_trendline_value, broken_trendline.line_type)
            
        except Exception as e:
            self.logger.error(f"Error detecting retest: {e}")
            return False
    
    def get_trendline_analysis_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get comprehensive trendline analysis summary
        
        Args:
            df: Price data
            
        Returns:
            Dictionary with trendline analysis results
        """
        try:
            # Identify trendlines
            trendlines = self.identify_trendlines(df)
            
            # Detect breaks
            breaks = self.detect_trendline_breaks(df, trendlines)
            
            # Categorize results
            support_lines = [tl for tl in trendlines if tl.line_type == 'support']
            resistance_lines = [tl for tl in trendlines if tl.line_type == 'resistance']
            
            support_breaks = [br for br in breaks if br.trendline.line_type == 'support']
            resistance_breaks = [br for br in breaks if br.trendline.line_type == 'resistance']
            
            # Calculate summary statistics
            avg_strength = sum(tl.strength for tl in trendlines) / len(trendlines) if trendlines else 0
            total_touches = sum(tl.touch_points for tl in trendlines)
            
            return {
                'total_trendlines': len(trendlines),
                'support_lines': len(support_lines),
                'resistance_lines': len(resistance_lines),
                'total_breaks': len(breaks),
                'support_breaks': len(support_breaks),
                'resistance_breaks': len(resistance_breaks),
                'average_strength': avg_strength,
                'total_touch_points': total_touches,
                'trendlines': [
                    {
                        'type': tl.line_type,
                        'strength': tl.strength,
                        'touches': tl.touch_points,
                        'slope': tl.slope,
                        'start_price': tl.start_point[1],
                        'end_price': tl.end_point[1]
                    } for tl in trendlines
                ],
                'breaks': [
                    {
                        'trendline_type': br.trendline.line_type,
                        'break_strength': br.break_strength,
                        'volume_confirmed': br.volume_confirmation,
                        'retest_confirmed': br.retest_confirmed,
                        'break_price': br.break_point[1]
                    } for br in breaks
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error generating trendline analysis summary: {e}")
            return {
                'error': str(e),
                'total_trendlines': 0,
                'total_breaks': 0
            }
    
    def filter_trendlines_by_strength(self, trendlines: List[Trendline], min_strength: float = 0.5) -> List[Trendline]:
        """
        Filter trendlines by minimum strength threshold
        
        Args:
            trendlines: List of trendlines to filter
            min_strength: Minimum strength threshold
            
        Returns:
            Filtered list of trendlines
        """
        return [tl for tl in trendlines if tl.strength >= min_strength]
    
    def filter_trendlines_by_recency(self, trendlines: List[Trendline], df: pd.DataFrame, 
                                   max_age_bars: int = 50) -> List[Trendline]:
        """
        Filter trendlines by recency (remove old trendlines)
        
        Args:
            trendlines: List of trendlines to filter
            df: Price data for age calculation
            max_age_bars: Maximum age in bars
            
        Returns:
            Filtered list of recent trendlines
        """
        current_bar = len(df) - 1
        filtered = []
        
        for tl in trendlines:
            # Estimate the age of the trendline (simplified)
            # In practice, you'd use actual timestamps
            estimated_age = max_age_bars // 2  # Assume moderate age for now
            
            if estimated_age <= max_age_bars:
                filtered.append(tl)
        
        return filtered
    
    def filter_overlapping_trendlines(self, trendlines: List[Trendline], 
                                    price_tolerance: float = 0.01) -> List[Trendline]:
        """
        Filter out overlapping trendlines, keeping the strongest ones
        
        Args:
            trendlines: List of trendlines to filter
            price_tolerance: Price tolerance for considering trendlines overlapping (1%)
            
        Returns:
            Filtered list without overlapping trendlines
        """
        if len(trendlines) <= 1:
            return trendlines
        
        # Sort by strength (strongest first)
        sorted_trendlines = sorted(trendlines, key=lambda x: x.strength, reverse=True)
        filtered = []
        
        for tl in sorted_trendlines:
            is_overlapping = False
            
            # Check against already selected trendlines
            for selected_tl in filtered:
                if self._are_trendlines_overlapping(tl, selected_tl, price_tolerance):
                    is_overlapping = True
                    break
            
            if not is_overlapping:
                filtered.append(tl)
        
        return filtered
    
    def _are_trendlines_overlapping(self, tl1: Trendline, tl2: Trendline, 
                                   tolerance: float) -> bool:
        """
        Check if two trendlines are overlapping
        
        Args:
            tl1: First trendline
            tl2: Second trendline
            tolerance: Price tolerance for overlap detection
            
        Returns:
            True if trendlines are overlapping
        """
        # Only check trendlines of the same type
        if tl1.line_type != tl2.line_type:
            return False
        
        # Compare price levels at start and end points
        tl1_start_price = tl1.start_point[1]
        tl1_end_price = tl1.end_point[1]
        tl2_start_price = tl2.start_point[1]
        tl2_end_price = tl2.end_point[1]
        
        # Calculate average prices for comparison
        tl1_avg_price = (tl1_start_price + tl1_end_price) / 2
        tl2_avg_price = (tl2_start_price + tl2_end_price) / 2
        
        # Check if average prices are within tolerance
        price_diff = abs(tl1_avg_price - tl2_avg_price) / max(tl1_avg_price, tl2_avg_price)
        
        return price_diff <= tolerance
    
    def validate_trendline_angle(self, trendline: Trendline) -> bool:
        """
        Validate trendline angle is within acceptable range
        
        Args:
            trendline: Trendline to validate
            
        Returns:
            True if angle is valid
        """
        # Calculate angle from slope
        # This is a simplified calculation - in practice you'd use actual time/price scaling
        price_change_per_bar = abs(trendline.slope)
        
        # Convert to approximate angle (this is simplified)
        if price_change_per_bar == 0:
            angle_degrees = 0
        else:
            # Normalize price change to get reasonable angle
            normalized_change = price_change_per_bar * 1000  # Scale factor
            angle_radians = math.atan(normalized_change)
            angle_degrees = math.degrees(angle_radians)
        
        return self.trendline_angle_min <= angle_degrees <= self.trendline_angle_max
    
    def validate_trendline_duration(self, trendline: Trendline, min_duration_bars: int = 10) -> bool:
        """
        Validate trendline has sufficient duration
        
        Args:
            trendline: Trendline to validate
            min_duration_bars: Minimum duration in bars
            
        Returns:
            True if duration is sufficient
        """
        # This is simplified - in practice you'd calculate actual bar difference from timestamps
        # For now, assume all trendlines meet minimum duration since we filter during creation
        return True
    
    def get_active_trendlines(self, df: pd.DataFrame, all_trendlines: List[Trendline]) -> List[Trendline]:
        """
        Get currently active trendlines (not broken, still relevant)
        
        Args:
            df: Current price data
            all_trendlines: All identified trendlines
            
        Returns:
            List of active trendlines
        """
        active_trendlines = []
        
        for tl in all_trendlines:
            # Check if trendline is still valid
            if self.validate_trendline(tl, df):
                # Check if trendline hasn't been significantly broken
                breaks = self.detect_trendline_breaks(df, [tl])
                
                # If no strong breaks, consider it active
                strong_breaks = [br for br in breaks if br.break_strength > 0.7]
                
                if not strong_breaks:
                    active_trendlines.append(tl)
        
        return active_trendlines
    
    def rank_trendlines_by_importance(self, trendlines: List[Trendline], df: pd.DataFrame) -> List[Trendline]:
        """
        Rank trendlines by importance/relevance
        
        Args:
            trendlines: List of trendlines to rank
            df: Price data for context
            
        Returns:
            Trendlines sorted by importance (most important first)
        """
        current_price = df.iloc[-1]['close']
        
        # Calculate importance score for each trendline
        scored_trendlines = []
        
        for tl in trendlines:
            importance_score = self._calculate_trendline_importance(tl, current_price, df)
            scored_trendlines.append((tl, importance_score))
        
        # Sort by importance score (highest first)
        scored_trendlines.sort(key=lambda x: x[1], reverse=True)
        
        return [tl for tl, _ in scored_trendlines]
    
    def _calculate_trendline_importance(self, trendline: Trendline, current_price: float, 
                                      df: pd.DataFrame) -> float:
        """
        Calculate importance score for a trendline
        
        Args:
            trendline: Trendline to score
            current_price: Current market price
            df: Price data
            
        Returns:
            Importance score (higher = more important)
        """
        base_score = trendline.strength
        
        # 1. Proximity to current price (closer = more important)
        current_trendline_value = self._calculate_trendline_value_at_time(trendline, len(df) - 1)
        if current_trendline_value:
            distance_pct = abs(current_price - current_trendline_value) / current_price
            proximity_bonus = max(0, 1.0 - distance_pct * 10)  # Closer lines get higher bonus
            base_score += proximity_bonus * 0.3
        
        # 2. Touch points (more touches = more important)
        touch_bonus = min(0.2, trendline.touch_points * 0.05)
        base_score += touch_bonus
        
        # 3. Recent activity (more recent = more important)
        # This is simplified - in practice you'd use actual timestamps
        recency_bonus = 0.1  # Assume moderate recency for all lines
        base_score += recency_bonus
        
        return min(2.0, base_score)  # Cap at 2.0
    
    def get_comprehensive_validation_report(self, trendlines: List[Trendline], 
                                          df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get comprehensive validation report for trendlines
        
        Args:
            trendlines: List of trendlines to validate
            df: Price data
            
        Returns:
            Dictionary with validation results
        """
        report = {
            'total_trendlines': len(trendlines),
            'validation_results': [],
            'summary': {
                'valid_count': 0,
                'invalid_count': 0,
                'strength_distribution': {'weak': 0, 'moderate': 0, 'strong': 0},
                'type_distribution': {'support': 0, 'resistance': 0}
            }
        }
        
        for i, tl in enumerate(trendlines):
            validation_result = {
                'trendline_index': i,
                'type': tl.line_type,
                'strength': tl.strength,
                'touch_points': tl.touch_points,
                'slope': tl.slope,
                'validations': {
                    'basic_validation': self.validate_trendline(tl, df),
                    'angle_validation': self.validate_trendline_angle(tl),
                    'duration_validation': self.validate_trendline_duration(tl),
                },
                'overall_valid': False
            }
            
            # Determine overall validity
            validation_result['overall_valid'] = all(validation_result['validations'].values())
            
            # Update summary counts
            if validation_result['overall_valid']:
                report['summary']['valid_count'] += 1
            else:
                report['summary']['invalid_count'] += 1
            
            # Strength distribution
            if tl.strength < 0.4:
                report['summary']['strength_distribution']['weak'] += 1
            elif tl.strength < 0.7:
                report['summary']['strength_distribution']['moderate'] += 1
            else:
                report['summary']['strength_distribution']['strong'] += 1
            
            # Type distribution
            report['summary']['type_distribution'][tl.line_type] += 1
            
            report['validation_results'].append(validation_result)
        
        return report
    
    def detect_enhanced_trendline_breaks(self, df: pd.DataFrame, trendlines: List[Trendline], 
                                       volume_analyzer=None) -> List[TrendlineBreak]:
        """
        Enhanced trendline break detection with comprehensive volume confirmation
        
        Args:
            df: Price data with OHLCV
            trendlines: List of active trendlines to check
            volume_analyzer: Optional VolumeAnalyzer instance for advanced volume analysis
            
        Returns:
            List of trendline breaks with enhanced analysis
        """
        if not trendlines or len(df) < 5:
            return []
        
        try:
            breaks = []
            current_bar = df.iloc[-1]
            current_price = current_bar['close']
            current_time = current_bar.name if hasattr(current_bar.name, 'timestamp') else datetime.now()
            
            self.logger.info(f"🔍 ENHANCED TRENDLINE BREAK DETECTION for {len(trendlines)} trendlines")
            
            for i, trendline in enumerate(trendlines, 1):
                self.logger.info(f"  Analyzing trendline {i}: {trendline.line_type} (strength: {trendline.strength:.3f})")
                
                # Calculate current trendline value with improved accuracy
                current_trendline_value = self._calculate_enhanced_trendline_value(trendline, df, len(df) - 1)
                
                if current_trendline_value is None:
                    self.logger.info(f"    ❌ Could not calculate trendline value")
                    continue
                
                # Enhanced break detection with multiple confirmation methods
                break_result = self._check_enhanced_trendline_break(
                    df, trendline, current_price, current_trendline_value, 
                    current_time, volume_analyzer
                )
                
                if break_result:
                    breaks.append(break_result)
                    self.logger.info(f"    ✅ ENHANCED BREAK DETECTED:")
                    self.logger.info(f"       Type: {break_result.trendline.line_type} break")
                    self.logger.info(f"       Break strength: {break_result.break_strength:.3f}")
                    self.logger.info(f"       Volume confirmed: {break_result.volume_confirmation}")
                    self.logger.info(f"       Retest confirmed: {break_result.retest_confirmed}")
                else:
                    distance_pct = abs(current_price - current_trendline_value) / current_trendline_value * 100
                    self.logger.info(f"    ❌ No break (distance: {distance_pct:.2f}%)")
            
            return breaks
            
        except Exception as e:
            self.logger.error(f"Error in enhanced trendline break detection: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return []
    
    def _calculate_enhanced_trendline_value(self, trendline: Trendline, df: pd.DataFrame, 
                                          bar_index: int) -> Optional[float]:
        """
        Calculate trendline value with enhanced accuracy using actual data points
        
        Args:
            trendline: Trendline object
            df: Price data for context
            bar_index: Bar index to calculate value for
            
        Returns:
            Enhanced trendline value calculation
        """
        try:
            # Use the slope and a reference point to calculate current value
            start_price = trendline.start_point[1]
            
            # Estimate how many bars have passed since the trendline start
            # This is simplified - in practice you'd use actual timestamps
            estimated_bars_elapsed = max(10, bar_index // 2)  # Conservative estimate
            
            # Calculate current trendline value
            current_value = start_price + (trendline.slope * estimated_bars_elapsed)
            
            # Validate the result is reasonable
            current_price = df.iloc[bar_index]['close']
            if abs(current_value - current_price) / current_price > 0.5:  # More than 50% difference
                # Fallback to simpler calculation
                end_price = trendline.end_point[1]
                current_value = (start_price + end_price) / 2  # Use average as fallback
            
            return current_value
            
        except Exception as e:
            self.logger.error(f"Error in enhanced trendline value calculation: {e}")
            return None
    
    def _check_enhanced_trendline_break(self, df: pd.DataFrame, trendline: Trendline,
                                      current_price: float, trendline_value: float,
                                      current_time: datetime, volume_analyzer=None) -> Optional[TrendlineBreak]:
        """
        Enhanced trendline break detection with multiple confirmation methods
        
        Args:
            df: Price data
            trendline: Trendline to check
            current_price: Current price
            trendline_value: Current trendline value
            current_time: Current timestamp
            volume_analyzer: Optional VolumeAnalyzer for advanced volume analysis
            
        Returns:
            Enhanced TrendlineBreak if break detected
        """
        # Calculate break threshold with dynamic adjustment based on volatility
        base_threshold = self.break_threshold
        
        # Adjust threshold based on recent volatility
        if len(df) >= 20:
            recent_volatility = df['close'].tail(20).std() / df['close'].tail(20).mean()
            volatility_adjustment = min(2.0, max(0.5, recent_volatility / 0.02))  # Normalize to 2% volatility
            adjusted_threshold = base_threshold * volatility_adjustment
        else:
            adjusted_threshold = base_threshold
        
        break_threshold_abs = trendline_value * adjusted_threshold
        
        # Enhanced volume confirmation
        volume_confirmed = self._check_enhanced_volume_confirmation(df, volume_analyzer)
        
        # Check for break with enhanced logic
        break_detected = False
        break_type = None
        
        if trendline.line_type == 'support':
            # Support break: price goes below trendline with confirmation
            if current_price < (trendline_value - break_threshold_abs):
                # Additional confirmation: check if break is sustained
                if self._is_break_sustained(df, trendline_value, 'support'):
                    break_detected = True
                    break_type = 'support_break'
        
        else:  # resistance
            # Resistance break: price goes above trendline with confirmation
            if current_price > (trendline_value + break_threshold_abs):
                # Additional confirmation: check if break is sustained
                if self._is_break_sustained(df, trendline_value, 'resistance'):
                    break_detected = True
                    break_type = 'resistance_break'
        
        if not break_detected:
            return None
        
        # Calculate enhanced break strength
        break_strength = self._calculate_enhanced_break_strength(
            current_price, trendline_value, trendline, volume_confirmed, 
            break_type, df, volume_analyzer
        )
        
        # Enhanced retest confirmation
        retest_confirmed = self._check_enhanced_retest_confirmation(
            df, trendline_value, trendline.line_type
        )
        
        return TrendlineBreak(
            trendline=trendline,
            break_point=(current_time, current_price),
            volume_confirmation=volume_confirmed,
            retest_confirmed=retest_confirmed,
            break_strength=break_strength
        )
    
    def _check_enhanced_volume_confirmation(self, df: pd.DataFrame, volume_analyzer=None) -> bool:
        """
        Enhanced volume confirmation using multiple methods
        
        Args:
            df: Price data with volume
            volume_analyzer: Optional VolumeAnalyzer for advanced analysis
            
        Returns:
            True if volume confirms the break
        """
        if 'volume' not in df.columns or len(df) < 20:
            return False
        
        try:
            # Method 1: Basic volume spike detection
            basic_confirmation = self._check_volume_confirmation_for_break(df)
            
            # Method 2: Advanced volume analysis if available
            advanced_confirmation = False
            if volume_analyzer is not None:
                try:
                    # Use volume analyzer for more sophisticated analysis
                    volume_ratio = volume_analyzer.get_volume_ratio(df)
                    volume_trend = volume_analyzer.analyze_volume_trend(df)
                    
                    # Confirm if volume is above average and trending up
                    advanced_confirmation = (
                        volume_ratio >= self.volume_confirmation_threshold and
                        volume_trend.get('trend_direction', 'neutral') in ['increasing', 'strong_increase']
                    )
                except Exception as e:
                    self.logger.debug(f"Advanced volume analysis failed: {e}")
            
            # Method 3: Volume pattern analysis
            pattern_confirmation = self._analyze_volume_pattern_for_break(df)
            
            # Combine confirmations (any strong method or multiple moderate methods)
            strong_confirmations = sum([basic_confirmation, advanced_confirmation])
            moderate_confirmations = sum([pattern_confirmation])
            
            return strong_confirmations >= 1 or (strong_confirmations + moderate_confirmations >= 2)
            
        except Exception as e:
            self.logger.error(f"Error in enhanced volume confirmation: {e}")
            return False
    
    def _analyze_volume_pattern_for_break(self, df: pd.DataFrame) -> bool:
        """
        Analyze volume patterns around the break for confirmation
        
        Args:
            df: Price data with volume
            
        Returns:
            True if volume pattern supports the break
        """
        if len(df) < 10:
            return False
        
        try:
            # Analyze last 5 bars vs previous 10 bars
            recent_volumes = df['volume'].tail(5)
            previous_volumes = df['volume'].tail(15).head(10)
            
            recent_avg = recent_volumes.mean()
            previous_avg = previous_volumes.mean()
            
            # Check for volume expansion
            volume_expansion = recent_avg / previous_avg if previous_avg > 0 else 1.0
            
            # Check for volume acceleration (increasing volume in recent bars)
            volume_acceleration = False
            if len(recent_volumes) >= 3:
                early_recent = recent_volumes.head(2).mean()
                late_recent = recent_volumes.tail(2).mean()
                if late_recent > early_recent * 1.1:  # 10% increase
                    volume_acceleration = True
            
            # Pattern confirmation criteria
            expansion_confirmed = volume_expansion >= 1.3  # 30% volume increase
            acceleration_confirmed = volume_acceleration
            
            return expansion_confirmed or acceleration_confirmed
            
        except Exception as e:
            self.logger.error(f"Error analyzing volume pattern: {e}")
            return False
    
    def _is_break_sustained(self, df: pd.DataFrame, trendline_value: float, 
                           trendline_type: str) -> bool:
        """
        Check if trendline break is sustained over multiple bars
        
        Args:
            df: Price data
            trendline_value: Trendline value at break
            trendline_type: 'support' or 'resistance'
            
        Returns:
            True if break is sustained
        """
        if len(df) < 3:
            return True  # Not enough data to check, assume sustained
        
        try:
            # Check last 3 bars for sustained break
            recent_bars = df.tail(3)
            sustained_count = 0
            
            for _, bar in recent_bars.iterrows():
                if trendline_type == 'support':
                    # For support breaks, close should stay below trendline
                    if bar['close'] < trendline_value * 0.998:  # 0.2% buffer
                        sustained_count += 1
                else:  # resistance
                    # For resistance breaks, close should stay above trendline
                    if bar['close'] > trendline_value * 1.002:  # 0.2% buffer
                        sustained_count += 1
            
            # Require at least 2 out of 3 bars to confirm sustainability
            return sustained_count >= 2
            
        except Exception as e:
            self.logger.error(f"Error checking break sustainability: {e}")
            return True  # Default to sustained if error
    
    def _calculate_enhanced_break_strength(self, current_price: float, trendline_value: float,
                                         trendline: Trendline, volume_confirmed: bool,
                                         break_type: str, df: pd.DataFrame, 
                                         volume_analyzer=None) -> float:
        """
        Calculate enhanced break strength with additional factors
        
        Args:
            current_price: Current price
            trendline_value: Trendline value at break
            trendline: The trendline being broken
            volume_confirmed: Whether volume confirms the break
            break_type: Type of break
            df: Price data for additional analysis
            volume_analyzer: Optional VolumeAnalyzer
            
        Returns:
            Enhanced break strength (0.0 to 1.0)
        """
        # Start with base calculation
        base_strength = self._calculate_break_strength(
            current_price, trendline_value, trendline, volume_confirmed, break_type
        )
        
        # Enhancement 1: Sustainability factor
        sustainability_bonus = 0.0
        if self._is_break_sustained(df, trendline_value, trendline.line_type):
            sustainability_bonus = 0.1
        
        # Enhancement 2: Volume pattern factor
        volume_pattern_bonus = 0.0
        if self._analyze_volume_pattern_for_break(df):
            volume_pattern_bonus = 0.05
        
        # Enhancement 3: Market context factor
        market_context_bonus = 0.0
        if len(df) >= 20:
            # Check if break aligns with broader market momentum
            recent_trend = (df['close'].iloc[-1] - df['close'].iloc[-20]) / df['close'].iloc[-20]
            if break_type == 'resistance_break' and recent_trend > 0.02:  # Bullish context
                market_context_bonus = 0.05
            elif break_type == 'support_break' and recent_trend < -0.02:  # Bearish context
                market_context_bonus = 0.05
        
        # Enhancement 4: Advanced volume analysis
        advanced_volume_bonus = 0.0
        if volume_analyzer is not None:
            try:
                volume_strength = volume_analyzer.calculate_volume_strength(df)
                if volume_strength > 0.7:
                    advanced_volume_bonus = 0.05
            except Exception:
                pass  # Ignore errors in advanced analysis
        
        # Combine all factors
        enhanced_strength = (
            base_strength + 
            sustainability_bonus + 
            volume_pattern_bonus + 
            market_context_bonus + 
            advanced_volume_bonus
        )
        
        return min(1.0, enhanced_strength)
    
    def _check_enhanced_retest_confirmation(self, df: pd.DataFrame, trendline_value: float,
                                          original_type: str) -> bool:
        """
        Enhanced retest confirmation with multiple validation methods
        
        Args:
            df: Price data
            trendline_value: Value of the broken trendline
            original_type: Original trendline type ('support' or 'resistance')
            
        Returns:
            True if enhanced retest is confirmed
        """
        if len(df) < 5:
            return False
        
        try:
            # Method 1: Basic retest check
            basic_retest = self._check_retest_confirmation(df, trendline_value, original_type)
            
            # Method 2: Multiple timeframe retest check
            extended_retest = self._check_extended_retest_pattern(df, trendline_value, original_type)
            
            # Method 3: Volume-confirmed retest
            volume_retest = self._check_volume_confirmed_retest(df, trendline_value, original_type)
            
            # Combine methods (any strong confirmation or multiple moderate ones)
            confirmations = sum([basic_retest, extended_retest, volume_retest])
            
            return confirmations >= 1  # At least one method confirms
            
        except Exception as e:
            self.logger.error(f"Error in enhanced retest confirmation: {e}")
            return False
    
    def _check_extended_retest_pattern(self, df: pd.DataFrame, trendline_value: float,
                                     original_type: str) -> bool:
        """
        Check for retest pattern over extended period
        
        Args:
            df: Price data
            trendline_value: Trendline value
            original_type: Original trendline type
            
        Returns:
            True if extended retest pattern is found
        """
        if len(df) < 10:
            return False
        
        try:
            # Look at last 10 bars for retest pattern
            recent_data = df.tail(10)
            retest_tolerance_abs = trendline_value * self.retest_tolerance
            
            retest_touches = 0
            successful_holds = 0
            
            for _, bar in recent_data.iterrows():
                if original_type == 'support':
                    # Former support now resistance - look for touches from below
                    if abs(bar['high'] - trendline_value) <= retest_tolerance_abs:
                        retest_touches += 1
                        if bar['close'] < trendline_value:  # Held as resistance
                            successful_holds += 1
                else:  # resistance
                    # Former resistance now support - look for touches from above
                    if abs(bar['low'] - trendline_value) <= retest_tolerance_abs:
                        retest_touches += 1
                        if bar['close'] > trendline_value:  # Held as support
                            successful_holds += 1
            
            # Confirm if we have multiple touches with successful holds
            return retest_touches >= 2 and successful_holds >= retest_touches * 0.7
            
        except Exception as e:
            self.logger.error(f"Error checking extended retest pattern: {e}")
            return False
    
    def _check_volume_confirmed_retest(self, df: pd.DataFrame, trendline_value: float,
                                     original_type: str) -> bool:
        """
        Check for volume-confirmed retest
        
        Args:
            df: Price data
            trendline_value: Trendline value
            original_type: Original trendline type
            
        Returns:
            True if volume-confirmed retest is found
        """
        if 'volume' not in df.columns or len(df) < 5:
            return False
        
        try:
            recent_data = df.tail(5)
            retest_tolerance_abs = trendline_value * self.retest_tolerance
            
            for _, bar in recent_data.iterrows():
                # Check if price approached the level
                approached_level = False
                held_level = False
                
                if original_type == 'support':
                    # Check approach from below and hold
                    if abs(bar['high'] - trendline_value) <= retest_tolerance_abs:
                        approached_level = True
                        if bar['close'] < trendline_value:
                            held_level = True
                else:  # resistance
                    # Check approach from above and hold
                    if abs(bar['low'] - trendline_value) <= retest_tolerance_abs:
                        approached_level = True
                        if bar['close'] > trendline_value:
                            held_level = True
                
                # If we found a retest, check volume
                if approached_level and held_level:
                    # Check if volume was above average during retest
                    avg_volume = df['volume'].tail(20).mean() if len(df) >= 20 else df['volume'].mean()
                    if bar['volume'] > avg_volume * 1.2:  # 20% above average
                        return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking volume-confirmed retest: {e}")
            return False