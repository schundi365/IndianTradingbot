"""
ML Integration Module
Integrates ML signals, sentiment analysis, and pattern recognition with the trading bot
"""

import logging
from typing import Dict, List, Tuple, Optional
import numpy as np

from src.ml_signal_generator import MLSignalGenerator
from src.sentiment_analyzer import SentimentAnalyzer
from src.pattern_recognition import PatternRecognition


class MLIntegration:
    """
    Integrates machine learning components with trading bot
    Combines ML signals, sentiment, and patterns for enhanced decision making
    """
    
    def __init__(self, config: Dict, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.config = config
        
        # Initialize ML components
        self.ml_generator = MLSignalGenerator(logger=self.logger)
        self.sentiment_analyzer = SentimentAnalyzer(logger=self.logger)
        self.pattern_recognition = PatternRecognition(logger=self.logger)
        
        # Configuration
        self.ml_enabled = config.get('ml_enabled', False)
        self.sentiment_enabled = config.get('sentiment_enabled', False)
        self.pattern_enabled = config.get('pattern_enabled', True)
        
        # Confidence thresholds
        self.ml_min_confidence = config.get('ml_min_confidence', 0.6)
        
        # Signal weights
        self.technical_weight = config.get('technical_weight', 0.4)
        self.ml_weight = config.get('ml_weight', 0.3)
        self.sentiment_weight = config.get('sentiment_weight', 0.15)
        self.pattern_weight = config.get('pattern_weight', 0.15)
        
        # Normalize weights
        total_weight = self.technical_weight + self.ml_weight + self.sentiment_weight + self.pattern_weight
        if total_weight > 0:
            self.technical_weight /= total_weight
            self.ml_weight /= total_weight
            self.sentiment_weight /= total_weight
            self.pattern_weight /= total_weight
        
        self.logger.info("ML Integration initialized")
        self.logger.info(f"ML Min Confidence: {self.ml_min_confidence:.2f}")
        self.logger.info(f"Weights - Technical: {self.technical_weight:.2f}, ML: {self.ml_weight:.2f}, "
                        f"Sentiment: {self.sentiment_weight:.2f}, Pattern: {self.pattern_weight:.2f}")
    
    def get_enhanced_signal(self, symbol: str, market_data: Dict, 
                           technical_signal: str, technical_confidence: float = 0.7,
                           news_data: Optional[List[str]] = None) -> Dict:
        """
        Get enhanced trading signal combining all ML components
        
        Args:
            symbol: Trading symbol
            market_data: Market data with OHLCV and indicators
            technical_signal: Signal from technical analysis
            technical_confidence: Confidence of technical signal
            news_data: Optional news headlines for sentiment
            
        Returns:
            Dictionary with enhanced signal and analysis
        """
        self.logger.info("=" * 80)
        self.logger.info(f"🔮 ML INTEGRATION - Enhanced Signal Analysis for {symbol}")
        self.logger.info("=" * 80)
        
        signals = {
            'technical': {'signal': technical_signal, 'confidence': technical_confidence},
            'ml': {'signal': 'NEUTRAL', 'confidence': 0.0},
            'sentiment': {'signal': 'NEUTRAL', 'confidence': 0.0},
            'pattern': {'signal': 'NEUTRAL', 'confidence': 0.0},
            'combined': {'signal': 'NEUTRAL', 'confidence': 0.0}
        }
        
        try:
            # Log technical signal
            self.logger.info(f"   📊 Technical Analysis:")
            self.logger.info(f"      Signal: {technical_signal}")
            self.logger.info(f"      Confidence: {technical_confidence:.4f} ({technical_confidence*100:.1f}%)")
            
            # Get ML signal
            if self.ml_enabled and self.ml_generator.is_trained:
                self.logger.info(f"   🤖 ML Analysis: ENABLED")
                ml_signal, ml_confidence = self._get_ml_signal(market_data)
                signals['ml'] = {'signal': ml_signal, 'confidence': ml_confidence}
            else:
                if self.ml_enabled:
                    self.logger.warning(f"   ⚠️ ML Analysis: ENABLED but model not trained")
                else:
                    self.logger.info(f"   ⚪ ML Analysis: DISABLED")
            
            # Get sentiment signal
            if self.sentiment_enabled:
                self.logger.info(f"   💭 Sentiment Analysis: ENABLED")
                sentiment_signal, sentiment_confidence = self._get_sentiment_signal(symbol, news_data)
                signals['sentiment'] = {'signal': sentiment_signal, 'confidence': sentiment_confidence}
            else:
                self.logger.info(f"   ⚪ Sentiment Analysis: DISABLED")
            
            # Get pattern signal
            if self.pattern_enabled:
                self.logger.info(f"   📈 Pattern Recognition: ENABLED")
                pattern_signal, pattern_confidence = self._get_pattern_signal(market_data)
                signals['pattern'] = {'signal': pattern_signal, 'confidence': pattern_confidence}
            else:
                self.logger.info(f"   ⚪ Pattern Recognition: DISABLED")
            
            # Combine all signals
            self.logger.info(f"   🔄 Combining signals with weighted voting...")
            combined_signal, combined_confidence = self._combine_signals(signals)
            signals['combined'] = {'signal': combined_signal, 'confidence': combined_confidence}
            
            # Add analysis details
            signals['analysis'] = self._generate_analysis(signals)
            
            self.logger.info("=" * 80)
            self.logger.info(f"✅ ML INTEGRATION - Enhanced Signal: {combined_signal} (Confidence: {combined_confidence:.4f})")
            self.logger.info("=" * 80)
            
            return signals
            
        except Exception as e:
            self.logger.error(f"❌ ML INTEGRATION - Error getting enhanced signal: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return signals
    
    def _get_ml_signal(self, market_data: Dict) -> Tuple[str, float]:
        """Get signal from ML model with confidence filtering"""
        try:
            features = self.ml_generator.extract_features(market_data)
            signal, confidence = self.ml_generator.predict_signal(features)
            
            # Apply confidence filtering
            if confidence < self.ml_min_confidence:
                self.logger.info(f"      ⚠️ ML signal filtered: confidence {confidence:.3f} < threshold {self.ml_min_confidence:.3f}")
                return 'NEUTRAL', 0.0
            
            self.logger.info(f"      ✅ ML signal accepted: {signal} with confidence {confidence:.3f}")
            return signal, confidence
        except Exception as e:
            self.logger.error(f"Error getting ML signal: {e}")
            return 'NEUTRAL', 0.0
    
    def _get_sentiment_signal(self, symbol: str, news_data: Optional[List[str]]) -> Tuple[str, float]:
        """Get signal from sentiment analysis"""
        try:
            sentiment = self.sentiment_analyzer.get_market_sentiment(symbol, news_data)
            signal, strength = self.sentiment_analyzer.get_sentiment_signal(sentiment)
            return signal, strength
        except Exception as e:
            self.logger.error(f"Error getting sentiment signal: {e}")
            return 'NEUTRAL', 0.0
    
    def _get_pattern_signal(self, market_data: Dict) -> Tuple[str, float]:
        """Get signal from pattern recognition"""
        try:
            ohlc_data = {
                'open': market_data.get('open', []),
                'high': market_data.get('high', []),
                'low': market_data.get('low', []),
                'close': market_data.get('close', [])
            }
            
            patterns = self.pattern_recognition.detect_all_patterns(ohlc_data)
            signal, confidence = self.pattern_recognition.get_pattern_signal(patterns)
            return signal, confidence
        except Exception as e:
            self.logger.error(f"Error getting pattern signal: {e}")
            return 'NEUTRAL', 0.0
    
    def _combine_signals(self, signals: Dict) -> Tuple[str, float]:
        """
        Combine all signals using weighted voting
        
        Args:
            signals: Dictionary of all signals
            
        Returns:
            Tuple of (combined_signal, combined_confidence)
        """
        self.logger.info(f"   🔢 WEIGHTED SIGNAL COMBINATION:")
        self.logger.info(f"      Weights: Technical={self.technical_weight:.2f}, ML={self.ml_weight:.2f}, "
                        f"Sentiment={self.sentiment_weight:.2f}, Pattern={self.pattern_weight:.2f}")
        
        # Convert signals to numeric scores
        signal_map = {'BUY': 1, 'NEUTRAL': 0, 'SELL': -1}
        
        # Calculate weighted score
        weighted_score = 0
        total_confidence = 0
        
        components = [
            ('technical', self.technical_weight),
            ('ml', self.ml_weight),
            ('sentiment', self.sentiment_weight),
            ('pattern', self.pattern_weight)
        ]
        
        self.logger.info(f"   📊 Component Contributions:")
        for component, weight in components:
            if component in signals:
                signal = signals[component]['signal']
                confidence = signals[component]['confidence']
                
                score = signal_map.get(signal, 0)
                contribution = score * weight * confidence
                weighted_score += contribution
                total_confidence += weight * confidence
                
                self.logger.info(f"      {component.capitalize()}: {signal} (conf={confidence:.3f}, weight={weight:.2f}) → contribution={contribution:.4f}")
        
        # Normalize
        if total_confidence > 0:
            final_score = weighted_score / total_confidence
        else:
            final_score = 0
        
        self.logger.info(f"   🎯 Weighted Score: {final_score:.4f}")
        self.logger.info(f"   📊 Total Confidence: {total_confidence:.4f}")
        
        # Convert back to signal
        if final_score > 0.3:
            combined_signal = 'BUY'
            reason = f"Final score {final_score:.3f} > 0.3 threshold"
        elif final_score < -0.3:
            combined_signal = 'SELL'
            reason = f"Final score {final_score:.3f} < -0.3 threshold"
        else:
            combined_signal = 'NEUTRAL'
            reason = f"Final score {final_score:.3f} in neutral zone (-0.3 to 0.3)"
        
        # Calculate combined confidence
        combined_confidence = min(abs(final_score), 1.0)
        
        self.logger.info(f"   ✅ Combined Signal: {combined_signal}")
        self.logger.info(f"      Reason: {reason}")
        self.logger.info(f"      Confidence: {combined_confidence:.4f}")
        
        return combined_signal, combined_confidence
    
    def _generate_analysis(self, signals: Dict) -> str:
        """Generate human-readable analysis"""
        analysis_parts = []
        
        # Technical analysis
        tech = signals['technical']
        analysis_parts.append(f"Technical: {tech['signal']} ({tech['confidence']:.2f})")
        
        # ML analysis
        if self.ml_enabled:
            ml = signals['ml']
            analysis_parts.append(f"ML: {ml['signal']} ({ml['confidence']:.2f})")
        
        # Sentiment analysis
        if self.sentiment_enabled:
            sent = signals['sentiment']
            analysis_parts.append(f"Sentiment: {sent['signal']} ({sent['confidence']:.2f})")
        
        # Pattern analysis
        if self.pattern_enabled:
            pat = signals['pattern']
            analysis_parts.append(f"Pattern: {pat['signal']} ({pat['confidence']:.2f})")
        
        # Combined
        combined = signals['combined']
        analysis_parts.append(f"Combined: {combined['signal']} ({combined['confidence']:.2f})")
        
        return " | ".join(analysis_parts)
    
    def should_trade(self, enhanced_signals: Dict, min_confidence: float = 0.6) -> bool:
        """
        Determine if trade should be executed based on enhanced signals
        
        Args:
            enhanced_signals: Enhanced signal dictionary
            min_confidence: Minimum confidence threshold
            
        Returns:
            True if trade should be executed
        """
        combined = enhanced_signals.get('combined', {})
        signal = combined.get('signal', 'NEUTRAL')
        confidence = combined.get('confidence', 0.0)
        
        # Don't trade on neutral signals
        if signal == 'NEUTRAL':
            self.logger.info("   ❌ Trade rejected: Combined signal is NEUTRAL")
            return False
        
        # Check confidence threshold
        if confidence < min_confidence:
            self.logger.info(f"   ❌ Trade rejected: Confidence {confidence:.4f} < threshold {min_confidence:.4f}")
            return False
        
        # Check signal agreement (at least 2 out of active components agree)
        # Only count components that are enabled and not NEUTRAL
        agreement_count = 0
        active_components = 0
        
        for component in ['technical', 'ml', 'pattern', 'sentiment']:
            if component in enhanced_signals:
                component_signal = enhanced_signals[component].get('signal', 'NEUTRAL')
                component_confidence = enhanced_signals[component].get('confidence', 0.0)
                
                # Only count if component is active (not NEUTRAL and has confidence)
                if component_signal != 'NEUTRAL' and component_confidence > 0:
                    active_components += 1
                    if component_signal == signal:
                        agreement_count += 1
        
        # Need at least 2 active components agreeing
        # If only 1 active component, allow it (edge case)
        if active_components <= 1:
            self.logger.info(f"   ✅ Trade approved: Only {active_components} active component(s)")
            return True
        
        if agreement_count >= 2:
            self.logger.info(f"   ✅ Trade approved: {agreement_count}/{active_components} components agree")
            return True
        else:
            self.logger.info(f"   ❌ Trade rejected: Only {agreement_count}/{active_components} components agree (need 2+)")
            return False
    
    def get_signal_strength_multiplier(self, enhanced_signals: Dict) -> float:
        """
        Get position size multiplier based on signal strength
        
        Args:
            enhanced_signals: Enhanced signal dictionary
            
        Returns:
            Multiplier for position size (0.5 to 1.5)
        """
        combined_confidence = enhanced_signals.get('combined', {}).get('confidence', 0.5)
        
        # Map confidence to multiplier
        # 0.5 confidence = 0.75x position
        # 0.7 confidence = 1.0x position
        # 0.9+ confidence = 1.25x position
        
        if combined_confidence < 0.5:
            return 0.5
        elif combined_confidence < 0.7:
            return 0.75
        elif combined_confidence < 0.85:
            return 1.0
        else:
            return 1.25
    
    def train_ml_model(self, historical_data, labels):
        """Train the ML model with historical data"""
        if self.ml_enabled:
            return self.ml_generator.train_model(historical_data, labels)
        return False
    
    def update_config(self, new_config: Dict):
        """Update configuration"""
        self.config.update(new_config)
        
        self.ml_enabled = self.config.get('ml_enabled', self.ml_enabled)
        self.sentiment_enabled = self.config.get('sentiment_enabled', self.sentiment_enabled)
        self.pattern_enabled = self.config.get('pattern_enabled', self.pattern_enabled)
        
        self.logger.info("ML Integration configuration updated")
