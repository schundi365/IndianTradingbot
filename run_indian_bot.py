"""
Indian Market Trading Bot Launcher
Run this script to start the bot with Kite Connect or Paper Trading
"""

import sys
import os
import json
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from indian_trading_bot import IndianTradingBot
from kite_adapter import KiteAdapter
from paper_trading_adapter import PaperTradingAdapter


def load_config(config_path='configs/_current.json'):
    """Load configuration from JSON file"""
    if not os.path.exists(config_path):
        print(f"Error: Configuration file not found: {config_path}")
        print("Please create a configuration using the dashboard or copy a sample config.")
        sys.exit(1)
    
    with open(config_path, 'r') as f:
        return json.load(f)


def display_config(config):
    """Display configuration summary"""
    print("Configuration:")
    print(f"  Name: {config.get('name', 'Unnamed')}")
    print(f"  Strategy: {config.get('strategy', 'trend_following')}")
    print(f"  Broker: {config.get('broker', 'paper')}")
    print(f"  Paper Trading: {config.get('paper_trading', True)}")
    print(f"  Timeframe: {config.get('timeframe', '5min')}")
    print(f"  Risk per trade: {config.get('risk_per_trade', 1.0)}%")
    print(f"  Max positions: {config.get('max_positions', 3)}")
    
    # Display instruments
    instruments = config.get('instruments', [])
    if instruments:
        print(f"  Instruments ({len(instruments)}):")
        for inst in instruments[:5]:  # Show first 5
            symbol = inst.get('symbol', 'Unknown')
            exchange = inst.get('exchange', 'NSE')
            print(f"    - {symbol} ({exchange})")
        if len(instruments) > 5:
            print(f"    ... and {len(instruments) - 5} more")
    else:
        print("  Instruments: None configured")
    
    print()


def create_broker_adapter(config):
    """Create appropriate broker adapter based on configuration"""
    broker_type = config.get('broker', 'paper').lower()
    paper_trading = config.get('paper_trading', True)
    
    # Force paper trading if explicitly enabled
    if paper_trading:
        print("Using Paper Trading mode (no real trades)")
        return PaperTradingAdapter(config)
    
    # Use real broker
    if broker_type == 'kite':
        print("Using Kite Connect (LIVE TRADING)")
        
        # Check for access token
        token_file = 'kite_token.json'
        if not os.path.exists(token_file):
            print(f"\nError: Kite access token not found!")
            print(f"Please run 'python kite_login.py' first to authenticate.")
            sys.exit(1)
        
        # Load token
        with open(token_file, 'r') as f:
            token_data = json.load(f)
        
        access_token = token_data.get('access_token')
        
        if not access_token:
            print("\nError: Invalid token file!")
            print("Please run 'python kite_login.py' to re-authenticate.")
            sys.exit(1)
        
        # Get API key from kite_login.py or environment
        api_key = os.environ.get('KITE_API_KEY', 'l2b10dmr6dfo1bqb')
        
        return KiteAdapter(api_key, access_token)
    
    else:
        print(f"Unknown broker type: {broker_type}, using Paper Trading")
        return PaperTradingAdapter(config)


def main():
    print("=" * 70)
    print("INDIAN MARKET AUTOMATED TRADING BOT")
    print("=" * 70)
    print()
    
    # Load configuration
    config_path = sys.argv[1] if len(sys.argv) > 1 else 'configs/_current.json'
    
    try:
        config = load_config(config_path)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)
    
    # Display configuration
    display_config(config)
    
    # Create broker adapter
    try:
        broker_adapter = create_broker_adapter(config)
    except Exception as e:
        print(f"Error creating broker adapter: {e}")
        sys.exit(1)
    
    # Confirmation
    if not config.get('paper_trading', True):
        print("⚠️  WARNING: LIVE TRADING MODE - REAL MONEY AT RISK ⚠️")
        print()
        response = input("Are you sure you want to start LIVE trading? (type 'YES' to confirm): ")
        if response != 'YES':
            print("Bot startup cancelled.")
            sys.exit(0)
    else:
        response = input("Start bot in paper trading mode? (yes/no): ").lower()
        if response not in ['yes', 'y']:
            print("Bot startup cancelled.")
            sys.exit(0)
    
    print()
    print("Starting bot...")
    print("Press Ctrl+C to stop the bot")
    print("=" * 70)
    print()
    
    # Convert config symbols to match broker adapter format
    # The config has 'instruments' list, but bot expects 'symbols' list
    if 'instruments' in config and 'symbols' not in config:
        config['symbols'] = [inst['symbol'] for inst in config['instruments']]
    
    # Create and run bot
    try:
        bot = IndianTradingBot(config, broker_adapter)
        bot.run()
    except KeyboardInterrupt:
        print("\n\nBot stopped by user.")
    except Exception as e:
        print(f"\n\nERROR: {str(e)}")
        print("Check indian_trading_bot.log for details")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
