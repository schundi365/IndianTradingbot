"""
Volume Analysis Module for MT5 Trading Bot
Implements volume filtering, confirmation, and indicators (OBV, Volume Profile)
"""

import numpy as np
import pandas as pd
import logging
import time
import inspect
from pathlib import Path

# Enhanced logging for volume analyzer
class VolumePerformanceLogger:
    """Enhanced logger for volume analyzer with performance tracking"""
    
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.operation_times = {}
    
    def start_operation(self, operation_name):
        """Start timing an operation"""
        self.operation_times[operation_name] = time.time()
    
    def end_operation(self, operation_name, message=""):
        """End timing an operation and log the duration"""
        if operation_name in self.operation_times:
            duration = time.time() - self.operation_times[operation_name]
            del self.operation_times[operation_name]
            
            # Get caller info
            frame = inspect.currentframe().f_back
            filename = Path(frame.f_code.co_filename).name
            line_number = frame.f_lineno
            
            self.logger.info(f"⏱️ {operation_name} completed in {duration:.3f}s {message}")
            return duration
        return 0
    
    def info(self, message):
        """Enhanced info logging with caller context"""
        frame = inspect.currentframe().f_back
        filename = Path(frame.f_code.co_filename).name
        line_number = frame.f_lineno
        enhanced_message = f"[{filename}:{line_number}] {message}"
        self.logger.info(enhanced_message)
    
    def warning(self, message):
        """Enhanced warning logging with caller context"""
        frame = inspect.currentframe().f_back
        filename = Path(frame.f_code.co_filename).name
        line_number = frame.f_lineno
        enhanced_message = f"[{filename}:{line_number}] {message}"
        self.logger.warning(enhanced_message)
    
    def error(self, message):
        """Enhanced error logging with caller context"""
        frame = inspect.currentframe().f_back
        filename = Path(frame.f_code.co_filename).name
        line_number = frame.f_lineno
        enhanced_message = f"[{filename}:{line_number}] {message}"
        self.logger.error(enhanced_message)
    
    def debug(self, message):
        """Enhanced debug logging with caller context"""
        frame = inspect.currentframe().f_back
        filename = Path(frame.f_code.co_filename).name
        line_number = frame.f_lineno
        enhanced_message = f"[{filename}:{line_number}] {message}"
        self.logger.debug(enhanced_message)


class VolumeAnalyzer:
    """Analyzes volume data for trade confirmation and filtering"""
    
    def __init__(self, config):
        """
        Initialize Volume Analyzer with improved default settings
        
        Args:
            config: Bot configuration dictionary
        """
        # Initialize enhanced logger
        self.logger = VolumePerformanceLogger(f"{__name__}.VolumeAnalyzer")
        self.logger.start_operation("Volume Analyzer Initialization")
        
        self.use_volume_filter = config.get('use_volume_filter', True)
        
        # IMPROVEMENT: Better default settings
        self.min_volume_ma = config.get('min_volume_ma', 0.7)  # Only reject VERY low volume
        self.normal_volume_ma = config.get('normal_volume_ma', 1.0)  # Normal threshold
        self.high_volume_ma = config.get('high_volume_ma', 1.5)  # High volume threshold
        self.very_high_volume_ma = config.get('very_high_volume_ma', 2.0)  # Exceptional volume
        self.volume_spike_threshold = config.get('volume_spike_threshold', 1.5)  # Spike detection threshold
        
        self.volume_ma_period = config.get('volume_ma_period', 20)
        self.volume_ma_min_period = config.get('volume_ma_min_period', 10)  # Fallback for insufficient data
        
        # Enhanced OBV settings
        self.obv_period = config.get('obv_period', 14)  # Keep for compatibility
        self.obv_period_short = config.get('obv_period_short', 10)
        self.obv_period_long = config.get('obv_period_long', 30)
        
        # Divergence settings
        self.divergence_lookback = config.get('divergence_lookback', 20)
        self.divergence_threshold = config.get('divergence_threshold', 0.85)  # 15% volume drop
        
        self.logger.info(f"Volume Analyzer initialized with improved settings:")
        self.logger.info(f"  Filter Enabled: {self.use_volume_filter}")
        self.logger.info(f"  Min Volume Threshold: {self.min_volume_ma}x (only reject very low)")
        self.logger.info(f"  Normal Volume: {self.normal_volume_ma}x")
        self.logger.info(f"  High Volume: {self.high_volume_ma}x")
        self.logger.info(f"  Very High Volume: {self.very_high_volume_ma}x")
        self.logger.info(f"  Volume Spike Threshold: {self.volume_spike_threshold}x")
        self.logger.info(f"  Volume MA Period: {self.volume_ma_period} (min: {self.volume_ma_min_period})")
        self.logger.info(f"  OBV Periods: Short={self.obv_period_short}, Long={self.obv_period_long}")
        self.logger.info(f"  Divergence: Lookback={self.divergence_lookback}, Threshold={self.divergence_threshold}")
        
        self.logger.end_operation("Volume Analyzer Initialization")
    
    def calculate_volume_ma(self, df):
        """
        Calculate volume moving average
        
        Args:
            df: DataFrame with 'tick_volume' column
            
        Returns:
            Series: Volume moving average
        """
        return df['tick_volume'].rolling(window=self.volume_ma_period).mean()
    
    def is_above_average_volume(self, df):
        """
        Check if current volume is above average with adaptive period handling
        
        Args:
            df: DataFrame with 'tick_volume' column
            
        Returns:
            bool: True if current volume > average * min_volume_ma
        """
        self.logger.start_operation("Volume Analysis")
        
        # IMPROVEMENT #1: Adaptive Data Requirements
        min_required = 10  # Minimum bars needed
        
        if len(df) < min_required:
            self.logger.warning(f"Insufficient data for volume analysis: {len(df)} bars < {min_required}")
            self.logger.end_operation("Volume Analysis", "- Insufficient data, allowing trade")
            return True  # Can't analyze, don't filter
        
        # Use adaptive period based on available data
        if len(df) < self.volume_ma_period:
            # Use shorter period
            actual_period = max(min_required, len(df) - 2)
            self.logger.info(f"Using adaptive volume period: {actual_period} (not enough for {self.volume_ma_period})")
        else:
            actual_period = self.volume_ma_period
        
        volume_ma = df['tick_volume'].rolling(window=actual_period).mean()
        current_volume = df['tick_volume'].iloc[-1]
        avg_volume = volume_ma.iloc[-1]
        
        if pd.isna(avg_volume) or avg_volume == 0:
            self.logger.end_operation("Volume Analysis", "- No average volume data, allowing trade")
            return True
        
        volume_ratio = current_volume / avg_volume
        
        # IMPROVEMENT #2: Tiered Volume Classification
        volume_class = self.classify_volume_strength(volume_ratio)
        
        # DETAILED LOGGING WITH ENHANCED LOGGER
        self.logger.info("="*80)
        self.logger.info("📊 VOLUME FILTER CHECK - DETAILED CALCULATIONS")
        self.logger.info("="*80)
        self.logger.info(f"Data Points Available:  {len(df)} bars")
        self.logger.info(f"Volume MA Period Used:  {actual_period} bars")
        self.logger.info(f"Current Volume:         {current_volume:.0f}")
        self.logger.info(f"Average Volume (MA{actual_period}):  {avg_volume:.0f}")
        self.logger.info(f"Volume Ratio:           {volume_ratio:.2f}x")
        self.logger.info(f"Volume Classification:  {volume_class['level']}")
        self.logger.info(f"Volume Description:     {volume_class['description']}")
        self.logger.info(f"Confidence Impact:      {volume_class['score']:+.2%}")
        
        if volume_class['passes']:
            self.logger.info(f"✅ VOLUME FILTER PASSED: {volume_class['level']} volume")
            self.logger.info(f"   Volume {volume_ratio:.2f}x is acceptable for trading")
            self.logger.end_operation("Volume Analysis", f"- {volume_class['level']} volume, trade allowed")
        else:
            self.logger.info(f"❌ VOLUME FILTER REJECTED: {volume_class['level']} volume")
            self.logger.info(f"   Volume {volume_ratio:.2f}x is too low for reliable signals")
            self.logger.end_operation("Volume Analysis", f"- {volume_class['level']} volume, trade rejected")
        self.logger.info("="*80)
        
        return volume_class['passes']
    
    def classify_volume_strength(self, volume_ratio):
        """
        Classify volume into tiers with graduated thresholds
        
        Args:
            volume_ratio: Current volume / Average volume
            
        Returns:
            dict: Volume classification with level, score, description, and passes flag
        """
        # IMPROVEMENT #2: Tiered Volume Thresholds (More lenient - accepts 0.5x and above)
        if volume_ratio >= self.very_high_volume_ma:
            return {
                'level': 'VERY_HIGH',
                'score': 0.15,  # Big confidence boost
                'description': 'Exceptional volume spike',
                'passes': True
            }
        elif volume_ratio >= self.high_volume_ma:
            return {
                'level': 'HIGH',
                'score': 0.10,
                'description': 'Above average volume',
                'passes': True
            }
        elif volume_ratio >= self.normal_volume_ma:
            return {
                'level': 'NORMAL',
                'score': 0.05,  # Small boost
                'description': 'Normal trading volume',
                'passes': True  # Don't reject normal volume!
            }
        elif volume_ratio >= 0.7:
            return {
                'level': 'MODERATE',
                'score': 0.02,  # Tiny boost
                'description': 'Moderate volume - acceptable',
                'passes': True  # Still allow
            }
        elif volume_ratio >= 0.5:
            return {
                'level': 'LOW',
                'score': 0.00,  # No boost
                'description': 'Low volume but acceptable',
                'passes': True  # Accept down to 0.5x average
            }
        else:  # < 0.5x
            return {
                'level': 'VERY_LOW',
                'score': -0.05,  # Small penalty
                'description': 'Very low volume - unreliable signals',
                'passes': False  # Only reject if extremely low (< 0.5x)
            }
    
    def get_volume_trend(self, df, periods=5):
        """
        Determine if volume is increasing or decreasing
        
        Args:
            df: DataFrame with 'tick_volume' column
            periods: Number of periods to analyze
            
        Returns:
            str: 'increasing', 'decreasing', or 'neutral'
        """
        if len(df) < periods:
            return 'neutral'
        
        recent_volumes = df['tick_volume'].iloc[-periods:].values
        
        # Calculate trend using linear regression
        x = np.arange(len(recent_volumes))
        slope = np.polyfit(x, recent_volumes, 1)[0]
        
        # Determine trend
        if slope > 0:
            return 'increasing'
        elif slope < 0:
            return 'decreasing'
        else:
            return 'neutral'
    
    def calculate_obv(self, df):
        """
        Calculate On-Balance Volume (OBV)
        
        OBV adds volume on up days and subtracts on down days
        
        Args:
            df: DataFrame with 'close' and 'tick_volume' columns
            
        Returns:
            Series: OBV values
        """
        if len(df) < 2:
            return pd.Series([0] * len(df), index=df.index)
        
        # Calculate price changes
        price_change = df['close'].diff()
        
        # Initialize OBV
        obv = pd.Series(index=df.index, dtype=float)
        obv.iloc[0] = df['tick_volume'].iloc[0]
        
        # Calculate OBV
        for i in range(1, len(df)):
            if price_change.iloc[i] > 0:
                obv.iloc[i] = obv.iloc[i-1] + df['tick_volume'].iloc[i]
            elif price_change.iloc[i] < 0:
                obv.iloc[i] = obv.iloc[i-1] - df['tick_volume'].iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i-1]
        
        return obv
    
    def get_obv_signal(self, df):
        """
        Get OBV-based signal
        
        Args:
            df: DataFrame with price and volume data
            
        Returns:
            str: 'bullish', 'bearish', or 'neutral'
        """
        if len(df) < self.obv_period + 1:
            return 'neutral'
        
        obv = self.calculate_obv(df)
        obv_ma = obv.rolling(window=self.obv_period).mean()
        
        current_obv = obv.iloc[-1]
        current_obv_ma = obv_ma.iloc[-1]
        
        if pd.isna(current_obv_ma):
            return 'neutral'
        
        # OBV above MA = bullish, below = bearish
        if current_obv > current_obv_ma:
            return 'bullish'
        elif current_obv < current_obv_ma:
            return 'bearish'
        else:
            return 'neutral'
    
    def check_volume_divergence(self, df, periods=10):
        """
        Check for volume divergence (price vs volume)
        
        Divergence occurs when:
        - Price makes new high but volume decreases (bearish)
        - Price makes new low but volume decreases (bullish)
        
        Args:
            df: DataFrame with price and volume data
            periods: Number of periods to check
            
        Returns:
            str: 'bullish_divergence', 'bearish_divergence', or 'none'
        """
        if len(df) < periods:
            return 'none'
        
        recent_df = df.iloc[-periods:]
        
        # Check for price highs/lows
        price_high = recent_df['high'].max()
        price_low = recent_df['low'].min()
        
        current_price = df['close'].iloc[-1]
        current_volume = df['tick_volume'].iloc[-1]
        
        # Get volume at price extremes
        high_idx = recent_df['high'].idxmax()
        low_idx = recent_df['low'].idxmin()
        
        volume_at_high = recent_df.loc[high_idx, 'tick_volume']
        volume_at_low = recent_df.loc[low_idx, 'tick_volume']
        
        # Bearish divergence: new high with lower volume
        if current_price >= price_high * 0.999:  # Near high
            if current_volume < volume_at_high * 0.8:  # 20% less volume
                self.logger.info("Bearish divergence detected: New high with lower volume")
                return 'bearish_divergence'
        
        # Bullish divergence: new low with lower volume
        if current_price <= price_low * 1.001:  # Near low
            if current_volume < volume_at_low * 0.8:  # 20% less volume
                self.logger.info("Bullish divergence detected: New low with lower volume")
                return 'bullish_divergence'
        
        return 'none'
    
    def get_candle_pressure(self, df):
        """
        Determine if volume is buying or selling pressure based on candle color
        
        Args:
            df: DataFrame with OHLC and volume data
            
        Returns:
            dict: Candle pressure analysis with type, strength, and boost
        """
        if len(df) < 20:
            return {
                'type': 'NEUTRAL',
                'strength': 'NONE',
                'boost': 0.00,
                'description': 'Insufficient data for candle pressure analysis'
            }
        
        current = df.iloc[-1]
        current_volume = current['tick_volume']
        
        # Check candle color
        candle_body = current['close'] - current['open']
        is_bullish = candle_body > 0
        
        # Check volume relative to average
        avg_volume = df['tick_volume'].rolling(20).mean().iloc[-1]
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
        
        # Analyze pressure based on candle color and volume
        if is_bullish and volume_ratio > 1.2:
            return {
                'type': 'BUYING',
                'strength': 'STRONG' if volume_ratio > self.high_volume_ma else 'MODERATE',
                'boost': 0.10 if volume_ratio > self.high_volume_ma else 0.05,
                'description': f'Bullish candle with {volume_ratio:.1f}x volume'
            }
        elif not is_bullish and volume_ratio > 1.2:
            return {
                'type': 'SELLING',
                'strength': 'STRONG' if volume_ratio > self.high_volume_ma else 'MODERATE',
                'boost': 0.10 if volume_ratio > self.high_volume_ma else 0.05,
                'description': f'Bearish candle with {volume_ratio:.1f}x volume'
            }
        elif is_bullish:
            return {
                'type': 'BUYING',
                'strength': 'WEAK',
                'boost': 0.02,
                'description': f'Bullish candle with normal volume ({volume_ratio:.1f}x)'
            }
        elif not is_bullish:
            return {
                'type': 'SELLING',
                'strength': 'WEAK',
                'boost': 0.02,
                'description': f'Bearish candle with normal volume ({volume_ratio:.1f}x)'
            }
        else:
            return {
                'type': 'NEUTRAL',
                'strength': 'NONE',
                'boost': 0.00,
                'description': 'Doji candle - neutral pressure'
            }
    
    def calculate_volume_profile(self, df, num_bins=20):
        """
        Calculate Volume Profile (Volume at Price levels)
        
        Args:
            df: DataFrame with price and volume data
            num_bins: Number of price bins
            
        Returns:
            dict: Volume profile data
        """
        if len(df) < 10:
            return None
        
        # Get price range
        price_min = df['low'].min()
        price_max = df['high'].max()
        
        # Create price bins
        bins = np.linspace(price_min, price_max, num_bins + 1)
        
        # Calculate volume at each price level
        volume_profile = {}
        for i in range(len(bins) - 1):
            bin_low = bins[i]
            bin_high = bins[i + 1]
            
            # Find candles in this price range
            mask = (df['low'] <= bin_high) & (df['high'] >= bin_low)
            volume_in_bin = df.loc[mask, 'tick_volume'].sum()
            
            price_level = (bin_low + bin_high) / 2
            volume_profile[price_level] = volume_in_bin
        
        # Find Point of Control (POC) - price with highest volume
        poc_price = max(volume_profile, key=volume_profile.get)
        poc_volume = volume_profile[poc_price]
        
        return {
            'profile': volume_profile,
            'poc_price': poc_price,
            'poc_volume': poc_volume,
            'price_range': (price_min, price_max)
        }
    
    def detect_exhaustion_volume(self, df, key_level: float = None, lookback: int = 20) -> dict:
        """
        Detect exhaustion volume patterns at key price levels
        
        Exhaustion occurs when:
        - High volume at resistance/support levels
        - Volume spikes without price follow-through
        - Decreasing volume on continued price movement
        
        Args:
            df: DataFrame with price and volume data
            key_level: Optional key price level to check
            lookback: Number of periods to analyze
            
        Returns:
            dict: Exhaustion analysis results
        """
        if len(df) < lookback:
            return {
                'detected': False,
                'type': 'none',
                'strength': 0.0,
                'description': 'Insufficient data for exhaustion analysis'
            }
        
        recent_df = df.iloc[-lookback:]
        current_price = df['close'].iloc[-1]
        current_volume = df['tick_volume'].iloc[-1]
        
        # Calculate volume statistics with more reasonable thresholds
        avg_volume = recent_df['tick_volume'].mean()
        volume_std = recent_df['tick_volume'].std()
        
        # Use configured spike threshold instead of hardcoded value
        high_volume_threshold = avg_volume * self.volume_spike_threshold
        
        self.logger.debug(f"Exhaustion analysis: avg_volume={avg_volume:.0f}, threshold={high_volume_threshold:.0f} ({self.volume_spike_threshold}x)")
        
        # Check for volume spikes
        volume_spikes = recent_df[recent_df['tick_volume'] > high_volume_threshold]
        
        if len(volume_spikes) == 0:
            return {
                'detected': False,
                'type': 'none',
                'strength': 0.0,
                'description': f'No volume spikes above {high_volume_threshold:.0f} threshold detected'
            }
        
        self.logger.debug(f"Found {len(volume_spikes)} volume spikes")
        
        # Analyze price action after volume spikes
        exhaustion_signals = []
        
        for idx, spike_row in volume_spikes.iterrows():
            spike_price = spike_row['close']
            spike_volume = spike_row['tick_volume']
            
            # Find position of spike in recent_df
            try:
                spike_position = recent_df.index.get_loc(idx)
            except KeyError:
                continue
            
            # Need at least 2 bars after spike to analyze follow-through
            if spike_position < len(recent_df) - 2:
                
                subsequent_bars = recent_df.iloc[spike_position+1:min(spike_position+4, len(recent_df))]
                
                if len(subsequent_bars) > 0:
                    # Check for exhaustion patterns
                    price_follow_through = abs(subsequent_bars['close'].iloc[-1] - spike_price) / spike_price
                    volume_decline = (subsequent_bars['tick_volume'].mean() / spike_volume) if spike_volume > 0 else 1.0
                    
                    self.logger.debug(f"Spike at {spike_price:.5f}: follow_through={price_follow_through:.4f}, volume_decline={volume_decline:.3f}")
                    
                    # Exhaustion criteria - low price follow-through AND volume decline
                    if price_follow_through < 0.005 and volume_decline < 0.8:  # Relaxed criteria
                        exhaustion_type = 'bearish_exhaustion' if spike_price >= current_price else 'bullish_exhaustion'
                        
                        # Calculate strength based on volume spike magnitude and lack of follow-through
                        volume_strength = min(2.0, spike_volume / avg_volume) / 2.0  # Normalize to 0-1
                        follow_through_penalty = price_follow_through / 0.005  # Penalty for follow-through
                        volume_decline_bonus = (1.0 - volume_decline)  # Bonus for volume decline
                        
                        strength = volume_strength * (1.0 - follow_through_penalty) * (1.0 + volume_decline_bonus)
                        strength = max(0.0, min(1.0, strength))
                        
                        exhaustion_signals.append({
                            'type': exhaustion_type,
                            'strength': strength,
                            'spike_price': spike_price,
                            'spike_volume': spike_volume,
                            'follow_through': price_follow_through,
                            'volume_decline': volume_decline
                        })
                        
                        self.logger.debug(f"Exhaustion signal: {exhaustion_type}, strength={strength:.3f}")
        
        if exhaustion_signals:
            # Return strongest exhaustion signal
            strongest = max(exhaustion_signals, key=lambda x: x['strength'])
            return {
                'detected': True,
                'type': strongest['type'],
                'strength': strongest['strength'],
                'description': f"Volume exhaustion at {strongest['spike_price']:.5f} with {strongest['strength']:.2f} strength"
            }
        
        return {
            'detected': False,
            'type': 'none',
            'strength': 0.0,
            'description': f'Volume spikes detected but no exhaustion pattern confirmed (need low follow-through + volume decline)'
        }
    
    def confirm_breakout_volume(self, df, breakout_price: float, breakout_direction: str, lookback: int = 10) -> dict:
        """
        Confirm breakout with volume analysis
        
        Valid breakouts should have:
        - Above average volume on breakout
        - Sustained volume on continuation
        - Volume expansion compared to consolidation period
        
        Args:
            df: DataFrame with price and volume data
            breakout_price: Price level of the breakout
            breakout_direction: 'up' or 'down'
            lookback: Periods to analyze before breakout
            
        Returns:
            dict: Breakout volume confirmation results
        """
        if len(df) < lookback + 5:
            return {
                'confirmed': False,
                'strength': 0.0,
                'volume_ratio': 1.0,
                'description': 'Insufficient data for breakout confirmation'
            }
        
        # Get pre-breakout consolidation period
        consolidation_df = df.iloc[-(lookback + 5):-5]
        breakout_df = df.iloc[-5:]  # Last 5 bars for breakout analysis
        
        # Calculate volume statistics
        consolidation_avg_volume = consolidation_df['tick_volume'].mean()
        breakout_avg_volume = breakout_df['tick_volume'].mean()
        current_volume = df['tick_volume'].iloc[-1]
        
        # Volume expansion ratio
        volume_expansion = breakout_avg_volume / consolidation_avg_volume if consolidation_avg_volume > 0 else 1.0
        current_volume_ratio = current_volume / consolidation_avg_volume if consolidation_avg_volume > 0 else 1.0
        
        # Price movement confirmation
        price_movement = abs(df['close'].iloc[-1] - breakout_price) / breakout_price
        
        # Breakout confirmation criteria
        volume_confirmed = volume_expansion >= 1.3  # 30% volume increase
        price_confirmed = price_movement >= 0.001   # Minimum price movement
        sustained_volume = current_volume_ratio >= 1.2  # Current volume still elevated
        
        # Calculate confirmation strength
        strength = 0.0
        if volume_confirmed:
            strength += 0.4
        if price_confirmed:
            strength += 0.3
        if sustained_volume:
            strength += 0.3
        
        # Bonus for exceptional volume
        if volume_expansion >= 2.0:
            strength += 0.2
        
        strength = min(1.0, strength)
        
        confirmed = volume_confirmed and price_confirmed
        
        return {
            'confirmed': confirmed,
            'strength': strength,
            'volume_ratio': volume_expansion,
            'current_volume_ratio': current_volume_ratio,
            'price_movement': price_movement,
            'description': f"Breakout {'confirmed' if confirmed else 'not confirmed'} with {volume_expansion:.1f}x volume expansion"
        }
    
    def detect_volume_price_divergence(self, df, trend_direction: str, lookback: int = 20) -> dict:
        """
        Detect volume-price divergence patterns for trend analysis
        
        Divergence types:
        - Bullish: Price makes lower lows but volume decreases (selling exhaustion)
        - Bearish: Price makes higher highs but volume decreases (buying exhaustion)
        
        Args:
            df: DataFrame with price and volume data
            trend_direction: 'up', 'down', or 'auto' to detect automatically
            lookback: Number of periods to analyze
            
        Returns:
            dict: Divergence analysis results
        """
        if len(df) < lookback:
            return {
                'detected': False,
                'type': 'none',
                'strength': 0.0,
                'price_points': [],
                'volume_points': [],
                'description': 'Insufficient data for divergence analysis'
            }
        
        recent_df = df.iloc[-lookback:].copy()
        
        # Calculate volume moving average for comparison
        recent_df['volume_ma'] = recent_df['tick_volume'].rolling(window=5).mean()
        
        # Find swing points for price and volume
        price_highs = []
        price_lows = []
        volume_highs = []
        volume_lows = []
        
        # Simple swing point detection (can be enhanced)
        for i in range(2, len(recent_df) - 2):
            current_high = recent_df['high'].iloc[i]
            current_low = recent_df['low'].iloc[i]
            current_volume = recent_df['volume_ma'].iloc[i]
            
            # Price swing highs
            if (current_high > recent_df['high'].iloc[i-2:i].max() and 
                current_high > recent_df['high'].iloc[i+1:i+3].max()):
                price_highs.append((recent_df.index[i], current_high))
            
            # Price swing lows
            if (current_low < recent_df['low'].iloc[i-2:i].min() and 
                current_low < recent_df['low'].iloc[i+1:i+3].min()):
                price_lows.append((recent_df.index[i], current_low))
            
            # Volume swing points
            if (current_volume > recent_df['volume_ma'].iloc[i-2:i].max() and 
                current_volume > recent_df['volume_ma'].iloc[i+1:i+3].max()):
                volume_highs.append((recent_df.index[i], current_volume))
            
            if (current_volume < recent_df['volume_ma'].iloc[i-2:i].min() and 
                current_volume < recent_df['volume_ma'].iloc[i+1:i+3].min()):
                volume_lows.append((recent_df.index[i], current_volume))
        
        # Analyze divergence patterns
        divergences = []
        
        # Bearish divergence: Higher price highs with lower volume highs
        if len(price_highs) >= 2 and len(volume_highs) >= 2:
            recent_price_highs = sorted(price_highs, key=lambda x: x[0])[-2:]
            recent_volume_highs = sorted(volume_highs, key=lambda x: x[0])[-2:]
            
            if (recent_price_highs[1][1] > recent_price_highs[0][1] and  # Higher price high
                recent_volume_highs[1][1] < recent_volume_highs[0][1]):   # Lower volume high
                
                price_change = (recent_price_highs[1][1] - recent_price_highs[0][1]) / recent_price_highs[0][1]
                volume_change = (recent_volume_highs[0][1] - recent_volume_highs[1][1]) / recent_volume_highs[0][1]
                strength = min(1.0, (price_change + volume_change) * 2)
                
                divergences.append({
                    'type': 'bearish_divergence',
                    'strength': strength,
                    'price_points': recent_price_highs,
                    'volume_points': recent_volume_highs
                })
        
        # Bullish divergence: Lower price lows with higher volume lows (less selling pressure)
        if len(price_lows) >= 2 and len(volume_lows) >= 2:
            recent_price_lows = sorted(price_lows, key=lambda x: x[0])[-2:]
            recent_volume_lows = sorted(volume_lows, key=lambda x: x[0])[-2:]
            
            if (recent_price_lows[1][1] < recent_price_lows[0][1] and    # Lower price low
                recent_volume_lows[1][1] > recent_volume_lows[0][1]):    # Higher volume low (less selling)
                
                price_change = (recent_price_lows[0][1] - recent_price_lows[1][1]) / recent_price_lows[0][1]
                volume_change = (recent_volume_lows[1][1] - recent_volume_lows[0][1]) / recent_volume_lows[0][1]
                strength = min(1.0, (price_change + volume_change) * 2)
                
                divergences.append({
                    'type': 'bullish_divergence',
                    'strength': strength,
                    'price_points': recent_price_lows,
                    'volume_points': recent_volume_lows
                })
        
        if divergences:
            # Return strongest divergence
            strongest = max(divergences, key=lambda x: x['strength'])
            return {
                'detected': True,
                'type': strongest['type'],
                'strength': strongest['strength'],
                'price_points': strongest['price_points'],
                'volume_points': strongest['volume_points'],
                'description': f"{strongest['type'].replace('_', ' ').title()} detected with {strongest['strength']:.2f} strength"
            }
        
        return {
            'detected': False,
            'type': 'none',
            'strength': 0.0,
            'price_points': [],
            'volume_points': [],
            'description': 'No significant volume-price divergence detected'
        }
    
    def filter_signals_by_volume(self, signals: list, df: pd.DataFrame, min_volume_score: float = 0.6) -> list:
        """
        Filter trading signals based on volume analysis
        
        Args:
            signals: List of trading signals to filter
            df: DataFrame with price and volume data
            min_volume_score: Minimum volume score required (0.0 to 1.0)
            
        Returns:
            list: Filtered signals that meet volume criteria
        """
        if not self.use_volume_filter:
            return signals
        
        filtered_signals = []
        
        for signal in signals:
            signal_type = 'buy' if 'buy' in str(signal).lower() or 'bullish' in str(signal).lower() else 'sell'
            
            # Get volume confirmation
            volume_confirmation = self.get_volume_confirmation(df, signal_type)
            
            # Check if signal meets volume criteria
            if volume_confirmation['score'] >= min_volume_score:
                # Add volume information to signal if possible
                if hasattr(signal, 'supporting_factors'):
                    signal.supporting_factors.append(f"volume_score_{volume_confirmation['score']:.2f}")
                
                filtered_signals.append(signal)
                self.logger.info(f"✅ Signal passed volume filter: {signal_type} (score: {volume_confirmation['score']:.2f})")
            else:
                self.logger.info(f"❌ Signal rejected by volume filter: {signal_type} (score: {volume_confirmation['score']:.2f} < {min_volume_score:.2f})")
        
        self.logger.info(f"Volume filtering: {len(filtered_signals)}/{len(signals)} signals passed")
        return filtered_signals

    def get_volume_confirmation(self, df, signal_type):
        """
        Get comprehensive volume confirmation with weighted scoring system
        Enhanced with trend-specific volume patterns
        
        Args:
            df: DataFrame with price and volume data
            signal_type: 'buy' or 'sell'
            
        Returns:
            dict: Volume confirmation data with weighted scoring
        """
        confirmation = {
            'above_average': False,
            'volume_trend': 'neutral',
            'obv_signal': 'neutral',
            'divergence': 'none',
            'candle_pressure': {},
            'exhaustion_volume': {},
            'volume_price_divergence': {},
            'confirmed': False,
            'confidence_boost': 0.0,
            'score': 0.5,  # Start neutral
            'reasons': []
        }
        
        self.logger.info("-"*80)
        self.logger.info(f"🔍 ENHANCED VOLUME CONFIRMATION ANALYSIS FOR {signal_type.upper()}")
        self.logger.info("-"*80)
        
        # IMPROVEMENT #3: Weighted Scoring System with Trend-Specific Patterns
        score = 0.5  # Start neutral
        reasons = []
        
        # 1. Volume strength analysis (0 to +0.20)
        volume_ratio = self.get_volume_ratio(df)
        vol_class = self.classify_volume_strength(volume_ratio)
        score += vol_class['score']
        reasons.append(f"Volume: {vol_class['level']} ({vol_class['score']:+.2f})")
        confirmation['above_average'] = vol_class['passes']
        
        # 2. Volume trend (±0.05)
        confirmation['volume_trend'] = self.get_volume_trend(df)
        if confirmation['volume_trend'] == 'increasing':
            score += 0.05
            reasons.append("Trend: Increasing (+0.05)")
        elif confirmation['volume_trend'] == 'decreasing':
            score -= 0.05
            reasons.append("Trend: Decreasing (-0.05)")
        else:
            reasons.append("Trend: Neutral (0.00)")
        
        # 3. OBV alignment (±0.10)
        confirmation['obv_signal'] = self.get_obv_signal(df)
        if signal_type == 'buy' and confirmation['obv_signal'] == 'bullish':
            score += 0.10
            reasons.append("OBV: Bullish (+0.10)")
        elif signal_type == 'sell' and confirmation['obv_signal'] == 'bearish':
            score += 0.10
            reasons.append("OBV: Bearish (+0.10)")
        elif confirmation['obv_signal'] == 'neutral':
            reasons.append("OBV: Neutral (0.00)")
        else:
            score -= 0.05  # Slight penalty for contradiction
            reasons.append(f"OBV: Contradicts (-0.05)")
        
        # 4. Divergence analysis (±0.15)
        confirmation['divergence'] = self.check_volume_divergence(df)
        if signal_type == 'buy' and confirmation['divergence'] == 'bullish_divergence':
            score += 0.15
            reasons.append("Divergence: Bullish (+0.15)")
        elif signal_type == 'sell' and confirmation['divergence'] == 'bearish_divergence':
            score += 0.15
            reasons.append("Divergence: Bearish (+0.15)")
        elif confirmation['divergence'] != 'none':
            score -= 0.10  # Contradictory divergence
            reasons.append("Divergence: Contradicts (-0.10)")
        else:
            reasons.append("Divergence: None (0.00)")
        
        # 5. Candle pressure analysis (±0.10)
        confirmation['candle_pressure'] = self.get_candle_pressure(df)
        pressure = confirmation['candle_pressure']
        
        if signal_type == 'buy' and pressure['type'] == 'BUYING':
            score += pressure['boost']
            reasons.append(f"Candle: {pressure['strength']} buying pressure (+{pressure['boost']:.2f})")
        elif signal_type == 'sell' and pressure['type'] == 'SELLING':
            score += pressure['boost']
            reasons.append(f"Candle: {pressure['strength']} selling pressure (+{pressure['boost']:.2f})")
        elif pressure['type'] != 'NEUTRAL':
            score -= 0.05
            reasons.append(f"Candle: Wrong pressure direction (-0.05)")
        else:
            reasons.append("Candle: Neutral pressure (0.00)")
        
        # 6. NEW: Exhaustion volume analysis (±0.12)
        confirmation['exhaustion_volume'] = self.detect_exhaustion_volume(df)
        exhaustion = confirmation['exhaustion_volume']
        
        if exhaustion['detected']:
            if signal_type == 'buy' and exhaustion['type'] == 'bearish_exhaustion':
                exhaustion_boost = exhaustion['strength'] * 0.12
                score += exhaustion_boost
                reasons.append(f"Exhaustion: Bearish exhaustion detected (+{exhaustion_boost:.2f})")
            elif signal_type == 'sell' and exhaustion['type'] == 'bullish_exhaustion':
                exhaustion_boost = exhaustion['strength'] * 0.12
                score += exhaustion_boost
                reasons.append(f"Exhaustion: Bullish exhaustion detected (+{exhaustion_boost:.2f})")
            else:
                score -= 0.06  # Wrong type of exhaustion
                reasons.append("Exhaustion: Wrong type (-0.06)")
        else:
            reasons.append("Exhaustion: None detected (0.00)")
        
        # 7. NEW: Volume-price divergence analysis (±0.15)
        trend_direction = 'up' if signal_type == 'buy' else 'down'
        confirmation['volume_price_divergence'] = self.detect_volume_price_divergence(df, trend_direction)
        vp_divergence = confirmation['volume_price_divergence']
        
        if vp_divergence['detected']:
            if signal_type == 'buy' and vp_divergence['type'] == 'bullish_divergence':
                divergence_boost = vp_divergence['strength'] * 0.15
                score += divergence_boost
                reasons.append(f"VP Divergence: Bullish pattern (+{divergence_boost:.2f})")
            elif signal_type == 'sell' and vp_divergence['type'] == 'bearish_divergence':
                divergence_boost = vp_divergence['strength'] * 0.15
                score += divergence_boost
                reasons.append(f"VP Divergence: Bearish pattern (+{divergence_boost:.2f})")
            else:
                score -= 0.08  # Contradictory divergence
                reasons.append("VP Divergence: Contradictory (-0.08)")
        else:
            reasons.append("VP Divergence: None detected (0.00)")
        
        # Clamp score between 0.0 and 1.0
        final_score = max(0.0, min(1.0, score))
        
        # Decision based on volume level and trend-specific patterns
        confirmation['confirmed'] = vol_class['passes']  # Based on volume level
        confidence_boost = (final_score - 0.5) * 0.2  # Convert to ±0.10 boost
        
        # Store results
        confirmation['score'] = final_score
        confirmation['confidence_boost'] = confidence_boost
        confirmation['reasons'] = reasons
        
        # Enhanced detailed logging
        self.logger.info(f"📊 WEIGHTED SCORING BREAKDOWN:")
        for reason in reasons:
            self.logger.info(f"   • {reason}")
        
        # Log trend-specific patterns
        if exhaustion['detected']:
            self.logger.info(f"🔥 EXHAUSTION PATTERN: {exhaustion['description']}")
        
        if vp_divergence['detected']:
            self.logger.info(f"📈 VOLUME-PRICE DIVERGENCE: {vp_divergence['description']}")
        
        self.logger.info("-"*80)
        self.logger.info(f"📈 FINAL VOLUME ANALYSIS RESULTS:")
        self.logger.info(f"   Volume Score: {final_score:.2f}/1.00")
        self.logger.info(f"   Volume Level: {vol_class['level']}")
        self.logger.info(f"   Decision: {'PASS' if confirmation['confirmed'] else 'REJECT'}")
        self.logger.info(f"   Confidence Boost: {confidence_boost:+.2%}")
        self.logger.info(f"   Reasoning: {vol_class['description']}")
        
        if confirmation['confirmed']:
            self.logger.info(f"✅ VOLUME CONFIRMATION PASSED")
            self.logger.info(f"   Volume conditions support the {signal_type.upper()} signal")
        else:
            self.logger.info(f"❌ VOLUME CONFIRMATION FAILED")
            self.logger.info(f"   Volume too low for reliable {signal_type.upper()} signal")
        
        self.logger.info("="*80)
        
        return confirmation
    
    def get_volume_ratio(self, df):
        """
        Get current volume ratio vs average with adaptive period
        
        Args:
            df: DataFrame with volume data
            
        Returns:
            float: Volume ratio (current/average)
        """
        min_required = 10
        
        if len(df) < min_required:
            return 1.0  # Neutral if insufficient data
        
        # Use adaptive period
        if len(df) < self.volume_ma_period:
            actual_period = max(min_required, len(df) - 2)
        else:
            actual_period = self.volume_ma_period
        
        volume_ma = df['tick_volume'].rolling(window=actual_period).mean()
        current_volume = df['tick_volume'].iloc[-1]
        avg_volume = volume_ma.iloc[-1]
        
        if pd.isna(avg_volume) or avg_volume == 0:
            return 1.0
        
        return current_volume / avg_volume
    
    def should_trade(self, df, signal_type):
        """
        Determine if trade should be taken based on volume analysis
        
        Args:
            df: DataFrame with price and volume data
            signal_type: 'buy' or 'sell'
            
        Returns:
            tuple: (should_trade: bool, confidence_adjustment: float)
        """
        if not self.use_volume_filter:
            return True, 0.0
        
        confirmation = self.get_volume_confirmation(df, signal_type)
        
        # If volume filter is enabled, require confirmation
        should_trade = confirmation['confirmed']
        confidence_adjustment = confirmation['confidence_boost']
        
        if not should_trade:
            self.logger.info(f"Trade rejected by volume filter: {signal_type}")
        
        return should_trade, confidence_adjustment


if __name__ == "__main__":
    # Test volume analyzer
    print("Testing Volume Analyzer...")
    
    # Create sample data
    dates = pd.date_range('2024-01-01', periods=100, freq='1H')
    df = pd.DataFrame({
        'time': dates,
        'open': np.random.randn(100).cumsum() + 100,
        'high': np.random.randn(100).cumsum() + 101,
        'low': np.random.randn(100).cumsum() + 99,
        'close': np.random.randn(100).cumsum() + 100,
        'tick_volume': np.random.randint(1000, 5000, 100)
    })
    
    config = {
        'use_volume_filter': True,
        'min_volume_ma': 1.2,
        'volume_ma_period': 20,
        'obv_period': 14
    }
    
    analyzer = VolumeAnalyzer(config)
    
    print("\n1. Volume MA Test:")
    print(f"   Above average: {analyzer.is_above_average_volume(df)}")
    
    print("\n2. Volume Trend Test:")
    print(f"   Trend: {analyzer.get_volume_trend(df)}")
    
    print("\n3. OBV Signal Test:")
    print(f"   OBV Signal: {analyzer.get_obv_signal(df)}")
    
    print("\n4. Volume Divergence Test:")
    print(f"   Divergence: {analyzer.check_volume_divergence(df)}")
    
    print("\n5. Volume Profile Test:")
    profile = analyzer.calculate_volume_profile(df)
    if profile:
        print(f"   POC Price: {profile['poc_price']:.2f}")
        print(f"   POC Volume: {profile['poc_volume']:.0f}")
    
    print("\n6. Buy Signal Confirmation Test:")
    should_trade, confidence = analyzer.should_trade(df, 'buy')
    print(f"   Should Trade: {should_trade}")
    print(f"   Confidence Boost: {confidence:+.2%}")
    
    print("\n✅ Volume Analyzer Test Complete!")
