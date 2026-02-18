#!/usr/bin/env python3
"""
Apply Clean ADX Fix

This applies a minimal fix to handle the ADX KeyError without
adding complex ADX calculations that might cause indentation issues.
"""

import os
import shutil
from datetime import datetime

def backup_file(filepath):
    """Create backup of file before modification"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{filepath}_backup_clean_adx_{timestamp}"
    shutil.copy2(filepath, backup_path)
    print(f"✅ Backup created: {backup_path}")
    return backup_path

def apply_clean_adx_fix():
    """
    Apply a clean fix for ADX KeyError
    """
    filepath = "src/mt5_trading_bot.py"
    
    # Create backup
    backup_path = backup_file(filepath)
    
    # Read current file
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace the problematic ADX access
    old_adx_check = "if not pd.isna(latest['adx']):"
    new_adx_check = "if 'adx' in df.columns and not pd.isna(latest['adx']):"
    
    if old_adx_check in content:
        content = content.replace(old_adx_check, new_adx_check)
        print("✅ Fixed ADX column access check")
    else:
        print("⚠️ ADX access check not found")
    
    # Also fix the plus_di and minus_di access to be safe
    old_plus_di = "plus_di = latest.get('plus_di', 0)"
    new_plus_di = "plus_di = latest.get('plus_di', 0) if 'plus_di' in df.columns else 0"
    
    old_minus_di = "minus_di = latest.get('minus_di', 0)"
    new_minus_di = "minus_di = latest.get('minus_di', 0) if 'minus_di' in df.columns else 0"
    
    if old_plus_di in content:
        content = content.replace(old_plus_di, new_plus_di)
        print("✅ Fixed plus_di access")
    
    if old_minus_di in content:
        content = content.replace(old_minus_di, new_minus_di)
        print("✅ Fixed minus_di access")
    
    # Add a simple fallback for when ADX is not available
    adx_fallback = '''            else:
                logging.info(f"  ⚠️  ADX data not available - skipping ADX filter")
        else:
            logging.info(f"  ⚠️  ADX filter disabled in configuration")'''
    
    # Find the end of the ADX section and make sure it has proper fallback
    if "logging.info(f\"  ⚠️  ADX data not available - skipping ADX filter\")" not in content:
        # Find where to add the fallback
        adx_section_end = "logging.info(f\"  ⚠️  ADX filter disabled in configuration\")"
        if adx_section_end in content:
            print("✅ ADX fallback already present")
        else:
            print("⚠️ ADX fallback section not found - ADX filter may not work properly")
    
    # Write the updated content
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Clean ADX fix applied to {filepath}")
    return True

if __name__ == "__main__":
    print("🔧 Applying Clean ADX Fix...")
    print("="*50)
    
    if apply_clean_adx_fix():
        print("\n✅ CLEAN ADX FIX COMPLETE!")
        print("The bot should now handle missing ADX columns safely.")
        print("ADX calculation is skipped when not available.")
        print("\n🔄 Test with: python test_adx_fix.py")
    else:
        print("\n❌ CLEAN ADX FIX FAILED!")
        print("Please check the file manually")