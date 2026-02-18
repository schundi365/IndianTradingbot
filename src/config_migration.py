"""
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
    
    def migrate_config(
        self,
        mt5_config_path: str,
        output_path: str,
        broker: str = "kite",
        api_key: Optional[str] = None,
        custom_symbol_mapping: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Migrate MT5 configuration to Indian broker configuration
        
        Args:
            mt5_config_path: Path to MT5 bot configuration file
            output_path: Path to save migrated configuration
            broker: Broker name (default: "kite")
            api_key: Broker API key (optional)
            custom_symbol_mapping: Custom symbol mappings to override defaults
            
        Returns:
            True if migration successful, False otherwise
        """
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
        """Create base configuration with broker settings"""
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
        """
        Migrate MT5 symbols to Indian market equivalents
        
        Args:
            mt5_symbols: List of MT5 symbols
            symbol_mapping: Symbol mapping dictionary
            
        Returns:
            List of Indian market symbols
        """
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

    
    def _preserve_parameters(
        self,
        mt5_config: Dict[str, Any],
        indian_config: Dict[str, Any]
    ) -> None:
        """Preserve all indicator and risk parameters from MT5 config"""
        # List of all parameters to preserve
        params_to_preserve = [
            # Risk management
            'risk_percent', 'reward_ratio', 'max_daily_loss_percent',
            'max_drawdown_percent', 'max_daily_loss', 'max_daily_trades',
            'max_trades_per_symbol', 'max_trades_total', 'max_lot_per_order',
            'max_positions', 'max_trades_per_day',
            # Indicators
            'fast_ma_period', 'slow_ma_period', 'atr_period', 'atr_multiplier',
            'macd_fast', 'macd_slow', 'macd_signal', 'macd_min_histogram',
            'rsi_period', 'rsi_overbought', 'rsi_oversold',
            'adx_period', 'adx_threshold', 'adx_min_strength',
            'trend_ma_period', 'ema_fast_period', 'ema_slow_period',
            'aroon_period', 'aroon_threshold',
            # Trading
            'magic_number', 'timeframe', 'lot_size',
            'use_split_orders', 'num_positions', 'tp_levels',
            'partial_close_percent', 'trail_activation', 'trail_distance',
            'enable_trailing_stop', 'enable_trailing_tp', 'trailing_tp_ratio',
            'enable_time_based_exit', 'max_hold_minutes',
            'enable_breakeven_stop', 'breakeven_atr_threshold',
            # Features
            'use_adaptive_risk', 'ml_enabled', 'use_volume_filter',
            'use_trend_detection', 'use_rsi', 'use_macd', 'use_adx',
            'use_trend_filter', 'use_scalping_mode', 'use_dynamic_tp',
            'use_dynamic_sl', 'prevent_worse_entries', 'enable_early_signals',
            'enable_mtf_confirmation', 'pattern_enabled', 'sentiment_enabled',
            'use_pip_based_sl', 'use_pip_based_tp',
            # Volume
            'min_volume_ratio', 'volume_ma_period', 'min_volume_ma',
            'obv_period', 'obv_period_short', 'obv_period_long',
            'normal_volume_ma', 'high_volume_ma', 'very_high_volume_ma',
            'volume_ma_min_period', 'volume_spike_threshold',
            # ML
            'ml_min_confidence', 'ml_require_agreement', 'ml_model_path',
            'ml_training_data_path', 'ml_auto_retrain', 'ml_retrain_frequency',
            'ml_min_training_samples', 'technical_weight', 'ml_weight',
            'sentiment_weight', 'pattern_weight', 'ml_min_agreement',
            'ml_retrain_frequency_days',
            # Pattern/Sentiment
            'pattern_min_confidence', 'pattern_lookback', 'pattern_lookback_bars',
            'sentiment_cache_duration', 'sentiment_min_confidence',
            'sentiment_cache_duration_hours', 'news_data_path',
            # Trend detection
            'trend_detection_sensitivity', 'min_trend_confidence',
            'min_swing_strength', 'structure_break_threshold',
            'min_divergence_strength', 'max_trendlines',
            'min_trendline_touches', 'trendline_angle_min',
            'trendline_angle_max', 'mtf_weight', 'mtf_alignment_threshold',
            'mtf_contradiction_penalty', 'divergence_lookback',
            'divergence_threshold',
            # Other
            'analysis_bars', 'update_interval', 'logging_level',
            'max_analysis_time_ms', 'min_trade_confidence',
            'roc_threshold', 'sl_pips', 'tp_pips'
        ]
        
        # Copy all parameters
        for param in params_to_preserve:
            if param in mt5_config:
                indian_config[param] = mt5_config[param]
        
        # Trading hours
        if mt5_config.get('enable_trading_hours', False):
            indian_config['enable_trading_hours'] = True
            indian_config['trading_start_hour'] = mt5_config.get('trading_start_hour', 9)
            indian_config['trading_end_hour'] = mt5_config.get('trading_end_hour', 15)
        
        # Hour filter
        if mt5_config.get('enable_hour_filter', False):
            indian_config['enable_hour_filter'] = True
            indian_config['dead_hours'] = mt5_config.get('dead_hours', [])
            indian_config['golden_hours'] = mt5_config.get('golden_hours', [])
        
        # Scalp TP caps
        if 'scalp_tp_caps' in mt5_config:
            indian_config['scalp_tp_caps'] = self._migrate_scalp_tp_caps(
                mt5_config['scalp_tp_caps']
            )
        
        # Version info
        indian_config['version'] = mt5_config.get('version', '1.0.0')
        indian_config['last_updated'] = datetime.now().isoformat()
    
    def _migrate_scalp_tp_caps(self, mt5_caps: Dict[str, float]) -> Dict[str, float]:
        """Migrate scalp TP caps with symbol mapping"""
        indian_caps = {}
        for symbol, cap in mt5_caps.items():
            if symbol == "DEFAULT":
                indian_caps["DEFAULT"] = cap
            elif symbol in self.SYMBOL_MAPPING:
                indian_symbol = self.SYMBOL_MAPPING[symbol]
                indian_caps[indian_symbol] = cap
        return indian_caps
    
    def _log_migration_summary(
        self,
        mt5_config: Dict[str, Any],
        indian_config: Dict[str, Any]
    ) -> None:
        """Log summary of migration"""
        self.logger.info("=" * 60)
        self.logger.info("MIGRATION SUMMARY")
        self.logger.info("=" * 60)
        self.logger.info(f"Original symbols: {len(mt5_config.get('symbols', []))}")
        self.logger.info(f"Migrated symbols: {len(indian_config.get('symbols', []))}")
        self.logger.info(f"Broker: {indian_config.get('broker')}")
        self.logger.info(f"Exchange: {indian_config.get('default_exchange')}")
        self.logger.info(f"Timeframe: {indian_config.get('timeframe')} minutes")
        self.logger.info(f"Product type: {indian_config.get('product_type')}")
        self.logger.info(f"Trading hours: {indian_config.get('trading_hours')}")
        self.logger.info("=" * 60)
    
    def convert_timeframe_to_broker_format(self, timeframe_minutes: int) -> str:
        """Convert timeframe in minutes to broker-specific format"""
        return self.TIMEFRAME_MAPPING.get(timeframe_minutes, f"{timeframe_minutes}minute")
    
    def get_symbol_mapping(self, mt5_symbol: str) -> Optional[str]:
        """Get Indian market equivalent for MT5 symbol"""
        return self.SYMBOL_MAPPING.get(mt5_symbol)
    
    def add_custom_mapping(self, mt5_symbol: str, indian_symbol: str) -> None:
        """Add custom symbol mapping"""
        self.SYMBOL_MAPPING[mt5_symbol] = indian_symbol
        self.logger.info(f"Added custom mapping: {mt5_symbol} -> {indian_symbol}")


def main():
    """Example usage of ConfigMigration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    migrator = ConfigMigration()
    
    # Example: Migrate bot_config.json to Indian market config
    success = migrator.migrate_config(
        mt5_config_path='bot_config.json',
        output_path='config_indian_migrated.json',
        broker='kite',
        api_key=None  # Will use placeholder
    )
    
    if success:
        print("\nMigration completed successfully!")
        print("Please review config_indian_migrated.json and update:")
        print("1. Broker API key")
        print("2. Symbol mappings (if needed)")
        print("3. Trading hours (if different)")
        print("4. Product type (MIS for intraday, NRML for delivery)")
    else:
        print("\nMigration failed. Check logs for details.")


if __name__ == '__main__':
    main()
