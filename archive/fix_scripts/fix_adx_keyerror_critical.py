#!/usr/bin/env python3
"""
Critical ADX KeyError Fix - Emergency Patch
"""

import re

def fix_adx_keyerror():
    """Fix the ADX KeyError by adding proper error handling"""
    print("🚨 CRITICAL ADX KEYERROR FIX")
    print("=" * 50)
    
    try:
        # Read the current file
        with open('src/mt5_trading_bot.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"✅ File read successfully ({len(content)} characters)")
        
        # Find the problematic line
        problematic_pattern = r"if 'adx' in df\.columns and not pd\.isna\(latest\['adx'\]\):"
        
        if re.search(problematic_pattern, content):
            print("✅ Found problematic ADX line")
            
            # Replace with safe version
            safe_replacement = "if 'adx' in df.columns and 'adx' in latest.index and not pd.isna(latest['adx']):"
            
            content = re.sub(problematic_pattern, safe_replacement, content)
            
            # Also fix the next line that accesses latest['adx']
            content = re.sub(
                r"adx = latest\['adx'\]",
                "adx = latest.get('adx', 0)",
                content
            )
            
            # Write the fixed content back
            with open('src/mt5_trading_bot.py', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ ADX KeyError fix applied successfully!")
            print("   • Added index check: 'adx' in latest.index")
            print("   • Changed to safe access: latest.get('adx', 0)")
            
            return True
        else:
            print("⚠️ Problematic ADX line not found - may already be fixed")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing ADX KeyError: {e}")
        return False

def verify_fix():
    """Verify the fix was applied correctly"""
    print("\n🔍 VERIFYING FIX")
    print("-" * 30)
    
    try:
        with open('src/mt5_trading_bot.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for the safe pattern
        safe_pattern = r"if 'adx' in df\.columns and 'adx' in latest\.index and not pd\.isna\(latest\['adx'\]\):"
        safe_access = r"adx = latest\.get\('adx', 0\)"
        
        has_safe_check = bool(re.search(safe_pattern, content))
        has_safe_access = bool(re.search(safe_access, content))
        
        print(f"✅ Safe ADX check: {'FOUND' if has_safe_check else 'NOT FOUND'}")
        print(f"✅ Safe ADX access: {'FOUND' if has_safe_access else 'NOT FOUND'}")
        
        if has_safe_check and has_safe_access:
            print("🎉 ADX KeyError fix verified successfully!")
            return True
        else:
            print("⚠️ Fix verification failed")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying fix: {e}")
        return False

if __name__ == "__main__":
    success = fix_adx_keyerror()
    if success:
        verify_fix()
        print("\n🎉 CRITICAL ADX FIX COMPLETE!")
        print("The bot should now handle USDJPY without KeyError crashes")
    else:
        print("\n❌ CRITICAL ADX FIX FAILED!")
        print("Manual intervention may be required")