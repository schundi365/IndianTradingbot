#!/usr/bin/env python3
"""
Analyze why no trades are being placed in the last 20 hours
"""

import json
from datetime import datetime

def analyze_no_trades_issue():
    """Analyze configuration and identify potential issues"""
    
    print("="*80)
    print("ANALYZING NO TRADES ISSUE")
    print("="*80)
    
    # Read current configuration
    try:
        with open('bot_config.json', 'r') as f:
            config = json.load(f)
        
        print("CURRENT CONFIGURATION ANALYSIS:")
        print(f"   Symbols: {config.get('symbols', [])}")
        print(f"   Timeframe: M{config.get('timeframe', 'Unknown')}")
        print(f"   Min Trade Confidence: {config.get('min_trade_confidence', 'Unknown')}")
        print(f"   MACD Min Histogram: {config.get('macd_min_histogram', 'Unknown')}")
        print(f"   Volume Filter Enabled: {config.get('use_volume_filter', 'Unknown')}")
        print(f"   Min Volume MA: {config.get('min_volume_ma', 'Unknown')}")
        print(f"   RSI Overbought: {config.get('rsi_overbought', 'Unknown')}")
        print(f"   RSI Oversold: {config.get('rsi_oversold', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ Error reading config: {e}")
        return
    
    print("\nPOTENTIAL ISSUES IDENTIFIED:")
    
    # Issue 1: MACD threshold too low
    macd_threshold = config.get('macd_min_histogram', 0)
    if macd_threshold < 0.0005:
        print(f"⚠️  ISSUE 1: MACD threshold too low ({macd_threshold})")
        print(f"   Current: {macd_threshold}")
        print(f"   Recommended: 0.0005 (optimized value)")
        print(f"   Impact: MACD filter rejecting most signals")
    
    # Issue 2: Volume filter too strict
    volume_filter = config.get('use_volume_filter', False)
    min_volume_ma = config.get('min_volume_ma', 1.0)
    if volume_filter and min_volume_ma > 1.0:
        print(f"⚠️  ISSUE 2: Volume filter too strict")
        print(f"   Volume Filter Enabled: {volume_filter}")
        print(f"   Min Volume MA: {min_volume_ma}")
        print(f"   Recommended: 0.7 (optimized value)")
        print(f"   Impact: Volume filter rejecting signals in low volume periods")
    
    # Issue 3: High confidence requirement
    min_confidence = config.get('min_trade_confidence', 0.5)
    if min_confidence > 0.7:
        print(f"⚠️  ISSUE 3: Trade confidence too high")
        print(f"   Current: {min_confidence} ({min_confidence*100}%)")
        print(f"   Recommended: 0.6 (60%)")
        print(f"   Impact: Rejecting trades that don't meet high confidence threshold")
    
    # Issue 4: Crypto symbols on M30 timeframe
    symbols = config.get('symbols', [])
    timeframe = config.get('timeframe', 30)
    crypto_symbols = [s for s in symbols if any(crypto in s for crypto in ['BTC', 'ETH', 'LTC', 'XRP', 'XLM'])]
    if crypto_symbols and timeframe >= 30:
        print(f"⚠️  ISSUE 4: Crypto symbols on high timeframe")
        print(f"   Crypto Symbols: {crypto_symbols}")
        print(f"   Current Timeframe: M{timeframe}")
        print(f"   Recommended: M5 or M15 for crypto")
        print(f"   Impact: Missing fast crypto movements on slower timeframes")
    
    # Issue 5: All filters enabled (too restrictive)
    filters_enabled = []
    if config.get('use_rsi', False): filters_enabled.append('RSI')
    if config.get('use_macd', False): filters_enabled.append('MACD')
    if config.get('use_adx', False): filters_enabled.append('ADX')
    if config.get('use_trend_filter', False): filters_enabled.append('Trend')
    if config.get('use_volume_filter', False): filters_enabled.append('Volume')
    
    if len(filters_enabled) >= 4:
        print(f"⚠️  ISSUE 5: Too many filters enabled")
        print(f"   Active Filters: {', '.join(filters_enabled)}")
        print(f"   Impact: All filters must pass simultaneously, reducing signal frequency")
        print(f"   Recommendation: Disable some filters or use 'OR' logic instead of 'AND'")
    
    # Issue 6: Signal generation logic
    print(f"\n⚠️  ISSUE 6: Signal generation logic")
    print(f"   Current Logic: Waiting for MA crossover OR trend confirmation")
    print(f"   Problem: In sideways markets, no crossovers occur")
    print(f"   Recommendation: Add momentum-based signals (RSI reversals, MACD divergence)")
    
    print("\nRECOMMENDED FIXES:")
    print("1. Lower MACD threshold to 0.0005")
    print("2. Lower volume filter to 0.7 or disable temporarily")
    print("3. Reduce confidence requirement to 60%")
    print("4. Consider M15 timeframe for crypto symbols")
    print("5. Disable some filters (keep RSI + MACD only)")
    print("6. Add RSI reversal signals in oversold/overbought zones")
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)

if __name__ == "__main__":
    analyze_no_trades_issue()