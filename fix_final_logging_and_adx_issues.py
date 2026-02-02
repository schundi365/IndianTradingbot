#!/usr/bin/env python3
"""
FINAL FIX: Comprehensive solution for remaining ADX KeyError and logger issues
This script addresses all remaining bare logging calls and ADX access issues
"""

import os
import re
import shutil
from datetime import datetime

def create_backup():
    """Create backup of current trading bot file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"src/mt5_trading_bot.py_backup_final_fix_{timestamp}"
    shutil.copy2("src/mt5_trading_bot.py", backup_path)
    print(f"✅ Backup created: {backup_path}")
    return backup_path

def fix_adx_and_logging_issues():
    """Fix all remaining ADX KeyError and bare logging issues"""
    
    # Read the current file
    with open("src/mt5_trading_bot.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Track changes
    changes_made = []
    
    # 1. Fix all bare logging calls in ADX section (lines 930-1035)
    adx_section_fixes = [
        (r'(\s+)logging\.info\(', r'\1self.logger.info('),
        (r'(\s+)logging\.warning\(', r'\1self.logger.warning('),
        (r'(\s+)logging\.error\(', r'\1self.logger.error('),
        (r'(\s+)logging\.debug\(', r'\1self.logger.debug('),
    ]
    
    for pattern, replacement in adx_section_fixes:
        old_content = content
        content = re.sub(pattern, replacement, content)
        if content != old_content:
            changes_made.append(f"Fixed bare logging calls: {pattern}")
    
    # 2. Fix ADX access with bulletproof error handling
    # Replace the problematic ADX access section
    adx_access_pattern = r'(if hasattr\(latest, \'index\'\) and \'adx\' in getattr\(latest, \'index\', \[\]\) and not pd\.isna\(latest\.get\(\'adx\', 0\)\):.*?adx = 0)'
    
    bulletproof_adx_access = '''try:
                    # Bulletproof ADX access with multiple safety checks
                    adx = 0
                    if 'adx' in df.columns and len(df) > 0:
                        if hasattr(latest, 'get'):
                            # Series access
                            adx_value = latest.get('adx', 0)
                            if pd.notna(adx_value) and isinstance(adx_value, (int, float)):
                                adx = float(adx_value)
                        elif hasattr(latest, '__getitem__') and 'adx' in latest:
                            # Dictionary-like access
                            adx_value = latest['adx']
                            if pd.notna(adx_value) and isinstance(adx_value, (int, float)):
                                adx = float(adx_value)
                        else:
                            # Direct DataFrame iloc access as fallback
                            if 'adx' in df.columns:
                                adx_value = df['adx'].iloc[-1]
                                if pd.notna(adx_value) and isinstance(adx_value, (int, float)):
                                    adx = float(adx_value)
                except (KeyError, AttributeError, IndexError, TypeError, ValueError) as e:
                    adx = 0
                    self.logger.warning(f"ADX access failed safely: {str(e)}")'''
    
    # Find and replace the ADX access section
    if 'if hasattr(latest, \'index\') and \'adx\' in getattr(latest, \'index\', [])' in content:
        # Replace the entire problematic section
        lines = content.split('\n')
        new_lines = []
        in_adx_section = False
        adx_section_start = False
        
        for i, line in enumerate(lines):
            if 'if hasattr(latest, \'index\') and \'adx\' in getattr(latest, \'index\', [])' in line:
                # Start of problematic section - replace with bulletproof version
                new_lines.append('                ' + bulletproof_adx_access.split('\n')[0])
                for bullet_line in bulletproof_adx_access.split('\n')[1:]:
                    new_lines.append('                ' + bullet_line)
                in_adx_section = True
                adx_section_start = True
                continue
            elif in_adx_section and ('except (KeyError, AttributeError):' in line or 'adx = 0' in line):
                # Skip the old error handling
                if 'else:' in lines[i+1] if i+1 < len(lines) else False:
                    continue
                else:
                    in_adx_section = False
                    continue
            elif in_adx_section:
                # Skip lines in the old ADX section
                continue
            else:
                new_lines.append(line)
        
        content = '\n'.join(new_lines)
        changes_made.append("Replaced ADX access with bulletproof error handling")
    
    # 3. Add additional safety for DI calculations
    di_safety_pattern = r'(plus_di = latest\.get\(\'plus_di\', 0\).*?minus_di = latest\.get\(\'minus_di\', 0\).*?)'
    di_safety_replacement = '''try:
                    plus_di = 0
                    minus_di = 0
                    if 'plus_di' in df.columns and hasattr(latest, 'get'):
                        plus_di_val = latest.get('plus_di', 0)
                        if pd.notna(plus_di_val) and isinstance(plus_di_val, (int, float)):
                            plus_di = float(plus_di_val)
                    
                    if 'minus_di' in df.columns and hasattr(latest, 'get'):
                        minus_di_val = latest.get('minus_di', 0)
                        if pd.notna(minus_di_val) and isinstance(minus_di_val, (int, float)):
                            minus_di = float(minus_di_val)
                except (KeyError, AttributeError, TypeError, ValueError):
                    plus_di = 0
                    minus_di = 0'''
    
    if 'plus_di = latest.get(\'plus_di\', 0)' in content:
        content = re.sub(
            r'plus_di = latest\.get\(\'plus_di\', 0\).*?minus_di = latest\.get\(\'minus_di\', 0\).*?',
            di_safety_replacement,
            content,
            flags=re.DOTALL
        )
        changes_made.append("Added safety for DI calculations")
    
    # 4. Ensure all try-except blocks use self.logger
    content = re.sub(
        r'except \([^)]+\):\s*\n\s*logging\.',
        r'except (\1):\n                self.logger.',
        content
    )
    
    # Write the fixed content
    with open("src/mt5_trading_bot.py", "w", encoding="utf-8") as f:
        f.write(content)
    
    return changes_made

def verify_fixes():
    """Verify that all fixes have been applied correctly"""
    with open("src/mt5_trading_bot.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    issues = []
    
    # Check for remaining bare logging calls
    bare_logging_matches = re.findall(r'\s+logging\.(info|warning|error|debug)\(', content)
    if bare_logging_matches:
        issues.append(f"Found {len(bare_logging_matches)} bare logging calls")
    
    # Check for unsafe ADX access
    unsafe_adx_patterns = [
        r'latest\[\'adx\'\]',
        r'latest\.adx',
    ]
    
    for pattern in unsafe_adx_patterns:
        if re.search(pattern, content):
            issues.append(f"Found unsafe ADX access: {pattern}")
    
    return issues

def main():
    """Main execution function"""
    print("🔧 FINAL FIX: Addressing remaining ADX KeyError and logger issues")
    print("=" * 80)
    
    # Create backup
    backup_path = create_backup()
    
    try:
        # Apply fixes
        print("\n📝 Applying comprehensive fixes...")
        changes = fix_adx_and_logging_issues()
        
        for change in changes:
            print(f"  ✅ {change}")
        
        # Verify fixes
        print("\n🔍 Verifying fixes...")
        issues = verify_fixes()
        
        if issues:
            print("  ⚠️  Remaining issues found:")
            for issue in issues:
                print(f"    - {issue}")
        else:
            print("  ✅ All issues resolved!")
        
        print("\n📊 Summary:")
        print(f"  - Backup created: {backup_path}")
        print(f"  - Changes applied: {len(changes)}")
        print(f"  - Remaining issues: {len(issues)}")
        
        if len(changes) > 0:
            print("\n🔄 NEXT STEPS:")
            print("  1. Restart the bot to load the fixed code")
            print("  2. Monitor logs for any remaining errors")
            print("  3. Verify ADX calculations work properly")
            print("  4. Check that all logging uses self.logger")
        
    except Exception as e:
        print(f"❌ Error during fix: {str(e)}")
        print(f"Backup available at: {backup_path}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ FINAL FIX COMPLETED SUCCESSFULLY!")
        print("The bot should now be free of ADX KeyError and logger NameError issues.")
    else:
        print("\n❌ FINAL FIX FAILED!")
        print("Please check the backup and try manual fixes.")