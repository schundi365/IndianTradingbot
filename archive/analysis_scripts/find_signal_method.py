#!/usr/bin/env python3
"""Find the check_entry_signal method and show its content"""

with open('src/mt5_trading_bot.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the method
method_start = None
for i, line in enumerate(lines):
    if 'def check_entry_signal(self, df):' in line:
        method_start = i
        break

if method_start is not None:
    print(f"Found check_entry_signal method at line {method_start + 1}")
    
    # Find the end of the method (next def or class)
    method_end = len(lines)
    for i in range(method_start + 1, len(lines)):
        if lines[i].strip().startswith('def ') and not lines[i].strip().startswith('def '):
            method_end = i
            break
    
    print(f"Method spans lines {method_start + 1} to {method_end}")
    print("\nMethod content:")
    print("=" * 80)
    
    for i in range(method_start, min(method_start + 100, method_end)):
        print(f"{i+1:4d}: {lines[i].rstrip()}")
    
    if method_end - method_start > 100:
        print(f"\n... (showing first 100 lines, method continues to line {method_end})")
else:
    print("check_entry_signal method not found!")