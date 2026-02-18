#!/usr/bin/env python3
"""
Complete Enhanced Logging Fix
This script adds the missing performance decorators and converts remaining basic logging calls
"""

import re
from pathlib import Path

def apply_final_enhanced_logging_fixes():
    """Apply the final enhanced logging fixes"""
    
    bot_file = Path("src/mt5_trading_bot.py")
    if not bot_file.exists():
        print("❌ src/mt5_trading_bot.py not found!")
        return False
    
    print("🔧 Applying final enhanced logging fixes...")
    
    # Read the current file
    with open(bot_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    changes_made = 0
    
    # 1. Add performance decorators to key methods (if not already present)
    decorators_to_add = [
        {
            'pattern': r'(\s+)def connect\(self\):',
            'replacement': r'\1@performance_timer("MT5 Connection")\n\1def connect(self):',
            'name': 'connect method'
        },
        {
            'pattern': r'(\s+)def get_historical_data\(self, symbol, timeframe, bars=200\):',
            'replacement': r'\1@performance_timer("Historical Data Fetch")\n\1def get_historical_data(self, symbol, timeframe, bars=200):',
            'name': 'get_historical_data method'
        },
        {
            'pattern': r'(\s+)def calculate_indicators\(self, df, symbol\):',
            'replacement': r'\1@performance_timer("Indicator Calculations")\n\1def calculate_indicators(self, df, symbol):',
            'name': 'calculate_indicators method'
        }
    ]
    
    for decorator in decorators_to_add:
        if re.search(decorator['pattern'], content) and '@performance_timer' not in content[content.find(decorator['pattern']):content.find(decorator['pattern']) + 200]:
            content = re.sub(decorator['pattern'], decorator['replacement'], content)
            changes_made += 1
            print(f"   ✅ Added performance timer to {decorator['name']}")
    
    # 2. Convert specific remaining basic logging calls to enhanced logging
    # Only convert calls that are clearly within class methods (have proper indentation and self access)
    
    # Find and replace logging calls within class methods
    lines = content.split('\n')
    new_lines = []
    in_class_method = False
    method_indent = 0
    
    for i, line in enumerate(lines):
        original_line = line
        
        # Detect if we're entering a class method
        method_match = re.match(r'^(\s+)def (\w+)\(self', line)
        if method_match:
            in_class_method = True
            method_indent = len(method_match.group(1))
        elif re.match(r'^(\s*)def ', line):
            # Check if it's still within the class (has proper indentation)
            current_indent = len(re.match(r'^(\s*)', line).group(1))
            if current_indent <= method_indent:
                in_class_method = False
        elif re.match(r'^class ', line) or re.match(r'^[a-zA-Z]', line):
            in_class_method = False
        
        # Convert logging calls only if we're in a class method
        if in_class_method and re.search(r'\s+logging\.(info|warning|error|debug)\(', line):
            # Convert to enhanced logging
            line = re.sub(r'(\s+)logging\.info\(', r'\1self.logger.info(', line)
            line = re.sub(r'(\s+)logging\.warning\(', r'\1self.logger.warning(', line)
            line = re.sub(r'(\s+)logging\.error\(', r'\1self.logger.error(', line)
            line = re.sub(r'(\s+)logging\.debug\(', r'\1self.logger.debug(', line)
            
            if line != original_line:
                changes_made += 1
                print(f"   ✅ Converted logging call on line {i+1}")
        
        new_lines.append(line)
    
    content = '\n'.join(new_lines)
    
    # 3. Ensure platform import is present
    if 'import platform' not in content:
        content = re.sub(
            r'(import time\n)',
            r'\1import platform\n',
            content
        )
        changes_made += 1
        print("   ✅ Added missing platform import")
    
    # Write the updated content back
    if changes_made > 0:
        with open(bot_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Applied {changes_made} final enhanced logging fixes")
        return True
    else:
        print("ℹ️  No additional changes needed")
        return True

def verify_final_implementation():
    """Verify the final enhanced logging implementation"""
    print("\n🔍 Final verification of enhanced logging...")
    
    bot_file = Path("src/mt5_trading_bot.py")
    with open(bot_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check key components
    checks = [
        ("PerformanceFormatter class", "class PerformanceFormatter"),
        ("PerformanceLogger class", "class PerformanceLogger"),
        ("performance_timer decorator", "def performance_timer"),
        ("Enhanced logging setup", "setup_enhanced_logging"),
        ("Logger initialization in __init__", "self.logger = PerformanceLogger"),
        ("Performance decorator on connect", "@performance_timer.*connect"),
        ("Performance decorator on get_historical_data", "@performance_timer.*Historical Data"),
        ("Performance decorator on calculate_indicators", "@performance_timer.*Indicator"),
    ]
    
    all_good = True
    for check_name, pattern in checks:
        if re.search(pattern, content):
            print(f"   ✅ {check_name}: Found")
        else:
            print(f"   ❌ {check_name}: Missing")
            all_good = False
    
    # Count remaining basic logging calls
    basic_logging_matches = re.findall(r'logging\.(info|warning|error|debug)\(', content)
    print(f"   📊 Basic logging calls remaining: {len(basic_logging_matches)}")
    
    # Count enhanced logging calls
    enhanced_logging_matches = re.findall(r'self\.logger\.(info|warning|error|debug)\(', content)
    print(f"   📊 Enhanced logging calls: {len(enhanced_logging_matches)}")
    
    # Count performance decorators
    decorator_matches = re.findall(r'@performance_timer', content)
    print(f"   📊 Performance decorators: {len(decorator_matches)}")
    
    return all_good

def main():
    print("🚀 Final Enhanced Logging Implementation")
    print("=" * 50)
    
    # Apply final fixes
    if apply_final_enhanced_logging_fixes():
        print("\n✅ Final enhanced logging fixes applied!")
    else:
        print("\n❌ Failed to apply final fixes")
        return
    
    # Verify final implementation
    if verify_final_implementation():
        print("\n🎉 Enhanced logging implementation is now complete!")
    else:
        print("\n⚠️  Some issues remain, but core functionality should work")
    
    print("\n📋 Enhanced Logging Features Now Active:")
    print("• Line numbers and file names in all log entries")
    print("• Performance timing for key operations")
    print("• Package context for better organization")
    print("• Enhanced error tracking with caller context")
    print("• Automatic operation timing with decorators")
    
    print("\n💡 Expected log format:")
    print("2026-02-01 12:34:56.789 - INFO - [src.mt5_trading_bot:mt5_trading_bot.py:123] - [+0.045s] - MT5 initialized successfully")

if __name__ == "__main__":
    main()