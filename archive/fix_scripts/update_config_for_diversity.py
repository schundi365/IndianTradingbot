#!/usr/bin/env python3
"""
Update configuration to allow more diverse symbol trading
"""

import json
from datetime import datetime

def update_config_for_diversity():
    """Update config to be less restrictive and allow more symbols to trade"""
    
    # Read current config
    try:
        with open('bot_config.json', 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error reading config: {e}")
        return False
    
    # Create backup
    backup_file = f"bot_config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(backup_file, 'w') as f:
        json.dump(config, f, indent=4)
    print(f"✅ Backup created: {backup_file}")
    
    # Update settings for more diversity
    original_settings = {}
    
    # 1. Lower confidence threshold
    original_settings['min_trade_confidence'] = config['min_trade_confidence']
    config['min_trade_confidence'] = 0.4  # From 0.5 to 0.4
    
    # 2. Lower MACD threshold
    original_settings['macd_min_histogram'] = config['macd_min_histogram']
    config['macd_min_histogram'] = 0.0002  # From 0.0003 to 0.0002
    
    # 3. Widen RSI ranges
    original_settings['rsi_overbought'] = config['rsi_overbought']
    original_settings['rsi_oversold'] = config['rsi_oversold']
    config['rsi_overbought'] = 70  # From 75 to 70
    config['rsi_oversold'] = 30    # From 25 to 30
    
    # 4. Increase risk slightly for more opportunities
    original_settings['risk_percent'] = config['risk_percent']
    config['risk_percent'] = 0.5  # From 0.3 to 0.5
    
    # 5. Reduce max trades per symbol to spread across symbols
    original_settings['max_trades_per_symbol'] = config['max_trades_per_symbol']
    config['max_trades_per_symbol'] = 5  # From 10 to 5
    
    # 6. Update timestamp
    config['last_updated'] = datetime.now().isoformat()
    config['version'] = "2.1.1"
    
    # Save updated config
    with open('bot_config.json', 'w') as f:
        json.dump(config, f, indent=4)
    
    print("=" * 80)
    print("CONFIGURATION UPDATED FOR SYMBOL DIVERSITY")
    print("=" * 80)
    
    print("\n📊 CHANGES MADE:")
    print(f"  Min Confidence:      {original_settings['min_trade_confidence']*100}% → {config['min_trade_confidence']*100}%")
    print(f"  MACD Threshold:      {original_settings['macd_min_histogram']} → {config['macd_min_histogram']}")
    print(f"  RSI Overbought:      {original_settings['rsi_overbought']} → {config['rsi_overbought']}")
    print(f"  RSI Oversold:        {original_settings['rsi_oversold']} → {config['rsi_oversold']}")
    print(f"  Risk per Trade:      {original_settings['risk_percent']}% → {config['risk_percent']}%")
    print(f"  Max Trades/Symbol:   {original_settings['max_trades_per_symbol']} → {config['max_trades_per_symbol']}")
    
    print("\n💡 EXPECTED RESULTS:")
    print("  ✅ More symbols should generate signals")
    print("  ✅ Lower confidence threshold allows weaker but valid signals")
    print("  ✅ Lower MACD threshold captures more momentum changes")
    print("  ✅ Wider RSI ranges allow more entry opportunities")
    print("  ✅ Limited trades per symbol forces diversification")
    
    print("\n🔄 NEXT STEPS:")
    print("  1. Restart the trading bot to apply new settings")
    print("  2. Monitor for 30-60 minutes to see signal diversity")
    print("  3. Check if other symbols start generating trades")
    
    return True

if __name__ == "__main__":
    if update_config_for_diversity():
        print("\n🎉 Configuration updated successfully!")
        print("   Restart the bot to see more diverse symbol trading.")
    else:
        print("\n❌ Failed to update configuration")