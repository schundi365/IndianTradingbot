#!/usr/bin/env python3
"""
Restart bot and monitor for errors after applying fixes
"""

import os
import sys
import time
import subprocess
import threading
from datetime import datetime

def clear_log_file():
    """Clear the existing log file to start fresh"""
    log_file = "trading_bot.log"
    try:
        if os.path.exists(log_file):
            with open(log_file, 'w') as f:
                f.write("")
            print(f"✅ Cleared log file: {log_file}")
        else:
            print(f"ℹ️  Log file doesn't exist yet: {log_file}")
    except Exception as e:
        print(f"⚠️  Could not clear log file: {str(e)}")

def stop_existing_processes():
    """Stop any existing bot processes"""
    try:
        # Kill any existing Python processes running the bot
        if os.name == 'nt':  # Windows
            subprocess.run(['taskkill', '/f', '/im', 'python.exe'], 
                         capture_output=True, text=True)
        else:  # Unix-like
            subprocess.run(['pkill', '-f', 'web_dashboard.py'], 
                         capture_output=True, text=True)
        
        print("🛑 Stopped existing bot processes")
        time.sleep(2)  # Give processes time to stop
        
    except Exception as e:
        print(f"⚠️  Could not stop existing processes: {str(e)}")

def start_bot():
    """Start the bot in background"""
    try:
        print("🚀 Starting bot...")
        
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

def monitor_logs(duration=300):  # Monitor for 5 minutes
    """Monitor the log file for errors"""
    log_file = "trading_bot.log"
    start_time = time.time()
    last_size = 0
    error_count = 0
    adx_errors = 0
    logger_errors = 0
    
    print(f"👀 Monitoring logs for {duration} seconds...")
    print("=" * 60)
    
    while time.time() - start_time < duration:
        try:
            if os.path.exists(log_file):
                current_size = os.path.getsize(log_file)
                
                if current_size > last_size:
                    # New content added
                    with open(log_file, 'r', encoding='utf-8') as f:
                        f.seek(last_size)
                        new_content = f.read()
                        
                        if new_content.strip():
                            lines = new_content.strip().split('\n')
                            for line in lines:
                                # Check for specific error patterns
                                if 'ERROR' in line:
                                    error_count += 1
                                    print(f"🔴 ERROR: {line}")
                                    
                                    if "'adx'" in line.lower():
                                        adx_errors += 1
                                    elif 'name \'logger\' is not defined' in line:
                                        logger_errors += 1
                                
                                elif 'INFO' in line and any(keyword in line for keyword in ['ANALYZING', 'SIGNAL', 'ADX', 'MACD']):
                                    print(f"ℹ️  {line}")
                    
                    last_size = current_size
            
            time.sleep(2)  # Check every 2 seconds
            
        except Exception as e:
            print(f"⚠️  Error monitoring logs: {str(e)}")
            time.sleep(5)
    
    print("\n" + "=" * 60)
    print("📊 MONITORING SUMMARY:")
    print(f"  - Total errors: {error_count}")
    print(f"  - ADX KeyErrors: {adx_errors}")
    print(f"  - Logger NameErrors: {logger_errors}")
    
    if error_count == 0:
        print("  ✅ NO ERRORS DETECTED!")
    elif adx_errors == 0 and logger_errors == 0:
        print("  ✅ NO ADX OR LOGGER ERRORS!")
    else:
        print("  ❌ ERRORS STILL PRESENT")
    
    return error_count, adx_errors, logger_errors

def main():
    """Main execution function"""
    print("🔄 RESTARTING BOT WITH FIXES")
    print("=" * 40)
    
    # Step 1: Clear log file
    clear_log_file()
    
    # Step 2: Stop existing processes
    stop_existing_processes()
    
    # Step 3: Start bot
    bot_process = start_bot()
    
    if not bot_process:
        print("❌ Failed to start bot!")
        return False
    
    # Step 4: Wait a moment for bot to initialize
    print("⏳ Waiting for bot to initialize...")
    time.sleep(10)
    
    # Step 5: Monitor logs
    try:
        error_count, adx_errors, logger_errors = monitor_logs(300)  # 5 minutes
        
        print("\n🎯 FINAL RESULTS:")
        if error_count == 0:
            print("  ✅ SUCCESS: No errors detected!")
            print("  🎉 All ADX and logger issues have been resolved!")
        elif adx_errors == 0 and logger_errors == 0:
            print("  ✅ SUCCESS: No ADX or logger errors!")
            print("  ℹ️  Other errors may be unrelated to our fixes")
        else:
            print("  ❌ PARTIAL SUCCESS: Some issues remain")
            print(f"     ADX errors: {adx_errors}")
            print(f"     Logger errors: {logger_errors}")
        
        return error_count == 0 or (adx_errors == 0 and logger_errors == 0)
        
    except KeyboardInterrupt:
        print("\n⏹️  Monitoring stopped by user")
        return True
    
    finally:
        # Keep bot running
        print("\n🔄 Bot continues running in background")
        print("   Use Ctrl+C to stop monitoring")
        print("   Check dashboard at http://localhost:5000")

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ BOT RESTART AND MONITORING COMPLETED SUCCESSFULLY!")
        else:
            print("\n⚠️  BOT RESTARTED BUT SOME ISSUES MAY REMAIN")
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")