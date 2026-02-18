#!/usr/bin/env python3
"""
Analyze why no trades are being placed currently
"""

import os
import re
import json
from datetime import datetime, timedelta

def analyze_recent_logs():
    """Analyze recent logs to understand why no trades are placed"""
    print("🔍 ANALYZING RECENT TRADING ACTIVITY")
    print("=" * 60)
    
    log_file = "trading_bot.log"
    if not os.path.exists(log_file):
        print("❌ Log file not found")
        return
    
    # Read recent logs
    with open(log_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Get last 500 lines for analysis
    recent_lines = lines[-500:] if len(lines) > 500 else lines
    
    # Analysis counters
    symbol_analyses = 0
    signals_generated = 0
    trades_attempted = 0
    trades_successful = 0
    no_signal_count = 0
    
    # Track reasons for no signals
    no_signal_reasons = {}
    
    # Track symbols analyzed
    symbols_analyzed = set()
    
    print("📊 RECENT ACTIVITY ANALYSIS:")
    print("-" * 40)
    
    for line in recent_lines:
        # Count symbol analyses
        if 'ANALYZING' in line and '║' in line:
            symbol_analyses += 1
            # Extract symbol
            parts = line.split('ANALYZING')
            if len(parts) > 1:
                symbol_part = parts[1].split('║')[0].strip()
                if symbol_part:
                    symbols_analyzed.add(symbol_part)
        
        # Count signal generation
        if '✅ SIGNAL GENERATED' in line or 'BUY SIGNAL' in line or 'SELL SIGNAL' in line:
            signals_generated += 1
            print(f"📈 SIGNAL: {line.strip()}")
        
        # Count no signals
        if '❌ NO SIGNAL GENERATED' in line:
            no_signal_count += 1
        
        # Track no signal reasons
        if 'No crossover' in line:
            no_signal_reasons['No MA Crossover'] = no_signal_reasons.get('No MA Crossover', 0) + 1
        elif 'No trend confirmation' in line:
            no_signal_reasons['No Trend Confirmation'] = no_signal_reasons.get('No Trend Confirmation', 0) + 1
        elif 'No momentum' in line:
            no_signal_reasons['No Momentum'] = no_signal_reasons.get('No Momentum', 0) + 1
        elif 'No pullback' in line:
            no_signal_reasons['No Pullback'] = no_signal_reasons.get('No Pullback', 0) + 1
        elif 'No breakout' in line:
            no_signal_reasons['No Breakout'] = no_signal_reasons.get('No Breakout', 0) + 1
        
        # Count trade attempts
        if 'Placing order' in line or 'ORDER PLACED' in line:
            trades_attempted += 1
            print(f"💰 TRADE: {line.strip()}")
        
        # Count successful trades
        if 'Trade placed successfully' in line or 'ORDER_SEND_OK' in line:
            trades_successful += 1
    
    print(f"\n📊 SUMMARY STATISTICS:")
    print(f"  Symbol Analyses:    {symbol_analyses}")
    print(f"  Unique Symbols:     {len(symbols_analyzed)}")
    print(f"  Signals Generated:  {signals_generated}")
    print(f"  No Signal Count:    {no_signal_count}")
    print(f"  Trades Attempted:   {trades_attempted}")
    print(f"  Trades Successful:  {trades_successful}")
    
    if symbols_analyzed:
        print(f"\n📋 SYMBOLS ANALYZED:")
        for symbol in sorted(symbols_analyzed):
            print(f"  - {symbol}")
    
    if no_signal_reasons:
        print(f"\n❌ NO SIGNAL REASONS:")
        for reason, count in sorted(no_signal_reasons.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {reason}: {count} times")
    
    # Calculate signal rate
    if symbol_analyses > 0:
        signal_rate = (signals_generated / symbol_analyses) * 100
        print(f"\n📈 SIGNAL GENERATION RATE: {signal_rate:.1f}%")
        
        if signal_rate < 5:
            print("⚠️  Very low signal rate - market conditions may be unfavorable")
        elif signal_rate < 15:
            print("⚠️  Low signal rate - consider adjusting parameters")
        else:
            print("✅ Reasonable signal rate")
    
    return {
        'symbol_analyses': symbol_analyses,
        'signals_generated': signals_generated,
        'trades_attempted': trades_attempted,
        'trades_successful': trades_successful,
        'symbols_analyzed': len(symbols_analyzed),
        'no_signal_reasons': no_signal_reasons
    }

def check_current_configuration():
    """Check current bot configuration for trading parameters"""
    print("\n🔧 CURRENT CONFIGURATION ANALYSIS:")
    print("-" * 40)
    
    try:
        with open('bot_config.json', 'r') as f:
            config = json.load(f)
        
        # Key parameters that affect signal generation
        key_params = {
            'min_trade_confidence': config.get('min_trade_confidence', 0.6),
            'macd_min_histogram': config.get('macd_min_histogram', 0.0005),
            'rsi_overbought': config.get('rsi_overbought', 70),
            'rsi_oversold': config.get('rsi_oversold', 30),
            'fast_ma_period': config.get('fast_ma_period', 10),
            'slow_ma_period': config.get('slow_ma_period', 20),
            'timeframe': config.get('timeframe', 30),
            'use_volume_filter': config.get('use_volume_filter', False),
            'min_volume_ma': config.get('min_volume_ma', 1.0),
        }
        
        print("📊 SIGNAL GENERATION PARAMETERS:")
        for param, value in key_params.items():
            print(f"  {param}: {value}")
        
        # Check if parameters are too restrictive
        issues = []
        
        if key_params['min_trade_confidence'] > 0.7:
            issues.append(f"High confidence threshold ({key_params['min_trade_confidence']}) may reduce signals")
        
        if key_params['macd_min_histogram'] > 0.001:
            issues.append(f"High MACD threshold ({key_params['macd_min_histogram']}) may reduce signals")
        
        if key_params['use_volume_filter'] and key_params['min_volume_ma'] > 1.5:
            issues.append(f"High volume filter ({key_params['min_volume_ma']}) may reduce signals")
        
        if issues:
            print(f"\n⚠️  POTENTIAL ISSUES:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print(f"\n✅ Configuration parameters look reasonable")
        
        return key_params
        
    except Exception as e:
        print(f"❌ Error reading configuration: {str(e)}")
        return None

def check_market_conditions():
    """Analyze current market conditions from recent logs"""
    print("\n📈 MARKET CONDITIONS ANALYSIS:")
    print("-" * 40)
    
    log_file = "trading_bot.log"
    if not os.path.exists(log_file):
        print("❌ Cannot analyze - log file not found")
        return
    
    with open(log_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Get recent market data from logs
    recent_lines = lines[-200:] if len(lines) > 200 else lines
    
    ma_trends = {'bullish': 0, 'bearish': 0}
    crossovers = 0
    
    for line in recent_lines:
        if 'Fast ABOVE Slow' in line:
            ma_trends['bullish'] += 1
        elif 'Fast BELOW Slow' in line:
            ma_trends['bearish'] += 1
        elif 'crossover detected' in line:
            crossovers += 1
    
    total_trends = ma_trends['bullish'] + ma_trends['bearish']
    
    if total_trends > 0:
        bullish_pct = (ma_trends['bullish'] / total_trends) * 100
        bearish_pct = (ma_trends['bearish'] / total_trends) * 100
        
        print(f"📊 MA TREND ANALYSIS:")
        print(f"  Bullish trends: {ma_trends['bullish']} ({bullish_pct:.1f}%)")
        print(f"  Bearish trends: {ma_trends['bearish']} ({bearish_pct:.1f}%)")
        print(f"  Crossovers detected: {crossovers}")
        
        if crossovers == 0:
            print(f"\n⚠️  NO CROSSOVERS DETECTED")
            print(f"     Market may be in consolidation or trending without reversals")
        
        if bullish_pct > 80:
            print(f"\n📈 STRONG BULLISH MARKET")
        elif bearish_pct > 80:
            print(f"\n📉 STRONG BEARISH MARKET")
        else:
            print(f"\n⚖️  MIXED MARKET CONDITIONS")

def provide_recommendations(analysis_data, config_params):
    """Provide recommendations based on analysis"""
    print("\n💡 RECOMMENDATIONS:")
    print("-" * 40)
    
    if analysis_data['signals_generated'] == 0:
        print("🎯 NO SIGNALS GENERATED - SUGGESTED ACTIONS:")
        confidence = config_params.get('min_trade_confidence', 0.6)
        macd_thresh = config_params.get('macd_min_histogram', 0.0005)
        print(f"  1. Lower confidence threshold (currently {confidence:.1f})")
        print(f"  2. Reduce MACD histogram threshold (currently {macd_thresh:.6f})")
        print("  3. Switch to faster timeframe (M15 or M5)")
        print("  4. Disable volume filter temporarily")
        print("  5. Use more sensitive MA periods (5/15 instead of 10/20)")
    
    elif analysis_data['signals_generated'] > 0 and analysis_data['trades_attempted'] == 0:
        print("🎯 SIGNALS GENERATED BUT NO TRADES - CHECK:")
        print("  1. Trading permissions in MT5")
        print("  2. Account balance and margin")
        print("  3. Symbol trading hours")
        print("  4. Position limits")
    
    elif analysis_data['trades_attempted'] > 0 and analysis_data['trades_successful'] == 0:
        print("🎯 TRADES ATTEMPTED BUT FAILED - CHECK:")
        print("  1. MT5 connection status")
        print("  2. Order execution errors in logs")
        print("  3. Lot size and margin requirements")
        print("  4. Symbol specifications")
    
    print(f"\n🔧 QUICK FIXES TO TRY:")
    print(f"  1. Restart bot to refresh connections")
    print(f"  2. Switch to M15 timeframe for more signals")
    print(f"  3. Lower confidence to 0.4 (40%)")
    print(f"  4. Reduce MACD threshold to 0.0001")

def main():
    """Main analysis function"""
    print("🔍 NO TRADES ANALYSIS")
    print("=" * 30)
    
    # Analyze recent activity
    analysis_data = analyze_recent_logs()
    
    # Check configuration
    config_params = check_current_configuration()
    
    # Check market conditions
    check_market_conditions()
    
    # Provide recommendations
    if config_params:
        provide_recommendations(analysis_data, config_params)
    
    print(f"\n📋 NEXT STEPS:")
    print(f"  1. Review the analysis above")
    print(f"  2. Consider adjusting parameters if needed")
    print(f"  3. Monitor for 30 minutes after changes")
    print(f"  4. Check MT5 terminal for any issues")

if __name__ == "__main__":
    main()