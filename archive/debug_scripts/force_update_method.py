#!/usr/bin/env python3
"""
Force update the calculate_indicators method with a unique signature
"""

import sys
import os
from pathlib import Path

def force_update_method():
    """Force update the method with a unique signature"""
    
    bot_file = Path("src/mt5_trading_bot.py")
    
    if not bot_file.exists():
        print("❌ Bot file not found!")
        return False
    
    print("📖 Reading current bot file...")
    with open(bot_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the calculate_indicators method and replace the first few lines
    method_start = 'def calculate_indicators(self, df):'
    
    if method_start not in content:
        print("❌ calculate_indicators method not found!")
        return False
    
    # Find the method and replace the logging section
    lines = content.split('\n')
    modified_lines = []
    in_method = False
    method_found = False
    
    for i, line in enumerate(lines):
        if method_start in line:
            in_method = True
            method_found = True
            modified_lines.append(line)
        elif in_method and line.strip().startswith('logging.info("') and 'CALCULATE_INDICATORS' in line:
            # Replace this line with our unique identifier
            indent = len(line) - len(line.lstrip())
            modified_lines.append(' ' * indent + 'logging.info("🔥🔥🔥 UNIQUE_METHOD_SIGNATURE_2026_02_01_FORCE_UPDATE 🔥🔥🔥")')
            modified_lines.append(' ' * indent + 'logging.info("🚨 DETAILED LOGGING IS NOW WORKING - VERSION 2.0 🚨")')
            modified_lines.append(' ' * indent + 'logging.info("="*80)')
        elif in_method and line.strip().startswith('def ') and method_start not in line:
            # Next method started, we're done with this method
            in_method = False
            modified_lines.append(line)
        else:
            modified_lines.append(line)
    
    if not method_found:
        print("❌ Could not find calculate_indicators method")
        return False
    
    # Write the modified content
    modified_content = '\n'.join(modified_lines)
    
    # Create backup
    import time
    backup_file = f"src/mt5_trading_bot_backup_force_update_{int(time.time())}.py"
    print(f"💾 Creating backup: {backup_file}")
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Write modified file
    print("💾 Writing force updated bot file...")
    with open(bot_file, 'w', encoding='utf-8') as f:
        f.write(modified_content)
    
    print("✅ Method force updated with unique signature!")
    return True

if __name__ == "__main__":
    print("🔧 FORCE UPDATE METHOD")
    print("=" * 50)
    
    success = force_update_method()
    
    if success:
        print("\n✅ FORCE UPDATE SUCCESSFUL!")
        print("📝 Method now has unique signature that should appear in logs")
        print("🔄 Test the bot to see if the unique signature appears")
    else:
        print("\n❌ FORCE UPDATE FAILED!")
        print("   Please check the file manually")