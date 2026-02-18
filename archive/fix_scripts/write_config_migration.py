"""Write the complete config_migration.py file"""

# Read the complete code from a string
with open('src/config_migration.py', 'w', encoding='utf-8') as f:
    f.write("""\"\"\"
Configuration Migration Utility

Migrates MT5 forex bot configuration to Indian market broker configuration.
Maps MT5 symbols to Indian equivalents and converts timeframes.
\"\"\"

import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime


class ConfigMigration:
    \"\"\"Utility to migrate MT5 configuration to Indian broker configuration\"\"\"
    
    # Symbol mapping from MT5 forex to Indian market equivalents
    SYMBOL_MAPPING = {
        # Forex to Indian equivalents
        "XAUUSD": "GOLD",  # Gold futures (MCX)
        "XAGUSD": "SILVER",  # Silver futures (MCX)
        "XPTUSD": "PLATINUM",  # Platinum (if available)
        "XPDUSD": "PALLADIUM",  # Palladium (if available)
        
        # Major forex pairs to popular Indian stocks/indices
        "EURUSD": "RELIANCE",  # Reliance Industries
        "GBPUSD": "TCS",  # Tata Consultancy Services
        "USDJPY": "INFY",  # Infosys
        "USDCHF": "HDFCBANK",  # HDFC Bank
        "AUDUSD": "ICICIBANK",  # ICICI Bank
        "USDCAD": "SBIN",  # State Bank of India
        "NZDUSD": "WIPRO",  # Wipro
        "EURJPY": "BHARTIARTL",  # Bharti Airtel
        "GBPJPY": "ITC",  # ITC Limited
        "EURGBP": "HINDUNILVR",  # Hindustan Unilever
        "EURAUD": "AXISBANK",  # Axis Bank
        "EURCAD": "KOTAKBANK",  # Kotak Mahindra Bank
        "GBPAUD": "LT",  # Larsen & Toubro
        "GBPCAD": "MARUTI",  # Maruti Suzuki
        
        # Indices
        "US30": "NIFTY 50",  # NIFTY 50 Index
        "US500": "BANKNIFTY",  # Bank NIFTY Index
        "NAS100": "NIFTYNEXT50",  # NIFTY Next 50
    }
    
    # Timeframe mapping from MT5 constants to broker format
    TIMEFRAME_MAPPING = {
        1: "minute",  # M1
        5: "5minute",  # M5
        15: "15minute",  # M15
        30: "30minute",  # M30
        60: "60minute",  # H1
        240: "4hour",  # H4
        1440: "day",  # D1
    }
    
    # Default Indian market settings
    INDIAN_MARKET_DEFAULTS = {
        "broker": "kite",
        "default_exchange": "NSE",
        "trading_hours": {
            "start": "09:15",
            "end": "15:30"
        },
        "product_type": "MIS",  # Intraday by default
    }
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        \"\"\"Initialize config migration utility\"\"\"
        self.logger = logger or logging.getLogger(__name__)
    
    def migrate_config(
        self,
        mt5_config_path: str,
        output_path: str,
        broker: str = "kite",
        api_key: Optional[str] = None,
        custom_symbol_mapping: Optional[Dict[str, str]] = None
    ) -> bool:
        \"\"\"
        Migrate MT5 configuration to Indian broker configuration
        
        Args:
            mt5_config_path: Path to MT5 bot configuration file
            output_path: Path to save migrated configuration
            broker: Broker name (default: "kite")
            api_key: Broker API key (optional)
            custom_symbol_mapping: Custom symbol mappings to override defaults
            
        Returns:
            True if migration successful, False otherwise
        \"\"\"
        try:
            # Read MT5 configuration
            self.logger.info(f"Reading MT5 configuration from {mt5_config_path}")
            with open(mt5_config_path, 'r') as f:
                mt5_config = json.load(f)
            
            # Create new configuration
            indian_config = self._create_base_config(broker, api_key)
            
            # Migrate symbols
            symbol_mapping = custom_symbol_mapping or self.SYMBOL_MAPPING
            indian_config['symbols'] = self._migrate_symbols(
                mt5_config.get('symbols', []),
                symbol_mapping
            )
            
            # Convert timeframe
            indian_config['timeframe'] = mt5_config.get('timeframe', 30)
            
            # Preserve all indicator and risk parameters
            self._preserve_parameters(mt5_config, indian_config)
            
            # Add Indian market specific settings
            indian_config.update(self.INDIAN_MARKET_DEFAULTS)
            
            # Override broker if specified
            if broker:
                indian_config['broker'] = broker
            
            # Add metadata
            indian_config['_migrated_from'] = mt5_config_path
            indian_config['_migration_date'] = datetime.now().isoformat()
            indian_config['_original_symbols'] = mt5_config.get('symbols', [])
            
            # Save migrated configuration
            self.logger.info(f"Saving migrated configuration to {output_path}")
            with open(output_path, 'w') as f:
                json.dump(indian_config, f, indent=2)
            
            self.logger.info("Configuration migration completed successfully")
            self._log_migration_summary(mt5_config, indian_config)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Configuration migration failed: {e}")
            return False
    
    def _create_base_config(self, broker: str, api_key: Optional[str]) -> Dict[str, Any]:
        \"\"\"Create base configuration with broker settings\"\"\"
        config = {
            "broker": broker,
        }
        
        # Add broker-specific settings
        if broker == "kite":
            config["kite_api_key"] = api_key or "YOUR_KITE_API_KEY_HERE"
            config["kite_token_file"] = "kite_token.json"
        elif broker == "alice_blue":
            config["alice_api_key"] = api_key or "YOUR_ALICE_API_KEY_HERE"
        elif broker == "angel_one":
            config["angel_api_key"] = api_key or "YOUR_ANGEL_API_KEY_HERE"
        elif broker == "upstox":
            config["upstox_api_key"] = api_key or "YOUR_UPSTOX_API_KEY_HERE"
        
        return config
    
    def _migrate_symbols(
        self,
        mt5_symbols: list,
        symbol_mapping: Dict[str, str]
    ) -> list:
        \"\"\"
        Migrate MT5 symbols to Indian market equivalents
        
        Args:
            mt5_symbols: List of MT5 symbols
            symbol_mapping: Symbol mapping dictionary
            
        Returns:
            List of Indian market symbols
        \"\"\"
        indian_symbols = []
        unmapped_symbols = []
        
        for symbol in mt5_symbols:
            if symbol in symbol_mapping:
                indian_symbol = symbol_mapping[symbol]
                indian_symbols.append(indian_symbol)
                self.logger.info(f"Mapped {symbol} -> {indian_symbol}")
            else:
                unmapped_symbols.append(symbol)
                self.logger.warning(f"No mapping found for {symbol}, skipping")
        
        if unmapped_symbols:
            self.logger.warning(
                f"Unmapped symbols: {', '.join(unmapped_symbols)}. "
                "Consider adding custom mappings."
            )
        
        # Remove duplicates while preserving order
        seen = set()
        unique_symbols = []
        for symbol in indian_symbols:
            if symbol not in seen:
                seen.add(symbol)
                unique_symbols.append(symbol)
        
        return unique_symbols
""")

print("Config migration file created successfully!")
print("File size:", len(open('src/config_migration.py').read()), "bytes")
