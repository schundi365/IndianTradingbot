#!/usr/bin/env python3
"""
Diagnose symbol processing issues - check which symbols are being processed
"""

import json
import sys
import os

# Add src directory to path
sys.path.append('src')

from config_manager import ConfigManager
from mt5_trading_bot import MT5TradingBot

def check_config_symbols():
    """Check symbols in configuration"""
    print("🔍 CHECKING CONFIGURATION SYMBOLS")
    print("=" * 50)
    
    # Load config from file
    try:
        with open('bot_config.json', 'r') as f:
            config = json.load(f)
        
        symbols = config.get('symbols', [])
        print(f"📊 Symbols in bot_config.json: {len(symbols)}")
        for i, symbol in enumerate(symbols, 1):
            print(f"  {i:2d}. {symbol}")
        
        return config
        
    except Exception as e:
        print(f"❌ Error loading config: {str(e)}")
        return None

def check_config_manager():
    """Check symbols from ConfigManager"""
    print("\n🔍 CHECKING CONFIG MANAGER")
    print("=" * 50)
    
    try:
        config_manager = ConfigManager()
        config = config_manager.get_config()
        
        symbols = config.get('symbols', [])
        print(f"📊 Symbols from ConfigManager: {len(symbols)}")
        for i, symbol in enumerate(symbols, 1):
            print(f"  {i:2d}. {symbol}")
        
        return config
        
    except Exception as e:
        print(f"❌ Error with ConfigManager: {str(e)}")
        return None

def check_bot_initialization():
    """Check bot initialization and symbol loading"""
    print("\n🔍 CHECKING BOT INITIALIZATION")
    print("=" * 50)
    
    try:
        # Load config
        config_manager = ConfigManager()
        config = config_manager.get_config()
        
        print(f"📊 Config loaded with {len(config.get('symbols', []))} symbols")
        
        # Try to create bot instance (without connecting to MT5)
        # We'll mock the MT5 connection to avoid errors
        import mt5_trading_bot
        
        # Temporarily disable MT5 connection
        original_connect = mt5_trading_bot.MT5TradingBot.connect
        mt5_trading_bot.MT5TradingBot.connect = lambda self: True
        
        bot = MT5TradingBot(config)
        
        print(f"📊 Bot initialized with {len(bot.symbols)} symbols:")
        for i, symbol in enumerate(bot.symbols, 1):
            print(f"  {i:2d}. {symbol}")
        
        # Restore original connect method
        mt5_trading_bot.MT5TradingBot.connect = original_connect
        
        return bot.symbols
        
    except Exception as e:
        print(f"❌ Error initializing bot: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def check_recent_logs():
    """Check recent logs for symbol processing"""
    print("\n🔍 CHECKING RECENT LOG PROCESSING")
    print("=" * 50)
    
    try:
        with open('trading_bot.log', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Find recent ANALYZING entries
        analyzing_symbols = []
        for line in reversed(lines[-1000:]):  # Check last 1000 lines
            if 'ANALYZING' in line and '║' in line:
                # Extract symbol name
                parts = line.split('ANALYZING')
                if len(parts) > 1:
                    symbol_part = parts[1].split('║')[0].strip()
                    if symbol_part and symbol_part not in analyzing_symbols:
                        analyzing_symbols.append(symbol_part)
        
        analyzing_symbols.reverse()  # Restore chronological order
        
        print(f"📊 Symbols found in recent logs: {len(analyzing_symbols)}")
        for i, symbol in enumerate(analyzing_symbols, 1):
            print(f"  {i:2d}. {symbol}")
        
        return analyzing_symbols
        
    except Exception as e:
        print(f"❌ Error reading logs: {str(e)}")
        return []

def compare_results():
    """Compare all results and identify discrepancies"""
    print("\n🎯 COMPARISON AND ANALYSIS")
    print("=" * 50)
    
    # Get all symbol lists
    config_symbols = []
    manager_symbols = []
    bot_symbols = []
    log_symbols = []
    
    # Config file
    try:
        with open('bot_config.json', 'r') as f:
            config = json.load(f)
        config_symbols = config.get('symbols', [])
    except:
        pass
    
    # Config manager
    try:
        config_manager = ConfigManager()
        config = config_manager.get_config()
        manager_symbols = config.get('symbols', [])
    except:
        pass
    
    # Bot initialization
    try:
        import mt5_trading_bot
        original_connect = mt5_trading_bot.MT5TradingBot.connect
        mt5_trading_bot.MT5TradingBot.connect = lambda self: True
        
        config_manager = ConfigManager()
        config = config_manager.get_config()
        bot = MT5TradingBot(config)
        bot_symbols = bot.symbols
        
        mt5_trading_bot.MT5TradingBot.connect = original_connect
    except:
        pass
    
    # Recent logs
    try:
        with open('trading_bot.log', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        analyzing_symbols = []
        for line in reversed(lines[-1000:]):
            if 'ANALYZING' in line and '║' in line:
                parts = line.split('ANALYZING')
                if len(parts) > 1:
                    symbol_part = parts[1].split('║')[0].strip()
                    if symbol_part and symbol_part not in analyzing_symbols:
                        analyzing_symbols.append(symbol_part)
        
        log_symbols = analyzing_symbols
    except:
        pass
    
    # Compare
    print(f"Config File:     {len(config_symbols)} symbols")
    print(f"Config Manager:  {len(manager_symbols)} symbols")
    print(f"Bot Instance:    {len(bot_symbols)} symbols")
    print(f"Recent Logs:     {len(log_symbols)} symbols")
    
    # Find missing symbols
    if config_symbols and log_symbols:
        missing_from_logs = set(config_symbols) - set(log_symbols)
        if missing_from_logs:
            print(f"\n⚠️  MISSING FROM LOGS: {len(missing_from_logs)} symbols")
            for symbol in sorted(missing_from_logs):
                print(f"  - {symbol}")
        else:
            print(f"\n✅ All config symbols found in logs")
    
    # Check for filtering
    if len(config_symbols) > len(log_symbols):
        print(f"\n🔍 POTENTIAL ISSUE: Config has {len(config_symbols)} symbols but only {len(log_symbols)} are being processed")
        print("   This suggests symbol filtering or processing limitations")

def main():
    """Main diagnostic function"""
    print("🔧 SYMBOL PROCESSING DIAGNOSTIC")
    print("=" * 60)
    
    # Check all sources
    config_symbols = check_config_symbols()
    manager_config = check_config_manager()
    bot_symbols = check_bot_initialization()
    log_symbols = check_recent_logs()
    
    # Compare and analyze
    compare_results()
    
    print("\n📋 RECOMMENDATIONS:")
    print("1. Check if all symbols are available in MT5")
    print("2. Verify symbol names are correct")
    print("3. Check for any filtering logic in the bot")
    print("4. Monitor logs for symbol-specific errors")

if __name__ == "__main__":
    main()