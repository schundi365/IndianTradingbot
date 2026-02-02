#!/usr/bin/env python3
"""
Apply Enhanced Logging Fixes to MT5 Trading Bot
This script converts remaining basic logging calls to enhanced logging
and adds performance timing decorators to key methods.
"""

import re
import os
from pathlib import Path

def apply_enhanced_logging_fixes():
    """Apply enhanced logging fixes to the trading bot"""
    
    bot_file = Path("src/mt5_trading_bot.py")
    if not bot_file.exists():
        print("❌ src/mt5_trading_bot.py not found!")
        return False
    
    print("🔧 Applying enhanced logging fixes...")
    
    # Read the current file
    with open(bot_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Track changes
    changes_made = 0
    
    # 1. Convert basic logging calls to enhanced logging (only within class methods)
    # We need to be careful to only convert logging calls that have access to self.logger
    
    # Find all logging.info/warning/error calls within class methods
    logging_patterns = [
        (r'(\s+)logging\.info\(', r'\1self.logger.info('),
        (r'(\s+)logging\.warning\(', r'\1self.logger.warning('),
        (r'(\s+)logging\.error\(', r'\1self.logger.error('),
        (r'(\s+)logging\.debug\(', r'\1self.logger.debug('),
    ]
    
    # Apply logging conversions only within class methods (indented)
    for pattern, replacement in logging_patterns:
        # Only replace if it's indented (inside a method)
        matches = re.findall(pattern, content)
        if matches:
            # Check if we're inside a class method by looking for self parameter
            lines = content.split('\n')
            new_lines = []
            in_class_method = False
            
            for i, line in enumerate(lines):
                # Check if we're entering a method with self parameter
                if re.match(r'\s+def \w+\(self', line):
                    in_class_method = True
                elif re.match(r'\s+def \w+\(', line) and 'self' not in line:
                    in_class_method = False
                elif re.match(r'^\s*def ', line):  # Top-level function
                    in_class_method = False
                elif re.match(r'^class ', line):  # New class
                    in_class_method = False
                elif re.match(r'^[a-zA-Z]', line):  # Top-level code
                    in_class_method = False
                
                # Apply replacements only if we're in a class method
                if in_class_method:
                    original_line = line
                    for pattern, replacement in logging_patterns:
                        line = re.sub(pattern, replacement, line)
                    if line != original_line:
                        changes_made += 1
                        print(f"   ✅ Converted logging call on line {i+1}")
                
                new_lines.append(line)
            
            content = '\n'.join(new_lines)
    
    # 2. Add performance timing decorators to key methods
    decorators_to_add = [
        (r'(\s+)def connect\(self\):', r'\1@performance_timer("MT5 Connection")\n\1def connect(self):'),
        (r'(\s+)def get_historical_data\(self,', r'\1@performance_timer("Historical Data Fetch")\n\1def get_historical_data(self,'),
        (r'(\s+)def calculate_indicators\(self,', r'\1@performance_timer("Indicator Calculations")\n\1def calculate_indicators(self,'),
    ]
    
    for pattern, replacement in decorators_to_add:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            changes_made += 1
            print(f"   ✅ Added performance timer decorator")
    
    # 3. Fix any remaining import issues
    if 'import platform' not in content:
        # Add platform import after other imports
        content = re.sub(
            r'(import time\n)',
            r'\1import platform\n',
            content
        )
        changes_made += 1
        print("   ✅ Added missing platform import")
    
    # 4. Ensure the old basic logging setup is removed/commented
    if 'logging.basicConfig(' in content:
        content = re.sub(
            r'logging\.basicConfig\(',
            r'# logging.basicConfig(',
            content
        )
        changes_made += 1
        print("   ✅ Commented out old logging setup")
    
    # Write the updated content back
    if changes_made > 0:
        # Create backup
        backup_file = bot_file.with_suffix('.py.backup')
        with open(backup_file, 'w', encoding='utf-8') as f:
            with open(bot_file, 'r', encoding='utf-8') as original:
                f.write(original.read())
        
        # Write updated content
        with open(bot_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Applied {changes_made} enhanced logging fixes")
        print(f"📁 Backup created: {backup_file}")
        return True
    else:
        print("ℹ️  No changes needed - enhanced logging already properly implemented")
        return True

def verify_enhanced_logging():
    """Verify that enhanced logging is working"""
    print("\n🔍 Verifying enhanced logging implementation...")
    
    bot_file = Path("src/mt5_trading_bot.py")
    if not bot_file.exists():
        print("❌ src/mt5_trading_bot.py not found!")
        return False
    
    with open(bot_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for key components
    checks = [
        ("PerformanceFormatter class", "class PerformanceFormatter"),
        ("PerformanceLogger class", "class PerformanceLogger"),
        ("performance_timer decorator", "def performance_timer"),
        ("Enhanced logging setup", "setup_enhanced_logging"),
        ("Logger initialization", "self.logger = PerformanceLogger"),
    ]
    
    all_good = True
    for check_name, pattern in checks:
        if pattern in content:
            print(f"   ✅ {check_name}: Found")
        else:
            print(f"   ❌ {check_name}: Missing")
            all_good = False
    
    # Check for remaining basic logging calls (should be minimal)
    basic_logging_count = len(re.findall(r'\s+logging\.(info|warning|error|debug)\(', content))
    if basic_logging_count > 5:  # Allow a few for imports/setup
        print(f"   ⚠️  Found {basic_logging_count} basic logging calls (should be converted)")
        all_good = False
    else:
        print(f"   ✅ Basic logging calls: {basic_logging_count} (acceptable)")
    
    # Check for performance decorators
    decorator_count = len(re.findall(r'@performance_timer', content))
    if decorator_count >= 3:
        print(f"   ✅ Performance decorators: {decorator_count} found")
    else:
        print(f"   ⚠️  Performance decorators: {decorator_count} found (expected at least 3)")
    
    return all_good

def main():
    print("🚀 Enhanced Logging Implementation Fixer")
    print("=" * 50)
    
    # Apply fixes
    if apply_enhanced_logging_fixes():
        print("\n✅ Enhanced logging fixes applied successfully!")
    else:
        print("\n❌ Failed to apply enhanced logging fixes")
        return
    
    # Verify implementation
    if verify_enhanced_logging():
        print("\n🎉 Enhanced logging implementation verified!")
        print("\n📊 Expected log format:")
        print("2026-02-01 12:34:56.789 - INFO - [src.mt5_trading_bot:mt5_trading_bot.py:123] - [+0.045s] - MT5 initialized successfully")
        print("\n💡 Benefits:")
        print("• Line numbers and file names for easy debugging")
        print("• Performance timing for operation monitoring")
        print("• Package context for better organization")
        print("• Enhanced error tracking with caller context")
    else:
        print("\n⚠️  Enhanced logging implementation has issues")
        print("Please check the output above for details")

if __name__ == "__main__":
    main()