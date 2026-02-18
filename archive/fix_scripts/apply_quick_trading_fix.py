#!/usr/bin/env python3
"""
Apply quick fixes to enable trading
"""

import json
import sys
from datetime import datetime

def apply_quick_trading_fix():
    """Apply configuration changes to enable more trading signals"""
    
    print("="*80)
    print("APPLYING QUICK TRADING FIXES")
    print("="*80)
    
    # Read current configuration
    try:
        with open('bot_config.json', 'r') as f:
            config = json.load(f)
        
        print("CURRENT PROBLEMATIC VALUES:")
        print(f"   MACD Min Histogram: {config.get('macd_min_histogram')}")
        print(f"   Min Volume MA: {config.get('min_volume_ma')}")
        print(f"   Volume Filter: {config.get('use_volume_filter')}")
        print(f"   Timeframe: M{config.get('timeframe')}")
        
    except Exception as e:
        print(f"❌ Error reading config: {e}")
        return
    
    # Create backup
    backup_file = f"config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        with open(backup_file, 'w') as f:
            json.dump(config, f, indent=4)
        print(f"✅ Backup created: {backup_file}")
    except Exception as e:
        print(f"⚠️  Warning: Could not create backup: {e}")
    
    # Apply fixes
    print("\nAPPLYING FIXES:")
    
    # Fix 1: Increase MACD threshold to optimized value
    old_macd = config.get('macd_min_histogram', 0.0003)
    config['macd_min_histogram'] = 0.0005
    print(f"1. MACD Min Histogram: {old_macd} → 0.0005")
    
    # Fix 2: Lower volume filter threshold
    old_volume = config.get('min_volume_ma', 1.2)
    config['min_volume_ma'] = 0.7
    print(f"2. Min Volume MA: {old_volume} → 0.7")
    
    # Fix 3: Change to M15 timeframe for crypto
    old_timeframe = config.get('timeframe', 30)
    config['timeframe'] = 15
    print(f"3. Timeframe: M{old_timeframe} → M15")
    
    # Fix 4: Temporarily disable some filters
    config['use_adx'] = False
    config['use_trend_filter'] = False
    print(f"4. Disabled ADX and Trend filters (keeping RSI + MACD + Volume)")
    
    # Fix 5: Increase analysis bars for M15
    config['analysis_bars'] = 150
    print(f"5. Analysis bars: 200 → 150 (optimized for M15)")
    
    # Fix 6: Update timestamp
    config['last_updated'] = datetime.now().isoformat()
    
    # Save updated configuration
    try:
        with open('bot_config.json', 'w') as f:
            json.dump(config, f, indent=4)
        
        print("\n✅ CONFIGURATION UPDATED SUCCESSFULLY")
        print("\nNEW OPTIMIZED VALUES:")
        print(f"   MACD Min Histogram: {config['macd_min_histogram']}")
        print(f"   Min Volume MA: {config['min_volume_ma']}")
        print(f"   Timeframe: M{config['timeframe']}")
        print(f"   Active Filters: RSI, MACD, Volume")
        print(f"   Analysis Bars: {config['analysis_bars']}")
        
        print("\n🚀 EXPECTED IMPROVEMENTS:")
        print("   • More sensitive MACD signals")
        print("   • Lower volume requirements")
        print("   • Faster M15 timeframe for crypto")
        print("   • Fewer restrictive filters")
        print("   • Should generate more trading signals")
        
        print("\n⚠️  NEXT STEPS:")
        print("   1. Restart the trading bot to apply changes")
        print("   2. Monitor logs for signal generation")
        print("   3. Check dashboard for new trades")
        print("   4. If still no signals, consider disabling volume filter")
        
    except Exception as e:
        print(f"❌ Error saving config: {e}")
        return
    
    print("\n" + "="*80)
    print("QUICK TRADING FIXES APPLIED")
    print("="*80)

if __name__ == "__main__":
    apply_quick_trading_fix()