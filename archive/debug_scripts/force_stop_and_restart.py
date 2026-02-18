"""
Force stop any running bot processes and prepare for clean restart
"""
import psutil
import sys
import time

print("="*80)
print("FORCE STOP BOT PROCESSES")
print("="*80)

# Find all Python processes running run_bot.py or mt5_trading_bot.py
bot_processes = []
for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        cmdline = proc.info['cmdline']
        if cmdline and any('run_bot.py' in str(cmd) or 'mt5_trading_bot.py' in str(cmd) for cmd in cmdline):
            bot_processes.append(proc)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

if bot_processes:
    print(f"\n⚠️  Found {len(bot_processes)} bot process(es) running:")
    for proc in bot_processes:
        print(f"   PID {proc.pid}: {' '.join(proc.info['cmdline'])}")
    
    print("\n🛑 Terminating processes...")
    for proc in bot_processes:
        try:
            proc.terminate()
            print(f"   Terminated PID {proc.pid}")
        except Exception as e:
            print(f"   Error terminating PID {proc.pid}: {e}")
    
    # Wait for processes to terminate
    print("\n⏳ Waiting for processes to stop...")
    time.sleep(3)
    
    # Force kill if still running
    for proc in bot_processes:
        try:
            if proc.is_running():
                proc.kill()
                print(f"   Force killed PID {proc.pid}")
        except:
            pass
    
    print("\n✅ All bot processes stopped")
else:
    print("\n✅ No bot processes found running")

print("\n" + "="*80)
print("NEXT STEPS:")
print("="*80)
print("1. Run: python clear_all_cache.py")
print("2. Wait 5 seconds")
print("3. Run: python run_bot.py")
print("="*80)
