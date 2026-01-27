"""
M1 TESTING Configuration for MT5 Trading Bot
EXTREME HIGH-FREQUENCY TRADING MODE

⚠️ WARNING: M1 timeframe generates 100-200+ trades per day!
⚠️ This is for TESTING ONLY with strict daily loss limits

Key M1 Settings:
1. M1 (1-minute) timeframe for maximum trade frequency
2. Tight stop losses (1.2x ATR) for quick exits
3. Lower confidence threshold (50%) for more signals
4. Fast indicators (5/10 MA, 5/13/3 MACD)
5. Quick trailing stops (0.8/0.6 ATR)
6. M15 trend filter (faster than H1)
7. 5% daily loss limit (stops trading when hit)
8. 0.3% risk per trade
9. 10-second update interval
10. Unlimited trades (until 5% daily loss)
"""

import MetaTrader5 as mt5

# ==============================================================================
# TRADING SYMBOLS
# ==============================================================================
SYMBOLS = ['XAUUSD', 'GBPUSD', 'XAGUSD']  # Gold, GBP/USD, Silver

# ==============================================================================
# TIMEFRAME SETTINGS - M1 EXTREME HIGH-FREQUENCY MODE
# ==============================================================================
TIMEFRAME = mt5.TIMEFRAME_M1  # 1-minute timeframe (100-200+ trades/day expected!)

# ==============================================================================
# RISK MANAGEMENT - M1 TESTING
# ==============================================================================
RISK_PERCENT = 0.3          # Risk 0.3% per trade (higher for M1 testing)
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

# Aggressive TP levels for M1 (quick profits)
TP_LEVELS = [1.0, 1.3, 1.8]  # M1 optimized - quick exits
PARTIAL_CLOSE_PERCENT = [40, 30, 30]
MAX_LOT_PER_ORDER = 0.5

# ==============================================================================
# ADAPTIVE RISK MANAGEMENT
# ==============================================================================
USE_ADAPTIVE_RISK = True

# M1 optimized periods
TREND_STRENGTH_PERIOD = 20  # Shorter period for M1

# Relaxed thresholds for M1 (more signals)
ADX_STRONG_TREND = 18       # Lower threshold for M1
ADX_RANGING = 12
TREND_CONSISTENCY_HIGH = 60
VOLATILITY_HIGH = 1.2

# LOWER confidence for M1 testing (more trades)
MIN_TRADE_CONFIDENCE = 0.50  # 50% minimum for M1 testing

MAX_RISK_MULTIPLIER = 1.5
MIN_RISK_MULTIPLIER = 0.3

# ==============================================================================
# MOVING AVERAGE STRATEGY - M1 OPTIMIZED
# ==============================================================================
FAST_MA_PERIOD = 5          # 5-period EMA (M1 optimized)
SLOW_MA_PERIOD = 10         # 10-period EMA (M1 optimized)
MA_TYPE = 'EMA'

WAIT_FOR_CONFIRMATION = True
MIN_MA_SEPARATION = 0.0001

# ==============================================================================
# RSI INDICATOR (ENHANCED - Most Popular Filter)
# ==============================================================================
USE_RSI = True
RSI_PERIOD = 14             # Standard RSI period
RSI_OVERBOUGHT = 70         # Don't buy above this
RSI_OVERSOLD = 30           # Don't sell below this

# ==============================================================================
# MACD INDICATOR - M1 OPTIMIZED
# ==============================================================================
USE_MACD = True
MACD_FAST = 5               # Faster for M1
MACD_SLOW = 13              # Faster for M1
MACD_SIGNAL = 3             # Faster for M1

# Relaxed MACD for M1 (more signals)
MACD_MIN_HISTOGRAM = 0.0    # No minimum for M1 testing
REQUIRE_MACD_CONFIRMATION = True

# ==============================================================================
# ATR-BASED STOP LOSS - M1 OPTIMIZED
# ==============================================================================
# Adjusted for M1 timeframe
ATR_PERIOD = 14             # Period for ATR calculation (14 periods = 14 minutes)
ATR_MULTIPLIER_SL = 1.2     # Stop Loss multiplier (VERY TIGHT for M1)

MIN_ATR_VALUE = 0.0001
MAX_ATR_VALUE = 999999

# ==============================================================================
# TRAILING STOP SETTINGS - M1 OPTIMIZED
# ==============================================================================
ENABLE_TRAILING_STOP = True

# Activation threshold (adjusted for M1)
TRAIL_ACTIVATION_ATR = 0.8  # Activate trailing very quickly on M1
# Example: If ATR=10 and this is 0.8, trailing activates after 8 points profit

# Trailing distance (adjusted for M1)
TRAIL_DISTANCE_ATR = 0.6    # Trail very close on M1
TRAIL_TYPE = 'atr'          # 'atr', 'percentage', 'swing', 'chandelier', 'breakeven'

TRAIL_PERCENT = 1.5
BREAKEVEN_ACTIVATION_PIPS = 30  # M1 optimized - faster breakeven
BREAKEVEN_PLUS_PIPS = 5
TRAIL_START_PIPS = 50           # M1 optimized - faster trailing

# ==============================================================================
# TRAILING TAKE PROFIT SETTINGS
# ==============================================================================
ENABLE_TRAILING_TP = False
TRAILING_TP_RATIO = 0.5

# ==============================================================================
# TRADE MANAGEMENT
# ==============================================================================
MAGIC_NUMBER = 234000

# Maximum trades (UNLIMITED FOR TESTING)
MAX_TRADES_TOTAL = 999        # Effectively unlimited
MAX_TRADES_PER_SYMBOL = 999   # Effectively unlimited
ALLOW_HEDGING = False

# TRADING HOURS - DISABLED FOR TESTING
ENABLE_TRADING_HOURS = False  # Trade 24/7 during testing
TRADING_START_HOUR = 0        # Not used when disabled
TRADING_END_HOUR = 24         # Not used when disabled

TRADING_DAYS = [0, 1, 2, 3, 4]  # Monday to Friday

# ==============================================================================
# ADDITIONAL FILTERS - STRONGER
# ==============================================================================
# FASTER trend filter for M1
USE_TREND_FILTER = True
TREND_TIMEFRAME = mt5.TIMEFRAME_M15  # M15 for trend (faster than H1)
TREND_MA_PERIOD = 20                 # Shorter MA for M1 responsiveness

USE_VOLUME_FILTER = False
MIN_VOLUME_MA = 1.2

AVOID_NEWS_TRADING = False
NEWS_BUFFER_MINUTES = 30

# ==============================================================================
# DYNAMIC RISK MANAGEMENT (NEW!)
# ==============================================================================
USE_DYNAMIC_SL = True           # Enable dynamic stop loss adjustments
USE_DYNAMIC_TP = True           # Enable dynamic take profit extensions
DYNAMIC_SL_CHECK_INTERVAL = 60  # Check SL every 60 seconds
DYNAMIC_TP_CHECK_INTERVAL = 60  # Check TP every 60 seconds
MAX_TP_EXTENSIONS = 5           # Maximum TP extensions per position

# ==============================================================================
# PERFORMANCE & MONITORING
# ==============================================================================
UPDATE_INTERVAL = 10        # Check every 10 seconds (M1 needs fast updates)
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
# SAFETY LIMITS (RELAXED FOR TESTING)
# ==============================================================================
MAX_DAILY_LOSS = 100.0      # Absolute dollar amount (backup limit)
MAX_DAILY_TRADES = 999      # Unlimited for testing
MAX_DAILY_LOSS_PERCENT = 5.0  # Stop trading if daily loss exceeds 5% of equity

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
        
        # Backtesting
        'backtest_mode': BACKTEST_MODE,
        'backtest_start_date': BACKTEST_START_DATE,
        'backtest_end_date': BACKTEST_END_DATE,
        
        # Dynamic Risk Management
        'use_dynamic_sl': USE_DYNAMIC_SL,
        'use_dynamic_tp': USE_DYNAMIC_TP,
        'dynamic_sl_check_interval': DYNAMIC_SL_CHECK_INTERVAL,
        'dynamic_tp_check_interval': DYNAMIC_TP_CHECK_INTERVAL,
        'max_tp_extensions': MAX_TP_EXTENSIONS,
    }


if __name__ == "__main__":
    import json
    config = get_config()
    print("=" * 80)
    print("M1 TESTING CONFIGURATION - EXTREME HIGH-FREQUENCY MODE")
    print("=" * 80)
    print()
    print("⚠️  WARNING: Expect 100-200+ trades per day!")
    print()
    print("Key M1 Settings:")
    print("  ✓ M1 (1-minute) timeframe")
    print("  ✓ Fast indicators (5/10 MA, 5/13/3 MACD)")
    print("  ✓ Tight stops (1.2x ATR)")
    print("  ✓ Quick trailing (0.8/0.6 ATR)")
    print("  ✓ Lower confidence (50%)")
    print("  ✓ M15 trend filter")
    print("  ✓ 5% daily loss limit")
    print("  ✓ 0.3% risk per trade")
    print("  ✓ 10-second updates")
    print("  ✓ Unlimited trades (until loss limit)")
    print()
    print("Configuration:")
    print(json.dumps({k: str(v) for k, v in config.items()}, indent=2))
