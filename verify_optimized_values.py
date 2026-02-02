#!/usr/bin/env python3
"""
Verify Optimized Values - Confirm All RSI/MACD/Volume Improvements Are Active
"""

import json
import sys
from pathlib import Path

def verify_config_file():
    """Verify bot_config.json has correct optimized values"""
    print("🔍 VERIFYING BOT_CONFIG.JSON")
    print("=" * 50)
    
    try:
        with open('bot_config.json', 'r') as f:
            config = json.load(f)
        
        # Check RSI values
        rsi_overbought = config.get('rsi_overbought')
        rsi_oversold = config.get('rsi_oversold')
        
        print(f"RSI Overbought: {rsi_overbought} {'✅' if rsi_overbought == 75 else '❌'}")
        print(f"RSI Oversold: {rsi_oversold} {'✅' if rsi_oversold == 25 else '❌'}")
        
        # Check MACD values
        macd_histogram = config.get('macd_min_histogram')
        print(f"MACD Min Histogram: {macd_histogram} {'✅' if macd_histogram == 0.0005 else '❌'}")
        
        # Check Volume values
        min_volume_ma = config.get('min_volume_ma')
        print(f"Min Volume MA: {min_volume_ma} {'✅' if min_volume_ma == 0.7 else '❌'}")
        
        # Check confidence
        min_confidence = config.get('min_trade_confidence')
        print(f"Min Trade Confidence: {min_confidence} {'✅' if min_confidence == 0.6 else '❌'}")
        
        return all([
            rsi_overbought == 75,
            rsi_oversold == 25,
            macd_histogram == 0.0005,
            min_volume_ma == 0.7,
            min_confidence == 0.6
        ])
        
    except Exception as e:
        print(f"❌ Error reading config: {e}")
        return False

def verify_trading_bot_defaults():
    """Verify trading bot has correct default values"""
    print("\n🔍 VERIFYING TRADING BOT DEFAULTS")
    print("=" * 50)
    
    try:
        with open('src/mt5_trading_bot.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for correct default values
        has_75_default = "rsi_overbought', 75)" in content
        has_25_default = "rsi_oversold', 25)" in content
        
        print(f"RSI Overbought Default 75: {'✅' if has_75_default else '❌'}")
        print(f"RSI Oversold Default 25: {'✅' if has_25_default else '❌'}")
        
        return has_75_default and has_25_default
        
    except Exception as e:
        print(f"❌ Error reading trading bot: {e}")
        return False

def verify_rsi_momentum_logic():
    """Verify RSI momentum logic is implemented"""
    print("\n🔍 VERIFYING RSI MOMENTUM LOGIC")
    print("=" * 50)
    
    try:
        with open('src/mt5_trading_bot.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for momentum confirmation logic
        has_buy_momentum = "if rsi < 50:" in content and "too weak for BUY" in content
        has_sell_momentum = "if rsi > 50:" in content and "too strong for SELL" in content
        has_range_logging = "RSI range 50-" in content and "RSI range" in content
        
        print(f"BUY Momentum Check (RSI < 50): {'✅' if has_buy_momentum else '❌'}")
        print(f"SELL Momentum Check (RSI > 50): {'✅' if has_sell_momentum else '❌'}")
        print(f"Range Logging: {'✅' if has_range_logging else '❌'}")
        
        return has_buy_momentum and has_sell_momentum and has_range_logging
        
    except Exception as e:
        print(f"❌ Error checking RSI logic: {e}")
        return False

def main():
    """Main verification function"""
    print("🚀 OPTIMIZED VALUES VERIFICATION")
    print("=" * 60)
    print()
    
    # Run all verifications
    config_ok = verify_config_file()
    defaults_ok = verify_trading_bot_defaults()
    logic_ok = verify_rsi_momentum_logic()
    
    print("\n" + "=" * 60)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 60)
    
    print(f"Configuration File: {'✅ PASS' if config_ok else '❌ FAIL'}")
    print(f"Trading Bot Defaults: {'✅ PASS' if defaults_ok else '❌ FAIL'}")
    print(f"RSI Momentum Logic: {'✅ PASS' if logic_ok else '❌ FAIL'}")
    
    overall_status = config_ok and defaults_ok and logic_ok
    
    print(f"\n🎯 OVERALL STATUS: {'✅ ALL OPTIMIZATIONS ACTIVE' if overall_status else '❌ ISSUES FOUND'}")
    
    if overall_status:
        print("\n🎉 SUCCESS! All optimized values are correctly configured:")
        print("   • RSI: 75/25 with momentum confirmation (50-75 BUY, 25-50 SELL)")
        print("   • MACD: 0.0005 threshold (highly sensitive)")
        print("   • Volume: 0.7 threshold (balanced quality)")
        print("   • Confidence: 60% (balanced selectivity)")
        print("\n✅ The bot is ready for optimal trading performance!")
    else:
        print("\n⚠️  Some issues were found. Please check the details above.")
    
    return overall_status

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)