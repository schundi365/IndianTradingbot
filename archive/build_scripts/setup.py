"""
Setup script for MT5 Trading Bot
Helps with initial installation and configuration
"""

import subprocess
import sys
import os


def install_dependencies():
    """Install required Python packages"""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False


def check_mt5_installed():
    """Check if MT5 Python package is installed"""
    try:
        import MetaTrader5 as mt5
        print("✅ MetaTrader5 package is installed")
        return True
    except ImportError:
        print("❌ MetaTrader5 package not found")
        return False


def create_directories():
    """Create necessary directories"""
    dirs = ['logs', 'data', 'backtest_results']
    for dir_name in dirs:
        os.makedirs(dir_name, exist_ok=True)
    print("✅ Created necessary directories")


def main():
    print("=" * 60)
    print("MT5 TRADING BOT - SETUP")
    print("=" * 60)
    print()
    
    # Step 1: Install dependencies
    print("Step 1: Installing dependencies...")
    if not install_dependencies():
        print("\nSetup failed. Please install dependencies manually:")
        print("pip install -r requirements.txt")
        return
    print()
    
    # Step 2: Verify MT5 package
    print("Step 2: Verifying MT5 package...")
    if not check_mt5_installed():
        print("\nPlease install MetaTrader5 package:")
        print("pip install MetaTrader5")
        return
    print()
    
    # Step 3: Create directories
    print("Step 3: Creating directories...")
    create_directories()
    print()
    
    # Step 4: Test connection
    print("Step 4: Testing MT5 connection...")
    print("Run: python test_connection.py")
    print()
    
    print("=" * 60)
    print("SETUP COMPLETE!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Make sure MT5 is running and logged in")
    print("2. Run: python test_connection.py")
    print("3. Configure settings in src/config.py")
    print("4. Start bot: python run_bot.py")
    print()


if __name__ == "__main__":
    main()
