#!/usr/bin/env python3
"""
Monitor the live bot to see which symbols are being processed
"""

import time
import os
import requests
import json

def check_bot_status():
    """Check the current bot status via API"""
    try:
        response = requests.get('http://localhost:5000/api/bot/status', timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        print(f"❌ Error checking bot status: {str(e)}")
        return None

def check_bot_config():
    """Check the current bot configuration via API"""
    try:
        response = requests.get('http://localhost:5000/api/config', timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        print(f"❌ Error checking bot config: {str(e)}")
        return None

def monitor_log_file(duration=120):
    """Monitor the log file for symbol processing"""
    log_file = "trading_bot.log"
    
    if not os.path.exists(log_file):
        print(f"❌ Log file not found: {log_file}")
        return
    
    print(f"👀 Monitoring {log_file} for {duration} seconds...")
    print("=" * 60)
    
    # Get initial file size
    initial_size = os.path.getsize(log_file)
    start_time = time.time()
    symbols_seen = set()
    analysis_count = 0
    
    while time.time() - start_time < duration:
        try:
            current_size = os.path.getsize(log_file)
            
            if current_size > initial_size:
                # Read new content
                with open(log_file, 'r', encoding='utf-8') as f:
                    f.seek(initial_size)
                    new_content = f.read()
                    
                    if new_content.strip():
                        lines = new_content.strip().split('\n')
                        for line in lines:
                            # Look for ANALYZING lines
                            if 'ANALYZING' in line and '║' in line:
                                # Extract symbol
                                parts = line.split('ANALYZING')
                                if len(parts) > 1:
                                    symbol_part = parts[1].split('║')[0].strip()
                                    if symbol_part:
                                        symbols_seen.add(symbol_part)
                                        analysis_count += 1
                                        timestamp = line.split(' - ')[0] if ' - ' in line else 'Unknown'
                                        print(f"📊 {timestamp}: Analyzing {symbol_part} (#{analysis_count})")
                
                initial_size = current_size
            
            time.sleep(2)  # Check every 2 seconds
            
        except Exception as e:
            print(f"⚠️  Error monitoring: {str(e)}")
            time.sleep(5)
    
    print("\n" + "=" * 60)
    print("📊 MONITORING SUMMARY:")
    print(f"  Duration: {duration} seconds")
    print(f"  Total analyses: {analysis_count}")
    print(f"  Unique symbols: {len(symbols_seen)}")
    
    if symbols_seen:
        print(f"\n📋 SYMBOLS PROCESSED:")
        for i, symbol in enumerate(sorted(symbols_seen), 1):
            print(f"  {i:2d}. {symbol}")
    
    return symbols_seen

def main():
    """Main monitoring function"""
    print("🔍 LIVE SYMBOL PROCESSING MONITOR")
    print("=" * 50)
    
    # Check bot status
    print("1. Checking bot status...")
    status = check_bot_status()
    if status:
        print(f"   ✅ Bot status: {status.get('status', 'unknown')}")
        print(f"   📊 Running: {status.get('running', False)}")
    else:
        print("   ⚠️  Could not get bot status")
    
    # Check bot configuration
    print("\n2. Checking bot configuration...")
    config = check_bot_config()
    if config:
        symbols = config.get('symbols', [])
        print(f"   ✅ Config loaded: {len(symbols)} symbols")
        print(f"   📋 Symbols: {', '.join(symbols[:5])}{'...' if len(symbols) > 5 else ''}")
    else:
        print("   ⚠️  Could not get bot configuration")
    
    # Monitor live processing
    print("\n3. Monitoring live symbol processing...")
    symbols_processed = monitor_log_file(120)  # Monitor for 2 minutes
    
    # Compare results
    if config and symbols_processed:
        config_symbols = set(config.get('symbols', []))
        missing_symbols = config_symbols - symbols_processed
        
        print(f"\n🎯 COMPARISON:")
        print(f"  Config symbols:     {len(config_symbols)}")
        print(f"  Processed symbols:  {len(symbols_processed)}")
        print(f"  Missing symbols:    {len(missing_symbols)}")
        
        if missing_symbols:
            print(f"\n❌ SYMBOLS NOT PROCESSED:")
            for symbol in sorted(missing_symbols):
                print(f"  - {symbol}")
        else:
            print(f"\n✅ All configured symbols are being processed!")

if __name__ == "__main__":
    main()