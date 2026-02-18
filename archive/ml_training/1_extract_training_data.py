"""
Extract Training Data from Bot Logs
Parses trading_bot.log to create ML training dataset
"""

import re
import csv
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_training_data(log_file='trading_bot.log', output_file='data/training_data.csv'):
    """
    Extract training data from bot logs
    
    Args:
        log_file: Path to trading bot log file
        output_file: Path to output CSV file
    """
    logger.info(f"Extracting training data from {log_file}")
    
    # Create data directory if it doesn't exist
    output_path = Path(output_file)
    output_path.parent.mkdir(exist_ok=True)
    
    # Read log file
    log_path = Path(log_file)
    if not log_path.exists():
        logger.error(f"Log file not found: {log_file}")
        return False
    
    # Parse log entries
    trades = []
    current_trade = {}
    
    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            # Look for trade signals with indicators
            if 'SIGNAL:' in line or 'Trade signal' in line:
                # Extract timestamp
                timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                if timestamp_match:
                    current_trade['timestamp'] = timestamp_match.group(1)
                
                # Extract symbol
                symbol_match = re.search(r'(XAUUSD|XAGUSD|EURUSD|GBPUSD|USDJPY|AUDUSD|USDCAD|NZDUSD|EURJPY|GBPJPY)', line)
                if symbol_match:
                    current_trade['symbol'] = symbol_match.group(1)
                
                # Extract signal type
                if 'BUY' in line:
                    current_trade['signal'] = 'BUY'
                elif 'SELL' in line:
                    current_trade['signal'] = 'SELL'
            
            # Extract indicator values
            if 'RSI:' in line or 'rsi=' in line.lower():
                rsi_match = re.search(r'RSI[:\s=]+(\d+\.?\d*)', line, re.IGNORECASE)
                if rsi_match:
                    current_trade['rsi'] = float(rsi_match.group(1))
            
            if 'MACD' in line:
                macd_match = re.search(r'MACD[:\s=]+(-?\d+\.?\d*)', line, re.IGNORECASE)
                if macd_match:
                    current_trade['macd'] = float(macd_match.group(1))
                
                signal_match = re.search(r'Signal[:\s=]+(-?\d+\.?\d*)', line, re.IGNORECASE)
                if signal_match:
                    current_trade['macd_signal'] = float(signal_match.group(1))
            
            if 'ADX' in line:
                adx_match = re.search(r'ADX[:\s=]+(\d+\.?\d*)', line, re.IGNORECASE)
                if adx_match:
                    current_trade['adx'] = float(adx_match.group(1))
            
            if 'ATR' in line:
                atr_match = re.search(r'ATR[:\s=]+(\d+\.?\d*)', line, re.IGNORECASE)
                if atr_match:
                    current_trade['atr'] = float(atr_match.group(1))
            
            if 'EMA' in line or 'ema_fast' in line.lower():
                ema_fast_match = re.search(r'EMA[_\s]?Fast[:\s=]+(\d+\.?\d*)', line, re.IGNORECASE)
                if ema_fast_match:
                    current_trade['ema_fast'] = float(ema_fast_match.group(1))
                
                ema_slow_match = re.search(r'EMA[_\s]?Slow[:\s=]+(\d+\.?\d*)', line, re.IGNORECASE)
                if ema_slow_match:
                    current_trade['ema_slow'] = float(ema_slow_match.group(1))
            
            if 'Volume' in line and 'volume=' in line.lower():
                volume_match = re.search(r'volume[:\s=]+(\d+)', line, re.IGNORECASE)
                if volume_match:
                    current_trade['volume'] = int(volume_match.group(1))
            
            if 'Price' in line or 'close=' in line.lower():
                price_match = re.search(r'(?:Price|close)[:\s=]+(\d+\.?\d*)', line, re.IGNORECASE)
                if price_match:
                    current_trade['close'] = float(price_match.group(1))
            
            # Extract trade outcome
            if 'Profit:' in line or 'profit=' in line.lower():
                profit_match = re.search(r'(?:Profit|profit)[:\s=]+(-?\d+\.?\d*)', line, re.IGNORECASE)
                if profit_match:
                    profit = float(profit_match.group(1))
                    current_trade['profitable'] = 1 if profit > 0 else 0
                    
                    # If we have enough data, save the trade
                    if len(current_trade) >= 5:  # Minimum fields
                        trades.append(current_trade.copy())
                    
                    current_trade = {}  # Reset for next trade
    
    logger.info(f"Extracted {len(trades)} trades from logs")
    
    if len(trades) == 0:
        logger.warning("No trades found in logs. Make sure bot has been running and making trades.")
        return False
    
    # Write to CSV
    fieldnames = ['timestamp', 'symbol', 'close', 'rsi', 'macd', 'macd_signal', 'adx', 'atr', 
                  'ema_fast', 'ema_slow', 'volume', 'profitable']
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        
        for trade in trades:
            # Fill in missing fields with defaults
            for field in fieldnames:
                if field not in trade:
                    if field == 'profitable':
                        trade[field] = 0
                    elif field in ['timestamp', 'symbol']:
                        trade[field] = ''
                    else:
                        trade[field] = 0.0
            
            writer.writerow(trade)
    
    logger.info(f"Training data saved to {output_file}")
    logger.info(f"Total samples: {len(trades)}")
    
    # Show statistics
    profitable_count = sum(1 for t in trades if t.get('profitable', 0) == 1)
    logger.info(f"Profitable trades: {profitable_count} ({profitable_count/len(trades)*100:.1f}%)")
    logger.info(f"Losing trades: {len(trades) - profitable_count} ({(len(trades)-profitable_count)/len(trades)*100:.1f}%)")
    
    return True


if __name__ == '__main__':
    print("=" * 80)
    print("EXTRACT TRAINING DATA FROM LOGS")
    print("=" * 80)
    print()
    
    success = extract_training_data()
    
    if success:
        print()
        print("✅ Training data extracted successfully!")
        print()
        print("Next steps:")
        print("1. Review data/training_data.csv")
        print("2. Open dashboard → ML Features")
        print("3. Click 'Train ML Model'")
        print()
    else:
        print()
        print("❌ Failed to extract training data")
        print()
        print("Troubleshooting:")
        print("1. Make sure trading_bot.log exists")
        print("2. Ensure bot has been running and making trades")
        print("3. Check log file contains trade information")
        print()
