#!/usr/bin/env python3
"""
Debug script to trace config loading step by step
"""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.append('src')

def debug_config_loading():
    """Debug the config loading process step by step"""
    
    print("="*80)
    print("DEBUGGING CONFIG LOADING PROCESS")
    print("="*80)
    
    # Step 1: Check bot_config.json directly
    print("\n1. DIRECT bot_config.json CONTENT:")
    try:
        with open('bot_config.json', 'r') as f:
            file_config = json.load(f)
        print(f"   RSI Overbought in file: {file_config.get('rsi_overbought', 'NOT FOUND')}")
        print(f"   File has {len(file_config)} keys")
    except Exception as e:
        print(f"   ERROR: {e}")
        return
    
    # Step 2: Check defaults
    print("\n2. DEFAULT CONFIG VALUES:")
    from src.config_manager import ConfigManager
    temp_manager = ConfigManager.__new__(ConfigManager)  # Create without __init__
    defaults = temp_manager._get_default_config()
    print(f"   RSI Overbought in defaults: {defaults.get('rsi_overbought', 'NOT FOUND')}")
    print(f"   Defaults has {len(defaults)} keys")
    
    # Step 3: Manual merge simulation
    print("\n3. MANUAL MERGE SIMULATION:")
    merged = defaults.copy()
    print(f"   Before update - RSI Overbought: {merged.get('rsi_overbought')}")
    merged.update(file_config)
    print(f"   After update - RSI Overbought: {merged.get('rsi_overbought')}")
    print(f"   Merged has {len(merged)} keys")
    
    # Step 4: Check if there are conflicting keys
    print("\n4. CHECKING FOR CONFLICTS:")
    for key in ['rsi_overbought', 'rsi_oversold', 'macd_min_histogram']:
        default_val = defaults.get(key, 'NOT IN DEFAULTS')
        file_val = file_config.get(key, 'NOT IN FILE')
        merged_val = merged.get(key, 'NOT IN MERGED')
        
        print(f"   {key}:")
        print(f"     Default: {default_val}")
        print(f"     File: {file_val}")
        print(f"     Merged: {merged_val}")
        
        if default_val != file_val and file_val != 'NOT IN FILE':
            print(f"     ⚠️  CONFLICT DETECTED!")
    
    # Step 5: Test actual ConfigManager
    print("\n5. ACTUAL CONFIG MANAGER:")
    try:
        # Clear any cached instance
        import src.config_manager as cm
        cm._config_manager = None
        
        # Create fresh instance
        from src.config_manager import get_config_manager
        config_manager = get_config_manager()
        actual_config = config_manager.get_config()
        
        print(f"   RSI Overbought from manager: {actual_config.get('rsi_overbought')}")
        print(f"   Manager config has {len(actual_config)} keys")
        
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print("\n" + "="*80)
    print("DEBUG COMPLETE")
    print("="*80)

if __name__ == "__main__":
    debug_config_loading()