"""
Fix Hardcoded Risk Multiplier Values in adaptive_risk_manager.py

This script updates adaptive_risk_manager.py to use config values
instead of hardcoded risk multiplier caps (0.3 and 1.5).

Changes:
- Line 447-448: Replace hardcoded 0.3 and 1.5 with config values
- Add config.get() calls for max_risk_multiplier and min_risk_multiplier
"""

import os
import shutil
from datetime import datetime

def fix_adaptive_risk_manager():
    """Fix hardcoded values in adaptive_risk_manager.py"""
    
    file_path = 'src/adaptive_risk_manager.py'
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    # Create backup
    backup_path = f"{file_path}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(file_path, backup_path)
    print(f"✅ Backup created: {backup_path}")
    
    # Read file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace the hardcoded line
    old_line = "        # Cap the multiplier\n        risk_multiplier = max(0.3, min(risk_multiplier, 1.5))"
    
    new_line = """        # Cap the multiplier using config values
        max_mult = self.config.get('max_risk_multiplier', 1.5)
        min_mult = self.config.get('min_risk_multiplier', 0.5)
        risk_multiplier = max(min_mult, min(risk_multiplier, max_mult))"""
    
    if old_line in content:
        content = content.replace(old_line, new_line)
        print("✅ Found and replaced hardcoded risk multiplier caps")
    else:
        print("⚠️  Could not find exact match for hardcoded line")
        print("    Searching for alternative pattern...")
        
        # Try alternative pattern
        alt_pattern = "risk_multiplier = max(0.3, min(risk_multiplier, 1.5))"
        if alt_pattern in content:
            # Replace just the line
            content = content.replace(
                alt_pattern,
                "risk_multiplier = max(self.config.get('min_risk_multiplier', 0.5), min(risk_multiplier, self.config.get('max_risk_multiplier', 1.5)))"
            )
            print("✅ Found and replaced using alternative pattern")
        else:
            print("❌ Could not find hardcoded values to replace")
            return False
    
    # Write updated content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Updated: {file_path}")
    print()
    print("Changes made:")
    print("  - Replaced hardcoded 0.3 with config.get('min_risk_multiplier', 0.5)")
    print("  - Replaced hardcoded 1.5 with config.get('max_risk_multiplier', 1.5)")
    print()
    print("Now adaptive_risk_manager.py will respect config values!")
    
    return True

if __name__ == "__main__":
    print("=" * 70)
    print("FIX ADAPTIVE RISK MANAGER - HARDCODED VALUES")
    print("=" * 70)
    print()
    
    success = fix_adaptive_risk_manager()
    
    if success:
        print()
        print("=" * 70)
        print("✅ FIX COMPLETE")
        print("=" * 70)
        print()
        print("Next steps:")
        print("1. Review the changes in src/adaptive_risk_manager.py")
        print("2. Test that config values are now respected")
        print("3. Restart the bot to load the updated module")
    else:
        print()
        print("=" * 70)
        print("❌ FIX FAILED")
        print("=" * 70)
        print()
        print("Manual fix required:")
        print("1. Open src/adaptive_risk_manager.py")
        print("2. Find line ~447-448 with: risk_multiplier = max(0.3, min(risk_multiplier, 1.5))")
        print("3. Replace with:")
        print("   max_mult = self.config.get('max_risk_multiplier', 1.5)")
        print("   min_mult = self.config.get('min_risk_multiplier', 0.5)")
        print("   risk_multiplier = max(min_mult, min(risk_multiplier, max_mult))")
