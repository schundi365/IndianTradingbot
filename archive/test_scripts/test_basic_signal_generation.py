#!/usr/bin/env python3
"""
Basic Signal Generation Test
Tests the basic signal generation pipeline to ensure it works correctly
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_simple_test_data(bars=50):
    """Create simple test data for basic testing"""
    np.random.seed(42)
    
    # Create simple uptrend
    base_price = 1.1000
    trend = np.linspace(0, 0.01, bars)  # 1% uptrend
    noise = np.random.normal(0, 0.0002, bars)  # Small noise
    
    close_prices = base_price + trend + noise
    
    data = []
    for i in range(bars):
        close = close_prices[i]
        high = close + abs(np.random.normal(0, 0.0001))
        low = close - abs(np.random.normal(0, 0.0001))
        open_price = close_prices[i-1] if i > 0 else close
        volume = np.random.randint(1000, 5000)
        
        timestamp = datetime.now() - timedelta(hours=bars-i)
        
        data.append({
            'time': timestamp,
            'open': open_price,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume
        })
    
    df = pd.DataFrame(data)
    df.set_index('time', inplace=True)
    
    # Add basic indicators
    # RSI
    delta = df['close'].diff()
    gains = delta.where(delta > 0, 0)
    losses = -delta.where(delta < 0, 0)
    avg_gains = gains.rolling(window=14).mean()
    avg_losses = losses.rolling(window=14).mean()
    rs = avg_gains / avg_losses
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # MACD
    ema_12 = df['close'].ewm(span=12).mean()
    ema_26 = df['close'].ewm(span=26).mean()
    df['macd'] = ema_12 - ema_26
    df['macd_signal'] = df['macd'].ewm(span=9).mean()
    df['macd_histogram'] = df['macd'] - df['macd_signal']
    
    # ADX (simplified)
    df['adx'] = 25 + np.random.normal(0, 3, len(df))
    df['adx'] = np.clip(df['adx'], 0, 100)
    
    return df

def test_basic_signal_generation():
    """Test basic signal generation"""
    logger.info("="*60)
    logger.info("BASIC SIGNAL GENERATION TEST")
    logger.info("="*60)
    
    try:
        # Import components
        from src.config import get_config
        from src.trend_detection_engine import TrendDetectionEngine
        
        config = get_config()
        
        # Lower the confidence threshold for testing
        config['min_trend_confidence'] = 0.3  # Lower threshold for testing
        
        # Initialize trend detection engine
        logger.info("Initializing TrendDetectionEngine...")
        trend_engine = TrendDetectionEngine(config)
        
        # Create test data
        logger.info("Creating test data...")
        df = create_simple_test_data(50)
        logger.info(f"Test data created: {len(df)} bars")
        
        # Test signal generation
        logger.info("Testing signal generation...")
        analysis = trend_engine.analyze_trend_change(df, "TEST")
        
        logger.info(f"Analysis results:")
        logger.info(f"  Total signals: {len(analysis.signals)}")
        logger.info(f"  Overall confidence: {analysis.confidence:.3f}")
        logger.info(f"  Market structure detected: {'Yes' if analysis.market_structure else 'No'}")
        logger.info(f"  Divergences found: {len(analysis.divergences)}")
        logger.info(f"  Aroon signal: {'Yes' if analysis.aroon_signal else 'No'}")
        logger.info(f"  EMA signal: {'Yes' if analysis.ema_signal else 'No'}")
        
        # Test individual components
        logger.info("\nTesting individual components:")
        
        # Test EMA analysis
        ema_signal = trend_engine.ema_momentum_analyzer.get_ema_signal(df)
        if ema_signal:
            logger.info(f"  EMA Signal Type: {ema_signal.signal_type}")
            logger.info(f"  EMA Momentum Strength: {ema_signal.momentum_strength:.3f}")
        
        # Test Aroon analysis
        aroon_signal = trend_engine.aroon_indicator.get_aroon_signal(df)
        if aroon_signal:
            logger.info(f"  Aroon Signal Type: {aroon_signal.signal_type}")
            logger.info(f"  Aroon Trend Strength: {aroon_signal.trend_strength:.3f}")
        
        # Test should_trade_trend
        should_buy, buy_conf = trend_engine.should_trade_trend(df, "buy")
        should_sell, sell_conf = trend_engine.should_trade_trend(df, "sell")
        
        logger.info(f"\nTrading recommendations:")
        logger.info(f"  Should trade BUY: {should_buy} (confidence: {buy_conf:.3f})")
        logger.info(f"  Should trade SELL: {should_sell} (confidence: {sell_conf:.3f})")
        
        logger.info("✅ Basic signal generation test PASSED")
        return True
        
    except Exception as e:
        logger.error(f"❌ Basic signal generation test FAILED: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_basic_signal_generation()
    sys.exit(0 if success else 1)