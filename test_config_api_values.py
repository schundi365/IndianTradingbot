#!/usr/bin/env python3
"""
Test script to check what values the config API is returning
"""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.append('src')

from config_manager import get_config_manager, get_config

def test_config_values():
    """Test what values are being returned by config manager"""
    
    print("="*80)
    print("TESTING CONFIG API VALUES")
    print("="*80)
    
    # Test 1: Direct bot_config.json reading
    print("\n1. DIRECT bot_config.json VALUES:")
    try:
        with open('bot_config.json', 'r') as f:
            direct_config = json.load(f)
        print(f"   RSI Overbought: {direct_config.get('rsi_overbought', 'NOT FOUND')}")
        print(f"   RSI Oversold: {direct_config.get('rsi_oversold', 'NOT FOUND')}")
        print(f"   MACD Min Histogram: {direct_config.get('macd_min_histogram', 'NOT FOUND')}")
    except Exception as e:
        print(f"   ERROR reading bot_config.json: {e}")
    
    # Test 2: Config Manager values
    print("\n2. CONFIG MANAGER VALUES:")
    try:
        config_manager = get_config_manager()
        config = config_manager.get_config()
        print(f"   RSI Overbought: {config.get('rsi_overbought', 'NOT FOUND')}")
        print(f"   RSI Oversold: {config.get('rsi_oversold', 'NOT FOUND')}")
        print(f"   MACD Min Histogram: {config.get('macd_min_histogram', 'NOT FOUND')}")
    except Exception as e:
        print(f"   ERROR with config manager: {e}")
    
    # Test 3: get_config() function
    print("\n3. get_config() FUNCTION VALUES:")
    try:
        config = get_config()
        print(f"   RSI Overbought: {config.get('rsi_overbought', 'NOT FOUND')}")
        print(f"   RSI Oversold: {config.get('rsi_oversold', 'NOT FOUND')}")
        print(f"   MACD Min Histogram: {config.get('macd_min_histogram', 'NOT FOUND')}")
    except Exception as e:
        print(f"   ERROR with get_config(): {e}")
    
    # Test 4: Force reload config manager
    print("\n4. FORCE RELOAD CONFIG MANAGER:")
    try:
        # Clear the global instance
        import src.config_manager as cm
        cm._config_manager = None
        
        # Get fresh instance
        config_manager = get_config_manager()
        config = config_manager.get_config()
        print(f"   RSI Overbought: {config.get('rsi_overbought', 'NOT FOUND')}")
        print(f"   RSI Oversold: {config.get('rsi_oversold', 'NOT FOUND')}")
        print(f"   MACD Min Histogram: {config.get('macd_min_histogram', 'NOT FOUND')}")
    except Exception as e:
        print(f"   ERROR with force reload: {e}")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    test_config_values()