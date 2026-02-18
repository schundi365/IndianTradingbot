#!/usr/bin/env python3
"""
Quick installation verification script
Run this after installation to verify everything is set up correctly
"""

import sys
import os
from pathlib import Path

def verify_installation():
    """Quick verification of installation"""
    print("Verifying Indian Market Web Dashboard installation...\n")
    
    issues = []
    
    # Check Python version
    if sys.version_info < (3, 8):
        issues.append("Python 3.8+ required")
    else:
        print("✓ Python version OK")
    
    # Check dependencies
    try:
        import flask
        import flask_cors
        import cryptography
        import pandas
        print("✓ Core dependencies installed")
    except ImportError as e:
        issues.append(f"Missing dependency: {e.name}")
    
    # Check .env file
    if not Path('.env').exists():
        issues.append(".env file not found - copy .env.example to .env")
    else:
        print("✓ .env file exists")
        
        # Check if keys are set
        with open('.env') as f:
            content = f.read()
            if 'change-this' in content.lower():
                issues.append("Secret keys not configured in .env file")
            else:
                print("✓ Secret keys configured")
    
    # Check directories
    required_dirs = ['data', 'configs', 'logs', 'static', 'templates', 'api', 'services']
    missing_dirs = [d for d in required_dirs if not Path(d).exists()]
    if missing_dirs:
        issues.append(f"Missing directories: {', '.join(missing_dirs)}")
    else:
        print("✓ Required directories exist")
    
    # Check config file
    try:
        from config import DASHBOARD_CONFIG
        print("✓ Configuration loads correctly")
    except Exception as e:
        issues.append(f"Configuration error: {str(e)}")
    
    # Summary
    print("\n" + "=" * 50)
    if issues:
        print("❌ Installation has issues:\n")
        for issue in issues:
            print(f"  - {issue}")
        print("\nRun 'python troubleshoot.py' for detailed diagnostics")
        return False
    else:
        print("✅ Installation verified successfully!")
        print("\nYou can now start the dashboard:")
        print("  python indian_dashboard.py")
        print("\nOr use the startup script:")
        print("  ./start_dashboard.sh  (Linux/macOS)")
        print("  start_dashboard.bat   (Windows)")
        return True

if __name__ == '__main__':
    success = verify_installation()
    sys.exit(0 if success else 1)
