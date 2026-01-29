"""
Show recent bot activity summary
"""
import re
from datetime import datetime
from collections import defaultdict

def parse_logs():
    """Parse recent log activity"""
    try:
        with open('trading_bot.log', 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except:
        print("Could not read log file")
        return
    
    # Get last 500 lines
    recent_lines = lines[-500:]
    
    # Track events
    symbols_analyzed = set()
    crossovers_detected = []
    signals_confirmed = []
    signals_rejected = []
    trades_opened = []
    
    current_symbol = None
    current_time = None
    
    for line in recent_lines:
        # Extract timestamp
        match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
        if match:
            current_time = match.group(1)
        
        # Track symbol being analyzed
        if "ANALYZING" in line and "╔" in line:
            match = re.search(r'ANALYZING\s+(\w+)', line)
            if match:
                current_symbol = match.group(1)
                symbols_analyzed.add(current_symbol)
        
        # Track crossovers
        if "crossover detected" in line.lower() and current_symbol:
            signal_type = "BUY" if "bullish" in line.lower() else "SELL"
            crossovers_detected.append({
                'time': current_time,
                'symbol': current_symbol,
                'type': signal_type
            })
        
        # Track confirmed signals
        if "SIGNAL CONFIRMED" in line and current_symbol:
            signal_type = "BUY" if "BUY" in line else "SELL"
            signals_confirmed.append({
                'time': current_time,
                'symbol': current_symbol,
                'type': signal_type
            })
        
        # Track rejected signals
        if "REJECTED" in line or "rejected" in line:
            if "RSI" in line:
                reason = "RSI"
            elif "MACD" in line:
                reason = "MACD"
            elif "Volume" in line:
                reason = "Volume"
            else:
                reason = "Other"
            
            if current_symbol:
                signals_rejected.append({
                    'time': current_time,
                    'symbol': current_symbol,
                    'reason': reason
                })
        
        # Track trades opened
        if "Successfully opened" in line and "split positions" in line:
            match = re.search(r'(\d+) split positions', line)
            if match and current_symbol:
                trades_opened.append({
                    'time': current_time,
                    'symbol': current_symbol,
                    'positions': int(match.group(1))
                })
    
    # Display summary
    print("="*80)
    print("RECENT BOT ACTIVITY SUMMARY")
    print("="*80)
    print()
    
    print(f"📊 Symbols Analyzed: {len(symbols_analyzed)}")
    if symbols_analyzed:
        print(f"   {', '.join(sorted(symbols_analyzed))}")
    print()
    
    print(f"🎯 Crossovers Detected: {len(crossovers_detected)}")
    if crossovers_detected:
        for event in crossovers_detected[-10:]:  # Last 10
            print(f"   {event['time']} - {event['symbol']} {event['type']}")
    print()
    
    print(f"✅ Signals Confirmed: {len(signals_confirmed)}")
    if signals_confirmed:
        for event in signals_confirmed[-10:]:
            print(f"   {event['time']} - {event['symbol']} {event['type']}")
    print()
    
    print(f"❌ Signals Rejected: {len(signals_rejected)}")
    if signals_rejected:
        # Group by reason
        by_reason = defaultdict(int)
        for event in signals_rejected:
            by_reason[event['reason']] += 1
        
        for reason, count in by_reason.items():
            print(f"   {reason}: {count}")
        
        print()
        print("   Recent rejections:")
        for event in signals_rejected[-5:]:
            print(f"   {event['time']} - {event['symbol']} ({event['reason']})")
    print()
    
    print(f"💰 Trades Opened: {len(trades_opened)}")
    if trades_opened:
        for event in trades_opened[-10:]:
            print(f"   {event['time']} - {event['symbol']} ({event['positions']} positions)")
    print()
    
    print("="*80)
    print("CURRENT STATUS")
    print("="*80)
    
    # Show last few log lines
    print()
    print("Last activity:")
    for line in recent_lines[-10:]:
        if any(keyword in line for keyword in ['ANALYZING', 'crossover', 'SIGNAL', 'Completed', 'Starting']):
            if "127.0.0.1" not in line and "GET /api/" not in line:
                print(f"  {line.strip()}")
    
    print()
    print("="*80)

if __name__ == "__main__":
    parse_logs()
