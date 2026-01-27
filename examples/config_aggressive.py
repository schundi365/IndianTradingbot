"""
Aggressive Trading Configuration
Higher risk, wider stops, larger positions
Good for: Experienced traders, trending markets, larger accounts
"""

import MetaTrader5 as mt5

# Copy this to src/config.py and modify as needed

SYMBOLS = ['XAUUSD', 'XAGUSD']  # Trade both Gold and Silver
TIMEFRAME = mt5.TIMEFRAME_H1  # 1-hour timeframe

# Aggressive risk management
RISK_PERCENT = 2.0  # Risk 2% per trade
REWARD_RATIO = 3.0  # Aggressive 1:3 ratio
MAX_LOT_SIZE = 1.0  # Larger maximum position

# Split orders - let winners run
USE_SPLIT_ORDERS = True
NUM_POSITIONS = 3
TP_LEVELS = [2.0, 3.5, 6.0]  # Aggressive targets
PARTIAL_CLOSE_PERCENT = [30, 30, 40]  # Keep 40% for big moves

# Adaptive risk - more trades
USE_ADAPTIVE_RISK = True
MIN_TRADE_CONFIDENCE = 0.55  # Accept more trades (55%+)

# Wider stops
ATR_MULTIPLIER_SL = 2.5  # Wider stop loss for volatility

# Trailing - let it run
ENABLE_TRAILING_STOP = True
TRAIL_ACTIVATION_ATR = 2.0  # Activate trailing later
TRAIL_DISTANCE_ATR = 1.5  # Trail further from price

# Safety limits
MAX_TRADES_TOTAL = 5  # Maximum 5 trades at once
MAX_DAILY_LOSS = 200.0  # Stop after $200 loss
MAX_DAILY_TRADES = 15  # Max 15 trades per day
