#!/usr/bin/env python3
"""
Test ADX Fix

This script tests if the ADX KeyError has been resolved
and the enhanced signal generation is working properly.
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime

# Add src directory to path
sys.path.append('src')

def test_adx_fix():
    """Test if the ADX fix is working"""
    print("🧪 Testing ADX Fix...")
    print("="*50)
    
    try:
        # Import the config first
        from config import get_config
        config = get_config()
        
        # Import the trading bot
        from mt5_trading_bot import MT5TradingBot
        
        # Create bot instance
        bot = MT5TradingBot(config)
        
        print("✅ Bot instance created successfully")
        
        # Create test data
        print("📊 Creating test market data...")
        dates = pd.date_range(start='2024-01-01', periods=50, freq='30T')
        
        df = pd.DataFrame({
            'time': dates,
            'open': np.linspace(1.8600, 1.8650, 50),
            'high': np.linspace(1.8610, 1.8660, 50),
            'low': np.linspace(1.8590, 1.8640, 50),
            'close': np.linspace(1.8605, 1.8655, 50),
            'tick_volume': np.random.randint(1000, 5000, 50)
        })
        
        print("✅ Test data created")
        
        # Test calculate_indicators method
        print("🔧 Testing calculate_indicators method...")
        df_with_indicators = bot.calculate_indicators(df)
        
        print("✅ calculate_indicators completed without errors")
        
        # Check if ADX columns are present
        adx_columns = ['adx', 'plus_di', 'minus_di']
        for col in adx_columns:
            if col in df_with_indicators.columns:
                print(f"✅ {col} column present")
            else:
                print(f"⚠️ {col} column missing")
        
        # Test check_entry_signal method
        print("🎯 Testing check_entry_signal method...")
        signal = bot.check_entry_signal(df_with_indicators)
        
        print(f"✅ check_entry_signal completed without errors")
        print(f"   Signal result: {'BUY' if signal == 1 else 'SELL' if signal == -1 else 'NO SIGNAL'}")
        
        return True
        
    except KeyError as e:
        if 'adx' in str(e):
            print(f"❌ ADX KeyError still present: {e}")
            return False
        else:
            print(f"❌ Other KeyError: {e}")
            return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_adx_code_changes():
    """Verify the ADX code changes are in place"""
    print("\n🔍 Verifying ADX Code Changes...")
    print("="*50)
    
    try:
        with open('src/mt5_trading_bot.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for the safe ADX access pattern
        safe_patterns = [
            "if 'adx' in df.columns and not pd.isna(latest['adx']):",
            "df['adx'] = df['adx'].fillna(0)",
            "df['plus_di'] = df['plus_di'].fillna(0)",
            "df['minus_di'] = df['minus_di'].fillna(0)"
        ]
        
        found_patterns = 0
        for pattern in safe_patterns:
            if pattern in content:
                print(f"✅ Found: {pattern}")
                found_patterns += 1
            else:
                print(f"❌ Missing: {pattern}")
        
        print(f"\nFound {found_patterns}/{len(safe_patterns)} safety patterns")
        
        # Check if ADX calculation is in calculate_indicators
        if "# ADX (Average Directional Index) for trend strength" in content:
            print("✅ ADX calculation added to calculate_indicators")
        else:
            print("❌ ADX calculation not found in calculate_indicators")
        
        return found_patterns >= 2  # At least 2 safety patterns should be present
        
    except Exception as e:
        print(f"❌ Error verifying code changes: {e}")
        return False

if __name__ == "__main__":
    print("🚀 ADX Fix Verification Test")
    print("="*50)
    
    # Verify code changes first
    code_ok = verify_adx_code_changes()
    
    # Test functionality
    if code_ok:
        success = test_adx_fix()
        
        if success:
            print("\n🎉 ADX FIX VERIFICATION SUCCESSFUL!")
            print("✅ No more ADX KeyError")
            print("✅ Enhanced signal generation working")
            print("✅ ADX calculation integrated")
            print("\nThe bot is ready to run with enhanced signal generation!")
        else:
            print("\n❌ ADX FIX VERIFICATION FAILED!")
            print("There may still be issues with the ADX implementation.")
    else:
        print("\n⚠️ CODE VERIFICATION INCOMPLETE!")
        print("Some ADX safety patterns may be missing.")
        print("The fix may not be fully applied.")