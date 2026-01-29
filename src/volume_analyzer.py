"""
Volume Analysis Module for MT5 Trading Bot
Implements volume filtering, confirmation, and indicators (OBV, Volume Profile)
"""

import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class VolumeAnalyzer:
    """Analyzes volume data for trade confirmation and filtering"""
    
    def __init__(self, config):
        """
        Initialize Volume Analyzer
        
        Args:
            config: Bot configuration dictionary
        """
        self.use_volume_filter = config.get('use_volume_filter', True)
        self.min_volume_ma = config.get('min_volume_ma', 1.2)
        self.volume_ma_period = config.get('volume_ma_period', 20)
        self.obv_period = config.get('obv_period', 14)
        
        logger.info(f"Volume Analyzer initialized: Filter={self.use_volume_filter}, Min MA={self.min_volume_ma}x")
    
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
        Check if current volume is above average
        
        Args:
            df: DataFrame with 'tick_volume' column
            
        Returns:
            bool: True if current volume > average * min_volume_ma
        """
        if len(df) < self.volume_ma_period:
            logger.warning("Not enough data for volume analysis")
            return True  # Don't filter if insufficient data
        
        volume_ma = self.calculate_volume_ma(df)
        current_volume = df['tick_volume'].iloc[-1]
        avg_volume = volume_ma.iloc[-1]
        
        if pd.isna(avg_volume) or avg_volume == 0:
            return True
        
        volume_ratio = current_volume / avg_volume
        is_above = volume_ratio >= self.min_volume_ma
        
        logger.debug(f"Volume check: Current={current_volume:.0f}, Avg={avg_volume:.0f}, Ratio={volume_ratio:.2f}x, Above={is_above}")
        
        return is_above
    
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
                logger.info("Bearish divergence detected: New high with lower volume")
                return 'bearish_divergence'
        
        # Bullish divergence: new low with lower volume
        if current_price <= price_low * 1.001:  # Near low
            if current_volume < volume_at_low * 0.8:  # 20% less volume
                logger.info("Bullish divergence detected: New low with lower volume")
                return 'bullish_divergence'
        
        return 'none'
    
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
        Get comprehensive volume confirmation for a trade signal
        
        Args:
            df: DataFrame with price and volume data
            signal_type: 'buy' or 'sell'
            
        Returns:
            dict: Volume confirmation data
        """
        confirmation = {
            'above_average': False,
            'volume_trend': 'neutral',
            'obv_signal': 'neutral',
            'divergence': 'none',
            'confirmed': False,
            'confidence_boost': 0.0
        }
        
        # 1. Check if volume is above average
        confirmation['above_average'] = self.is_above_average_volume(df)
        
        # 2. Get volume trend
        confirmation['volume_trend'] = self.get_volume_trend(df)
        
        # 3. Get OBV signal
        confirmation['obv_signal'] = self.get_obv_signal(df)
        
        # 4. Check for divergence
        confirmation['divergence'] = self.check_volume_divergence(df)
        
        # 5. Determine if signal is confirmed
        if signal_type == 'buy':
            # Buy confirmation: above average volume, increasing trend, bullish OBV
            if confirmation['above_average']:
                confirmation['confidence_boost'] += 0.05
            
            if confirmation['volume_trend'] == 'increasing':
                confirmation['confidence_boost'] += 0.05
            
            if confirmation['obv_signal'] == 'bullish':
                confirmation['confidence_boost'] += 0.05
            
            if confirmation['divergence'] == 'bullish_divergence':
                confirmation['confidence_boost'] += 0.10
            elif confirmation['divergence'] == 'bearish_divergence':
                confirmation['confidence_boost'] -= 0.10
            
            # RELAXED CONFIRMATION: Confirmed if at least 2 positive signals
            # Don't require above_average volume as mandatory
            positive_signals = 0
            if confirmation['above_average']:
                positive_signals += 1
            if confirmation['volume_trend'] == 'increasing':
                positive_signals += 1
            if confirmation['obv_signal'] == 'bullish':
                positive_signals += 1
            
            confirmation['confirmed'] = positive_signals >= 2
        
        elif signal_type == 'sell':
            # Sell confirmation: above average volume, increasing trend, bearish OBV
            if confirmation['above_average']:
                confirmation['confidence_boost'] += 0.05
            
            if confirmation['volume_trend'] == 'increasing':
                confirmation['confidence_boost'] += 0.05
            
            if confirmation['obv_signal'] == 'bearish':
                confirmation['confidence_boost'] += 0.05
            
            if confirmation['divergence'] == 'bearish_divergence':
                confirmation['confidence_boost'] += 0.10
            elif confirmation['divergence'] == 'bullish_divergence':
                confirmation['confidence_boost'] -= 0.10
            
            # RELAXED CONFIRMATION: Confirmed if at least 2 positive signals
            # Don't require above_average volume as mandatory
            positive_signals = 0
            if confirmation['above_average']:
                positive_signals += 1
            if confirmation['volume_trend'] == 'increasing':
                positive_signals += 1
            if confirmation['obv_signal'] == 'bearish':
                positive_signals += 1
            
            confirmation['confirmed'] = positive_signals >= 2
        
        logger.info(f"Volume confirmation for {signal_type}: {confirmation}")
        
        return confirmation
    
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
            logger.info(f"Trade rejected by volume filter: {signal_type}")
        
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
