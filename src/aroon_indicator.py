"""
Aroon Indicator Implementation for Advanced Trend Detection
Calculates Aroon Up/Down indicators for trend strength and direction analysis
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging

# Import data models from trend detection engine
from src.trend_detection_engine import AroonSignal

logger = logging.getLogger(__name__)

class AroonIndicator:
    """
    Aroon Indicator for trend strength and direction analysis
    
    The Aroon indicator consists of two lines:
    - Aroon Up: ((period - periods since highest high) / period) * 100
    - Aroon Down: ((period - periods since lowest low) / period) * 100
    
    Values range from 0 to 100:
    - Values above 70 indicate strong trend
    - Values below 30 indicate weak trend
    - Crossovers indicate potential trend changes
    """
    
    def __init__(self, period: int = 25):
        """
        Initialize the Aroon indicator
        
        Args:
            period: Calculation period (default 25)
        """
        self.period = period
        self.logger = logging.getLogger(__name__)
        
        # Validation
        if period < 1:
            raise ValueError("Aroon period must be at least 1")
        
        self.logger.info(f"AroonIndicator initialized with period={period}")
    
    def calculate_aroon(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate Aroon Up and Aroon Down indicators
        
        Args:
            df: Price data with high, low columns
            
        Returns:
            DataFrame with aroon_up, aroon_down, aroon_oscillator columns
        """
        if len(df) < self.period:
            self.logger.warning(f"Insufficient data for Aroon calculation (need {self.period}, got {len(df)})")
            return df.copy()
        
        try:
            df_copy = df.copy()
            
            # Calculate periods since highest high and lowest low
            aroon_up_values = []
            aroon_down_values = []
            
            for i in range(len(df)):
                if i < self.period - 1:
                    aroon_up_values.append(np.nan)
                    aroon_down_values.append(np.nan)
                    continue
                
                # Get the period window
                window_start = i - self.period + 1
                window_high = df['high'].iloc[window_start:i+1]
                window_low = df['low'].iloc[window_start:i+1]
                
                # Find periods since highest high and lowest low
                highest_high_idx = window_high.idxmax()
                lowest_low_idx = window_low.idxmin()
                
                # Calculate periods since (using position-based indexing)
                high_position = window_high.index.get_loc(highest_high_idx)
                low_position = window_low.index.get_loc(lowest_low_idx)
                
                periods_since_high = (self.period - 1) - high_position
                periods_since_low = (self.period - 1) - low_position
                
                # Calculate Aroon values
                aroon_up = ((self.period - periods_since_high) / self.period) * 100
                aroon_down = ((self.period - periods_since_low) / self.period) * 100
                
                aroon_up_values.append(aroon_up)
                aroon_down_values.append(aroon_down)
            
            # Add to dataframe
            df_copy['aroon_up'] = aroon_up_values
            df_copy['aroon_down'] = aroon_down_values
            df_copy['aroon_oscillator'] = df_copy['aroon_up'] - df_copy['aroon_down']
            
            self.logger.debug(f"Aroon calculation completed for {len(df)} bars")
            return df_copy
            
        except Exception as e:
            self.logger.error(f"Error calculating Aroon indicators: {e}")
            return df.copy()
    
    def get_aroon_signal(self, df: pd.DataFrame) -> Optional[AroonSignal]:
        """
        Get Aroon signal from price data with enhanced crossover detection
        
        Args:
            df: Price data (will calculate Aroon if not present)
            
        Returns:
            AroonSignal object or None if insufficient data
        """
        try:
            # Calculate Aroon if not present
            if 'aroon_up' not in df.columns or 'aroon_down' not in df.columns:
                df = self.calculate_aroon(df)
            
            if len(df) < 3:  # Need at least 3 bars for crossover detection
                return None
            
            # Get current and previous values
            current = df.iloc[-1]
            previous = df.iloc[-2]
            
            if pd.isna(current['aroon_up']) or pd.isna(current['aroon_down']):
                return None
            
            aroon_up = current['aroon_up']
            aroon_down = current['aroon_down']
            oscillator = current['aroon_oscillator']
            
            # Enhanced signal type detection
            signal_type = self._detect_aroon_signal_type(df)
            
            # Calculate enhanced trend strength
            trend_strength = self._calculate_enhanced_trend_strength(df)
            
            return AroonSignal(
                aroon_up=aroon_up,
                aroon_down=aroon_down,
                oscillator=oscillator,
                signal_type=signal_type,
                trend_strength=trend_strength
            )
            
        except Exception as e:
            self.logger.error(f"Error getting Aroon signal: {e}")
            return None
    
    def _detect_aroon_signal_type(self, df: pd.DataFrame) -> str:
        """
        Enhanced Aroon signal type detection with crossover analysis
        
        Args:
            df: DataFrame with Aroon indicators
            
        Returns:
            Signal type string
        """
        if len(df) < 3:
            return 'insufficient_data'
        
        current = df.iloc[-1]
        previous = df.iloc[-2]
        prev_prev = df.iloc[-3] if len(df) >= 3 else previous
        
        aroon_up = current['aroon_up']
        aroon_down = current['aroon_down']
        prev_up = previous['aroon_up']
        prev_down = previous['aroon_down']
        
        # 1. Check for crossovers (most important signals)
        if prev_up <= prev_down and aroon_up > aroon_down:
            # Bullish crossover - Aroon Up crosses above Aroon Down
            crossover_strength = self._calculate_crossover_strength(df, 'bullish')
            if crossover_strength > 0.7:
                return 'strong_bullish_cross'
            else:
                return 'bullish_cross'
                
        elif prev_up >= prev_down and aroon_up < aroon_down:
            # Bearish crossover - Aroon Down crosses above Aroon Up
            crossover_strength = self._calculate_crossover_strength(df, 'bearish')
            if crossover_strength > 0.7:
                return 'strong_bearish_cross'
            else:
                return 'bearish_cross'
        
        # 2. Check for strong trend conditions (no crossover but strong signals)
        elif aroon_up > 70 and aroon_down < 30:
            # Strong uptrend
            if aroon_up > 85:
                return 'very_strong_bullish'
            else:
                return 'strong_bullish'
                
        elif aroon_down > 70 and aroon_up < 30:
            # Strong downtrend
            if aroon_down > 85:
                return 'very_strong_bearish'
            else:
                return 'strong_bearish'
        
        # 3. Check for consolidation patterns
        elif aroon_up < 50 and aroon_down < 50:
            # Both indicators low - consolidation
            if max(aroon_up, aroon_down) < 30:
                return 'tight_consolidation'
            else:
                return 'consolidation'
        
        # 4. Check for trend weakening
        elif self._is_trend_weakening(df):
            if aroon_up > aroon_down:
                return 'weakening_bullish'
            else:
                return 'weakening_bearish'
        
        # 5. Default to current trend direction
        else:
            if aroon_up > aroon_down:
                return 'moderate_bullish'
            else:
                return 'moderate_bearish'
    
    def _calculate_crossover_strength(self, df: pd.DataFrame, crossover_type: str) -> float:
        """
        Calculate the strength of an Aroon crossover
        
        Args:
            df: DataFrame with Aroon indicators
            crossover_type: 'bullish' or 'bearish'
            
        Returns:
            Crossover strength (0.0 to 1.0)
        """
        if len(df) < 5:
            return 0.5
        
        current = df.iloc[-1]
        aroon_up = current['aroon_up']
        aroon_down = current['aroon_down']
        
        strength = 0.5  # Base strength
        
        # 1. Separation strength - how far apart are the indicators?
        separation = abs(aroon_up - aroon_down)
        strength += min(0.3, separation / 100)  # Max 0.3 bonus
        
        # 2. Absolute level strength - are we crossing at high levels?
        if crossover_type == 'bullish':
            level_strength = aroon_up / 100
        else:
            level_strength = aroon_down / 100
        strength += level_strength * 0.2  # Max 0.2 bonus
        
        # 3. Momentum strength - how fast is the crossover happening?
        if len(df) >= 5:
            recent_aroon = df[['aroon_up', 'aroon_down']].tail(5)
            if crossover_type == 'bullish':
                momentum = (recent_aroon['aroon_up'].iloc[-1] - recent_aroon['aroon_up'].iloc[0]) / 5
            else:
                momentum = (recent_aroon['aroon_down'].iloc[-1] - recent_aroon['aroon_down'].iloc[0]) / 5
            
            momentum_bonus = min(0.2, abs(momentum) / 20)  # Max 0.2 bonus
            strength += momentum_bonus
        
        return min(1.0, strength)
    
    def _calculate_enhanced_trend_strength(self, df: pd.DataFrame) -> float:
        """
        Calculate enhanced trend strength using multiple factors
        
        Args:
            df: DataFrame with Aroon indicators
            
        Returns:
            Enhanced trend strength (0.0 to 1.0)
        """
        if len(df) < 5:
            return self.calculate_trend_strength(df.iloc[-1]['aroon_up'], df.iloc[-1]['aroon_down'])
        
        current = df.iloc[-1]
        aroon_up = current['aroon_up']
        aroon_down = current['aroon_down']
        
        # 1. Basic separation strength
        separation = abs(aroon_up - aroon_down)
        max_value = max(aroon_up, aroon_down)
        base_strength = (separation / 100) * (max_value / 100)
        
        # 2. Consistency strength - how consistent is the trend over time?
        recent_aroon = df[['aroon_up', 'aroon_down']].tail(5)
        if aroon_up > aroon_down:
            # Bullish trend - check consistency of Aroon Up being higher
            consistency = (recent_aroon['aroon_up'] > recent_aroon['aroon_down']).sum() / 5
        else:
            # Bearish trend - check consistency of Aroon Down being higher
            consistency = (recent_aroon['aroon_down'] > recent_aroon['aroon_up']).sum() / 5
        
        consistency_bonus = consistency * 0.3  # Max 0.3 bonus
        
        # 3. Momentum strength - is the trend accelerating?
        if aroon_up > aroon_down:
            momentum = (recent_aroon['aroon_up'].iloc[-1] - recent_aroon['aroon_up'].iloc[0]) / 5
        else:
            momentum = (recent_aroon['aroon_down'].iloc[-1] - recent_aroon['aroon_down'].iloc[0]) / 5
        
        momentum_bonus = min(0.2, abs(momentum) / 20)  # Max 0.2 bonus
        
        # 4. Extreme level bonus - very high values get extra strength
        if max_value > 80:
            extreme_bonus = (max_value - 80) / 100  # Max 0.2 bonus
        else:
            extreme_bonus = 0
        
        total_strength = base_strength + consistency_bonus + momentum_bonus + extreme_bonus
        return min(1.0, total_strength)
    
    def _is_trend_weakening(self, df: pd.DataFrame) -> bool:
        """
        Check if the current trend is weakening
        
        Args:
            df: DataFrame with Aroon indicators
            
        Returns:
            True if trend is weakening
        """
        if len(df) < 5:
            return False
        
        recent_aroon = df[['aroon_up', 'aroon_down']].tail(5)
        current = df.iloc[-1]
        
        # Check if the dominant indicator is declining
        if current['aroon_up'] > current['aroon_down']:
            # In bullish trend - check if Aroon Up is declining
            aroon_up_trend = recent_aroon['aroon_up'].iloc[-1] - recent_aroon['aroon_up'].iloc[0]
            return aroon_up_trend < -10  # Declining by more than 10 points
        else:
            # In bearish trend - check if Aroon Down is declining
            aroon_down_trend = recent_aroon['aroon_down'].iloc[-1] - recent_aroon['aroon_down'].iloc[0]
            return aroon_down_trend < -10  # Declining by more than 10 points
    
    def calculate_trend_strength(self, aroon_up: float, aroon_down: float) -> float:
        """
        Calculate trend strength based on Aroon values
        
        Args:
            aroon_up: Aroon Up value
            aroon_down: Aroon Down value
            
        Returns:
            Trend strength (0.0 to 1.0)
        """
        # Trend strength based on separation and absolute values
        separation = abs(aroon_up - aroon_down)
        max_value = max(aroon_up, aroon_down)
        
        # Strong trend when values are separated and at least one is high
        strength = (separation / 100) * (max_value / 100)
        
        return min(1.0, strength)
    
    def is_consolidation(self, aroon_up: float, aroon_down: float) -> bool:
        """
        Determine if market is in consolidation based on Aroon values
        
        Args:
            aroon_up: Aroon Up value
            aroon_down: Aroon Down value
            
        Returns:
            True if consolidating, False otherwise
        """
        return aroon_up < 50 and aroon_down < 50
    
    def get_consolidation_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get detailed consolidation analysis
        
        Args:
            df: DataFrame with Aroon indicators
            
        Returns:
            Dictionary with consolidation details
        """
        if 'aroon_up' not in df.columns or 'aroon_down' not in df.columns:
            df = self.calculate_aroon(df)
        
        if len(df) < 10:
            return {'consolidation': False, 'reason': 'insufficient_data'}
        
        recent_data = df.tail(10)
        current = df.iloc[-1]
        
        aroon_up = current['aroon_up']
        aroon_down = current['aroon_down']
        
        # Basic consolidation check
        is_consolidating = self.is_consolidation(aroon_up, aroon_down)
        
        if not is_consolidating:
            return {
                'consolidation': False,
                'reason': 'trending',
                'aroon_up': aroon_up,
                'aroon_down': aroon_down
            }
        
        # Detailed consolidation analysis
        consolidation_strength = self._calculate_consolidation_strength(recent_data)
        consolidation_duration = self._estimate_consolidation_duration(df)
        breakout_probability = self._calculate_breakout_probability(recent_data)
        
        # Determine consolidation type
        if max(aroon_up, aroon_down) < 30:
            consolidation_type = 'tight'
        elif max(aroon_up, aroon_down) < 40:
            consolidation_type = 'moderate'
        else:
            consolidation_type = 'loose'
        
        return {
            'consolidation': True,
            'type': consolidation_type,
            'strength': consolidation_strength,
            'duration_bars': consolidation_duration,
            'breakout_probability': breakout_probability,
            'aroon_up': aroon_up,
            'aroon_down': aroon_down,
            'max_aroon': max(aroon_up, aroon_down),
            'aroon_range': abs(aroon_up - aroon_down)
        }
    
    def _calculate_consolidation_strength(self, df: pd.DataFrame) -> float:
        """
        Calculate how strong the consolidation is
        
        Args:
            df: Recent DataFrame with Aroon indicators
            
        Returns:
            Consolidation strength (0.0 to 1.0, higher = stronger consolidation)
        """
        aroon_up_values = df['aroon_up'].values
        aroon_down_values = df['aroon_down'].values
        
        # 1. How consistently low are both indicators?
        low_threshold = 50
        up_below_threshold = (aroon_up_values < low_threshold).sum() / len(aroon_up_values)
        down_below_threshold = (aroon_down_values < low_threshold).sum() / len(aroon_down_values)
        consistency = (up_below_threshold + down_below_threshold) / 2
        
        # 2. How low are the average values?
        avg_up = aroon_up_values.mean()
        avg_down = aroon_down_values.mean()
        avg_level = (avg_up + avg_down) / 2
        level_strength = max(0, (50 - avg_level) / 50)  # Stronger when lower
        
        # 3. How stable are the values (low volatility)?
        up_volatility = aroon_up_values.std()
        down_volatility = aroon_down_values.std()
        avg_volatility = (up_volatility + down_volatility) / 2
        stability = max(0, (20 - avg_volatility) / 20)  # Stronger when more stable
        
        # Combine factors
        strength = (consistency * 0.5) + (level_strength * 0.3) + (stability * 0.2)
        return min(1.0, strength)
    
    def _estimate_consolidation_duration(self, df: pd.DataFrame) -> int:
        """
        Estimate how long the consolidation has been going on
        
        Args:
            df: DataFrame with Aroon indicators
            
        Returns:
            Number of bars in consolidation
        """
        if len(df) < 5:
            return 0
        
        duration = 0
        # Look backwards to find when consolidation started
        for i in range(len(df) - 1, -1, -1):
            aroon_up = df.iloc[i]['aroon_up']
            aroon_down = df.iloc[i]['aroon_down']
            
            if self.is_consolidation(aroon_up, aroon_down):
                duration += 1
            else:
                break
        
        return duration
    
    def _calculate_breakout_probability(self, df: pd.DataFrame) -> float:
        """
        Calculate probability of breakout from consolidation
        
        Args:
            df: Recent DataFrame with Aroon indicators
            
        Returns:
            Breakout probability (0.0 to 1.0)
        """
        if len(df) < 5:
            return 0.5
        
        # Look for signs of building momentum
        recent_up = df['aroon_up'].tail(3).mean()
        recent_down = df['aroon_down'].tail(3).mean()
        earlier_up = df['aroon_up'].head(3).mean()
        earlier_down = df['aroon_down'].head(3).mean()
        
        # Check if either indicator is starting to rise
        up_momentum = recent_up - earlier_up
        down_momentum = recent_down - earlier_down
        
        # Higher momentum suggests higher breakout probability
        max_momentum = max(up_momentum, down_momentum)
        
        # Base probability
        base_prob = 0.3
        
        # Add momentum factor
        momentum_factor = min(0.4, max_momentum / 20)  # Max 0.4 bonus
        
        # Add duration factor (longer consolidation = higher breakout probability)
        duration = len(df)
        duration_factor = min(0.3, duration / 20)  # Max 0.3 bonus
        
        total_prob = base_prob + momentum_factor + duration_factor
        return min(1.0, total_prob)
