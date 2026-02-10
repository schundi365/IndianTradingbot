"""
Compare mt5_trading_bot.py and mt5_trading_bot_PROFIT_FIX.py

This script identifies the key differences between the two versions.
"""

import difflib
from pathlib import Path

def compare_files():
    """Compare the two bot files and show differences"""
    
    file1 = Path("src/mt5_trading_bot.py")
    file2 = Path("src/mt5_trading_bot_PROFIT_FIX.py")
    
    print("=" * 80)
    print("COMPARING BOT VERSIONS")
    print("=" * 80)
    print()
    
    # Read files
    with open(file1, 'r', encoding='utf-8') as f:
        lines1 = f.readlines()
    
    with open(file2, 'r', encoding='utf-8') as f:
        lines2 = f.readlines()
    
    print(f"File 1: {file1.name}")
    print(f"  Lines: {len(lines1)}")
    print()
    print(f"File 2: {file2.name}")
    print(f"  Lines: {len(lines2)}")
    print()
    
    # Find differences
    differ = difflib.Differ()
    diff = list(differ.compare(lines1, lines2))
    
    # Count changes
    additions = sum(1 for line in diff if line.startswith('+ '))
    deletions = sum(1 for line in diff if line.startswith('- '))
    
    print(f"Changes:")
    print(f"  Additions: {additions} lines")
    print(f"  Deletions: {deletions} lines")
    print()
    
    # Find significant differences (methods added/removed)
    print("=" * 80)
    print("KEY DIFFERENCES")
    print("=" * 80)
    print()
    
    # Look for method definitions
    methods1 = set()
    methods2 = set()
    
    for line in lines1:
        if line.strip().startswith('def '):
            method_name = line.strip().split('(')[0].replace('def ', '')
            methods1.add(method_name)
    
    for line in lines2:
        if line.strip().startswith('def '):
            method_name = line.strip().split('(')[0].replace('def ', '')
            methods2.add(method_name)
    
    # Methods only in file1
    only_in_1 = methods1 - methods2
    if only_in_1:
        print(f"Methods ONLY in {file1.name}:")
        for method in sorted(only_in_1):
            print(f"  • {method}()")
        print()
    
    # Methods only in file2
    only_in_2 = methods2 - methods1
    if only_in_2:
        print(f"Methods ONLY in {file2.name} (PROFIT_FIX):")
        for method in sorted(only_in_2):
            print(f"  • {method}()")
        print()
    
    # Show first 100 significant differences
    print("=" * 80)
    print("DETAILED DIFFERENCES (First 100 changes)")
    print("=" * 80)
    print()
    
    change_count = 0
    context_lines = []
    in_change = False
    
    for i, line in enumerate(diff):
        if line.startswith('+ ') or line.startswith('- '):
            if not in_change:
                # Show context before change
                if context_lines:
                    print("Context:")
                    for ctx in context_lines[-3:]:
                        print(f"  {ctx.rstrip()}")
                    print()
                in_change = True
            
            # Show the change
            if line.startswith('+ '):
                print(f"+ PROFIT_FIX: {line[2:].rstrip()}")
            else:
                print(f"- CURRENT:    {line[2:].rstrip()}")
            
            change_count += 1
            if change_count >= 100:
                print()
                print("... (truncated, showing first 100 changes)")
                break
        else:
            if in_change:
                print()  # Blank line after change block
                in_change = False
            context_lines.append(line)
    
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    
    if only_in_2:
        print("🔧 PROFIT_FIX adds these methods:")
        for method in sorted(only_in_2):
            print(f"   • {method}()")
        print()
    
    if only_in_1:
        print("⚠️  Current version has these methods not in PROFIT_FIX:")
        for method in sorted(only_in_1):
            print(f"   • {method}()")
        print()
    
    print(f"Total changes: {additions + deletions} lines")
    print()

if __name__ == "__main__":
    compare_files()
