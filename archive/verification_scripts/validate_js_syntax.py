#!/usr/bin/env python3
"""
Extract and validate JavaScript syntax from dashboard template
"""

import re
import requests

def extract_javascript_from_dashboard():
    """Extract JavaScript code from the dashboard template"""
    try:
        response = requests.get('http://127.0.0.1:5000/', timeout=10)
        if response.status_code != 200:
            print(f"❌ Failed to fetch dashboard: {response.status_code}")
            return None
        
        content = response.text
        
        # Find the script tag content
        script_match = re.search(r'<script>(.*?)</script>', content, re.DOTALL)
        if not script_match:
            print("❌ No script tag found")
            return None
        
        js_code = script_match.group(1)
        return js_code
        
    except Exception as e:
        print(f"❌ Error extracting JavaScript: {e}")
        return None

def validate_javascript_syntax(js_code):
    """Basic JavaScript syntax validation"""
    print("🔍 Analyzing JavaScript syntax...")
    
    lines = js_code.split('\n')
    issues = []
    
    # Count braces
    open_braces = js_code.count('{')
    close_braces = js_code.count('}')
    
    print(f"📊 Brace count: {open_braces} open, {close_braces} close")
    
    if open_braces != close_braces:
        issues.append(f"Brace mismatch: {open_braces} open vs {close_braces} close")
    
    # Count parentheses
    open_parens = js_code.count('(')
    close_parens = js_code.count(')')
    
    print(f"📊 Parentheses count: {open_parens} open, {close_parens} close")
    
    if open_parens != close_parens:
        issues.append(f"Parentheses mismatch: {open_parens} open vs {close_parens} close")
    
    # Look for common syntax errors
    for i, line in enumerate(lines, 1):
        line = line.strip()
        
        # Check for double closing braces
        if '}' in line and line.count('}') > 1:
            # Skip CSS rules and legitimate cases
            if not any(keyword in line for keyword in ['@keyframes', '100%', '0%', '50%']):
                issues.append(f"Line {i}: Multiple closing braces: {line}")
        
        # Check for missing semicolons after statements (basic check)
        if line.endswith('}') and i < len(lines):
            next_line = lines[i].strip() if i < len(lines) else ""
            if next_line and not next_line.startswith(('/', 'function', 'async', 'if', 'else', 'for', 'while', 'try', 'catch', 'finally', '}', ')', ']')):
                # This might indicate a missing semicolon or other issue
                pass
    
    # Look for specific patterns that might cause issues
    problematic_patterns = [
        (r'}\s*}(?!\s*[,;)])', "Double closing brace"),
        (r'function\s+\w+\s*\([^)]*\)\s*{[^}]*$', "Unclosed function"),
        (r'if\s*\([^)]*\)\s*{[^}]*$', "Unclosed if statement"),
    ]
    
    for pattern, description in problematic_patterns:
        matches = re.finditer(pattern, js_code, re.MULTILINE)
        for match in matches:
            line_num = js_code[:match.start()].count('\n') + 1
            issues.append(f"Line {line_num}: {description}")
    
    return issues

def main():
    print("🚀 JavaScript Syntax Validation")
    print("="*50)
    
    js_code = extract_javascript_from_dashboard()
    if not js_code:
        return
    
    print(f"✅ Extracted {len(js_code)} characters of JavaScript")
    
    issues = validate_javascript_syntax(js_code)
    
    print("\n" + "="*50)
    if issues:
        print("❌ SYNTAX ISSUES FOUND:")
        for issue in issues:
            print(f"  • {issue}")
    else:
        print("✅ NO OBVIOUS SYNTAX ISSUES DETECTED")
    
    print("\n💡 If issues persist, try:")
    print("  1. Check browser console for specific error messages")
    print("  2. Use browser developer tools to debug JavaScript")
    print("  3. Test individual functions in browser console")
    print("="*50)

if __name__ == "__main__":
    main()