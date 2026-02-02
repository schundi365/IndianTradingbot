#!/usr/bin/env python3
"""Find ADX-related code that's causing the error"""

try:
    with open('src/mt5_trading_bot.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"Total lines in file: {len(lines)}")
    
    # Search for ADX-related code
    adx_lines = []
    for i, line in enumerate(lines):
        if 'adx' in line.lower() or 'plus_dm' in line.lower() or 'minus_dm' in line.lower():
            adx_lines.append((i+1, line.strip()))
    
    if adx_lines:
        print(f"\nFound {len(adx_lines)} lines with ADX-related code:")
        for line_num, line_content in adx_lines:
            print(f"Line {line_num:4d}: {line_content}")
    else:
        print("No ADX-related code found")
        
    # Also search for the specific error pattern from logs
    error_patterns = ['np.where', 'high.*shift', 'low.*shift']
    for pattern in error_patterns:
        print(f"\nSearching for pattern: {pattern}")
        for i, line in enumerate(lines):
            if pattern.replace('.*', '') in line:
                print(f"Line {i+1:4d}: {line.strip()}")
        
except Exception as e:
    print(f"Error reading file: {e}")