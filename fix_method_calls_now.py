#!/usr/bin/env python3
"""
Fix method calls - Replace calculate_indicators_with_logging with calculate_indicators
"""

import sys
import os
from pathlib import Path

def fix_method_calls():
    """Replace all calculate_indicators_with_logging calls with calculate_indicators"""
    
    bot_file = Path("src/mt5_trading_bot.py")
    
    if not bot_file.exists():
        print("❌ Bot file not found!")
        return False
    
    print("📖 Reading current bot file...")
    with open(bot_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count current occurrences
    wrapper_calls = content.count('self.calculate_indicators_with_logging(')
    original_calls = content.count('self.calculate_indicators(')
    
    print(f"📊 Current state:")
    print(f"   Wrapper calls: {wrapper_calls}")
    print(f"   Original calls: {original_calls}")
    
    if wrapper_calls == 0:
        print("✅ No wrapper calls found - already fixed!")
        return True
    
    # Replace all wrapper calls with original calls
    print("🔄 Replacing wrapper calls with original method...")
    
    modified_content = content.replace(
        'self.calculate_indicators_with_logging(',
        'self.calculate_indicators('
    )
    
    # Verify changes
    new_wrapper_calls = modified_content.count('self.calculate_indicators_with_logging(')
    new_original_calls = modified_content.count('self.calculate_indicators(')
    
    print(f"📊 After replacement:")
    print(f"   Wrapper calls: {new_wrapper_calls}")
    print(f"   Original calls: {new_original_calls}")
    
    if new_wrapper_calls == 0:
        # Create backup
        import time
        backup_file = f"src/mt5_trading_bot_backup_method_fix_{int(time.time())}.py"
        print(f"💾 Creating backup: {backup_file}")
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Write modified file
        print("💾 Writing fixed bot file...")
        with open(bot_file, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        print("✅ SUCCESS: All method calls fixed!")
        return True
    else:
        print("❌ Some calls were not replaced")
        return False

if __name__ == "__main__":
    print("🔧 FIX METHOD CALLS")
    print("=" * 50)
    
    success = fix_method_calls()
    
    if success:
        print("\n✅ METHOD CALLS FIXED SUCCESSFULLY!")
        print("📝 All calls now use calculate_indicators() which has detailed logging")
        print("🔄 The bot should now work without errors")
    else:
        print("\n❌ FIX FAILED!")
        print("   Please check the file manually")