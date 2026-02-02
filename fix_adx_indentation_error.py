#!/usr/bin/env python3
"""
Fix the indentation error caused by the ADX fix
"""

import os
import shutil
from datetime import datetime

def fix_indentation_error():
    """Fix the indentation error in the ADX section"""
    
    bot_file = "src/mt5_trading_bot.py"
    
    if not os.path.exists(bot_file):
        print(f"❌ Error: {bot_file} not found")
        return False
    
    # Create backup
    backup_file = f"{bot_file}_backup_indent_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(bot_file, backup_file)
    print(f"✅ Backup created: {backup_file}")
    
    # Read the file
    with open(bot_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find and remove the incorrectly placed ADX safety code
    fixed_lines = []
    skip_lines = False
    adx_safety_start = False
    
    for i, line in enumerate(lines):
        # Detect start of incorrectly placed ADX safety code
        if "# ADX SAFETY CHECK - Prevent KeyError" in line:
            adx_safety_start = True
            skip_lines = True
            print(f"✅ Found incorrectly placed ADX safety code at line {i+1}")
            continue
        
        # Detect end of ADX safety code block
        if skip_lines and line.strip().startswith("if self.config.get('use_adx', True):"):
            skip_lines = False
            # Keep this line but fix the indentation issue
            continue
        
        # Skip lines that are part of the incorrectly placed ADX safety code
        if skip_lines:
            continue
        
        # Fix duplicate if statements
        if "if adx_available:" in line and i < len(lines) - 1:
            next_line = lines[i + 1] if i + 1 < len(lines) else ""
            if "if self.config.get('use_adx', True):" in next_line:
                # Skip the duplicate if statement
                continue
        
        fixed_lines.append(line)
    
    # Write the fixed content back
    with open(bot_file, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print(f"✅ Fixed indentation error in {bot_file}")
    return True

def apply_correct_adx_fix():
    """Apply the ADX fix in the correct location (check_entry_signal method)"""
    
    bot_file = "src/mt5_trading_bot.py"
    
    with open(bot_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the check_entry_signal method and add proper ADX safety
    # Look for the pattern where ADX is accessed unsafely
    import re
    
    # Pattern to find unsafe ADX access in check_entry_signal
    pattern = r"(if 'adx' in df\.columns and 'adx' in latest\.index and not pd\.isna\(latest\.get\('adx', 0\)\):)"
    
    if re.search(pattern, content):
        print("✅ ADX safety check already present in check_entry_signal")
        return True
    
    # Look for the original unsafe pattern and replace it
    unsafe_pattern = r"if 'adx' in df\.columns and not pd\.isna\(latest\['adx'\]\):"
    safe_replacement = "if 'adx' in df.columns and 'adx' in latest.index and not pd.isna(latest.get('adx', 0)):"
    
    if re.search(unsafe_pattern, content):
        content = re.sub(unsafe_pattern, safe_replacement, content)
        print("✅ Applied safe ADX access pattern")
    
    # Replace any remaining unsafe ADX access
    content = re.sub(r"latest\['adx'\]", "latest.get('adx', 0)", content)
    content = re.sub(r"latest\['plus_di'\]", "latest.get('plus_di', 0)", content)
    content = re.sub(r"latest\['minus_di'\]", "latest.get('minus_di', 0)", content)
    
    # Write back
    with open(bot_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Applied correct ADX safety fixes")
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 FIXING ADX INDENTATION ERROR")
    print("=" * 60)
    
    if fix_indentation_error():
        if apply_correct_adx_fix():
            print("\n🎉 ADX indentation error fixed successfully!")
            print("✅ The bot should now start without syntax errors")
        else:
            print("\n⚠️  Indentation fixed but ADX safety not applied")
    else:
        print("\n❌ Failed to fix indentation error")
    
    print("\n📝 Next steps:")
    print("1. Restart the trading bot")
    print("2. Verify no more syntax errors")
    print("3. Monitor for ADX KeyErrors")