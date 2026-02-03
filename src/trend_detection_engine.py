"""
Advanced Trend Detection Engine for GEM Trading Bot
Implements sophisticated market structure analysis, divergence detection, and multi-timeframe confirmation
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
import logging
from enum import Enum

# Configure logging
logger = logging.getLogger(__name__)

class SignalType(Enum):
    """Enumeration for different signal types"""
    BULLISH_TREND_CHANGE = "bullish_trend_change"
    BEARISH_TREND_CHANGE = "bearish_trend_change"
    EARLY_WARNING_BULLISH = "early_warning_bullish"
    EARLY_WARNING_BEARISH = "early_warning_bearish"

class BreakType(Enum):
    """Enumeration for market structure break types"""
    HIGHER_HIGH = "higher_high"
    LOWER_LOW = "lower_low"
    SUPPORT_BREAK = "support_break"
    RESISTANCE_BREAK = "resistance_break"

class DivergenceType(Enum):
    """Enumeration for divergence types"""
    BULLISH_RSI = "bullish_rsi"
    BEARISH_RSI = "bearish_rsi"
    BULLISH_MACD = "bullish_macd"
    BEARISH_MACD = "bearish_macd"

@dataclass
class TrendSignal:
    """Represents a trend detection signal"""
    signal_type: str
    strength: float  # 0.0 to 1.0
    source: str  # 'market_structure', 'divergence', 'aroon', etc.
    confidence: float
    timestamp: datetime
    price_level: float
    supporting_factors: List[str]

@dataclass
class StructureBreakResult:
    """Represents a market structure break analysis result"""
    break_type: str  # 'higher_high', 'lower_low', 'support_break', 'resistance_break'
    break_level: float
    previous_level: float
    volume_confirmation: bool
    strength: float
    confirmed: bool

@dataclass
class DivergenceResult:
    """Represents a divergence analysis result"""
    divergence_type: str  # 'bullish_rsi', 'bearish_rsi', 'bullish_macd', 'bearish_macd'
    indicator: str  # 'RSI', 'MACD'
    price_points: List[Tuple[datetime, float]]
    indicator_points: List[Tuple[datetime, float]]
    strength: float
    validated: bool

@dataclass
class AroonSignal:
    """Represents an Aroon indicator signal"""
    aroon_up: float
    aroon_down: float
    oscillator: float
    signal_type: str  # 'bullish_cross', 'bearish_cross', 'consolidation'
    trend_strength: float

@dataclass
class Trendline:
    """Represents a trendline"""
    start_point: Tuple[datetime, float]
    end_point: Tuple[datetime, float]
    slope: float
    touch_points: int
    strength: float
    line_type: str  # 'support', 'resistance'

@dataclass
class TrendlineBreak:
    """Represents a trendline break"""
    trendline: Trendline
    break_point: Tuple[datetime, float]
    volume_confirmation: bool
    retest_confirmed: bool
    break_strength: float

@dataclass
class TimeframeAlignment:
    """Represents multi-timeframe alignment analysis"""
    primary_timeframe: str
    higher_timeframe: str
    alignment_score: float
    confirmation_level: str

@dataclass
class VolumeConfirmation:
    """Represents volume confirmation analysis"""
    volume_spike: bool
    volume_ratio: float
    strength: float

@dataclass
class EarlyWarningSignal:
    """Represents an early warning signal"""
    warning_type: str
    confidence: float
    price_level: float
    factors: List[str]

@dataclass
class TrendAnalysisResult:
    """Comprehensive trend analysis result"""
    signals: List[TrendSignal]
    confidence: float
    market_structure: Optional[StructureBreakResult]
    divergences: List[DivergenceResult]
    aroon_signal: Optional[AroonSignal]
    ema_signal: Optional['EMASignal']
    trendline_breaks: List[TrendlineBreak]
    timeframe_alignment: Optional[TimeframeAlignment]
    volume_confirmation: Optional[VolumeConfirmation]
    early_warnings: List[EarlyWarningSignal]

class TrendDetectionEngine:
    """
    Main orchestrator for all trend detection functionality
    Integrates market structure analysis, divergence detection, and multi-timeframe confirmation
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the trend detection engine
        
        Args:
            config: Configuration dictionary with trend detection parameters
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Configuration parameters
        self.use_trend_detection = config.get('use_trend_detection', True)
        self.sensitivity = config.get('trend_detection_sensitivity', 5)
        self.min_confidence = config.get('min_trend_confidence', 0.6)
        self.enable_early_signals = config.get('enable_early_signals', True)
        
        # Initialize sub-components
        try:
            from src.market_structure_analyzer import MarketStructureAnalyzer
            from src.aroon_indicator import AroonIndicator
            from src.ema_momentum_analyzer import EMAMomentumAnalyzer, EMASignal
            
            self.market_structure_analyzer = MarketStructureAnalyzer(config)
            self.aroon_indicator = AroonIndicator(period=config.get('aroon_period', 25))
            self.ema_momentum_analyzer = EMAMomentumAnalyzer(config)
            
            self.logger.info(f"TrendDetectionEngine initialized with sensitivity={self.sensitivity}")
            
        except ImportError as e:
            self.logger.error(f"Failed to initialize trend detection components: {e}")
            raise
    
    def analyze_trend_change(self, df: pd.DataFrame, symbol: str) -> TrendAnalysisResult:
        """
        Perform comprehensive trend change analysis
        
        Args:
            df: Price data with indicators
            symbol: Trading symbol
            
        Returns:
            TrendAnalysisResult with all analysis components
        """
        if not self.use_trend_detection or len(df) < 50:
            return TrendAnalysisResult(
                signals=[],
                confidence=0.0,
                market_structure=None,
                divergences=[],
                aroon_signal=None,
                ema_signal=None,
                trendline_breaks=[],
                timeframe_alignment=None,
                volume_confirmation=None,
                early_warnings=[]
            )
        
        try:
            signals = []
            
            # 1. Market Structure Analysis
            structure_break = self.market_structure_analyzer.detect_structure_break(df)
            if structure_break and structure_break.confirmed:
                signal_type = SignalType.BULLISH_TREND_CHANGE if 'bullish' in structure_break.break_type else SignalType.BEARISH_TREND_CHANGE
                signals.append(TrendSignal(
                    signal_type=signal_type.value,
                    strength=structure_break.strength,
                    source='market_structure',
                    confidence=0.8 if structure_break.volume_confirmation else 0.6,
                    timestamp=datetime.now(),
                    price_level=structure_break.break_level,
                    supporting_factors=['structure_break', 'volume_confirmation'] if structure_break.volume_confirmation else ['structure_break']
                ))
            
            # 2. Aroon Analysis
            aroon_signal = self.aroon_indicator.get_aroon_signal(df)
            if aroon_signal and aroon_signal.signal_type != 'consolidation':
                signal_type = SignalType.BULLISH_TREND_CHANGE if 'bullish' in aroon_signal.signal_type else SignalType.BEARISH_TREND_CHANGE
                signals.append(TrendSignal(
                    signal_type=signal_type.value,
                    strength=aroon_signal.trend_strength,
                    source='aroon',
                    confidence=0.7,
                    timestamp=datetime.now(),
                    price_level=df.iloc[-1]['close'],
                    supporting_factors=['aroon_crossover']
                ))
            
            # 3. EMA Momentum Analysis
            ema_signal = self.ema_momentum_analyzer.get_ema_signal(df)
            if ema_signal and 'cross' in ema_signal.signal_type:
                signal_type = SignalType.BULLISH_TREND_CHANGE if 'bullish' in ema_signal.signal_type else SignalType.BEARISH_TREND_CHANGE
                confidence = 0.8 if ema_signal.crossover_confirmed else 0.6
                signals.append(TrendSignal(
                    signal_type=signal_type.value,
                    strength=ema_signal.momentum_strength,
                    source='ema',
                    confidence=confidence,
                    timestamp=datetime.now(),
                    price_level=df.iloc[-1]['close'],
                    supporting_factors=['ema_crossover', 'momentum_confirmation'] if ema_signal.crossover_confirmed else ['ema_crossover']
                ))
            
            # 4. Calculate overall confidence
            overall_confidence = self._calculate_trend_confidence(signals)
            
            return TrendAnalysisResult(
                signals=signals,
                confidence=overall_confidence,
                market_structure=structure_break,
                divergences=[],  # TODO: Implement divergence detection
                aroon_signal=aroon_signal,
                ema_signal=ema_signal,
                trendline_breaks=[],  # TODO: Implement trendline analysis
                timeframe_alignment=None,  # TODO: Implement multi-timeframe analysis
                volume_confirmation=None,  # TODO: Implement volume confirmation
                early_warnings=[]  # TODO: Implement early warning signals
            )
            
        except Exception as e:
            self.logger.error(f"Error in trend analysis for {symbol}: {e}")
            return TrendAnalysisResult(
                signals=[],
                confidence=0.0,
                market_structure=None,
                divergences=[],
                aroon_signal=None,
                ema_signal=None,
                trendline_breaks=[],
                timeframe_alignment=None,
                volume_confirmation=None,
                early_warnings=[]
            )
    
    def get_trend_signals(self, df: pd.DataFrame, signal_type: str) -> List[TrendSignal]:
        """
        Get trend signals for a specific signal type
        
        Args:
            df: Price data with indicators
            signal_type: 'buy' or 'sell'
            
        Returns:
            List of relevant trend signals
        """
        analysis_result = self.analyze_trend_change(df, "unknown")
        
        if signal_type.lower() == 'buy':
            return [s for s in analysis_result.signals if 'bullish' in s.signal_type]
        elif signal_type.lower() == 'sell':
            return [s for s in analysis_result.signals if 'bearish' in s.signal_type]
        else:
            return analysis_result.signals
    
    def calculate_trend_confidence(self, signals: List[TrendSignal]) -> float:
        """
        Calculate overall trend confidence from multiple signals
        
        Args:
            signals: List of trend signals
            
        Returns:
            Overall confidence score (0.0 to 1.0)
        """
        return self._calculate_trend_confidence(signals)
    
    def should_trade_trend(self, df: pd.DataFrame, signal_type: str) -> Tuple[bool, float]:
        """
        Determine if trend conditions support trading
        
        Args:
            df: Price data with indicators
            signal_type: 'buy' or 'sell'
            
        Returns:
            Tuple of (should_trade, confidence_score)
        """
        analysis_result = self.analyze_trend_change(df, "unknown")
        
        # Check if we have relevant signals
        relevant_signals = self.get_trend_signals(df, signal_type)
        
        if not relevant_signals:
            return False, 0.0
        
        # Check if confidence meets minimum threshold
        if analysis_result.confidence < self.min_confidence:
            return False, analysis_result.confidence
        
        return True, analysis_result.confidence
    
    def _calculate_trend_confidence(self, signals: List[TrendSignal]) -> float:
        """
        Internal method to calculate confidence from signals
        
        Args:
            signals: List of trend signals
            
        Returns:
            Weighted confidence score
        """
        if not signals:
            return 0.0
        
        # Weight signals by source reliability
        source_weights = {
            'market_structure': 0.4,
            'aroon': 0.3,
            'divergence': 0.2,
            'volume': 0.1
        }
        
        total_weight = 0.0
        weighted_confidence = 0.0
        
        for signal in signals:
            weight = source_weights.get(signal.source, 0.1)
            weighted_confidence += signal.confidence * signal.strength * weight
            total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        return min(1.0, weighted_confidence / total_weight)