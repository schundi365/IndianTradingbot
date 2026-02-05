"""
Test ML Features
Demonstrates ML signal generation, sentiment analysis, and pattern recognition
"""

import numpy as np
import logging
from src.ml_integration import MLIntegration
from src.sentiment_analyzer import SentimentAnalyzer
from src.pattern_recognition import PatternRecognition

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_sentiment_analysis():
    """Test sentiment analysis"""
    print("\n" + "="*60)
    print("TESTING SENTIMENT ANALYSIS")
    print("="*60)
    
    analyzer = SentimentAnalyzer(logger=logger)
    
    # Test individual text
    print("\n1. Individual Text Analysis:")
    texts = [
        "EUR/USD rallies strongly on positive economic data",
        "Markets crash amid recession fears",
        "Trading volumes remain stable"
    ]
    
    for text in texts:
        sentiment = analyzer.analyze_text(text)
        print(f"\nText: {text}")
        print(f"  Polarity: {sentiment['polarity']:.3f}")
        print(f"  Score: {sentiment['score']:.3f}")
        print(f"  Classification: {sentiment['classification']}")
    
    # Test news headlines
    print("\n2. News Headlines Analysis:")
    headlines = [
        "EUR/USD breaks resistance, bullish momentum continues",
        "Strong buying pressure in forex markets",
        "Technical indicators show uptrend formation"
    ]
    
    news_sentiment = analyzer.analyze_news_headlines(headlines)
    print(f"\nHeadlines analyzed: {news_sentiment['headline_count']}")
    print(f"Average score: {news_sentiment['average_score']:.3f}")
    print(f"Classification: {news_sentiment['classification']}")
    print(f"Confidence: {news_sentiment['confidence']:.3f}")
    
    # Get trading signal
    signal, strength = analyzer.get_sentiment_signal(news_sentiment)
    print(f"\nTrading Signal: {signal}")
    print(f"Signal Strength: {strength:.3f}")


def test_pattern_recognition():
    """Test pattern recognition"""
    print("\n" + "="*60)
    print("TESTING PATTERN RECOGNITION")
    print("="*60)
    
    recognizer = PatternRecognition(logger=logger)
    
    # Generate sample OHLC data
    print("\n1. Generating sample market data...")
    
    # Simulate double bottom pattern
    close_prices = np.array([
        100, 99, 98, 97, 96, 97, 98, 99, 100, 101,
        100, 99, 98, 97, 96, 97, 98, 99, 100, 101,
        102, 103, 104, 105, 106, 107, 108, 109, 110, 111
    ])
    
    high_prices = close_prices + np.random.uniform(0.5, 1.5, len(close_prices))
    low_prices = close_prices - np.random.uniform(0.5, 1.5, len(close_prices))
    open_prices = close_prices + np.random.uniform(-0.5, 0.5, len(close_prices))
    
    ohlc_data = {
        'open': open_prices,
        'high': high_prices,
        'low': low_prices,
        'close': close_prices
    }
    
    # Detect patterns
    print("\n2. Detecting patterns...")
    patterns = recognizer.detect_all_patterns(ohlc_data)
    
    if patterns:
        print(f"\nFound {len(patterns)} pattern(s):")
        for i, pattern in enumerate(patterns, 1):
            print(f"\n  Pattern {i}:")
            print(f"    Name: {pattern['name']}")
            print(f"    Type: {pattern['type']}")
            print(f"    Direction: {pattern['direction']}")
            print(f"    Confidence: {pattern['confidence']:.3f}")
            print(f"    Signal: {pattern['signal']}")
    else:
        print("\nNo patterns detected")
    
    # Get trading signal
    signal, confidence = recognizer.get_pattern_signal(patterns)
    print(f"\nCombined Pattern Signal: {signal}")
    print(f"Confidence: {confidence:.3f}")


def test_ml_integration():
    """Test ML integration"""
    print("\n" + "="*60)
    print("TESTING ML INTEGRATION")
    print("="*60)
    
    # Configuration
    config = {
        'ml_enabled': False,  # Set to True after training
        'sentiment_enabled': True,
        'pattern_enabled': True,
        'technical_weight': 0.4,
        'ml_weight': 0.3,
        'sentiment_weight': 0.15,
        'pattern_weight': 0.15
    }
    
    ml_integration = MLIntegration(config, logger=logger)
    
    # Sample market data
    print("\n1. Preparing market data...")
    market_data = {
        'close': np.array([1.0850, 1.0855, 1.0860, 1.0865, 1.0870] * 10),
        'high': np.array([1.0860, 1.0865, 1.0870, 1.0875, 1.0880] * 10),
        'low': np.array([1.0840, 1.0845, 1.0850, 1.0855, 1.0860] * 10),
        'open': np.array([1.0845, 1.0850, 1.0855, 1.0860, 1.0865] * 10),
        'volume': np.array([1000, 1100, 1200, 1300, 1400] * 10),
        'rsi': 65.0,
        'macd': 0.0015,
        'macd_signal': 0.0012,
        'adx': 25.0,
        'atr': 0.0015,
        'ema_fast': 1.0865,
        'ema_slow': 1.0855,
        'bb_upper': 1.0880,
        'bb_lower': 1.0840
    }
    
    # Sample news
    news_headlines = [
        "EUR/USD shows strong bullish momentum",
        "Positive economic indicators support euro",
        "Technical breakout signals further gains"
    ]
    
    # Get enhanced signal
    print("\n2. Getting enhanced signal...")
    enhanced_signals = ml_integration.get_enhanced_signal(
        symbol='EURUSD',
        market_data=market_data,
        technical_signal='BUY',
        technical_confidence=0.75,
        news_data=news_headlines
    )
    
    # Display results
    print("\n3. Signal Analysis:")
    print(f"\n  Technical: {enhanced_signals['technical']['signal']} "
          f"(confidence: {enhanced_signals['technical']['confidence']:.3f})")
    
    print(f"  ML: {enhanced_signals['ml']['signal']} "
          f"(confidence: {enhanced_signals['ml']['confidence']:.3f})")
    
    print(f"  Sentiment: {enhanced_signals['sentiment']['signal']} "
          f"(confidence: {enhanced_signals['sentiment']['confidence']:.3f})")
    
    print(f"  Pattern: {enhanced_signals['pattern']['signal']} "
          f"(confidence: {enhanced_signals['pattern']['confidence']:.3f})")
    
    print(f"\n  COMBINED: {enhanced_signals['combined']['signal']} "
          f"(confidence: {enhanced_signals['combined']['confidence']:.3f})")
    
    print(f"\n  Analysis: {enhanced_signals['analysis']}")
    
    # Trading decision
    print("\n4. Trading Decision:")
    should_trade = ml_integration.should_trade(enhanced_signals, min_confidence=0.6)
    print(f"  Should Trade: {should_trade}")
    
    if should_trade:
        multiplier = ml_integration.get_signal_strength_multiplier(enhanced_signals)
        print(f"  Position Size Multiplier: {multiplier:.2f}x")


def test_feature_extraction():
    """Test ML feature extraction"""
    print("\n" + "="*60)
    print("TESTING FEATURE EXTRACTION")
    print("="*60)
    
    from src.ml_signal_generator import MLSignalGenerator
    
    ml_generator = MLSignalGenerator(logger=logger)
    
    # Sample market data
    market_data = {
        'close': np.array([1.0850, 1.0855, 1.0860, 1.0865, 1.0870] * 10),
        'volume': np.array([1000, 1100, 1200, 1300, 1400] * 10),
        'rsi': 65.0,
        'macd': 0.0015,
        'macd_signal': 0.0012,
        'adx': 25.0,
        'atr': 0.0015,
        'ema_fast': 1.0865,
        'ema_slow': 1.0855,
        'bb_upper': 1.0880,
        'bb_lower': 1.0840
    }
    
    print("\n1. Extracting features from market data...")
    features = ml_generator.extract_features(market_data)
    
    print(f"\nExtracted {features.shape[1]} features:")
    print(f"Feature array shape: {features.shape}")
    print(f"Feature values: {features[0][:5]}... (showing first 5)")
    
    print("\n2. Model Status:")
    print(f"  Model trained: {ml_generator.is_trained}")
    print(f"  Model available: {ml_generator.model is not None}")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("ML FEATURES TEST SUITE")
    print("="*60)
    
    try:
        # Test sentiment analysis
        test_sentiment_analysis()
        
        # Test pattern recognition
        test_pattern_recognition()
        
        # Test feature extraction
        test_feature_extraction()
        
        # Test ML integration
        test_ml_integration()
        
        print("\n" + "="*60)
        print("ALL TESTS COMPLETED")
        print("="*60)
        print("\nNext Steps:")
        print("1. Install ML dependencies: pip install -r requirements_ml.txt")
        print("2. Download TextBlob corpora: python -m textblob.download_corpora")
        print("3. Enable ML features in bot_config.json")
        print("4. Train ML model with historical data")
        print("5. Monitor performance and adjust weights")
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        print(f"\nERROR: {e}")
        print("\nMake sure to install dependencies:")
        print("  pip install -r requirements_ml.txt")


if __name__ == "__main__":
    main()
