"""
Setup Validation Script
Validates the project structure and dependencies without requiring MT5
"""

import sys
import os


def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} (requires 3.8+)")
        return False


def check_dependencies():
    """Check if required packages are installed"""
    packages = {
        'MetaTrader5': 'MetaTrader5',
        'pandas': 'pandas',
        'numpy': 'numpy'
    }
    
    all_ok = True
    for name, import_name in packages.items():
        try:
            __import__(import_name)
            print(f"✅ {name} installed")
        except ImportError:
            print(f"❌ {name} not installed")
            all_ok = False
    
    return all_ok


def check_file_structure():
    """Check if all required files exist"""
    required_files = [
        os.path.join('src', 'mt5_trading_bot.py'),
        os.path.join('src', 'config.py'),
        os.path.join('src', 'adaptive_risk_manager.py'),
        os.path.join('src', 'split_order_calculator.py'),
        os.path.join('src', 'trailing_strategies.py'),
        'run_bot.py',
        'test_connection.py',
        'requirements.txt'
    ]
    
    all_ok = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} missing")
            all_ok = False
    
    return all_ok


def check_config():
    """Check if config can be imported"""
    try:
        sys.path.insert(0, 'src')
        from config import get_config
        config = get_config()
        print(f"✅ Configuration loaded")
        print(f"   Symbols: {config['symbols']}")
        print(f"   Risk: {config['risk_percent']}%")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {str(e)}")
        return False


def main():
    print("=" * 60)
    print("MT5 TRADING BOT - SETUP VALIDATION")
    print("=" * 60)
    print()
    
    results = []
    
    # Check Python version
    print("Checking Python version...")
    results.append(check_python_version())
    print()
    
    # Check dependencies
    print("Checking dependencies...")
    results.append(check_dependencies())
    print()
    
    # Check file structure
    print("Checking file structure...")
    results.append(check_file_structure())
    print()
    
    # Check configuration
    print("Checking configuration...")
    results.append(check_config())
    print()
    
    # Summary
    print("=" * 60)
    if all(results):
        print("✅ ALL CHECKS PASSED")
        print()
        print("Setup is complete! Next steps:")
        print("1. Make sure MT5 is installed and running")
        print("2. Run: python test_connection.py")
        print("3. Configure: src/config.py")
        print("4. Start bot: python run_bot.py")
    else:
        print("❌ SOME CHECKS FAILED")
        print()
        print("Please fix the issues above before proceeding.")
        print("Run: python setup.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
