#!/usr/bin/env python3
"""
Verify All Improvements Are Active

This script checks that all the improvements we made are properly
implemented and ready to use.
"""

import json
import os
import sys

def verify_configuration():
    """Verify the bot configuration has optimized values"""
    print("🔧 VERIFYING CONFIGURATION...")
    
    try:
        with open('bot_config.json', 'r') as f:
            config = json.load(f)
        
        checks = [
            ('MACD Min Histogram', config.get('macd_min_histogram'), 0.0005, '=='),
            ('Min Volume MA', config.get('min_volume_ma'), 0.7, '=='),
            ('Timeframe', config.get('timeframe'), 15, '=='),
            ('RSI Overbought', config.get('rsi_overbought'), 70, '=='),
            ('RSI Oversold', config.get('rsi_oversold'), 30, '=='),
            ('Min Trade Confidence', config.get('min_trade_confidence'), 0.5, '=='),
        ]
        
        all_good = True
        for name, actual, expected, op in checks:
            if op == '==' and actual == expected:
                print(f"   ✅ {name}: {actual} (correct)")
            else:
                print(f"   ❌ {name}: {actual} (expected {expected})")
                all_good = False
        
        return all_good
        
    except Exception as e:
        print(f"   ❌ Error reading config: {e}")
        return False

def verify_enhanced_logging():
    """Verify enhanced logging is implemented"""
    print("\n📊 VERIFYING ENHANCED LOGGING...")
    
    try:
        with open('src/mt5_trading_bot.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = [
            ('Enhanced Formatter', 'class EnhancedFormatter'),
            ('Performance Timer', '@performance_timer'),
            ('5-Method Signal Generation', 'METHOD 5: CHECKING BREAKOUT SIGNALS'),
            ('Detailed Indicator Logging', '🔧 DETAILED TECHNICAL INDICATOR VALUES'),
            ('Volume Analysis Breakdown', 'DETAILED VOLUME BREAKDOWN'),
        ]
        
        all_good = True
        for name, pattern in checks:
            if pattern in content:
                print(f"   ✅ {name}: Implemented")
            else:
                print(f"   ❌ {name}: Not found")
                all_good = False
        
        return all_good
        
    except Exception as e:
        print(f"   ❌ Error reading trading bot: {e}")
        return False

def verify_dashboard_improvements():
    """Verify dashboard has optimized defaults and logging controls"""
    print("\n🌐 VERIFYING DASHBOARD IMPROVEMENTS...")
    
    try:
        with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = [
            ('M15 Selected by Default', 'value="15" selected'),
            ('Confidence 50% Default', 'id="min-confidence" value="50"'),
            ('MACD 0.0005 Default', 'id="macd-min-histogram".*value="0.0005"'),
            ('Volume 0.7 Default', 'id="min-volume-ma".*value="0.7"'),
            ('RSI 70 Default', 'id="rsi-overbought".*value="70"'),
            ('RSI 30 Default', 'id="rsi-oversold".*value="30"'),
            ('Logging Controls in Logs Tab', 'Logging Level Controls'),
            ('Update Logging Level Function', 'function updateLoggingLevel'),
        ]
        
        all_good = True
        for name, pattern in checks:
            if pattern in content:
                print(f"   ✅ {name}: Implemented")
            else:
                print(f"   ❌ {name}: Not found")
                all_good = False
        
        return all_good
        
    except Exception as e:
        print(f"   ❌ Error reading dashboard: {e}")
        return False

def verify_files_exist():
    """Verify all required files exist"""
    print("\n📁 VERIFYING REQUIRED FILES...")
    
    required_files = [
        'src/mt5_trading_bot.py',
        'templates/dashboard.html',
        'web_dashboard.py',
        'bot_config.json',
        'run_bot.py',
        'src/volume_analyzer.py',
    ]
    
    all_good = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}: Exists")
        else:
            print(f"   ❌ {file_path}: Missing")
            all_good = False
    
    return all_good

def main():
    print("🚀 VERIFYING ALL IMPROVEMENTS")
    print("="*60)
    
    results = []
    
    # Run all verifications
    results.append(verify_files_exist())
    results.append(verify_configuration())
    results.append(verify_enhanced_logging())
    results.append(verify_dashboard_improvements())
    
    # Summary
    print("\n" + "="*60)
    if all(results):
        print("🎉 ALL IMPROVEMENTS VERIFIED SUCCESSFULLY!")
        print("\n✅ READY TO RESTART SERVICES:")
        print("1. python web_dashboard.py")
        print("2. python run_bot.py")
        print("\n🎯 EXPECTED BENEFITS:")
        print("• 4x more frequent analysis (M15)")
        print("• 5-method signal generation")
        print("• Enhanced logging with line numbers")
        print("• Optimized defaults in dashboard")
        print("• Logging controls in System Logs tab")
        return True
    else:
        print("❌ SOME IMPROVEMENTS NOT VERIFIED!")
        print("Please check the issues above before restarting.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)