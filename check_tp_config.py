"""
Check and update TP levels configuration
"""
import json

print("="*80)
print("TP LEVELS CONFIGURATION CHECK")
print("="*80)

# Load current config
with open('bot_config.json', 'r') as f:
    config = json.load(f)

print("\nCURRENT CONFIGURATION:")
print("-"*80)
print(f"tp_levels: {config.get('tp_levels')}")
print(f"partial_close_percent: {config.get('partial_close_percent')}")
print(f"num_positions: {config.get('num_positions')}")
print(f"use_split_orders: {config.get('use_split_orders')}")

print("\n" + "="*80)
print("WHAT THE BOT DOES:")
print("="*80)
print("\nThe bot splits each trade into 3 positions:")
print(f"  Position 1: {config.get('partial_close_percent', [40,30,30])[0]}% of lots at TP level {config.get('tp_levels', [1.5,2.5,4.0])[0]}x risk")
print(f"  Position 2: {config.get('partial_close_percent', [40,30,30])[1]}% of lots at TP level {config.get('tp_levels', [1.5,2.5,4.0])[1]}x risk")
print(f"  Position 3: {config.get('partial_close_percent', [40,30,30])[2]}% of lots at TP level {config.get('tp_levels', [1.5,2.5,4.0])[2]}x risk")

print("\n" + "="*80)
print("EXAMPLE CALCULATION:")
print("="*80)
print("\nIf risk (SL distance) = 100 pips:")
print(f"  TP Level 1: {config.get('tp_levels', [1.5,2.5,4.0])[0]} x 100 = {config.get('tp_levels', [1.5,2.5,4.0])[0] * 100} pips")
print(f"  TP Level 2: {config.get('tp_levels', [1.5,2.5,4.0])[1]} x 100 = {config.get('tp_levels', [1.5,2.5,4.0])[1] * 100} pips")
print(f"  TP Level 3: {config.get('tp_levels', [1.5,2.5,4.0])[2]} x 100 = {config.get('tp_levels', [1.5,2.5,4.0])[2] * 100} pips")

print("\n" + "="*80)
print("TO CHANGE TP LEVELS:")
print("="*80)
print("\n1. Open web dashboard")
print("2. Go to 'Split Orders' section")
print("3. Update 'TP Levels' field")
print("4. Click 'Save Configuration'")
print("5. Restart bot")
print("\nOR edit bot_config.json directly:")
print('  "tp_levels": [1.5, 2.5, 4.0]  <- Change these values')
print('  "partial_close_percent": [40, 30, 30]  <- Change these percentages')

print("\n" + "="*80)
print("COMMON PRESETS:")
print("="*80)
print("\nConservative (safer, smaller profits):")
print('  "tp_levels": [1.0, 2.0, 3.0]')
print('  "partial_close_percent": [50, 30, 20]')

print("\nBalanced (current setting):")
print('  "tp_levels": [1.5, 2.5, 4.0]')
print('  "partial_close_percent": [40, 30, 30]')

print("\nAggressive (riskier, bigger profits):")
print('  "tp_levels": [2.0, 3.5, 6.0]')
print('  "partial_close_percent": [30, 30, 40]')

print("\n" + "="*80)
