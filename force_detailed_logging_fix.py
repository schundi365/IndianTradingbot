#!/usr/bin/env python3
"""
Force detailed logging fix - Replace calculate_indicators calls with wrapper
"""

import sys
import os
from pathlib import Path

def fix_detailed_logging():
    """Replace all calculate_indicators calls with the wrapper method"""
    
    # Read the current bot file
    bot_file = Path("src/mt5_trading_bot.py")
    
    if not bot_file.exists():
        print("❌ Bot file not found!")
        return False
    
    print("📖 Reading current bot file...")
    with open(bot_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count current occurrences
    original_calls = content.count('self.calculate_indicators(')
    wrapper_calls = content.count('self.calculate_indicators_with_logging(')
    
    print(f"📊 Current state:")
    print(f"   Original calls: {original_calls}")
    print(f"   Wrapper calls: {wrapper_calls}")
    
    if original_calls == 0:
        print("✅ All calls are already using the wrapper!")
        return True
    
    # Replace all calculate_indicators calls with the wrapper
    print("🔄 Replacing calculate_indicators calls with wrapper...")
    
    # Replace the calls (but not the method definition)
    lines = content.split('\n')
    modified_lines = []
    
    for line in lines:
        # Skip method definitions
        if 'def calculate_indicators' in line:
            modified_lines.append(line)
        # Replace method calls
        elif 'self.calculate_indicators(' in line and 'self.calculate_indicators_with_logging(' not in line:
            # Replace the call
            new_line = line.replace('self.calculate_indicators(', 'self.calculate_indicators_with_logging(')
            modified_lines.append(new_line)
            print(f"   ✅ Replaced: {line.strip()}")
        else:
            modified_lines.append(line)
    
    # Write the modified content
    modified_content = '\n'.join(modified_lines)
    
    # Create backup
    backup_file = f"src/mt5_trading_bot_backup_{int(time.time())}.py"
    print(f"💾 Creating backup: {backup_file}")
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Write modified file
    print("💾 Writing modified bot file...")
    with open(bot_file, 'w', encoding='utf-8') as f:
        f.write(modified_content)
    
    # Verify changes
    with open(bot_file, 'r', encoding='utf-8') as f:
        new_content = f.read()
    
    new_original_calls = new_content.count('self.calculate_indicators(')
    new_wrapper_calls = new_content.count('self.calculate_indicators_with_logging(')
    
    print(f"📊 After modification:")
    print(f"   Original calls: {new_original_calls}")
    print(f"   Wrapper calls: {new_wrapper_calls}")
    
    if new_original_calls == 0:
        print("✅ SUCCESS: All calls now use the wrapper method!")
        print("🔄 Please restart the bot to see detailed logging")
        return True
    else:
        print("❌ Some calls were not replaced")
        return False

if __name__ == "__main__":
    import time
    
    print("🔧 FORCE DETAILED LOGGING FIX")
    print("=" * 50)
    
    success = fix_detailed_logging()
    
    if success:
        print("\n✅ FIX APPLIED SUCCESSFULLY!")
        print("📝 Next steps:")
        print("   1. Restart the web dashboard")
        print("   2. Restart the trading bot")
        print("   3. Check trading_bot.log for detailed indicator calculations")
    else:
        print("\n❌ FIX FAILED!")
        print("   Please check the file manually")