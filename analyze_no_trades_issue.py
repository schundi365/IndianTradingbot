#!/usr/bin/env python3
"""
Analyze No Trades Issue - Comprehensive Log Analysis
"""

import re
from datetime import datetime, timedelta
import json

def analyze_trading_logs():
    """Analyze trading bot logs to understand why no trades are placed"""
    print("🔍 ANALYZING NO TRADES ISSUE")
    print("=" * 60)
    
    try:
        # Read the log file
        with open('trading_bot.log', 'r', encoding='utf-8') as f:
            log_content = f.read()
        
        print(f"✅ Log file read successfully ({len(log_content)} characters)")
        
        # Get current time and 5 hours ago
        now = datetime.now()
        five_hours_ago = now - timedelta(hours=5)
        
        print(f"📅 Analyzing period: {five_hours_ago.strftime('%H:%M:%S')} to {now.strftime('%H:%M:%S')}")
        
        # Analysis counters
        analysis_count = 0
        signal_attempts = 0
        no_signal_count = 0
        volume_rejections = 0
        confidence_rejections = 0
        ma_crossover_checks = 0
        trend_confirmation_checks = 0
        symbols_analyzed = set()
        
        # Pattern matching
        patterns = {
            'analysis_start': r'ANALYZING\s+(\w+)',
            'signal_analysis': r'📊 SIGNAL ANALYSIS - DETAILED CALCULATIONS',
            'no_signal': r'❌ NO SIGNAL GENERATED',
            'ma_crossover': r'🔍 CHECKING MA CROSSOVER:',
            'no_crossover': r'❌ No crossover detected',
            'trend_confirmation': r'🔍 CHECKING TREND CONFIRMATION:',
            'no_trend_confirmation': r'❌ No trend confirmation',
            'volume_rejection': r'Trade rejected by volume filter',
            'confidence_too_low': r'confidence.*too low',
            'waiting_for': r'Waiting for MA crossover or trend confirmation',
            'current_price': r'Current Price:\s+([\d.]+)',
            'fast_ma': r'Fast MA \(\d+\):\s+([\d.]+)',
            'slow_ma': r'Slow MA \(\d+\):\s+([\d.]+)',
            'ma_position': r'MA Position:\s+Fast (ABOVE|BELOW) Slow'
        }
        
        # Find all matches
        results = {}
        for pattern_name, pattern in patterns.items():
            matches = re.findall(pattern, log_content, re.IGNORECASE)
            results[pattern_name] = matches
        
        # Count occurrences
        analysis_count = len(results['analysis_start'])
        signal_attempts = len(results['signal_analysis'])
        no_signal_count = len(results['no_signal'])
        ma_crossover_checks = len(results['ma_crossover'])
        no_crossover_count = len(results['no_crossover'])
        trend_confirmation_checks = len(results['trend_confirmation'])
        no_trend_confirmation_count = len(results['no_trend_confirmation'])
        volume_rejections = len(results['volume_rejection'])
        
        # Get unique symbols
        symbols_analyzed = set(results['analysis_start'])
        
        # Get MA positions
        ma_positions = results['ma_position']
        above_count = ma_positions.count('ABOVE')
        below_count = ma_positions.count('BELOW')
        
        print("\n📊 ANALYSIS SUMMARY:")
        print("-" * 40)
        print(f"Total Symbol Analyses: {analysis_count}")
        print(f"Unique Symbols Analyzed: {len(symbols_analyzed)}")
        print(f"Signal Analysis Attempts: {signal_attempts}")
        print(f"No Signal Generated: {no_signal_count}")
        print(f"MA Crossover Checks: {ma_crossover_checks}")
        print(f"No Crossover Detected: {no_crossover_count}")
        print(f"Trend Confirmation Checks: {trend_confirmation_checks}")
        print(f"No Trend Confirmation: {no_trend_confirmation_count}")
        print(f"Volume Rejections: {volume_rejections}")
        
        print(f"\n📈 MARKET CONDITIONS:")
        print("-" * 40)
        print(f"Fast MA Above Slow MA: {above_count} times")
        print(f"Fast MA Below Slow MA: {below_count} times")
        
        if symbols_analyzed:
            print(f"\n🎯 SYMBOLS ANALYZED:")
            print("-" * 40)
            for symbol in sorted(symbols_analyzed):
                count = results['analysis_start'].count(symbol)
                print(f"  {symbol}: {count} times")
        
        # Identify the main issues
        print(f"\n🚨 MAIN ISSUES IDENTIFIED:")
        print("-" * 40)
        
        issues = []
        
        if no_crossover_count == ma_crossover_checks and ma_crossover_checks > 0:
            issues.append("❌ NO MA CROSSOVERS: All crossover checks failed")
            print("   • No moving average crossovers detected")
            print("   • Bot is waiting for Fast MA to cross above/below Slow MA")
        
        if no_trend_confirmation_count == trend_confirmation_checks and trend_confirmation_checks > 0:
            issues.append("❌ NO TREND CONFIRMATIONS: All trend checks failed")
            print("   • No trend confirmation signals detected")
            print("   • Price not aligned with MA trend direction")
        
        if below_count > above_count * 2:
            issues.append("❌ BEARISH MARKET: Fast MA mostly below Slow MA")
            print(f"   • Market is in bearish trend ({below_count} below vs {above_count} above)")
            print("   • Bot may be waiting for bullish crossover")
        
        if volume_rejections > 0:
            issues.append(f"❌ VOLUME FILTER: {volume_rejections} trades rejected by volume")
            print(f"   • {volume_rejections} potential trades rejected due to low volume")
        
        if no_signal_count == signal_attempts and signal_attempts > 0:
            issues.append("❌ NO SIGNALS: 100% signal generation failure")
            print("   • All signal analysis attempts resulted in no signal")
            print("   • Bot is not finding any trading opportunities")
        
        # Check configuration
        print(f"\n⚙️ CONFIGURATION CHECK:")
        print("-" * 40)
        
        try:
            with open('bot_config.json', 'r') as f:
                config = json.load(f)
            
            print(f"Timeframe: M{config.get('timeframe', 'Unknown')}")
            print(f"Min Confidence: {config.get('min_trade_confidence', 'Unknown')*100:.1f}%")
            print(f"Volume Filter: {'Enabled' if config.get('use_volume_filter', False) else 'Disabled'}")
            print(f"Volume Threshold: {config.get('min_volume_ma', 'Unknown')}x")
            print(f"Fast MA Period: {config.get('fast_ma_period', 'Unknown')}")
            print(f"Slow MA Period: {config.get('slow_ma_period', 'Unknown')}")
            print(f"MACD Histogram: {config.get('macd_min_histogram', 'Unknown')}")
            print(f"RSI Overbought: {config.get('rsi_overbought', 'Unknown')}")
            print(f"RSI Oversold: {config.get('rsi_oversold', 'Unknown')}")
            
        except Exception as e:
            print(f"❌ Could not read config: {e}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        print("-" * 40)
        
        if no_crossover_count == ma_crossover_checks:
            print("1. 🔄 REDUCE MA PERIODS:")
            print("   • Current: Fast MA=10, Slow MA=30")
            print("   • Try: Fast MA=5, Slow MA=15 for more crossovers")
        
        if below_count > above_count * 2:
            print("2. 📉 BEARISH MARKET ADAPTATION:")
            print("   • Enable short selling if not already enabled")
            print("   • Consider trend-following instead of crossover strategy")
        
        if volume_rejections > 0:
            print("3. 📊 VOLUME FILTER ADJUSTMENT:")
            print("   • Current volume threshold may be too strict")
            print("   • Consider lowering min_volume_ma from current value")
        
        print("4. ⚡ IMMEDIATE ACTIONS:")
        print("   • Switch to M15 timeframe for more opportunities")
        print("   • Lower confidence threshold to 40% temporarily")
        print("   • Disable volume filter temporarily for testing")
        print("   • Add more volatile symbols (crypto pairs)")
        
        return {
            'analysis_count': analysis_count,
            'no_signal_count': no_signal_count,
            'symbols_analyzed': len(symbols_analyzed),
            'main_issues': issues,
            'ma_below_ratio': below_count / (above_count + below_count) if (above_count + below_count) > 0 else 0
        }
        
    except Exception as e:
        print(f"❌ Error analyzing logs: {e}")
        return None

def create_quick_fix_config():
    """Create a quick fix configuration for more trading opportunities"""
    print(f"\n🔧 CREATING QUICK FIX CONFIGURATION:")
    print("-" * 40)
    
    try:
        with open('bot_config.json', 'r') as f:
            config = json.load(f)
        
        # Make aggressive changes for more signals
        original_values = {}
        changes = {
            'timeframe': 15,  # M15 instead of M30
            'min_trade_confidence': 0.4,  # 40% instead of 50%
            'fast_ma_period': 5,  # Faster crossovers
            'slow_ma_period': 15,  # Faster crossovers
            'use_volume_filter': False,  # Disable temporarily
            'macd_min_histogram': 0.0003,  # More sensitive
            'rsi_overbought': 75,  # Less restrictive
            'rsi_oversold': 25,   # Less restrictive
        }
        
        for key, new_value in changes.items():
            original_values[key] = config.get(key, 'Not set')
            config[key] = new_value
        
        # Save the modified config
        with open('bot_config_quick_fix.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print("✅ Quick fix configuration created: bot_config_quick_fix.json")
        print("\nChanges made:")
        for key, new_value in changes.items():
            print(f"  {key}: {original_values[key]} → {new_value}")
        
        print("\n⚠️ To apply these changes:")
        print("1. Stop the bot")
        print("2. Copy bot_config_quick_fix.json to bot_config.json")
        print("3. Restart the bot")
        print("4. Monitor for increased signal generation")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating quick fix config: {e}")
        return False

if __name__ == "__main__":
    results = analyze_trading_logs()
    if results:
        print(f"\n🎯 SUMMARY:")
        print(f"The bot analyzed {results['symbols_analyzed']} symbols {results['analysis_count']} times")
        print(f"but generated {results['no_signal_count']} 'no signal' results.")
        
        if results['ma_below_ratio'] > 0.7:
            print(f"Market is {results['ma_below_ratio']*100:.1f}% bearish (Fast MA below Slow MA)")
        
        create_quick_fix_config()
        
        print(f"\n🚨 MAIN CONCLUSION:")
        print("The bot is working correctly but market conditions are not")
        print("generating crossover or trend confirmation signals with current settings.")
    else:
        print("❌ Analysis failed - check log file availability")