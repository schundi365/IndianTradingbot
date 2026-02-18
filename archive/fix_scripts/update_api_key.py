#!/usr/bin/env python3
"""
API Key Update Script

Helps update the Kite API key in all configuration files.
"""

import json
import os
import glob

def update_api_key_in_file(filepath, api_key):
    """Update API key in a single configuration file"""
    try:
        with open(filepath, 'r') as f:
            config = json.load(f)
        
        old_key = config.get('kite_api_key', '')
        config['kite_api_key'] = api_key
        
        with open(filepath, 'w') as f:
            json.dump(config, f, indent=2)
        
        return True, old_key
    except Exception as e:
        return False, str(e)

def main():
    print("\n" + "="*70)
    print("KITE API KEY UPDATE UTILITY")
    print("="*70 + "\n")
    
    # Get API key from user
    print("📝 Enter your Kite Connect API Key")
    print("   (Get it from: https://kite.trade/)\n")
    
    api_key = input("API Key: ").strip()
    
    if not api_key:
        print("\n❌ No API key provided. Exiting.")
        return
    
    if api_key == "YOUR_KITE_API_KEY_HERE":
        print("\n⚠️  Warning: You entered the placeholder key.")
        print("   Please enter your actual API key from https://kite.trade/")
        return
    
    # Confirm
    print(f"\n🔍 API Key: {api_key[:4]}...{api_key[-4:] if len(api_key) > 8 else ''}")
    confirm = input("\nUpdate all configuration files with this key? (yes/no): ").strip().lower()
    
    if confirm not in ['yes', 'y']:
        print("\n❌ Update cancelled.")
        return
    
    # Find all config files
    config_files = glob.glob("config_*.json")
    
    if not config_files:
        print("\n⚠️  No configuration files found.")
        return
    
    print(f"\n📦 Found {len(config_files)} configuration files:")
    for f in config_files:
        print(f"   • {f}")
    
    print("\n🔄 Updating API keys...\n")
    
    # Update each file
    success_count = 0
    for filepath in config_files:
        success, old_key = update_api_key_in_file(filepath, api_key)
        
        if success:
            status = "✅"
            success_count += 1
            if old_key == "YOUR_KITE_API_KEY_HERE":
                change = "Updated from placeholder"
            elif old_key == api_key:
                change = "Already up to date"
            else:
                change = "Updated from previous key"
        else:
            status = "❌"
            change = f"Error: {old_key}"
        
        print(f"{status} {filepath:40s} - {change}")
    
    # Summary
    print("\n" + "="*70)
    if success_count == len(config_files):
        print("✅ SUCCESS: All configuration files updated!")
        print(f"\n   Updated {success_count}/{len(config_files)} files")
        print("\n🚀 Next Steps:")
        print("   1. Run: python kite_login.py")
        print("   2. Run: python test_configuration.py --config config_test_paper_trading.json")
        print("   3. Run: python run_bot.py --config config_test_paper_trading.json")
    else:
        print(f"⚠️  WARNING: Updated {success_count}/{len(config_files)} files")
        print("   Some files failed to update. Check errors above.")
    
    print("="*70 + "\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Update cancelled by user.")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
