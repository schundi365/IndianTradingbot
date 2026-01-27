"""
Configuration file for MT5 Trading Bot
Customize these settings for your trading strategy
"""

import MetaTrader5 as mt5

# ==============================================================================
# TRADING SYMBOLS
# ==============================================================================
SYMBOLS = ['XAUUSD', 'XAGUSD']  # Gold and Silver
# Other options: 'XAUUSD' (Gold), 'XAGUSD' (Silver), 'XPTUSD' (Platinum)

# ==============================================================================
# TIMEFRAME SETTINGS
# ==============================================================================
TIMEFRAME = mt5.TIMEFRAME_M5  # 5-minute timeframe (CHANGED FROM H1)

# Available timeframes:
# mt5.TIMEFRAME_M1  - 1 minute (NOT RECOMMENDED - too fast)
# mt5.TIMEFRAME_M5  - 5 minutes (CURRENT - active trading)
# mt5.TIMEFRAME_M15 - 15 minutes
# mt5.TIMEFRAME_M30 - 30 minutes
# mt5.TIMEFRAME_H1  - 1 hour
# mt5.TIMEFRAME_H4  - 4 hours
# mt5.TIMEFRAME_D1  - 1 day
# mt5.TIMEFRAME_W1  - 1 week

# ⚠️ WARNING: M5 timeframe is VERY ACTIVE
# - Expect 20-50+ trades per day
# - Requires constant monitoring
# - Higher spread costs
# - More false signals
# - Recommended for experienced traders only

# ==============================================================================
# RISK MANAGEMENT
# ==============================================================================
RISK_PERCENT = 0.5          # Risk 0.5% per trade (REDUCED for M5 - more trades)
REWARD_RATIO = 1.5          # Risk:Reward ratio (1:1.5 for faster timeframe)
DEFAULT_LOT_SIZE = 0.01     # Fallback lot size if calculation fails

# Position sizing
USE_DYNAMIC_SIZING = True   # Calculate lot size based on risk percentage
MAX_LOT_SIZE = 1.0         # Maximum lot size allowed
MIN_LOT_SIZE = 0.01        # Minimum lot size allowed

# ==============================================================================
# SPLIT ORDERS & PARTIAL PROFIT TAKING
# ==============================================================================
USE_SPLIT_ORDERS = True     # Split position into multiple orders with different TPs

# Number of positions to split into (2-5 recommended)
NUM_POSITIONS = 3           # Split into 3 separate positions

# Take profit levels (Risk:Reward ratios for each position)
# Example: [1.5, 2.5, 4.0] means:
#   - Position 1 exits at 1.5x risk distance
#   - Position 2 exits at 2.5x risk distance  
#   - Position 3 exits at 4.0x risk distance
TP_LEVELS = [1.5, 2.5, 4.0]

# Percentage of total position for each TP level
# Must sum to 100%. Example: [40, 30, 30] means:
#   - 40% of position closes at first TP
#   - 30% of position closes at second TP
#   - 30% of position closes at third TP
PARTIAL_CLOSE_PERCENT = [40, 30, 30]

# Maximum lot size per individual order (prevents broker rejection)
MAX_LOT_PER_ORDER = 0.5

# Example strategies:
# Conservative: TP_LEVELS=[1.0, 2.0, 3.0], PARTIAL_CLOSE_PERCENT=[50, 30, 20]
# Balanced: TP_LEVELS=[1.5, 2.5, 4.0], PARTIAL_CLOSE_PERCENT=[40, 30, 30]
# Aggressive: TP_LEVELS=[2.0, 3.5, 6.0], PARTIAL_CLOSE_PERCENT=[30, 30, 40]

# ==============================================================================
# ADAPTIVE RISK MANAGEMENT
# ==============================================================================
USE_ADAPTIVE_RISK = True    # Enable intelligent risk adjustment based on market conditions

# When enabled, the bot will:
# - Adjust stop loss width based on market volatility and structure
# - Modify take profit targets based on trend strength
# - Change trailing parameters based on market type
# - Increase/decrease position size based on market favorability
# - Filter trades based on confidence scores

# Trend strength analysis
TREND_STRENGTH_PERIOD = 50  # Period for analyzing trend consistency

# Market condition thresholds (Advanced - leave as default unless experienced)
ADX_STRONG_TREND = 25       # ADX above this = trending market
ADX_RANGING = 20            # ADX below this = ranging market
TREND_CONSISTENCY_HIGH = 70 # % of bars in same direction = strong trend
VOLATILITY_HIGH = 1.3       # ATR ratio above this = volatile market

# Trade confidence requirements
MIN_TRADE_CONFIDENCE = 0.60 # Minimum confidence score to take trade (60%)
# Higher = fewer trades but higher quality
# Lower = more trades but some lower quality

# Risk adjustment limits
MAX_RISK_MULTIPLIER = 1.5   # Maximum risk increase in favorable conditions
MIN_RISK_MULTIPLIER = 0.3   # Minimum risk in unfavorable conditions

# ==============================================================================
# MOVING AVERAGE STRATEGY
# ==============================================================================
# Adjusted for M5 timeframe (shorter periods for faster signals)
FAST_MA_PERIOD = 10         # Fast moving average period (was 20 for H1)
SLOW_MA_PERIOD = 20         # Slow moving average period (was 50 for H1)
MA_TYPE = 'EMA'            # 'SMA' or 'EMA' (EMA better for lower timeframes)

# Entry conditions
WAIT_FOR_CONFIRMATION = True    # Wait for price to confirm above/below MAs
MIN_MA_SEPARATION = 0.0001      # Minimum distance between MAs for signal (0 = any)

# ==============================================================================
# ATR-BASED STOP LOSS
# ==============================================================================
ATR_PERIOD = 14             # Period for ATR calculation
ATR_MULTIPLIER_SL = 2.0     # Stop Loss = Entry ± (ATR × this multiplier)

# ATR filters
MIN_ATR_VALUE = 0.0001      # Minimum ATR to place trade (avoid low volatility)
MAX_ATR_VALUE = 999999      # Maximum ATR to place trade (avoid high volatility)

# ==============================================================================
# TRAILING STOP SETTINGS
# ==============================================================================
ENABLE_TRAILING_STOP = True

# Activation threshold
TRAIL_ACTIVATION_ATR = 1.5  # Activate trailing after this many ATRs of profit
# Example: If ATR=10 and this is 1.5, trailing activates after 15 points profit

# Trailing distance
TRAIL_DISTANCE_ATR = 1.0    # Trail at this many ATRs from current price
TRAIL_TYPE = 'atr'          # 'atr', 'percentage', 'swing', 'chandelier', 'breakeven'

# Percentage trailing (if TRAIL_TYPE = 'percentage')
TRAIL_PERCENT = 2.0         # Trail 2% from current price

# Breakeven settings (if TRAIL_TYPE = 'breakeven')
BREAKEVEN_ACTIVATION_PIPS = 100  # Move to BE after this many pips
BREAKEVEN_PLUS_PIPS = 10         # Lock in this many pips at BE
TRAIL_START_PIPS = 150           # Start normal trailing after this profit

# ==============================================================================
# TRAILING TAKE PROFIT SETTINGS
# ==============================================================================
ENABLE_TRAILING_TP = False  # Move TP as profit increases
TRAILING_TP_RATIO = 0.5     # Give back 50% of unrealized profit before hitting TP

# ==============================================================================
# TRADE MANAGEMENT
# ==============================================================================
MAGIC_NUMBER = 234000       # Unique identifier for bot trades (change if running multiple bots)

# Maximum trades
MAX_TRADES_TOTAL = 5        # Maximum total open trades
MAX_TRADES_PER_SYMBOL = 1   # Maximum trades per symbol
ALLOW_HEDGING = False       # Allow both buy and sell on same symbol

# Trading hours (UTC time)
ENABLE_TRADING_HOURS = False
TRADING_START_HOUR = 0      # Start trading at this hour (24h format)
TRADING_END_HOUR = 24       # Stop trading at this hour

# Days of week (0=Monday, 6=Sunday)
TRADING_DAYS = [0, 1, 2, 3, 4]  # Monday to Friday

# ==============================================================================
# ADDITIONAL FILTERS
# ==============================================================================
# Trend filter
USE_TREND_FILTER = True     # Only trade in direction of higher timeframe trend
TREND_TIMEFRAME = mt5.TIMEFRAME_H4  # Timeframe for trend determination
TREND_MA_PERIOD = 200       # MA period for trend (price above = uptrend)

# Volume filter
USE_VOLUME_FILTER = False   # Filter trades by volume
MIN_VOLUME_MA = 1.2         # Current volume must be X times average volume

# News filter
AVOID_NEWS_TRADING = False  # Pause trading during high-impact news
NEWS_BUFFER_MINUTES = 30    # Don't trade X minutes before/after news

# ==============================================================================
# PERFORMANCE & MONITORING
# ==============================================================================
UPDATE_INTERVAL = 30        # Check for signals every X seconds (30 = 30 seconds for M5)
LOG_LEVEL = 'INFO'          # 'DEBUG', 'INFO', 'WARNING', 'ERROR'
SAVE_TRADE_HISTORY = True   # Save trade history to CSV

# Notifications (optional - requires additional setup)
ENABLE_TELEGRAM = False     # Send notifications via Telegram
TELEGRAM_TOKEN = ''         # Your Telegram bot token
TELEGRAM_CHAT_ID = ''       # Your Telegram chat ID

ENABLE_EMAIL = False        # Send notifications via email
EMAIL_ADDRESS = ''          # Your email address
EMAIL_PASSWORD = ''         # Your email password

# ==============================================================================
# SAFETY LIMITS
# ==============================================================================
# Daily limits (ADJUSTED for M5 - more trades expected)
MAX_DAILY_LOSS = 100.0      # Stop trading if daily loss exceeds this (in account currency)
MAX_DAILY_TRADES = 30       # Maximum trades per day (INCREASED for M5)
MAX_DAILY_LOSS_PERCENT = 5.0  # Stop if account loses X% in a day

# Drawdown protection
MAX_DRAWDOWN_PERCENT = 10.0  # Pause trading if drawdown exceeds X%

# Account protection
MIN_ACCOUNT_BALANCE = 100.0  # Stop trading if balance falls below this

# ==============================================================================
# BACKTESTING (for future development)
# ==============================================================================
BACKTEST_MODE = False       # Run in backtest mode (simulated trading)
BACKTEST_START_DATE = '2024-01-01'
BACKTEST_END_DATE = '2024-12-31'

# ==============================================================================
# BUILD CONFIG DICTIONARY
# ==============================================================================
def get_config():
    """Return configuration dictionary"""
    return {
        # Symbols and timeframe
        'symbols': SYMBOLS,
        'timeframe': TIMEFRAME,
        
        # Risk management
        'risk_percent': RISK_PERCENT,
        'reward_ratio': REWARD_RATIO,
        'lot_size': DEFAULT_LOT_SIZE,
        'use_dynamic_sizing': USE_DYNAMIC_SIZING,
        'max_lot_size': MAX_LOT_SIZE,
        'min_lot_size': MIN_LOT_SIZE,
        
        # Split orders
        'use_split_orders': USE_SPLIT_ORDERS,
        'num_positions': NUM_POSITIONS,
        'tp_levels': TP_LEVELS,
        'partial_close_percent': PARTIAL_CLOSE_PERCENT,
        'max_lot_per_order': MAX_LOT_PER_ORDER,
        
        # Adaptive risk management
        'use_adaptive_risk': USE_ADAPTIVE_RISK,
        'trend_strength_period': TREND_STRENGTH_PERIOD,
        'adx_strong_trend': ADX_STRONG_TREND,
        'adx_ranging': ADX_RANGING,
        'trend_consistency_high': TREND_CONSISTENCY_HIGH,
        'volatility_high': VOLATILITY_HIGH,
        'min_trade_confidence': MIN_TRADE_CONFIDENCE,
        'max_risk_multiplier': MAX_RISK_MULTIPLIER,
        'min_risk_multiplier': MIN_RISK_MULTIPLIER,
        
        # Strategy parameters
        'fast_ma_period': FAST_MA_PERIOD,
        'slow_ma_period': SLOW_MA_PERIOD,
        'ma_type': MA_TYPE,
        'wait_for_confirmation': WAIT_FOR_CONFIRMATION,
        
        # ATR settings
        'atr_period': ATR_PERIOD,
        'atr_multiplier': ATR_MULTIPLIER_SL,
        'min_atr_value': MIN_ATR_VALUE,
        'max_atr_value': MAX_ATR_VALUE,
        
        # Trailing settings
        'enable_trailing_stop': ENABLE_TRAILING_STOP,
        'trail_activation': TRAIL_ACTIVATION_ATR,
        'trail_distance': TRAIL_DISTANCE_ATR,
        'trail_type': TRAIL_TYPE,
        'trail_percent': TRAIL_PERCENT,
        'breakeven_activation_pips': BREAKEVEN_ACTIVATION_PIPS,
        'breakeven_plus_pips': BREAKEVEN_PLUS_PIPS,
        'trail_start_pips': TRAIL_START_PIPS,
        
        # Trailing TP
        'enable_trailing_tp': ENABLE_TRAILING_TP,
        'trailing_tp_ratio': TRAILING_TP_RATIO,
        
        # Trade management
        'magic_number': MAGIC_NUMBER,
        'max_trades_total': MAX_TRADES_TOTAL,
        'max_trades_per_symbol': MAX_TRADES_PER_SYMBOL,
        'allow_hedging': ALLOW_HEDGING,
        
        # Trading hours
        'enable_trading_hours': ENABLE_TRADING_HOURS,
        'trading_start_hour': TRADING_START_HOUR,
        'trading_end_hour': TRADING_END_HOUR,
        'trading_days': TRADING_DAYS,
        
        # Filters
        'use_trend_filter': USE_TREND_FILTER,
        'trend_timeframe': TREND_TIMEFRAME,
        'trend_ma_period': TREND_MA_PERIOD,
        'use_volume_filter': USE_VOLUME_FILTER,
        'min_volume_ma': MIN_VOLUME_MA,
        'avoid_news_trading': AVOID_NEWS_TRADING,
        'news_buffer_minutes': NEWS_BUFFER_MINUTES,
        
        # Performance
        'update_interval': UPDATE_INTERVAL,
        'log_level': LOG_LEVEL,
        'save_trade_history': SAVE_TRADE_HISTORY,
        
        # Notifications
        'enable_telegram': ENABLE_TELEGRAM,
        'telegram_token': TELEGRAM_TOKEN,
        'telegram_chat_id': TELEGRAM_CHAT_ID,
        'enable_email': ENABLE_EMAIL,
        'email_address': EMAIL_ADDRESS,
        'email_password': EMAIL_PASSWORD,
        
        # Safety limits
        'max_daily_loss': MAX_DAILY_LOSS,
        'max_daily_trades': MAX_DAILY_TRADES,
        'max_daily_loss_percent': MAX_DAILY_LOSS_PERCENT,
        'max_drawdown_percent': MAX_DRAWDOWN_PERCENT,
        'min_account_balance': MIN_ACCOUNT_BALANCE,
        
        # Backtesting
        'backtest_mode': BACKTEST_MODE,
        'backtest_start_date': BACKTEST_START_DATE,
        'backtest_end_date': BACKTEST_END_DATE,
    }


if __name__ == "__main__":
    import json
    config = get_config()
    print("Current Configuration:")
    print(json.dumps({k: str(v) for k, v in config.items()}, indent=2))
