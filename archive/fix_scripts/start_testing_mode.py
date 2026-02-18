"""
Automated Testing Mode
Applies aggressive testing config, monitors trades, and can revert when done
"""
import json
import shutil
from datetime import datetime
import os

print("="*80)
print("TRADING BOT - TESTING MODE")
print("="*80)
print()

# Backup current config
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = f"config_backups/config_backup_testing_{timestamp}.json"

print(f"📦 Backing up current config to: {backup_file}")
shutil.copy("bot_config.json", backup_file)
print("✅ Backup created")
print()

# Load testing config
print("📋 Loading testing configuration...")
with open("config_testing_mode.json", "r") as f:
    testing_config = json.load(f)

# Update timestamp
testing_config["last_updated"] = datetime.now().isoformat()

# Save as active config
with open("bot_config.json", "w") as f:
    json.dump(testing_config, f, indent=4)

print("✅ Testing configuration applied!")
print()

print("="*80)
print("TESTING MODE ACTIVE")
print("="*80)
print()
print("Configuration:")
print(f"  Symbols: {len(testing_config['symbols'])} ({', '.join(testing_config['symbols'][:4])}...)")
print(f"  Fast MA: {testing_config['fast_ma_period']}")
print(f"  Slow MA: {testing_config['slow_ma_period']}")
print(f"  Min Confidence: {testing_config['min_confidence']*100}%")
print(f"  RSI Thresholds: {testing_config['rsi_oversold']}/{testing_config['rsi_overbought']}")
print(f"  MACD Filter: {'Enabled' if testing_config['use_macd'] else 'Disabled'}")
print(f"  Volume Filter: {'Enabled' if testing_config['use_volume_filter'] else 'Disabled'}")
print(f"  Max Daily Trades: {testing_config['max_daily_trades']}")
print()

print("Expected Results:")
print("  ⚡ 10-30 crossovers per hour")
print("  ⚡ Most signals will be accepted")
print("  ⚡ Trades should appear within 5-10 minutes")
print()

print("="*80)
print("NEXT STEPS")
print("="*80)
print()
print("1. Start the bot:")
print("   python start_dashboard.py")
print()
print("2. Watch the logs for trades")
print()
print("3. Monitor dashboard: http://localhost:5000")
print()
print("4. When done testing, restore safe config:")
print(f"   copy {backup_file} bot_config.json")
print()

print("="*80)
print("⚠️  WARNING: TESTING MODE IS AGGRESSIVE")
print("="*80)
print()
print("This configuration is designed for TESTING ONLY!")
print("- Very permissive filters")
print("- Many symbols")
print("- Fast MA periods")
print()
print("DO NOT use for real trading with large lot sizes!")
print()

print("="*80)
print("Ready to start testing! 🚀")
print("="*80)
print()

# Ask if user wants to start bot automatically
response = input("Start bot now? (y/n): ").strip().lower()
if response == 'y':
    print()
    print("Starting bot...")
    os.system("python start_dashboard.py")
else:
    print()
    print("Bot not started. Run manually when ready:")
    print("  python start_dashboard.py")
