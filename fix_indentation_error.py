#!/usr/bin/env python3
"""
Fix Indentation Error in mt5_trading_bot.py

The ADX calculation insertion caused an indentation error.
We need to fix the file structure.
"""

import os
import shutil
from datetime import datetime

def backup_file(filepath):
    """Create backup of file before modification"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{filepath}_backup_indent_fix_{timestamp}"
    shutil.copy2(filepath, backup_path)
    print(f"✅ Backup created: {backup_path}")
    return backup_path

def fix_indentation_error():
    """
    Fix the indentation error caused by ADX insertion
    """
    filepath = "src/mt5_trading_bot.py"
    
    # Create backup
    backup_path = backup_file(filepath)
    
    # Read current file
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"📄 File has {len(lines)} lines")
    
    # Find the problematic area around line 330
    problem_found = False
    for i in range(max(0, 325), min(len(lines), 340)):
        line = lines[i]
        if line.strip().startswith('error = mt5.last_error()') and not line.startswith('        '):
            print(f"🔍 Found indentation issue at line {i+1}: {line.strip()}")
            # Fix the indentation
            lines[i] = '        ' + line.lstrip()
            problem_found = True
        elif line.strip().startswith('error_code = error[0]') and not line.startswith('        '):
            print(f"🔍 Found indentation issue at line {i+1}: {line.strip()}")
            lines[i] = '        ' + line.lstrip()
            problem_found = True
        elif line.strip().startswith('if error_code in') and not line.startswith('        '):
            print(f"🔍 Found indentation issue at line {i+1}: {line.strip()}")
            lines[i] = '        ' + line.lstrip()
            problem_found = True
    
    if not problem_found:
        print("⚠️ Specific indentation issue not found, checking for general issues...")
        
        # Look for lines that should be indented but aren't
        for i, line in enumerate(lines):
            if i > 0:  # Skip first line
                prev_line = lines[i-1].strip()
                current_line = line.strip()
                
                # If previous line ends with : and current line is not indented properly
                if (prev_line.endswith(':') and 
                    current_line and 
                    not current_line.startswith('#') and
                    not line.startswith('    ')):  # Should be indented
                    
                    print(f"🔍 Potential indentation issue at line {i+1}")
                    print(f"   Previous: {prev_line}")
                    print(f"   Current:  {current_line}")
                    
                    # Fix common patterns
                    if any(keyword in current_line for keyword in ['error =', 'if ', 'return ', 'logging.']):
                        lines[i] = '        ' + line.lstrip()
                        print(f"✅ Fixed indentation for line {i+1}")
                        problem_found = True
    
    if problem_found:
        # Write the fixed content
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print(f"✅ Indentation errors fixed in {filepath}")
        return True
    else:
        print("❌ No indentation issues found to fix")
        return False

def restore_from_working_backup():
    """
    Restore from a working backup if available
    """
    print("🔄 Looking for working backup files...")
    
    # Look for recent backups
    backup_files = []
    for filename in os.listdir('.'):
        if filename.startswith('src/mt5_trading_bot.py_backup_') and filename.endswith('.py'):
            backup_files.append(filename)
    
    if not backup_files:
        # Check in src directory
        if os.path.exists('src'):
            for filename in os.listdir('src'):
                if filename.startswith('mt5_trading_bot.py_backup_') and filename.endswith('.py'):
                    backup_files.append(f'src/{filename}')
    
    if backup_files:
        # Sort by modification time (newest first)
        backup_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        
        print(f"📁 Found {len(backup_files)} backup files:")
        for i, backup in enumerate(backup_files[:5]):  # Show first 5
            mtime = datetime.fromtimestamp(os.path.getmtime(backup))
            print(f"   {i+1}. {backup} ({mtime.strftime('%Y-%m-%d %H:%M:%S')})")
        
        # Use the most recent backup that's not the one we just created
        for backup in backup_files:
            if 'indent_fix' not in backup and 'adx_fix' not in backup:
                print(f"🔄 Restoring from: {backup}")
                shutil.copy2(backup, 'src/mt5_trading_bot.py')
                print("✅ Restored from working backup")
                return True
    
    print("❌ No suitable backup found")
    return False

if __name__ == "__main__":
    print("🔧 Fixing Indentation Error...")
    print("="*50)
    
    # Try to fix the indentation error
    if fix_indentation_error():
        print("\n✅ INDENTATION FIX COMPLETE!")
    else:
        print("\n⚠️ Direct fix failed, trying backup restore...")
        if restore_from_working_backup():
            print("✅ BACKUP RESTORE COMPLETE!")
            print("Now we need to re-apply the ADX fix more carefully...")
        else:
            print("❌ BACKUP RESTORE FAILED!")
    
    print("\n🔄 Test the file with: python test_adx_fix.py")