"""
Sentiment Analysis Module
Analyzes market sentiment from news and social media
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import re

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    logging.warning("TextBlob not available. Install with: pip install textblob")


class SentimentAnalyzer:
    """
    Analyzes market sentiment from various sources
    Provides sentiment scores to enhance trading signals
    """
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.sentiment_cache = {}
        self.cache_duration = timedelta(hours=1)
        
        # Sentiment keywords
        self.bullish_keywords = [
            'bullish', 'rally', 'surge', 'breakout', 'uptrend', 'gains',
            'strong', 'positive', 'growth', 'momentum', 'buy', 'long'
        ]
        
        self.bearish_keywords = [
            'bearish', 'crash', 'decline', 'breakdown', 'downtrend', 'losses',
            'weak', 'negative', 'recession', 'sell', 'short', 'dump'
        ]
    
    def analyze_text(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment from text
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment scores
        """
        if not text:
            return {'polarity': 0.0, 'subjectivity': 0.0, 'score': 0.0}
        
        try:
            self.logger.info(f"   💭 SENTIMENT ANALYSIS - Analyzing text:")
            self.logger.info(f"      Text: \"{text[:100]}{'...' if len(text) > 100 else ''}\"")
            
            # Use TextBlob if available
            if TEXTBLOB_AVAILABLE:
                self.logger.info(f"      Method: TextBlob NLP")
                blob = TextBlob(text)
                polarity = blob.sentiment.polarity  # -1 to 1
                subjectivity = blob.sentiment.subjectivity  # 0 to 1
            else:
                self.logger.info(f"      Method: Keyword-based (TextBlob not available)")
                # Fallback to keyword-based analysis
                polarity = self._keyword_sentiment(text)
                subjectivity = 0.5
            
            # Calculate overall sentiment score
            score = self._calculate_sentiment_score(polarity, subjectivity)
            classification = self._classify_sentiment(score)
            
            self.logger.info(f"      Results:")
            self.logger.info(f"         Polarity: {polarity:.3f} (-1=negative, 0=neutral, 1=positive)")
            self.logger.info(f"         Subjectivity: {subjectivity:.3f} (0=objective, 1=subjective)")
            self.logger.info(f"         Weighted Score: {score:.3f}")
            self.logger.info(f"         Classification: {classification}")
            
            return {
                'polarity': polarity,
                'subjectivity': subjectivity,
                'score': score,
                'classification': classification
            }
            
        except Exception as e:
            self.logger.error(f"❌ SENTIMENT ANALYSIS - Error analyzing text sentiment: {e}")
            return {'polarity': 0.0, 'subjectivity': 0.0, 'score': 0.0}
    
    def _keyword_sentiment(self, text: str) -> float:
        """
        Calculate sentiment based on keywords
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment score (-1 to 1)
        """
        text_lower = text.lower()
        
        bullish_count = sum(1 for keyword in self.bullish_keywords if keyword in text_lower)
        bearish_count = sum(1 for keyword in self.bearish_keywords if keyword in text_lower)
        
        total = bullish_count + bearish_count
        if total == 0:
            return 0.0
        
        return (bullish_count - bearish_count) / total
    
    def _calculate_sentiment_score(self, polarity: float, subjectivity: float) -> float:
        """
        Calculate weighted sentiment score
        
        Args:
            polarity: Sentiment polarity (-1 to 1)
            subjectivity: Text subjectivity (0 to 1)
            
        Returns:
            Weighted sentiment score
        """
        # Weight polarity by objectivity (1 - subjectivity)
        # More objective statements carry more weight
        objectivity = 1 - subjectivity
        weighted_score = polarity * (0.5 + 0.5 * objectivity)
        
        return weighted_score
    
    def _classify_sentiment(self, score: float) -> str:
        """
        Classify sentiment into categories
        
        Args:
            score: Sentiment score
            
        Returns:
            Classification string
        """
        if score > 0.3:
            return 'BULLISH'
        elif score < -0.3:
            return 'BEARISH'
        else:
            return 'NEUTRAL'
    
    def analyze_news_headlines(self, headlines: List[str]) -> Dict[str, any]:
        """
        Analyze sentiment from multiple news headlines
        
        Args:
            headlines: List of news headlines
            
        Returns:
            Aggregated sentiment analysis
        """
        if not headlines:
            self.logger.info("   💭 SENTIMENT ANALYSIS - No headlines provided")
            return {
                'average_score': 0.0,
                'classification': 'NEUTRAL',
                'confidence': 0.0,
                'headline_count': 0
            }
        
        try:
            self.logger.info(f"   💭 SENTIMENT ANALYSIS - Analyzing {len(headlines)} headline(s)")
            
            sentiments = []
            for i, headline in enumerate(headlines, 1):
                self.logger.info(f"      Headline {i}/{len(headlines)}:")
                sentiment = self.analyze_text(headline)
                sentiments.append(sentiment)
            
            # Calculate average sentiment
            avg_score = sum(s['score'] for s in sentiments) / len(sentiments)
            avg_polarity = sum(s['polarity'] for s in sentiments) / len(sentiments)
            
            # Calculate confidence based on consistency
            score_std = self._calculate_std([s['score'] for s in sentiments])
            confidence = 1 - min(score_std, 1.0)  # Lower std = higher confidence
            
            classification = self._classify_sentiment(avg_score)
            
            self.logger.info(f"   📊 AGGREGATE SENTIMENT:")
            self.logger.info(f"      Average Score: {avg_score:.3f}")
            self.logger.info(f"      Average Polarity: {avg_polarity:.3f}")
            self.logger.info(f"      Classification: {classification}")
            self.logger.info(f"      Confidence: {confidence:.3f} (based on consistency)")
            self.logger.info(f"      Score Std Dev: {score_std:.3f}")
            
            return {
                'average_score': avg_score,
                'average_polarity': avg_polarity,
                'classification': classification,
                'confidence': confidence,
                'headline_count': len(headlines),
                'individual_sentiments': sentiments
            }
            
        except Exception as e:
            self.logger.error(f"❌ SENTIMENT ANALYSIS - Error analyzing news headlines: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return {
                'average_score': 0.0,
                'classification': 'NEUTRAL',
                'confidence': 0.0,
                'headline_count': 0
            }
    
    def _calculate_std(self, values: List[float]) -> float:
        """Calculate standard deviation"""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    def get_market_sentiment(self, symbol: str, news_data: Optional[List[str]] = None) -> Dict[str, any]:
        """
        Get overall market sentiment for a symbol
        
        Args:
            symbol: Trading symbol
            news_data: Optional list of news headlines
            
        Returns:
            Market sentiment analysis
        """
        cache_key = f"{symbol}_{datetime.now().strftime('%Y%m%d%H')}"
        
        # Check cache
        if cache_key in self.sentiment_cache:
            cached_time, cached_data = self.sentiment_cache[cache_key]
            if datetime.now() - cached_time < self.cache_duration:
                return cached_data
        
        # Analyze sentiment
        if news_data:
            sentiment = self.analyze_news_headlines(news_data)
        else:
            # Default neutral sentiment if no data
            sentiment = {
                'average_score': 0.0,
                'classification': 'NEUTRAL',
                'confidence': 0.0,
                'headline_count': 0
            }
        
        # Cache result
        self.sentiment_cache[cache_key] = (datetime.now(), sentiment)
        
        return sentiment
    
    def get_sentiment_signal(self, sentiment_data: Dict) -> Tuple[str, float]:
        """
        Convert sentiment analysis to trading signal
        
        Args:
            sentiment_data: Sentiment analysis results
            
        Returns:
            Tuple of (signal, strength)
        """
        score = sentiment_data.get('average_score', 0.0)
        confidence = sentiment_data.get('confidence', 0.0)
        
        self.logger.info(f"   🎯 SENTIMENT SIGNAL CONVERSION:")
        self.logger.info(f"      Sentiment Score: {score:.3f}")
        self.logger.info(f"      Confidence: {confidence:.3f}")
        
        # Calculate signal strength
        strength = abs(score) * confidence
        
        if score > 0.3 and confidence > 0.5:
            signal = 'BUY'
            self.logger.info(f"      ✅ Signal: {signal} (score {score:.3f} > 0.3 and confidence {confidence:.3f} > 0.5)")
        elif score < -0.3 and confidence > 0.5:
            signal = 'SELL'
            self.logger.info(f"      ✅ Signal: {signal} (score {score:.3f} < -0.3 and confidence {confidence:.3f} > 0.5)")
        else:
            signal = 'NEUTRAL'
            if confidence <= 0.5:
                self.logger.info(f"      ⚪ Signal: {signal} (confidence {confidence:.3f} <= 0.5 threshold)")
            else:
                self.logger.info(f"      ⚪ Signal: {signal} (score {score:.3f} in neutral zone -0.3 to 0.3)")
        
        self.logger.info(f"      Signal Strength: {strength:.3f}")
        
        return signal, strength
    
    def combine_with_technical(self, technical_signal: str, sentiment_signal: str, 
                               technical_weight: float = 0.7) -> str:
        """
        Combine technical and sentiment signals
        
        Args:
            technical_signal: Signal from technical analysis
            sentiment_signal: Signal from sentiment analysis
            technical_weight: Weight for technical signal (0-1)
            
        Returns:
            Combined signal
        """
        sentiment_weight = 1 - technical_weight
        
        # Convert signals to numeric scores
        signal_map = {'BUY': 1, 'NEUTRAL': 0, 'SELL': -1}
        
        tech_score = signal_map.get(technical_signal, 0)
        sent_score = signal_map.get(sentiment_signal, 0)
        
        # Calculate weighted average
        combined_score = tech_score * technical_weight + sent_score * sentiment_weight
        
        # Convert back to signal
        if combined_score > 0.3:
            return 'BUY'
        elif combined_score < -0.3:
            return 'SELL'
        else:
            return 'NEUTRAL'
