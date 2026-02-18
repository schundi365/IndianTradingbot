"""Script to create config_migration.py file"""

code = '''"""
Configuration Migration Utility

Migrates MT5 forex bot configuration to Indian market broker configuration.
Maps MT5 symbols to Indian equivalents and converts timeframes.
"""

import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime


class ConfigMigration:
    """Utility to migrate MT5 configuration to Indian broker configuration"""
    
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
        """Initialize config migration utility"""
        self.logger = logger or logging.getLogger(__name__)
'''

with open('src/config_migration.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Part 1 written")
