#!/usr/bin/env python3
"""
Check why only EURJPY is getting trades
"""

import json

def analyze_configuration():
    """Analyze configuration for symbol bias"""
    
    try:
        with open('bot_config.json', 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error reading config: {e}")
        return
    
    print("=" * 80)
    print("CONFIGURATION ANALYSIS - WHY ONLY EURJPY?")
    print("=" * 80)
    
    print(f"\n📊 CONFIGURED SYMBOLS ({len(config['symbols'])}):")
    for i, symbol in enumerate(config['symbols'], 1):
        print(f"  {i:2}. {symbol}")
    
    print(f"\n🎯 FILTER SETTINGS:")
    print(f"  Risk per trade: {config['risk_percent']}%")
    print(f"  Min confidence: {config['min_trade_confidence']*100}%")
    print(f"  MACD min histogram: {config['macd_min_histogram']}")
    print(f"  RSI overbought: {config['rsi_overbought']}")
    print(f"  RSI oversold: {config['rsi_oversold']}")
    print(f"  Use volume filter: {config['use_volume_filter']}")
    print(f"  Max trades per symbol: {config['max_trades_per_symbol']}")
    
    print(f"\n⚙️  POTENTIAL ISSUES:")
    
    # Check if confidence threshold is too high
    if config['min_trade_confidence'] > 0.6:
        print(f"  ⚠️  High confidence threshold ({config['min_trade_confidence']*100}%) may reject many trades")
    
    # Check MACD threshold
    if config['macd_min_histogram'] > 0.0005:
        print(f"  ⚠️  High MACD threshold ({config['macd_min_histogram']}) may reject weak signals")
    
    # Check if volume filter is too strict
    if config['use_volume_filter']:
        print(f"  ⚠️  Volume filter enabled - may reject low volume periods")
    
    # Check symbol-specific settings
    if 'symbol_tp_levels' in config:
        print(f"\n📈 SYMBOL-SPECIFIC TP LEVELS:")
        for symbol, levels in config['symbol_tp_levels'].items():
            if symbol in ['EURJPY', 'EURUSD', 'GBPUSD', 'USDJPY']:
                print(f"  {symbol}: {levels}")
    
    print(f"\n💡 RECOMMENDATIONS TO INCREASE SIGNAL DIVERSITY:")
    print(f"  1. Lower min_trade_confidence from {config['min_trade_confidence']} to 0.4")
    print(f"  2. Lower macd_min_histogram from {config['macd_min_histogram']} to 0.0002")
    print(f"  3. Disable volume filter temporarily: use_volume_filter = false")
    print(f"  4. Check if EURJPY has particularly favorable market conditions")
    
    return config

def check_recent_market_conditions():
    """Check recent market analysis from logs"""
    
    print(f"\n📊 RECENT MARKET CONDITIONS:")
    
    try:
        with open('trading_bot.log', 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading logs: {e}")
        return
    
    # Get recent analysis for different symbols
    symbols_analyzed = {}
    
    for line in reversed(lines[-1000:]):  # Check last 1000 lines
        if "ANALYZING" in line and "║" in line:
            # Extract symbol from analysis header
            if "XAUUSD" in line:
                symbols_analyzed["XAUUSD"] = "Recently analyzed"
            elif "EURUSD" in line:
                symbols_analyzed["EURUSD"] = "Recently analyzed"
            elif "EURJPY" in line:
                symbols_analyzed["EURJPY"] = "Recently analyzed"
            elif "GBPUSD" in line:
                symbols_analyzed["GBPUSD"] = "Recently analyzed"
        
        # Check for rejection reasons
        if "MACD FILTER REJECTED" in line:
            for symbol in ["XAUUSD", "EURUSD", "EURJPY", "GBPUSD", "USDJPY"]:
                if symbol in line:
                    symbols_analyzed[symbol] = "MACD rejected"
        
        if "RSI FILTER REJECTED" in line:
            for symbol in ["XAUUSD", "EURUSD", "EURJPY", "GBPUSD", "USDJPY"]:
                if symbol in line:
                    symbols_analyzed[symbol] = "RSI rejected"
    
    for symbol, status in symbols_analyzed.items():
        print(f"  {symbol}: {status}")

if __name__ == "__main__":
    config = analyze_configuration()
    check_recent_market_conditions()
    
    print(f"\n🔧 QUICK FIX SUGGESTIONS:")
    print(f"  To get more diverse signals, try these settings:")
    print(f"  - min_trade_confidence: 0.4 (currently {config['min_trade_confidence']})")
    print(f"  - macd_min_histogram: 0.0002 (currently {config['macd_min_histogram']})")
    print(f"  - use_volume_filter: false (currently {config['use_volume_filter']})")
    print(f"  - rsi_overbought: 70 (currently {config['rsi_overbought']})")
    print(f"  - rsi_oversold: 30 (currently {config['rsi_oversold']})")