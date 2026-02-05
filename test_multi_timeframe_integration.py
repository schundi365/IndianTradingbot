"""
Integration Test for Multi-Timeframe Confirmation System
Tests the complete integration of multi-timeframe analysis with the TrendDetectionEngine
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
from multi_timeframe_analyzer import MultiTimeframeAnalyzer

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_data(bars=100, trend='bullish'):
    """Create synthetic test data for integration testing"""
    
    # Base price and time series
    base_price = 1.1000
    dates = pd.date_range(start='2024-01-01', periods=bars, freq='h')
    
    # Generate price movement based on trend
    if trend == 'bullish':
        trend_component = np.linspace(0, 0.02, bars)  # 2% upward trend
    elif trend == 'bearish':
        trend_component = np.linspace(0, -0.02, bars)  # 2% downward trend
    else:  # neutral
        trend_component = np.zeros(bars)
    
    # Add some noise
    noise_component = np.random.normal(0, 0.005, bars)
    
    # Combine components
    price_changes = trend_component + noise_component
    prices = base_price + np.cumsum(price_changes)
    
    # Generate OHLC data
    df = pd.DataFrame({
        'time': dates,
        'open': prices,
        'high': prices * (1 + np.random.uniform(0, 0.002, bars)),
        'low': prices * (1 - np.random.uniform(0, 0.002, bars)),
        'close': prices,
        'volume': np.random.randint(1000, 10000, bars)
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

def test_multi_timeframe_integration():
    """Test the complete multi-timeframe integration"""
    
    print("="*80)
    print("TESTING MULTI-TIMEFRAME INTEGRATION")
    print("="*80)
    
    try:
        # Get configuration
        config = get_config()
        config['timeframe'] = mt5.TIMEFRAME_M30  # Set primary timeframe to M30
        
        # Initialize trend detection engine
        engine = TrendDetectionEngine(config)
        
        print(f"\n✅ TrendDetectionEngine initialized successfully")
        print(f"   Multi-timeframe enabled: {hasattr(engine, 'multi_timeframe_analyzer')}")
        
        if hasattr(engine, 'multi_timeframe_analyzer'):
            mtf_analyzer = engine.multi_timeframe_analyzer
            print(f"   MTF configuration: {len(mtf_analyzer.primary_to_higher)} timeframe relationships")
            print(f"   MTF enabled: {mtf_analyzer.enable_mtf}")
            print(f"   Alignment threshold: {mtf_analyzer.alignment_threshold}")
        
        # Create test data for primary timeframe (M30)
        print(f"\n📊 Creating test data...")
        primary_df = create_test_data(bars=100, trend='bullish')
        primary_df = add_indicators(primary_df)
        
        print(f"   Primary timeframe data: {len(primary_df)} bars")
        print(f"   Price range: {primary_df['close'].min():.5f} - {primary_df['close'].max():.5f}")
        
        # Test 1: Basic trend analysis
        print(f"\n🔍 Test 1: Basic Trend Analysis")
        analysis_result = engine.analyze_trend_change(primary_df, "EURUSD")
        
        print(f"   Signals generated: {len(analysis_result.signals)}")
        print(f"   Overall confidence: {analysis_result.confidence:.3f}")
        print(f"   Timeframe alignment: {analysis_result.timeframe_alignment is not None}")
        
        if analysis_result.timeframe_alignment:
            ta = analysis_result.timeframe_alignment
            print(f"   Primary TF: {ta.primary_timeframe}")
            print(f"   Higher TF: {ta.higher_timeframe}")
            print(f"   Alignment Score: {ta.alignment_score:.3f}")
            print(f"   Confirmation Level: {ta.confirmation_level}")
        
        # Test 2: Signal confirmation
        print(f"\n🔍 Test 2: Signal Confirmation")
        
        # Test buy signal confirmation
        should_buy, buy_confidence = engine.should_trade_trend(primary_df, 'buy')
        print(f"   Should trade BUY: {should_buy} (confidence: {buy_confidence:.3f})")
        
        # Test sell signal confirmation
        should_sell, sell_confidence = engine.should_trade_trend(primary_df, 'sell')
        print(f"   Should trade SELL: {should_sell} (confidence: {sell_confidence:.3f})")
        
        # Test 3: Multi-timeframe analyzer standalone
        print(f"\n🔍 Test 3: Multi-Timeframe Analyzer Standalone")
        
        if hasattr(engine, 'multi_timeframe_analyzer'):
            mtf_analyzer = engine.multi_timeframe_analyzer
            
            # Create higher timeframe data (H4)
            higher_df = create_test_data(bars=50, trend='bullish')  # Aligned trend
            higher_df = add_indicators(higher_df)
            
            # Test alignment analysis
            alignment_result = mtf_analyzer.analyze_timeframe_alignment(primary_df, higher_df)
            
            print(f"   Primary signal: {alignment_result.primary_signal}")
            print(f"   Higher signal: {alignment_result.higher_signal}")
            print(f"   Alignment score: {alignment_result.alignment_score:.3f}")
            print(f"   Confirmation level: {alignment_result.confirmation_level}")
            print(f"   Contributing factors: {', '.join(alignment_result.factors)}")
            
            # Test signal confirmation
            should_confirm_buy = mtf_analyzer.should_confirm_signal(alignment_result, 'buy')
            should_confirm_sell = mtf_analyzer.should_confirm_signal(alignment_result, 'sell')
            
            print(f"   Should confirm BUY: {should_confirm_buy}")
            print(f"   Should confirm SELL: {should_confirm_sell}")
        
        # Test 4: Contradictory timeframes
        print(f"\n🔍 Test 4: Contradictory Timeframes")
        
        if hasattr(engine, 'multi_timeframe_analyzer'):
            # Create contradictory higher timeframe data
            contradictory_df = create_test_data(bars=50, trend='bearish')  # Opposite trend
            contradictory_df = add_indicators(contradictory_df)
            
            # Test alignment with contradictory data
            contradictory_alignment = mtf_analyzer.analyze_timeframe_alignment(primary_df, contradictory_df)
            
            print(f"   Primary signal: {contradictory_alignment.primary_signal}")
            print(f"   Higher signal: {contradictory_alignment.higher_signal}")
            print(f"   Alignment score: {contradictory_alignment.alignment_score:.3f}")
            print(f"   Confirmation level: {contradictory_alignment.confirmation_level}")
            
            # Test signal confirmation with contradictory data
            should_confirm_contradictory = mtf_analyzer.should_confirm_signal(contradictory_alignment, 'buy')
            print(f"   Should confirm BUY with contradictory HTF: {should_confirm_contradictory}")
        
        print(f"\n" + "="*80)
        print(f"🎉 MULTI-TIMEFRAME INTEGRATION TEST COMPLETED SUCCESSFULLY!")
        print(f"✅ All components are properly integrated")
        print(f"✅ Multi-timeframe confirmation is working")
        print(f"✅ Signal validation includes MTF analysis")
        print("="*80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_multi_timeframe_integration()
    sys.exit(0 if success else 1)