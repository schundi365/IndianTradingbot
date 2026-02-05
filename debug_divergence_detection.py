#!/usr/bin/env python3
"""
Debug script to understand why divergence detection is failing
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from divergence_detector import DivergenceDetector

def create_simple_bearish_rsi_divergence():
    """Create very clear bearish RSI divergence pattern"""
    dates = pd.date_range('2024-01-01', periods=60, freq='h')
    
    # Create clear pattern: price goes 100 -> 105 -> 102 -> 108 (higher high)
    # RSI goes 50 -> 70 -> 60 -> 65 (lower high)
    
    prices = []
    rsi_values = []
    
    for i in range(60):
        if i < 15:
            # Initial uptrend
            price = 100 + (i * 0.3)
            rsi = 50 + (i * 1.3)
        elif i < 30:
            # First peak
            price = 104.5 + np.sin((i - 15) * 0.2) * 0.5
            rsi = 69.5 + np.sin((i - 15) * 0.2) * 0.5
        elif i < 45:
            # Pullback
            price = 104.5 - ((i - 30) * 0.15)
            rsi = 69.5 - ((i - 30) * 0.6)
        else:
            # Second peak - higher price, lower RSI
            price = 102.25 + ((i - 45) * 0.25)  # Goes to ~106.0 (higher than 104.5)
            rsi = 60.5 + ((i - 45) * 0.3)       # Goes to ~65.0 (lower than 69.5)
        
        prices.append(price)
        rsi_values.append(max(0, min(100, rsi)))
    
    df = pd.DataFrame({
        'time': dates,
        'open': prices,
        'high': [p + 0.1 for p in prices],
        'low': [p - 0.1 for p in prices],
        'close': prices,
        'tick_volume': [1500] * 60,
        'rsi': rsi_values
    })
    
    # Ensure price consistency
    for i in range(len(df)):
        df.loc[i, 'low'] = min(df.loc[i, 'low'], df.loc[i, 'close'])
        df.loc[i, 'high'] = max(df.loc[i, 'high'], df.loc[i, 'close'])
    
    return df

def debug_divergence_detection():
    """Debug the divergence detection process step by step"""
    print("🔍 Debugging Divergence Detection")
    print("=" * 50)
    
    # Create test data
    df = create_simple_bearish_rsi_divergence()
    
    print(f"Data created: {len(df)} rows")
    print(f"Price range: {df['close'].min():.2f} - {df['close'].max():.2f}")
    print(f"RSI range: {df['rsi'].min():.2f} - {df['rsi'].max():.2f}")
    
    # Test with very relaxed config
    config = {
        'divergence_swing_strength': 2,
        'min_swing_separation': 3,
        'divergence_threshold': 0.0001,  # Very low threshold
        'validation_swings': 2,
        'rsi_period': 14
    }
    
    detector = DivergenceDetector(config)
    
    # Step 1: Check swing point detection
    print("\n🎯 Step 1: Swing Point Detection")
    price_highs = detector._find_swing_points(df, 'high', 'high')
    price_lows = detector._find_swing_points(df, 'low', 'low')
    rsi_highs = detector._find_swing_points(df, 'rsi', 'high')
    rsi_lows = detector._find_swing_points(df, 'rsi', 'low')
    
    print(f"Price highs found: {len(price_highs)}")
    for i, swing in enumerate(price_highs):
        print(f"  High {i+1}: Index {swing.index}, Price {swing.price:.2f}")
    
    print(f"RSI highs found: {len(rsi_highs)}")
    for i, swing in enumerate(rsi_highs):
        print(f"  RSI High {i+1}: Index {swing.index}, RSI {swing.indicator_value:.2f}")
    
    # Step 2: Test divergence detection
    print("\n🎯 Step 2: Divergence Detection")
    result = detector.detect_rsi_divergence(df)
    
    if result:
        print(f"✅ Divergence detected: {result.divergence_type}")
        print(f"Strength: {result.strength:.3f}")
        print(f"Validated: {result.validated}")
        print(f"Price points: {result.price_points}")
        print(f"RSI points: {result.indicator_points}")
    else:
        print("❌ No divergence detected")
        
        # Debug the detection process
        print("\n🔍 Debugging detection process...")
        
        # Try manual bearish divergence detection
        if len(price_highs) >= 2 and len(rsi_highs) >= 2:
            print("Sufficient swing points found, checking patterns...")
            
            # Check recent highs
            for i in range(max(0, len(price_highs) - 3), len(price_highs) - 1):
                for j in range(i + 1, len(price_highs)):
                    price_swing1 = price_highs[i]
                    price_swing2 = price_highs[j]
                    
                    print(f"\nChecking price swings {i} and {j}:")
                    print(f"  Price 1: {price_swing1.price:.2f} at index {price_swing1.index}")
                    print(f"  Price 2: {price_swing2.price:.2f} at index {price_swing2.index}")
                    print(f"  Price higher: {price_swing2.price > price_swing1.price}")
                    
                    # Find corresponding RSI swings
                    rsi_swing1 = detector._find_closest_indicator_swing(price_swing1, rsi_highs)
                    rsi_swing2 = detector._find_closest_indicator_swing(price_swing2, rsi_highs)
                    
                    if rsi_swing1 and rsi_swing2:
                        print(f"  RSI 1: {rsi_swing1.indicator_value:.2f} at index {rsi_swing1.index}")
                        print(f"  RSI 2: {rsi_swing2.indicator_value:.2f} at index {rsi_swing2.index}")
                        print(f"  RSI lower: {rsi_swing2.indicator_value < rsi_swing1.indicator_value}")
                        
                        # Check separation
                        separation = abs(price_swing2.index - price_swing1.index)
                        print(f"  Separation: {separation} (min required: {config['min_swing_separation']})")
                        
                        if separation >= config['min_swing_separation']:
                            price_higher = price_swing2.price > price_swing1.price
                            rsi_lower = rsi_swing2.indicator_value < rsi_swing1.indicator_value
                            
                            if price_higher and rsi_lower:
                                print("  ✅ Bearish divergence pattern found!")
                                
                                # Check thresholds
                                price_change = (price_swing2.price - price_swing1.price) / price_swing1.price
                                rsi_change = abs(rsi_swing2.indicator_value - rsi_swing1.indicator_value) / 100
                                
                                print(f"  Price change: {price_change:.4f} (threshold: {config['divergence_threshold']})")
                                print(f"  RSI change: {rsi_change:.4f} (threshold: {config['divergence_threshold']})")
                                
                                if price_change > config['divergence_threshold'] and rsi_change > config['divergence_threshold']:
                                    print("  ✅ Thresholds met!")
                                else:
                                    print("  ❌ Thresholds not met")
                            else:
                                print("  ❌ Not a bearish divergence pattern")
                    else:
                        print("  ❌ Could not find corresponding RSI swings")
        else:
            print("❌ Insufficient swing points")
    
    # Step 3: Test validation separately
    if result:
        print("\n🎯 Step 3: Validation Testing")
        validation_result = detector.validate_divergence(result)
        print(f"Validation result: {validation_result}")
        
        if not validation_result:
            print("Checking validation criteria...")
            
            # Check strength threshold
            print(f"Strength: {result.strength:.3f} (min: 0.2)")
            
            # Check swing points
            print(f"Price points: {len(result.price_points)} (min: 2)")
            print(f"Indicator points: {len(result.indicator_points)} (min: 2)")
            
            if len(result.price_points) >= 2 and len(result.indicator_points) >= 2:
                # Check magnitude
                price_change = abs(result.price_points[-1][1] - result.price_points[0][1]) / result.price_points[0][1]
                indicator_change = abs(result.indicator_points[-1][1] - result.indicator_points[0][1]) / 100
                
                print(f"Price magnitude: {price_change:.4f} (min: 0.005)")
                print(f"Indicator magnitude: {indicator_change:.4f} (min: 0.005)")
                
                # Check direction
                price_direction = 1 if result.price_points[-1][1] > result.price_points[0][1] else -1
                indicator_direction = 1 if result.indicator_points[-1][1] > result.indicator_points[0][1] else -1
                
                print(f"Price direction: {price_direction}")
                print(f"Indicator direction: {indicator_direction}")
                print(f"Opposite directions: {price_direction != indicator_direction}")

def main():
    debug_divergence_detection()

if __name__ == "__main__":
    main()