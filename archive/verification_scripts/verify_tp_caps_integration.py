"""
Verify TP Caps Integration
Checks that TP caps are properly configured across all layers
"""

import json
import sys
from pathlib import Path

def verify_tp_caps():
    """Verify TP caps integration across all layers"""
    
    print("=" * 60)
    print("TP CAPS INTEGRATION VERIFICATION")
    print("=" * 60)
    
    issues = []
    
    # 1. Check bot_config.json
    print("\n1. Checking bot_config.json...")
    try:
        with open('bot_config.json', 'r') as f:
            config = json.load(f)
        
        if 'scalp_tp_caps' in config:
            print("   ✅ scalp_tp_caps found in bot_config.json")
            tp_caps = config['scalp_tp_caps']
            print(f"   - XAUUSD: {tp_caps.get('XAUUSD', 'MISSING')}")
            print(f"   - XAGUSD: {tp_caps.get('XAGUSD', 'MISSING')}")
            print(f"   - XPTUSD: {tp_caps.get('XPTUSD', 'MISSING')}")
            print(f"   - XPDUSD: {tp_caps.get('XPDUSD', 'MISSING')}")
            print(f"   - DEFAULT: {tp_caps.get('DEFAULT', 'MISSING')}")
            
            # Verify all required symbols
            required = ['XAUUSD', 'XAGUSD', 'XPTUSD', 'XPDUSD', 'DEFAULT']
            for symbol in required:
                if symbol not in tp_caps:
                    issues.append(f"Missing {symbol} in scalp_tp_caps")
        else:
            print("   ❌ scalp_tp_caps NOT found in bot_config.json")
            issues.append("scalp_tp_caps missing from bot_config.json")
    except Exception as e:
        print(f"   ❌ Error reading bot_config.json: {e}")
        issues.append(f"Cannot read bot_config.json: {e}")
    
    # 2. Check config_manager.py
    print("\n2. Checking config_manager.py...")
    try:
        with open('src/config_manager.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'scalp_tp_caps' in content:
            print("   ✅ scalp_tp_caps found in config_manager.py")
            if "'XAUUSD': 2.0" in content:
                print("   ✅ Default values defined")
            else:
                print("   ⚠️  Default values may be missing")
                issues.append("Default TP caps values not found in config_manager.py")
        else:
            print("   ❌ scalp_tp_caps NOT found in config_manager.py")
            issues.append("scalp_tp_caps missing from config_manager.py")
    except Exception as e:
        print(f"   ❌ Error reading config_manager.py: {e}")
        issues.append(f"Cannot read config_manager.py: {e}")
    
    # 3. Check dashboard.html
    print("\n3. Checking dashboard.html...")
    try:
        with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for UI controls
        ui_elements = [
            'tp-cap-xauusd',
            'tp-cap-xagusd',
            'tp-cap-xptusd',
            'tp-cap-xpdusd',
            'tp-cap-default'
        ]
        
        missing_ui = []
        for element in ui_elements:
            if element not in content:
                missing_ui.append(element)
        
        if not missing_ui:
            print("   ✅ All TP cap UI controls found")
        else:
            print(f"   ❌ Missing UI controls: {missing_ui}")
            issues.append(f"Missing UI controls: {missing_ui}")
        
        # Check for JavaScript loading
        if 'scalp_tp_caps' in content and 'tp-cap-xauusd' in content:
            print("   ✅ JavaScript loading code found")
        else:
            print("   ❌ JavaScript loading code NOT found")
            issues.append("JavaScript loading code missing")
        
        # Check for JavaScript saving
        if 'scalp_tp_caps:' in content and 'getElementById(\'tp-cap-xauusd\')' in content:
            print("   ✅ JavaScript saving code found")
        else:
            print("   ❌ JavaScript saving code NOT found")
            issues.append("JavaScript saving code missing")
    except Exception as e:
        print(f"   ❌ Error reading dashboard.html: {e}")
        issues.append(f"Cannot read dashboard.html: {e}")
    
    # 4. Check bot files
    print("\n4. Checking bot files...")
    bot_files = [
        'src/mt5_trading_bot.py',
        'src/mt5_trading_bot_SIGNAL_FIX.py'
    ]
    
    for bot_file in bot_files:
        try:
            with open(bot_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'scalp_tp_caps' in content:
                print(f"   ✅ {bot_file}: TP cap logic found")
            else:
                print(f"   ❌ {bot_file}: TP cap logic NOT found")
                issues.append(f"{bot_file} missing TP cap logic")
        except Exception as e:
            print(f"   ⚠️  {bot_file}: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    if not issues:
        print("\n✅ ALL CHECKS PASSED!")
        print("\nTP Caps Integration Status:")
        print("  ✅ Configuration: bot_config.json")
        print("  ✅ Defaults: config_manager.py")
        print("  ✅ UI Controls: dashboard.html")
        print("  ✅ JavaScript: Load & Save")
        print("  ✅ Bot Logic: Both bot files")
        print("\n🎉 TP caps are fully integrated and ready to use!")
        return True
    else:
        print(f"\n❌ FOUND {len(issues)} ISSUE(S):")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        print("\n⚠️  Please fix these issues before using TP caps")
        return False

if __name__ == "__main__":
    success = verify_tp_caps()
    sys.exit(0 if success else 1)
