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
        # IMPROVEMENT #2: Tiered Volume Thresholds
        if volume_ratio >= 2.0:
            return {
                'level': 'VERY_HIGH',
                'score': 0.15,  # Big confidence boost
                'description': 'Exceptional volume spike',
                'passes': True
            }
        elif volume_ratio >= 1.5:
            return {
                'level': 'HIGH',
                'score': 0.10,
                'description': 'Above average volume',
                'passes': True
            }
        elif volume_ratio >= 1.0:
            return {
                'level': 'NORMAL',
                'score': 0.05,  # Small boost
                'description': 'Normal trading volume',
                'passes': True  # Don't reject normal volume!
            }
        elif volume_ratio >= 0.7:
            return {
                'level': 'LOW',
                'score': 0.00,  # No boost
                'description': 'Below average volume',
                'passes': True  # Still allow (just no boost)
            }
        else:  # < 0.7x
            return {
                'level': 'VERY_LOW',
                'score': -0.05,  # Small penalty
                'description': 'Very low volume - unreliable signals',
                'passes': False  # Only reject if VERY low
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
                'strength': 'STRONG' if volume_ratio > 1.5 else 'MODERATE',
                'boost': 0.10 if volume_ratio > 1.5 else 0.05,
                'description': f'Bullish candle with {volume_ratio:.1f}x volume'
            }
        elif not is_bullish and volume_ratio > 1.2:
            return {
                'type': 'SELLING',
                'strength': 'STRONG' if volume_ratio > 1.5 else 'MODERATE',
                'boost': 0.10 if volume_ratio > 1.5 else 0.05,
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
    
    def get_volume_confirmation(self, df, signal_type):
        """
        Get comprehensive volume confirmation with weighted scoring system
        
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
            'confirmed': False,
            'confidence_boost': 0.0,
            'score': 0.5,  # Start neutral
            'reasons': []
        }
        
        self.logger.info("-"*80)
        self.logger.info(f"🔍 ENHANCED VOLUME CONFIRMATION ANALYSIS FOR {signal_type.upper()}")
        self.logger.info("-"*80)
        
        # IMPROVEMENT #3: Weighted Scoring System
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
        
        # 5. IMPROVEMENT #6: Candle pressure analysis (±0.10)
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
        
        # Clamp score between 0.0 and 1.0
        final_score = max(0.0, min(1.0, score))
        
        # IMPROVEMENT #3: Relaxed Confirmation Logic
        # Decision based on volume level (not requiring all factors)
        confirmation['confirmed'] = vol_class['passes']  # Based on volume level
        confidence_boost = (final_score - 0.5) * 0.2  # Convert to ±0.10 boost
        
        # Store results
        confirmation['score'] = final_score
        confirmation['confidence_boost'] = confidence_boost
        confirmation['reasons'] = reasons
        
        # Detailed logging
        self.logger.info(f"📊 WEIGHTED SCORING BREAKDOWN:")
        for reason in reasons:
            self.logger.info(f"   • {reason}")
        
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
