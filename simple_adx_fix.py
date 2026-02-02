#!/usr/bin/env python3
"""
Simple, targeted fix for ADX KeyError
Only fixes the specific line that causes the error
"""

import os
import re
import shutil
from datetime import datetime

def simple_adx_fix():
    """Apply a simple, targeted fix for the ADX KeyError"""
    
    bot_file = "src/mt5_trading_bot.py"
    
    if not os.path.exists(bot_file):
        print(f"❌ Error: {bot_file} not found")
        return False
    
    # Create backup
    backup_file = f"{bot_file}_backup_simple_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(bot_file, backup_file)
    print(f"✅ Backup created: {backup_file}")
    
    # Read the file
    with open(bot_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Simple fix: Replace the problematic line
    # Find: if 'adx' in df.columns and not pd.isna(latest['adx']):
    # Replace: if 'adx' in df.columns and 'adx' in latest.index and not pd.isna(latest.get('adx', 0)):
    
    original_pattern = r"if 'adx' in df\.columns and not pd\.isna\(latest\['adx'\]\):"
    fixed_pattern = "if 'adx' in df.columns and 'adx' in latest.index and not pd.isna(latest.get('adx', 0)):"
    
    if re.search(original_pattern, content):
        content = re.sub(original_pattern, fixed_pattern, content)
        print("✅ Fixed: ADX column existence check")
    
    # Fix any direct access to latest['adx'] 
    content = re.sub(r"adx = latest\['adx'\]", "adx = latest.get('adx', 0)", content)
    print("✅ Fixed: ADX value access")
    
    # Fix plus_di and minus_di access
    content = re.sub(r"latest\['plus_di'\]", "latest.get('plus_di', 0)", content)
    content = re.sub(r"latest\['minus_di'\]", "latest.get('minus_di', 0)", content)
    print("✅ Fixed: Plus DI and Minus DI access")
    
    # Write the fixed content back
    with open(bot_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Applied simple ADX fix to {bot_file}")
    return True

def test_syntax():
    """Test if the file has valid Python syntax"""
    try:
        with open("src/mt5_trading_bot.py", 'r', encoding='utf-8') as f:
            code = f.read()
        
        compile(code, "src/mt5_trading_bot.py", "exec")
        print("✅ Syntax check passed")
        return True
    except SyntaxError as e:
        print(f"❌ Syntax error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 SIMPLE ADX KEYERROR FIX")
    print("=" * 60)
    
    if simple_adx_fix():
        if test_syntax():
            print("\n🎉 Simple ADX fix completed successfully!")
            print("✅ No syntax errors detected")
        else:
            print("\n⚠️  Fix applied but syntax errors remain")
    else:
        print("\n❌ Failed to apply simple ADX fix")
    
    print("\n📝 Next steps:")
    print("1. Restart the trading bot")
    print("2. Monitor for ADX KeyErrors")
    print("3. The bot should handle missing ADX data gracefully")