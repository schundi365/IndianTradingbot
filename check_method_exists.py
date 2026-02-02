#!/usr/bin/env python3
"""
Check if the method exists
"""

import sys
import os
sys.path.append('src')

def check_method():
    try:
        from mt5_trading_bot import MT5TradingBot
        
        # Check if method exists
        if hasattr(MT5TradingBot, 'calculate_indicators_with_logging'):
            print("✅ Method calculate_indicators_with_logging EXISTS")
            
            # Check method signature
            method = getattr(MT5TradingBot, 'calculate_indicators_with_logging')
            print(f"   Method: {method}")
            print(f"   Type: {type(method)}")
            
            # Check if it's callable
            if callable(method):
                print("✅ Method is callable")
            else:
                print("❌ Method is not callable")
                
        else:
            print("❌ Method calculate_indicators_with_logging DOES NOT EXIST")
            
        # List all methods that contain 'calculate'
        print("\n📋 All methods containing 'calculate':")
        for attr_name in dir(MT5TradingBot):
            if 'calculate' in attr_name.lower():
                attr = getattr(MT5TradingBot, attr_name)
                if callable(attr):
                    print(f"   ✅ {attr_name}")
                    
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    check_method()