"""
Force Restart Dashboard to Load Updated Code

This script helps restart the dashboard completely to ensure
the updated analysis_bars code is loaded.
"""

import subprocess
import sys
import time
import psutil
import os

def find_dashboard_process():
    """Find running dashboard process"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and any('web_dashboard.py' in str(arg) for arg in cmdline):
                return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None

def main():
    print("=" * 80)
    print("FORCE RESTART DASHBOARD")
    print("=" * 80)
    print()
    
    # Check if dashboard is running
    proc = find_dashboard_process()
    
    if proc:
        print(f"✅ Found dashboard process (PID: {proc.pid})")
        print(f"   Command: {' '.join(proc.cmdline())}")
        print()
        
        # Ask user to confirm
        response = input("Do you want to stop this process? (y/n): ")
        if response.lower() != 'y':
            print("Cancelled.")
            return
        
        print()
        print("Stopping dashboard process...")
        try:
            proc.terminate()
            proc.wait(timeout=10)
            print("✅ Dashboard stopped successfully")
        except psutil.TimeoutExpired:
            print("⚠️  Process didn't stop gracefully, forcing...")
            proc.kill()
            print("✅ Dashboard force-stopped")
        except Exception as e:
            print(f"❌ Error stopping process: {e}")
            return
        
        print()
        time.sleep(2)
    else:
        print("ℹ️  No dashboard process found running")
        print()
    
    # Start dashboard
    print("=" * 80)
    print("STARTING DASHBOARD")
    print("=" * 80)
    print()
    print("Starting dashboard with updated code...")
    print()
    
    try:
        # Start dashboard in a new process
        if sys.platform == 'win32':
            # Windows - start in new window
            subprocess.Popen(
                ['python', 'web_dashboard.py'],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            # Linux/Mac
            subprocess.Popen(['python', 'web_dashboard.py'])
        
        print("✅ Dashboard started successfully!")
        print()
        print("=" * 80)
        print("NEXT STEPS")
        print("=" * 80)
        print()
        print("1. Wait 5 seconds for dashboard to initialize")
        print("2. Open browser: http://localhost:5000")
        print("3. Click 'Start Bot'")
        print("4. Check logs - you should now see:")
        print()
        print("   📈 Fetching historical data for XAUUSD (Timeframe: M30)...")
        print("      Requesting 100 bars for analysis")
        print("   ✅ Retrieved 100 bars of data (requested: 100)")
        print()
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        print()
        print("MANUAL START:")
        print("  python web_dashboard.py")
        print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
