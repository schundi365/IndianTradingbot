#!/usr/bin/env python3
"""
Test logging directly to see if it's working
"""

import logging
import sys
from pathlib import Path

# Determine base directory (works for both script and executable)
if getattr(sys, 'frozen', False):
    # Running as executable
    BASE_DIR = Path(sys.executable).parent
else:
    # Running as script
    BASE_DIR = Path(__file__).parent

# Log file path
LOG_FILE = BASE_DIR / 'trading_bot.log'

# Setup logging exactly like the bot
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def test_logging():
    """Test if logging is working"""
    
    print("🧪 TESTING LOGGING DIRECTLY")
    print("=" * 50)
    
    # Test basic logging
    logging.info("✅ BASIC LOGGING TEST")
    
    # Test detailed logging like in the bot
    logging.info("="*80)
    logging.info("🔧 DETAILED INDICATOR CALCULATION STARTING")
    logging.info("="*80)
    
    # Test emoji logging
    logging.info("📈 MOVING AVERAGES:")
    logging.info("   Fast MA (10 periods): 1.23456")
    logging.info("   Slow MA (30 periods): 1.23400")
    logging.info("   MA Spread: 0.00056 points")
    
    logging.info("📊 AVERAGE TRUE RANGE (ATR):")
    logging.info("   ATR Period: 14")
    logging.info("   Current ATR: 0.00123")
    
    logging.info("📈 RELATIVE STRENGTH INDEX (RSI):")
    logging.info("   RSI Period: 14")
    logging.info("   Current RSI: 65.43")
    
    logging.info("="*80)
    logging.info("✅ DETAILED INDICATOR CALCULATION COMPLETE")
    logging.info("="*80)
    
    print("✅ Logging test completed - check trading_bot.log")

if __name__ == "__main__":
    test_logging()