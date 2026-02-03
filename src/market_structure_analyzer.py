"""
Market Structure Analyzer for Advanced Trend Detection
Detects broken market structure patterns and support/resistance zones
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
import logging

# Import data models from trend detection engine
from src.trend_detection_engine import StructureBreakResult, BreakType

logger = logging.getLogger(__name__)

@dataclass
class SwingPoint:
    """Represents a swing high or low point"""
    index: int
    timestamp: datetime
    price: float
    swing_type: str  # 'high' or 'low'
    strength: int    # Number of bars on each side
    volume: float

@dataclass
class SRLevel:
    """Represents a support or resistance level"""
    price: float
    level_type: str  # 'support' or 'resistance'
    strength: float  # Based on number of touches and volume
    first_touch: datetime
    last_touch: datetime
    touch_count: int
    active: bool

class MarketStructureAnalyzer:
    """
    Analyzes market structure to detect trend changes and key levels
    Implements swing point detection and structure break analysis
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the market structure analyzer
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Configuration parameters
        self.swing_strength = config.get('swing_strength', 5)  # Bars on each side for swing detection
        self.min_structure_distance = config.get('min_structure_distance', 0.001)  # Minimum distance for structure break
        self.volume_confirmation_threshold = config.get('volume_confirmation_threshold', 1.5)  # Volume multiplier
        
        self.logger.info(f"MarketStructureAnalyzer initialized with swing_strength={self.swing_strength}")
    
    def detect_structure_break(self, df: pd.DataFrame) -> Optional[StructureBreakResult]:
        """
        Detect broken market structure patterns
        
        Args:
            df: Price data with OHLCV
            
        Returns:
            StructureBreakResult if structure break detected, None otherwise
        """
        if len(df) < self.swing_strength * 4:  # Need enough data for swing detection
            return None
        
        try:
            # Identify swing points
            swing_highs = self._find_swing_points(df, 'high')
            swing_lows = self._find_swing_points(df, 'low')
            
            if len(swing_highs) < 2 or len(swing_lows) < 2:
                return None
            
            # Get current price for confirmation
            current_price = df.iloc[-1]['close']
            
            # Check for structure breaks in different scenarios
            structure_breaks = []
            
            # 1. Check for higher high breaks (potential bearish structure break)
            hh_break = self._check_higher_high_break(swing_highs, current_price, df)
            if hh_break:
                structure_breaks.append(hh_break)
            
            # 2. Check for lower low breaks (potential bullish structure break)
            ll_break = self._check_lower_low_break(swing_lows, current_price, df)
            if ll_break:
                structure_breaks.append(ll_break)
            
            # 3. Check for support/resistance level breaks
            sr_levels = self.identify_support_resistance(df)
            sr_break = self._check_sr_level_break(sr_levels, current_price, df)
            if sr_break:
                structure_breaks.append(sr_break)
            
            # Return the strongest structure break
            if structure_breaks:
                # Sort by strength and return the strongest
                structure_breaks.sort(key=lambda x: x.strength, reverse=True)
                return structure_breaks[0]
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error in structure break detection: {e}")
            return None
    
    def _check_higher_high_break(self, swing_highs: List[SwingPoint], current_price: float, df: pd.DataFrame) -> Optional[StructureBreakResult]:
        """Check for higher high structure breaks"""
        if len(swing_highs) < 2:
            return None
        
        latest_high = swing_highs[-1]
        previous_high = swing_highs[-2]
        
        # Check if we have a new higher high
        if latest_high.price > previous_high.price:
            # Check if price has failed to sustain above the high (bearish structure break)
            if current_price < latest_high.price * 0.995:  # 0.5% below high
                volume_confirmed = self._check_volume_confirmation(df, latest_high.index)
                strength = self._calculate_structure_break_strength(
                    latest_high.price, previous_high.price, volume_confirmed, df
                )
                
                return StructureBreakResult(
                    break_type=BreakType.HIGHER_HIGH.value,
                    break_level=latest_high.price,
                    previous_level=previous_high.price,
                    volume_confirmation=volume_confirmed,
                    strength=strength,
                    confirmed=self._is_break_confirmed(df, latest_high.price, 'resistance')
                )
        
        return None
    
    def _check_lower_low_break(self, swing_lows: List[SwingPoint], current_price: float, df: pd.DataFrame) -> Optional[StructureBreakResult]:
        """Check for lower low structure breaks"""
        if len(swing_lows) < 2:
            return None
        
        latest_low = swing_lows[-1]
        previous_low = swing_lows[-2]
        
        # Check if we have a new lower low
        if latest_low.price < previous_low.price:
            # Check if price has recovered above the low (bullish structure break)
            if current_price > latest_low.price * 1.005:  # 0.5% above low
                volume_confirmed = self._check_volume_confirmation(df, latest_low.index)
                strength = self._calculate_structure_break_strength(
                    latest_low.price, previous_low.price, volume_confirmed, df
                )
                
                return StructureBreakResult(
                    break_type=BreakType.LOWER_LOW.value,
                    break_level=latest_low.price,
                    previous_level=previous_low.price,
                    volume_confirmation=volume_confirmed,
                    strength=strength,
                    confirmed=self._is_break_confirmed(df, latest_low.price, 'support')
                )
        
        return None
    
    def _check_sr_level_break(self, sr_levels: List[SRLevel], current_price: float, df: pd.DataFrame) -> Optional[StructureBreakResult]:
        """Check for support/resistance level breaks"""
        if not sr_levels:
            return None
        
        # Check for recent breaks of strong S/R levels
        for level in sr_levels:
            if not level.active or level.strength < 0.5:  # Only check strong levels
                continue
            
            price_diff_pct = abs(current_price - level.price) / level.price
            
            # Check if we're near the level (within 0.1%)
            if price_diff_pct < 0.001:
                continue
            
            # Determine break type
            if level.level_type == 'resistance' and current_price > level.price * 1.002:  # 0.2% above resistance
                break_type = BreakType.RESISTANCE_BREAK.value
                volume_confirmed = self._check_recent_volume_spike(df)
                
            elif level.level_type == 'support' and current_price < level.price * 0.998:  # 0.2% below support
                break_type = BreakType.SUPPORT_BREAK.value
                volume_confirmed = self._check_recent_volume_spike(df)
                
            else:
                continue
            
            # Calculate break strength
            strength = min(0.9, level.strength + (0.2 if volume_confirmed else 0))
            
            return StructureBreakResult(
                break_type=break_type,
                break_level=level.price,
                previous_level=level.price,  # Same level for S/R breaks
                volume_confirmation=volume_confirmed,
                strength=strength,
                confirmed=True  # S/R breaks are immediately confirmed
            )
        
        return None
    
    def _calculate_structure_break_strength(self, break_level: float, previous_level: float, 
                                          volume_confirmed: bool, df: pd.DataFrame) -> float:
        """Calculate the strength of a structure break"""
        base_strength = 0.5
        
        # Add strength for volume confirmation
        if volume_confirmed:
            base_strength += 0.2
        
        # Add strength based on break magnitude
        break_magnitude = abs(break_level - previous_level) / previous_level
        if break_magnitude > 0.02:  # 2% break
            base_strength += 0.2
        elif break_magnitude > 0.01:  # 1% break
            base_strength += 0.1
        elif break_magnitude > 0.005:  # 0.5% break
            base_strength += 0.05
        
        # Add strength based on recent price action
        if len(df) >= 10:
            recent_volatility = df['close'].tail(10).std() / df['close'].tail(10).mean()
            if recent_volatility > 0.02:  # High volatility adds strength
                base_strength += 0.1
        
        return min(1.0, base_strength)
    
    def _is_break_confirmed(self, df: pd.DataFrame, break_level: float, level_type: str) -> bool:
        """Check if structure break is confirmed by subsequent price action"""
        if len(df) < 5:
            return False
        
        # Check last 5 bars for confirmation
        recent_closes = df['close'].tail(5)
        
        if level_type == 'resistance':
            # For resistance breaks, confirmation is staying above
            return all(close > break_level * 0.995 for close in recent_closes)
        else:  # support
            # For support breaks, confirmation is staying below
            return all(close < break_level * 1.005 for close in recent_closes)
    
    def _check_recent_volume_spike(self, df: pd.DataFrame) -> bool:
        """Check for recent volume spike in last few bars"""
        if 'volume' not in df.columns or len(df) < 20:
            return False
        
        try:
            # Check last 3 bars for volume spike
            recent_volume = df['volume'].tail(3).max()
            avg_volume = df['volume'].tail(20).mean()
            
            return recent_volume > avg_volume * self.volume_confirmation_threshold
            
        except Exception:
            return False
    
    def identify_support_resistance(self, df: pd.DataFrame) -> List[SRLevel]:
        """
        Identify support and resistance levels
        
        Args:
            df: Price data with OHLCV
            
        Returns:
            List of support/resistance levels
        """
        if len(df) < self.swing_strength * 4:
            return []
        
        try:
            sr_levels = []
            
            # Find swing points for both highs and lows
            swing_highs = self._find_swing_points(df, 'high')
            swing_lows = self._find_swing_points(df, 'low')
            
            # Group swing points by price level (with tolerance)
            tolerance = self.config.get('sr_tolerance', 0.0005)  # 0.05% tolerance
            
            # Process swing highs for resistance levels
            resistance_groups = self._group_price_levels(swing_highs, tolerance)
            for group in resistance_groups:
                if len(group) >= 2:  # At least 2 touches
                    avg_price = sum(point.price for point in group) / len(group)
                    strength = self._calculate_sr_strength(group, df)
                    
                    sr_levels.append(SRLevel(
                        price=avg_price,
                        level_type='resistance',
                        strength=strength,
                        first_touch=min(point.timestamp for point in group),
                        last_touch=max(point.timestamp for point in group),
                        touch_count=len(group),
                        active=True
                    ))
            
            # Process swing lows for support levels
            support_groups = self._group_price_levels(swing_lows, tolerance)
            for group in support_groups:
                if len(group) >= 2:  # At least 2 touches
                    avg_price = sum(point.price for point in group) / len(group)
                    strength = self._calculate_sr_strength(group, df)
                    
                    sr_levels.append(SRLevel(
                        price=avg_price,
                        level_type='support',
                        strength=strength,
                        first_touch=min(point.timestamp for point in group),
                        last_touch=max(point.timestamp for point in group),
                        touch_count=len(group),
                        active=True
                    ))
            
            # Sort by strength (strongest first)
            sr_levels.sort(key=lambda x: x.strength, reverse=True)
            
            # Keep only top levels to avoid clutter
            max_levels = self.config.get('max_sr_levels', 10)
            return sr_levels[:max_levels]
            
        except Exception as e:
            self.logger.error(f"Error identifying support/resistance levels: {e}")
            return []
    
    def calculate_structure_strength(self, break_info: StructureBreakResult) -> float:
        """
        Calculate the strength of a structure break
        
        Args:
            break_info: Structure break information
            
        Returns:
            Strength score (0.0 to 1.0)
        """
        base_strength = 0.5
        
        # Add strength for volume confirmation
        if break_info.volume_confirmation:
            base_strength += 0.2
        
        # Add strength based on break magnitude
        break_magnitude = abs(break_info.break_level - break_info.previous_level) / break_info.previous_level
        if break_magnitude > 0.01:  # 1% break
            base_strength += 0.2
        elif break_magnitude > 0.005:  # 0.5% break
            base_strength += 0.1
        
        return min(1.0, base_strength)
    
    def is_structure_confirmed(self, df: pd.DataFrame, break_level: float) -> bool:
        """
        Check if structure break is confirmed by subsequent price action
        
        Args:
            df: Price data
            break_level: Price level of the break
            
        Returns:
            True if confirmed, False otherwise
        """
        if len(df) < 5:
            return False
        
        # Check last 5 bars for confirmation
        recent_closes = df['close'].tail(5)
        current_price = df.iloc[-1]['close']
        
        # For breaks above level, confirmation is staying above
        if current_price > break_level:
            return all(close > break_level * 0.995 for close in recent_closes)
        # For breaks below level, confirmation is staying below
        else:
            return all(close < break_level * 1.005 for close in recent_closes)
    
    def _find_swing_points(self, df: pd.DataFrame, price_type: str) -> List[SwingPoint]:
        """
        Find swing high or low points
        
        Args:
            df: Price data
            price_type: 'high' or 'low'
            
        Returns:
            List of swing points
        """
        swing_points = []
        prices = df[price_type].values
        
        for i in range(self.swing_strength, len(prices) - self.swing_strength):
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
                swing_points.append(SwingPoint(
                    index=i,
                    timestamp=df.iloc[i].name if hasattr(df.iloc[i].name, 'timestamp') else datetime.now(),
                    price=current_price,
                    swing_type=price_type,
                    strength=self.swing_strength,
                    volume=df.iloc[i]['volume'] if 'volume' in df.columns else 0
                ))
        
        return swing_points
    
    def _check_volume_confirmation(self, df: pd.DataFrame, break_index: int) -> bool:
        """
        Check if volume confirms the structure break
        
        Args:
            df: Price data with volume
            break_index: Index of the break bar
            
        Returns:
            True if volume confirms, False otherwise
        """
        if 'volume' not in df.columns or break_index < 20:
            return False
        
        try:
            # Get volume at break and average volume
            break_volume = df.iloc[break_index]['volume']
            
            # Calculate multiple volume metrics for confirmation
            lookback_period = min(20, break_index)
            recent_volumes = df['volume'].iloc[break_index-lookback_period:break_index]
            
            # 1. Average volume comparison
            avg_volume = recent_volumes.mean()
            volume_ratio = break_volume / avg_volume if avg_volume > 0 else 0
            
            # 2. Volume percentile (is this volume in top percentile?)
            volume_percentile = (recent_volumes < break_volume).sum() / len(recent_volumes)
            
            # 3. Recent volume trend (is volume increasing?)
            if len(recent_volumes) >= 5:
                recent_trend = recent_volumes.tail(5).mean() / recent_volumes.head(5).mean()
            else:
                recent_trend = 1.0
            
            # Volume confirmation criteria
            strong_volume = volume_ratio > self.volume_confirmation_threshold  # Above threshold
            high_percentile = volume_percentile > 0.8  # Top 20% of recent volumes
            increasing_trend = recent_trend > 1.1  # 10% increase in recent volume
            
            # Confirmation if any strong criteria met, or multiple moderate criteria
            if strong_volume or high_percentile:
                return True
            elif volume_ratio > 1.2 and increasing_trend:  # Moderate volume + trend
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error in volume confirmation: {e}")
            return False
    
    def _check_recent_volume_spike(self, df: pd.DataFrame) -> bool:
        """
        Check for recent volume spike in last few bars
        Enhanced version with multiple confirmation methods
        """
        if 'volume' not in df.columns or len(df) < 20:
            return False
        
        try:
            # Check last 3 bars for volume spike
            recent_volumes = df['volume'].tail(3)
            max_recent_volume = recent_volumes.max()
            
            # Compare against different baselines
            lookback_volumes = df['volume'].tail(20)
            
            # 1. Compare to average
            avg_volume = lookback_volumes.mean()
            avg_ratio = max_recent_volume / avg_volume if avg_volume > 0 else 0
            
            # 2. Compare to median (less affected by outliers)
            median_volume = lookback_volumes.median()
            median_ratio = max_recent_volume / median_volume if median_volume > 0 else 0
            
            # 3. Compare to 75th percentile
            percentile_75 = lookback_volumes.quantile(0.75)
            percentile_ratio = max_recent_volume / percentile_75 if percentile_75 > 0 else 0
            
            # Volume spike confirmation
            strong_spike = avg_ratio > self.volume_confirmation_threshold
            moderate_spike = median_ratio > 1.3 and percentile_ratio > 1.2
            
            return strong_spike or moderate_spike
            
        except Exception as e:
            self.logger.error(f"Error checking volume spike: {e}")
            return False
    
    def get_volume_confirmation_details(self, df: pd.DataFrame, break_index: int) -> Dict[str, float]:
        """
        Get detailed volume confirmation metrics for analysis
        
        Args:
            df: Price data with volume
            break_index: Index of the break bar
            
        Returns:
            Dictionary with volume metrics
        """
        if 'volume' not in df.columns or break_index < 20:
            return {}
        
        try:
            break_volume = df.iloc[break_index]['volume']
            lookback_period = min(20, break_index)
            recent_volumes = df['volume'].iloc[break_index-lookback_period:break_index]
            
            avg_volume = recent_volumes.mean()
            median_volume = recent_volumes.median()
            std_volume = recent_volumes.std()
            
            return {
                'break_volume': break_volume,
                'avg_volume': avg_volume,
                'median_volume': median_volume,
                'volume_ratio': break_volume / avg_volume if avg_volume > 0 else 0,
                'volume_percentile': (recent_volumes < break_volume).sum() / len(recent_volumes),
                'volume_z_score': (break_volume - avg_volume) / std_volume if std_volume > 0 else 0,
                'confirmation_threshold': self.volume_confirmation_threshold
            }
            
        except Exception as e:
            self.logger.error(f"Error getting volume details: {e}")
            return {}
    
    def _group_price_levels(self, swing_points: List[SwingPoint], tolerance: float) -> List[List[SwingPoint]]:
        """
        Group swing points by price level within tolerance
        
        Args:
            swing_points: List of swing points
            tolerance: Price tolerance for grouping (as percentage)
            
        Returns:
            List of grouped swing points
        """
        if not swing_points:
            return []
        
        groups = []
        used_points = set()
        
        for i, point in enumerate(swing_points):
            if i in used_points:
                continue
                
            group = [point]
            used_points.add(i)
            
            # Find other points within tolerance
            for j, other_point in enumerate(swing_points):
                if j in used_points or j == i:
                    continue
                
                price_diff = abs(point.price - other_point.price) / point.price
                if price_diff <= tolerance:
                    group.append(other_point)
                    used_points.add(j)
            
            groups.append(group)
        
        return groups
    
    def _calculate_sr_strength(self, group: List[SwingPoint], df: pd.DataFrame) -> float:
        """
        Calculate strength of support/resistance level
        
        Args:
            group: Group of swing points at similar price level
            df: Price data for volume analysis
            
        Returns:
            Strength score (0.0 to 1.0)
        """
        base_strength = 0.3
        
        # Add strength based on number of touches
        touch_bonus = min(0.4, len(group) * 0.1)  # Max 0.4 for touches
        base_strength += touch_bonus
        
        # Add strength based on time span
        if len(group) > 1:
            time_span = (max(point.timestamp for point in group) - 
                        min(point.timestamp for point in group)).total_seconds()
            days_span = time_span / (24 * 3600)  # Convert to days
            time_bonus = min(0.2, days_span / 30)  # Max 0.2 for 30+ days
            base_strength += time_bonus
        
        # Add strength based on volume at touches
        try:
            total_volume = sum(point.volume for point in group if point.volume > 0)
            if total_volume > 0:
                avg_volume = df['volume'].mean() if 'volume' in df.columns else 0
                if avg_volume > 0:
                    volume_ratio = (total_volume / len(group)) / avg_volume
                    volume_bonus = min(0.1, volume_ratio * 0.05)  # Max 0.1
                    base_strength += volume_bonus
        except:
            pass
        
        return min(1.0, base_strength)