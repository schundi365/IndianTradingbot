#!/usr/bin/env python3
"""
Detailed debug script to trace the exact location of the 'bool' object is not callable issue
"""

import sys
import traceback
import logging
sys.path.append('src')

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

def debug_with_detailed_trace():
    """Debug with detailed tracing"""
    
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
        
        # Create minimal test data
        import pandas as pd
        import numpy as np
        from datetime import datetime, timedelta
        
        dates = pd.date_range(start=datetime.now() - timedelta(days=50), periods=50, freq='1h')
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
        
        print("🔧 Attempting analysis with detailed tracing...")
        
        # Monkey patch to add tracing
        original_perform_analysis = engine._perform_analysis_with_error_handling
        
        def traced_perform_analysis(df, symbol):
            print(f"📍 Entering _perform_analysis_with_error_handling for {symbol}")
            try:
                return original_perform_analysis(df, symbol)
            except Exception as e:
                print(f"📍 Exception in _perform_analysis_with_error_handling: {e}")
                print(f"📍 Exception type: {type(e)}")
                
                # Print detailed traceback
                tb = traceback.extract_tb(e.__traceback__)
                print("📍 Detailed traceback:")
                for i, frame in enumerate(tb):
                    print(f"   {i}: {frame.filename}:{frame.lineno} in {frame.name}")
                    print(f"      {frame.line}")
                    
                    # Look for the specific error
                    if "'bool' object is not callable" in str(e) and 'is_component_available' in frame.line:
                        print(f"   🎯 FOUND THE ISSUE AT: {frame.filename}:{frame.lineno}")
                        print(f"      Line: {frame.line}")
                
                raise
        
        engine._perform_analysis_with_error_handling = traced_perform_analysis
        
        try:
            result = engine.analyze_trend_change(df, 'TEST')
            print(f"✅ Analysis completed: {len(result.signals)} signals, confidence={result.confidence:.2f}")
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            print(f"   Full traceback: {traceback.format_exc()}")
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        print(f"   Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    debug_with_detailed_trace()