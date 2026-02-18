#!/usr/bin/env python3
"""
Test importing just the class
"""

import sys
sys.path.append('src')

try:
    print("Attempting to import...")
    from mt5_trading_bot import MT5TradingBot
    print("✅ Import successful")
    
    print("Checking class definition...")
    print(f"Class: {MT5TradingBot}")
    print(f"MRO: {MT5TradingBot.__mro__}")
    
    print("Checking methods...")
    methods = [method for method in dir(MT5TradingBot) if not method.startswith('_')]
    print(f"Total methods: {len(methods)}")
    
    for method in methods:
        if 'calculate' in method:
            print(f"  📊 {method}")
    
except SyntaxError as e:
    print(f"❌ Syntax Error: {e}")
    print(f"   File: {e.filename}")
    print(f"   Line: {e.lineno}")
    print(f"   Text: {e.text}")
    
except Exception as e:
    print(f"❌ Import Error: {e}")
    import traceback
    traceback.print_exc()