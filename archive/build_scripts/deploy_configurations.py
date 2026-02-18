#!/usr/bin/env python3
"""
Configuration Deployment and Validation Script

This script validates all Indian market configurations and prepares them for testing.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Tuple

class ConfigurationValidator:
    """Validates configuration files for completeness and correctness"""
    
    REQUIRED_FIELDS = [
        'broker', 'symbols', 'timeframe', 'risk_percent', 'reward_ratio',
        'trading_hours', 'product_type'
    ]
    
    OPTIONAL_FIELDS = [
        'kite_api_key', 'kite_token_file', 'default_exchange',
        'magic_number', 'max_daily_loss_percent', 'max_drawdown_percent',
        'fast_ma_period', 'slow_ma_period', 'atr_period', 'atr_multiplier',
        'use_split_orders', 'num_positions', 'tp_levels', 'partial_close_percent',
        'use_adaptive_risk', 'ml_enabled', 'use_volume_filter', 'use_trend_detection',
        'max_positions', 'max_trades_per_day'
    ]
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []
    
    def validate_config(self, config_path: str) -> Tuple[bool, Dict]:
        """Validate a configuration file"""
        self.errors = []
        self.warnings = []
        self.info = []
        
        # Check file exists
        if not os.path.exists(config_path):
            self.errors.append(f"Configuration file not found: {config_path}")
            return False, {}
        
        # Load JSON
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON in {config_path}: {e}")
            return False, {}
        
        # Check required fields
        for field in self.REQUIRED_FIELDS:
            if field not in config:
                self.errors.append(f"Missing required field: {field}")
        
        # Validate field values
        self._validate_broker(config)
        self._validate_symbols(config)
        self._validate_timeframe(config)
        self._validate_risk_params(config)
        self._validate_trading_hours(config)
        self._validate_product_type(config)
        
        # Check for API key placeholder
        if config.get('kite_api_key') == 'YOUR_KITE_API_KEY_HERE':
            self.warnings.append("API key is still placeholder - update before live trading")
        
        # Summary
        is_valid = len(self.errors) == 0
        self.info.append(f"Configuration: {os.path.basename(config_path)}")
        self.info.append(f"Broker: {config.get('broker', 'N/A')}")
        self.info.append(f"Symbols: {len(config.get('symbols', []))} configured")
        self.info.append(f"Timeframe: {config.get('timeframe', 'N/A')} minutes")
        self.info.append(f"Risk per trade: {config.get('risk_percent', 'N/A')}%")
        
        return is_valid, config
    
    def _validate_broker(self, config: Dict):
        """Validate broker configuration"""
        broker = config.get('broker')
        if broker and broker not in ['kite']:
            self.warnings.append(f"Unknown broker: {broker} (currently only 'kite' is supported)")
    
    def _validate_symbols(self, config: Dict):
        """Validate symbols configuration"""
        symbols = config.get('symbols', [])
        if not symbols:
            self.errors.append("No symbols configured")
        elif not isinstance(symbols, list):
            self.errors.append("Symbols must be a list")
        else:
            self.info.append(f"Symbols configured: {', '.join(symbols[:3])}{'...' if len(symbols) > 3 else ''}")
    
    def _validate_timeframe(self, config: Dict):
        """Validate timeframe"""
        timeframe = config.get('timeframe')
        if timeframe:
            valid_timeframes = [1, 5, 15, 30, 60]
            if timeframe not in valid_timeframes:
                self.warnings.append(f"Unusual timeframe: {timeframe} (common: {valid_timeframes})")
    
    def _validate_risk_params(self, config: Dict):
        """Validate risk parameters"""
        risk_percent = config.get('risk_percent')
        if risk_percent:
            if risk_percent < 0.1:
                self.warnings.append(f"Very low risk: {risk_percent}% (may limit trading)")
            elif risk_percent > 5.0:
                self.warnings.append(f"Very high risk: {risk_percent}% (dangerous!)")
        
        reward_ratio = config.get('reward_ratio')
        if reward_ratio:
            if reward_ratio < 1.0:
                self.warnings.append(f"Reward ratio < 1.0: {reward_ratio} (risk > reward)")
            elif reward_ratio > 5.0:
                self.warnings.append(f"Very high reward ratio: {reward_ratio} (may be unrealistic)")
    
    def _validate_trading_hours(self, config: Dict):
        """Validate trading hours"""
        trading_hours = config.get('trading_hours', {})
        if not isinstance(trading_hours, dict):
            self.errors.append("trading_hours must be a dictionary")
        elif 'start' not in trading_hours or 'end' not in trading_hours:
            self.errors.append("trading_hours must have 'start' and 'end' fields")
    
    def _validate_product_type(self, config: Dict):
        """Validate product type"""
        product_type = config.get('product_type')
        if product_type and product_type not in ['MIS', 'NRML']:
            self.warnings.append(f"Unknown product type: {product_type} (should be MIS or NRML)")
    
    def print_results(self):
        """Print validation results"""
        print("\n" + "="*70)
        
        # Info
        if self.info:
            print("\n📋 CONFIGURATION INFO:")
            for msg in self.info:
                print(f"   {msg}")
        
        # Warnings
        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for msg in self.warnings:
                print(f"   • {msg}")
        
        # Errors
        if self.errors:
            print("\n❌ ERRORS:")
            for msg in self.errors:
                print(f"   • {msg}")
        else:
            print("\n✅ VALIDATION PASSED")
        
        print("="*70)


def validate_all_configurations():
    """Validate all configuration files"""
    print("\n" + "="*70)
    print("INDIAN MARKET TRADING BOT - CONFIGURATION DEPLOYMENT")
    print("="*70)
    
    configs = [
        'config_nifty_futures.json',
        'config_banknifty_futures.json',
        'config_equity_intraday.json',
        'config_options_trading.json'
    ]
    
    validator = ConfigurationValidator()
    results = {}
    
    for config_file in configs:
        print(f"\n\n🔍 Validating: {config_file}")
        is_valid, config = validator.validate_config(config_file)
        validator.print_results()
        results[config_file] = {
            'valid': is_valid,
            'config': config,
            'errors': validator.errors.copy(),
            'warnings': validator.warnings.copy()
        }
    
    # Summary
    print("\n\n" + "="*70)
    print("DEPLOYMENT SUMMARY")
    print("="*70)
    
    valid_count = sum(1 for r in results.values() if r['valid'])
    total_count = len(results)
    
    print(f"\n✅ Valid configurations: {valid_count}/{total_count}")
    
    for config_file, result in results.items():
        status = "✅ READY" if result['valid'] else "❌ NEEDS FIXES"
        print(f"   {status} - {config_file}")
    
    # Next steps
    print("\n" + "="*70)
    print("NEXT STEPS FOR TESTING")
    print("="*70)
    print("""
1. UPDATE API CREDENTIALS:
   • Edit each config file
   • Replace 'YOUR_KITE_API_KEY_HERE' with your actual Kite API key
   • Get API key from: https://kite.trade/

2. UPDATE SYMBOLS (for futures/options):
   • Check current expiry dates
   • Update symbol names to current/next month contracts
   • Example: NIFTY24JANFUT → NIFTY24FEBFUT (if January expired)

3. AUTHENTICATE WITH KITE:
   • Run: python kite_login.py
   • This generates kite_token.json (valid for 1 day)
   • Must be run daily before trading

4. TEST WITH PAPER TRADING:
   • Copy a config: cp config_nifty_futures.json test_config.json
   • Edit test_config.json and add: "paper_trading": true
   • Run: python validate_paper_trading.py --config test_config.json

5. VALIDATE INSTRUMENTS:
   • Run: python validate_instruments.py --config test_config.json
   • This checks if symbols exist and are tradable

6. START PAPER TRADING:
   • Run: python run_bot.py --config test_config.json
   • Monitor for 1-2 days
   • Check logs for signals and simulated trades

7. GO LIVE (after successful paper trading):
   • Edit config and set: "paper_trading": false
   • Start with small position sizes (reduce risk_percent to 0.5%)
   • Run: python run_bot.py --config your_config.json
   • Monitor closely for first few trades

8. DOCUMENTATION:
   • Read: examples/README_CONFIGURATIONS.md (comprehensive guide)
   • Read: examples/CONFIGURATION_SELECTOR.md (choose right config)
   • Read: MIGRATION_GUIDE.md (migration from MT5)
   • Read: INDIAN_MARKET_CONFIGS_README.md (quick reference)
""")
    
    print("="*70)
    print("\n✨ Configuration deployment validation complete!")
    print("📚 For detailed documentation, see examples/README_CONFIGURATIONS.md")
    print("🚀 Ready to start testing with paper trading mode!\n")
    
    return results


def create_test_config():
    """Create a test configuration for immediate testing"""
    print("\n" + "="*70)
    print("CREATING TEST CONFIGURATION")
    print("="*70)
    
    # Load NIFTY futures config as base
    with open('config_nifty_futures.json', 'r') as f:
        config = json.load(f)
    
    # Modify for testing
    config['paper_trading'] = True
    config['risk_percent'] = 0.5  # Very conservative for testing
    config['max_trades_per_day'] = 3  # Limit trades during testing
    config['max_positions'] = 1  # Single position for testing
    
    # Add testing notes
    config['_testing_notes'] = [
        "This is a TEST configuration with paper trading enabled",
        "No real trades will be placed",
        "All orders are simulated",
        "Use this to validate the bot before going live",
        "Monitor logs for signals and simulated trades",
        "After successful testing, copy to production config and disable paper_trading"
    ]
    
    # Save test config
    test_config_path = 'config_test_paper_trading.json'
    with open(test_config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n✅ Created: {test_config_path}")
    print("\nTest configuration features:")
    print("   • Paper trading: ENABLED (no real trades)")
    print("   • Risk per trade: 0.5% (very conservative)")
    print("   • Max trades/day: 3 (limited for testing)")
    print("   • Max positions: 1 (simple testing)")
    print("\nTo test:")
    print(f"   1. Update API key in {test_config_path}")
    print("   2. Run: python kite_login.py")
    print(f"   3. Run: python validate_paper_trading.py --config {test_config_path}")
    print(f"   4. Run: python run_bot.py --config {test_config_path}")
    
    print("="*70)


def check_documentation():
    """Check if all documentation files exist"""
    print("\n" + "="*70)
    print("DOCUMENTATION CHECK")
    print("="*70)
    
    docs = {
        'examples/README_CONFIGURATIONS.md': 'Comprehensive configuration guide',
        'examples/CONFIGURATION_SELECTOR.md': 'Configuration selection tool',
        'MIGRATION_GUIDE.md': 'MT5 to Indian market migration guide',
        'INDIAN_MARKET_CONFIGS_README.md': 'Quick reference for Indian configs',
        'config_nifty_futures.json': 'NIFTY futures configuration',
        'config_banknifty_futures.json': 'BANKNIFTY futures configuration',
        'config_equity_intraday.json': 'Equity intraday configuration',
        'config_options_trading.json': 'Options trading configuration'
    }
    
    all_exist = True
    for doc_path, description in docs.items():
        exists = os.path.exists(doc_path)
        status = "✅" if exists else "❌"
        print(f"{status} {doc_path}")
        print(f"   {description}")
        if not exists:
            all_exist = False
    
    print("\n" + "="*70)
    if all_exist:
        print("✅ All documentation files are present!")
    else:
        print("⚠️  Some documentation files are missing")
    
    return all_exist


if __name__ == '__main__':
    print("\n🚀 Starting configuration deployment and validation...\n")
    
    # Check documentation
    check_documentation()
    
    # Validate all configurations
    results = validate_all_configurations()
    
    # Create test configuration
    create_test_config()
    
    print("\n" + "="*70)
    print("🎉 DEPLOYMENT COMPLETE!")
    print("="*70)
    print("\n📖 Next: Read examples/README_CONFIGURATIONS.md for detailed guide")
    print("🧪 Test: Run paper trading with config_test_paper_trading.json")
    print("🚀 Deploy: Update API keys and start testing!\n")
