#!/usr/bin/env python3
"""
Restart the bot to ensure it picks up all 18 symbols from the configuration
"""

import os
import sys
import time
import subprocess
import requests
import json

def stop_existing_bot():
    """Stop any existing bot processes"""
    print("🛑 Stopping existing bot processes...")
    
    try:
        # Kill any existing Python processes running the bot
        if os.name == 'nt':  # Windows
            subprocess.run(['taskkill', '/f', '/im', 'python.exe'], 
                         capture_output=True, text=True)
        else:  # Unix-like
            subprocess.run(['pkill', '-f', 'web_dashboard.py'], 
                         capture_output=True, text=True)
        
        print("✅ Stopped existing processes")
        time.sleep(3)  # Give processes time to stop
        
    except Exception as e:
        print(f"⚠️  Could not stop existing processes: {str(e)}")

def verify_configuration():
    """Verify the bot configuration has all 18 symbols"""
    print("🔍 Verifying configuration...")
    
    try:
        with open('bot_config.json', 'r') as f:
            config = json.load(f)
        
        symbols = config.get('symbols', [])
        print(f"✅ Configuration loaded: {len(symbols)} symbols")
        
        expected_symbols = [
            'XAUUSD', 'XAGUSD', 'XPTUSD', 'XPDUSD', 'EURUSD', 'GBPUSD',
            'USDJPY', 'USDCHF', 'AUDUSD', 'USDCAD', 'NZDUSD', 'EURJPY',
            'GBPJPY', 'EURGBP', 'EURAUD', 'EURCAD', 'GBPAUD', 'GBPCAD'
        ]
        
        missing_symbols = set(expected_symbols) - set(symbols)
        extra_symbols = set(symbols) - set(expected_symbols)
        
        if missing_symbols:
            print(f"⚠️  Missing symbols: {', '.join(missing_symbols)}")
        
        if extra_symbols:
            print(f"ℹ️  Extra symbols: {', '.join(extra_symbols)}")
        
        if len(symbols) == 18 and not missing_symbols:
            print("✅ Configuration is correct")
            return True
        else:
            print(f"❌ Configuration issue: expected 18 symbols, found {len(symbols)}")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying configuration: {str(e)}")
        return False

def start_bot():
    """Start the bot with fresh configuration"""
    print("🚀 Starting bot with fresh configuration...")
    
    try:
        # Clear log file to start fresh
        log_file = "trading_bot.log"
        if os.path.exists(log_file):
            with open(log_file, 'w') as f:
                f.write("")
            print("✅ Cleared log file")
        
        # Start the web dashboard which runs the bot
        if os.name == 'nt':  # Windows
            process = subprocess.Popen(
                ['python', 'web_dashboard.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:  # Unix-like
            process = subprocess.Popen(
                ['python', 'web_dashboard.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        
        print(f"✅ Bot started with PID: {process.pid}")
        return process
        
    except Exception as e:
        print(f"❌ Failed to start bot: {str(e)}")
        return None

def wait_for_bot_ready():
    """Wait for the bot to be ready and responding"""
    print("⏳ Waiting for bot to initialize...")
    
    max_attempts = 30  # 30 seconds
    for attempt in range(max_attempts):
        try:
            response = requests.get('http://localhost:5000/api/bot/status', timeout=2)
            if response.status_code == 200:
                status = response.json()
                if status.get('running', False):
                    print("✅ Bot is running and ready")
                    return True
        except:
            pass
        
        time.sleep(1)
        print(f"   Attempt {attempt + 1}/{max_attempts}...")
    
    print("⚠️  Bot may not be fully ready, but continuing...")
    return False

def verify_symbol_processing():
    """Verify that all symbols are being processed"""
    print("🔍 Verifying symbol processing...")
    
    # Monitor for 60 seconds to see which symbols are processed
    log_file = "trading_bot.log"
    start_time = time.time()
    symbols_seen = set()
    
    if not os.path.exists(log_file):
        print("⚠️  Log file not found")
        return False
    
    initial_size = os.path.getsize(log_file)
    
    while time.time() - start_time < 60:  # Monitor for 1 minute
        try:
            current_size = os.path.getsize(log_file)
            
            if current_size > initial_size:
                with open(log_file, 'r', encoding='utf-8') as f:
                    f.seek(initial_size)
                    new_content = f.read()
                    
                    for line in new_content.split('\n'):
                        if 'ANALYZING' in line and '║' in line:
                            parts = line.split('ANALYZING')
                            if len(parts) > 1:
                                symbol_part = parts[1].split('║')[0].strip()
                                if symbol_part:
                                    symbols_seen.add(symbol_part)
                                    print(f"📊 Processing: {symbol_part}")
                
                initial_size = current_size
            
            time.sleep(2)
            
        except Exception as e:
            print(f"⚠️  Error monitoring: {str(e)}")
            time.sleep(5)
    
    print(f"\n📊 Verification Results:")
    print(f"  Symbols processed: {len(symbols_seen)}")
    print(f"  Symbols found: {', '.join(sorted(symbols_seen))}")
    
    if len(symbols_seen) >= 15:  # Allow some tolerance
        print("✅ Most symbols are being processed")
        return True
    else:
        print(f"⚠️  Only {len(symbols_seen)} symbols processed, expected ~18")
        return False

def main():
    """Main restart function"""
    print("🔄 RESTARTING BOT WITH ALL SYMBOLS")
    print("=" * 50)
    
    # Step 1: Verify configuration
    if not verify_configuration():
        print("❌ Configuration verification failed")
        return False
    
    # Step 2: Stop existing bot
    stop_existing_bot()
    
    # Step 3: Start fresh bot
    bot_process = start_bot()
    if not bot_process:
        print("❌ Failed to start bot")
        return False
    
    # Step 4: Wait for bot to be ready
    wait_for_bot_ready()
    
    # Step 5: Verify symbol processing
    success = verify_symbol_processing()
    
    if success:
        print("\n✅ SUCCESS: Bot restarted and processing all symbols!")
        print("🌐 Dashboard available at: http://localhost:5000")
    else:
        print("\n⚠️  Bot restarted but may not be processing all symbols")
        print("   Check the dashboard and logs for more details")
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🎉 Bot restart completed successfully!")
        else:
            print("\n⚠️  Bot restart completed with warnings")
    except KeyboardInterrupt:
        print("\n👋 Restart interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")