"""
Live Log Monitor
Shows important bot events in real-time with color coding
"""
import time
import os
from datetime import datetime

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_last_n_lines(filename, n=50):
    """Get last N lines from file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            return lines[-n:] if len(lines) > n else lines
    except Exception as e:
        return [f"Error reading log: {str(e)}"]

def format_log_line(line):
    """Format log line with highlights"""
    line = line.strip()
    
    # Highlight important events
    if "ANALYZING" in line and "╔" in line:
        return f"\n{'='*80}\n{line}"
    elif "crossover detected" in line.lower():
        return f"🎯 {line}"
    elif "SIGNAL CONFIRMED" in line:
        return f"✅ {line}"
    elif "REJECTED" in line or "rejected" in line:
        return f"❌ {line}"
    elif "RSI FILTER" in line:
        return f"📊 {line}"
    elif "MACD FILTER" in line:
        return f"📈 {line}"
    elif "Opening split positions" in line:
        return f"💰 {line}"
    elif "Position" in line and "Ticket:" in line:
        return f"  ✓ {line}"
    elif "Successfully opened" in line:
        return f"🎉 {line}"
    elif "ERROR" in line or "Error" in line:
        return f"⚠️  {line}"
    elif "WARNING" in line and "IPC" not in line:
        return f"⚠️  {line}"
    elif "Starting analysis cycle" in line:
        return f"\n{'─'*80}\n⏰ {line}"
    elif "Completed analysis" in line:
        return f"✓ {line}"
    else:
        return f"   {line}"

def monitor_logs():
    """Monitor logs in real-time"""
    print("="*80)
    print("LIVE LOG MONITOR - Trading Bot")
    print("="*80)
    print("Monitoring: trading_bot.log")
    print("Press Ctrl+C to stop")
    print("="*80)
    print()
    
    last_size = 0
    last_lines = []
    
    try:
        while True:
            # Check if file size changed
            try:
                current_size = os.path.getsize('trading_bot.log')
            except:
                print("Waiting for log file...")
                time.sleep(2)
                continue
            
            if current_size != last_size:
                # File changed, read new lines
                lines = get_last_n_lines('trading_bot.log', 100)
                
                # Find new lines
                if last_lines:
                    # Get only new lines
                    new_lines = []
                    found_last = False
                    for line in reversed(lines):
                        if not found_last:
                            if line == last_lines[-1]:
                                found_last = True
                            else:
                                new_lines.insert(0, line)
                    
                    # Display new lines
                    for line in new_lines:
                        if line.strip():
                            # Filter out noise
                            if "GET /api/" in line or "127.0.0.1" in line:
                                continue
                            if "No trades found for performance" in line:
                                continue
                            if "IPC connection error" in line:
                                continue
                            if "MT5 reconnected" in line:
                                continue
                            
                            print(format_log_line(line))
                else:
                    # First run, show last 20 lines
                    print("📜 Recent activity:")
                    print("-"*80)
                    for line in lines[-20:]:
                        if line.strip():
                            if "GET /api/" in line or "127.0.0.1" in line:
                                continue
                            print(format_log_line(line))
                
                last_lines = lines
                last_size = current_size
            
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n\n" + "="*80)
        print("Log monitoring stopped")
        print("="*80)

if __name__ == "__main__":
    monitor_logs()
