#!/usr/bin/env python3
"""
Debug script to check component attributes
"""

import sys
sys.path.append('src')

def debug_component_attributes():
    """Debug component attribute setting"""
    
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
        
        print("📊 Checking component attributes...")
        
        # Check what attributes exist
        component_attrs = [
            'market_structure_analyzer',
            'aroon_indicator', 
            'ema_analyzer',
            'ema_momentum_analyzer',
            'divergence_detector',
            'multi_timeframe_analyzer',
            'trendline_analyzer'
        ]
        
        for attr in component_attrs:
            has_attr = hasattr(engine, attr)
            if has_attr:
                value = getattr(engine, attr)
                print(f"   ✅ {attr}: {type(value)} - {value is not None}")
            else:
                print(f"   ❌ {attr}: NOT FOUND")
        
        # Check component status
        print("\n📊 Component status:")
        status = engine.get_component_status()
        for name, stat in status.items():
            print(f"   {name}: {stat}")
        
        # Check all attributes that contain 'analyzer' or 'indicator'
        print("\n📊 All analyzer/indicator attributes:")
        for attr_name in dir(engine):
            if 'analyzer' in attr_name or 'indicator' in attr_name:
                attr_value = getattr(engine, attr_name)
                print(f"   {attr_name}: {type(attr_value)}")
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    debug_component_attributes()