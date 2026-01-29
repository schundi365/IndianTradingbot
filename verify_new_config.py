"""
Verify New Configuration is Loaded
Checks that the updated config values are being used by the bot
"""

import json
import sys
from pathlib import Path

def verify_config():
    """Verify the configuration file has the correct values"""
    
    print("=" * 70)
    print("CONFIGURATION VERIFICATION")
    print("=" * 70)
    print()
    
    # Load config
    config_file = Path('bot_config.json')
    
    if not config_file.exists():
        print("❌ ERROR: bot_config.json not found!")
        return False
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ ERROR: Failed to load config: {e}")
        return False
    
    print("✅ Configuration file loaded successfully")
    print()
    
    # Check critical values
    checks = {
        'timeframe': (30, 'M30 (30-minute candles)'),
        'max_daily_trades': (999, 'Virtually unlimited'),
        'max_trades_total': (999, 'Virtually unlimited'),
        'max_trades_per_symbol': (10, 'Per-symbol limit'),
        'use_dynamic_tp': (True, 'Dynamic TP extension enabled'),
        'use_dynamic_sl': (True, 'Dynamic SL tightening enabled'),
    }
    
    print("CRITICAL CONFIGURATION VALUES:")
    print("-" * 70)
    
    all_correct = True
    for key, (expected, description) in checks.items():
        actual = config.get(key)
        status = "✅" if actual == expected else "❌"
        
        if actual == expected:
            print(f"{status} {key}: {actual} - {description}")
        else:
            print(f"{status} {key}: {actual} (EXPECTED: {expected}) - {description}")
            all_correct = False
    
    print()
    print("-" * 70)
    
    # Additional info
    print()
    print("ADDITIONAL CONFIGURATION:")
    print("-" * 70)
    print(f"Symbols: {len(config.get('symbols', []))} pairs")
    print(f"  {', '.join(config.get('symbols', [])[:8])}")
    print(f"  {', '.join(config.get('symbols', [])[8:])}")
    print()
    print(f"Fast MA: {config.get('fast_ma_period', 'N/A')}")
    print(f"Slow MA: {config.get('slow_ma_period', 'N/A')}")
    print(f"Min Confidence: {config.get('min_confidence', 'N/A')}")
    print(f"Reward Ratio: {config.get('reward_ratio', 'N/A')}")
    print(f"TP Levels: {config.get('tp_levels', 'N/A')}")
    print(f"ATR Multiplier: {config.get('atr_multiplier', 'N/A')}")
    print()
    print(f"RSI Filter: {'Enabled' if config.get('use_rsi') else 'Disabled'}")
    print(f"MACD Filter: {'Enabled' if config.get('use_macd') else 'Disabled'}")
    print(f"ADX Filter: {'Enabled' if config.get('use_adx') else 'Disabled'}")
    print(f"Volume Filter: {'Enabled' if config.get('use_volume_filter') else 'Disabled'}")
    print()
    print(f"Adaptive Risk: {'Enabled' if config.get('use_adaptive_risk') else 'Disabled'}")
    print(f"Max Daily Loss: {config.get('max_daily_loss', 'N/A')}%")
    print(f"Max Drawdown: {config.get('max_drawdown_percent', 'N/A')}%")
    
    print()
    print("=" * 70)
    
    if all_correct:
        print("✅ ALL CONFIGURATION VALUES ARE CORRECT!")
        print()
        print("The bot will use these settings on next reload.")
        print("If bot is running, it will reload config automatically.")
    else:
        print("❌ SOME CONFIGURATION VALUES ARE INCORRECT!")
        print()
        print("Please check bot_config.json and fix the values.")
    
    print("=" * 70)
    
    return all_correct


if __name__ == "__main__":
    success = verify_config()
    sys.exit(0 if success else 1)
