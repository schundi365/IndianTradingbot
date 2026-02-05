"""
Verify Configuration Usage
Check that all config values are actually being used from config, not hardcoded
"""

import json
import re

# Load config
with open('bot_config.json', 'r') as f:
    config = json.load(f)

print("="*100)
print("CONFIGURATION USAGE VERIFICATION")
print("="*100)

# Critical config values that MUST come from config
critical_configs = {
    'rsi_overbought': 70,
    'rsi_oversold': 30,
    'macd_min_histogram': 0.0003,
    'adx_min_strength': 25,
    'tp_levels': [1.5, 2.5, 4.0],
    'reward_ratio': 1.2,
    'atr_multiplier': 2,
    'fast_ma_period': 20,
    'slow_ma_period': 50,
    'max_analysis_time_ms': 250,
}

# Read main bot file
with open('src/mt5_trading_bot.py', 'r', encoding='utf-8') as f:
    bot_content = f.read()

print("\nChecking critical configuration usage in mt5_trading_bot.py...\n")

issues = []

# Check RSI thresholds
if 'rsi_overbought = 70' in bot_content or 'rsi > 70' in bot_content:
    if 'config.get("rsi_overbought"' not in bot_content and 'self.config.get("rsi_overbought"' not in bot_content:
        issues.append("RSI overbought threshold (70) may be hardcoded")

if 'rsi_oversold = 30' in bot_content or 'rsi < 30' in bot_content:
    if 'config.get("rsi_oversold"' not in bot_content and 'self.config.get("rsi_oversold"' not in bot_content:
        issues.append("RSI oversold threshold (30) may be hardcoded")

# Check MACD threshold
macd_patterns = [
    r'histogram\s*[<>]=?\s*0\.0003',
    r'histogram\s*[<>]=?\s*0\.0005',
    r'MACD_THRESHOLD\s*=\s*0\.000[35]'
]

for pattern in macd_patterns:
    if re.search(pattern, bot_content):
        issues.append(f"MACD threshold may be hardcoded (pattern: {pattern})")

# Check TP levels
if '[1.5, 2.5, 4.0]' in bot_content or '[1.5, 2.0, 3.0]' in bot_content:
    # Check if it's using config
    if 'self.tp_levels' not in bot_content and 'config.get("tp_levels"' not in bot_content:
        issues.append("TP levels [1.5, 2.5, 4.0] may be hardcoded")

print("Critical Configuration Issues Found:")
print("="*100)

if issues:
    for i, issue in enumerate(issues, 1):
        print(f"{i}. {issue}")
else:
    print("[OK] No critical hardcoded values found!")

print(f"\n{'='*100}")
print("CONFIGURATION KEYS VERIFICATION")
print(f"{'='*100}")

# Check which config keys are actually used in the code
used_keys = set()
for key in config.keys():
    # Check if key is used in bot code
    patterns = [
        f'config.get("{key}"',
        f'config.get(\'{key}\'',
        f'self.config.get("{key}"',
        f'self.config.get(\'{key}\'',
        f'config["{key}"]',
        f'config[\'{key}\']',
    ]
    
    for pattern in patterns:
        if pattern in bot_content:
            used_keys.add(key)
            break

unused_keys = set(config.keys()) - used_keys

print(f"\nTotal config keys: {len(config)}")
print(f"Used in bot code: {len(used_keys)}")
print(f"Potentially unused: {len(unused_keys)}")

if unused_keys:
    print("\nPotentially unused config keys:")
    for key in sorted(unused_keys):
        print(f"  - {key}: {config[key]}")

print(f"\n{'='*100}")
print("RECOMMENDATIONS")
print(f"{'='*100}")

print("\n1. All critical values should use config.get() with defaults")
print("2. Remove unused config keys or implement their usage")
print("3. Add dashboard controls for all used config keys")
print("4. Document which config keys affect which features")

print(f"\n{'='*100}")
print("NEXT STEPS")
print(f"{'='*100}")

print("\n1. Review the issues found above")
print("2. Check if hardcoded values are intentional or bugs")
print("3. Update code to use config.get() for all configurable values")
print("4. Test that changing config values affects bot behavior")
print("5. Update dashboard to expose all config options")
