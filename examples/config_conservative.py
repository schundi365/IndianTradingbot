"""
Conservative Trading Configuration
Lower risk, tighter stops, smaller positions
Good for: Beginners, volatile markets, smaller accounts
"""

import MetaTrader5 as mt5

# Copy this to src/config.py and modify as needed

SYMBOLS = ['XAUUSD']  # Trade only Gold
TIMEFRAME = mt5.TIMEFRAME_H4  # 4-hour timeframe (less noise)

# Conservative risk management
RISK_PERCENT = 0.5  # Risk only 0.5% per trade
REWARD_RATIO = 1.5  # Conservative 1:1.5 ratio
MAX_LOT_SIZE = 0.1  # Small maximum position

# Split orders - take profits early
USE_SPLIT_ORDERS = True
NUM_POSITIONS = 3
TP_LEVELS = [1.0, 1.5, 2.0]  # Conservative targets
PARTIAL_CLOSE_PERCENT = [50, 30, 20]  # Lock in 50% early

# Adaptive risk - strict filtering
USE_ADAPTIVE_RISK = True
MIN_TRADE_CONFIDENCE = 0.70  # Only take high-confidence trades (70%+)

# Tighter stops
ATR_MULTIPLIER_SL = 1.5  # Tighter stop loss

# Trailing - protect profits quickly
ENABLE_TRAILING_STOP = True
TRAIL_ACTIVATION_ATR = 1.0  # Activate trailing sooner
TRAIL_DISTANCE_ATR = 0.8  # Trail closer to price

# Safety limits
MAX_TRADES_TOTAL = 2  # Maximum 2 trades at once
MAX_DAILY_LOSS = 50.0  # Stop after $50 loss
MAX_DAILY_TRADES = 5  # Max 5 trades per day
