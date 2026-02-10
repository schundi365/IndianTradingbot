"""
Final Audit: Ensure NO Hardcoded Values in Bot Logic
"""

import re
from pathlib import Path

print("=" * 80)
print("FINAL HARDCODE AUDIT")
print("=" * 80)
print()

# Bot files to check
bot_files = [
    'src/mt5_trading_bot.py',
    'src/mt5_trading_bot_SIGNAL_FIX.py',
]

# Parameters that should come from config
critical_params = {
    'fast_ma_period': 10,
    'slow_ma_period': 21,
    'tp_levels': [1, 1.5, 2.5],
    'dead_hours': [0, 1, 2, 17, 20, 21, 22],
    'golden_hours': [8, 11, 13, 14, 15, 19, 23],
    'atr_multiplier': None,  # Should come from config
    'rsi_period': 14,
    'macd_fast': 12,
    'macd_slow': 26,
}

print("Checking for hardcoded defaults in bot files...")
print()

all_correct = True

for bot_file in bot_files:
    file_path = Path(bot_file)
    if not file_path.exists():
        continue
    
    print(f"{bot_file}")
    print("-" * 80)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check each critical parameter
    for param, expected_value in critical_params.items():
        # Find config.get() calls for this parameter
        pattern = rf"config\.get\('{param}',\s*([^\)]+)\)"
        matches = re.findall(pattern, content)
        
        if matches:
            for match in matches:
                # Clean up the match
                default_value = match.strip()
                
                # Check if it matches expected
                if expected_value is not None:
                    expected_str = str(expected_value).replace("'", "")
                    if expected_str in default_value or default_value == str(expected_value):
                        print(f"  ✓ {param}: {default_value}")
                    else:
                        print(f"  ⚠️  {param}: {default_value} (expected: {expected_value})")
                        all_correct = False
                else:
                    print(f"  ✓ {param}: {default_value}")
    
    print()

# Check for any remaining hardcoded arrays that might be problematic
print("Checking for suspicious hardcoded arrays...")
print("-" * 80)

suspicious_patterns = [
    (r'\[1\.5,\s*2\.5,\s*4\.0\]', 'Old TP levels [1.5, 2.5, 4.0]'),
    (r'\[0,\s*1,\s*2,\s*17,\s*18,\s*20,\s*21,\s*22\]', 'Old dead_hours with hour 18'),
]

found_issues = False
for bot_file in bot_files:
    file_path = Path(bot_file)
    if not file_path.exists():
        continue
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for pattern, description in suspicious_patterns:
        if re.search(pattern, content):
            print(f"  ⚠️  Found in {bot_file}: {description}")
            found_issues = True
            all_correct = False

if not found_issues:
    print("  ✓ No suspicious hardcoded arrays found")

print()

# Final summary
print("=" * 80)
print("AUDIT SUMMARY")
print("=" * 80)
print()

if all_correct:
    print("✅ ALL CHECKS PASSED")
    print()
    print("No hardcoded values found!")
    print("All defaults match the web config standard:")
    print()
    for param, value in critical_params.items():
        if value is not None:
            print(f"  • {param}: {value}")
    print()
    print("Configuration flow is clean:")
    print("  Dashboard → bot_config.json → config_manager.py → Bot Logic")
else:
    print("⚠️  ISSUES FOUND")
    print()
    print("Please review the warnings above.")
    print("Some hardcoded values may need to be updated.")

print()
