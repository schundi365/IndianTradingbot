#!/usr/bin/env python3
"""
Test Volume Analyzer Logger Fix
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_volume_analyzer_import():
    """Test that volume analyzer can be imported without logger errors"""
    print("🧪 TESTING VOLUME ANALYZER LOGGER FIX")
    print("=" * 50)
    
    try:
        from src.volume_analyzer import VolumeAnalyzer
        
        # Create a test configuration
        config = {
            'use_volume_filter': True,
            'min_volume_ma': 0.7,
            'volume_ma_period': 20
        }
        
        # Try to create volume analyzer instance
        volume_analyzer = VolumeAnalyzer(config)
        
        print("✅ Volume analyzer imported successfully")
        print("✅ Volume analyzer instance created")
        print("✅ Logger references are working correctly")
        
        # Test that the logger is properly initialized
        if hasattr(volume_analyzer, 'logger'):
            print("✅ Volume analyzer has logger attribute")
        else:
            print("❌ Volume analyzer missing logger attribute")
            return False
        
        print("🎉 Volume analyzer logger fix verified!")
        return True
        
    except NameError as e:
        if "logger" in str(e):
            print(f"❌ Logger error still exists: {e}")
            return False
        else:
            print(f"❌ Other NameError: {e}")
            return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_volume_analyzer_import()
    if success:
        print("\n🎉 VOLUME ANALYZER LOGGER FIX VERIFIED!")
        print("The bot should now process EURJPY without logger errors")
    else:
        print("\n❌ VOLUME ANALYZER LOGGER FIX FAILED!")
        print("Additional fixes may be needed")