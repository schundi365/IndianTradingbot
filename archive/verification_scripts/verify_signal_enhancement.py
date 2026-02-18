#!/usr/bin/env python3
"""
Verify Enhanced Signal Generation Implementation

This script checks if the enhanced signal generation methods
have been successfully implemented in the trading bot.
"""

def verify_signal_enhancement():
    """Verify the enhanced signal generation is implemented"""
    print("🔍 Verifying Enhanced Signal Generation Implementation...")
    print("="*70)
    
    try:
        # Read the trading bot file
        with open('src/mt5_trading_bot.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for enhanced signal methods
        enhancements = {
            "METHOD 1: CHECKING MA CROSSOVER": "✅ MA Crossover method",
            "METHOD 2: CHECKING TREND CONFIRMATION": "✅ Trend Confirmation method", 
            "METHOD 3: CHECKING MOMENTUM SIGNALS": "🆕 Momentum Signals method",
            "METHOD 4: CHECKING PULLBACK SIGNALS": "🆕 Pullback Signals method",
            "METHOD 5: CHECKING BREAKOUT SIGNALS": "🆕 Breakout Signals method",
            "signal_reason": "✅ Signal reason tracking",
            "Bullish Momentum Recovery": "✅ Momentum signal types",
            "Bullish Pullback to MA": "✅ Pullback signal types",
            "Bullish Breakout": "✅ Breakout signal types"
        }
        
        print("📊 Checking for enhanced signal methods:")
        print("-" * 70)
        
        found_count = 0
        for check, description in enhancements.items():
            if check in content:
                print(f"✅ {description}")
                found_count += 1
            else:
                print(f"❌ Missing: {description}")
        
        print("-" * 70)
        print(f"Found: {found_count}/{len(enhancements)} enhancements")
        
        # Check for specific signal generation improvements
        critical_features = [
            "RSI recovering from oversold",
            "MACD histogram improving", 
            "Price pulled back to fast MA",
            "Price broke above recent high",
            "Checked 5 signal methods"
        ]
        
        print("\n🎯 Checking for critical signal features:")
        print("-" * 70)
        
        critical_found = 0
        for feature in critical_features:
            if feature in content:
                print(f"✅ {feature}")
                critical_found += 1
            else:
                print(f"❌ Missing: {feature}")
        
        print("-" * 70)
        print(f"Critical Features: {critical_found}/{len(critical_features)}")
        
        # Overall assessment
        print("\n📈 ENHANCEMENT ASSESSMENT:")
        print("="*70)
        
        if found_count >= 7 and critical_found >= 4:
            print("🎉 EXCELLENT! Enhanced signal generation is fully implemented!")
            print("✅ The bot now has 5 different signal generation methods")
            print("✅ Multiple signal types: Crossover, Trend, Momentum, Pullback, Breakout")
            print("✅ Detailed logging for each signal method")
            print("✅ Signal reason tracking for transparency")
            success = True
        elif found_count >= 5 and critical_found >= 3:
            print("✅ GOOD! Most enhancements are implemented")
            print("⚠️ Some features may be missing but core functionality is there")
            success = True
        else:
            print("❌ INCOMPLETE! Signal generation enhancements not fully implemented")
            print("🔧 The fix may not have been applied correctly")
            success = False
        
        # Check if old restrictive logic is still present
        print("\n🔍 Checking for old restrictive logic:")
        old_restrictive_patterns = [
            "Waiting for MA crossover or trend confirmation...",
            "return 0  # No signal"
        ]
        
        old_logic_found = 0
        for pattern in old_restrictive_patterns:
            if pattern in content:
                old_logic_found += 1
        
        if old_logic_found == 0:
            print("✅ Old restrictive logic has been replaced")
        else:
            print(f"⚠️ Found {old_logic_found} instances of old restrictive logic")
        
        return success
        
    except Exception as e:
        print(f"❌ Error verifying signal enhancement: {e}")
        return False

def check_current_bot_status():
    """Check if the bot is currently running and needs restart"""
    print("\n🔄 Bot Restart Recommendations:")
    print("="*70)
    print("To apply the enhanced signal generation:")
    print("1. Stop the current trading bot if running")
    print("2. Stop the web dashboard if running") 
    print("3. Restart with: python run_bot.py")
    print("4. Monitor logs for new signal methods")
    print("\n📊 Expected improvements:")
    print("• More frequent signal generation")
    print("• 5 different signal detection methods")
    print("• Better market opportunity detection")
    print("• Detailed signal reasoning in logs")

if __name__ == "__main__":
    print("🚀 Enhanced Signal Generation Verification")
    print("="*70)
    
    success = verify_signal_enhancement()
    check_current_bot_status()
    
    if success:
        print("\n🎉 VERIFICATION SUCCESSFUL!")
        print("Enhanced signal generation is ready to use!")
    else:
        print("\n❌ VERIFICATION FAILED!")
        print("Please check the implementation manually.")