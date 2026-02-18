#!/usr/bin/env python3
"""Find line 907 in mt5_trading_bot.py to locate ADX error"""

try:
    with open('src/mt5_trading_bot.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"Total lines in file: {len(lines)}")
    
    if len(lines) >= 907:
        print(f"\nLine 907: {lines[906].strip()}")
        
        # Show context around line 907
        start = max(0, 906 - 5)
        end = min(len(lines), 906 + 6)
        
        print(f"\nContext around line 907 (lines {start+1}-{end}):")
        for i in range(start, end):
            marker = ">>> " if i == 906 else "    "
            print(f"{marker}{i+1:4d}: {lines[i].rstrip()}")
    else:
        print(f"File only has {len(lines)} lines, line 907 doesn't exist")
        
except Exception as e:
    print(f"Error reading file: {e}")