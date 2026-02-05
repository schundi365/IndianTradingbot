"""
Debug script for volume exhaustion detection
"""

import sys
sys.path.append('src')

import pandas as pd
import numpy as np
from volume_analyzer import VolumeAnalyzer

def test_exhaustion_detection():
    """Test exhaustion volume detection with simple data"""
    
    # Create test configuration
    config = {
        'use_volume_filter': True,
        'min_volume_ma': 0.7,
        'volume_ma_period': 20,
        'obv_period': 14
    }
    
    analyzer = VolumeAnalyzer(config)
    
    # Create simple test data with clear exhaustion pattern
    bars = 50
    base_volume = 3000
    spike_multiplier = 3.0  # 3x volume spike
    price_movement = 0.002  # Very small price movement
    
    dates = pd.date_range('2024-01-01', periods=bars, freq='h')
    
    # Base price and volume
    base_price = 1.1000
    prices = np.full(bars, base_price)
    volumes = np.full(bars, base_volume)
    
    # Add volume spike closer to the end so it's in the analysis window
    spike_position = bars - 10  # 10 bars from the end
    volumes[spike_position] = base_volume * spike_multiplier
    
    print(f"Volume spike at position {spike_position}: {volumes[spike_position]} (vs normal {base_volume})")
    
    # Minimal price movement after spike
    for i in range(spike_position + 1, min(spike_position + 4, bars)):
        prices[i] = prices[spike_position] + (price_movement * (i - spike_position) / 3)
    
    print(f"Price movement after spike: {prices[spike_position]} -> {prices[min(spike_position + 3, bars-1)]}")
    
    # Generate OHLC from prices
    df = pd.DataFrame({
        'time': dates,
        'open': prices,
        'high': prices * 1.001,
        'low': prices * 0.999,
        'close': prices,
        'tick_volume': volumes
    })
    
    df.set_index('time', inplace=True)
    
    print(f"\nDataFrame created with {len(df)} bars")
    print(f"Volume range: {df['tick_volume'].min()} - {df['tick_volume'].max()}")
    print(f"Price range: {df['close'].min():.5f} - {df['close'].max():.5f}")
    
    # Debug: Check the volume data around spike
    print(f"\nVolume data around spike (position {spike_position}):")
    start_idx = max(0, spike_position - 3)
    end_idx = min(len(df), spike_position + 4)
    for i in range(start_idx, end_idx):
        marker = " <-- SPIKE" if i == spike_position else ""
        print(f"  Position {i}: Volume = {df['tick_volume'].iloc[i]}, Price = {df['close'].iloc[i]:.5f}{marker}")
    
    # Check recent data used for analysis
    recent_df = df.iloc[-20:]  # Last 20 bars
    avg_volume = recent_df['tick_volume'].mean()
    threshold = avg_volume * 1.5
    
    print(f"\nVolume analysis (last 20 bars):")
    print(f"  Average volume: {avg_volume:.0f}")
    print(f"  Threshold (1.5x): {threshold:.0f}")
    print(f"  Max volume in recent data: {recent_df['tick_volume'].max()}")
    print(f"  Spike volume: {volumes[spike_position]}")
    print(f"  Is spike above threshold? {volumes[spike_position] > threshold}")
    
    # Test exhaustion detection
    print(f"\n" + "="*60)
    print("TESTING EXHAUSTION DETECTION")
    print("="*60)
    
    result = analyzer.detect_exhaustion_volume(df, lookback=20)
    
    print(f"\nExhaustion Detection Result:")
    print(f"  Detected: {result['detected']}")
    print(f"  Type: {result['type']}")
    print(f"  Strength: {result['strength']}")
    print(f"  Description: {result['description']}")
    
    # Also test volume confirmation
    print(f"\n" + "="*60)
    print("TESTING VOLUME CONFIRMATION")
    print("="*60)
    
    confirmation = analyzer.get_volume_confirmation(df, 'buy')
    
    print(f"\nVolume Confirmation Result:")
    print(f"  Confirmed: {confirmation['confirmed']}")
    print(f"  Score: {confirmation['score']:.3f}")
    print(f"  Exhaustion Volume: {confirmation.get('exhaustion_volume', {})}")

if __name__ == "__main__":
    test_exhaustion_detection()