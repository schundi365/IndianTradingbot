"""
Apply user's requested settings and prepare for restart
This ensures all your configuration changes are saved before restart
"""
import json
from datetime import datetime

# Load current config
with open('bot_config.json', 'r') as f:
    config = json.load(f)

print("="*80)
print("APPLYING USER REQUESTED SETTINGS")
print("="*80)
print()

# Apply user's requested changes
changes_made = []

# 1. Timeframe M1 (already set)
if config['timeframe'] == 1:
    print("✓ Timeframe: M1 (1-minute) - Already set")
else:
    config['timeframe'] = 1
    changes_made.append("Timeframe changed to M1")
    print("✓ Timeframe: Changed to M1 (1-minute)")

# 2. Disable volume filter (user requested)
if config['use_volume_filter'] == False:
    print("✓ Volume Filter: Disabled - Already set")
else:
    config['use_volume_filter'] = False
    changes_made.append("Volume filter disabled")
    print("✓ Volume Filter: DISABLED")

# 3. Reduce confidence to 40% (user requested)
if config['min_confidence'] == 0.4:
    print("✓ Min Confidence: 40% - Already set")
else:
    config['min_confidence'] = 0.4
    changes_made.append("Min confidence reduced to 40%")
    print("✓ Min Confidence: Changed to 40%")

# 4. Keep symbols as is
print(f"✓ Symbols: {', '.join(config['symbols'])}")

# 5. Show filter status
print()
print("FILTER STATUS:")
print(f"  RSI Filter: {'ENABLED' if config['use_rsi'] else 'DISABLED'}")
print(f"  MACD Filter: {'ENABLED' if config['use_macd'] else 'DISABLED'}")
print(f"  Volume Filter: {'ENABLED' if config['use_volume_filter'] else 'DISABLED'}")
print(f"  ADX Filter: {'ENABLED' if config['use_adx'] else 'DISABLED'}")

# Update timestamp
config['last_updated'] = datetime.now().isoformat()

# Save configuration
if changes_made:
    print()
    print("="*80)
    print("SAVING CHANGES:")
    for change in changes_made:
        print(f"  - {change}")
    
    with open('bot_config.json', 'w') as f:
        json.dump(config, f, indent=4)
    
    print()
    print("✅ Configuration saved to bot_config.json")
else:
    print()
    print("✅ All settings already match your requests - no changes needed")

print("="*80)
print()
print("NEXT STEPS:")
print("1. Stop the current bot (Ctrl+C in the terminal)")
print("2. Restart: python start_dashboard.py")
print("3. The bot will load these settings automatically")
print("4. You'll see detailed logging in the next analysis cycle")
print()
print("="*80)
