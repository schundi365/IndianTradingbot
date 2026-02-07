"""
Fix TP/SL Inconsistency Issue
================================
Problem: SL uses ratio-based (ATR), TP uses pip-based, causing SL > TP

Solution: Make both use the same calculation method
"""

import json
import shutil
from datetime import datetime

def fix_tp_sl_config():
    """Fix the TP/SL calculation inconsistency"""
    
    config_file = 'bot_config.json'
    
    # Backup current config
    backup_file = f'bot_config_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    shutil.copy(config_file, backup_file)
    print(f"✓ Backed up config to: {backup_file}")
    
    # Load config
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    print("\n" + "="*70)
    print("CURRENT CONFIGURATION (PROBLEMATIC):")
    print("="*70)
    print(f"use_pip_based_sl: {config.get('use_pip_based_sl', False)}")
    print(f"sl_pips: {config.get('sl_pips', 50)}")
    print(f"use_pip_based_tp: {config.get('use_pip_based_tp', False)}")
    print(f"tp_pips: {config.get('tp_pips', 100)}")
    print(f"atr_multiplier: {config.get('atr_multiplier', 2.0)}")
    print(f"reward_ratio: {config.get('reward_ratio', 2.0)}")
    
    print("\n" + "="*70)
    print("ISSUE IDENTIFIED:")
    print("="*70)
    print("❌ SL uses ATR-based calculation (can be 200-400+ pips for gold)")
    print("❌ TP uses fixed 250 pips")
    print("❌ Result: SL distance > TP distance (bad risk/reward!)")
    
    print("\n" + "="*70)
    print("SOLUTION OPTIONS:")
    print("="*70)
    print("\nOption 1: Both use PIP-BASED (Recommended for consistency)")
    print("  - SL: 50 pips")
    print("  - TP: 100 pips (1:2 risk/reward)")
    print("  - Pros: Predictable, consistent across all symbols")
    print("  - Cons: May not adapt to volatility")
    
    print("\nOption 2: Both use RATIO-BASED (Adaptive to volatility)")
    print("  - SL: ATR × 2.0")
    print("  - TP: SL × reward_ratio (e.g., 2.0 for 1:2)")
    print("  - Pros: Adapts to market volatility")
    print("  - Cons: Variable pip distances")
    
    # Apply Option 1 (Pip-based for both)
    print("\n" + "="*70)
    print("APPLYING FIX: Option 1 (Pip-based for both)")
    print("="*70)
    
    config['use_pip_based_sl'] = True
    config['sl_pips'] = 50
    config['use_pip_based_tp'] = True
    config['tp_pips'] = 100  # 1:2 risk/reward
    
    # Also update tp_levels for split orders
    config['tp_levels'] = [1.5, 2.5, 4.0]  # Multipliers of base TP
    
    print("✓ use_pip_based_sl: True")
    print("✓ sl_pips: 50")
    print("✓ use_pip_based_tp: True")
    print("✓ tp_pips: 100")
    print("✓ tp_levels: [1.5, 2.5, 4.0]")
    print("\nThis means:")
    print("  - SL: 50 pips from entry")
    print("  - TP Level 1: 150 pips (100 × 1.5)")
    print("  - TP Level 2: 250 pips (100 × 2.5)")
    print("  - TP Level 3: 400 pips (100 × 4.0)")
    
    # Save updated config
    config['last_updated'] = datetime.now().isoformat()
    
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=4)
    
    print("\n" + "="*70)
    print("✓ CONFIGURATION UPDATED SUCCESSFULLY")
    print("="*70)
    print(f"Config file: {config_file}")
    print(f"Backup: {backup_file}")
    
    print("\n" + "="*70)
    print("NEXT STEPS:")
    print("="*70)
    print("1. Restart the bot to apply changes")
    print("2. Monitor first few trades to verify SL < TP")
    print("3. Adjust sl_pips/tp_pips if needed for your strategy")
    
    print("\n" + "="*70)
    print("ALTERNATIVE: If you prefer ATR-based (Option 2)")
    print("="*70)
    print("Set these values instead:")
    print("  use_pip_based_sl: false")
    print("  use_pip_based_tp: false")
    print("  atr_multiplier: 2.0")
    print("  reward_ratio: 2.0")
    print("This will make both SL and TP scale with volatility")

if __name__ == "__main__":
    fix_tp_sl_config()
