"""
Multi-Timeframe Analyzer for GEM Trading Bot
Implements multi-timeframe confirmation system for trend detection signals
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import logging

# Import data models from trend detection engine
from src.trend_detection_engine import TimeframeAlignment, TrendSignal

logger = logging.getLogger(__name__)

@dataclass
class TimeframeData:
    """Represents data from a specific timeframe"""
    timeframe: int
    timeframe_name: str
    data: pd.DataFrame
    last_update: datetime

@dataclass
class AlignmentResult:
    """Represents alignment analysis between timeframes"""
    primary_signal: str  # 'bullish', 'bearish', 'neutral'
    higher_signal: str   # 'bullish', 'bearish', 'neutral'
    alignment_score: float  # 0.0 to 1.0
    confirmation_level: str  # 'strong', 'moderate', 'weak', 'contradictory'
    factors: List[str]  # Contributing factors to alignment

class MultiTimeframeAnalyzer:
    """
    Multi-timeframe confirmation system for trend detection
    Analyzes signal alignment across different timeframes to improve signal quality
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the multi-timeframe analyzer
        
        Args:
            config: Configuration dictionary with MTF parameters
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Configuration parameters
        self.enable_mtf = config.get('enable_mtf_confirmation', True)
        self.mtf_weight = config.get('mtf_weight', 0.3)
        self.primary_to_higher = config.get('mtf_primary_to_higher', {})
        self.confirmation_bars = config.get('mtf_confirmation_bars', 100)
        self.alignment_threshold = config.get('mtf_alignment_threshold', 0.6)
        self.contradiction_penalty = config.get('mtf_contradiction_penalty', 0.4)
        
        # Cache for higher timeframe data
        self.timeframe_cache = {}
        self.cache_expiry = {}
        
        # Timeframe names for logging
        self.timeframe_names = {
            mt5.TIMEFRAME_M1: "M1",
            mt5.TIMEFRAME_M5: "M5",
            mt5.TIMEFRAME_M15: "M15",
            mt5.TIMEFRAME_M30: "M30",
            mt5.TIMEFRAME_H1: "H1",
            mt5.TIMEFRAME_H4: "H4",
            mt5.TIMEFRAME_D1: "D1",
            mt5.TIMEFRAME_W1: "W1",
            mt5.TIMEFRAME_MN1: "MN1"
        }
        
        self.logger.info(f"MultiTimeframeAnalyzer initialized with {len(self.primary_to_higher)} timeframe relationships")
        
    def get_higher_timeframe_data(self, symbol: str, primary_tf: int) -> Optional[pd.DataFrame]:
        """
        Retrieve higher timeframe data for the given primary timeframe
        
        Args:
            symbol: Trading symbol
            primary_tf: Primary timeframe (MT5 constant)
            
        Returns:
            DataFrame with higher timeframe data or None if not available
        """
        if not self.enable_mtf:
            return None
            
        # Get the corresponding higher timeframe
        higher_tf = self.primary_to_higher.get(primary_tf)
        if higher_tf is None:
            self.logger.debug(f"No higher timeframe mapping for {self.timeframe_names.get(primary_tf, primary_tf)}")
            return None
        
        cache_key = f"{symbol}_{higher_tf}"
        current_time = datetime.now()
        
        # Check cache validity (5 minutes for higher timeframes)
        if (cache_key in self.timeframe_cache and 
            cache_key in self.cache_expiry and 
            current_time < self.cache_expiry[cache_key]):
            
            self.logger.debug(f"Using cached data for {symbol} {self.timeframe_names.get(higher_tf, higher_tf)}")
            return self.timeframe_cache[cache_key].data
        
        try:
            # Fetch higher timeframe data
            self.logger.info(f"Fetching {self.timeframe_names.get(higher_tf, higher_tf)} data for {symbol}")
            
            rates = mt5.copy_rates_from_pos(symbol, higher_tf, 0, self.confirmation_bars)
            
            if rates is None or len(rates) == 0:
                self.logger.warning(f"Failed to fetch {self.timeframe_names.get(higher_tf, higher_tf)} data for {symbol}")
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df.set_index('time', inplace=True)
            
            # Calculate basic indicators for higher timeframe analysis
            df = self._calculate_higher_tf_indicators(df)
            
            # Cache the data
            self.timeframe_cache[cache_key] = TimeframeData(
                timeframe=higher_tf,
                timeframe_name=self.timeframe_names.get(higher_tf, str(higher_tf)),
                data=df,
                last_update=current_time
            )
            
            # Set cache expiry (5 minutes for higher timeframes)
            self.cache_expiry[cache_key] = current_time + timedelta(minutes=5)
            
            self.logger.info(f"Successfully fetched {len(df)} bars of {self.timeframe_names.get(higher_tf, higher_tf)} data for {symbol}")
            return df
            
        except Exception as e:
            self.logger.error(f"Error fetching higher timeframe data for {symbol}: {e}")
            return None
    
    def _calculate_higher_tf_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate indicators needed for higher timeframe analysis
        
        Args:
            df: Higher timeframe price data
            
        Returns:
            DataFrame with calculated indicators
        """
        try:
            # EMA indicators for trend direction
            df['ema_20'] = df['close'].ewm(span=20).mean()
            df['ema_50'] = df['close'].ewm(span=50).mean()
            
            # RSI for momentum
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
            
            # MACD for momentum confirmation
            exp1 = df['close'].ewm(span=12).mean()
            exp2 = df['close'].ewm(span=26).mean()
            df['macd'] = exp1 - exp2
            df['macd_signal'] = df['macd'].ewm(span=9).mean()
            df['macd_histogram'] = df['macd'] - df['macd_signal']
            
            # ADX for trend strength
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
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error calculating higher timeframe indicators: {e}")
            return df
    
    def analyze_timeframe_alignment(self, primary_df: pd.DataFrame, higher_df: pd.DataFrame) -> AlignmentResult:
        """
        Analyze alignment between primary and higher timeframe signals
        
        Args:
            primary_df: Primary timeframe data with indicators
            higher_df: Higher timeframe data with indicators
            
        Returns:
            AlignmentResult with alignment analysis
        """
        try:
            # Get current signals from both timeframes
            primary_signal = self._get_timeframe_signal(primary_df, "primary")
            higher_signal = self._get_timeframe_signal(higher_df, "higher")
            
            # Calculate alignment score
            alignment_score = self._calculate_alignment_score(primary_signal, higher_signal, primary_df, higher_df)
            
            # Determine confirmation level
            confirmation_level = self._get_confirmation_level(alignment_score, primary_signal, higher_signal)
            
            # Identify contributing factors
            factors = self._identify_alignment_factors(primary_df, higher_df, primary_signal, higher_signal)
            
            self.logger.info(f"Timeframe Alignment Analysis:")
            self.logger.info(f"  Primary Signal: {primary_signal}")
            self.logger.info(f"  Higher Signal: {higher_signal}")
            self.logger.info(f"  Alignment Score: {alignment_score:.3f}")
            self.logger.info(f"  Confirmation Level: {confirmation_level}")
            self.logger.info(f"  Contributing Factors: {', '.join(factors)}")
            
            return AlignmentResult(
                primary_signal=primary_signal,
                higher_signal=higher_signal,
                alignment_score=alignment_score,
                confirmation_level=confirmation_level,
                factors=factors
            )
            
        except Exception as e:
            self.logger.error(f"Error in timeframe alignment analysis: {e}")
            return AlignmentResult(
                primary_signal="neutral",
                higher_signal="neutral",
                alignment_score=0.0,
                confirmation_level="weak",
                factors=["analysis_error"]
            )
    
    def _get_timeframe_signal(self, df: pd.DataFrame, tf_type: str) -> str:
        """
        Determine the current signal from timeframe data
        
        Args:
            df: Timeframe data with indicators
            tf_type: "primary" or "higher" for logging
            
        Returns:
            Signal type: 'bullish', 'bearish', or 'neutral'
        """
        if len(df) < 50:
            return "neutral"
        
        try:
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            
            bullish_factors = 0
            bearish_factors = 0
            
            # EMA trend analysis
            if 'ema_20' in df.columns and 'ema_50' in df.columns:
                if latest['ema_20'] > latest['ema_50']:
                    bullish_factors += 1
                elif latest['ema_20'] < latest['ema_50']:
                    bearish_factors += 1
                
                # EMA slope
                ema_20_slope = latest['ema_20'] - prev['ema_20']
                ema_50_slope = latest['ema_50'] - prev['ema_50']
                
                if ema_20_slope > 0 and ema_50_slope > 0:
                    bullish_factors += 1
                elif ema_20_slope < 0 and ema_50_slope < 0:
                    bearish_factors += 1
            
            # RSI momentum
            if 'rsi' in df.columns:
                rsi = latest['rsi']
                if 30 < rsi < 70:  # Not in extreme zones
                    if rsi > 50:
                        bullish_factors += 0.5
                    else:
                        bearish_factors += 0.5
            
            # MACD momentum
            if 'macd' in df.columns and 'macd_signal' in df.columns:
                if latest['macd'] > latest['macd_signal']:
                    bullish_factors += 1
                else:
                    bearish_factors += 1
                
                # MACD histogram trend
                if 'macd_histogram' in df.columns:
                    if latest['macd_histogram'] > prev['macd_histogram']:
                        bullish_factors += 0.5
                    else:
                        bearish_factors += 0.5
            
            # ADX trend strength
            if 'adx' in df.columns:
                adx = latest['adx']
                if adx > 25:  # Strong trend
                    # Determine direction based on other factors
                    if bullish_factors > bearish_factors:
                        bullish_factors += 0.5
                    elif bearish_factors > bullish_factors:
                        bearish_factors += 0.5
            
            # Determine overall signal
            if bullish_factors > bearish_factors + 0.5:
                signal = "bullish"
            elif bearish_factors > bullish_factors + 0.5:
                signal = "bearish"
            else:
                signal = "neutral"
            
            self.logger.debug(f"{tf_type.title()} timeframe signal: {signal} "
                            f"(bullish: {bullish_factors}, bearish: {bearish_factors})")
            
            return signal
            
        except Exception as e:
            self.logger.error(f"Error determining {tf_type} timeframe signal: {e}")
            return "neutral"
    
    def _calculate_alignment_score(self, primary_signal: str, higher_signal: str, 
                                 primary_df: pd.DataFrame, higher_df: pd.DataFrame) -> float:
        """
        Calculate alignment score between timeframes
        
        Args:
            primary_signal: Primary timeframe signal
            higher_signal: Higher timeframe signal
            primary_df: Primary timeframe data
            higher_df: Higher timeframe data
            
        Returns:
            Alignment score (0.0 to 1.0)
        """
        try:
            base_score = 0.0
            
            # Signal direction alignment
            if primary_signal == higher_signal:
                if primary_signal in ["bullish", "bearish"]:
                    base_score = 0.8  # Strong alignment for directional signals
                else:
                    base_score = 0.5  # Neutral alignment
            elif (primary_signal == "neutral" and higher_signal in ["bullish", "bearish"]) or \
                 (higher_signal == "neutral" and primary_signal in ["bullish", "bearish"]):
                base_score = 0.6  # Partial alignment
            else:
                base_score = 0.2  # Contradictory signals
            
            # Adjust based on signal strength
            strength_bonus = 0.0
            
            # Check trend strength in higher timeframe
            if len(higher_df) > 0 and 'adx' in higher_df.columns:
                higher_adx = higher_df.iloc[-1]['adx']
                if higher_adx > 30:
                    strength_bonus += 0.1
                elif higher_adx > 25:
                    strength_bonus += 0.05
            
            # Check momentum alignment
            if len(primary_df) > 0 and len(higher_df) > 0:
                if 'rsi' in primary_df.columns and 'rsi' in higher_df.columns:
                    primary_rsi = primary_df.iloc[-1]['rsi']
                    higher_rsi = higher_df.iloc[-1]['rsi']
                    
                    # RSI alignment bonus
                    if (primary_rsi > 50 and higher_rsi > 50) or (primary_rsi < 50 and higher_rsi < 50):
                        strength_bonus += 0.05
                
                if 'macd' in primary_df.columns and 'macd' in higher_df.columns:
                    primary_macd = primary_df.iloc[-1]['macd']
                    primary_signal_line = primary_df.iloc[-1]['macd_signal']
                    higher_macd = higher_df.iloc[-1]['macd']
                    higher_signal_line = higher_df.iloc[-1]['macd_signal']
                    
                    # MACD alignment bonus
                    primary_macd_bullish = primary_macd > primary_signal_line
                    higher_macd_bullish = higher_macd > higher_signal_line
                    
                    if primary_macd_bullish == higher_macd_bullish:
                        strength_bonus += 0.05
            
            final_score = min(1.0, base_score + strength_bonus)
            
            self.logger.debug(f"Alignment calculation: base={base_score:.3f}, "
                            f"strength_bonus={strength_bonus:.3f}, final={final_score:.3f}")
            
            return final_score
            
        except Exception as e:
            self.logger.error(f"Error calculating alignment score: {e}")
            return 0.0
    
    def _get_confirmation_level(self, alignment_score: float, primary_signal: str, higher_signal: str) -> str:
        """
        Determine confirmation level based on alignment score and signals
        
        Args:
            alignment_score: Calculated alignment score
            primary_signal: Primary timeframe signal
            higher_signal: Higher timeframe signal
            
        Returns:
            Confirmation level string
        """
        if alignment_score >= 0.8:
            return "strong"
        elif alignment_score >= 0.6:
            return "moderate"
        elif alignment_score >= 0.4:
            return "weak"
        else:
            return "contradictory"
    
    def _identify_alignment_factors(self, primary_df: pd.DataFrame, higher_df: pd.DataFrame,
                                  primary_signal: str, higher_signal: str) -> List[str]:
        """
        Identify factors contributing to timeframe alignment
        
        Args:
            primary_df: Primary timeframe data
            higher_df: Higher timeframe data
            primary_signal: Primary timeframe signal
            higher_signal: Higher timeframe signal
            
        Returns:
            List of contributing factors
        """
        factors = []
        
        try:
            # Signal direction factor
            if primary_signal == higher_signal:
                if primary_signal in ["bullish", "bearish"]:
                    factors.append(f"directional_alignment_{primary_signal}")
                else:
                    factors.append("neutral_alignment")
            else:
                factors.append("signal_divergence")
            
            # Trend strength factor
            if len(higher_df) > 0 and 'adx' in higher_df.columns:
                higher_adx = higher_df.iloc[-1]['adx']
                if higher_adx > 30:
                    factors.append("strong_higher_trend")
                elif higher_adx > 25:
                    factors.append("moderate_higher_trend")
                else:
                    factors.append("weak_higher_trend")
            
            # EMA alignment factor
            if (len(primary_df) > 0 and len(higher_df) > 0 and 
                'ema_20' in primary_df.columns and 'ema_50' in primary_df.columns and
                'ema_20' in higher_df.columns and 'ema_50' in higher_df.columns):
                
                primary_ema_bullish = primary_df.iloc[-1]['ema_20'] > primary_df.iloc[-1]['ema_50']
                higher_ema_bullish = higher_df.iloc[-1]['ema_20'] > higher_df.iloc[-1]['ema_50']
                
                if primary_ema_bullish == higher_ema_bullish:
                    factors.append("ema_alignment")
                else:
                    factors.append("ema_divergence")
            
            # Momentum alignment factor
            if (len(primary_df) > 0 and len(higher_df) > 0 and 
                'rsi' in primary_df.columns and 'rsi' in higher_df.columns):
                
                primary_rsi = primary_df.iloc[-1]['rsi']
                higher_rsi = higher_df.iloc[-1]['rsi']
                
                if (primary_rsi > 50 and higher_rsi > 50) or (primary_rsi < 50 and higher_rsi < 50):
                    factors.append("momentum_alignment")
                else:
                    factors.append("momentum_divergence")
            
            return factors
            
        except Exception as e:
            self.logger.error(f"Error identifying alignment factors: {e}")
            return ["analysis_error"]
    
    def calculate_alignment_score(self, alignment: AlignmentResult) -> float:
        """
        Calculate final alignment score for use in signal confidence
        
        Args:
            alignment: AlignmentResult from timeframe analysis
            
        Returns:
            Final alignment score (0.0 to 1.0)
        """
        return alignment.alignment_score
    
    def should_confirm_signal(self, alignment: AlignmentResult, signal_type: str) -> bool:
        """
        Determine if higher timeframe confirms the primary signal
        
        Args:
            alignment: AlignmentResult from timeframe analysis
            signal_type: 'buy' or 'sell' signal type
            
        Returns:
            True if signal is confirmed by higher timeframe
        """
        if not self.enable_mtf:
            return True  # No MTF filtering if disabled
        
        # Check if alignment meets minimum threshold
        if alignment.alignment_score < self.alignment_threshold:
            self.logger.info(f"MTF confirmation failed: alignment score {alignment.alignment_score:.3f} "
                           f"below threshold {self.alignment_threshold:.3f}")
            return False
        
        # Check for contradictory signals
        if alignment.confirmation_level == "contradictory":
            self.logger.info(f"MTF confirmation failed: contradictory signals detected")
            return False
        
        # Check signal direction alignment
        expected_higher_signal = "bullish" if signal_type.lower() == "buy" else "bearish"
        
        if alignment.higher_signal == expected_higher_signal:
            self.logger.info(f"MTF confirmation passed: {alignment.confirmation_level} alignment "
                           f"({alignment.alignment_score:.3f})")
            return True
        elif alignment.higher_signal == "neutral":
            # Neutral higher timeframe is acceptable with moderate alignment
            if alignment.alignment_score >= 0.5:
                self.logger.info(f"MTF confirmation passed: neutral higher timeframe with "
                               f"moderate alignment ({alignment.alignment_score:.3f})")
                return True
        
        self.logger.info(f"MTF confirmation failed: higher timeframe signal '{alignment.higher_signal}' "
                       f"does not support {signal_type} signal")
        return False
    
    def get_timeframe_name(self, timeframe: int) -> str:
        """
        Get human-readable name for MT5 timeframe constant
        
        Args:
            timeframe: MT5 timeframe constant
            
        Returns:
            Human-readable timeframe name
        """
        return self.timeframe_names.get(timeframe, str(timeframe))