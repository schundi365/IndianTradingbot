"""
Simple MT5 Connection Test
Tests basic MT5 connection and provides troubleshooting steps
"""

import MetaTrader5 as mt5
import sys


def test_mt5():
    print("=" * 60)
    print("MT5 SIMPLE CONNECTION TEST")
    print("=" * 60)
    print()
    
    # Test 1: Check if MT5 package is installed
    print("Test 1: Checking MT5 package...")
    try:
        print(f"✅ MetaTrader5 package version: {mt5.__version__}")
    except:
        print("✅ MetaTrader5 package installed")
    print()
    
    # Test 2: Try to initialize MT5
    print("Test 2: Initializing MT5...")
    
    # Try default initialization
    if mt5.initialize():
        print("✅ MT5 initialized successfully!")
        
        # Get terminal info
        terminal_info = mt5.terminal_info()
        if terminal_info:
            print(f"   Terminal: {terminal_info.name}")
            print(f"   Company: {terminal_info.company}")
            print(f"   Path: {terminal_info.path}")
            print(f"   Connected: {terminal_info.connected}")
        
        # Get account info
        account_info = mt5.account_info()
        if account_info:
            print()
            print("✅ Account connected!")
            print(f"   Login: {account_info.login}")
            print(f"   Server: {account_info.server}")
            print(f"   Balance: {account_info.balance} {account_info.currency}")
            print(f"   Leverage: 1:{account_info.leverage}")
            print()
            print("🎉 SUCCESS! MT5 is ready to use!")
        else:
            print()
            print("⚠️  MT5 initialized but no account logged in")
            print()
            print("SOLUTION:")
            print("1. Open MetaTrader 5")
            print("2. Go to File → Login to Trade Account")
            print("3. Enter your account credentials")
            print("4. Make sure you see your account balance")
            print("5. Run this test again")
        
        mt5.shutdown()
        return account_info is not None
        
    else:
        error = mt5.last_error()
        print(f"❌ MT5 initialization failed")
        print(f"   Error code: {error[0]}")
        print(f"   Error message: {error[1]}")
        print()
        
        # Provide specific solutions based on error
        if error[0] == -6:
            print("PROBLEM: Authorization failed")
            print()
            print("SOLUTIONS:")
            print("1. Make sure MetaTrader 5 is RUNNING")
            print("2. Open MT5 and LOGIN to your account:")
            print("   - File → Login to Trade Account")
            print("   - Enter your login, password, and server")
            print("   - Click 'Login'")
            print("3. Verify you see your account balance in MT5")
            print("4. Run this test again")
            print()
            print("DEMO ACCOUNT:")
            print("If you don't have an account:")
            print("1. In MT5: File → Open an Account")
            print("2. Choose a broker (e.g., MetaQuotes-Demo)")
            print("3. Select 'Open a demo account'")
            print("4. Fill in the form and submit")
            print("5. You'll receive demo account credentials")
            
        elif error[0] == -2:
            print("PROBLEM: MT5 terminal not found")
            print()
            print("SOLUTIONS:")
            print("1. Install MetaTrader 5 from:")
            print("   https://www.metatrader5.com/en/download")
            print("2. Make sure MT5 is running")
            print("3. Run this test again")
            
        else:
            print("SOLUTIONS:")
            print("1. Make sure MetaTrader 5 is installed")
            print("2. Make sure MT5 is running")
            print("3. Try restarting MT5")
            print("4. Run this test again")
        
        return False
    
    print("=" * 60)


if __name__ == "__main__":
    try:
        success = test_mt5()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        print("\nMake sure:")
        print("1. MetaTrader 5 is installed")
        print("2. MT5 is running")
        print("3. You have Python package 'MetaTrader5' installed")
        sys.exit(1)
