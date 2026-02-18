#!/usr/bin/env python3
"""
Prepare Repository for GitHub

This script:
1. Creates template configuration files (without API keys)
2. Lists files that should be deleted
3. Updates .gitignore
4. Creates a clean README
"""

import json
import glob
import os
from pathlib import Path

def create_config_templates():
    """Create template configuration files"""
    print("\n" + "="*70)
    print("CREATING CONFIGURATION TEMPLATES")
    print("="*70 + "\n")
    
    config_files = glob.glob("config_*.json")
    
    for config_file in config_files:
        # Skip if already a template
        if config_file.endswith('.template'):
            continue
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Replace API key with placeholder
            if 'kite_api_key' in config:
                config['kite_api_key'] = "YOUR_KITE_API_KEY_HERE"
            
            # Create template file
            template_file = config_file + '.template'
            with open(template_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"✅ Created: {template_file}")
        
        except Exception as e:
            print(f"❌ Error processing {config_file}: {e}")
    
    print("\n" + "="*70)

def list_files_to_delete():
    """List files that should be deleted before GitHub push"""
    print("\n" + "="*70)
    print("FILES TO DELETE (contain sensitive data or are temporary)")
    print("="*70 + "\n")
    
    files_to_delete = [
        # Sensitive files
        "kite_token.json",
        
        # Config files with API keys (keep templates only)
        "config_nifty_futures.json",
        "config_banknifty_futures.json",
        "config_equity_intraday.json",
        "config_options_trading.json",
        "config_test_paper_trading.json",
        "config_paper_trading.json",
        "config_indian_migrated.json",
        "bot_config.json",
        
        # Log files
        "*.log",
        "indian_trading_bot.log",
        "trading_bot.log",
        "test_trading_decisions.log",
        
        # Hypothesis testing data
        ".hypothesis/",
        
        # Temporary/test files
        "mock_mt5.py",
        "test_*.html",
        "simple_*.py",
        
        # Backup files
        "bot_config_backup_*.json",
        "config_backup_*.json",
        
        # Build artifacts
        "build/",
        "dist/",
        "__pycache__/",
        "*.pyc",
        ".pytest_cache/",
        "cachedir/",
        
        # IDE files
        ".vscode/",
        ".idea/",
        
        # Unnecessary documentation (keep main docs only)
        "SESSION_*.txt",
        "SESSION_*.md",
        "TASK_*.md",
        "*_SUMMARY.txt",
        "*_STATUS.txt",
        "*_COMPLETE.txt",
        "*_FIX*.txt",
        "*_IMPLEMENTATION*.md",
        "*_ANALYSIS*.txt",
        "*_GUIDE.txt",
        "*_REFERENCE*.txt",
    ]
    
    print("Delete these files/patterns before pushing to GitHub:\n")
    for pattern in files_to_delete:
        print(f"   • {pattern}")
    
    print("\n" + "="*70)

def list_files_to_keep():
    """List important files that should be kept"""
    print("\n" + "="*70)
    print("FILES TO KEEP (essential for the project)")
    print("="*70 + "\n")
    
    files_to_keep = [
        # Core source files
        "src/broker_adapter.py",
        "src/kite_adapter.py",
        "src/indian_trading_bot.py",
        "src/paper_trading.py",
        "src/error_handler.py",
        "src/trading_decision_logger.py",
        "src/instrument_validator.py",
        "src/config_migration.py",
        
        # Authentication
        "kite_login.py",
        
        # Configuration templates
        "config_*.json.template",
        
        # Utility scripts
        "update_api_key.py",
        "check_api_key.py",
        "test_configuration.py",
        "deploy_configurations.py",
        "verify_deployment.py",
        "validate_paper_trading.py",
        "validate_instruments.py",
        "prepare_for_github.py",
        
        # Documentation
        "README.md",
        "README_INDIAN_MARKET.md",
        "QUICK_START_TESTING.md",
        "COMPLETE_SETUP_GUIDE.md",
        "TESTING_GUIDE.md",
        "MIGRATION_GUIDE.md",
        "INDIAN_MARKET_CONFIGS_README.md",
        "PORT_CHANGE_NOTICE.md",
        "FIX_API_KEY_ERROR.md",
        "DEPLOYMENT_SUMMARY.md",
        "examples/README_CONFIGURATIONS.md",
        "examples/CONFIGURATION_SELECTOR.md",
        
        # Tests
        "tests/test_*.py",
        
        # Project files
        ".gitignore",
        "requirements.txt",
        "LICENSE",
        
        # Spec files
        ".kiro/specs/indian-market-broker-integration/requirements.md",
        ".kiro/specs/indian-market-broker-integration/design.md",
        ".kiro/specs/indian-market-broker-integration/tasks.md",
    ]
    
    print("Keep these files (essential):\n")
    for file in files_to_keep:
        print(f"   ✅ {file}")
    
    print("\n" + "="*70)

def create_setup_instructions():
    """Create setup instructions for users"""
    print("\n" + "="*70)
    print("SETUP INSTRUCTIONS FOR USERS")
    print("="*70 + "\n")
    
    instructions = """
After cloning the repository, users should:

1. Copy template configs:
   cp config_nifty_futures.json.template config_nifty_futures.json
   cp config_banknifty_futures.json.template config_banknifty_futures.json
   cp config_equity_intraday.json.template config_equity_intraday.json
   cp config_options_trading.json.template config_options_trading.json
   cp config_test_paper_trading.json.template config_test_paper_trading.json

2. Update API keys:
   python update_api_key.py

3. Edit kite_login.py:
   - Add API_KEY
   - Add API_SECRET

4. Authenticate:
   python kite_login.py

5. Start testing:
   python run_bot.py --config config_test_paper_trading.json
"""
    
    print(instructions)
    print("="*70)

def main():
    print("\n" + "="*70)
    print("PREPARE REPOSITORY FOR GITHUB")
    print("="*70)
    
    # Create template configs
    create_config_templates()
    
    # List files to delete
    list_files_to_delete()
    
    # List files to keep
    list_files_to_keep()
    
    # Setup instructions
    create_setup_instructions()
    
    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print("""
1. Review the files listed above
2. Delete sensitive/temporary files
3. Keep only essential files and templates
4. Update README.md with README_INDIAN_MARKET.md content
5. Verify .gitignore is updated
6. Test that templates work:
   - Copy a template
   - Add API key
   - Run the bot
7. Commit and push to GitHub

Commands to clean up:
   # Delete config files with API keys (keep templates)
   rm config_nifty_futures.json config_banknifty_futures.json
   rm config_equity_intraday.json config_options_trading.json
   rm config_test_paper_trading.json
   
   # Delete log files
   rm *.log
   
   # Delete hypothesis data
   rm -rf .hypothesis/
   
   # Delete temporary files
   rm SESSION_*.txt SESSION_*.md TASK_*.md
   rm *_SUMMARY.txt *_STATUS.txt *_COMPLETE.txt
   
   # Delete build artifacts
   rm -rf build/ dist/ __pycache__/ .pytest_cache/ cachedir/

Then commit:
   git add .
   git commit -m "Prepare for GitHub: Remove sensitive data, add templates"
   git push origin main
""")
    print("="*70 + "\n")

if __name__ == '__main__':
    main()
