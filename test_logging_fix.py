import sys
import os
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

from logging_utils import configure_safe_logging
from indian_trading_bot import LOG_FILE

def test_logging():
    print(f"Original sys.stdout encoding: {sys.stdout.encoding}")
    
    # Test logging with emojis
    logging.info("Testing emojis: ✅ ❌ 🔍 🔒 🚀")
    logging.warning("Warning with emoji: ⚠️")
    
    # Create a sub-logger to simulate TradingDecisionLogger
    test_logger = logging.getLogger("test_sub")
    handler = logging.FileHandler("test_sub.log", encoding='utf-8')
    test_logger.addHandler(handler)
    
    # Re-configure to catch the new handler
    configure_safe_logging()
    
    test_logger.info("Sub-logger emoji: 🎯")
    
    print("Logging test completed without crashing.")
    print(f"Check indian_trading_bot.log and test_sub.log for UTF-8 content.")

if __name__ == "__main__":
    test_logging()
