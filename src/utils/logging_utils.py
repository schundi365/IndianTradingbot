"""
Logging utilities for Windows console compatibility
Strips Unicode emojis that cause encoding errors on Windows cp1252
"""

import re
import logging
import os
from pathlib import Path


# Emoji to ASCII mapping for common trading bot emojis
EMOJI_MAP = {
    '✅': '[OK]',
    '❌': '[X]',
    '⚠️': '[!]',
    '🎯': '[TARGET]',
    '📊': '[CHART]',
    '📈': '[UP]',
    '📉': '[DOWN]',
    '💰': '[MONEY]',
    '🤖': '[BOT]',
    '⚡': '[SIGNAL]',
    '🔍': '[SEARCH]',
    '🧪': '[TEST]',
    '🔧': '[CONFIG]',
    '💎': '[GEM]',
    '₹': 'Rs.',
    '🚫': '[BLOCKED]',
    '⏱️': '[TIME]',
    '🔗': '[LINK]',
    '🔄': '[REFRESH]',
    '═': '=',
    '║': '|',
    '╔': '+',
    '╗': '+',
    '╚': '+',
    '╝': '+',
    '🚀': '[START]',
    '📉': '[DOWN]',
    '📈': '[UP]',
    '💰': '[PROFIT]',
    '💸': '[LOSS]',
    '🔒': '[LOCKED]',
}


# Global flag to disable safe logging if the environment supports UTF-8
DISABLE_SAFE_LOGGING = False

def strip_emojis(text):
    """
    Replace emojis with ASCII equivalents for Windows console compatibility
    
    Args:
        text: String that may contain emojis
        
    Returns:
        String with emojis replaced by ASCII equivalents
    """
    if DISABLE_SAFE_LOGGING:
        return text
        
    if not isinstance(text, str):
        return text
    
    # Replace known emojis
    for emoji, replacement in EMOJI_MAP.items():
        text = text.replace(emoji, replacement)
    
    # Remove any remaining emojis (Unicode ranges for emojis)
    # This regex covers most emoji ranges
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U00002600-\U000026FF"  # Miscellaneous Symbols
        "\U00002700-\U000027BF"  # Dingbats
        "]+",
        flags=re.UNICODE
    )
    
    text = emoji_pattern.sub('', text)
    
    return text


class SafeFormatter(logging.Formatter):
    """
    Custom formatter that strips emojis before formatting
    """
    
    def format(self, record):
        # Format the record first
        formatted = super().format(record)
        
        # Strip emojis from the formatted message
        return strip_emojis(formatted)


def configure_safe_logging():
    """
    Configure logging to use SafeFormatter for all handlers in all loggers
    Call this at the start of your application and after initializing key components
    """
    # Configure root logger
    _apply_safe_formatter(logging.getLogger())
    
    # Configure all other loggers
    for logger_name in logging.Logger.manager.loggerDict:
        logger = logging.getLogger(logger_name)
        _apply_safe_formatter(logger)


def _apply_safe_formatter(logger):
    """Internal helper to apply SafeFormatter to a logger's handlers"""
    for handler in logger.handlers:
        # Don't apply safe formatter to DatabaseHandler as it handles UTF-8 correctly
        from src.utils.db_logging_handler import DatabaseHandler
        if isinstance(handler, DatabaseHandler):
            continue
            
        if not isinstance(handler.formatter, SafeFormatter):
            # Get the current format string
            fmt = handler.formatter._fmt if (handler.formatter and hasattr(handler.formatter, '_fmt')) else '%(asctime)s - %(levelname)s - %(message)s'
            datefmt = handler.formatter.datefmt if (handler.formatter and hasattr(handler.formatter, 'datefmt')) else None
            
            # Replace with SafeFormatter
            handler.setFormatter(SafeFormatter(fmt, datefmt))


def setup_db_logging(db_path: str = "data/logs.db"):
    """
    Setup database logging handler and attach it to the root logger.
    
    Args:
        db_path: Path to the SQLite database
    """
    from src.utils.db_logging_handler import DatabaseHandler
    
    root_logger = logging.getLogger()
    
    # Check if already attached
    for handler in root_logger.handlers:
        if isinstance(handler, DatabaseHandler):
            return handler
            
    # Create and add handler
    db_handler = DatabaseHandler(db_path)
    db_handler.setLevel(logging.DEBUG)  # Capture everything; filtering happens in dashboard
    
    # Use standard formatter for DB (no emoji stripping)
    formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    db_handler.setFormatter(formatter)
    
    root_logger.addHandler(db_handler)
    return db_handler
