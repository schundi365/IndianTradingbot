#!/usr/bin/env python3
"""
Simple fix - Add detailed logging directly to calculate_indicators method
"""

import sys
import os
from pathlib import Path

def add_detailed_logging_to_method():
    """Add detailed logging directly to the calculate_indicators method"""
    
    bot_file = Path("src/mt5_trading_bot.py")
    
    if not bot_file.exists():
        print("❌ Bot file not found!")
        return False
    
    print("📖 Reading current bot file...")
    with open(bot_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the calculate_indicators method and add logging at the beginning
    method_start = 'def calculate_indicators(self, df):'
    
    if method_start not in content:
        print("❌ calculate_indicators method not found!")
        return False
    
    # Find the method and add detailed logging right after the docstring
    lines = content.split('\n')
    modified_lines = []
    in_method = False
    docstring_ended = False
    logging_added = False
    
    for line in lines:
        if method_start in line:
            in_method = True
            docstring_ended = False
            logging_added = False
            modified_lines.append(line)
        elif in_method and '"""' in line and not docstring_ended:
            # End of docstring
            docstring_ended = True
            modified_lines.append(line)
            # Add detailed logging right after docstring
            if not logging_added:
                modified_lines.append('')
                modified_lines.append('        # DETAILED LOGGING - FORCE EXECUTION')
                modified_lines.append('        logging.info("="*80)')
                modified_lines.append('        logging.info("🔧 DETAILED INDICATOR CALCULATION STARTING")')
                modified_lines.append('        logging.info("="*80)')
                modified_lines.append('        logging.info(f"📊 Input Data: {len(df)} bars")')
                modified_lines.append('        logging.info(f"📊 Data Range: {df.index[0]} to {df.index[-1]}")')
                modified_lines.append('        logging.info(f"📊 Latest Close: {df[\"close\"].iloc[-1]:.5f}")')
                modified_lines.append('')
                logging_added = True
        elif in_method and line.strip().startswith('def ') and method_start not in line:
            # Next method started, we're done with this method
            in_method = False
            # Add final logging before return
            if logging_added:
                modified_lines.append('')
                modified_lines.append('        logging.info("="*80)')
                modified_lines.append('        logging.info("✅ DETAILED INDICATOR CALCULATION COMPLETE")')
                modified_lines.append('        logging.info("="*80)')
                modified_lines.append('')
            modified_lines.append(line)
        elif in_method and line.strip().startswith('return df'):
            # Add final logging before return
            if logging_added:
                modified_lines.append('')
                modified_lines.append('        logging.info("="*80)')
                modified_lines.append('        logging.info("✅ DETAILED INDICATOR CALCULATION COMPLETE")')
                modified_lines.append('        logging.info("="*80)')
                modified_lines.append('')
            modified_lines.append(line)
            in_method = False
        else:
            modified_lines.append(line)
    
    if not logging_added:
        print("❌ Could not add detailed logging - method structure not recognized")
        return False
    
    # Write the modified content
    modified_content = '\n'.join(modified_lines)
    
    # Create backup
    import time
    backup_file = f"src/mt5_trading_bot_backup_simple_{int(time.time())}.py"
    print(f"💾 Creating backup: {backup_file}")
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Write modified file
    print("💾 Writing modified bot file...")
    with open(bot_file, 'w', encoding='utf-8') as f:
        f.write(modified_content)
    
    print("✅ Detailed logging added directly to calculate_indicators method!")
    return True

if __name__ == "__main__":
    print("🔧 SIMPLE LOGGING FIX")
    print("=" * 50)
    
    success = add_detailed_logging_to_method()
    
    if success:
        print("\n✅ FIX APPLIED SUCCESSFULLY!")
        print("📝 Detailed logging is now embedded in the calculate_indicators method")
        print("🔄 Restart the bot to see the detailed logging")
    else:
        print("\n❌ FIX FAILED!")
        print("   Please check the file manually")