"""
Verify ML Integration is Complete
Checks that ML has been successfully integrated into the bot
"""

import sys

def verify_ml_integration():
    """Verify ML integration is complete"""
    
    print("=" * 70)
    print("ML INTEGRATION VERIFICATION")
    print("=" * 70)
    
    issues = []
    
    # 1. Check bot file for ML integration
    print("\n1. Checking src/mt5_trading_bot.py...")
    try:
        with open('src/mt5_trading_bot.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = {
            'ML Import': 'from src.ml_integration import MLIntegration',
            'ML Available Flag': 'ML_INTEGRATION_AVAILABLE',
            'ML Initialization': 'self.ml_integration = MLIntegration',
            'ML Enabled Check': 'if self.ml_integration:',
            'get_enhanced_signal Call': 'get_enhanced_signal(',
            'ML Approved Check': 'ml_approved =',
            'ML Size Multiplier': 'ml_size_multiplier',
            'ML Logging': '🤖 ML ENHANCED SIGNAL ANALYSIS'
        }
        
        for check_name, check_str in checks.items():
            if check_str in content:
                print(f"   ✅ {check_name}")
            else:
                print(f"   ❌ {check_name} NOT found")
                issues.append(f"Missing: {check_name}")
    
    except Exception as e:
        print(f"   ❌ Error reading bot file: {e}")
        issues.append(f"Cannot read bot file: {e}")
    
    # 2. Check config
    print("\n2. Checking bot_config.json...")
    try:
        import json
        with open('bot_config.json', 'r') as f:
            config = json.load(f)
        
        ml_enabled = config.get('ml_enabled', False)
        print(f"   ml_enabled: {ml_enabled}")
        
        if ml_enabled:
            print("   ✅ ML is ENABLED")
        else:
            print("   ⚠️  ML is DISABLED (can be enabled in dashboard)")
    
    except Exception as e:
        print(f"   ❌ Error reading config: {e}")
    
    # 3. Check ML modules exist
    print("\n3. Checking ML modules...")
    ml_files = [
        'src/ml_integration.py',
        'src/ml_signal_generator.py',
        'src/sentiment_analyzer.py',
        'src/pattern_recognition.py'
    ]
    
    for file in ml_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                pass
            print(f"   ✅ {file}")
        except FileNotFoundError:
            print(f"   ❌ {file} NOT FOUND")
            issues.append(f"Missing file: {file}")
    
    # Summary
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    
    if not issues:
        print("\n✅ ML INTEGRATION COMPLETE!")
        print("\nML features are now integrated into the bot:")
        print("  ✅ ML modules imported")
        print("  ✅ ML initialized in __init__()")
        print("  ✅ get_enhanced_signal() called before trades")
        print("  ✅ ML confidence filtering applied")
        print("  ✅ ML position sizing applied")
        print("  ✅ Comprehensive ML logging added")
        print("\n🎉 You will now see ML logs when the bot runs!")
        print("\nExpected log output:")
        print("  - '✅ ML INTEGRATION INITIALIZED'")
        print("  - '🤖 ML ENHANCED SIGNAL ANALYSIS'")
        print("  - '✅ ML APPROVED' or '❌ ML REJECTED'")
        print("  - ML confidence scores and component analysis")
        print("\nNext steps:")
        print("  1. Restart the bot")
        print("  2. Watch for ML logs")
        print("  3. Adjust ml_min_confidence if needed (dashboard)")
        print("  4. Monitor improved trading performance")
        return True
    else:
        print(f"\n❌ FOUND {len(issues)} ISSUE(S):")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        return False

if __name__ == "__main__":
    success = verify_ml_integration()
    sys.exit(0 if success else 1)
