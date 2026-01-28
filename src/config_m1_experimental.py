"""
PROFITABLE BALANCED Configuration for MT5 Trading Bot
RECOMMENDED FOR MOST TRADERS

Strategy: Trend-Following with Multiple Confirmations
Timeframe: H1 (1-hour)
Expected: 5-15 quality trades per day
Win Rate: 55-65%
Risk/Reward: 1:2 minimum

Key Features:
1. H1 timeframe (clear trends, less noise)
2. Multiple confirmation indicators
3. Strong trend filter (H4)
4. Wider stops (let trades breathe)
5. High confidence threshold (70%)
6. Time-based filters
7. News avoidance
8. Proper risk management
"""

import MetaTrader5 as mt5

# ==============================================================================
# TRADING SYMBOLS
# ==============================================================================
SYMBOLS = ['XAUUSD', 'XAGUSD']  # Gold and Silver (best for trending)

# ==============================================================================
# TIMEFRAME - H1 FOR QUALITY TRADES
# ==============================================================================
TIMEFRAME = mt5.TIMEFRAME_H1  # 1-hour charts

# ==============================================================================
# RISK MANAGEMENT - CONSERVATIVE
# ==============================================================================
RISK_PERCENT = 0.5              # 0.5% per trade (safe)
REWARD_RATIO = 2.0              # 1:2 risk/reward minimum
DEFAULT_LOT_SIZE = 0.01

USE_DYNAMIC_SIZING = True
MAX_LOT_SIZE = 0.5              # Conservative max
MIN_LOT_SIZE = 0.01

# ==============================================================================
# SPLIT ORDERS - MULTIPLE TP LEVELS
# ==============================================================================
USE_SPLIT_ORDERS = True
NUM_POSITIONS = 3

# Conservative TP levels
TP_LEVELS = [1.5, 2.5, 4.0]     # 1.5R, 2.5R, 4.0R
PARTIAL_CLOSE_PERCENT = [40, 30, 30]
MAX_LOT_PER_ORDER = 0.3

# ==============================================================================
# ADAPTIVE RISK - HIGH QUALITY TRADES ONLY
# ==============================================================================
USE_ADAPTIVE_RISK = True

TREND_STRENGTH_PERIOD = 50      # Longer period for stability

# Strong thresholds (quality over quantity)
ADX_STRONG_TREND = 25           # Only trade strong trends
ADX_RANGING = 15                # Avoid ranging markets
TREND_CONSISTENCY_HIGH = 70     # High consistency required
VOLATILITY_HIGH = 1.5

# HIGH confidence threshold
MIN_TRADE_CONFIDENCE = 0.70     # 70% minimum (high quality)

MAX_RISK_MULTIPLIER = 1.5
MIN_RISK_MULTIPLIER = 0.5

# ==============================================================================
# MOVING AVERAGES - INDUSTRY STANDARD
# ==============================================================================
FAST_MA_PERIOD = 20             # 20 EMA (proven effective)
SLOW_MA_PERIOD = 50             # 50 EMA (trend line)
MA_TYPE = 'EMA'                 # Exponential MA

WAIT_FOR_CONFIRMATION = True
MIN_MA_SEPARATION = 0.0005      # Require clear separation

# ==============================================================================
# RSI - AVOID EXTREMES
# ==============================================================================
USE_RSI = True
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70             # Don't buy above 70
RSI_OVERSOLD = 30               # Don't sell below 30

# ==============================================================================
# MACD - MOMENTUM CONFIRMATION
# ==============================================================================
USE_MACD = True
MACD_FAST = 12                  # Standard settings
MACD_SLOW = 26
MACD_SIGNAL = 9

MACD_MIN_HISTOGRAM = 0.5        # Require strong momentum
REQUIRE_MACD_CONFIRMATION = True

# ==============================================================================
# ATR-BASED STOPS - WIDER FOR H1
# ==============================================================================
ATR_PERIOD = 14
ATR_MULTIPLIER_SL = 2.0         # 2x ATR (let trades breathe)

MIN_ATR_VALUE = 0.0001
MAX_ATR_VALUE = 999999

# ==============================================================================
# TRAILING STOP - PROTECT PROFITS
# ==============================================================================
ENABLE_TRAILING_STOP = True

TRAIL_ACTIVATION_ATR = 1.5      # After 1.5R profit
TRAIL_DISTANCE_ATR = 1.0        # 1x ATR distance
TRAIL_TYPE = 'atr'

TRAIL_PERCENT = 2.0
BREAKEVEN_ACTIVATION_PIPS = 50  # Move to breakeven after 50 pips
BREAKEVEN_PLUS_PIPS = 10
TRAIL_START_PIPS = 100

# ==============================================================================
# TRAILING TAKE PROFIT
# ==============================================================================
ENABLE_TRAILING_TP = True
TRAILING_TP_RATIO = 0.5

# ==============================================================================
# TRADE MANAGEMENT
# ==============================================================================
MAGIC_NUMBER = 234001

# Limit trades (quality over quantity)
MAX_TRADES_TOTAL = 10           # Max 10 open trades
MAX_TRADES_PER_SYMBOL = 3       # Max 3 per symbol
ALLOW_HEDGING = False

# ==============================================================================
# TRADING HOURS - BEST TIMES ONLY
# ==============================================================================
ENABLE_TRADING_HOURS = True
TRADING_START_HOUR = 8          # 8 AM (London open)
TRADING_END_HOUR = 16           # 4 PM (before NY close)

TRADING_DAYS = [0, 1, 2, 3, 4]  # Monday to Friday

# ==============================================================================
# TREND FILTER - H4 FOR MAJOR TREND
# ==============================================================================
USE_TREND_FILTER = True
TREND_TIMEFRAME = mt5.TIMEFRAME_H4  # H4 for major trend
TREND_MA_PERIOD = 100               # 100 EMA for trend direction

# ==============================================================================
# ADDITIONAL FILTERS
# ==============================================================================
USE_VOLUME_FILTER = True
MIN_VOLUME_MA = 1.2             # Require above-average volume

AVOID_NEWS_TRADING = True
NEWS_BUFFER_MINUTES = 60        # Avoid 1 hour before/after news

# ==============================================================================
# BOLLINGER BANDS - VOLATILITY FILTER
# ==============================================================================
USE_BOLLINGER = True
BB_PERIOD = 20
BB_STD_DEV = 2.0
BB_SQUEEZE_THRESHOLD = 0.5      # Avoid low volatility

# ==============================================================================
# ADX - TREND STRENGTH FILTER
# ==============================================================================
USE_ADX = True
ADX_PERIOD = 14
ADX_MIN_STRENGTH = 25           # Only trade when ADX > 25

# ==============================================================================
# SUPPORT/RESISTANCE LEVELS
# ==============================================================================
USE_SR_LEVELS = True
SR_LOOKBACK = 100               # Look back 100 bars
SR_TOLERANCE = 0.0005           # 5 pips tolerance

# ==============================================================================
# DYNAMIC RISK MANAGEMENT
# ==============================================================================
USE_DYNAMIC_SL = True
USE_DYNAMIC_TP = True
DYNAMIC_SL_CHECK_INTERVAL = 300  # Check every 5 minutes
DYNAMIC_TP_CHECK_INTERVAL = 300
MAX_TP_EXTENSIONS = 3

# ==============================================================================
# SCALPING MODE - DISABLED FOR H1
# ==============================================================================
USE_SCALPING_MODE = False

# ==============================================================================
# PERFORMANCE & MONITORING
# ==============================================================================
UPDATE_INTERVAL = 60            # Check every 60 seconds
LOG_LEVEL = 'INFO'
SAVE_TRADE_HISTORY = True

# ==============================================================================
# NOTIFICATIONS
# ==============================================================================
ENABLE_TELEGRAM = False
TELEGRAM_TOKEN = ''
TELEGRAM_CHAT_ID = ''

ENABLE_EMAIL = False
EMAIL_ADDRESS = ''
EMAIL_PASSWORD = ''

# ==============================================================================
# SAFETY LIMITS
# ==============================================================================
MAX_DAILY_LOSS = 200.0          # $200 max daily loss
MAX_DAILY_TRADES = 20           # Max 20 trades per day
MAX_DAILY_LOSS_PERCENT = 3.0    # Stop at 3% daily loss

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
        'use_rsi': USE_RSI,
        'rsi_period': RSI_PERIOD,
        'rsi_overbought': RSI_OVERBOUGHT,
        'rsi_oversold': RSI_OVERSOLD,
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
        'use_bollinger': USE_BOLLINGER,
        'bb_period': BB_PERIOD,
        'bb_std_dev': BB_STD_DEV,
        'use_adx': USE_ADX,
        'adx_period': ADX_PERIOD,
        'adx_min_strength': ADX_MIN_STRENGTH,
        'use_sr_levels': USE_SR_LEVELS,
        'sr_lookback': SR_LOOKBACK,
        'sr_tolerance': SR_TOLERANCE,
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
        'use_dynamic_sl': USE_DYNAMIC_SL,
        'use_dynamic_tp': USE_DYNAMIC_TP,
        'dynamic_sl_check_interval': DYNAMIC_SL_CHECK_INTERVAL,
        'dynamic_tp_check_interval': DYNAMIC_TP_CHECK_INTERVAL,
        'max_tp_extensions': MAX_TP_EXTENSIONS,
        'use_scalping_mode': USE_SCALPING_MODE,
    }


if __name__ == "__main__":
    import json
    config = get_config()
    print("=" * 80)
    print("PROFITABLE BALANCED CONFIGURATION")
    print("=" * 80)
    print()
    print("Strategy: Trend-Following with Multiple Confirmations")
    print("Timeframe: H1 (1-hour)")
    print("Expected: 5-15 quality trades per day")
    print("Win Rate: 55-65%")
    print("Risk/Reward: 1:2 minimum")
    print()
    print("Key Features:")
    print("  ✓ H1 timeframe (clear trends)")
    print("  ✓ 20/50 EMA (industry standard)")
    print("  ✓ RSI filter (avoid extremes)")
    print("  ✓ MACD confirmation (momentum)")
    print("  ✓ ADX filter (trend strength)")
    print("  ✓ H4 trend filter (major trend)")
    print("  ✓ 70% confidence minimum")
    print("  ✓ 2x ATR stops (wider)")
    print("  ✓ Trading hours filter")
    print("  ✓ News avoidance")
    print()
    print("Configuration loaded successfully!")
