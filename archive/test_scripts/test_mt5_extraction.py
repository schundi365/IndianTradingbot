"""
Test MT5 Data Extraction
Diagnose issues with MT5 historical data extraction
"""

import MetaTrader5 as mt5
import pandas as pd
import sys

print("=" * 80)
print("MT5 DATA EXTRACTION DIAGNOSTIC")
print("=" * 80)
print()

# Test 1: MT5 Import
print("Test 1: MT5 Import")
try:
    print(f"  ✅ MT5 version: {mt5.__version__}")
except Exception as e:
    print(f"  ❌ Error: {e}")
    sys.exit(1)

# Test 2: MT5 Initialize
print("\nTest 2: MT5 Initialize")
if not mt5.initialize():
    error = mt5.last_error()
    print(f"  ❌ Failed to initialize MT5")
    print(f"     Error code: {error}")
    print()
    print("Troubleshooting:")
    print("  1. Make sure MT5 is running")
    print("  2. Login to your MT5 account")
    print("  3. Check MT5 is not busy")
    sys.exit(1)
else:
    print("  ✅ MT5 initialized successfully")

# Test 3: Account Info
print("\nTest 3: Account Info")
account_info = mt5.account_info()
if account_info is None:
    print("  ❌ Could not get account info")
else:
    print(f"  ✅ Account: {account_info.login}")
    print(f"     Server: {account_info.server}")
    print(f"     Balance: {account_info.balance}")

# Test 4: Symbol Check
print("\nTest 4: Symbol Availability")
test_symbols = ['XAUUSD', 'EURUSD', 'GBPUSD', 'USDJPY']
available_symbols = []

for symbol in test_symbols:
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(f"  ❌ {symbol}: Not available")
    else:
        print(f"  ✅ {symbol}: Available")
        available_symbols.append(symbol)

if len(available_symbols) == 0:
    print("\n❌ No symbols available!")
    print("   Add symbols to Market Watch in MT5")
    mt5.shutdown()
    sys.exit(1)

# Test 5: Data Fetch
print("\nTest 5: Historical Data Fetch")
test_symbol = available_symbols[0]
print(f"  Testing with {test_symbol}...")

rates = mt5.copy_rates_from_pos(test_symbol, mt5.TIMEFRAME_M30, 0, 100)

if rates is None:
    error = mt5.last_error()
    print(f"  ❌ Failed to fetch data")
    print(f"     Error: {error}")
    mt5.shutdown()
    sys.exit(1)
else:
    print(f"  ✅ Fetched {len(rates)} bars")
    print(f"     Timeframe: M30")
    print(f"     Columns: {rates.dtype.names}")

# Test 6: DataFrame Conversion
print("\nTest 6: DataFrame Conversion")
try:
    df = pd.DataFrame(rates)
    print(f"  ✅ Converted to DataFrame")
    print(f"     Shape: {df.shape}")
    print(f"     Columns: {list(df.columns)}")
except Exception as e:
    print(f"  ❌ Error: {e}")
    mt5.shutdown()
    sys.exit(1)

# Test 7: Indicator Calculation
print("\nTest 7: Indicator Calculation")
try:
    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    print(f"  ✅ RSI calculated")
    print(f"     Latest RSI: {df['rsi'].iloc[-1]:.2f}")
    
    # MACD
    exp1 = df['close'].ewm(span=12).mean()
    exp2 = df['close'].ewm(span=26).mean()
    df['macd'] = exp1 - exp2
    df['macd_signal'] = df['macd'].ewm(span=9).mean()
    
    print(f"  ✅ MACD calculated")
    print(f"     Latest MACD: {df['macd'].iloc[-1]:.6f}")
    
except Exception as e:
    print(f"  ❌ Error: {e}")
    import traceback
    traceback.print_exc()
    mt5.shutdown()
    sys.exit(1)

# Cleanup
mt5.shutdown()

print("\n" + "=" * 80)
print("ALL TESTS PASSED ✅")
print("=" * 80)
print()
print("MT5 data extraction should work!")
print("Try running: python ml_training/0_extract_from_mt5.py")
print()
