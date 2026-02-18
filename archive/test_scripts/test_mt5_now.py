"""Quick MT5 connection test"""
import MetaTrader5 as mt5
import sys

print("="*80)
print("MT5 CONNECTION TEST")
print("="*80)

print("\n1. Testing MT5 initialization...")
if mt5.initialize():
    print("   ✓ MT5 initialized successfully")
    
    print("\n2. Getting terminal info...")
    terminal = mt5.terminal_info()
    if terminal:
        print(f"   ✓ Build: {terminal.build}")
        print(f"   ✓ Company: {terminal.company}")
        print(f"   ✓ Connected: {terminal.connected}")
    
    print("\n3. Getting account info...")
    account = mt5.account_info()
    if account:
        print(f"   ✓ Login: {account.login}")
        print(f"   ✓ Server: {account.server}")
        print(f"   ✓ Balance: {account.balance}")
        print(f"   ✓ Equity: {account.equity}")
    else:
        print("   ✗ No account info - NOT LOGGED IN!")
        mt5.shutdown()
        sys.exit(1)
    
    print("\n4. Testing data fetch (XAUUSD)...")
    rates = mt5.copy_rates_from_pos("XAUUSD", mt5.TIMEFRAME_M1, 0, 10)
    if rates is not None and len(rates) > 0:
        print(f"   ✓ Got {len(rates)} bars")
        print(f"   ✓ Latest close: {rates[-1]['close']}")
    else:
        print(f"   ✗ Failed to get data: {mt5.last_error()}")
    
    mt5.shutdown()
    print("\n" + "="*80)
    print("✓ MT5 CONNECTION TEST PASSED")
    print("="*80)
    print("\nMT5 is working correctly. The bot should be able to connect.")
    print("If bot still fails, there's a code issue in web_dashboard.py")
    
else:
    error = mt5.last_error()
    print(f"   ✗ MT5 initialization failed!")
    print(f"   Error: {error}")
    print("\n" + "="*80)
    print("✗ MT5 CONNECTION TEST FAILED")
    print("="*80)
    print("\nPossible causes:")
    print("1. MT5 terminal is not running")
    print("2. MT5 is not logged in")
    print("3. MT5 is in safe mode or restricted")
    print("\nSolution:")
    print("1. Open MetaTrader 5")
    print("2. Login to your account")
    print("3. Wait for connection (green indicator)")
    print("4. Run this test again")
    sys.exit(1)
