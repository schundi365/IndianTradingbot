#!/usr/bin/env python3
"""
Configuration Testing Script

Quick test runner for Indian market trading bot configurations.
"""

import argparse
import json
import os
import sys
from datetime import datetime

def print_banner():
    """Print test banner"""
    print("\n" + "="*70)
    print("INDIAN MARKET TRADING BOT - CONFIGURATION TESTER")
    print("="*70 + "\n")

def load_config(config_path):
    """Load and display configuration"""
    if not os.path.exists(config_path):
        print(f"❌ Configuration file not found: {config_path}")
        return None
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in configuration: {e}")
        return None

def display_config_summary(config, config_path):
    """Display configuration summary"""
    print("📋 CONFIGURATION SUMMARY")
    print("-" * 70)
    print(f"File: {config_path}")
    print(f"Broker: {config.get('broker', 'N/A')}")
    print(f"Exchange: {config.get('default_exchange', 'N/A')}")
    print(f"Symbols: {', '.join(config.get('symbols', [])[:3])}{'...' if len(config.get('symbols', [])) > 3 else ''}")
    print(f"Timeframe: {config.get('timeframe', 'N/A')} minutes")
    print(f"Risk per trade: {config.get('risk_percent', 'N/A')}%")
    print(f"Reward ratio: {config.get('reward_ratio', 'N/A')}x")
    print(f"Max positions: {config.get('max_positions', 'N/A')}")
    print(f"Max trades/day: {config.get('max_trades_per_day', 'N/A')}")
    print(f"Product type: {config.get('product_type', 'N/A')}")
    
    # Paper trading status
    paper_trading = config.get('paper_trading', False)
    status = "🧪 PAPER TRADING (Safe)" if paper_trading else "💰 LIVE TRADING (Real money!)"
    print(f"\nMode: {status}")
    
    print("-" * 70 + "\n")

def check_prerequisites():
    """Check if prerequisites are met"""
    print("🔍 CHECKING PREREQUISITES")
    print("-" * 70)
    
    checks = []
    
    # Check if kite_token.json exists
    token_exists = os.path.exists('kite_token.json')
    checks.append(("Kite token file", token_exists))
    
    if token_exists:
        try:
            with open('kite_token.json', 'r') as f:
                token_data = json.load(f)
            token_date = token_data.get('date', '')
            today = datetime.now().strftime("%Y-%m-%d")
            token_valid = token_date == today
            checks.append(("Token is current", token_valid))
        except:
            checks.append(("Token is current", False))
    
    # Check if required modules exist
    required_files = [
        'src/broker_adapter.py',
        'src/kite_adapter.py',
        'src/indian_trading_bot.py'
    ]
    
    for file in required_files:
        exists = os.path.exists(file)
        checks.append((f"Module: {file}", exists))
    
    # Display results
    all_passed = True
    for check_name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}")
        if not passed:
            all_passed = False
    
    print("-" * 70 + "\n")
    
    if not all_passed:
        print("⚠️  Some prerequisites are missing!")
        print("\nTo fix:")
        print("1. Run: python kite_login.py (to generate token)")
        print("2. Ensure all source files are present")
        print()
        return False
    
    return True

def run_validation_tests(config_path):
    """Run validation tests"""
    print("🧪 RUNNING VALIDATION TESTS")
    print("-" * 70)
    
    tests = [
        ("Configuration validation", f"python deploy_configurations.py"),
        ("Instrument validation", f"python validate_instruments.py --config {config_path}"),
        ("Paper trading validation", f"python validate_paper_trading.py --config {config_path}")
    ]
    
    print("Available validation tests:")
    for i, (test_name, command) in enumerate(tests, 1):
        print(f"{i}. {test_name}")
        print(f"   Command: {command}")
    
    print("\nRun these tests manually to validate your configuration.")
    print("-" * 70 + "\n")

def display_next_steps(config, config_path):
    """Display next steps"""
    print("🚀 NEXT STEPS")
    print("-" * 70)
    
    paper_trading = config.get('paper_trading', False)
    
    if paper_trading:
        print("✅ Paper trading is ENABLED - Safe to test!")
        print("\nTo start testing:")
        print(f"   python run_bot.py --config {config_path}")
        print("\nMonitor the logs for:")
        print("   • Connection status")
        print("   • Signal generation")
        print("   • Simulated order placement")
        print("   • Position tracking")
        print("\nLet it run for 1-2 hours during market hours.")
    else:
        print("⚠️  LIVE TRADING is ENABLED - Real money at risk!")
        print("\n🚨 IMPORTANT: Before going live:")
        print("   1. Test with paper trading first")
        print("   2. Verify all signals are correct")
        print("   3. Start with very small position sizes")
        print("   4. Monitor first few trades closely")
        print("\nTo enable paper trading:")
        print(f'   Edit {config_path} and add: "paper_trading": true')
        print("\nTo start live trading (after testing):")
        print(f"   python run_bot.py --config {config_path}")
    
    print("-" * 70 + "\n")

def display_monitoring_tips():
    """Display monitoring tips"""
    print("📊 MONITORING TIPS")
    print("-" * 70)
    print("During testing, monitor these:")
    print("\n1. Connection Status:")
    print("   • Bot connects to Kite successfully")
    print("   • No authentication errors")
    print("\n2. Data Fetching:")
    print("   • Historical data loads without errors")
    print("   • All symbols are found")
    print("\n3. Signal Generation:")
    print("   • Signals are generated (check logs)")
    print("   • Signal quality is good (not too many/few)")
    print("\n4. Order Execution:")
    print("   • Orders are placed correctly")
    print("   • Stop losses are set")
    print("   • Take profits are set")
    print("\n5. Risk Management:")
    print("   • Position sizes are correct")
    print("   • Risk per trade is within limits")
    print("   • Daily loss limits are respected")
    print("\nLog Commands:")
    print("   • View logs: tail -f indian_trading_bot.log")
    print("   • Search signals: grep 'SIGNAL' indian_trading_bot.log")
    print("   • Search orders: grep 'ORDER' indian_trading_bot.log")
    print("   • Search errors: grep 'ERROR' indian_trading_bot.log")
    print("-" * 70 + "\n")

def main():
    parser = argparse.ArgumentParser(
        description='Test Indian market trading bot configuration'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config_test_paper_trading.json',
        help='Configuration file to test (default: config_test_paper_trading.json)'
    )
    parser.add_argument(
        '--quick',
        action='store_true',
        help='Quick test (skip detailed checks)'
    )
    
    args = parser.parse_args()
    
    print_banner()
    
    # Load configuration
    config = load_config(args.config)
    if not config:
        sys.exit(1)
    
    # Display configuration summary
    display_config_summary(config, args.config)
    
    if not args.quick:
        # Check prerequisites
        if not check_prerequisites():
            print("❌ Prerequisites check failed!")
            print("\nFix the issues above and try again.")
            sys.exit(1)
        
        # Run validation tests
        run_validation_tests(args.config)
    
    # Display next steps
    display_next_steps(config, args.config)
    
    # Display monitoring tips
    if not args.quick:
        display_monitoring_tips()
    
    print("="*70)
    print("✨ Configuration test preparation complete!")
    print("📚 For detailed guide, see: TESTING_GUIDE.md")
    print("🚀 Ready to start testing!")
    print("="*70 + "\n")

if __name__ == '__main__':
    main()
