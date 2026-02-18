"""Append remaining methods to config_migration.py"""

with open('src/config_migration.py', 'a', encoding='utf-8') as f:
    f.write("""
    
    def _preserve_parameters(
        self,
        mt5_config: Dict[str, Any],
        indian_config: Dict[str, Any]
    ) -> None:
        \"\"\"Preserve all indicator and risk parameters from MT5 config\"\"\"
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
        \"\"\"Migrate scalp TP caps with symbol mapping\"\"\"
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
        \"\"\"Log summary of migration\"\"\"
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
        \"\"\"Convert timeframe in minutes to broker-specific format\"\"\"
        return self.TIMEFRAME_MAPPING.get(timeframe_minutes, f"{timeframe_minutes}minute")
    
    def get_symbol_mapping(self, mt5_symbol: str) -> Optional[str]:
        \"\"\"Get Indian market equivalent for MT5 symbol\"\"\"
        return self.SYMBOL_MAPPING.get(mt5_symbol)
    
    def add_custom_mapping(self, mt5_symbol: str, indian_symbol: str) -> None:
        \"\"\"Add custom symbol mapping\"\"\"
        self.SYMBOL_MAPPING[mt5_symbol] = indian_symbol
        self.logger.info(f"Added custom mapping: {mt5_symbol} -> {indian_symbol}")


def main():
    \"\"\"Example usage of ConfigMigration\"\"\"
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
        print("\\nMigration completed successfully!")
        print("Please review config_indian_migrated.json and update:")
        print("1. Broker API key")
        print("2. Symbol mappings (if needed)")
        print("3. Trading hours (if different)")
        print("4. Product type (MIS for intraday, NRML for delivery)")
    else:
        print("\\nMigration failed. Check logs for details.")


if __name__ == '__main__':
    main()
""")

print("Appended remaining methods successfully!")
print("Final file size:", len(open('src/config_migration.py').read()), "bytes")
