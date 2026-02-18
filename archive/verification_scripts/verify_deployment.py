#!/usr/bin/env python3
"""
Deployment Verification Script

Verifies that all configurations and documentation are properly deployed.
"""

import os
import json

def check_file(filepath, description):
    """Check if a file exists"""
    exists = os.path.exists(filepath)
    status = "✅" if exists else "❌"
    print(f"{status} {description}")
    return exists

def check_json_valid(filepath):
    """Check if JSON file is valid"""
    try:
        with open(filepath, 'r') as f:
            json.load(f)
        return True
    except:
        return False

def main():
    print("\n" + "="*70)
    print("DEPLOYMENT VERIFICATION")
    print("="*70 + "\n")
    
    all_good = True
    
    # Configuration files
    print("📦 CONFIGURATION FILES:")
    configs = [
        ('config_nifty_futures.json', 'NIFTY Futures Configuration'),
        ('config_banknifty_futures.json', 'BANKNIFTY Futures Configuration'),
        ('config_equity_intraday.json', 'Equity Intraday Configuration'),
        ('config_options_trading.json', 'Options Trading Configuration'),
        ('config_test_paper_trading.json', 'Test Paper Trading Configuration')
    ]
    
    for filepath, desc in configs:
        exists = check_file(filepath, desc)
        if exists and not check_json_valid(filepath):
            print(f"   ⚠️  Invalid JSON in {filepath}")
            all_good = False
        elif not exists:
            all_good = False
    
    # Documentation files
    print("\n📚 DOCUMENTATION FILES:")
    docs = [
        ('examples/README_CONFIGURATIONS.md', 'Comprehensive Configuration Guide'),
        ('examples/CONFIGURATION_SELECTOR.md', 'Configuration Selector Tool'),
        ('TESTING_GUIDE.md', 'Testing Guide'),
        ('DEPLOYMENT_SUMMARY.md', 'Deployment Summary'),
        ('QUICK_START_TESTING.md', 'Quick Start Testing Guide'),
        ('MIGRATION_GUIDE.md', 'Migration Guide'),
        ('INDIAN_MARKET_CONFIGS_README.md', 'Indian Market Configs README')
    ]
    
    for filepath, desc in docs:
        if not check_file(filepath, desc):
            all_good = False
    
    # Testing tools
    print("\n🔧 TESTING TOOLS:")
    tools = [
        ('deploy_configurations.py', 'Configuration Deployment Tool'),
        ('test_configuration.py', 'Configuration Test Runner'),
        ('validate_paper_trading.py', 'Paper Trading Validator'),
        ('validate_instruments.py', 'Instrument Validator'),
        ('kite_login.py', 'Kite Authentication Tool')
    ]
    
    for filepath, desc in tools:
        if not check_file(filepath, desc):
            all_good = False
    
    # Source files
    print("\n💻 SOURCE FILES:")
    sources = [
        ('src/broker_adapter.py', 'Broker Adapter Interface'),
        ('src/kite_adapter.py', 'Kite Connect Adapter'),
        ('src/indian_trading_bot.py', 'Indian Trading Bot')
    ]
    
    for filepath, desc in sources:
        if not check_file(filepath, desc):
            all_good = False
    
    # Summary
    print("\n" + "="*70)
    if all_good:
        print("✅ DEPLOYMENT VERIFICATION PASSED")
        print("\nAll files are present and valid!")
        print("\n🚀 READY FOR TESTING")
        print("\nNext steps:")
        print("1. Read: QUICK_START_TESTING.md")
        print("2. Update API key in config_test_paper_trading.json")
        print("3. Run: python kite_login.py")
        print("4. Run: python test_configuration.py")
        print("5. Run: python run_bot.py --config config_test_paper_trading.json")
    else:
        print("❌ DEPLOYMENT VERIFICATION FAILED")
        print("\nSome files are missing or invalid.")
        print("Please check the errors above.")
    
    print("="*70 + "\n")
    
    return all_good

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
