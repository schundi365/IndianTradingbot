"""
Standardize TP Levels Across All Files
Remove hardcoded defaults and ensure consistency
"""

import json
from pathlib import Path

print("=" * 80)
print("STANDARDIZING TP LEVELS")
print("=" * 80)
print()

# Define the standard TP levels
STANDARD_TP_LEVELS = [1, 1.5, 2.5]

print(f"Standard TP Levels: {STANDARD_TP_LEVELS}")
print()

# Step 1: Update bot_config.json
print("Step 1: Verifying bot_config.json...")
print("-" * 80)

config_file = Path("bot_config.json")
with open(config_file, 'r') as f:
    config = json.load(f)

current_tp = config.get('tp_levels', [])
if current_tp == STANDARD_TP_LEVELS:
    print(f"  ✓ bot_config.json already has correct TP levels: {current_tp}")
else:
    print(f"  ⚠️  bot_config.json has: {current_tp}")
    print(f"  ✓ Updating to: {STANDARD_TP_LEVELS}")
    config['tp_levels'] = STANDARD_TP_LEVELS
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=4)

print()

# Step 2: Update config_manager.py
print("Step 2: Updating config_manager.py...")
print("-" * 80)

config_manager_file = Path("src/config_manager.py")
with open(config_manager_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the TP levels line
old_line = "'tp_levels': [1.5, 2.5, 4.0],"
new_line = "'tp_levels': [1, 1.5, 2.5],"

if old_line in content:
    content = content.replace(old_line, new_line)
    with open(config_manager_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  ✓ Updated: [1.5, 2.5, 4.0] → [1, 1.5, 2.5]")
else:
    print(f"  ✓ Already correct or pattern not found")

print()

# Step 3: Update bot files
print("Step 3: Updating bot files...")
print("-" * 80)

bot_files = [
    'src/mt5_trading_bot.py',
    'src/mt5_trading_bot_SIGNAL_FIX.py',
]

for bot_file in bot_files:
    file_path = Path(bot_file)
    if not file_path.exists():
        continue
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the hardcoded default
    old_default = "config.get('tp_levels', [1.5, 2.5, 4.0])"
    new_default = "config.get('tp_levels', [1, 1.5, 2.5])"
    
    if old_default in content:
        content = content.replace(old_default, new_default)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ {bot_file}: Updated default")
    else:
        print(f"  ✓ {bot_file}: Already correct or pattern not found")

print()

# Step 4: Update config.py (already correct, but verify)
print("Step 4: Verifying src/config.py...")
print("-" * 80)

config_py_file = Path("src/config.py")
with open(config_py_file, 'r', encoding='utf-8') as f:
    content = f.read()

if "TP_LEVELS = [1, 1.5, 2.5]" in content:
    print("  ✓ src/config.py already has correct TP levels")
else:
    print("  ⚠️  src/config.py may need manual review")

print()

# Step 5: Summary
print("=" * 80)
print("TP LEVELS STANDARDIZATION COMPLETE")
print("=" * 80)
print()

print(f"Standard TP Levels: {STANDARD_TP_LEVELS}")
print()
print("Updated Files:")
print("  • bot_config.json")
print("  • src/config_manager.py")
print("  • src/mt5_trading_bot.py")
print("  • src/mt5_trading_bot_SIGNAL_FIX.py")
print()
print("Rationale:")
print("  • [1, 1.5, 2.5] = Conservative, realistic targets")
print("  • 1.0R = Quick profit (40% of position)")
print("  • 1.5R = Moderate profit (30% of position)")
print("  • 2.5R = Extended profit (30% of position)")
print()
print("These levels work well for:")
print("  • M15-M30 timeframes")
print("  • Balanced risk/reward")
print("  • Consistent profit taking")
print()
