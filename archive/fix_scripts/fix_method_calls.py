#!/usr/bin/env python3
"""
Fix the incorrect method calls in mt5_trading_bot.py
"""

import re

# Read the file
with open('src/mt5_trading_bot.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace all occurrences of calculate_indicators_with_logging with calculate_indicators
content = content.replace('calculate_indicators_with_logging', 'calculate_indicators')

# Write the file back
with open('src/mt5_trading_bot.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed all calculate_indicators_with_logging calls")
print("🔍 Checking for remaining occurrences...")

# Check if any remain
if 'calculate_indicators_with_logging' in content:
    print("❌ Some occurrences still remain")
else:
    print("✅ All occurrences fixed successfully")