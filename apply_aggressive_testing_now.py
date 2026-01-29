"""
Apply AGGRESSIVE testing configuration for maximum signal generation
"""
import json
from datetime import datetime

# Aggressive testing configuration
config = {
    "symbols": [
        "XAUUSD",
        "XAGUSD", 
        "EURUSD",
        "GBPUSD",
        "USDJPY",
        "AUDUSD",
        "USDCAD",
        "NZDUSD"
    ],
    "timeframe": 1,  # M1 - fastest
    "magic_number": 123456,
    "lot_size": 0.01,
    "risk_percent": 0.5,
    "reward_ratio": 2,
    "min_confidence": 0.25,  # Very low - accept almost everything
    "max_daily_loss": 10,
    "fast_ma_period": 10,  # Very fast
    "slow_ma_period": 20,  # Very fast
    "rsi_period": 14,
    "rsi_overbought": 90,  # Very permissive
    "rsi_oversold": 10,    # Very permissive
    "macd_fast": 12,
    "macd_slow": 26,
    "macd_signal": 9,
    "macd_min_histogram": 0.5,
    "atr_period": 14,
    "atr_multiplier": 2,
    "adx_min_strength": 25,
    "use_rsi": True,
    "use_macd": False,  # DISABLED - too strict
    "use_adx": False,   # DISABLED - too strict
    "use_trend_filter": False,  # DISABLED - too strict
    "trend_ma_period": 100,
    "enable_trading_hours": False,  # Trade 24/7
    "trading_start_hour": 0,
    "trading_end_hour": 23,
    "avoid_news_trading": False,  # Don't avoid news
    "news_buffer_minutes": 60,
    "use_split_orders": True,
    "num_positions": 3,
    "tp_level_1": 1.5,
    "tp_level_2": 2.5,
    "tp_level_3": 4,
    "tp_levels": [1.5, 2.5, 4.0],
    "partial_close_percent": [40, 30, 30],
    "max_lot_per_order": 0.5,
    "max_trades_total": 50,
    "max_trades_per_symbol": 5,
    "enable_trailing_stop": True,
    "trail_activation": 1.5,
    "trail_distance": 1,
    "use_adaptive_risk": True,
    "max_risk_multiplier": 1.5,
    "min_risk_multiplier": 0.5,
    "max_drawdown_percent": 10,
    "max_daily_trades": 50,
    "use_volume_filter": False,  # DISABLED - too strict
    "min_volume_ma": 1.2,
    "volume_ma_period": 20,
    "obv_period": 20,
    "update_interval": 60,
    "version": "2.1.0",
    "last_updated": datetime.now().isoformat()
}

# Save configuration
with open('bot_config.json', 'w') as f:
    json.dump(config, f, indent=4)

print("="*80)
print("AGGRESSIVE TESTING CONFIGURATION APPLIED")
print("="*80)
print("\nSettings:")
print(f"  Symbols: {len(config['symbols'])} (XAUUSD, XAGUSD, EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, NZDUSD)")
print(f"  Timeframe: M1 (1 minute)")
print(f"  Fast MA: {config['fast_ma_period']}")
print(f"  Slow MA: {config['slow_ma_period']}")
print(f"  Min Confidence: {config['min_confidence']*100}%")
print(f"  RSI: {config['rsi_oversold']}/{config['rsi_overbought']}")
print(f"  MACD: {'Enabled' if config['use_macd'] else 'DISABLED'}")
print(f"  ADX: {'Enabled' if config['use_adx'] else 'DISABLED'}")
print(f"  Trend Filter: {'Enabled' if config['use_trend_filter'] else 'DISABLED'}")
print(f"  Volume Filter: {'Enabled' if config['use_volume_filter'] else 'DISABLED'}")
trading_hours = '24/7' if not config['enable_trading_hours'] else f'{config["trading_start_hour"]}-{config["trading_end_hour"]}'
print(f"  Trading Hours: {trading_hours}")
print(f"  Max Daily Trades: {config['max_daily_trades']}")
print("\n" + "="*80)
print("RESTART BOT NOW TO APPLY SETTINGS")
print("="*80)
print("\n1. Stop bot: Ctrl+C or dashboard 'Stop Bot'")
print("2. Start bot: python start_dashboard.py")
print("3. Expect trades within 5-15 minutes")
print("\n" + "="*80)
