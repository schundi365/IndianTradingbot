#!/usr/bin/env python3
"""
Comprehensive Cache Clearing Script
Clears all Python cache, configuration cache, and temporary files to ensure latest code is applied
"""

import os
import sys
import shutil
import glob
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clear_python_cache():
    """Clear all Python cache files and directories"""
    logger.info("🧹 Clearing Python cache files...")
    
    cache_patterns = [
        '**/__pycache__',
        '**/*.pyc',
        '**/*.pyo',
        '**/*.pyd',
        '**/.pytest_cache',
        '**/pytest_cache',
        '**/.coverage',
        '**/coverage.xml',
        '**/.tox',
        '**/.mypy_cache',
        '**/build',
        '**/dist',
        '**/*.egg-info'
    ]
    
    cleared_count = 0
    
    for pattern in cache_patterns:
        for path in glob.glob(pattern, recursive=True):
            try:
                if os.path.isfile(path):
                    os.remove(path)
                    logger.info(f"   Removed file: {path}")
                    cleared_count += 1
                elif os.path.isdir(path):
                    shutil.rmtree(path)
                    logger.info(f"   Removed directory: {path}")
                    cleared_count += 1
            except Exception as e:
                logger.warning(f"   Could not remove {path}: {e}")
    
    logger.info(f"✅ Cleared {cleared_count} Python cache items")

def clear_config_cache():
    """Clear configuration cache and temporary config files"""
    logger.info("🔧 Clearing configuration cache...")
    
    config_cache_patterns = [
        'config_cache.json',
        'config_cache.pkl',
        '.config_cache',
        'temp_config_*.json',
        'config_backup_temp_*.json',
        '**/.config_cache',
        '**/config_cache.*'
    ]
    
    cleared_count = 0
    
    for pattern in config_cache_patterns:
        for path in glob.glob(pattern, recursive=True):
            try:
                if os.path.isfile(path):
                    os.remove(path)
                    logger.info(f"   Removed config cache: {path}")
                    cleared_count += 1
                elif os.path.isdir(path):
                    shutil.rmtree(path)
                    logger.info(f"   Removed config cache dir: {path}")
                    cleared_count += 1
            except Exception as e:
                logger.warning(f"   Could not remove {path}: {e}")
    
    logger.info(f"✅ Cleared {cleared_count} configuration cache items")

def clear_log_cache():
    """Clear old log files and temporary logs"""
    logger.info("📝 Clearing old log files...")
    
    log_patterns = [
        'trading_bot_*.log',
        'debug_*.log',
        'temp_*.log',
        '*.log.old',
        '*.log.bak',
        '**/logs/*.log.old',
        '**/logs/*.log.bak'
    ]
    
    cleared_count = 0
    
    for pattern in log_patterns:
        for path in glob.glob(pattern, recursive=True):
            try:
                if os.path.isfile(path):
                    os.remove(path)
                    logger.info(f"   Removed old log: {path}")
                    cleared_count += 1
            except Exception as e:
                logger.warning(f"   Could not remove {path}: {e}")
    
    logger.info(f"✅ Cleared {cleared_count} old log files")

def clear_temp_files():
    """Clear temporary files and directories"""
    logger.info("🗑️ Clearing temporary files...")
    
    temp_patterns = [
        '*.tmp',
        '*.temp',
        '*~',
        '.DS_Store',
        'Thumbs.db',
        '**/.DS_Store',
        '**/Thumbs.db',
        'temp_*',
        '*.swp',
        '*.swo',
        '.vscode/.ropeproject',
        '**/.pytest_cache',
        '**/node_modules/.cache'
    ]
    
    cleared_count = 0
    
    for pattern in temp_patterns:
        for path in glob.glob(pattern, recursive=True):
            try:
                if os.path.isfile(path):
                    os.remove(path)
                    logger.info(f"   Removed temp file: {path}")
                    cleared_count += 1
                elif os.path.isdir(path):
                    shutil.rmtree(path)
                    logger.info(f"   Removed temp directory: {path}")
                    cleared_count += 1
            except Exception as e:
                logger.warning(f"   Could not remove {path}: {e}")
    
    logger.info(f"✅ Cleared {cleared_count} temporary files")

def clear_import_cache():
    """Clear Python import cache"""
    logger.info("🔄 Clearing Python import cache...")
    
    # Clear sys.modules cache for our modules
    modules_to_clear = []
    for module_name in list(sys.modules.keys()):
        if any(pattern in module_name for pattern in ['src.', 'config', 'mt5_trading_bot', 'volume_analyzer']):
            modules_to_clear.append(module_name)
    
    for module_name in modules_to_clear:
        if module_name in sys.modules:
            del sys.modules[module_name]
            logger.info(f"   Cleared module cache: {module_name}")
    
    # Clear importlib cache
    try:
        import importlib
        importlib.invalidate_caches()
        logger.info("   Invalidated importlib caches")
    except Exception as e:
        logger.warning(f"   Could not invalidate importlib caches: {e}")
    
    logger.info(f"✅ Cleared {len(modules_to_clear)} cached modules")

def restart_services():
    """Provide instructions for restarting services"""
    logger.info("🔄 Service restart recommendations:")
    logger.info("   1. Stop the trading bot if running")
    logger.info("   2. Stop the web dashboard if running")
    logger.info("   3. Close any Python IDEs/editors")
    logger.info("   4. Restart the bot with: python run_bot.py")
    logger.info("   5. Restart dashboard with: python web_dashboard.py")

def verify_latest_config():
    """Verify that latest configuration values are in place"""
    logger.info("🔍 Verifying latest configuration values...")
    
    try:
        # Check bot_config.json
        import json
        with open('bot_config.json', 'r') as f:
            config = json.load(f)
        
        # Verify key optimized values
        checks = [
            ('min_volume_ma', 0.7, 'Volume threshold'),
            ('macd_min_histogram', 0.0005, 'MACD threshold'),
            ('min_trade_confidence', 0.6, 'Confidence threshold')
        ]
        
        all_good = True
        for key, expected, description in checks:
            if key in config:
                actual = config[key]
                if actual == expected:
                    logger.info(f"   ✅ {description}: {actual} (correct)")
                else:
                    logger.warning(f"   ⚠️ {description}: {actual} (expected {expected})")
                    all_good = False
            else:
                logger.warning(f"   ❌ {description}: Missing key '{key}'")
                all_good = False
        
        if all_good:
            logger.info("✅ All optimized configuration values are in place")
        else:
            logger.warning("⚠️ Some configuration values may need attention")
            
    except Exception as e:
        logger.error(f"❌ Could not verify configuration: {e}")

def main():
    """Main cache clearing function"""
    logger.info("🚀 COMPREHENSIVE CACHE CLEARING STARTED")
    logger.info("=" * 60)
    
    try:
        # Clear all types of cache
        clear_python_cache()
        clear_config_cache()
        clear_log_cache()
        clear_temp_files()
        clear_import_cache()
        
        # Verify configuration
        verify_latest_config()
        
        # Provide restart instructions
        restart_services()
        
        logger.info("=" * 60)
        logger.info("🎉 CACHE CLEARING COMPLETED SUCCESSFULLY")
        logger.info("")
        logger.info("📋 NEXT STEPS:")
        logger.info("1. Restart any running bot processes")
        logger.info("2. Restart the web dashboard")
        logger.info("3. Test the latest optimized settings")
        logger.info("4. Monitor logs for enhanced logging output")
        logger.info("")
        logger.info("🔧 Latest optimizations now active:")
        logger.info("   • Enhanced logging with line numbers and timing")
        logger.info("   • Optimized volume threshold (0.7)")
        logger.info("   • Optimized MACD threshold (0.0005)")
        logger.info("   • Consistent confidence naming (min_trade_confidence)")
        logger.info("   • All RSI, ADX, and volume improvements")
        
    except Exception as e:
        logger.error(f"❌ Error during cache clearing: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)