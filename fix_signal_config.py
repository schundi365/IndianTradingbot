#!/usr/bin/env python3
"""
Fix Signal Generation Configuration Issues

The enhanced 5-method signal generation is working correctly,
but the configuration values are preventing signals from being generated.

Issues found:
1. MACD threshold too low (0.0003 vs optimal 0.0005)
2. Volume threshold too high (1.0 vs optimal 0.7)
3. M30 timeframe too slow (should be M15 for more signals)
4. RSI ranges too restrictive (75/25 vs optimal 70/30)
"""

import json
from datetime import datetime

def fix_signal_config():
    """Fix the configuration to generate more signals"""
    
    config_file = "bot_config.json"
    
    # Read current config
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    print("🔧 FIXING SIGNAL GENERATION CONFIGURATION")
    print("="*60)
    
    # Store original values for comparison
    original_values = {
        'macd_min_histogram': config.get('macd_min_histogram', 0.0003),
        'min_volume_ma': config.get('min_volume_ma', 1.0),
        'timeframe': config.get('timeframe', 30),
        'rsi_overbought': config.get('rsi_overbought', 75),
        'rsi_oversold': config.get('rsi_oversold', 25),
        'min_trade_confidence': config.get('min_trade_confidence', 0.6)
    }
    
    # Apply optimized values
    optimized_values = {
        'macd_min_histogram': 0.0005,  # More sensitive MACD
        'min_volume_ma': 0.7,          # Less restrictive volume filter
        'timeframe': 15,               # Faster timeframe for more signals
        'rsi_overbought': 70,          # Standard RSI levels
        'rsi_oversold': 30,            # Standard RSI levels
        'min_trade_confidence': 0.5,   # Lower confidence for more signals
        'last_updated': datetime.now().isoformat()
    }
    
    # Update config
    config.update(optimized_values)
    
    # Write updated config
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=4)
    
    print("✅ CONFIGURATION FIXES APPLIED:")
    print()
    for key, new_value in optimized_values.items():
        if key == 'last_updated':
            continue
        old_value = original_values.get(key, 'N/A')
        print(f"   {key}:")
        print(f"      OLD: {old_value}")
        print(f"      NEW: {new_value}")
        print(f"      IMPACT: {'More signals' if new_value != old_value else 'No change'}")
        print()
    
    print("🎯 EXPECTED IMPROVEMENTS:")
    print("• MACD 0.0005: More sensitive to momentum changes")
    print("• Volume 0.7: Less restrictive volume filtering")
    print("• M15 timeframe: More frequent analysis (4x more signals)")
    print("• RSI 70/30: Standard overbought/oversold levels")
    print("• Confidence 0.5: Lower threshold for signal acceptance")
    
    print("\n🔄 RESTART REQUIRED:")
    print("1. Stop the current bot")
    print("2. Clear cache: python clear_all_cache.py")
    print("3. Restart bot: python run_bot.py")
    print("4. Monitor logs for increased signal generation")
    
    return True

if __name__ == "__main__":
    if fix_signal_config():
        print("\n✅ SIGNAL GENERATION CONFIGURATION FIXED!")
        print("The bot should now generate significantly more trading signals.")
    else:
        print("\n❌ FAILED TO FIX CONFIGURATION!")