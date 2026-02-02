#!/usr/bin/env python3
"""
Fix ADX Crash - Final Solution

The ADX calculation is causing crashes because it's trying to access
columns that don't exist. We need to disable the ADX calculation
entirely and make the ADX filter safe.
"""

import os
import shutil
from datetime import datetime

def backup_file(filepath):
    """Create backup of file before modification"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{filepath}_backup_adx_crash_fix_{timestamp}"
    shutil.copy2(filepath, backup_path)
    print(f"✅ Backup created: {backup_path}")
    return backup_path

def fix_adx_crash():
    """
    Fix the ADX crash by disabling problematic ADX calculation
    """
    filepath = "src/mt5_trading_bot.py"
    
    # Create backup
    backup_path = backup_file(filepath)
    
    # Read current file
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and disable the problematic ADX calculation section
    adx_calc_start = '''        # Apply ADX trend direction filter (MISSING FROM ORIGINAL - NOW ADDED)
        logging.info("-"*80)
        logging.info("🔍 ADX TREND DIRECTION FILTER:")
        if self.config.get('use_adx', True):
            # Calculate ADX and directional indicators if not already present
            if 'adx' not in df.columns:'''
    
    # Replace with safe ADX handling
    safe_adx_section = '''        # Apply ADX trend direction filter (DISABLED - CAUSING CRASHES)
        logging.info("-"*80)
        logging.info("🔍 ADX TREND DIRECTION FILTER:")
        if False:  # ADX disabled to prevent crashes
            # ADX calculation disabled due to column access issues
            pass'''
    
    if adx_calc_start in content:
        # Find the end of the ADX section
        adx_section_start = content.find(adx_calc_start)
        if adx_section_start != -1:
            # Find the end of the ADX section (look for the next major section)
            adx_section_end = content.find("        # All filters passed", adx_section_start)
            if adx_section_end == -1:
                adx_section_end = content.find("        logging.info(\"-\"*80)", adx_section_start + 100)
            
            if adx_section_end != -1:
                # Replace the entire ADX section
                before_adx = content[:adx_section_start]
                after_adx = content[adx_section_end:]
                
                safe_replacement = '''        # Apply ADX trend direction filter (DISABLED - PREVENTING CRASHES)
        logging.info("-"*80)
        logging.info("🔍 ADX TREND DIRECTION FILTER:")
        logging.info("  ⚠️  ADX filter temporarily disabled to prevent crashes")
        logging.info("  ⚠️  ADX calculation needs to be fixed in calculate_indicators method")
        logging.info("  ✅ Proceeding with other 4 signal methods")
        
'''
                
                content = before_adx + safe_replacement + after_adx
                print("✅ Disabled problematic ADX calculation section")
            else:
                print("❌ Could not find end of ADX section")
                return False
        else:
            print("❌ Could not find ADX section start")
            return False
    else:
        print("⚠️ ADX calculation section not found - may already be fixed")
    
    # Also make sure any remaining ADX column access is safe
    unsafe_patterns = [
        ("if not pd.isna(latest['adx']):", "if 'adx' in df.columns and not pd.isna(latest['adx']):"),
        ("latest['adx']", "latest.get('adx', 0)"),
        ("latest['plus_di']", "latest.get('plus_di', 0)"),
        ("latest['minus_di']", "latest.get('minus_di', 0)")
    ]
    
    for old_pattern, new_pattern in unsafe_patterns:
        if old_pattern in content:
            content = content.replace(old_pattern, new_pattern)
            print(f"✅ Fixed unsafe pattern: {old_pattern}")
    
    # Write the updated content
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ ADX crash fix applied to {filepath}")
    return True

if __name__ == "__main__":
    print("🔧 Fixing ADX Crash Issue...")
    print("="*50)
    
    if fix_adx_crash():
        print("\n✅ ADX CRASH FIX COMPLETE!")
        print("\nChanges made:")
        print("• Disabled problematic ADX calculation")
        print("• Made ADX column access safe")
        print("• Added informative logging about ADX status")
        print("• Preserved all other signal methods")
        
        print("\n📊 Signal methods still active:")
        print("1. ✅ MA Crossover")
        print("2. ✅ Trend Confirmation")
        print("3. ✅ Momentum Signals")
        print("4. ✅ Pullback Signals")
        print("5. ✅ Breakout Signals")
        
        print("\n🔄 The bot can now run without ADX crashes!")
        print("Clear cache and restart: python clear_all_cache.py && python run_bot_auto.py")
        
    else:
        print("\n❌ ADX CRASH FIX FAILED!")
        print("Please check the file manually")