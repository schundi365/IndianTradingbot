"""
Fix Configuration Synchronization Issues
1. Remove unused parameters from bot_config.json
2. Update bot_config.json with standardized values
3. Generate dashboard UI additions
"""

import json
from pathlib import Path
from datetime import datetime

print("=" * 80)
print("FIXING CONFIGURATION SYNCHRONIZATION")
print("=" * 80)
print()

# Load bot_config.json
config_file = Path("bot_config.json")
if not config_file.exists():
    print("❌ bot_config.json not found")
    exit(1)

with open(config_file, 'r') as f:
    config = json.load(f)

print(f"✅ Loaded bot_config.json ({len(config)} parameters)")
print()

# Step 1: Remove unused parameters
print("Step 1: Removing unused parameters...")
print("-" * 80)

unused_params = ['symbol_tp_levels', 'symbol_atr_multipliers']
removed = []

for param in unused_params:
    if param in config:
        del config[param]
        removed.append(param)
        print(f"  ✓ Removed: {param}")

if removed:
    print(f"\n  Removed {len(removed)} unused parameters")
else:
    print("  No unused parameters found")

print()

# Step 2: Update with standardized values
print("Step 2: Updating standardized values...")
print("-" * 80)

updates = {
    'fast_ma_period': 10,
    'slow_ma_period': 21,
    'dead_hours': [0, 1, 2, 17, 20, 21, 22],
    'golden_hours': [8, 11, 13, 14, 15, 19, 23],
}

for key, value in updates.items():
    old_value = config.get(key)
    if old_value != value:
        config[key] = value
        print(f"  ✓ Updated {key}: {old_value} → {value}")
    else:
        print(f"  ✓ {key}: Already correct ({value})")

print()

# Step 3: Update timestamp
config['last_updated'] = datetime.now().isoformat()
config['version'] = '2.1.0'

# Step 4: Save updated config
print("Step 3: Saving updated configuration...")
print("-" * 80)

# Backup original
backup_file = Path(f"bot_config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
with open(backup_file, 'w') as f:
    json.dump(json.load(open(config_file)), f, indent=4)
print(f"  ✓ Backup created: {backup_file}")

# Save updated config
with open(config_file, 'w') as f:
    json.dump(config, f, indent=4)
print(f"  ✓ Updated config saved: {config_file}")
print(f"  ✓ Total parameters: {len(config)}")

print()
print("=" * 80)
print("CONFIGURATION SYNC FIXED")
print("=" * 80)
print()

print("Summary:")
print(f"  • Removed {len(removed)} unused parameters")
print(f"  • Updated {len(updates)} standardized values")
print(f"  • Configuration backed up to {backup_file}")
print()

print("Next Steps:")
print("  1. Update dashboard UI to include missing controls")
print("  2. Restart bot to load new configuration")
print("  3. Verify all settings work correctly")
print()
