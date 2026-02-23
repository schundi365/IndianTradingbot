"""
Configuration for Indian Market Web Dashboard
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Dashboard configuration
DASHBOARD_CONFIG = {
    # Server settings
    "host": os.getenv("DASHBOARD_HOST", "127.0.0.1"),
    "port": int(os.getenv("DASHBOARD_PORT", "8080")),
    "debug": os.getenv("DASHBOARD_DEBUG", "False").lower() == "true",
    
    # Security
    "secret_key": os.getenv("FLASK_SECRET_KEY", "dev-secret-key-change-in-production"),
    "encryption_key": os.getenv("ENCRYPTION_KEY", None),  # For credential encryption
    
    # Session
    "session_timeout": int(os.getenv("SESSION_TIMEOUT", "3600")),  # 1 hour
    
    # Directories
    "cache_dir": BASE_DIR / "data" / "cache",
    "config_dir": BASE_DIR / "configs",
    "log_dir": BASE_DIR / "logs",
    "credentials_dir": BASE_DIR / "data" / "credentials",
    
    # Auto-refresh
    "auto_refresh_interval": int(os.getenv("AUTO_REFRESH_INTERVAL", "5")),  # 5 seconds
    
    # Instrument cache
    "instrument_cache_ttl": int(os.getenv("INSTRUMENT_CACHE_TTL", "86400")),  # 24 hours
    
    # Rate limiting
    "rate_limit_enabled": os.getenv("RATE_LIMIT_ENABLED", "True").lower() == "true",
    "rate_limit_per_minute": int(os.getenv("RATE_LIMIT_PER_MINUTE", "60")),
    
    # Logging
    "log_level": os.getenv("LOG_LEVEL", "INFO"),
    "log_file": "dashboard.log",
}

# Broker configurations
BROKER_CONFIGS = {
    "kite": {
        "name": "Kite Connect",
        "logo": "/static/logos/kite.png",
        "oauth_enabled": True,
        "oauth_url": "https://kite.zerodha.com/connect/login",
        "redirect_url": "http://127.0.0.1:8080/api/broker/oauth/callback",
    },
    "alice_blue": {
        "name": "Alice Blue",
        "logo": "/static/logos/alice.png",
        "oauth_enabled": False,
    },
    "angel_one": {
        "name": "Angel One",
        "logo": "/static/logos/angel.png",
        "oauth_enabled": False,
    },
    "upstox": {
        "name": "Upstox",
        "logo": "/static/logos/upstox.png",
        "oauth_enabled": True,
    },
    "paper": {
        "name": "Paper Trading",
        "logo": "/static/logos/paper.png",
        "oauth_enabled": False,
    },
}

# Credential form fields for each broker
CREDENTIAL_FORMS = {
    "kite": [
        {
            "name": "api_key",
            "type": "text",
            "label": "API Key",
            "placeholder": "Enter your Kite API Key",
            "value": os.getenv("KITE_API_KEY", ""),
            "required": True,
            "minlength": 10,
            "help": "Get your API Key from https://kite.zerodha.com/apps"
        },
        {
            "name": "api_secret",
            "type": "password",
            "label": "API Secret",
            "placeholder": "Enter your Kite API Secret",
            "required": True,
            "minlength": 10,
            "help": "Keep this secret and never share it with anyone"
        },
        {
            "name": "oauth_button",
            "type": "button",
            "label": "Login with Kite",
            "action": "oauth",
            "help": "Alternative: Click to authenticate via Kite Connect OAuth"
        }
    ],
    "alice_blue": [
        {
            "name": "user_id",
            "type": "text",
            "label": "User ID",
            "placeholder": "Enter your Alice Blue User ID",
            "required": True,
            "help": "Your Alice Blue trading account user ID"
        },
        {
            "name": "api_key",
            "type": "text",
            "label": "API Key",
            "placeholder": "Enter your Alice Blue API Key",
            "required": True,
            "minlength": 10,
            "help": "Get your API Key from Alice Blue developer portal"
        }
    ],
    "angel_one": [
        {
            "name": "client_id",
            "type": "text",
            "label": "Client ID",
            "placeholder": "Enter your Angel One Client ID",
            "required": True,
            "help": "Your Angel One trading account client ID"
        },
        {
            "name": "password",
            "type": "password",
            "label": "Password",
            "placeholder": "Enter your password",
            "required": True,
            "minlength": 6,
            "help": "Your Angel One account password"
        },
        {
            "name": "totp",
            "type": "text",
            "label": "TOTP",
            "placeholder": "Enter 6-digit TOTP",
            "required": True,
            "pattern": "\\d{6}",
            "maxlength": 6,
            "help": "Time-based One-Time Password from your authenticator app (e.g., Google Authenticator)"
        }
    ],
    "upstox": [
        {
            "name": "api_key",
            "type": "text",
            "label": "API Key",
            "placeholder": "Enter your Upstox API Key",
            "required": True,
            "minlength": 10,
            "help": "Get your API Key from Upstox developer console"
        },
        {
            "name": "api_secret",
            "type": "password",
            "label": "API Secret",
            "placeholder": "Enter your Upstox API Secret",
            "required": True,
            "minlength": 10,
            "help": "Keep this secret and never share it"
        },
        {
            "name": "redirect_uri",
            "type": "text",
            "label": "Redirect URI",
            "placeholder": "http://127.0.0.1:8080/callback",
            "required": True,
            "help": "Must match the redirect URI configured in your Upstox app settings"
        }
    ],
    "paper": []  # No credentials needed for paper trading
}

# Preset configurations
PRESET_CONFIGS = {
    "nifty_futures": {
        "name": "NIFTY 50 Futures",
        "description": "Trend following strategy for NIFTY 50 futures with 15-minute timeframe. Optimized for liquid NIFTY contracts with conservative risk management suitable for intraday trading.",
        "broker": "kite",
        "instruments": [
            {
                "symbol": "NIFTY24JANFUT",
                "name": "NIFTY 50 JAN FUT",
                "exchange": "NFO",
                "instrument_type": "FUT",
                "lot_size": 50,
                "tick_size": 0.05
            }
        ],
        "strategy": "trend_following",
        "timeframe": "15min",
        "risk_per_trade": 1.0,  # 1% risk per trade - conservative for futures
        "max_positions": 2,  # Max 2 NIFTY positions to avoid overexposure
        "max_daily_loss": 3.0,  # Stop trading if 3% daily loss reached
        "trading_hours": {
            "start": "09:15",  # Market open
            "end": "15:15"     # Close positions 15 min before market close
        },
        "indicator_period": 20,  # 20-period moving average for trend detection
        "position_sizing": "risk_based",  # Size positions based on risk percentage
        "base_position_size": 100000,  # ₹1 lakh base capital per position
        "take_profit": 1.5,  # 1.5% take profit target
        "stop_loss": 0.75,  # 0.75% stop loss (2:1 reward-risk ratio)
        "paper_trading": True,  # Start with paper trading for testing
        "log_level": "INFO",
        "data_refresh_interval": 60,  # Refresh data every 60 seconds
        "enable_notifications": True,
        # Additional NIFTY-specific parameters
        "min_volume": 100000,  # Minimum volume for entry
        "atr_period": 14,  # ATR period for volatility-based stops
        "trailing_stop": True,  # Enable trailing stop loss
        "trailing_stop_activation": 1.0,  # Activate trailing stop at 1% profit
        "trailing_stop_distance": 0.5  # Trail by 0.5%
    },
    "banknifty_futures": {
        "name": "BANKNIFTY Futures",
        "description": "Momentum strategy for BANKNIFTY futures with 15-minute timeframe. Designed for highly liquid BANKNIFTY contracts with higher volatility tolerance. Suitable for experienced traders comfortable with banking sector movements.",
        "broker": "kite",
        "instruments": [
            {
                "symbol": "BANKNIFTY24JANFUT",
                "name": "BANKNIFTY JAN FUT",
                "exchange": "NFO",
                "instrument_type": "FUT",
                "lot_size": 25,
                "tick_size": 0.05
            }
        ],
        "strategy": "momentum",
        "timeframe": "15min",
        "risk_per_trade": 1.5,  # 1.5% risk per trade - higher than NIFTY due to volatility
        "max_positions": 2,  # Max 2 BANKNIFTY positions to manage risk
        "max_daily_loss": 4.0,  # Stop trading if 4% daily loss reached
        "trading_hours": {
            "start": "09:15",  # Market open
            "end": "15:15"     # Close positions 15 min before market close
        },
        "indicator_period": 14,  # 14-period for faster momentum detection
        "position_sizing": "risk_based",  # Size positions based on risk percentage
        "base_position_size": 75000,  # ₹75k base capital per position (lower due to higher volatility)
        "take_profit": 2.5,  # 2.5% take profit target (higher due to volatility)
        "stop_loss": 1.5,  # 1.5% stop loss (maintains ~1.67:1 reward-risk ratio)
        "paper_trading": True,  # Start with paper trading for testing
        "log_level": "INFO",
        "data_refresh_interval": 60,  # Refresh data every 60 seconds
        "enable_notifications": True,
        # Additional BANKNIFTY-specific parameters
        "min_volume": 50000,  # Minimum volume for entry (lower than NIFTY, still liquid)
        "atr_period": 14,  # ATR period for volatility-based stops
        "trailing_stop": True,  # Enable trailing stop loss
        "trailing_stop_activation": 1.5,  # Activate trailing stop at 1.5% profit
        "trailing_stop_distance": 0.75,  # Trail by 0.75% (wider for volatility)
        "momentum_threshold": 0.5,  # Minimum momentum strength for entry
        "rsi_period": 14,  # RSI period for momentum confirmation
        "rsi_overbought": 70,  # RSI overbought level
        "rsi_oversold": 30  # RSI oversold level
    },
    "equity_intraday": {
        "name": "Equity Intraday",
        "description": "Mean reversion strategy for liquid NSE/BSE stocks with 15-minute timeframe. Optimized for high-volume equities with tight spreads. Suitable for capturing intraday price reversions in liquid stocks like RELIANCE, TCS, INFY, HDFC Bank, etc. Conservative risk management with multiple positions for diversification.",
        "broker": "kite",
        "instruments": [
            {
                "symbol": "RELIANCE",
                "name": "Reliance Industries Ltd",
                "exchange": "NSE",
                "instrument_type": "EQ",
                "lot_size": 1,
                "tick_size": 0.05
            },
            {
                "symbol": "TCS",
                "name": "Tata Consultancy Services Ltd",
                "exchange": "NSE",
                "instrument_type": "EQ",
                "lot_size": 1,
                "tick_size": 0.05
            },
            {
                "symbol": "INFY",
                "name": "Infosys Ltd",
                "exchange": "NSE",
                "instrument_type": "EQ",
                "lot_size": 1,
                "tick_size": 0.05
            },
            {
                "symbol": "HDFCBANK",
                "name": "HDFC Bank Ltd",
                "exchange": "NSE",
                "instrument_type": "EQ",
                "lot_size": 1,
                "tick_size": 0.05
            },
            {
                "symbol": "ICICIBANK",
                "name": "ICICI Bank Ltd",
                "exchange": "NSE",
                "instrument_type": "EQ",
                "lot_size": 1,
                "tick_size": 0.05
            }
        ],
        "strategy": "mean_reversion",
        "timeframe": "15min",
        "risk_per_trade": 0.5,  # 0.5% risk per trade - very conservative for equities
        "max_positions": 5,  # Max 5 positions for diversification across stocks
        "max_daily_loss": 2.0,  # Stop trading if 2% daily loss reached
        "trading_hours": {
            "start": "09:30",  # Start 15 min after market open to avoid volatility
            "end": "15:00"     # Close positions 30 min before market close
        },
        "indicator_period": 20,  # 20-period Bollinger Bands for mean reversion
        "position_sizing": "percentage",  # Percentage-based position sizing
        "base_position_size": 20000,  # ₹20k per position (allows 5 positions with ₹1L capital)
        "take_profit": 1.5,  # 1.5% take profit target (realistic for intraday equities)
        "stop_loss": 0.75,  # 0.75% stop loss (2:1 reward-risk ratio)
        "paper_trading": True,  # Start with paper trading for testing
        "log_level": "INFO",
        "data_refresh_interval": 60,  # Refresh data every 60 seconds
        "enable_notifications": True,
        # Additional equity-specific parameters
        "min_volume": 500000,  # Minimum daily volume for liquidity (5 lakh shares)
        "min_price": 100,  # Minimum stock price (₹100) to avoid penny stocks
        "max_price": 5000,  # Maximum stock price (₹5000) for affordability
        "bollinger_std": 2.0,  # Bollinger Bands standard deviation
        "rsi_period": 14,  # RSI period for mean reversion confirmation
        "rsi_overbought": 70,  # RSI overbought level (sell signal)
        "rsi_oversold": 30,  # RSI oversold level (buy signal)
        "atr_period": 14,  # ATR period for volatility measurement
        "max_spread_percent": 0.2,  # Maximum bid-ask spread (0.2% for tight spreads)
        "trailing_stop": False,  # Disable trailing stop for mean reversion
        "scale_in": False,  # No scaling in for intraday equity trades
        "scale_out": True,  # Enable partial profit taking
        "scale_out_levels": [0.75, 1.5],  # Take 50% profit at 0.75%, rest at 1.5%
        "avoid_first_last_candle": True,  # Avoid trading in first/last 5-min candles
        "min_reversion_distance": 1.5,  # Minimum distance from mean (in std devs) for entry
        "max_holding_time": 180  # Maximum holding time in minutes (3 hours)
    },
    "options_trading": {
        "name": "Options Trading",
        "description": "Options selling strategy for NIFTY/BANKNIFTY with delta-neutral approach. Focuses on premium collection through credit spreads and iron condors. Designed for weekly options with theta decay advantage. Requires understanding of options Greeks and risk management. Conservative position sizing with defined risk per trade.",
        "broker": "kite",
        "instruments": [
            {
                "symbol": "NIFTY24JAN21000CE",
                "name": "NIFTY 21000 CE",
                "exchange": "NFO",
                "instrument_type": "CE",
                "lot_size": 50,
                "tick_size": 0.05,
                "strike": 21000,
                "expiry": "2024-01-25"
            },
            {
                "symbol": "NIFTY24JAN21000PE",
                "name": "NIFTY 21000 PE",
                "exchange": "NFO",
                "instrument_type": "PE",
                "lot_size": 50,
                "tick_size": 0.05,
                "strike": 21000,
                "expiry": "2024-01-25"
            }
        ],
        "strategy": "options_selling",
        "timeframe": "15min",
        "risk_per_trade": 2.0,  # 2% risk per trade - higher than futures due to defined risk
        "max_positions": 3,  # Max 3 option positions (e.g., 1 iron condor = 4 legs, but counts as 1 position)
        "max_daily_loss": 5.0,  # Stop trading if 5% daily loss reached
        "trading_hours": {
            "start": "09:30",  # Start after initial volatility settles
            "end": "15:00"     # Close positions 30 min before expiry on expiry day
        },
        "indicator_period": 20,  # 20-period for volatility assessment
        "position_sizing": "fixed",  # Fixed position sizing for options
        "base_position_size": 30000,  # ₹30k per position (1-2 lots depending on premium)
        "take_profit": 50.0,  # 50% of premium collected (e.g., sold at ₹100, buy back at ₹50)
        "stop_loss": 200.0,  # 200% of premium (e.g., sold at ₹100, exit at ₹200) - defined risk
        "paper_trading": True,  # Start with paper trading for testing
        "log_level": "INFO",
        "data_refresh_interval": 60,  # Refresh data every 60 seconds
        "enable_notifications": True,
        # Options-specific parameters
        "option_type": "both",  # Trade both CE and PE (for spreads/iron condors)
        "strategy_type": "credit_spread",  # credit_spread, iron_condor, or naked_selling
        "min_premium": 50,  # Minimum premium to collect (₹50 per lot)
        "max_premium": 200,  # Maximum premium (avoid deep ITM options)
        "min_days_to_expiry": 0,  # Minimum days to expiry (0 = can trade on expiry day)
        "max_days_to_expiry": 7,  # Maximum days to expiry (weekly options)
        "delta_range": [0.15, 0.35],  # Target delta range for sold options (OTM)
        "iv_percentile_min": 30,  # Minimum IV percentile for entry (sell when IV is elevated)
        "iv_percentile_max": 100,  # Maximum IV percentile
        "spread_width": 100,  # Spread width in points (e.g., 21000-21100 CE spread)
        "max_loss_per_spread": 5000,  # Maximum loss per spread (₹5000)
        "profit_target_percent": 50,  # Close at 50% of max profit
        "adjustment_threshold": 150,  # Adjust position if loss reaches 150% of premium
        "close_before_expiry_minutes": 60,  # Close positions 60 min before expiry
        "avoid_earnings": True,  # Avoid trading around major events
        "max_vega_exposure": 10000,  # Maximum vega exposure across all positions
        "max_theta_collection": 5000,  # Target theta collection per day
        "hedge_delta": True,  # Hedge delta exposure with futures if needed
        "delta_hedge_threshold": 0.3,  # Hedge when portfolio delta exceeds ±0.3
        "roll_options": True,  # Roll options before expiry if profitable
        "roll_days_before_expiry": 2,  # Roll 2 days before expiry
        "min_credit_received": 100,  # Minimum credit for credit spreads (₹100 per lot)
        "commission_per_lot": 40,  # Estimated commission per lot (₹40)
        "slippage_percent": 0.5,  # Expected slippage (0.5%)
        "margin_requirement_multiplier": 1.5,  # Keep 1.5x margin requirement as buffer
        "use_stop_loss_orders": True,  # Use stop loss orders for risk management
        "trailing_stop": False,  # No trailing stop for options (use profit target instead)
        "scale_in": False,  # No scaling in for options
        "scale_out": True,  # Scale out at profit targets
        "scale_out_levels": [25, 50, 75],  # Take profits at 25%, 50%, 75% of max profit
        "max_spread_width_percent": 5,  # Maximum spread width as % of underlying price
        "underlying_symbol": "NIFTY",  # Underlying for options
        "monitor_underlying": True,  # Monitor underlying price movement
        "underlying_stop_loss_percent": 3.0,  # Exit if underlying moves 3% against position
        "rebalance_frequency": "daily",  # Rebalance portfolio daily
        "max_portfolio_delta": 0.5,  # Maximum portfolio delta (±0.5)
        "max_portfolio_vega": 15000,  # Maximum portfolio vega
        "target_theta": 3000,  # Target daily theta collection (₹3000)
        "greek_calculation_interval": 300  # Recalculate Greeks every 5 minutes
    }
}


def ensure_directories():
    """Ensure all required directories exist"""
    for key in ["cache_dir", "config_dir", "log_dir", "credentials_dir"]:
        dir_path = DASHBOARD_CONFIG[key]
        os.makedirs(dir_path, exist_ok=True)


def get_config(key: str, default=None):
    """Get configuration value"""
    return DASHBOARD_CONFIG.get(key, default)


def get_broker_config(broker: str):
    """Get broker configuration"""
    return BROKER_CONFIGS.get(broker)


def get_credential_form(broker: str):
    """Get credential form fields for broker"""
    return CREDENTIAL_FORMS.get(broker, [])


def get_preset_config(preset: str):
    """Get preset configuration"""
    return PRESET_CONFIGS.get(preset)


# Initialize directories on import
ensure_directories()
