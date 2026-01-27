"""
OPTIMIZED Configuration for MT5 Trading Bot
Based on trade analysis - designed for better profitability

Key Changes from Original:
1. M5 timeframe instead of M1 (less noise)
2. Wider stop losses (2.0x ATR instead of 1.2x)
3. Higher confidence threshold (70% instead of 50%)
4. Relaxed trailing stops
5. Stronger trend filter (H1 instead of M15)
6. Reduced risk during testing (0.2% instead of 0.3%)
7. Time-of-day filter enabled
"""

import MetaTrader5 as mt5

# ==============================================================================
# TRADING SYMBOLS
# ==============================================================================
SYMBOLS = ['XAUUSD', 'GBPUSD']  # Gold + GBP/USD

# ==============================================================================
# TIMEFRAME SETTINGS - OPTIMIZED FOR M5
# ==============================================================================
TIMEFRAME = mt5.TIMEFRAME_M5  # 5-minute timeframe (MUCH BETTER than M1!)

# ==============================================================================
# RISK MANAGEMENT - REDUCED FOR TESTING
# ==============================================================================
RISK_PERCENT = 0.2          # Risk 0.2% per trade (reduced from 0.3%)
REWARD_RATIO = 1.5          # Risk:Reward ratio 1:1.5
DEFAULT_LOT_SIZE = 0.01     # Fallback lot size

USE_DYNAMIC_SIZING = True
MAX_LOT_SIZE = 1.0
MIN_LOT_SIZE = 0.01

# ==============================================================================
# SPLIT ORDERS & PARTIAL PROFIT TAKING
# ==============================================================================
USE_SPLIT_ORDERS = True
NUM_POSITIONS = 3

# More realistic TP levels for M5
TP_LEVELS = [1.2, 1.8, 2.5]  # Conservative targets
PARTIAL_CLOSE_PERCENT = [40, 30, 30]
MAX_LOT_PER_ORDER = 0.5

# ==============================================================================
# ADAPTIVE RISK MANAGEMENT
# ==============================================================================
USE_ADAPTIVE_RISK = True

# M5 optimized periods
TREND_STRENGTH_PERIOD = 30  # Longer period for M5

# Stricter thresholds
ADX_STRONG_TREND = 20       # Standard ADX threshold
ADX_RANGING = 15
TREND_CONSISTENCY_HIGH = 65
VOLATILITY_HIGH = 1.2

# HIGHER confidence requirement (KEY CHANGE!)
MIN_TRADE_CONFIDENCE = 0.70  # 70% minimum (was 50%)

MAX_RISK_MULTIPLIER = 1.5
MIN_RISK_MULTIPLIER = 0.3

# ==============================================================================
# MOVING AVERAGE STRATEGY - M5 OPTIMIZED
# ==============================================================================
FAST_MA_PERIOD = 10         # 10-period EMA
SLOW_MA_PERIOD = 20         # 20-period EMA
MA_TYPE = 'EMA'

WAIT_FOR_CONFIRMATION = True
MIN_MA_SEPARATION = 0.0001

# ==============================================================================
# MACD INDICATOR - STRICTER CONFIRMATION
# ==============================================================================
USE_MACD = True
MACD_FAST = 8
MACD_SLOW = 17
MACD_SIGNAL = 5

# Require stronger MACD signal (KEY CHANGE!)
MACD_MIN_HISTOGRAM = 0.5    # Minimum histogram value (was 0.0)
REQUIRE_MACD_CONFIRMATION = True

# ==============================================================================
# ATR-BASED STOP LOSS - WIDER STOPS
# ==============================================================================
ATR_PERIOD = 14
ATR_MULTIPLIER_SL = 2.0     # WIDER stop loss (was 1.2) - KEY CHANGE!

MIN_ATR_VALUE = 0.0001
MAX_ATR_VALUE = 999999

# ==============================================================================
# TRAILING STOP SETTINGS - RELAXED
# ==============================================================================
ENABLE_TRAILING_STOP = True

# More profit before trailing activates (KEY CHANGE!)
TRAIL_ACTIVATION_ATR = 1.5  # was 0.8
TRAIL_DISTANCE_ATR = 1.0    # was 0.6
TRAIL_TYPE = 'atr'

TRAIL_PERCENT = 1.5
BREAKEVEN_ACTIVATION_PIPS = 50
BREAKEVEN_PLUS_PIPS = 5
TRAIL_START_PIPS = 75

# ==============================================================================
# TRAILING TAKE PROFIT SETTINGS
# ==============================================================================
ENABLE_TRAILING_TP = False
TRAILING_TP_RATIO = 0.5

# ==============================================================================
# TRADE MANAGEMENT
# ==============================================================================
MAGIC_NUMBER = 234000

# M5 limits (fewer trades than M1)
MAX_TRADES_TOTAL = 6        # Reduced from 10
MAX_TRADES_PER_SYMBOL = 2   # Reduced from 3
ALLOW_HEDGING = False

# TRADING HOURS - ENABLED (KEY CHANGE!)
ENABLE_TRADING_HOURS = True
TRADING_START_HOUR = 8      # 8 AM UTC (London open)
TRADING_END_HOUR = 16       # 4 PM UTC (before NY close)

TRADING_DAYS = [0, 1, 2, 3, 4]  # Monday to Friday

# ==============================================================================
# ADDITIONAL FILTERS - STRONGER
# ==============================================================================
# STRONGER trend filter (KEY CHANGE!)
USE_TREND_FILTER = True
TREND_TIMEFRAME = mt5.TIMEFRAME_H1  # H1 for trend (was M15)
TREND_MA_PERIOD = 50                # Longer MA (was 20)

USE_VOLUME_FILTER = False
MIN_VOLUME_MA = 1.2

AVOID_NEWS_TRADING = False
NEWS_BUFFER_MINUTES = 30

# ==============================================================================
# PERFORMANCE & MONITORING
# ==============================================================================
UPDATE_INTERVAL = 30        # Check every 30 seconds (was 10)
LOG_LEVEL = 'INFO'
SAVE_TRADE_HISTORY = True

# Notifications
ENABLE_TELEGRAM = False
TELEGRAM_TOKEN = ''
TELEGRAM_CHAT_ID = ''

ENABLE_EMAIL = False
EMAIL_ADDRESS = ''
EMAIL_PASSWORD = ''

# ==============================================================================
# SAFETY LIMITS
# ==============================================================================
MAX_DAILY_LOSS = 100.0
MAX_DAILY_TRADES = 30       # Reduced from 100
MAX_DAILY_LOSS_PERCENT = 5.0

MAX_DRAWDOWN_PERCENT = 10.0
MIN_ACCOUNT_BALANCE = 100.0

# ==============================================================================
# BACKTESTING
# ==============================================================================
BACKTEST_MODE = False
BACKTEST_START_DATE = '2024-01-01'
BACKTEST_END_DATE = '2024-12-31'

# ==============================================================================
# BUILD CONFIG DICTIONARY
# ==============================================================================
def get_config():
    """Return configuration dictionary"""
    return {
        'symbols': SYMBOLS,
        'timeframe': TIMEFRAME,
        'risk_percent': RISK_PERCENT,
        'reward_ratio': REWARD_RATIO,
        'lot_size': DEFAULT_LOT_SIZE,
        'use_dynamic_sizing': USE_DYNAMIC_SIZING,
        'max_lot_size': MAX_LOT_SIZE,
        'min_lot_size': MIN_LOT_SIZE,
        'use_split_orders': USE_SPLIT_ORDERS,
        'num_positions': NUM_POSITIONS,
        'tp_levels': TP_LEVELS,
        'partial_close_percent': PARTIAL_CLOSE_PERCENT,
        'max_lot_per_order': MAX_LOT_PER_ORDER,
        'use_adaptive_risk': USE_ADAPTIVE_RISK,
        'trend_strength_period': TREND_STRENGTH_PERIOD,
        'adx_strong_trend': ADX_STRONG_TREND,
        'adx_ranging': ADX_RANGING,
        'trend_consistency_high': TREND_CONSISTENCY_HIGH,
        'volatility_high': VOLATILITY_HIGH,
        'min_trade_confidence': MIN_TRADE_CONFIDENCE,
        'max_risk_multiplier': MAX_RISK_MULTIPLIER,
        'min_risk_multiplier': MIN_RISK_MULTIPLIER,
        'fast_ma_period': FAST_MA_PERIOD,
        'slow_ma_period': SLOW_MA_PERIOD,
        'ma_type': MA_TYPE,
        'wait_for_confirmation': WAIT_FOR_CONFIRMATION,
        'use_macd': USE_MACD,
        'macd_fast': MACD_FAST,
        'macd_slow': MACD_SLOW,
        'macd_signal': MACD_SIGNAL,
        'macd_min_histogram': MACD_MIN_HISTOGRAM,
        'require_macd_confirmation': REQUIRE_MACD_CONFIRMATION,
        'atr_period': ATR_PERIOD,
        'atr_multiplier': ATR_MULTIPLIER_SL,
        'min_atr_value': MIN_ATR_VALUE,
        'max_atr_value': MAX_ATR_VALUE,
        'enable_trailing_stop': ENABLE_TRAILING_STOP,
        'trail_activation': TRAIL_ACTIVATION_ATR,
        'trail_distance': TRAIL_DISTANCE_ATR,
        'trail_type': TRAIL_TYPE,
        'trail_percent': TRAIL_PERCENT,
        'breakeven_activation_pips': BREAKEVEN_ACTIVATION_PIPS,
        'breakeven_plus_pips': BREAKEVEN_PLUS_PIPS,
        'trail_start_pips': TRAIL_START_PIPS,
        'enable_trailing_tp': ENABLE_TRAILING_TP,
        'trailing_tp_ratio': TRAILING_TP_RATIO,
        'magic_number': MAGIC_NUMBER,
        'max_trades_total': MAX_TRADES_TOTAL,
        'max_trades_per_symbol': MAX_TRADES_PER_SYMBOL,
        'allow_hedging': ALLOW_HEDGING,
        'enable_trading_hours': ENABLE_TRADING_HOURS,
        'trading_start_hour': TRADING_START_HOUR,
        'trading_end_hour': TRADING_END_HOUR,
        'trading_days': TRADING_DAYS,
        'use_trend_filter': USE_TREND_FILTER,
        'trend_timeframe': TREND_TIMEFRAME,
        'trend_ma_period': TREND_MA_PERIOD,
        'use_volume_filter': USE_VOLUME_FILTER,
        'min_volume_ma': MIN_VOLUME_MA,
        'avoid_news_trading': AVOID_NEWS_TRADING,
        'news_buffer_minutes': NEWS_BUFFER_MINUTES,
        'update_interval': UPDATE_INTERVAL,
        'log_level': LOG_LEVEL,
        'save_trade_history': SAVE_TRADE_HISTORY,
        'enable_telegram': ENABLE_TELEGRAM,
        'telegram_token': TELEGRAM_TOKEN,
        'telegram_chat_id': TELEGRAM_CHAT_ID,
        'enable_email': ENABLE_EMAIL,
        'email_address': EMAIL_ADDRESS,
        'email_password': EMAIL_PASSWORD,
        'max_daily_loss': MAX_DAILY_LOSS,
        'max_daily_trades': MAX_DAILY_TRADES,
        'max_daily_loss_percent': MAX_DAILY_LOSS_PERCENT,
        'max_drawdown_percent': MAX_DRAWDOWN_PERCENT,
        'min_account_balance': MIN_ACCOUNT_BALANCE,
        'backtest_mode': BACKTEST_MODE,
        'backtest_start_date': BACKTEST_START_DATE,
        'backtest_end_date': BACKTEST_END_DATE,
    }


if __name__ == "__main__":
    import json
    config = get_config()
    print("=" * 80)
    print("OPTIMIZED CONFIGURATION")
    print("=" * 80)
    print()
    print("Key Improvements:")
    print("  ✓ M5 timeframe (less noise)")
    print("  ✓ Wider stops (2.0x ATR)")
    print("  ✓ Higher confidence (70%)")
    print("  ✓ Relaxed trailing stops")
    print("  ✓ Stronger trend filter (H1)")
    print("  ✓ Trading hours enabled")
    print("  ✓ Reduced risk (0.2%)")
    print()
    print("Configuration:")
    print(json.dumps({k: str(v) for k, v in config.items()}, indent=2))
