"""
Automated Launcher for MT5 Trading Bot
Run this script to start the bot automatically without confirmation
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config import get_config
from mt5_trading_bot import MT5TradingBot


def main():
    print("=" * 60)
    print("MT5 AUTOMATED TRADING BOT - AUTO START")
    print("=" * 60)
    print()
    
    # Load configuration
    config = get_config()
    
    # Display configuration
    print("Configuration:")
    print(f"  Symbols: {', '.join(config['symbols'])}")
    print(f"  Timeframe: {config['timeframe']}")
    print(f"  Risk per trade: {config['risk_percent']}%")
    print(f"  Risk:Reward ratio: 1:{config['reward_ratio']}")
    print(f"  Fast MA: {config['fast_ma_period']}, Slow MA: {config['slow_ma_period']}")
    print(f"  ATR Period: {config['atr_period']}, Multiplier: {config['atr_multiplier']}")
    print(f"  Trailing Stop: {'Enabled' if config['enable_trailing_stop'] else 'Disabled'}")
    print()
    
    # Auto-start without confirmation
    print("🚀 Starting bot automatically...")
    print("📊 Enhanced signal generation: ACTIVE")
    print("🔍 Detailed logging: ENABLED")
    print("Press Ctrl+C to stop the bot")
    print("=" * 60)
    print()
    
    # Create and run bot
    try:
        bot = MT5TradingBot(config)
        bot.run()
    except KeyboardInterrupt:
        print("\n\nBot stopped by user.")
    except Exception as e:
        print(f"\n\nERROR: {str(e)}")
        print("Check trading_bot.log for details")


if __name__ == "__main__":
    main()