"""
Advanced Pattern Recognition Module
Uses ML and statistical methods to detect chart patterns
"""

import numpy as np
import logging
from typing import Dict, List, Tuple, Optional
from scipy.signal import find_peaks, argrelextrema
from scipy.stats import linregress


class PatternRecognition:
    """
    Advanced pattern recognition using ML and statistical methods
    Detects candlestick patterns, chart patterns, and price structures
    """
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        
        # Pattern confidence thresholds
        self.confidence_threshold = 0.6
        
        # Pattern definitions
        self.patterns = {
            'double_top': {'type': 'reversal', 'direction': 'bearish'},
            'double_bottom': {'type': 'reversal', 'direction': 'bullish'},
            'head_shoulders': {'type': 'reversal', 'direction': 'bearish'},
            'inverse_head_shoulders': {'type': 'reversal', 'direction': 'bullish'},
            'triangle_ascending': {'type': 'continuation', 'direction': 'bullish'},
            'triangle_descending': {'type': 'continuation', 'direction': 'bearish'},
            'flag_bullish': {'type': 'continuation', 'direction': 'bullish'},
            'flag_bearish': {'type': 'continuation', 'direction': 'bearish'},
            'wedge_rising': {'type': 'reversal', 'direction': 'bearish'},
            'wedge_falling': {'type': 'reversal', 'direction': 'bullish'},
        }
    
    def detect_all_patterns(self, ohlc_data: Dict) -> List[Dict]:
        """
        Detect all patterns in OHLC data
        
        Args:
            ohlc_data: Dictionary with 'open', 'high', 'low', 'close' arrays
            
        Returns:
            List of detected patterns with confidence scores
        """
        detected_patterns = []
        
        try:
            self.logger.info("🔍 PATTERN RECOGNITION - Starting pattern detection")
            
            # Extract price arrays
            high = np.array(ohlc_data.get('high', []))
            low = np.array(ohlc_data.get('low', []))
            close = np.array(ohlc_data.get('close', []))
            
            self.logger.info(f"   📊 Data Points: {len(close)} candles")
            
            if len(close) < 20:
                self.logger.warning(f"   ⚠️ Insufficient data: {len(close)} candles (minimum 20 required)")
                return detected_patterns
            
            # Detect various patterns
            self.logger.info(f"   🔎 Scanning for patterns...")
            
            patterns_to_check = [
                ('Double Top/Bottom', self.detect_double_top_bottom(high, low, close)),
                ('Head & Shoulders', self.detect_head_shoulders(high, low, close)),
                ('Triangles', self.detect_triangles(high, low, close)),
                ('Flags', self.detect_flags(high, low, close)),
                ('Wedges', self.detect_wedges(high, low, close)),
            ]
            
            # Flatten and filter patterns
            for pattern_type, pattern_list in patterns_to_check:
                if pattern_list:
                    self.logger.info(f"      ✅ {pattern_type}: Found {len(pattern_list)} pattern(s)")
                    for pattern in pattern_list:
                        self.logger.info(f"         - {pattern['name']}: {pattern['signal']} (confidence: {pattern['confidence']:.3f})")
                    detected_patterns.extend(pattern_list)
                else:
                    self.logger.info(f"      ⚪ {pattern_type}: None detected")
            
            # Sort by confidence
            detected_patterns.sort(key=lambda x: x.get('confidence', 0), reverse=True)
            
            if detected_patterns:
                self.logger.info(f"   ✅ Total patterns detected: {len(detected_patterns)}")
                self.logger.info(f"   🏆 Highest confidence pattern: {detected_patterns[0]['name']} ({detected_patterns[0]['confidence']:.3f})")
            else:
                self.logger.info(f"   ⚪ No patterns detected")
            
            return detected_patterns
            
        except Exception as e:
            self.logger.error(f"❌ PATTERN RECOGNITION - Error detecting patterns: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return []
    
    def detect_double_top_bottom(self, high: np.ndarray, low: np.ndarray, 
                                  close: np.ndarray) -> List[Dict]:
        """Detect double top and double bottom patterns"""
        patterns = []
        
        try:
            # Find peaks and troughs
            peaks, _ = find_peaks(high, distance=5)
            troughs, _ = find_peaks(-low, distance=5)
            
            # Check for double top
            if len(peaks) >= 2:
                for i in range(len(peaks) - 1):
                    peak1, peak2 = peaks[i], peaks[i + 1]
                    if abs(high[peak1] - high[peak2]) / high[peak1] < 0.02:  # Within 2%
                        confidence = 1 - abs(high[peak1] - high[peak2]) / high[peak1]
                        patterns.append({
                            'name': 'double_top',
                            'type': 'reversal',
                            'direction': 'bearish',
                            'confidence': confidence,
                            'start_index': peak1,
                            'end_index': peak2,
                            'signal': 'SELL'
                        })
            
            # Check for double bottom
            if len(troughs) >= 2:
                for i in range(len(troughs) - 1):
                    trough1, trough2 = troughs[i], troughs[i + 1]
                    if abs(low[trough1] - low[trough2]) / low[trough1] < 0.02:
                        confidence = 1 - abs(low[trough1] - low[trough2]) / low[trough1]
                        patterns.append({
                            'name': 'double_bottom',
                            'type': 'reversal',
                            'direction': 'bullish',
                            'confidence': confidence,
                            'start_index': trough1,
                            'end_index': trough2,
                            'signal': 'BUY'
                        })
            
        except Exception as e:
            self.logger.error(f"Error detecting double top/bottom: {e}")
        
        return patterns
    
    def detect_head_shoulders(self, high: np.ndarray, low: np.ndarray, 
                              close: np.ndarray) -> List[Dict]:
        """Detect head and shoulders patterns"""
        patterns = []
        
        try:
            peaks, _ = find_peaks(high, distance=5)
            
            if len(peaks) >= 3:
                for i in range(len(peaks) - 2):
                    left, head, right = peaks[i], peaks[i + 1], peaks[i + 2]
                    
                    # Check for head and shoulders
                    if (high[head] > high[left] and high[head] > high[right] and
                        abs(high[left] - high[right]) / high[left] < 0.03):
                        
                        confidence = 0.7 + 0.3 * (1 - abs(high[left] - high[right]) / high[left])
                        patterns.append({
                            'name': 'head_shoulders',
                            'type': 'reversal',
                            'direction': 'bearish',
                            'confidence': confidence,
                            'start_index': left,
                            'end_index': right,
                            'signal': 'SELL'
                        })
            
            # Check for inverse head and shoulders
            troughs, _ = find_peaks(-low, distance=5)
            
            if len(troughs) >= 3:
                for i in range(len(troughs) - 2):
                    left, head, right = troughs[i], troughs[i + 1], troughs[i + 2]
                    
                    if (low[head] < low[left] and low[head] < low[right] and
                        abs(low[left] - low[right]) / low[left] < 0.03):
                        
                        confidence = 0.7 + 0.3 * (1 - abs(low[left] - low[right]) / low[left])
                        patterns.append({
                            'name': 'inverse_head_shoulders',
                            'type': 'reversal',
                            'direction': 'bullish',
                            'confidence': confidence,
                            'start_index': left,
                            'end_index': right,
                            'signal': 'BUY'
                        })
            
        except Exception as e:
            self.logger.error(f"Error detecting head and shoulders: {e}")
        
        return patterns
    
    def detect_triangles(self, high: np.ndarray, low: np.ndarray, 
                        close: np.ndarray) -> List[Dict]:
        """Detect triangle patterns (ascending, descending, symmetrical)"""
        patterns = []
        
        try:
            if len(close) < 20:
                return patterns
            
            # Get recent data
            recent_high = high[-20:]
            recent_low = low[-20:]
            
            # Fit trendlines
            x = np.arange(len(recent_high))
            high_slope, _, _, _, _ = linregress(x, recent_high)
            low_slope, _, _, _, _ = linregress(x, recent_low)
            
            # Ascending triangle: flat top, rising bottom
            if abs(high_slope) < 0.001 and low_slope > 0.001:
                patterns.append({
                    'name': 'triangle_ascending',
                    'type': 'continuation',
                    'direction': 'bullish',
                    'confidence': 0.7,
                    'start_index': len(close) - 20,
                    'end_index': len(close) - 1,
                    'signal': 'BUY'
                })
            
            # Descending triangle: falling top, flat bottom
            elif high_slope < -0.001 and abs(low_slope) < 0.001:
                patterns.append({
                    'name': 'triangle_descending',
                    'type': 'continuation',
                    'direction': 'bearish',
                    'confidence': 0.7,
                    'start_index': len(close) - 20,
                    'end_index': len(close) - 1,
                    'signal': 'SELL'
                })
            
            # Symmetrical triangle: converging lines
            elif high_slope < -0.001 and low_slope > 0.001:
                patterns.append({
                    'name': 'triangle_symmetrical',
                    'type': 'continuation',
                    'direction': 'neutral',
                    'confidence': 0.6,
                    'start_index': len(close) - 20,
                    'end_index': len(close) - 1,
                    'signal': 'NEUTRAL'
                })
            
        except Exception as e:
            self.logger.error(f"Error detecting triangles: {e}")
        
        return patterns
    
    def detect_flags(self, high: np.ndarray, low: np.ndarray, 
                    close: np.ndarray) -> List[Dict]:
        """Detect flag patterns (bullish and bearish)"""
        patterns = []
        
        try:
            if len(close) < 30:
                return patterns
            
            # Look for strong trend followed by consolidation
            trend_period = close[-30:-10]
            flag_period = close[-10:]
            
            # Calculate trend strength
            trend_change = (trend_period[-1] - trend_period[0]) / trend_period[0]
            
            # Calculate consolidation (low volatility)
            flag_volatility = np.std(flag_period) / np.mean(flag_period)
            
            # Bullish flag: strong uptrend + consolidation
            if trend_change > 0.05 and flag_volatility < 0.02:
                patterns.append({
                    'name': 'flag_bullish',
                    'type': 'continuation',
                    'direction': 'bullish',
                    'confidence': 0.75,
                    'start_index': len(close) - 30,
                    'end_index': len(close) - 1,
                    'signal': 'BUY'
                })
            
            # Bearish flag: strong downtrend + consolidation
            elif trend_change < -0.05 and flag_volatility < 0.02:
                patterns.append({
                    'name': 'flag_bearish',
                    'type': 'continuation',
                    'direction': 'bearish',
                    'confidence': 0.75,
                    'start_index': len(close) - 30,
                    'end_index': len(close) - 1,
                    'signal': 'SELL'
                })
            
        except Exception as e:
            self.logger.error(f"Error detecting flags: {e}")
        
        return patterns
    
    def detect_wedges(self, high: np.ndarray, low: np.ndarray, 
                     close: np.ndarray) -> List[Dict]:
        """Detect wedge patterns (rising and falling)"""
        patterns = []
        
        try:
            if len(close) < 20:
                return patterns
            
            recent_high = high[-20:]
            recent_low = low[-20:]
            
            x = np.arange(len(recent_high))
            high_slope, _, _, _, _ = linregress(x, recent_high)
            low_slope, _, _, _, _ = linregress(x, recent_low)
            
            # Rising wedge: both lines rising, converging (bearish)
            if high_slope > 0 and low_slope > 0 and high_slope < low_slope * 1.5:
                patterns.append({
                    'name': 'wedge_rising',
                    'type': 'reversal',
                    'direction': 'bearish',
                    'confidence': 0.65,
                    'start_index': len(close) - 20,
                    'end_index': len(close) - 1,
                    'signal': 'SELL'
                })
            
            # Falling wedge: both lines falling, converging (bullish)
            elif high_slope < 0 and low_slope < 0 and low_slope < high_slope * 1.5:
                patterns.append({
                    'name': 'wedge_falling',
                    'type': 'reversal',
                    'direction': 'bullish',
                    'confidence': 0.65,
                    'start_index': len(close) - 20,
                    'end_index': len(close) - 1,
                    'signal': 'BUY'
                })
            
        except Exception as e:
            self.logger.error(f"Error detecting wedges: {e}")
        
        return patterns
    
    def get_pattern_signal(self, patterns: List[Dict]) -> Tuple[str, float]:
        """
        Get trading signal from detected patterns
        
        Args:
            patterns: List of detected patterns
            
        Returns:
            Tuple of (signal, confidence)
        """
        if not patterns:
            self.logger.info("   📊 PATTERN SIGNAL: NEUTRAL (no patterns detected)")
            return 'NEUTRAL', 0.0
        
        self.logger.info(f"   📊 PATTERN SIGNAL CALCULATION:")
        self.logger.info(f"      Analyzing {len(patterns)} detected pattern(s)")
        
        # Weight patterns by confidence
        buy_score = 0
        sell_score = 0
        total_confidence = 0
        
        for i, pattern in enumerate(patterns, 1):
            confidence = pattern.get('confidence', 0)
            signal = pattern.get('signal', 'NEUTRAL')
            pattern_name = pattern.get('name', 'unknown')
            
            self.logger.info(f"      Pattern {i}: {pattern_name}")
            self.logger.info(f"         Signal: {signal}, Confidence: {confidence:.3f}")
            
            if signal == 'BUY':
                buy_score += confidence
                self.logger.info(f"         → Adding {confidence:.3f} to BUY score")
            elif signal == 'SELL':
                sell_score += confidence
                self.logger.info(f"         → Adding {confidence:.3f} to SELL score")
            
            total_confidence += confidence
        
        if total_confidence == 0:
            self.logger.info("   ⚪ PATTERN SIGNAL: NEUTRAL (zero total confidence)")
            return 'NEUTRAL', 0.0
        
        self.logger.info(f"   📊 Score Summary:")
        self.logger.info(f"      BUY Score: {buy_score:.3f}")
        self.logger.info(f"      SELL Score: {sell_score:.3f}")
        self.logger.info(f"      Total Confidence: {total_confidence:.3f}")
        
        # Determine overall signal
        if buy_score > sell_score * 1.2:
            signal = 'BUY'
            confidence = buy_score / total_confidence
            self.logger.info(f"   ✅ PATTERN SIGNAL: {signal} (BUY score {buy_score:.3f} > SELL score {sell_score:.3f} * 1.2)")
        elif sell_score > buy_score * 1.2:
            signal = 'SELL'
            confidence = sell_score / total_confidence
            self.logger.info(f"   ✅ PATTERN SIGNAL: {signal} (SELL score {sell_score:.3f} > BUY score {buy_score:.3f} * 1.2)")
        else:
            signal = 'NEUTRAL'
            confidence = max(buy_score, sell_score) / total_confidence
            self.logger.info(f"   ⚪ PATTERN SIGNAL: {signal} (scores too close: BUY={buy_score:.3f}, SELL={sell_score:.3f})")
        
        self.logger.info(f"      Final Confidence: {confidence:.3f}")
        
        return signal, confidence
