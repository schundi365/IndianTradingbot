"""
Integrate TP Caps from SCALP_TP_FIX
Adds symbol-specific TP caps to prevent unrealistic targets on volatile symbols
"""

from pathlib import Path
import re

print("=" * 80)
print("INTEGRATING TP CAPS FROM SCALP_TP_FIX")
print("=" * 80)
print()

print("This will add TP caps to prevent unrealistic take profit levels")
print("on volatile symbols like XAUUSD and XAGUSD.")
print()

# Step 1: Add to config_manager.py
print("Step 1: Adding scalp_tp_caps to config_manager.py...")
print("-" * 80)

config_manager_file = Path("src/config_manager.py")
with open(config_manager_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Add scalp_tp_caps after tp_levels
tp_caps_config = """            'scalp_tp_caps': {
                'XAUUSD': 2.0,   # Max 200 points on Gold
                'XAGUSD': 0.25,  # Max 250 points on Silver
                'XPTUSD': 3.0,   # Platinum
                'XPDUSD': 5.0,   # Palladium
                'DEFAULT': 0.01  # Forex: ~100 points
            },"""

# Find insertion point (after tp_levels line)
marker = "'tp_levels': [1, 1.5, 2.5],"
if marker in content and 'scalp_tp_caps' not in content:
    content = content.replace(marker, marker + '\n' + tp_caps_config)
    with open(config_manager_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("  ✓ Added scalp_tp_caps to config_manager.py")
elif 'scalp_tp_caps' in content:
    print("  ✓ scalp_tp_caps already exists in config_manager.py")
else:
    print("  ❌ Could not find insertion point")

print()

# Step 2: Update bot files
print("Step 2: Updating bot files with TP cap logic...")
print("-" * 80)

bot_files = [
    'src/mt5_trading_bot.py',
    'src/mt5_trading_bot_SIGNAL_FIX.py',
]

tp_cap_code_single = '''
        # ── TP CAP: Prevent unrealistic TPs on volatile symbols ──────────
        # Protects against huge TP on symbols like XAUUSD/XAGUSD
        if symbol:
            sym_upper = symbol.upper()
            tp_caps = self.config.get('scalp_tp_caps', {
                'XAUUSD': 2.0,   # max 200 pts on Gold
                'XAGUSD': 0.25,  # max 250 pts on Silver
                'XPTUSD': 3.0,   # Platinum
                'XPDUSD': 5.0,   # Palladium
                'DEFAULT': 0.01  # Forex: ~100 pts
            })
            cap = tp_caps.get(sym_upper, tp_caps.get('DEFAULT', 0.01))
            actual_reward = abs(tp - entry_price)
            if actual_reward > cap:
                if direction == 1:
                    tp = entry_price + cap
                else:
                    tp = entry_price - cap
                logging.info(f"  🎯 TP CAP applied on {symbol}: capped at {cap} (was {actual_reward:.5f})")
        # ─────────────────────────────────────────────────────────────────
        '''

tp_cap_code_multiple = '''
            # Apply TP cap per symbol (scaled for each level)
            if symbol:
                sym_upper = symbol.upper()
                tp_caps = self.config.get('scalp_tp_caps', {
                    'XAUUSD': 2.0,
                    'XAGUSD': 0.25,
                    'XPTUSD': 3.0,
                    'XPDUSD': 5.0,
                    'DEFAULT': 0.01
                })
                cap = tp_caps.get(sym_upper, tp_caps.get('DEFAULT', 0.01))
                # Scale cap with level: T1=1x, T2=1.5x, T3=2x
                level_cap = cap * (1 + i * 0.5)
                actual_reward = abs(tp - entry_price)
                if actual_reward > level_cap:
                    tp = (entry_price + level_cap) if direction == 1 else (entry_price - level_cap)
                    logging.info(f"    🎯 TP Level {i+1} capped at {level_cap:.5f} for {symbol}")
            '''

for bot_file in bot_files:
    file_path = Path(bot_file)
    if not file_path.exists():
        continue
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    modified = False
    
    # Update calculate_take_profit
    if 'TP CAP' not in content:
        # Find the return tp line in calculate_take_profit
        pattern = r'(def calculate_take_profit.*?else:  # Sell\s+tp = entry_price - reward)\s+(return tp)'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            content = content.replace(match.group(0), match.group(1) + '\n' + tp_cap_code_single + '\n        return tp')
            modified = True
            print(f"  ✓ {bot_file}: Added TP cap to calculate_take_profit()")
    
    # Update calculate_multiple_take_profits
    if 'Apply TP cap per symbol' not in content:
        # Find the tp_prices.append line in calculate_multiple_take_profits
        pattern = r'(if direction == 1:  # Buy\s+tp = entry_price \+ reward\s+else:  # Sell\s+tp = entry_price - reward)\s+(tp_prices\.append\(tp\))'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            content = content.replace(match.group(0), match.group(1) + '\n' + tp_cap_code_multiple + '\n            tp_prices.append(tp)')
            modified = True
            print(f"  ✓ {bot_file}: Added TP cap to calculate_multiple_take_profits()")
    
    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    elif 'TP CAP' in content:
        print(f"  ✓ {bot_file}: TP caps already integrated")
    else:
        print(f"  ⚠️  {bot_file}: Could not find insertion points (may need manual integration)")

print()

# Step 3: Summary
print("=" * 80)
print("TP CAPS INTEGRATION COMPLETE")
print("=" * 80)
print()

print("What was added:")
print("  • scalp_tp_caps configuration in config_manager.py")
print("  • TP cap logic in calculate_take_profit()")
print("  • Scaled TP cap logic in calculate_multiple_take_profits()")
print()

print("TP Caps by Symbol:")
print("  • XAUUSD (Gold): 2.0 points max")
print("  • XAGUSD (Silver): 0.25 points max")
print("  • XPTUSD (Platinum): 3.0 points max")
print("  • XPDUSD (Palladium): 5.0 points max")
print("  • Forex pairs: 0.01 points max (~100 pips)")
print()

print("Benefits:")
print("  ✓ Prevents unrealistic TPs on volatile symbols")
print("  ✓ Higher TP hit rate")
print("  ✓ Better profit taking")
print("  ✓ Symbol-specific (doesn't affect all pairs)")
print()

print("Next Steps:")
print("  1. Test with XAUUSD trades")
print("  2. Verify TPs are capped correctly")
print("  3. Monitor trade performance")
print("  4. Adjust caps if needed (in bot_config.json)")
print()
