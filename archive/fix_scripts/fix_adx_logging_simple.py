#!/usr/bin/env python3
"""
Simple targeted fix for ADX and logging issues
"""

import os
import re
import shutil
from datetime import datetime

def create_backup():
    """Create backup of current trading bot file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"src/mt5_trading_bot.py_backup_simple_fix_{timestamp}"
    shutil.copy2("src/mt5_trading_bot.py", backup_path)
    print(f"✅ Backup created: {backup_path}")
    return backup_path

def fix_logging_calls():
    """Fix bare logging calls in the trading bot"""
    
    with open("src/mt5_trading_bot.py", "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    changes_made = 0
    
    for i, line in enumerate(lines):
        original_line = line
        
        # Fix bare logging calls - only in method context (indented)
        if re.match(r'\s+', line) and 'logging.' in line:
            # Replace logging.info with self.logger.info etc.
            line = re.sub(r'logging\.info\(', 'self.logger.info(', line)
            line = re.sub(r'logging\.warning\(', 'self.logger.warning(', line)
            line = re.sub(r'logging\.error\(', 'self.logger.error(', line)
            line = re.sub(r'logging\.debug\(', 'self.logger.debug(', line)
            
            if line != original_line:
                lines[i] = line
                changes_made += 1
                print(f"  Fixed line {i+1}: logging -> self.logger")
    
    # Write back the fixed content
    with open("src/mt5_trading_bot.py", "w", encoding="utf-8") as f:
        f.writelines(lines)
    
    return changes_made

def fix_adx_access():
    """Fix ADX access to prevent KeyError"""
    
    with open("src/mt5_trading_bot.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Find the problematic ADX access line and replace it
    problematic_pattern = r"if hasattr\(latest, 'index'\) and 'adx' in getattr\(latest, 'index', \[\]\) and not pd\.isna\(latest\.get\('adx', 0\)\):"
    
    safe_replacement = """try:
                    # Safe ADX access with comprehensive error handling
                    adx = 0
                    if 'adx' in df.columns and len(df) > 0:
                        try:
                            adx_value = latest.get('adx', 0) if hasattr(latest, 'get') else df['adx'].iloc[-1]
                            if pd.notna(adx_value):
                                adx = float(adx_value)
                        except (KeyError, IndexError, TypeError, ValueError):
                            adx = 0
                except Exception:
                    adx = 0
                
                if adx > 0:"""
    
    if re.search(problematic_pattern, content):
        content = re.sub(problematic_pattern, safe_replacement, content)
        print("  ✅ Fixed ADX access pattern")
        
        # Also need to remove the old exception handling that follows
        content = re.sub(r'\s+except \(KeyError, AttributeError, IndexError\):\s+adx = 0\s+else:\s+adx = 0\s+except \(KeyError, AttributeError\):\s+adx = 0', '', content, flags=re.MULTILINE)
        
        with open("src/mt5_trading_bot.py", "w", encoding="utf-8") as f:
            f.write(content)
        
        return True
    
    return False

def main():
    """Main execution function"""
    print("🔧 SIMPLE FIX: Addressing ADX KeyError and logger issues")
    print("=" * 60)
    
    # Create backup
    backup_path = create_backup()
    
    try:
        # Fix logging calls
        print("\n📝 Fixing bare logging calls...")
        logging_changes = fix_logging_calls()
        print(f"  ✅ Fixed {logging_changes} logging calls")
        
        # Fix ADX access
        print("\n🔍 Fixing ADX access...")
        adx_fixed = fix_adx_access()
        if adx_fixed:
            print("  ✅ Fixed ADX access pattern")
        else:
            print("  ⚠️  ADX pattern not found or already fixed")
        
        print("\n📊 Summary:")
        print(f"  - Backup: {backup_path}")
        print(f"  - Logging fixes: {logging_changes}")
        print(f"  - ADX access fixed: {adx_fixed}")
        
        print("\n🔄 NEXT STEPS:")
        print("  1. Restart the bot to load fixed code")
        print("  2. Monitor logs for remaining errors")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ SIMPLE FIX COMPLETED!")
    else:
        print("\n❌ FIX FAILED!")