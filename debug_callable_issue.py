#!/usr/bin/env python3
"""
Debug script to identify the 'bool' object is not callable issue
"""

import sys
import traceback
sys.path.append('src')

def debug_trend_detection_engine():
    """Debug the TrendDetectionEngine initialization and method calls"""
    
    try:
        from src.trend_detection_engine import TrendDetectionEngine
        
        # Test configuration
        test_config = {
            'use_trend_detection': True,
            'trend_detection_sensitivity': 5,
            'min_trend_confidence': 0.6,
            'enable_early_signals': True,
            'logging_level': 'debug'
        }
        
        print("🔧 Creating TrendDetectionEngine...")
        engine = TrendDetectionEngine(test_config)
        
        print("✅ Engine created successfully")
        
        # Check if is_component_available is callable
        print(f"📋 is_component_available type: {type(engine.is_component_available)}")
        print(f"📋 is_component_available callable: {callable(engine.is_component_available)}")
        
        # Test calling the method
        print("🔧 Testing is_component_available method...")
        try:
            result = engine.is_component_available('market_structure')
            print(f"✅ is_component_available('market_structure') = {result}")
        except Exception as e:
            print(f"❌ Error calling is_component_available: {e}")
            print(f"   Traceback: {traceback.format_exc()}")
        
        # Check component status
        print("📊 Component status:")
        status = engine.get_component_status()
        for name, stat in status.items():
            print(f"   {name}: {stat}")
        
        # Test with simple data
        import pandas as pd
        import numpy as np
        from datetime import datetime, timedelta
        
        print("\n🔧 Testing with simple data...")
        
        # Create minimal test data
        dates = pd.date_range(start=datetime.now() - timedelta(days=50), periods=50, freq='1H')
        df = pd.DataFrame({
            'open': np.random.uniform(2000, 2010, 50),
            'high': np.random.uniform(2005, 2015, 50),
            'low': np.random.uniform(1995, 2005, 50),
            'close': np.random.uniform(2000, 2010, 50),
            'tick_volume': np.random.randint(100, 1000, 50)
        }, index=dates)
        
        # Ensure OHLC relationships are valid
        df['high'] = df[['open', 'high', 'close']].max(axis=1)
        df['low'] = df[['open', 'low', 'close']].min(axis=1)
        
        print(f"📊 Test data shape: {df.shape}")
        print(f"📊 Test data columns: {list(df.columns)}")
        
        # Try analysis
        print("🔧 Attempting trend analysis...")
        try:
            result = engine.analyze_trend_change(df, 'TEST')
            print(f"✅ Analysis completed: {len(result.signals)} signals, confidence={result.confidence:.2f}")
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            print(f"   Traceback: {traceback.format_exc()}")
            
            # Try to identify the exact line causing the issue
            tb = traceback.extract_tb(e.__traceback__)
            for frame in tb:
                if 'is_component_available' in frame.line:
                    print(f"   Problem line: {frame.filename}:{frame.lineno} - {frame.line}")
        
    except Exception as e:
        print(f"❌ Failed to create engine: {e}")
        print(f"   Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    debug_trend_detection_engine()