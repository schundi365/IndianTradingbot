"""
Audit Configuration Synchronization
Checks for mismatches between bot_config.json, dashboard, and bot logic
"""

import json
from pathlib import Path

print("=" * 80)
print("CONFIGURATION SYNCHRONIZATION AUDIT")
print("=" * 80)
print()

# Load bot_config.json
config_file = Path("bot_config.json")
if config_file.exists():
    with open(config_file, 'r') as f:
        config = json.load(f)
    print(f"✅ Loaded bot_config.json ({len(config)} parameters)")
else:
    print("❌ bot_config.json not found")
    exit(1)

print()
print("=" * 80)
print("ISSUE 1: Parameters in Config but NOT Used by Bot Logic")
print("=" * 80)
print()

# These are in config but not used
unused_params = {
    'symbol_tp_levels': 'Per-symbol TP levels (NOT USED - bot uses global tp_levels)',
    'symbol_atr_multipliers': 'Per-symbol ATR multipliers (NOT USED - bot uses global atr_multiplier)',
}

for param, description in unused_params.items():
    if param in config:
        print(f"⚠️  {param}")
        print(f"   Description: {description}")
        print(f"   Current value: {type(config[param]).__name__} with {len(config[param])} entries")
        print()

print("=" * 80)
print("ISSUE 2: Parameters NOT in Dashboard UI")
print("=" * 80)
print()

# These should be in dashboard but aren't
missing_from_dashboard = [
    'golden_hours',
    'dead_hours',
    'roc_threshold',
    'enable_hour_filter',
    'fast_ma_period',
    'slow_ma_period',
    'enable_time_based_exit',
    'max_hold_minutes',
    'enable_breakeven_stop',
    'breakeven_atr_threshold',
]

for param in missing_from_dashboard:
    if param in config:
        print(f"⚠️  {param}: {config[param]}")

print()
print("=" * 80)
print("ISSUE 3: Hardcoded Values in Bot Logic")
print("=" * 80)
print()

print("Checking for hardcoded defaults in bot files...")
print("(These should come from config, not hardcoded)")
print()

# Check mt5_trading_bot.py for hardcoded values
bot_files = [
    'src/mt5_trading_bot.py',
    'src/mt5_trading_bot_SIGNAL_FIX.py'
]

for bot_file in bot_files:
    if Path(bot_file).exists():
        with open(bot_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for hardcoded defaults in config.get() calls
        hardcoded_patterns = [
            ("config.get('fast_ma_period'", "fast_ma_period"),
            ("config.get('slow_ma_period'", "slow_ma_period"),
            ("config.get('dead_hours'", "dead_hours"),
            ("config.get('golden_hours'", "golden_hours"),
        ]
        
        print(f"\n{bot_file}:")
        for pattern, param in hardcoded_patterns:
            if pattern in content:
                # Extract the default value
                start = content.find(pattern)
                if start != -1:
                    line_start = content.rfind('\n', 0, start) + 1
                    line_end = content.find('\n', start)
                    line = content[line_start:line_end].strip()
                    print(f"  ✓ {param}: {line}")

print()
print("=" * 80)
print("RECOMMENDATIONS")
print("=" * 80)
print()

print("1. REMOVE UNUSED PARAMETERS from bot_config.json:")
print("   - symbol_tp_levels (use global tp_levels instead)")
print("   - symbol_atr_multipliers (use global atr_multiplier instead)")
print()

print("2. ADD TO DASHBOARD UI:")
print("   - golden_hours / dead_hours (hour filter configuration)")
print("   - fast_ma_period / slow_ma_period (MA configuration)")
print("   - Time-based exit settings")
print("   - Breakeven stop settings")
print()

print("3. ENSURE NO HARDCODED VALUES:")
print("   - All defaults should match config_manager.py")
print("   - Bot should always use config.get() with correct defaults")
print()

print("=" * 80)
print("AUDIT COMPLETE")
print("=" * 80)
