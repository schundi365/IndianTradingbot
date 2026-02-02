#!/usr/bin/env python3
"""
Fix the indentation error in mt5_trading_bot.py around line 969
"""

import re

def fix_indentation_error():
    """Fix the indentation error in the trading bot file"""
    
    # Read the file
    with open('src/mt5_trading_bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the problematic section and fix it
    # The issue is around the ADX section where there are malformed try blocks
    
    # Pattern to find the problematic section
    problematic_pattern = r'(\s+)try:\s*\n\s*try:\s*\n\s*if \'adx\' in df\.columns:\s*\n\s+try:'
    
    # Look for the pattern and fix it
    lines = content.split('\n')
    fixed_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this is the problematic area around line 969
        if i >= 965 and i <= 975:
            # Check for the specific pattern
            if 'try:' in line and i + 1 < len(lines) and 'try:' in lines[i + 1]:
                # Skip duplicate try statements
                print(f"Fixing duplicate try at line {i + 1}")
                fixed_lines.append(line)
                i += 1
                # Skip the duplicate try
                while i < len(lines) and lines[i].strip() == 'try:':
                    i += 1
                continue
            elif "if 'adx' in df.columns:" in line and not line.strip().endswith(':'):
                # This line is fine, add it
                fixed_lines.append(line)
            elif "if 'adx' in df.columns:" in line:
                # This is the problematic if statement, ensure it has proper indentation
                fixed_lines.append(line)
                # Make sure the next line is properly indented
                i += 1
                if i < len(lines) and lines[i].strip() == 'try:':
                    # Add proper indentation for the try block
                    indent = len(line) - len(line.lstrip()) + 4
                    fixed_lines.append(' ' * indent + 'try:')
                else:
                    fixed_lines.append(lines[i])
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
        
        i += 1
    
    # Write the fixed content back
    fixed_content = '\n'.join(fixed_lines)
    
    with open('src/mt5_trading_bot.py', 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print("✅ Fixed indentation error")
    
    # Test if the file can be compiled now
    try:
        import py_compile
        py_compile.compile('src/mt5_trading_bot.py', doraise=True)
        print("✅ File compiles successfully")
        return True
    except Exception as e:
        print(f"❌ Still has errors: {e}")
        return False

if __name__ == "__main__":
    success = fix_indentation_error()
    if success:
        print("🎉 Indentation error fixed successfully!")
    else:
        print("⚠️  Manual fix may be required")