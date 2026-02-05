"""
Check if bot is running and when it was started
"""
import psutil
import datetime
import json

print("="*80)
print("BOT STATUS CHECK")
print("="*80)

# Check for running bot processes
print("\n1. Checking for running bot processes...")
bot_processes = []
for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
    try:
        cmdline = proc.info['cmdline']
        if cmdline and any('run_bot.py' in str(cmd) or 'mt5_trading_bot.py' in str(cmd) for cmd in cmdline):
            bot_processes.append(proc)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

if bot_processes:
    print(f"   ⚠️  Found {len(bot_processes)} bot process(es) RUNNING:")
    for proc in bot_processes:
        start_time = datetime.datetime.fromtimestamp(proc.info['create_time'])
        now = datetime.datetime.now()
        running_time = now - start_time
        print(f"\n   PID {proc.pid}:")
        print(f"   Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Running for: {running_time}")
        print(f"   Command: {' '.join(proc.info['cmdline'])}")
    
    print("\n   ⚠️  THE BOT IS STILL RUNNING OLD CODE!")
    print("   You MUST stop it and restart for the fix to work.")
else:
    print("   ✅ No bot processes running")
    print("   Ready to start with new code")

# Check config
print("\n2. Checking config file...")
with open('bot_config.json', 'r') as f:
    config = json.load(f)
    use_macd = config.get('use_macd')
    last_updated = config.get('last_updated', 'unknown')
    print(f"   use_macd: {use_macd}")
    print(f"   Last updated: {last_updated}")

# Check code file modification time
print("\n3. Checking when code was last modified...")
import os
mod_time = os.path.getmtime('src/mt5_trading_bot.py')
mod_datetime = datetime.datetime.fromtimestamp(mod_time)
print(f"   src/mt5_trading_bot.py modified: {mod_datetime.strftime('%Y-%m-%d %H:%M:%S')}")

if bot_processes:
    for proc in bot_processes:
        start_time = datetime.datetime.fromtimestamp(proc.info['create_time'])
        if start_time < mod_datetime:
            print(f"\n   ⚠️  Bot started BEFORE code was modified!")
            print(f"   Bot started:  {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Code modified: {mod_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Bot is running OLD code - RESTART REQUIRED!")
        else:
            print(f"\n   ✅ Bot started AFTER code was modified")
            print(f"   Bot should have new code")

print("\n" + "="*80)
print("RECOMMENDATION")
print("="*80)

if bot_processes:
    print("\n⚠️  BOT IS RUNNING - RESTART REQUIRED")
    print("\nTo restart:")
    print("1. Press Ctrl+C in the bot terminal")
    print("2. Run: EMERGENCY_RESTART_BOT.bat")
    print("\nOR just run: EMERGENCY_RESTART_BOT.bat (it will stop the bot for you)")
else:
    print("\n✅ BOT IS NOT RUNNING")
    print("\nTo start with new code:")
    print("Run: python run_bot.py")

print("="*80)
