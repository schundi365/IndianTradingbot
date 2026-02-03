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
        
        # Validation
        if self.fast_period >= self.slow_period:
            raise ValueError("Fast EMA period must be less than slow EMA period")
        
        self.logger.info(f"EMAMomentumAnalyzer initialized with periods {self.fast_period}/{self.slow_period}")
    
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
        
        # 2. Slope alignment strength (both slopes in same direction = stronger)
        if slope_fast * slope_slow > 0:  # Same sign
            slope_alignment = 1.0
        else:
            slope_alignment = 0.5
        
        # 3. Slope magnitude strength
        avg_slope = (abs(slope_fast) + abs(slope_slow)) / 2
        slope_strength = min(1.0, avg_slope / 0.01)  # Normalize to 1% max slope
        
        # 4. Consistency strength (how consistent is the trend over time?)
        recent_separations = df['ema_separation'].tail(5)
        if len(recent_separations) >= 5:
            consistency = 1.0 - (recent_separations.std() / (abs(recent_separations.mean()) + 0.001))
            consistency = max(0.0, min(1.0, consistency))
        else:
            consistency = 0.5
        
        # Combine factors
        total_strength = (
            separation_strength * 0.4 +
            slope_alignment * 0.2 +
            slope_strength * 0.2 +
            consistency * 0.2
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
    
    def get_ema_analysis_details(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get detailed EMA analysis information
        
        Args:
            df: DataFrame with EMA data
            
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
        
        return {
            'fast_ema': current[f'ema_{self.fast_period}'],
            'slow_ema': current[f'ema_{self.slow_period}'],
            'separation_pct': current['ema_separation'],
            'fast_slope': current['ema_fast_slope'],
            'slow_slope': current['ema_slow_slope'],
            'signal': signal,
            'support_resistance_levels': sr_levels,
            'trend_direction': 'bullish' if current[f'ema_{self.fast_period}'] > current[f'ema_{self.slow_period}'] else 'bearish',
            'trend_strength': signal.momentum_strength if signal else 0.0
        }