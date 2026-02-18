#!/usr/bin/env python3
"""
Final fix for ADX KeyError in mt5_trading_bot.py
This script will fix the issue where the code tries to access latest['adx'] 
when the 'adx' column doesn't exist in the dataframe.
"""

import os
import re
import shutil
from datetime import datetime

def fix_adx_keyerror():
    """Fix the ADX KeyError by adding proper safety checks"""
    
    bot_file = "src/mt5_trading_bot.py"
    
    if not os.path.exists(bot_file):
        print(f"❌ Error: {bot_file} not found")
        return False
    
    # Create backup
    backup_file = f"{bot_file}_backup_adx_keyerror_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(bot_file, backup_file)
    print(f"✅ Backup created: {backup_file}")
    
    # Read the file
    with open(bot_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern 1: Fix the main ADX KeyError issue
    # Replace: if 'adx' in df.columns and not pd.isna(latest['adx']):
    # With: if 'adx' in df.columns and 'adx' in latest.index and not pd.isna(latest['adx']):
    pattern1 = r"if 'adx' in df\.columns and not pd\.isna\(latest\['adx'\]\):"
    replacement1 = "if 'adx' in df.columns and 'adx' in latest.index and not pd.isna(latest['adx']):"
    
    if re.search(pattern1, content):
        content = re.sub(pattern1, replacement1, content)
        print("✅ Fixed: ADX column check with proper index validation")
    else:
        print("⚠️  Pattern 1 not found - checking alternative patterns")
    
    # Pattern 2: Fix any direct access to latest['adx'] without checking
    # Replace: latest['adx']
    # With: latest.get('adx', 0)
    pattern2 = r"latest\['adx'\]"
    replacement2 = "latest.get('adx', 0)"
    
    # Only replace if not already in a safe context
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Skip lines that already have proper checks
        if "if 'adx' in df.columns and 'adx' in latest.index" in line:
            fixed_lines.append(line)
        elif "latest['adx']" in line and "latest.get('adx'" not in line:
            # Replace unsafe access with safe access
            fixed_line = re.sub(pattern2, replacement2, line)
            fixed_lines.append(fixed_line)
            if fixed_line != line:
                print(f"✅ Fixed unsafe ADX access: {line.strip()}")
        else:
            fixed_lines.append(line)
    
    content = '\n'.join(fixed_lines)
    
    # Pattern 3: Fix any other ADX-related KeyError patterns
    # Look for patterns like: adx = latest['adx']
    pattern3 = r"(\s+)adx = latest\['adx'\]"
    replacement3 = r"\1adx = latest.get('adx', 0)"
    
    if re.search(pattern3, content):
        content = re.sub(pattern3, replacement3, content)
        print("✅ Fixed: ADX variable assignment with safe access")
    
    # Pattern 4: Fix plus_di and minus_di similar issues
    pattern4 = r"plus_di = latest\.get\('plus_di', 0\) if 'plus_di' in df\.columns else 0 if 'plus_di' in df\.columns else 0"
    replacement4 = "plus_di = latest.get('plus_di', 0) if 'plus_di' in df.columns else 0"
    
    if re.search(pattern4, content):
        content = re.sub(pattern4, replacement4, content)
        print("✅ Fixed: Redundant plus_di check")
    
    pattern5 = r"minus_di = latest\.get\('minus_di', 0\) if 'minus_di' in df\.columns else 0 if 'minus_di' in df\.columns else 0"
    replacement5 = "minus_di = latest.get('minus_di', 0) if 'minus_di' in df.columns else 0"
    
    if re.search(pattern5, content):
        content = re.sub(pattern5, replacement5, content)
        print("✅ Fixed: Redundant minus_di check")
    
    # Pattern 6: Add comprehensive ADX safety wrapper
    adx_safety_code = '''
        # ADX SAFETY CHECK - Prevent KeyError
        try:
            if 'adx' in df.columns and len(df) > 0:
                # Ensure ADX column exists and has valid data
                if 'adx' in df.iloc[-1].index and not pd.isna(df.iloc[-1]['adx']):
                    adx_available = True
                else:
                    adx_available = False
                    logging.info(f"   ⚠️  ADX data not available or invalid - skipping ADX filter")
            else:
                adx_available = False
                logging.info(f"   ⚠️  ADX column not found - skipping ADX filter")
        except Exception as e:
            adx_available = False
            logging.error(f"   ❌ ADX safety check failed: {e}")
        
        if adx_available:'''
    
    # Look for the ADX TREND DIRECTION FILTER section and add safety
    adx_filter_pattern = r"(logging\.info\(\"-\"\*80\)\s*\n\s*logging\.info\(\"🔍 ADX TREND DIRECTION FILTER:\"\))"
    
    if re.search(adx_filter_pattern, content):
        content = re.sub(adx_filter_pattern, r"\1" + adx_safety_code, content)
        print("✅ Added: Comprehensive ADX safety wrapper")
    
    # Write the fixed content back
    with open(bot_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Fixed ADX KeyError issues in {bot_file}")
    return True

def verify_fix():
    """Verify that the fix was applied correctly"""
    
    bot_file = "src/mt5_trading_bot.py"
    
    with open(bot_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ("Safe ADX access", "latest.get('adx'" in content),
        ("ADX column validation", "'adx' in latest.index" in content or "adx_available" in content),
        ("No unsafe ADX access", "latest['adx']" not in content or content.count("latest['adx']") <= 1),
        ("Plus DI safe access", "latest.get('plus_di'" in content),
        ("Minus DI safe access", "latest.get('minus_di'" in content)
    ]
    
    print("\n🔍 Verification Results:")
    all_passed = True
    
    for check_name, passed in checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {check_name}: {status}")
        if not passed:
            all_passed = False
    
    return all_passed

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 FIXING ADX KEYERROR IN MT5 TRADING BOT")
    print("=" * 60)
    
    if fix_adx_keyerror():
        if verify_fix():
            print("\n🎉 ADX KeyError fix completed successfully!")
            print("✅ The bot should now handle missing ADX data gracefully")
        else:
            print("\n⚠️  Fix applied but verification failed")
            print("   Please check the file manually")
    else:
        print("\n❌ Failed to apply ADX KeyError fix")
    
    print("\n📝 Next steps:")
    print("1. Restart the trading bot to apply the fix")
    print("2. Monitor the logs to ensure no more ADX KeyErrors")
    print("3. The bot will now skip ADX filter when data is unavailable")