#!/usr/bin/env python3
"""
Fix all self.logger references in web_dashboard.py
"""

def fix_logger_references():
    """Replace all self.logger with logger in web_dashboard.py"""
    
    with open('web_dashboard.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace all self.logger with logger
    updated_content = content.replace('self.logger', 'logger')
    
    # Write back to file
    with open('web_dashboard.py', 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("✅ Fixed all self.logger references in web_dashboard.py")
    print("🔄 All self.logger -> logger replacements completed")

if __name__ == "__main__":
    fix_logger_references()