#!/usr/bin/env python3
"""
Analyze the signal generation logic to find issues
"""

import re

# Read the trading bot file
with open('src/mt5_trading_bot.py', 'r', encoding='utf-8') as f:
    content = f.read()

print("🔍 ANALYZING SIGNAL GENERATION LOGIC")
print("=" * 50)

# Find the check_entry_signal method
method_start = content.find('def check_entry_signal(self, df):')
if method_start == -1:
    print("❌ check_entry_signal method not found!")
    exit(1)

# Find the end of the method (next def or class)
method_end = content.find('\n    def ', method_start + 1)
if method_end == -1:
    method_end = content.find('\nclass ', method_start + 1)
if method_end == -1:
    method_end = len(content)

method_content = content[method_start:method_end]

print(f"✅ Found check_entry_signal method ({len(method_content)} characters)")
print()

# Analyze signal assignments
signal_assignments = re.findall(r'signal\s*=\s*([01-])', method_content)
print(f"📊 Signal assignments found: {signal_assignments}")

# Look for crossover detection
crossover_patterns = [
    r'BULLISH CROSSOVER DETECTED',
    r'BEARISH CROSSOVER DETECTED',
    r'ma_cross.*==.*1',
    r'ma_cross.*==.*-1'
]

print("\n🔍 Crossover detection patterns:")
for pattern in crossover_patterns:
    matches = re.findall(pattern, method_content, re.IGNORECASE)
    if matches:
        print(f"  ✅ Found: {pattern} -> {matches}")
    else:
        print(f"  ❌ Missing: {pattern}")

# Look for return statements
returns = re.findall(r'return\s+([^#\n]+)', method_content)
print(f"\n📤 Return statements: {returns}")

# Look for signal filtering logic
filters = [
    'RSI',
    'MACD',
    'ADX',
    'volume'
]

print(f"\n🔧 Signal filters:")
for filter_name in filters:
    if filter_name.lower() in method_content.lower():
        print(f"  ✅ {filter_name} filter present")
    else:
        print(f"  ❌ {filter_name} filter missing")

# Check for common issues
issues = []

if 'signal = 0' not in method_content:
    issues.append("Signal not initialized to 0")

if 'return signal' not in method_content:
    issues.append("Method doesn't return signal")

if method_content.count('signal = 1') == 0:
    issues.append("No BUY signal generation")

if method_content.count('signal = -1') == 0:
    issues.append("No SELL signal generation")

print(f"\n🚨 POTENTIAL ISSUES:")
if issues:
    for issue in issues:
        print(f"  ❌ {issue}")
else:
    print("  ✅ No obvious issues found")

# Show the method structure
lines = method_content.split('\n')
print(f"\n📋 METHOD STRUCTURE ({len(lines)} lines):")
for i, line in enumerate(lines[:20]):  # Show first 20 lines
    if 'signal' in line.lower() or 'return' in line.lower():
        print(f"  {i+1:3d}: {line.strip()}")

if len(lines) > 20:
    print(f"  ... ({len(lines) - 20} more lines)")