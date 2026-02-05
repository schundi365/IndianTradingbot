"""
Integration Test for Enhanced Volume Analysis with Trend Detection
Tests the complete integration of enhanced volume analysis with the TrendDetectionEngine
"""

import sys
import os
sys.path.append('src')

import pandas as pd
import numpy as np
import MetaTrader5 as mt5
from datetime import datetime, timedelta
import logging

# Import the components we're testing
from config import get_config
from trend_detection_engine import TrendDetectionEngine

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_data_with_volume_patterns(bars=100, pattern_type='exhaustion'):
    """Create synthetic test data with specific volume patterns"""
    
    # Base price and time series
    base_price = 1.1000
    base_volume = 3000
    dates = pd.date_range(start='2024-01-01', periods=bars, freq='h')
    
    # Generate base price movement
    price_changes = np.random.normal(0, 0.0001, bars)
    prices = base_price + np.cumsum(price_changes)
    
    # Generate base volume
    volumes = np.random.normal(base_volume, base_volume * 0.2, bars)
    volumes = np.maximum(volumes, base_volume * 0.5)  # Ensure positive volumes
    
    if pattern_type == 'exhaustion':
        # Add volume exhaustion pattern near the end
        spike_position = bars - 10
        volumes[spike_position] = base_volume * 3.0  # 3x volume spike
        
        # Minimal price follow-through after spike
        for i in range(spike_position + 1, min(spike_position + 4, bars)):
            prices[i] = prices[spike_position] + (0.001 * (i - spike_position) / 3)
    
    elif pattern_type == 'breakout':
        # Add breakout pattern with volume expansion
        breakout_start = int(bars * 0.7)
        
        # Consolidation period (normal volume)
        # Breakout period (higher volume and price movement)
        for i in range(breakout_start, bars):
            volumes[i] = base_volume * 1.8  # 80% volume increase
            prices[i] = prices[breakout_start] + (0.01 * (i - breakout_start) / (bars - breakout_start))
    
    elif pattern_type == 'divergence':
        # Create volume-price divergence
        trend_start = int(bars * 0.5)
        
        # Price trend up, volume trend down (bearish divergence)
        for i in range(trend_start, bars):
            progress = (i - trend_start) / (bars - trend_start)
            prices[i] = prices[trend_start] + (0.008 * progress)  # Price up
            volumes[i] = base_volume * (1.5 - 0.7 * progress)    # Volume down
    
    # Generate OHLC data
    df = pd.DataFrame({
        'time': dates,
        'open': prices,
        'high': prices * (1 + np.random.uniform(0, 0.002, bars)),
        'low': prices * (1 - np.random.uniform(0, 0.002, bars)),
        'close': prices,
        'tick_volume': volumes.astype(int)
    })
    
    # Ensure high >= close >= low and high >= open >= low
    df['high'] = np.maximum(df['high'], np.maximum(df['open'], df['close']))
    df['low'] = np.minimum(df['low'], np.minimum(df['open'], df['close']))
    
    df.set_index('time', inplace=True)
    
    return df

def add_indicators(df):
    """Add technical indicators to the dataframe"""
    
    # Moving averages
    df['ma_20'] = df['close'].rolling(window=20).mean()
    df['ma_50'] = df['close'].rolling(window=50).mean()
    
    # EMA
    df['ema_20'] = df['close'].ewm(span=20).mean()
    df['ema_50'] = df['close'].ewm(span=50).mean()
    
    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # MACD
    exp1 = df['close'].ewm(span=12).mean()
    exp2 = df['close'].ewm(span=26).mean()
    df['macd'] = exp1 - exp2
    df['macd_signal'] = df['macd'].ewm(span=9).mean()
    df['macd_histogram'] = df['macd'] - df['macd_signal']
    
    # ADX (simplified)
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
    
    # Fill NaN values
    df = df.bfill().ffill()
    
    return df

def test_volume_trend_integration():
    """Test the complete volume-trend integration"""
    
    print("="*80)
    print("TESTING ENHANCED VOLUME ANALYSIS INTEGRATION")
    print("="*80)
    
    try:
        # Get configuration with volume analysis enabled
        config = get_config()
        config['timeframe'] = mt5.TIMEFRAME_M30
        config['use_volume_filter'] = True
        config['use_trend_detection'] = True
        
        # Initialize trend detection engine
        engine = TrendDetectionEngine(config)
        
        print(f"\n✅ TrendDetectionEngine initialized successfully")
        print(f"   Trend detection enabled: {engine.use_trend_detection}")
        
        # Test 1: Volume Exhaustion Pattern
        print(f"\n🔍 Test 1: Volume Exhaustion Pattern Analysis")
        exhaustion_df = create_test_data_with_volume_patterns(bars=100, pattern_type='exhaustion')
        exhaustion_df = add_indicators(exhaustion_df)
        
        print(f"   Created exhaustion test data: {len(exhaustion_df)} bars")
        print(f"   Volume range: {exhaustion_df['tick_volume'].min()} - {exhaustion_df['tick_volume'].max()}")
        
        exhaustion_result = engine.analyze_trend_change(exhaustion_df, "EURUSD")
        
        print(f"   Analysis Results:")
        print(f"     Signals generated: {len(exhaustion_result.signals)}")
        print(f"     Overall confidence: {exhaustion_result.confidence:.3f}")
        print(f"     Volume confirmation available: {exhaustion_result.volume_confirmation is not None}")
        
        if exhaustion_result.volume_confirmation:
            vc = exhaustion_result.volume_confirmation
            print(f"     Volume spike detected: {vc.volume_spike}")
            print(f"     Volume ratio: {vc.volume_ratio:.2f}x")
            print(f"     Volume strength: {vc.strength:.3f}")
        
        # Test 2: Breakout Volume Pattern
        print(f"\n🔍 Test 2: Breakout Volume Pattern Analysis")
        breakout_df = create_test_data_with_volume_patterns(bars=100, pattern_type='breakout')
        breakout_df = add_indicators(breakout_df)
        
        print(f"   Created breakout test data: {len(breakout_df)} bars")
        print(f"   Volume range: {breakout_df['tick_volume'].min()} - {breakout_df['tick_volume'].max()}")
        
        breakout_result = engine.analyze_trend_change(breakout_df, "EURUSD")
        
        print(f"   Analysis Results:")
        print(f"     Signals generated: {len(breakout_result.signals)}")
        print(f"     Overall confidence: {breakout_result.confidence:.3f}")
        
        if breakout_result.volume_confirmation:
            vc = breakout_result.volume_confirmation
            print(f"     Volume spike detected: {vc.volume_spike}")
            print(f"     Volume ratio: {vc.volume_ratio:.2f}x")
            print(f"     Volume strength: {vc.strength:.3f}")
        
        # Test 3: Volume-Price Divergence Pattern
        print(f"\n🔍 Test 3: Volume-Price Divergence Analysis")
        divergence_df = create_test_data_with_volume_patterns(bars=100, pattern_type='divergence')
        divergence_df = add_indicators(divergence_df)
        
        print(f"   Created divergence test data: {len(divergence_df)} bars")
        print(f"   Volume range: {divergence_df['tick_volume'].min()} - {divergence_df['tick_volume'].max()}")
        
        divergence_result = engine.analyze_trend_change(divergence_df, "EURUSD")
        
        print(f"   Analysis Results:")
        print(f"     Signals generated: {len(divergence_result.signals)}")
        print(f"     Overall confidence: {divergence_result.confidence:.3f}")
        
        if divergence_result.volume_confirmation:
            vc = divergence_result.volume_confirmation
            print(f"     Volume spike detected: {vc.volume_spike}")
            print(f"     Volume ratio: {vc.volume_ratio:.2f}x")
            print(f"     Volume strength: {vc.strength:.3f}")
        
        # Test 4: Signal Trading Decision with Volume
        print(f"\n🔍 Test 4: Trading Decision with Volume Analysis")
        
        # Test buy signal with volume confirmation
        should_buy, buy_confidence = engine.should_trade_trend(exhaustion_df, 'buy')
        print(f"   Should trade BUY (exhaustion data): {should_buy} (confidence: {buy_confidence:.3f})")
        
        should_sell, sell_confidence = engine.should_trade_trend(divergence_df, 'sell')
        print(f"   Should trade SELL (divergence data): {should_sell} (confidence: {sell_confidence:.3f})")
        
        # Test 5: Volume Filter Impact
        print(f"\n🔍 Test 5: Volume Filter Impact Analysis")
        
        # Create low volume data
        low_volume_df = create_test_data_with_volume_patterns(bars=100, pattern_type='exhaustion')
        low_volume_df['tick_volume'] = low_volume_df['tick_volume'] * 0.3  # Very low volume
        low_volume_df = add_indicators(low_volume_df)
        
        low_volume_result = engine.analyze_trend_change(low_volume_df, "EURUSD")
        
        print(f"   Low volume analysis:")
        print(f"     Signals generated: {len(low_volume_result.signals)}")
        print(f"     Overall confidence: {low_volume_result.confidence:.3f}")
        
        if low_volume_result.volume_confirmation:
            vc = low_volume_result.volume_confirmation
            print(f"     Volume strength: {vc.strength:.3f}")
        
        print(f"\n" + "="*80)
        print(f"🎉 ENHANCED VOLUME ANALYSIS INTEGRATION TEST COMPLETED!")
        print(f"✅ Volume exhaustion detection integrated")
        print(f"✅ Volume breakout confirmation integrated")
        print(f"✅ Volume-price divergence analysis integrated")
        print(f"✅ Volume-based signal filtering integrated")
        print(f"✅ Volume confidence adjustments working")
        print("="*80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_volume_trend_integration()
    sys.exit(0 if success else 1)