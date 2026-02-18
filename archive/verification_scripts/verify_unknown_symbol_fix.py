"""
Verification script for the "unknown" symbol fix in trend detection
"""

import re

def verify_fix():
    """Verify that the unknown symbol issue has been fixed"""
    
    print("=" * 80)
    print("VERIFYING 'UNKNOWN' SYMBOL FIX")
    print("=" * 80)
    
    issues_found = []
    fixes_verified = []
    
    # Check 1: Verify get_trend_signals has symbol parameter
    print("\n1. Checking get_trend_signals method...")
    with open('src/trend_detection_engine.py', 'r', encoding='utf-8') as f:
        content = f.read()
        
        # Find the method signature
        pattern = r'def get_trend_signals\(self, df: pd\.DataFrame, signal_type: str(, symbol: str = "unknown")?\)'
        match = re.search(pattern, content)
        
        if match and match.group(1):
            print("   ✅ get_trend_signals has symbol parameter with default value")
            fixes_verified.append("get_trend_signals signature updated")
        else:
            print("   ❌ get_trend_signals missing symbol parameter")
            issues_found.append("get_trend_signals signature not updated")
        
        # Check if it passes symbol to analyze_trend_change
        if 'def get_trend_signals' in content:
            method_start = content.find('def get_trend_signals')
            method_end = content.find('\n    def ', method_start + 1)
            method_content = content[method_start:method_end]
            
            if 'analyze_trend_change(df, symbol)' in method_content:
                print("   ✅ get_trend_signals passes symbol to analyze_trend_change")
                fixes_verified.append("get_trend_signals passes symbol correctly")
            elif 'analyze_trend_change(df, "unknown")' in method_content:
                print("   ❌ get_trend_signals still uses hardcoded 'unknown'")
                issues_found.append("get_trend_signals still hardcoded")
    
    # Check 2: Verify should_trade_trend has symbol parameter
    print("\n2. Checking should_trade_trend method...")
    with open('src/trend_detection_engine.py', 'r', encoding='utf-8') as f:
        content = f.read()
        
        # Find the method signature
        pattern = r'def should_trade_trend\(self, df: pd\.DataFrame, signal_type: str(, symbol: str = "unknown")?\)'
        match = re.search(pattern, content)
        
        if match and match.group(1):
            print("   ✅ should_trade_trend has symbol parameter with default value")
            fixes_verified.append("should_trade_trend signature updated")
        else:
            print("   ❌ should_trade_trend missing symbol parameter")
            issues_found.append("should_trade_trend signature not updated")
        
        # Check if it passes symbol to analyze_trend_change and get_trend_signals
        if 'def should_trade_trend' in content:
            method_start = content.find('def should_trade_trend')
            method_end = content.find('\n    def ', method_start + 1)
            method_content = content[method_start:method_end]
            
            if 'analyze_trend_change(df, symbol)' in method_content:
                print("   ✅ should_trade_trend passes symbol to analyze_trend_change")
                fixes_verified.append("should_trade_trend passes symbol to analyze_trend_change")
            elif 'analyze_trend_change(df, "unknown")' in method_content:
                print("   ❌ should_trade_trend still uses hardcoded 'unknown' for analyze_trend_change")
                issues_found.append("should_trade_trend analyze_trend_change still hardcoded")
            
            if 'get_trend_signals(df, signal_type, symbol)' in method_content:
                print("   ✅ should_trade_trend passes symbol to get_trend_signals")
                fixes_verified.append("should_trade_trend passes symbol to get_trend_signals")
            elif 'get_trend_signals(df, signal_type)' in method_content and 'get_trend_signals(df, signal_type, symbol)' not in method_content:
                print("   ❌ should_trade_trend doesn't pass symbol to get_trend_signals")
                issues_found.append("should_trade_trend get_trend_signals call not updated")
    
    # Check 3: Verify mt5_trading_bot.py passes symbol
    print("\n3. Checking mt5_trading_bot.py...")
    with open('src/mt5_trading_bot.py', 'r', encoding='utf-8') as f:
        content = f.read()
        
        # Find the should_trade_trend call
        if 'should_trade_trend(df, signal_type_str, symbol)' in content:
            print("   ✅ mt5_trading_bot.py passes symbol to should_trade_trend")
            fixes_verified.append("mt5_trading_bot.py updated")
        elif 'should_trade_trend(df, signal_type_str)' in content:
            print("   ❌ mt5_trading_bot.py doesn't pass symbol to should_trade_trend")
            issues_found.append("mt5_trading_bot.py not updated")
    
    # Summary
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    
    if not issues_found:
        print("\n✅ ALL CHECKS PASSED!")
        print(f"\nFixes verified ({len(fixes_verified)}):")
        for fix in fixes_verified:
            print(f"  ✅ {fix}")
        
        print("\n" + "=" * 80)
        print("EXPECTED BEHAVIOR AFTER FIX:")
        print("=" * 80)
        print("""
Before fix - logs showed:
  🔍 Starting trend analysis for XPDUSD (15)
  🔍 Starting trend analysis for unknown (15)  ← Wrong!
  🔍 Starting trend analysis for unknown (15)  ← Wrong!

After fix - logs should show:
  🔍 Starting trend analysis for XPDUSD (15)
  🔍 Starting trend analysis for XPDUSD (15)  ← Correct!
  🔍 Starting trend analysis for XPDUSD (15)  ← Correct!

The three calls are:
1. analyze_trend_change(df, symbol) - direct call from bot
2. should_trade_trend(df, signal_type, symbol) → analyze_trend_change(df, symbol)
3. should_trade_trend → get_trend_signals(df, signal_type, symbol) → analyze_trend_change(df, symbol)
""")
        
        print("\n" + "=" * 80)
        print("NEXT STEPS:")
        print("=" * 80)
        print("""
1. Restart the bot to apply the fix
2. Monitor the logs for "Starting trend analysis" messages
3. Verify all three calls now show the correct symbol name (e.g., XPDUSD)
4. Confirm no more "unknown" symbols appear in trend detection logs
""")
        
        return True
    else:
        print("\n❌ ISSUES FOUND!")
        print(f"\nIssues ({len(issues_found)}):")
        for issue in issues_found:
            print(f"  ❌ {issue}")
        
        if fixes_verified:
            print(f"\nPartial fixes verified ({len(fixes_verified)}):")
            for fix in fixes_verified:
                print(f"  ✅ {fix}")
        
        return False

if __name__ == "__main__":
    success = verify_fix()
    exit(0 if success else 1)
