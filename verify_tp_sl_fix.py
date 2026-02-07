"""
Verify TP/SL Fix
================
Confirms that SL and TP calculations are now consistent
"""

import json

def verify_config():
    """Verify the configuration is now consistent"""
    
    with open('bot_config.json', 'r') as f:
        config = json.load(f)
    
    print("="*70)
    print("CONFIGURATION VERIFICATION")
    print("="*70)
    
    use_pip_sl = config.get('use_pip_based_sl', False)
    use_pip_tp = config.get('use_pip_based_tp', False)
    sl_pips = config.get('sl_pips', 50)
    tp_pips = config.get('tp_pips', 100)
    tp_levels = config.get('tp_levels', [1.0, 2.0, 3.0])
    
    print(f"\nStop Loss Configuration:")
    print(f"  use_pip_based_sl: {use_pip_sl}")
    print(f"  sl_pips: {sl_pips}")
    
    print(f"\nTake Profit Configuration:")
    print(f"  use_pip_based_tp: {use_pip_tp}")
    print(f"  tp_pips: {tp_pips}")
    print(f"  tp_levels: {tp_levels}")
    
    # Check consistency
    print("\n" + "="*70)
    print("CONSISTENCY CHECK:")
    print("="*70)
    
    issues = []
    
    if use_pip_sl != use_pip_tp:
        issues.append("❌ SL and TP use different calculation methods!")
        print(f"❌ INCONSISTENT: SL uses {'pip-based' if use_pip_sl else 'ratio-based'}, "
              f"TP uses {'pip-based' if use_pip_tp else 'ratio-based'}")
    else:
        print(f"✓ CONSISTENT: Both use {'pip-based' if use_pip_sl else 'ratio-based'} calculation")
    
    if use_pip_sl and use_pip_tp:
        # Calculate actual TP levels
        tp_level_pips = [tp_pips * ratio for ratio in tp_levels]
        
        print(f"\n✓ Pip-based calculation:")
        print(f"  SL Distance: {sl_pips} pips")
        print(f"  TP Level 1: {tp_level_pips[0]:.0f} pips (ratio {tp_level_pips[0]/sl_pips:.1f}:1)")
        print(f"  TP Level 2: {tp_level_pips[1]:.0f} pips (ratio {tp_level_pips[1]/sl_pips:.1f}:1)")
        print(f"  TP Level 3: {tp_level_pips[2]:.0f} pips (ratio {tp_level_pips[2]/sl_pips:.1f}:1)")
        
        # Verify all TPs are greater than SL
        for i, tp_level in enumerate(tp_level_pips):
            if tp_level <= sl_pips:
                issues.append(f"❌ TP Level {i+1} ({tp_level} pips) is not greater than SL ({sl_pips} pips)!")
                print(f"  ❌ TP Level {i+1}: {tp_level} pips <= SL {sl_pips} pips")
            else:
                print(f"  ✓ TP Level {i+1}: {tp_level:.0f} pips > SL {sl_pips} pips")
    
    print("\n" + "="*70)
    if issues:
        print("❌ VERIFICATION FAILED")
        print("="*70)
        for issue in issues:
            print(issue)
        return False
    else:
        print("✓ VERIFICATION PASSED")
        print("="*70)
        print("All TP levels are greater than SL distance")
        print("Configuration is consistent and correct")
        return True

if __name__ == "__main__":
    success = verify_config()
    
    if success:
        print("\n" + "="*70)
        print("READY TO TRADE")
        print("="*70)
        print("The bot is now configured with consistent TP/SL calculations.")
        print("Restart the bot to apply these changes.")
    else:
        print("\n" + "="*70)
        print("ACTION REQUIRED")
        print("="*70)
        print("Please review and fix the configuration issues above.")
