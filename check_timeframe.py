"""Quick script to check current timeframe setting"""
import sys
sys.path.insert(0, 'src')
from config import get_config
import MetaTrader5 as mt5

config = get_config()
timeframe = config['timeframe']

# Map timeframe codes to names
timeframe_map = {
    1: 'M1 (1 minute)',
    5: 'M5 (5 minutes)',
    15: 'M15 (15 minutes)',
    30: 'M30 (30 minutes)',
    16385: 'H1 (1 hour)',
    16388: 'H4 (4 hours)',
    16408: 'D1 (1 day)',
    32769: 'W1 (1 week)'
}

print("=" * 50)
print("CURRENT TIMEFRAME SETTING")
print("=" * 50)
print()
print(f"Timeframe: {timeframe_map.get(timeframe, f'Unknown ({timeframe})')}")
print(f"Code: {timeframe}")
print()
print("Other settings:")
print(f"  Fast MA: {config['fast_ma_period']} periods")
print(f"  Slow MA: {config['slow_ma_period']} periods")
print(f"  ATR Period: {config['atr_period']} periods")
print()
print("=" * 50)
