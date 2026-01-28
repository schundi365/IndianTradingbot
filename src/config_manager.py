"""
Configuration Manager for GEM Trading Bot
Handles external configuration file for executable compatibility
"""

import json
import os
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages bot configuration with external JSON file support"""
    
    def __init__(self, config_file='bot_config.json'):
        """
        Initialize configuration manager
        
        Args:
            config_file: Path to external configuration file
        """
        # Determine config file location
        if getattr(sys, 'frozen', False):
            # Running as executable - use directory where exe is located
            self.base_dir = Path(sys.executable).parent
        else:
            # Running as script - use project root
            self.base_dir = Path(__file__).parent.parent
        
        self.config_file = self.base_dir / config_file
        self.backup_dir = self.base_dir / 'config_backups'
        
        # Create backup directory if it doesn't exist
        self.backup_dir.mkdir(exist_ok=True)
        
        # Load or create configuration
        self.config = self._load_or_create_config()
    
    def _get_default_config(self):
        """Get default configuration values"""
        return {
            'symbols': ['XAUUSD', 'XAGUSD'],
            'timeframe': 30,  # M30
            'risk_percent': 1.0,
            'reward_ratio': 1.5,
            'min_confidence': 0.6,
            'max_daily_loss': 5,
            'fast_ma_period': 10,
            'slow_ma_period': 30,
            'rsi_period': 14,
            'rsi_overbought': 75,
            'rsi_oversold': 25,
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9,
            'macd_min_histogram': 0.3,
            'atr_period': 14,
            'atr_multiplier': 1.5,
            'adx_min_strength': 20,
            'use_rsi': True,
            'use_macd': True,
            'use_adx': True,
            'use_trend_filter': False,
            'trend_ma_period': 100,
            'enable_trading_hours': False,
            'trading_start_hour': 0,
            'trading_end_hour': 23,
            'avoid_news_trading': False,
            'news_buffer_minutes': 30,
            'use_split_orders': True,
            'num_positions': 3,
            'tp_level_1': 1.0,
            'tp_level_2': 1.5,
            'tp_level_3': 2.5,
            'max_trades_total': 20,
            'max_trades_per_symbol': 5,
            'enable_trailing_stop': True,
            'trail_activation': 1.0,
            'trail_distance': 0.8,
            'use_adaptive_risk': True,
            'max_risk_multiplier': 2.0,
            'min_risk_multiplier': 0.5,
            'max_drawdown_percent': 15,
            'max_daily_trades': 50,
            'version': '2.1.0',
            'last_updated': datetime.now().isoformat()
        }
    
    def _load_or_create_config(self):
        """Load configuration from file or create default"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                logger.info(f"Configuration loaded from {self.config_file}")
                return config
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                logger.info("Creating default configuration")
                return self._create_default_config()
        else:
            logger.info("No configuration file found, creating default")
            return self._create_default_config()
    
    def _create_default_config(self):
        """Create and save default configuration"""
        config = self._get_default_config()
        self.save_config(config)
        return config
    
    def save_config(self, config=None):
        """
        Save configuration to file
        
        Args:
            config: Configuration dictionary (uses self.config if None)
        """
        if config is None:
            config = self.config
        
        # Create backup before saving
        self._create_backup()
        
        # Update timestamp
        config['last_updated'] = datetime.now().isoformat()
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            logger.info(f"Configuration saved to {self.config_file}")
            self.config = config
            return True
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False
    
    def _create_backup(self):
        """Create backup of current configuration"""
        if not self.config_file.exists():
            return
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = self.backup_dir / f'config_backup_{timestamp}.json'
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            
            logger.info(f"Configuration backup created: {backup_file}")
            
            # Keep only last 10 backups
            self._cleanup_old_backups()
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
    
    def _cleanup_old_backups(self, keep=10):
        """Keep only the most recent backups"""
        try:
            backups = sorted(self.backup_dir.glob('config_backup_*.json'))
            if len(backups) > keep:
                for backup in backups[:-keep]:
                    backup.unlink()
                    logger.info(f"Deleted old backup: {backup}")
        except Exception as e:
            logger.error(f"Failed to cleanup backups: {e}")
    
    def get_config(self):
        """Get current configuration"""
        return self.config.copy()
    
    def update_config(self, updates):
        """
        Update configuration with new values
        
        Args:
            updates: Dictionary of configuration updates
        
        Returns:
            bool: True if successful
        """
        try:
            # Validate updates
            if not self._validate_config(updates):
                logger.error("Configuration validation failed")
                return False
            
            # Update configuration
            self.config.update(updates)
            
            # Save to file
            return self.save_config()
        except Exception as e:
            logger.error(f"Failed to update config: {e}")
            return False
    
    def _validate_config(self, config):
        """
        Validate configuration values
        
        Args:
            config: Configuration dictionary to validate
        
        Returns:
            bool: True if valid
        """
        try:
            # Validate risk
            if 'risk_percent' in config:
                risk = config['risk_percent']
                if risk < 0.1 or risk > 5:
                    logger.error(f"Invalid risk: {risk}")
                    return False
            
            # Validate confidence
            if 'min_confidence' in config:
                confidence = config['min_confidence']
                if confidence < 0.2 or confidence > 0.9:
                    logger.error(f"Invalid confidence: {confidence}")
                    return False
            
            # Validate symbols
            if 'symbols' in config:
                symbols = config['symbols']
                if not symbols or len(symbols) == 0:
                    logger.error("No symbols selected")
                    return False
            
            # Validate timeframe
            if 'timeframe' in config:
                timeframe = config['timeframe']
                valid_timeframes = [1, 5, 15, 30, 16385, 16388, 16408]
                if timeframe not in valid_timeframes:
                    logger.error(f"Invalid timeframe: {timeframe}")
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False
    
    def reset_to_default(self):
        """Reset configuration to default values"""
        logger.info("Resetting configuration to default")
        self.config = self._get_default_config()
        return self.save_config()
    
    def export_config(self, export_path):
        """
        Export configuration to specified path
        
        Args:
            export_path: Path to export file
        """
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            logger.info(f"Configuration exported to {export_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to export config: {e}")
            return False
    
    def import_config(self, import_path):
        """
        Import configuration from specified path
        
        Args:
            import_path: Path to import file
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            if self._validate_config(config):
                self.config = config
                self.save_config()
                logger.info(f"Configuration imported from {import_path}")
                return True
            else:
                logger.error("Imported configuration is invalid")
                return False
        except Exception as e:
            logger.error(f"Failed to import config: {e}")
            return False


# Global configuration manager instance
import sys
_config_manager = None


def get_config_manager():
    """Get global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_config():
    """Get current configuration (compatibility function)"""
    return get_config_manager().get_config()


def update_config(updates):
    """Update configuration (compatibility function)"""
    return get_config_manager().update_config(updates)


if __name__ == "__main__":
    # Test configuration manager
    print("Testing Configuration Manager...")
    
    manager = ConfigManager('test_config.json')
    
    print("\nDefault Configuration:")
    config = manager.get_config()
    print(json.dumps(config, indent=2))
    
    print("\nUpdating configuration...")
    updates = {
        'symbols': ['XAUUSD', 'EURUSD', 'GBPUSD'],
        'risk_percent': 0.5,
        'timeframe': 16385
    }
    success = manager.update_config(updates)
    print(f"Update {'successful' if success else 'failed'}")
    
    print("\nUpdated Configuration:")
    config = manager.get_config()
    print(f"Symbols: {config['symbols']}")
    print(f"Risk: {config['risk_percent']}%")
    print(f"Timeframe: {config['timeframe']}")
    
    print("\nConfiguration file location:")
    print(f"  {manager.config_file}")
    print(f"  Exists: {manager.config_file.exists()}")
    
    print("\nBackup directory:")
    print(f"  {manager.backup_dir}")
    backups = list(manager.backup_dir.glob('config_backup_*.json'))
    print(f"  Backups: {len(backups)}")
    
    print("\n✅ Configuration Manager Test Complete!")
