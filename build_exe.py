"""
Build Executable for MT5 Trading Bot
Creates a standalone .exe file that can be shared with other users
"""

import PyInstaller.__main__
import os
import shutil

def build_executable():
    """Build the trading bot executable"""
    
    print("=" * 80)
    print("BUILDING MT5 TRADING BOT EXECUTABLE")
    print("=" * 80)
    print()
    
    # Clean previous builds
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    
    print("1. Cleaning previous builds...")
    print("   ✓ Removed build/ and dist/ directories")
    print()
    
    # PyInstaller options
    options = [
        'run_bot.py',                    # Main script
        '--name=MT5_Trading_Bot',        # Executable name
        '--onefile',                     # Single executable file
        '--windowed',                    # No console window (GUI mode)
        '--icon=NONE',                   # No icon (can add later)
        '--add-data=src;src',            # Include src folder
        '--add-data=docs;docs',          # Include docs folder
        '--add-data=examples;examples',  # Include examples folder
        '--hidden-import=MetaTrader5',   # Ensure MT5 is included
        '--hidden-import=pandas',
        '--hidden-import=numpy',
        '--hidden-import=logging',
        '--collect-all=MetaTrader5',     # Collect all MT5 files
        '--noconfirm',                   # Overwrite without asking
    ]
    
    print("2. Building executable with PyInstaller...")
    print("   This may take a few minutes...")
    print()
    
    try:
        PyInstaller.__main__.run(options)
        
        print()
        print("=" * 80)
        print("BUILD SUCCESSFUL!")
        print("=" * 80)
        print()
        print("Executable created:")
        print("  Location: dist/MT5_Trading_Bot.exe")
        print("  Size: ~50-100 MB (includes Python + all dependencies)")
        print()
        print("To distribute:")
        print("  1. Copy dist/MT5_Trading_Bot.exe to target computer")
        print("  2. User needs MetaTrader 5 installed")
        print("  3. User needs to configure src/config.py (symbols, risk, etc.)")
        print()
        print("Note: Users will need to edit config.py before running!")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print()
        print("=" * 80)
        print("BUILD FAILED!")
        print("=" * 80)
        print(f"Error: {str(e)}")
        print()
        print("Common issues:")
        print("  1. PyInstaller not installed: pip install pyinstaller")
        print("  2. Missing dependencies: pip install -r requirements.txt")
        print("  3. Antivirus blocking: Temporarily disable antivirus")
        print("=" * 80)
        
        return False


if __name__ == "__main__":
    build_executable()
