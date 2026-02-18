"""
Update TP levels to match dashboard settings
"""
import json
from datetime import datetime

print("="*80)
print("UPDATING TP LEVELS TO MATCH DASHBOARD")
print("="*80)

# Load current config
with open('bot_config.json', 'r') as f:
    config = json.load(f)

print("\nCURRENT VALUES:")
print(f"  tp_levels: {config.get('tp_levels')}")
print(f"  partial_close_percent: {config.get('partial_close_percent')}")

# Update to match dashboard
config['tp_levels'] = [1.0, 2.0, 3.0]
# Keep the same allocation percentages
# config['partial_close_percent'] stays [40, 30, 30]

print("\nNEW VALUES:")
print(f"  tp_levels: {config['tp_levels']}")
print(f"  partial_close_percent: {config.get('partial_close_percent')}")

# Update timestamp
config['last_updated'] = datetime.now().isoformat()

# Save config
with open('bot_config.json', 'w') as f:
    json.dump(config, f, indent=4)

print("\n✅ Configuration updated!")
print("\nNEW TP CALCULATION:")
print("  If risk (SL distance) = 100 pips:")
print("    TP Level 1: 1.0 x 100 = 100 pips (40% of lots)")
print("    TP Level 2: 2.0 x 100 = 200 pips (30% of lots)")
print("    TP Level 3: 3.0 x 100 = 300 pips (30% of lots)")

print("\n⚠️  RESTART BOT to apply changes!")
print("="*80)
