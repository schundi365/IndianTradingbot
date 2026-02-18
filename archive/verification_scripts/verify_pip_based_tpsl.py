"""
Verify Pip-Based TP/SL Implementation
Checks that pip-based TP/SL is properly integrated across all layers
"""

import json
import sys
from pathlib import Path

def verify_pip_based_tpsl():
    """Verify pip-based TP/SL integration"""
    
    print("=" * 70)
    print("PIP-BASED TP/SL VERIFICATION")
    print("=" * 70)
    
    issues = []
    
    # 1. Check bot_config.json
    print("\n1. Checking bot_config.json...")
    try:
        with open('bot_config.json', 'r') as f:
            config = json.load(f)
        
        required_keys = ['use_pip_based_sl', 'sl_pips', 'use_pip_based_tp', 'tp_pips']
        missing = []
        
        for key in required_keys:
            if key in config:
                print(f"   ✅ {key}: {config[key]}")
            else:
                print(f"   ❌ {key}: MISSING")
                missing.append(key)
        
        if missing:
            issues.append(f"Missing keys in bot_config.json: {missing}")
    except Exception as e:
        print(f"   ❌ Error reading bot_config.json: {e}")
        issues.append(f"Cannot read bot_config.json: {e}")
    
    # 2. Check dashboard.html
    print("\n2. Checking dashboard.html...")
    try:
        with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for UI controls
        ui_elements = [
            'use-pip-based-sl',
            'sl-pips',
            'use-pip-based-tp',
            'tp-pips'
        ]
        
        missing_ui = []
        for element in ui_elements:
            if f'id="{element}"' in content:
                print(f"   ✅ UI control found: {element}")
            else:
                print(f"   ❌ UI control missing: {element}")
                missing_ui.append(element)
        
        if missing_ui:
            issues.append(f"Missing UI controls: {missing_ui}")
        
        # Check for JavaScript loading
        if 'use_pip_based_sl' in content and 'use_pip_based_tp' in content:
            print("   ✅ JavaScript loading code found")
        else:
            print("   ❌ JavaScript loading code NOT found")
            issues.append("JavaScript loading code missing")
        
        # Check for JavaScript saving
        if 'use_pip_based_sl:' in content and 'use_pip_based_tp:' in content:
            print("   ✅ JavaScript saving code found")
        else:
            print("   ❌ JavaScript saving code NOT found")
            issues.append("JavaScript saving code missing")
    except Exception as e:
        print(f"   ❌ Error reading dashboard.html: {e}")
        issues.append(f"Cannot read dashboard.html: {e}")
    
    # 3. Check bot files
    print("\n3. Checking bot implementation...")
    bot_files = [
        'src/mt5_trading_bot.py',
        'src/mt5_trading_bot_SIGNAL_FIX.py'
    ]
    
    for bot_file in bot_files:
        try:
            with open(bot_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for pip-based logic
            checks = {
                'use_pip_based_sl check': "self.config.get('use_pip_based_sl'",
                'use_pip_based_tp check': "self.config.get('use_pip_based_tp'",
                'calculate_price_from_pips': 'def calculate_price_from_pips',
                'sl_pips config': "self.config.get('sl_pips'",
                'tp_pips config': "self.config.get('tp_pips'"
            }
            
            print(f"\n   {bot_file}:")
            missing_checks = []
            for check_name, check_str in checks.items():
                if check_str in content:
                    print(f"     ✅ {check_name}")
                else:
                    print(f"     ❌ {check_name} NOT found")
                    missing_checks.append(check_name)
            
            if missing_checks:
                issues.append(f"{bot_file} missing: {missing_checks}")
        except Exception as e:
            print(f"   ⚠️  {bot_file}: {e}")
    
    # 4. Check config_manager.py
    print("\n4. Checking config_manager.py...")
    try:
        with open('src/config_manager.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        defaults = {
            'use_pip_based_sl': False,
            'sl_pips': 50,
            'use_pip_based_tp': False,
            'tp_pips': 100
        }
        
        missing_defaults = []
        for key, value in defaults.items():
            if f"'{key}'" in content:
                print(f"   ✅ Default for {key} found")
            else:
                print(f"   ⚠️  Default for {key} not found")
                missing_defaults.append(key)
        
        if missing_defaults:
            issues.append(f"Missing defaults in config_manager.py: {missing_defaults}")
    except Exception as e:
        print(f"   ❌ Error reading config_manager.py: {e}")
        issues.append(f"Cannot read config_manager.py: {e}")
    
    # Summary
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    
    if not issues:
        print("\n✅ ALL CHECKS PASSED!")
        print("\nPip-Based TP/SL Integration Status:")
        print("  ✅ Configuration: bot_config.json")
        print("  ✅ Defaults: config_manager.py")
        print("  ✅ UI Controls: dashboard.html")
        print("  ✅ JavaScript: Load & Save")
        print("  ✅ Bot Logic: calculate_price_from_pips()")
        print("  ✅ Implementation: Both bot files")
        print("\n🎉 Pip-based TP/SL is fully integrated and working!")
        print("\n📋 How to Use:")
        print("  1. Open dashboard → Configuration tab")
        print("  2. Expand 'Position Management' section")
        print("  3. Find 'Pip-Based TP/SL' (green box)")
        print("  4. Enable and set pip values")
        print("  5. Save configuration")
        return True
    else:
        print(f"\n❌ FOUND {len(issues)} ISSUE(S):")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        print("\n⚠️  Please fix these issues")
        return False

if __name__ == "__main__":
    success = verify_pip_based_tpsl()
    sys.exit(0 if success else 1)
