"""
Divergence Detector for Advanced Trend Detection
Implements divergence detection between price and momentum indicators (RSI, MACD)
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
import logging

# Import data models from trend detection engine
from src.trend_detection_engine import DivergenceResult, DivergenceType

logger = logging.getLogger(__name__)

@dataclass
class SwingPoint:
    """Represents a swing high or low point for divergence analysis"""
    index: int
    timestamp: datetime
    price: float
    indicator_value: float
    swing_type: str  # 'high' or 'low'
    strength: int    # Number of bars on each side

@dataclass
class DivergencePattern:
    """Represents a complete divergence pattern"""
    divergence_type: str
    indicator: str
    price_swing1: SwingPoint
    price_swing2: SwingPoint
    indicator_swing1: SwingPoint
    indicator_swing2: SwingPoint
    strength: float
    confidence: float
    validated: bool

class DivergenceDetector:
    """
    Detects divergences between price and momentum indicators
    
    Implements:
    - Swing point identification for price and indicators
    - RSI divergence detection (bullish and bearish)
    - MACD divergence detection (bullish and bearish)
    - Multi-swing validation to reduce false signals
    - Confidence scoring based on divergence clarity
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the divergence detector
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Configuration parameters
        self.swing_strength = config.get('divergence_swing_strength', 5)  # Bars on each side for swing detection
        self.min_swing_separation = config.get('min_swing_separation', 10)  # Minimum bars between swings
        self.divergence_threshold = config.get('divergence_threshold', 0.001)  # Minimum divergence magnitude
        self.validation_swings = config.get('validation_swings', 2)  # Number of swings to validate
        
        # RSI parameters
        self.rsi_period = config.get('rsi_period', 14)
        self.rsi_overbought = config.get('rsi_overbought', 70)
        self.rsi_oversold = config.get('rsi_oversold', 30)
        
        # MACD parameters
        self.macd_fast = config.get('macd_fast', 12)
        self.macd_slow = config.get('macd_slow', 26)
        self.macd_signal = config.get('macd_signal', 9)
        
        self.logger.info(f"DivergenceDetector initialized with swing_strength={self.swing_strength}")
    
    def detect_rsi_divergence(self, df: pd.DataFrame) -> DivergenceResult:
        """
        Detect RSI divergences between price and RSI indicator
        
        Args:
            df: Price data with RSI indicator
            
        Returns:
            DivergenceResult with RSI divergence information
        """
        if len(df) < self.swing_strength * 4:  # Need enough data for swing detection
            return None
        
        try:
            # Calculate RSI if not present
            if 'rsi' not in df.columns:
                df = self._calculate_rsi(df)
            
            # Find swing points for both price and RSI
            price_highs = self._find_swing_points(df, 'high', 'high')
            price_lows = self._find_swing_points(df, 'low', 'low')
            rsi_highs = self._find_swing_points(df, 'rsi', 'high')
            rsi_lows = self._find_swing_points(df, 'rsi', 'low')
            
            # Detect bearish divergence (higher high price, lower high RSI)
            bearish_divergence = self._detect_bearish_divergence(
                price_highs, rsi_highs, df, 'RSI'
            )
            
            # Detect bullish divergence (lower low price, higher low RSI)
            bullish_divergence = self._detect_bullish_divergence(
                price_lows, rsi_lows, df, 'RSI'
            )
            
            # Return the strongest divergence found
            if bearish_divergence and bullish_divergence:
                # Return the one with higher confidence
                if bearish_divergence.strength > bullish_divergence.strength:
                    return bearish_divergence
                else:
                    return bullish_divergence
            elif bearish_divergence:
                return bearish_divergence
            elif bullish_divergence:
                return bullish_divergence
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error in RSI divergence detection: {e}")
            return None
    
    def detect_macd_divergence(self, df: pd.DataFrame) -> DivergenceResult:
        """
        Detect MACD divergences between price and MACD indicator
        
        Args:
            df: Price data with MACD indicator
            
        Returns:
            DivergenceResult with MACD divergence information
        """
        if len(df) < self.swing_strength * 4:  # Need enough data for swing detection
            return None
        
        try:
            # Calculate MACD if not present
            if 'macd' not in df.columns or 'macd_histogram' not in df.columns:
                df = self._calculate_macd(df)
            
            # Use MACD histogram for divergence detection (more sensitive)
            # Find swing points for both price and MACD histogram
            price_highs = self._find_swing_points(df, 'high', 'high')
            price_lows = self._find_swing_points(df, 'low', 'low')
            macd_highs = self._find_swing_points(df, 'macd_histogram', 'high')
            macd_lows = self._find_swing_points(df, 'macd_histogram', 'low')
            
            # Detect bearish divergence (higher high price, lower high MACD)
            bearish_divergence = self._detect_bearish_divergence(
                price_highs, macd_highs, df, 'MACD'
            )
            
            # Detect bullish divergence (lower low price, higher low MACD)
            bullish_divergence = self._detect_bullish_divergence(
                price_lows, macd_lows, df, 'MACD'
            )
            
            # Return the strongest divergence found
            if bearish_divergence and bullish_divergence:
                # Return the one with higher confidence
                if bearish_divergence.strength > bullish_divergence.strength:
                    return bearish_divergence
                else:
                    return bullish_divergence
            elif bearish_divergence:
                return bearish_divergence
            elif bullish_divergence:
                return bullish_divergence
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error in MACD divergence detection: {e}")
            return None
    
    def validate_divergence(self, divergence: DivergenceResult) -> bool:
        """
        Validate divergence using multiple criteria
        
        Args:
            divergence: DivergenceResult to validate
            
        Returns:
            True if divergence is valid, False otherwise
        """
        if not divergence:
            return False
        
        try:
            # 1. Check if divergence strength meets minimum threshold (lowered)
            if divergence.strength < 0.1:  # Lowered from 0.2
                return False
            
            # 2. Check if we have enough swing points for validation
            if len(divergence.price_points) < 2 or len(divergence.indicator_points) < 2:
                return False
            
            # 3. Check divergence magnitude (lowered thresholds)
            price_change = abs(divergence.price_points[-1][1] - divergence.price_points[0][1]) / divergence.price_points[0][1]
            indicator_change = abs(divergence.indicator_points[-1][1] - divergence.indicator_points[0][1])
            
            # For RSI, normalize to 0-100 scale
            if divergence.indicator == 'RSI':
                indicator_change = indicator_change / 100
            elif divergence.indicator == 'MACD':
                # For MACD, use relative change
                base_value = abs(divergence.indicator_points[0][1]) + 0.0001
                indicator_change = indicator_change / base_value
            
            # Divergence should have meaningful magnitude (lowered threshold significantly)
            if price_change < 0.002 or indicator_change < 0.002:  # 0.2% threshold (was 0.5%)
                return False
            
            # 4. Check divergence direction consistency
            price_direction = 1 if divergence.price_points[-1][1] > divergence.price_points[0][1] else -1
            indicator_direction = 1 if divergence.indicator_points[-1][1] > divergence.indicator_points[0][1] else -1
            
            # For valid divergence, directions should be opposite
            if price_direction == indicator_direction:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating divergence: {e}")
            return False
    
    def calculate_divergence_strength(self, divergence: DivergenceResult) -> float:
        """
        Calculate the strength of a divergence pattern
        
        Args:
            divergence: DivergenceResult to analyze
            
        Returns:
            Strength score (0.0 to 1.0)
        """
        if not divergence or len(divergence.price_points) < 2 or len(divergence.indicator_points) < 2:
            return 0.0
        
        try:
            strength = 0.0
            
            # 1. Magnitude factor (larger divergences are stronger)
            price_change = abs(divergence.price_points[-1][1] - divergence.price_points[0][1]) / divergence.price_points[0][1]
            indicator_change = abs(divergence.indicator_points[-1][1] - divergence.indicator_points[0][1])
            
            # Normalize indicator change
            if divergence.indicator == 'RSI':
                indicator_change = indicator_change / 100
            elif divergence.indicator == 'MACD':
                # MACD values can vary widely, use relative change
                base_value = abs(divergence.indicator_points[0][1]) + 0.0001  # Avoid division by zero
                indicator_change = indicator_change / base_value
            
            magnitude_factor = min(1.0, (price_change + indicator_change) / 0.04)  # Normalize to 4% total change
            strength += magnitude_factor * 0.4
            
            # 2. Time span factor (longer divergences are more reliable)
            time_span = abs((divergence.price_points[-1][0] - divergence.price_points[0][0]).total_seconds())
            days_span = time_span / (24 * 3600)
            time_factor = min(1.0, days_span / 7)  # Normalize to 1 week
            strength += time_factor * 0.2
            
            # 3. Swing point quality factor
            # More swing points in the pattern increase reliability
            swing_count = len(divergence.price_points)
            swing_factor = min(1.0, swing_count / 4)  # Normalize to 4 swings
            strength += swing_factor * 0.2
            
            # 4. Indicator extreme levels factor (divergences at extremes are stronger)
            extreme_factor = 0.0
            if divergence.indicator == 'RSI':
                for _, rsi_value in divergence.indicator_points:
                    if rsi_value > self.rsi_overbought or rsi_value < self.rsi_oversold:
                        extreme_factor += 0.1
                extreme_factor = min(1.0, extreme_factor)
            elif divergence.indicator == 'MACD':
                # For MACD, check if values are at recent extremes
                extreme_factor = 0.5  # Default moderate factor for MACD
            
            strength += extreme_factor * 0.2
            
            return min(1.0, strength)
            
        except Exception as e:
            self.logger.error(f"Error calculating divergence strength: {e}")
            return 0.0
    
    def _detect_bearish_divergence(self, price_highs: List[SwingPoint], 
                                  indicator_highs: List[SwingPoint], 
                                  df: pd.DataFrame, indicator_name: str) -> Optional[DivergenceResult]:
        """
        Detect bearish divergence (higher high price, lower high indicator)
        
        Args:
            price_highs: List of price swing highs
            indicator_highs: List of indicator swing highs
            df: Price data
            indicator_name: Name of the indicator ('RSI' or 'MACD')
            
        Returns:
            DivergenceResult if bearish divergence found, None otherwise
        """
        if len(price_highs) < 2 or len(indicator_highs) < 2:
            return None
        
        try:
            # Look for divergence patterns in recent swings
            # Try different combinations of recent highs
            for i in range(max(0, len(price_highs) - 4), len(price_highs) - 1):
                for j in range(i + 1, len(price_highs)):
                    price_swing1 = price_highs[i]
                    price_swing2 = price_highs[j]
                    
                    # Find corresponding indicator swings
                    indicator_swing1 = self._find_closest_indicator_swing(price_swing1, indicator_highs)
                    indicator_swing2 = self._find_closest_indicator_swing(price_swing2, indicator_highs)
                    
                    if not indicator_swing1 or not indicator_swing2:
                        continue
                    
                    # Check for bearish divergence pattern
                    price_higher = price_swing2.price > price_swing1.price
                    indicator_lower = indicator_swing2.indicator_value < indicator_swing1.indicator_value
                    
                    # Ensure minimum separation
                    index_separation = abs(price_swing2.index - price_swing1.index)
                    if index_separation < self.min_swing_separation:
                        continue
                    
                    if price_higher and indicator_lower:
                        # Check if divergence is significant enough
                        price_change = (price_swing2.price - price_swing1.price) / price_swing1.price
                        indicator_change = abs(indicator_swing2.indicator_value - indicator_swing1.indicator_value)
                        
                        if indicator_name == 'RSI':
                            indicator_change = indicator_change / 100  # Normalize RSI
                        
                        if price_change > self.divergence_threshold and indicator_change > self.divergence_threshold:
                            # Create divergence result
                            divergence_type = DivergenceType.BEARISH_RSI.value if indicator_name == 'RSI' else DivergenceType.BEARISH_MACD.value
                            
                            price_points = [
                                (price_swing1.timestamp, price_swing1.price),
                                (price_swing2.timestamp, price_swing2.price)
                            ]
                            
                            indicator_points = [
                                (indicator_swing1.timestamp, indicator_swing1.indicator_value),
                                (indicator_swing2.timestamp, indicator_swing2.indicator_value)
                            ]
                            
                            divergence = DivergenceResult(
                                divergence_type=divergence_type,
                                indicator=indicator_name,
                                price_points=price_points,
                                indicator_points=indicator_points,
                                strength=0.0,  # Will be calculated
                                validated=False  # Will be validated
                            )
                            
                            # Calculate strength and validate
                            divergence.strength = self.calculate_divergence_strength(divergence)
                            divergence.validated = self.validate_divergence(divergence)
                            
                            if divergence.validated:
                                return divergence
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error detecting bearish divergence: {e}")
            return None
    
    def _detect_bullish_divergence(self, price_lows: List[SwingPoint], 
                                  indicator_lows: List[SwingPoint], 
                                  df: pd.DataFrame, indicator_name: str) -> Optional[DivergenceResult]:
        """
        Detect bullish divergence (lower low price, higher low indicator)
        
        Args:
            price_lows: List of price swing lows
            indicator_lows: List of indicator swing lows
            df: Price data
            indicator_name: Name of the indicator ('RSI' or 'MACD')
            
        Returns:
            DivergenceResult if bullish divergence found, None otherwise
        """
        if len(price_lows) < 2 or len(indicator_lows) < 2:
            return None
        
        try:
            # Look for divergence patterns in recent swings
            # Try different combinations of recent lows
            for i in range(max(0, len(price_lows) - 4), len(price_lows) - 1):
                for j in range(i + 1, len(price_lows)):
                    price_swing1 = price_lows[i]
                    price_swing2 = price_lows[j]
                    
                    # Find corresponding indicator swings
                    indicator_swing1 = self._find_closest_indicator_swing(price_swing1, indicator_lows)
                    indicator_swing2 = self._find_closest_indicator_swing(price_swing2, indicator_lows)
                    
                    if not indicator_swing1 or not indicator_swing2:
                        continue
                    
                    # Check for bullish divergence pattern
                    price_lower = price_swing2.price < price_swing1.price
                    indicator_higher = indicator_swing2.indicator_value > indicator_swing1.indicator_value
                    
                    # Ensure minimum separation
                    index_separation = abs(price_swing2.index - price_swing1.index)
                    if index_separation < self.min_swing_separation:
                        continue
                    
                    if price_lower and indicator_higher:
                        # Check if divergence is significant enough
                        price_change = abs(price_swing2.price - price_swing1.price) / price_swing1.price
                        indicator_change = abs(indicator_swing2.indicator_value - indicator_swing1.indicator_value)
                        
                        if indicator_name == 'RSI':
                            indicator_change = indicator_change / 100  # Normalize RSI
                        
                        if price_change > self.divergence_threshold and indicator_change > self.divergence_threshold:
                            # Create divergence result
                            divergence_type = DivergenceType.BULLISH_RSI.value if indicator_name == 'RSI' else DivergenceType.BULLISH_MACD.value
                            
                            price_points = [
                                (price_swing1.timestamp, price_swing1.price),
                                (price_swing2.timestamp, price_swing2.price)
                            ]
                            
                            indicator_points = [
                                (indicator_swing1.timestamp, indicator_swing1.indicator_value),
                                (indicator_swing2.timestamp, indicator_swing2.indicator_value)
                            ]
                            
                            divergence = DivergenceResult(
                                divergence_type=divergence_type,
                                indicator=indicator_name,
                                price_points=price_points,
                                indicator_points=indicator_points,
                                strength=0.0,  # Will be calculated
                                validated=False  # Will be validated
                            )
                            
                            # Calculate strength and validate
                            divergence.strength = self.calculate_divergence_strength(divergence)
                            divergence.validated = self.validate_divergence(divergence)
                            
                            if divergence.validated:
                                return divergence
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error detecting bullish divergence: {e}")
            return None
    
    def _find_swing_points(self, df: pd.DataFrame, column: str, swing_type: str) -> List[SwingPoint]:
        """
        Find swing high or low points in a data series
        
        Args:
            df: DataFrame with price/indicator data
            column: Column name to analyze
            swing_type: 'high' or 'low'
            
        Returns:
            List of swing points
        """
        swing_points = []
        
        if column not in df.columns or len(df) < self.swing_strength * 2 + 1:
            return swing_points
        
        try:
            values = df[column].values
            
            for i in range(self.swing_strength, len(values) - self.swing_strength):
                is_swing = True
                current_value = values[i]
                
                if pd.isna(current_value):
                    continue
                
                # Check if current point is higher/lower than surrounding points
                for j in range(i - self.swing_strength, i + self.swing_strength + 1):
                    if j == i:
                        continue
                    
                    if pd.isna(values[j]):
                        continue
                    
                    if swing_type == 'high':
                        if values[j] >= current_value:
                            is_swing = False
                            break
                    else:  # low
                        if values[j] <= current_value:
                            is_swing = False
                            break
                
                if is_swing:
                    # Get corresponding indicator value for divergence analysis
                    if column in ['high', 'low']:
                        # For price swings, we need the corresponding indicator value
                        indicator_value = current_value  # Will be updated when matching
                    else:
                        # For indicator swings, the value is the indicator itself
                        indicator_value = current_value
                    
                    swing_points.append(SwingPoint(
                        index=i,
                        timestamp=df.index[i] if hasattr(df.index[i], 'timestamp') else datetime.now(),
                        price=current_value,
                        indicator_value=indicator_value,
                        swing_type=swing_type,
                        strength=self.swing_strength
                    ))
            
            return swing_points
            
        except Exception as e:
            self.logger.error(f"Error finding swing points for {column}: {e}")
            return []
    
    def _match_swing_points(self, price_swings: List[SwingPoint], 
                           indicator_swings: List[SwingPoint]) -> List[Tuple[SwingPoint, SwingPoint]]:
        """
        Match price swing points with corresponding indicator swing points
        
        Args:
            price_swings: List of price swing points
            indicator_swings: List of indicator swing points
            
        Returns:
            List of matched swing point pairs
        """
        matched_pairs = []
        max_index_diff = self.min_swing_separation  # Use index difference instead of time
        
        try:
            used_indicator_swings = set()
            
            for price_swing in price_swings:
                best_match = None
                min_index_diff = float('inf')
                
                for i, indicator_swing in enumerate(indicator_swings):
                    if i in used_indicator_swings:
                        continue
                    
                    # Calculate index difference between swings
                    index_diff = abs(price_swing.index - indicator_swing.index)
                    
                    # Find the closest indicator swing within the index window
                    if index_diff <= max_index_diff and index_diff < min_index_diff:
                        min_index_diff = index_diff
                        best_match = (i, indicator_swing)
                
                if best_match:
                    idx, indicator_swing = best_match
                    used_indicator_swings.add(idx)
                    
                    # Update the indicator value in the price swing for consistency
                    price_swing.indicator_value = indicator_swing.indicator_value
                    matched_pairs.append((price_swing, indicator_swing))
            
            # Sort by index to maintain chronological order
            matched_pairs.sort(key=lambda x: x[0].index)
            
            return matched_pairs
            
        except Exception as e:
            self.logger.error(f"Error matching swing points: {e}")
            return []
    
    def _calculate_rsi(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate RSI indicator if not present
        
        Args:
            df: Price data
            
        Returns:
            DataFrame with RSI column added
        """
        try:
            df_copy = df.copy()
            
            # Calculate price changes
            delta = df_copy['close'].diff()
            
            # Separate gains and losses
            gains = delta.where(delta > 0, 0)
            losses = -delta.where(delta < 0, 0)
            
            # Calculate average gains and losses
            avg_gains = gains.rolling(window=self.rsi_period, min_periods=1).mean()
            avg_losses = losses.rolling(window=self.rsi_period, min_periods=1).mean()
            
            # Calculate RSI
            rs = avg_gains / avg_losses
            rsi = 100 - (100 / (1 + rs))
            
            df_copy['rsi'] = rsi
            
            return df_copy
            
        except Exception as e:
            self.logger.error(f"Error calculating RSI: {e}")
            return df.copy()
    
    def _calculate_macd(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate MACD indicator if not present
        
        Args:
            df: Price data
            
        Returns:
            DataFrame with MACD columns added
        """
        try:
            df_copy = df.copy()
            
            # Calculate EMAs
            ema_fast = df_copy['close'].ewm(span=self.macd_fast).mean()
            ema_slow = df_copy['close'].ewm(span=self.macd_slow).mean()
            
            # Calculate MACD line
            macd_line = ema_fast - ema_slow
            
            # Calculate signal line
            signal_line = macd_line.ewm(span=self.macd_signal).mean()
            
            # Calculate histogram
            histogram = macd_line - signal_line
            
            df_copy['macd'] = macd_line
            df_copy['macd_signal'] = signal_line
            df_copy['macd_histogram'] = histogram
            
            return df_copy
            
        except Exception as e:
            self.logger.error(f"Error calculating MACD: {e}")
            return df.copy()
    
    def _find_closest_indicator_swing(self, price_swing: SwingPoint, 
                                     indicator_swings: List[SwingPoint]) -> Optional[SwingPoint]:
        """
        Find the closest indicator swing to a price swing
        
        Args:
            price_swing: Price swing point to match
            indicator_swings: List of indicator swing points
            
        Returns:
            Closest indicator swing or None
        """
        if not indicator_swings:
            return None
        
        best_match = None
        min_index_diff = float('inf')
        max_index_diff = self.min_swing_separation * 2  # Allow some flexibility
        
        for indicator_swing in indicator_swings:
            index_diff = abs(price_swing.index - indicator_swing.index)
            
            if index_diff <= max_index_diff and index_diff < min_index_diff:
                min_index_diff = index_diff
                best_match = indicator_swing
        
        return best_match
    
    def get_divergence_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get comprehensive divergence analysis for both RSI and MACD
        
        Args:
            df: Price data with indicators
            
        Returns:
            Dictionary with divergence analysis results
        """
        try:
            analysis = {
                'rsi_divergence': None,
                'macd_divergence': None,
                'has_divergence': False,
                'strongest_divergence': None,
                'divergence_count': 0,
                'analysis_timestamp': datetime.now()
            }
            
            # Detect RSI divergence
            rsi_divergence = self.detect_rsi_divergence(df)
            if rsi_divergence and rsi_divergence.validated:
                analysis['rsi_divergence'] = {
                    'type': rsi_divergence.divergence_type,
                    'strength': rsi_divergence.strength,
                    'validated': rsi_divergence.validated,
                    'price_points': rsi_divergence.price_points,
                    'indicator_points': rsi_divergence.indicator_points
                }
                analysis['divergence_count'] += 1
            
            # Detect MACD divergence
            macd_divergence = self.detect_macd_divergence(df)
            if macd_divergence and macd_divergence.validated:
                analysis['macd_divergence'] = {
                    'type': macd_divergence.divergence_type,
                    'strength': macd_divergence.strength,
                    'validated': macd_divergence.validated,
                    'price_points': macd_divergence.price_points,
                    'indicator_points': macd_divergence.indicator_points
                }
                analysis['divergence_count'] += 1
            
            # Determine if we have any divergences
            analysis['has_divergence'] = analysis['divergence_count'] > 0
            
            # Find the strongest divergence
            if rsi_divergence and macd_divergence:
                if rsi_divergence.strength > macd_divergence.strength:
                    analysis['strongest_divergence'] = analysis['rsi_divergence']
                else:
                    analysis['strongest_divergence'] = analysis['macd_divergence']
            elif rsi_divergence:
                analysis['strongest_divergence'] = analysis['rsi_divergence']
            elif macd_divergence:
                analysis['strongest_divergence'] = analysis['macd_divergence']
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error in divergence analysis: {e}")
            return {
                'error': str(e),
                'has_divergence': False,
                'divergence_count': 0
            }