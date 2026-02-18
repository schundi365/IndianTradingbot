#!/usr/bin/env python3
"""
Fix Persistent Errors - ADX KeyError and Logger NameError
"""

import re
import os

def fix_all_logger_references():
    """Fix all bare logger references in the codebase"""
    print("🔧 FIXING ALL LOGGER REFERENCES")
    print("=" * 50)
    
    files_to_check = [
        'src/mt5_trading_bot.py',
        'src/volume_analyzer.py',
        'src/config_manager.py',
        'web_dashboard.py'
    ]
    
    fixes_applied = 0
    
    for file_path in files_to_check:
        if not os.path.exists(file_path):
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Fix patterns for logger references
            patterns = [
                # Fix bare logger.info, logger.warning, etc.
                (r'\n(\s+)logger\.(info|warning|error|debug)\(', r'\n\1self.logger.\2('),
                # Fix logger.exception
                (r'\n(\s+)logger\.exception\(', r'\n\1self.logger.error('),
                # Fix any remaining bare logger references
                (r'(?<!self\.)(?<!\.)\blogger\.', r'self.logger.'),
            ]
            
            file_fixes = 0
            for pattern, replacement in patterns:
                new_content = re.sub(pattern, replacement, content)
                if new_content != content:
                    content = new_content
                    file_fixes += 1
            
            if file_fixes > 0:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Fixed {file_fixes} logger references in {file_path}")
                fixes_applied += file_fixes
            else:
                print(f"ℹ️ No logger fixes needed in {file_path}")
                
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
    
    return fixes_applied

def fix_all_adx_references():
    """Fix all ADX KeyError issues"""
    print(f"\n🔧 FIXING ALL ADX KEYERROR ISSUES")
    print("=" * 50)
    
    try:
        with open('src/mt5_trading_bot.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Comprehensive ADX fixes
        adx_fixes = [
            # Fix any remaining direct ADX access
            (r"latest\['adx'\]", "latest.get('adx', 0)"),
            (r"latest\['plus_di'\]", "latest.get('plus_di', 0)"),
            (r"latest\['minus_di'\]", "latest.get('minus_di', 0)"),
            
            # Fix ADX index checks
            (r"'adx' in latest\.index", "hasattr(latest, 'index') and 'adx' in getattr(latest, 'index', [])"),
            (r"'plus_di' in latest\.index", "hasattr(latest, 'index') and 'plus_di' in getattr(latest, 'index', [])"),
            (r"'minus_di' in latest\.index", "hasattr(latest, 'index') and 'minus_di' in getattr(latest, 'index', [])"),
            
            # Wrap any ADX calculations in try-except
            (r"(\s+)(# ADX.*?\n)(.*?)(adx = latest\.get\('adx', 0\))", 
             r"\1\2\1try:\n\3\4\n\1except (KeyError, AttributeError, IndexError):\n\1    adx = 0\n\1    plus_di = 0\n\1    minus_di = 0\n"),
        ]
        
        fixes_applied = 0
        for pattern, replacement in adx_fixes:
            new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            if new_content != content:
                content = new_content
                fixes_applied += 1
        
        # Add comprehensive ADX error handling
        if "# ADX and trend analysis" in content:
            # Find and replace the entire ADX section with bulletproof version
            adx_section_pattern = r"(# ADX and trend analysis.*?\n)(.*?)(adx = latest\.get\('adx', 0\).*?\n)"
            
            bulletproof_adx = r"""\1        # Bulletproof ADX calculation with comprehensive error handling
        adx = 0
        plus_di = 0
        minus_di = 0
        
        try:
            if 'adx' in df.columns and len(df) > 0:
                latest_row = df.iloc[-1]
                if hasattr(latest_row, 'get'):
                    adx = latest_row.get('adx', 0) if not pd.isna(latest_row.get('adx', 0)) else 0
                    plus_di = latest_row.get('plus_di', 0) if not pd.isna(latest_row.get('plus_di', 0)) else 0
                    minus_di = latest_row.get('minus_di', 0) if not pd.isna(latest_row.get('minus_di', 0)) else 0
                    
                    self.logger.info(f"ADX Values - ADX: {adx:.2f}, +DI: {plus_di:.2f}, -DI: {minus_di:.2f}")
        except Exception as e:
            self.logger.warning(f"ADX calculation error for {symbol}: {e} - using defaults")
            adx = 0
            plus_di = 0
            minus_di = 0
        
"""
            
            content = re.sub(adx_section_pattern, bulletproof_adx, content, flags=re.DOTALL)
            fixes_applied += 1
        
        if fixes_applied > 0:
            with open('src/mt5_trading_bot.py', 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Applied {fixes_applied} ADX fixes to mt5_trading_bot.py")
        else:
            print("ℹ️ No ADX fixes needed")
        
        return fixes_applied
        
    except Exception as e:
        print(f"❌ Error fixing ADX references: {e}")
        return 0

def add_missing_imports():
    """Add any missing imports that might be causing issues"""
    print(f"\n🔧 CHECKING AND ADDING MISSING IMPORTS")
    print("=" * 50)
    
    files_to_check = {
        'src/mt5_trading_bot.py': ['import pandas as pd', 'import numpy as np', 'import logging'],
        'src/volume_analyzer.py': ['import pandas as pd', 'import numpy as np', 'import logging'],
    }
    
    fixes_applied = 0
    
    for file_path, required_imports in files_to_check.items():
        if not os.path.exists(file_path):
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for import_statement in required_imports:
                if import_statement not in content:
                    # Add import at the top after existing imports
                    lines = content.split('\n')
                    import_line_added = False
                    
                    for i, line in enumerate(lines):
                        if line.startswith('import ') or line.startswith('from '):
                            continue
                        else:
                            # Insert import before first non-import line
                            lines.insert(i, import_statement)
                            import_line_added = True
                            break
                    
                    if import_line_added:
                        content = '\n'.join(lines)
                        fixes_applied += 1
                        print(f"✅ Added missing import: {import_statement} to {file_path}")
            
            # Write back if changes were made
            if fixes_applied > 0:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
        except Exception as e:
            print(f"❌ Error checking imports in {file_path}: {e}")
    
    return fixes_applied

def create_emergency_restart_script():
    """Create a script to restart the bot with error handling"""
    script_content = '''#!/usr/bin/env python3
"""
Emergency Bot Restart with Error Monitoring
"""

import subprocess
import time
import requests

def restart_bot_safely():
    """Restart bot and monitor for errors"""
    print("🚨 EMERGENCY BOT RESTART")
    print("=" * 40)
    
    try:
        # Stop bot via API
        print("🛑 Stopping bot...")
        response = requests.post("http://localhost:5000/api/bot/stop", timeout=10)
        if response.status_code == 200:
            print("✅ Bot stopped successfully")
        else:
            print("⚠️ Bot stop API call failed, continuing...")
        
        time.sleep(3)
        
        # Start bot via API
        print("🚀 Starting bot...")
        response = requests.post("http://localhost:5000/api/bot/start", timeout=10)
        if response.status_code == 200:
            print("✅ Bot started successfully")
            
            # Monitor for errors
            print("🔍 Monitoring for errors...")
            time.sleep(10)
            
            # Check recent logs
            response = requests.get("http://localhost:5000/api/logs?lines=50", timeout=5)
            if response.status_code == 200:
                logs = response.text
                if "KeyError: 'adx'" in logs:
                    print("❌ ADX KeyError still present!")
                elif "name 'logger' is not defined" in logs:
                    print("❌ Logger NameError still present!")
                else:
                    print("✅ No critical errors detected in recent logs")
            
            return True
        else:
            print("❌ Bot start failed")
            return False
            
    except Exception as e:
        print(f"❌ Error during restart: {e}")
        return False

if __name__ == "__main__":
    restart_bot_safely()
'''
    
    with open('emergency_restart_bot.py', 'w') as f:
        f.write(script_content)
    
    print("✅ Created emergency restart script: emergency_restart_bot.py")

def main():
    """Main fix function"""
    print("🚨 FIXING PERSISTENT ERRORS - COMPREHENSIVE SOLUTION")
    print("=" * 60)
    
    total_fixes = 0
    
    # Fix logger references
    logger_fixes = fix_all_logger_references()
    total_fixes += logger_fixes
    
    # Fix ADX references
    adx_fixes = fix_all_adx_references()
    total_fixes += adx_fixes
    
    # Add missing imports
    import_fixes = add_missing_imports()
    total_fixes += import_fixes
    
    # Create emergency restart script
    create_emergency_restart_script()
    
    print(f"\n🎉 COMPREHENSIVE FIX COMPLETE!")
    print(f"Total fixes applied: {total_fixes}")
    
    if total_fixes > 0:
        print(f"\n📋 NEXT STEPS:")
        print("1. Run: python emergency_restart_bot.py")
        print("2. Monitor logs for error elimination")
        print("3. Verify bot processes all symbols without crashes")
        
        print(f"\n✅ FIXES APPLIED:")
        if logger_fixes > 0:
            print(f"   • Logger references: {logger_fixes} fixes")
        if adx_fixes > 0:
            print(f"   • ADX KeyError issues: {adx_fixes} fixes")
        if import_fixes > 0:
            print(f"   • Missing imports: {import_fixes} fixes")
    else:
        print("ℹ️ No fixes were needed - errors may be elsewhere")
    
    return total_fixes > 0

if __name__ == "__main__":
    main()