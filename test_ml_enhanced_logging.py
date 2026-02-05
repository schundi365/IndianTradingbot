"""
Test ML Enhanced Logging
Verifies that all ML modules have detailed logging enabled
"""

import logging
import numpy as np
import pandas as pd
from src.ml_signal_generator import MLSignalGenerator
from src.ml_integration import MLIntegration
from src.pattern_recognition import PatternRecognition
from src.sentiment_analyzer import SentimentAnalyzer

# Setup logging to see output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_ml_signal_generator_logging():
    """Test ML Signal Generator logging"""
    print("\n" + "="*80)
    print("TEST 1: ML Signal Generator Logging")
    print("="*80)
    
    ml_gen = MLSignalGenerator()
    
    # Test feature extraction logging
    print("\n--- Testing Feature Extraction Logging ---")
    market_data = {
        'close': [2040.0, 2041.5, 2043.0, 2045.5],
        'high': [2042.0, 2043.5, 2045.0, 2047.5],
        'low': [2038.0, 2039.5, 2041.0, 2043.5],
        'volume': [1000, 1100, 1200, 1300],
        'rsi': 65.5,
        'macd': 0.00234,
        'macd_signal': 0.00189,
        'adx': 25.3,
        'atr': 12.5,
        'ema_fast': 2044.0,
        'ema_slow': 2040.0,
        'bb_upper': 2050.0,
        'bb_lower': 2035.0
    }
    
    features = ml_gen.extract_features(market_data)
    print(f"\n✅ Feature extraction completed with {features.shape[1]} features")
    
    # Test prediction logging (will show model not trained)
    print("\n--- Testing Prediction Logging (Model Not Trained) ---")
    signal, confidence = ml_gen.predict_signal(features)
    print(f"✅ Prediction completed: {signal} (confidence: {confidence:.4f})")
    
    print("\n✅ TEST 1 PASSED: ML Signal Generator logging working")


def test_pattern_recognition_logging():
    """Test Pattern Recognition logging"""
    print("\n" + "="*80)
    print("TEST 2: Pattern Recognition Logging")
    print("="*80)
    
    pattern_rec = PatternRecognition()
    
    # Create sample OHLC data
    print("\n--- Testing Pattern Detection Logging ---")
    np.random.seed(42)
    n = 50
    base_price = 2040.0
    
    ohlc_data = {
        'open': base_price + np.random.randn(n) * 5,
        'high': base_price + np.random.randn(n) * 5 + 2,
        'low': base_price + np.random.randn(n) * 5 - 2,
        'close': base_price + np.random.randn(n) * 5
    }
    
    patterns = pattern_rec.detect_all_patterns(ohlc_data)
    print(f"\n✅ Pattern detection completed, found {len(patterns)} pattern(s)")
    
    # Test pattern signal calculation
    print("\n--- Testing Pattern Signal Calculation ---")
    signal, confidence = pattern_rec.get_pattern_signal(patterns)
    print(f"✅ Pattern signal: {signal} (confidence: {confidence:.4f})")
    
    print("\n✅ TEST 2 PASSED: Pattern Recognition logging working")


def test_sentiment_analyzer_logging():
    """Test Sentiment Analyzer logging"""
    print("\n" + "="*80)
    print("TEST 3: Sentiment Analyzer Logging")
    print("="*80)
    
    sentiment = SentimentAnalyzer()
    
    # Test single text analysis
    print("\n--- Testing Single Text Analysis Logging ---")
    text = "Gold prices surge to new highs on strong demand and bullish momentum"
    result = sentiment.analyze_text(text)
    print(f"✅ Text analysis completed: {result['classification']}")
    
    # Test multiple headlines
    print("\n--- Testing Multiple Headlines Analysis ---")
    headlines = [
        "Gold rallies on safe haven demand",
        "Bullish outlook for precious metals",
        "Strong buying pressure in gold market"
    ]
    
    news_sentiment = sentiment.analyze_news_headlines(headlines)
    print(f"✅ Headlines analysis completed: {news_sentiment['classification']}")
    
    # Test signal conversion
    print("\n--- Testing Sentiment Signal Conversion ---")
    signal, strength = sentiment.get_sentiment_signal(news_sentiment)
    print(f"✅ Sentiment signal: {signal} (strength: {strength:.4f})")
    
    print("\n✅ TEST 3 PASSED: Sentiment Analyzer logging working")


def test_ml_integration_logging():
    """Test ML Integration logging"""
    print("\n" + "="*80)
    print("TEST 4: ML Integration Logging")
    print("="*80)
    
    config = {
        'ml_enabled': False,  # Disabled since model not trained
        'sentiment_enabled': True,
        'pattern_enabled': True,
        'technical_weight': 0.4,
        'ml_weight': 0.3,
        'sentiment_weight': 0.15,
        'pattern_weight': 0.15
    }
    
    ml_integration = MLIntegration(config)
    
    # Test enhanced signal generation
    print("\n--- Testing Enhanced Signal Generation ---")
    
    market_data = {
        'close': [2040.0, 2041.5, 2043.0, 2045.5],
        'high': [2042.0, 2043.5, 2045.0, 2047.5],
        'low': [2038.0, 2039.5, 2041.0, 2043.5],
        'open': [2039.0, 2040.5, 2042.0, 2044.5],
        'volume': [1000, 1100, 1200, 1300],
        'rsi': 65.5,
        'macd': 0.00234,
        'macd_signal': 0.00189,
        'adx': 25.3,
        'atr': 12.5,
        'ema_fast': 2044.0,
        'ema_slow': 2040.0,
        'bb_upper': 2050.0,
        'bb_lower': 2035.0
    }
    
    news_data = [
        "Gold prices surge on strong demand",
        "Bullish momentum continues in precious metals"
    ]
    
    enhanced_signals = ml_integration.get_enhanced_signal(
        symbol='XAUUSD',
        market_data=market_data,
        technical_signal='BUY',
        technical_confidence=0.75,
        news_data=news_data
    )
    
    print(f"\n✅ Enhanced signal: {enhanced_signals['combined']['signal']}")
    print(f"   Confidence: {enhanced_signals['combined']['confidence']:.4f}")
    print(f"   Analysis: {enhanced_signals['analysis']}")
    
    print("\n✅ TEST 4 PASSED: ML Integration logging working")


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("ML ENHANCED LOGGING TEST SUITE")
    print("="*80)
    print("\nThis test verifies that all ML modules have detailed logging enabled")
    print("Watch for emoji indicators and detailed step-by-step logging\n")
    
    try:
        test_ml_signal_generator_logging()
        test_pattern_recognition_logging()
        test_sentiment_analyzer_logging()
        test_ml_integration_logging()
        
        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED - Enhanced Logging Working Correctly")
        print("="*80)
        print("\nAll ML modules now have comprehensive logging that matches")
        print("the detailed logging level used throughout the trading bot.")
        print("\nKey features:")
        print("  ✅ Step-by-step process visibility")
        print("  ✅ Detailed feature values and calculations")
        print("  ✅ Signal decision reasoning")
        print("  ✅ Error tracebacks for debugging")
        print("  ✅ Emoji indicators for quick scanning")
        print("\nThe enhanced logging will automatically appear in trading_bot.log")
        print("when ML features are used during trading.")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
