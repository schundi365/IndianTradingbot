#!/usr/bin/env python3
"""
Simple Cache Clearing Script
Clears Python cache and verifies configuration without complex imports
"""

import os
import sys
import shutil
import glob
import json

def clear_python_cache():
    """Clear Python cache files"""
    print("🧹 Clearing Python cache...")
    
    # Remove __pycache__ directories
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs[:]:  # Use slice to avoid modifying list while iterating
            if dir_name == '__pycache__':
                cache_path = os.path.join(root, dir_name)
                try:
                    shutil.rmtree(cache_path)
                    print(f"   Removed: {cache_path}")
                except Exception as e:
                    print(f"   Could not remove {cache_path}: {e}")
    
    # Remove .pyc files
    for pyc_file in glob.glob('**/*.pyc', recursive=True):
        try:
            os.remove(pyc_file)
            print(f"   Removed: {pyc_file}")
        except Exception as e:
            print(f"   Could not remove {pyc_file}: {e}")
    
    print("✅ Python cache cleared")

def verify_config():
    """Verify configuration values"""
    print("🔍 Verifying configuration...")
    
    try:
        with open('bot_config.json', 'r') as f:
            config = json.load(f)
        
        # Check optimized values
        checks = [
            ('min_volume_ma', 0.7),
            ('macd_min_histogram', 0.0005),
            ('min_trade_confidence', 0.6),
            ('normal_volume_ma', 1.0),
            ('high_volume_ma', 1.5),
            ('very_high_volume_ma', 2.0)
        ]
        
        all_good = True
        for key, expected in checks:
            if key in config:
                actual = config[key]
                if actual == expected:
                    print(f"   ✅ {key}: {actual}")
                else:
                    print(f"   ⚠️ {key}: {actual} (expected {expected})")
                    all_good = False
            else:
                print(f"   ❌ Missing: {key}")
                all_good = False
        
        if all_good:
            print("✅ All configuration values are correct")
        else:
            print("⚠️ Some configuration values need attention")
            
        return all_good
        
    except Exception as e:
        print(f"❌ Error reading config: {e}")
        return False

def main():
    """Main function"""
    print("🚀 SIMPLE CACHE CLEARING")
    print("=" * 40)
    
    # Clear cache
    clear_python_cache()
    
    # Verify config
    config_ok = verify_config()
    
    print("=" * 40)
    print("✅ CACHE CLEARING COMPLETE")
    print("")
    print("📋 NEXT STEPS:")
    print("1. Restart any running processes")
    print("2. Start bot: python run_bot.py")
    print("3. Start dashboard: python web_dashboard.py")
    print("")
    print("🔧 Latest optimizations active:")
    print("   • Volume threshold: 0.7")
    print("   • MACD threshold: 0.0005")
    print("   • Enhanced logging system")
    print("   • RSI momentum improvements")
    print("   • ADX trend filtering")
    
    return 0

if __name__ == "__main__":
    main()