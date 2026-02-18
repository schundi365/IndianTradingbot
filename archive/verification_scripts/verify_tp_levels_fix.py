"""
Verify TP Levels Fix
=====================
Confirms that the contradiction has been resolved
"""

import json

def verify_config():
    """Verify bot_config.json has no contradictions"""
    
    print("="*70)
    print("VERIFYING TP LEVELS CONFIGURATION")
    print("="*70)
    
    with open('bot_config.json', 'r') as f:
        config = json.load(f)
    
    # Check for obsolete fields
    has_tp_level_1 = 'tp_level_1' in config
    has_tp_level_2 = 'tp_level_2' in config
    has_tp_level_3 = 'tp_level_3' in config
    has_tp_levels = 'tp_levels' in config
    
    print("\nConfiguration Status:")
    print(f"  tp_level_1 exists: {has_tp_level_1}")
    print(f"  tp_level_2 exists: {has_tp_level_2}")
    print(f"  tp_level_3 exists: {has_tp_level_3}")
    print(f"  tp_levels exists: {has_tp_levels}")
    
    if has_tp_levels:
        print(f"\n  tp_levels value: {config['tp_levels']}")
    
    # Verify no contradiction
    print("\n" + "="*70)
    print("VERIFICATION RESULTS")
    print("="*70)
    
    issues = []
    
    if has_tp_level_1 or has_tp_level_2 or has_tp_level_3:
        issues.append("❌ Obsolete individual tp_level fields still exist")
        print("❌ FAILED: Obsolete fields found")
        if has_tp_level_1:
            print(f"  - tp_level_1: {config['tp_level_1']}")
        if has_tp_level_2:
            print(f"  - tp_level_2: {config['tp_level_2']}")
        if has_tp_level_3:
            print(f"  - tp_level_3: {config['tp_level_3']}")
    else:
        print("✓ No obsolete individual fields")
    
    if not has_tp_levels:
        issues.append("❌ tp_levels array is missing")
        print("❌ FAILED: tp_levels array not found")
    else:
        print("✓ tp_levels array exists")
        
        # Validate array format
        tp_levels = config['tp_levels']
        if not isinstance(tp_levels, list):
            issues.append("❌ tp_levels is not an array")
            print("❌ FAILED: tp_levels is not an array")
        elif len(tp_levels) != 3:
            issues.append(f"❌ tp_levels has {len(tp_levels)} elements (expected 3)")
            print(f"❌ FAILED: tp_levels has {len(tp_levels)} elements (expected 3)")
        else:
            print(f"✓ tp_levels is a valid array with 3 elements")
            
            # Check values are in ascending order
            if tp_levels[0] < tp_levels[1] < tp_levels[2]:
                print(f"✓ TP levels are in ascending order: {tp_levels}")
            else:
                issues.append("⚠️ TP levels are not in ascending order")
                print(f"⚠️ WARNING: TP levels not in ascending order: {tp_levels}")
    
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
        print("Configuration is clean and consistent")
        print(f"TP Levels: {config['tp_levels']}")
        return True

def verify_dashboard():
    """Verify dashboard saves to array"""
    
    print("\n" + "="*70)
    print("VERIFYING DASHBOARD CODE")
    print("="*70)
    
    with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if dashboard saves to array
    saves_array = 'tp_levels: [' in content
    saves_individual = 'tp_level_1: parseFloat' in content
    
    print(f"\nDashboard saves to tp_levels array: {saves_array}")
    print(f"Dashboard saves individual fields: {saves_individual}")
    
    if saves_array and not saves_individual:
        print("\n✓ Dashboard correctly saves to tp_levels array")
        return True
    elif saves_individual:
        print("\n❌ Dashboard still saves individual fields")
        return False
    else:
        print("\n❌ Dashboard doesn't save TP levels")
        return False

def verify_config_manager():
    """Verify config_manager has no obsolete defaults"""
    
    print("\n" + "="*70)
    print("VERIFYING CONFIG MANAGER")
    print("="*70)
    
    with open('src/config_manager.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    has_individual = "'tp_level_1':" in content or "'tp_level_2':" in content or "'tp_level_3':" in content
    has_array = "'tp_levels':" in content
    
    print(f"\nConfig manager has individual fields: {has_individual}")
    print(f"Config manager has tp_levels array: {has_array}")
    
    if has_array and not has_individual:
        print("\n✓ Config manager correctly uses tp_levels array")
        return True
    elif has_individual:
        print("\n❌ Config manager still has individual fields")
        return False
    else:
        print("\n❌ Config manager doesn't have TP levels")
        return False

if __name__ == "__main__":
    print("="*70)
    print("TP LEVELS CONTRADICTION VERIFICATION")
    print("="*70)
    
    config_ok = verify_config()
    dashboard_ok = verify_dashboard()
    manager_ok = verify_config_manager()
    
    print("\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)
    print(f"Config file: {'✓ PASS' if config_ok else '❌ FAIL'}")
    print(f"Dashboard: {'✓ PASS' if dashboard_ok else '❌ FAIL'}")
    print(f"Config manager: {'✓ PASS' if manager_ok else '❌ FAIL'}")
    
    if config_ok and dashboard_ok and manager_ok:
        print("\n" + "="*70)
        print("✓ ALL CHECKS PASSED")
        print("="*70)
        print("TP levels contradiction has been fully resolved!")
        print("\nYou can now:")
        print("1. Use the dashboard to change TP levels")
        print("2. Values will be saved to tp_levels array")
        print("3. Bot will read from tp_levels array")
        print("4. No more contradictions!")
    else:
        print("\n" + "="*70)
        print("❌ SOME CHECKS FAILED")
        print("="*70)
        print("Please review the issues above and fix them.")
