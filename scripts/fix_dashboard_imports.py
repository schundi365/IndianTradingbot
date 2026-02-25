"""
Fix all indian_dashboard imports to use relative imports
"""

import os
import re
from pathlib import Path

def fix_imports_in_file(filepath):
    """Fix imports in a single file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Fix imports
    content = re.sub(r'from indian_dashboard\.validators import', 'from validators import', content)
    content = re.sub(r'from indian_dashboard\.rate_limiter import', 'from rate_limiter import', content)
    content = re.sub(r'from indian_dashboard\.error_handler import', 'from error_handler import', content)
    content = re.sub(r'from indian_dashboard\.config import', 'from config import', content)
    content = re.sub(r'from indian_dashboard\.session_manager import', 'from session_manager import', content)
    
    # Only write if changed
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    """Fix all files in indian_dashboard/api"""
    api_dir = Path('indian_dashboard/api')
    
    if not api_dir.exists():
        print(f"Error: {api_dir} not found")
        return
    
    fixed_count = 0
    for py_file in api_dir.glob('*.py'):
        if fix_imports_in_file(py_file):
            print(f"Fixed: {py_file}")
            fixed_count += 1
    
    print(f"\nFixed {fixed_count} files")

if __name__ == '__main__':
    main()
