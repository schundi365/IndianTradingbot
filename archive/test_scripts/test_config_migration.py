"""Test configuration migration utility"""

import logging
from src.config_migration import ConfigMigration

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Create migrator
migrator = ConfigMigration()

# Migrate configuration
print("Starting migration...")
success = migrator.migrate_config(
    mt5_config_path='bot_config.json',
    output_path='config_indian_migrated.json',
    broker='kite',
    api_key=None
)

if success:
    print("\n" + "="*60)
    print("Migration completed successfully!")
    print("="*60)
    print("\nPlease review config_indian_migrated.json and update:")
    print("1. Broker API key (kite_api_key)")
    print("2. Symbol mappings (if needed)")
    print("3. Trading hours (if different from 09:15-15:30)")
    print("4. Product type (MIS for intraday, NRML for delivery)")
    print("5. Exchange (NSE/BSE/NFO/MCX)")
else:
    print("\nMigration failed. Check logs for details.")
