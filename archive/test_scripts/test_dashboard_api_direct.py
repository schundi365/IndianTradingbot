#!/usr/bin/env python3
"""
Test script to check what the web dashboard API returns
"""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.append('src')

# Import web dashboard components
from web_dashboard import config_manager, current_config

def test_dashboard_api():
    """Test what values the dashboard API returns"""
    
    print("="*80)
    print("TESTING WEB DASHBOARD API VALUES")
    print("="*80)
    
    # Test 1: Dashboard's config_manager
    print("\n1. DASHBOARD config_manager VALUES:")
    try:
        config = config_manager.get_config()
        print(f"   RSI Overbought: {config.get('rsi_overbought', 'NOT FOUND')}")
        print(f"   RSI Oversold: {config.get('rsi_oversold', 'NOT FOUND')}")
        print(f"   MACD Min Histogram: {config.get('macd_min_histogram', 'NOT FOUND')}")
    except Exception as e:
        print(f"   ERROR with dashboard config_manager: {e}")
    
    # Test 2: Dashboard's current_config
    print("\n2. DASHBOARD current_config VALUES:")
    try:
        print(f"   RSI Overbought: {current_config.get('rsi_overbought', 'NOT FOUND')}")
        print(f"   RSI Oversold: {current_config.get('rsi_oversold', 'NOT FOUND')}")
        print(f"   MACD Min Histogram: {current_config.get('macd_min_histogram', 'NOT FOUND')}")
    except Exception as e:
        print(f"   ERROR with dashboard current_config: {e}")
    
    # Test 3: Force reload current_config
    print("\n3. FORCE RELOAD current_config:")
    try:
        import web_dashboard
        web_dashboard.current_config = web_dashboard.config_manager.get_config()
        
        print(f"   RSI Overbought: {web_dashboard.current_config.get('rsi_overbought', 'NOT FOUND')}")
        print(f"   RSI Oversold: {web_dashboard.current_config.get('rsi_oversold', 'NOT FOUND')}")
        print(f"   MACD Min Histogram: {web_dashboard.current_config.get('macd_min_histogram', 'NOT FOUND')}")
    except Exception as e:
        print(f"   ERROR with force reload: {e}")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    test_dashboard_api()