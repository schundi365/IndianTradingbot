"""
Configuration file for MT5 Trading Bot
Customize these settings for your trading strategy
"""

import MetaTrader5 as mt5

# ==============================================================================
# TRADING SYMBOLS
# ==============================================================================
# Add any MT5 symbols you want to trade
SYMBOLS = ['XAUUSD', 'GBPUSD']  # Example: Major Forex pairs

# You can trade any symbols your broker supports:
# Forex pairs: 'EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'NZDUSD'
# Commodities: 'XAUUSD' (Gold), 'XAGUSD' (Silver), 'XTIUSD' (Oil), 'XBRUSD' (Brent)
# Indices: 'US30' (Dow), 'US500' (S&P500), 'NAS100' (Nasdaq), 'GER40' (DAX)
# Crypto: 'BTCUSD', 'ETHUSD' (if broker supports)
# Stocks: 'AAPL', 'TSLA', 'GOOGL' (if broker supports)

# Note: Symbol names may vary by broker. Check your MT5 Market Watch for exact names.

# ==============================================================================
# TIMEFRAME SETTINGS
# ==============================================================================
TIMEFRAME = mt5.TIMEFRAME_M1  # 1-minute timeframe (EXTREMELY ACTIVE!)

# Available timeframes:
# mt5.TIMEFRAME_M1  - 1 minute (CURRENT - VERY FAST!)
# mt5.TIMEFRAME_M5  - 5 minutes
# mt5.TIMEFRAME_M15 - 15 minutes
# mt5.TIMEFRAME_M30 - 30 minutes
# mt5.TIMEFRAME_H1  - 1 hour
# mt5.TIMEFRAME_H4  - 4 hours
# mt5.TIMEFRAME_D1  - 1 day
# mt5.TIMEFRAME_W1  - 1 week

# ⚠️⚠️⚠️ CRITICAL WARNING: M1 timeframe is EXTREMELY ACTIVE ⚠️⚠️⚠️
# - Expect 100-200+ trades per day
# - Requires CONSTANT monitoring (every 5-10 minutes)
# - VERY HIGH spread costs ($20-40+/day)
# - MANY false signals (high noise)
# - NOT recommended for beginners
# - NOT recommended for automated trading
# - Requires VERY fast execution
# - High stress and time commitment

# ==============================================================================
# RISK MANAGEMENT
# ==============================================================================
RISK_PERCENT = 0.3          # Risk 0.3% per trade (VERY LOW for M1 - many trades)
REWARD_RATIO = 1.2          # Risk:Reward ratio (1:1.2 for ultra-fast timeframe)
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

# Take profit levels (Risk:Reward ratios for each position) - adjusted for M1
# Example: [1.0, 1.3, 1.8] means:
#   - Position 1 exits at 1.0x risk distance (very quick profit)
#   - Position 2 exits at 1.3x risk distance (quick)
#   - Position 3 exits at 1.8x risk distance (moderate)
TP_LEVELS = [1.0, 1.3, 1.8]  # Very realistic for M1 (was [1.2, 1.8, 2.5] for M5)

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

# Trend strength analysis (adjusted for M1)
TREND_STRENGTH_PERIOD = 20  # Period for analyzing trend consistency (was 30 for M5)

# Market condition thresholds (adjusted for M1)
ADX_STRONG_TREND = 18       # ADX above this = trending market (was 20 for M5)
ADX_RANGING = 12            # ADX below this = ranging market (was 15 for M5)
TREND_CONSISTENCY_HIGH = 60 # % of bars in same direction = strong trend (was 65)
VOLATILITY_HIGH = 1.1       # ATR ratio above this = volatile market (was 1.2)

# Trade confidence requirements
# Trade confidence requirements (adjusted for M1)
MIN_TRADE_CONFIDENCE = 0.50 # Minimum confidence score to take trade (50% for M1)
# Even lower threshold for M1 due to extreme noise
# M5 used 55%, M1 uses 50%

# Risk adjustment limits
MAX_RISK_MULTIPLIER = 1.5   # Maximum risk increase in favorable conditions
MIN_RISK_MULTIPLIER = 0.3   # Minimum risk in unfavorable conditions

# ==============================================================================
# MOVING AVERAGE STRATEGY
# ==============================================================================
# Adjusted for M1 timeframe (very short periods for ultra-fast signals)
FAST_MA_PERIOD = 5          # Fast moving average period (was 10 for M5)
SLOW_MA_PERIOD = 10         # Slow moving average period (was 20 for M5)
MA_TYPE = 'EMA'            # 'SMA' or 'EMA' (EMA essential for M1)

# Entry conditions
WAIT_FOR_CONFIRMATION = True    # Wait for price to confirm above/below MAs
MIN_MA_SEPARATION = 0.0001      # Minimum distance between MAs for signal (0 = any)

# ==============================================================================
# MACD INDICATOR (NEW - Added for M1)
# ==============================================================================
USE_MACD = True             # Enable MACD indicator for additional confirmation
MACD_FAST = 8               # Fast EMA period (standard 12, adjusted for M1)
MACD_SLOW = 17              # Slow EMA period (standard 26, adjusted for M1)
MACD_SIGNAL = 5             # Signal line period (standard 9, adjusted for M1)

# MACD filters
MACD_MIN_HISTOGRAM = 0.0    # Minimum histogram value for signal (0 = any)
REQUIRE_MACD_CONFIRMATION = True  # Require MACD to confirm MA signal

# ==============================================================================
# ATR-BASED STOP LOSS
# ==============================================================================
# Adjusted for M1 timeframe
ATR_PERIOD = 14             # Period for ATR calculation (14 periods = 14 minutes)
ATR_MULTIPLIER_SL = 1.2     # Stop Loss multiplier (VERY TIGHT for M1)

# ATR filters (adjusted for M1 volatility)
MIN_ATR_VALUE = 0.0001      # Minimum ATR to place trade (avoid low volatility)
MAX_ATR_VALUE = 999999      # Maximum ATR to place trade (avoid high volatility)

# ==============================================================================
# TRAILING STOP SETTINGS
# ==============================================================================
ENABLE_TRAILING_STOP = True

# Activation threshold (adjusted for M1)
TRAIL_ACTIVATION_ATR = 0.8  # Activate trailing very quickly on M1 (was 1.0 for M5)
# Example: If ATR=10 and this is 0.8, trailing activates after 8 points profit

# Trailing distance (adjusted for M1)
TRAIL_DISTANCE_ATR = 0.6    # Trail very close on M1 (was 0.8 for M5)
TRAIL_TYPE = 'atr'          # 'atr', 'percentage', 'swing', 'chandelier', 'breakeven'

# Percentage trailing (if TRAIL_TYPE = 'percentage')
TRAIL_PERCENT = 1.0         # Trail 1.0% from current price (was 1.5 for M5)

# Breakeven settings (if TRAIL_TYPE = 'breakeven') - adjusted for M1
BREAKEVEN_ACTIVATION_PIPS = 30   # Move to BE after this many pips (was 50)
BREAKEVEN_PLUS_PIPS = 3          # Lock in this many pips at BE (was 5)
TRAIL_START_PIPS = 50            # Start normal trailing after this profit (was 75)

# ==============================================================================
# TRAILING TAKE PROFIT SETTINGS
# ==============================================================================
ENABLE_TRAILING_TP = False  # Move TP as profit increases
TRAILING_TP_RATIO = 0.5     # Give back 50% of unrealized profit before hitting TP

# ==============================================================================
# TRADE MANAGEMENT
# ==============================================================================
MAGIC_NUMBER = 234000       # Unique identifier for bot trades (change if running multiple bots)

# Maximum trades (adjusted for M1 - VERY active)
MAX_TRADES_TOTAL = 10       # Maximum total open trades (was 8 for M5)
MAX_TRADES_PER_SYMBOL = 3   # Maximum trades per symbol (was 2 for M5)
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
# Trend filter (adjusted for M1)
USE_TREND_FILTER = True     # Only trade in direction of higher timeframe trend
TREND_TIMEFRAME = mt5.TIMEFRAME_M15  # Use M15 for trend on M1 (was H1 for M5)
TREND_MA_PERIOD = 20        # MA period for trend (was 50 for M5)

# Volume filter
USE_VOLUME_FILTER = False   # Filter trades by volume
MIN_VOLUME_MA = 1.2         # Current volume must be X times average volume

# News filter
AVOID_NEWS_TRADING = False  # Pause trading during high-impact news
NEWS_BUFFER_MINUTES = 30    # Don't trade X minutes before/after news

# ==============================================================================
# PERFORMANCE & MONITORING
# ==============================================================================
UPDATE_INTERVAL = 10        # Check for signals every X seconds (10 = 10 seconds for M1)
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
# Daily limits (ADJUSTED for M1 - MANY trades expected)
MAX_DAILY_LOSS = 100.0      # Stop trading if daily loss exceeds this (in account currency)
MAX_DAILY_TRADES = 100      # Maximum trades per day (VERY HIGH for M1)
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
        
        # MACD parameters
        'use_macd': USE_MACD,
        'macd_fast': MACD_FAST,
        'macd_slow': MACD_SLOW,
        'macd_signal': MACD_SIGNAL,
        'macd_min_histogram': MACD_MIN_HISTOGRAM,
        'require_macd_confirmation': REQUIRE_MACD_CONFIRMATION,
        
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
