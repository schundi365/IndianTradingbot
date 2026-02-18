"""
Apply Optimized Configuration
Backs up current config and applies optimized settings
"""

import shutil
import os
from datetime import datetime

def apply_optimized_config():
    """Apply the optimized configuration"""
    
    print("=" * 80)
    print("APPLY OPTIMIZED CONFIGURATION")
    print("=" * 80)
    print()
    
    # Backup current config
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join('src', f"config_backup_{timestamp}.py")
    config_file = os.path.join('src', 'config.py')
    optimized_file = os.path.join('src', 'config_optimized.py')
    
    print(f"1. Backing up current config to: {backup_file}")
    shutil.copy(config_file, backup_file)
    print("   ✓ Backup created")
    print()
    
    # Copy optimized config
    print("2. Applying optimized configuration...")
    shutil.copy(optimized_file, config_file)
    print("   ✓ Optimized config applied")
    print()
    
    print("=" * 80)
    print("CONFIGURATION UPDATED!")
    print("=" * 80)
    print()
    print("Key Changes Applied:")
    print("  ✓ Timeframe: M1 → M5 (less noise, better signals)")
    print("  ✓ Stop Loss: 1.2x ATR → 2.0x ATR (wider stops)")
    print("  ✓ Min Confidence: 50% → 70% (higher quality trades)")
    print("  ✓ Trailing Activation: 0.8x → 1.5x ATR (more profit before trailing)")
    print("  ✓ Trailing Distance: 0.6x → 1.0x ATR (wider trailing)")
    print("  ✓ Trend Filter: M15 → H1 (stronger trend confirmation)")
    print("  ✓ Trend MA: 20 → 50 periods (longer-term trend)")
    print("  ✓ Risk: 0.3% → 0.2% (reduced for testing)")
    print("  ✓ MACD Min: 0.0 → 0.5 (stronger confirmation)")
    print("  ✓ Trading Hours: Enabled (8 AM - 4 PM UTC)")
    print("  ✓ Max Daily Trades: 100 → 30")
    print()
    print("Next Steps:")
    print("  1. Review the changes in src/config.py")
    print("  2. Test the bot: python run_bot.py")
    print("  3. Monitor performance: python analyze_trades.py")
    print("  4. If you want to revert: copy the backup file back")
    print()
    print(f"Backup location: {backup_file}")
    print("=" * 80)


if __name__ == "__main__":
    try:
        apply_optimized_config()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
