"""
Fix TP Levels Contradiction
============================
Problem: Config has both individual tp_level_1/2/3 AND tp_levels array
Solution: Remove obsolete individual fields, use only tp_levels array
"""

import json
import shutil
from datetime import datetime

def fix_config():
    """Fix the contradictory TP level fields"""
    
    config_file = 'bot_config.json'
    
    # Backup
    backup_file = f'bot_config_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    shutil.copy(config_file, backup_file)
    print(f"✓ Backed up config to: {backup_file}")
    
    # Load config
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    print("\n" + "="*70)
    print("CONTRADICTORY TP LEVEL FIELDS FOUND")
    print("="*70)
    
    # Check for contradiction
    has_individual = 'tp_level_1' in config or 'tp_level_2' in config or 'tp_level_3' in config
    has_array = 'tp_levels' in config
    
    if has_individual:
        print("\n❌ Individual fields (OBSOLETE):")
        print(f"  tp_level_1: {config.get('tp_level_1', 'NOT SET')}")
        print(f"  tp_level_2: {config.get('tp_level_2', 'NOT SET')}")
        print(f"  tp_level_3: {config.get('tp_level_3', 'NOT SET')}")
    
    if has_array:
        print("\n✓ Array field (USED BY BOT):")
        print(f"  tp_levels: {config.get('tp_levels', 'NOT SET')}")
    
    if has_individual and has_array:
        print("\n⚠️ CONTRADICTION DETECTED!")
        print("The bot uses 'tp_levels' array, but individual fields also exist.")
        print("This causes confusion and potential errors.")
    
    # Fix: Remove individual fields
    print("\n" + "="*70)
    print("APPLYING FIX")
    print("="*70)
    
    removed_fields = []
    
    if 'tp_level_1' in config:
        del config['tp_level_1']
        removed_fields.append('tp_level_1')
    
    if 'tp_level_2' in config:
        del config['tp_level_2']
        removed_fields.append('tp_level_2')
    
    if 'tp_level_3' in config:
        del config['tp_level_3']
        removed_fields.append('tp_level_3')
    
    if removed_fields:
        print(f"✓ Removed obsolete fields: {', '.join(removed_fields)}")
    else:
        print("✓ No obsolete fields found")
    
    # Ensure tp_levels array exists
    if 'tp_levels' not in config:
        config['tp_levels'] = [1.5, 2.5, 4.0]
        print("✓ Added tp_levels array with default values")
    else:
        print(f"✓ Kept tp_levels array: {config['tp_levels']}")
    
    # Update timestamp
    config['last_updated'] = datetime.now().isoformat()
    
    # Save
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=4)
    
    print("\n" + "="*70)
    print("✓ CONFIGURATION FIXED")
    print("="*70)
    print(f"Config file: {config_file}")
    print(f"Backup: {backup_file}")
    print(f"\nTP Levels now: {config['tp_levels']}")
    
    return True

def check_bot_code():
    """Check which format the bot actually uses"""
    
    print("\n" + "="*70)
    print("VERIFYING BOT CODE")
    print("="*70)
    
    with open('src/mt5_trading_bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    uses_array = "config.get('tp_levels'" in content
    uses_individual = "config.get('tp_level_1'" in content
    
    print(f"\nBot uses tp_levels array: {uses_array}")
    print(f"Bot uses individual tp_level_1/2/3: {uses_individual}")
    
    if uses_array and not uses_individual:
        print("\n✓ Bot correctly uses tp_levels array only")
        return True
    elif uses_individual:
        print("\n⚠️ Bot uses individual fields - needs updating!")
        return False
    else:
        print("\n❌ Bot doesn't use either format!")
        return False

def check_dashboard():
    """Check what the dashboard saves"""
    
    print("\n" + "="*70)
    print("CHECKING DASHBOARD")
    print("="*70)
    
    with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    saves_individual = 'tp_level_1:' in content
    saves_array = 'tp_levels:' in content
    
    print(f"\nDashboard saves individual tp_level_1/2/3: {saves_individual}")
    print(f"Dashboard saves tp_levels array: {saves_array}")
    
    if saves_individual and not saves_array:
        print("\n⚠️ Dashboard needs updating to save tp_levels array!")
        print("This will be fixed in the next step.")
        return False
    elif saves_array:
        print("\n✓ Dashboard correctly saves tp_levels array")
        return True
    else:
        print("\n❌ Dashboard doesn't save TP levels!")
        return False

if __name__ == "__main__":
    print("="*70)
    print("TP LEVELS CONTRADICTION FIX")
    print("="*70)
    
    # Check bot code
    bot_ok = check_bot_code()
    
    # Check dashboard
    dashboard_ok = check_dashboard()
    
    # Fix config
    config_ok = fix_config()
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Bot code: {'✓ OK' if bot_ok else '⚠️ Needs update'}")
    print(f"Dashboard: {'✓ OK' if dashboard_ok else '⚠️ Needs update'}")
    print(f"Config file: {'✓ Fixed' if config_ok else '❌ Failed'}")
    
    if not dashboard_ok:
        print("\n" + "="*70)
        print("NEXT STEP: UPDATE DASHBOARD")
        print("="*70)
        print("The dashboard needs to be updated to save tp_levels array")
        print("instead of individual tp_level_1/2/3 fields.")
        print("\nRun: python fix_dashboard_tp_levels.py")
