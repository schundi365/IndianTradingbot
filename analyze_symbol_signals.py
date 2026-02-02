#!/usr/bin/env python3
"""
Analyze why only EURJPY is generating successful trades
"""

import re
from collections import defaultdict

def analyze_signal_patterns():
    """Analyze signal generation patterns across symbols"""
    
    try:
        with open('trading_bot.log', 'r', encoding='utf-8', errors='ignore') as f:
            log_content = f.read()
    except Exception as e:
        print(f"Error reading log file: {e}")
        return
    
    # Track signal generation by symbol
    signals_generated = defaultdict(int)
    signals_rejected = defaultdict(list)
    signals_successful = defaultdict(int)
    
    # Find all signal generations
    signal_pattern = r'Signal for (\w+): (BUY|SELL)'
    for match in re.finditer(signal_pattern, log_content):
        symbol = match.group(1)
        signal_type = match.group(2)
        signals_generated[symbol] += 1
    
    # Find rejections
    rejection_patterns = [
        (r'(\w+).*MACD FILTER REJECTED', 'MACD Filter'),
        (r'(\w+).*RSI FILTER REJECTED', 'RSI Filter'),
        (r'Trade rejected by adaptive risk manager.*for (\w+)', 'Low Confidence'),
        (r'TRADE REJECTED by price level protection.*(\w+)', 'Price Protection'),
        (r'(\w+).*momentum insufficient', 'Insufficient Momentum')
    ]
    
    for pattern, reason in rejection_patterns:
        for match in re.finditer(pattern, log_content):
            symbol = match.group(1)
            signals_rejected[symbol].append(reason)
    
    # Find successful trades
    success_pattern = r'Split positions opened successfully.*Completed analysis for (\w+)'
    for match in re.finditer(success_pattern, log_content):
        symbol = match.group(1)
        signals_successful[symbol] += 1
    
    print("=" * 80)
    print("SIGNAL ANALYSIS REPORT")
    print("=" * 80)
    
    print("\n📊 SIGNAL GENERATION BY SYMBOL:")
    for symbol, count in sorted(signals_generated.items(), key=lambda x: x[1], reverse=True):
        success_rate = (signals_successful[symbol] / count * 100) if count > 0 else 0
        print(f"  {symbol:10} | Generated: {count:3} | Successful: {signals_successful[symbol]:3} | Success Rate: {success_rate:5.1f}%")
    
    print("\n❌ REJECTION REASONS BY SYMBOL:")
    for symbol in sorted(signals_rejected.keys()):
        rejection_counts = defaultdict(int)
        for reason in signals_rejected[symbol]:
            rejection_counts[reason] += 1
        
        print(f"\n  {symbol}:")
        for reason, count in sorted(rejection_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"    - {reason}: {count} times")
    
    print("\n🎯 TOP PERFORMING SYMBOLS:")
    successful_symbols = [(symbol, count) for symbol, count in signals_successful.items() if count > 0]
    for symbol, count in sorted(successful_symbols, key=lambda x: x[1], reverse=True):
        print(f"  {symbol}: {count} successful trades")
    
    print("\n💡 RECOMMENDATIONS:")
    
    # Check if EURJPY is dominating
    total_successful = sum(signals_successful.values())
    eurjpy_successful = signals_successful.get('EURJPY', 0)
    
    if eurjpy_successful > total_successful * 0.8:
        print("  ⚠️  EURJPY is dominating (>80% of successful trades)")
        print("     Consider:")
        print("     1. Lowering MACD threshold to allow more symbols")
        print("     2. Reducing confidence threshold")
        print("     3. Adjusting RSI ranges")
        print("     4. Checking if EURJPY has favorable market conditions")
    
    # Check for symbols with high generation but low success
    print("\n  📈 Symbols with potential (high signals, low success):")
    for symbol, generated in signals_generated.items():
        successful = signals_successful[symbol]
        if generated >= 5 and successful == 0:
            print(f"     {symbol}: {generated} signals generated, 0 successful")
            main_rejections = defaultdict(int)
            for reason in signals_rejected[symbol]:
                main_rejections[reason] += 1
            if main_rejections:
                top_reason = max(main_rejections.items(), key=lambda x: x[1])
                print(f"       Main issue: {top_reason[0]} ({top_reason[1]} times)")

if __name__ == "__main__":
    analyze_signal_patterns()