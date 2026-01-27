"""
Verify M5 Settings - Complete Configuration Check
Confirms all indicators are properly configured for M5 timeframe
"""

import sys
sys.path.insert(0, 'src')
from config import get_config
import MetaTrader5 as mt5

def verify_m5_settings():
    """Verify all M5 settings are correct"""
    
    print("=" * 70)
    print("M5 CONFIGURATION VERIFICATION")
    print("=" * 70)
    print()
    
    config = get_config()
    
    # Expected M5 values
    expected = {
        'timeframe': 5,  # M5
        'fast_ma_period': 10,
        'slow_ma_period': 20,
        'ma_type': 'EMA',
        'atr_period': 14,
        'atr_multiplier': 1.5,
        'risk_percent': 0.5,
        'reward_ratio': 1.5,
        'trail_activation': 1.0,
        'trail_distance': 0.8,
        'tp_levels': [1.2, 1.8, 2.5],
        'max_trades_total': 8,
        'max_trades_per_symbol': 2,
        'max_daily_trades': 30,
        'update_interval': 30,
        'trend_strength_period': 30,
        'adx_strong_trend': 20,
        'adx_ranging': 15,
        'min_trade_confidence': 0.55,
        'trend_timeframe': 16385,  # H1
        'trend_ma_period': 50,
    }
    
    all_correct = True
    
    print("Checking Core Settings:")
    print("-" * 70)
    
    # Check each setting
    checks = [
        ('Timeframe', 'timeframe', 'M5 (5 min)'),
        ('Fast MA Period', 'fast_ma_period', '10 periods (50 min)'),
        ('Slow MA Period', 'slow_ma_period', '20 periods (100 min)'),
        ('MA Type', 'ma_type', 'EMA'),
        ('ATR Period', 'atr_period', '14 periods (70 min)'),
        ('ATR Multiplier SL', 'atr_multiplier', '1.5× (tighter)'),
        ('Risk Per Trade', 'risk_percent', '0.5%'),
        ('Reward Ratio', 'reward_ratio', '1:1.5'),
        ('Trail Activation', 'trail_activation', '1.0× ATR (sooner)'),
        ('Trail Distance', 'trail_distance', '0.8× ATR (closer)'),
        ('Max Total Trades', 'max_trades_total', '8 trades'),
        ('Max Per Symbol', 'max_trades_per_symbol', '2 trades'),
        ('Max Daily Trades', 'max_daily_trades', '30 trades'),
        ('Update Interval', 'update_interval', '30 seconds'),
    ]
    
    for name, key, description in checks:
        actual = config.get(key)
        expected_val = expected.get(key)
        
        if actual == expected_val:
            print(f"✅ {name:25} {actual:10} - {description}")
        else:
            print(f"❌ {name:25} {actual:10} - Expected: {expected_val}")
            all_correct = False
    
    print()
    print("Checking Adaptive Risk Settings:")
    print("-" * 70)
    
    adaptive_checks = [
        ('Trend Strength Period', 'trend_strength_period', '30 periods'),
        ('ADX Strong Trend', 'adx_strong_trend', '20 (lower)'),
        ('ADX Ranging', 'adx_ranging', '15 (lower)'),
        ('Min Trade Confidence', 'min_trade_confidence', '55%'),
    ]
    
    for name, key, description in adaptive_checks:
        actual = config.get(key)
        expected_val = expected.get(key)
        
        if actual == expected_val:
            print(f"✅ {name:25} {actual:10} - {description}")
        else:
            print(f"❌ {name:25} {actual:10} - Expected: {expected_val}")
            all_correct = False
    
    print()
    print("Checking Take Profit Levels:")
    print("-" * 70)
    
    tp_levels = config.get('tp_levels', [])
    expected_tp = expected['tp_levels']
    
    if tp_levels == expected_tp:
        print(f"✅ TP Levels: {tp_levels}")
        print(f"   TP1: {tp_levels[0]}× risk (quick profit)")
        print(f"   TP2: {tp_levels[1]}× risk (moderate)")
        print(f"   TP3: {tp_levels[2]}× risk (let it run)")
    else:
        print(f"❌ TP Levels: {tp_levels} - Expected: {expected_tp}")
        all_correct = False
    
    print()
    print("Checking Trend Filter:")
    print("-" * 70)
    
    trend_tf = config.get('trend_timeframe')
    trend_ma = config.get('trend_ma_period')
    
    if trend_tf == 16385:  # H1
        print(f"✅ Trend Timeframe: H1 (correct for M5)")
    else:
        print(f"❌ Trend Timeframe: {trend_tf} - Expected: H1 (16385)")
        all_correct = False
    
    if trend_ma == 50:
        print(f"✅ Trend MA Period: 50 periods")
    else:
        print(f"❌ Trend MA Period: {trend_ma} - Expected: 50")
        all_correct = False
    
    print()
    print("=" * 70)
    
    if all_correct:
        print("✅ ALL SETTINGS CORRECT FOR M5!")
        print()
        print("Your bot is properly configured for 5-minute trading.")
        print()
        print("Key Points:")
        print("  • Timeframe: M5 (5 minutes)")
        print("  • MAs: 10/20 EMA (faster response)")
        print("  • ATR: 1.5× multiplier (tighter stops)")
        print("  • Risk: 0.5% per trade (conservative)")
        print("  • Trailing: 1.0× ATR activation (sooner)")
        print("  • TPs: [1.2, 1.8, 2.5] (realistic)")
        print("  • Max Trades: 8 total, 2 per symbol")
        print("  • Trend Filter: H1 (appropriate for M5)")
        print()
        print("Ready to test:")
        print("  python examples/quick_test.py")
        print("  python test_bot_live.py")
        print("  python run_bot.py")
    else:
        print("⚠️  SOME SETTINGS INCORRECT!")
        print()
        print("Please check src/config.py and fix the settings above.")
        print("See M5_INDICATOR_SETTINGS.md for correct values.")
    
    print("=" * 70)
    
    return all_correct


if __name__ == "__main__":
    try:
        success = verify_m5_settings()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
