#!/usr/bin/env python3
"""
Fix extra closing braces in the dashboard template
"""

import re

def fix_extra_braces():
    """Remove extra closing braces from the dashboard template"""
    
    # Read the current template
    with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔧 Fixing extra closing braces...")
    
    # Split into lines for processing
    lines = content.split('\n')
    fixed_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        fixed_lines.append(line)
        
        # Check if this line ends a function and the next line is just a closing brace
        if (line.strip() == '}' and 
            i + 1 < len(lines) and 
            lines[i + 1].strip() == '}' and
            i + 2 < len(lines) and
            lines[i + 2].strip() == ''):
            
            # This looks like an extra closing brace pattern
            # Skip the extra closing brace
            print(f"  Removing extra brace at line {i + 2}")
            i += 2  # Skip the extra brace and empty line
        else:
            i += 1
    
    # Join the fixed lines
    fixed_content = '\n'.join(fixed_lines)
    
    # Write the fixed template
    with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print("✅ Fixed extra closing braces")
    
    # Verify the fix
    open_braces = fixed_content.count('{')
    close_braces = fixed_content.count('}')
    
    print(f"📊 After fix: {open_braces} open braces, {close_braces} close braces")
    
    if open_braces == close_braces:
        print("✅ Braces are now balanced!")
    else:
        print(f"⚠️  Braces still unbalanced: {open_braces - close_braces} difference")

if __name__ == "__main__":
    print("🚀 Fixing Dashboard JavaScript Syntax")
    print("="*50)
    
    fix_extra_braces()
    
    print("="*50)
    print("🎯 Fix complete! Restart the dashboard to test.")