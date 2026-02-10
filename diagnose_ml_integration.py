"""
Diagnose ML Integration Status
Checks if ML features are being used by the bot
"""

import json
import sys

def diagnose_ml_integration():
    """Diagnose ML integration status"""
    
    print("=" * 70)
    print("ML INTEGRATION DIAGNOSTIC")
    print("=" * 70)
    
    issues = []
    recommendations = []
    
    # 1. Check bot_config.json
    print("\n1. Checking bot_config.json...")
    try:
        with open('bot_config.json', 'r') as f:
            config = json.load(f)
        
        ml_enabled = config.get('ml_enabled', False)
        pattern_enabled = config.get('pattern_enabled', False)
        sentiment_enabled = config.get('sentiment_enabled', False)
        
        print(f"   ml_enabled: {ml_enabled}")
        print(f"   pattern_enabled: {pattern_enabled}")
        print(f"   sentiment_enabled: {sentiment_enabled}")
        
        if ml_enabled:
            print("   ✅ ML is ENABLED in config")
        else:
            print("   ⚠️  ML is DISABLED in config")
            recommendations.append("Enable ML in dashboard: Configuration → ML Features → Enable ML")
        
        # Check ML model path
        ml_model_path = config.get('ml_model_path', '')
        if ml_model_path:
            print(f"   ML Model Path: {ml_model_path}")
        else:
            print("   ⚠️  ML Model Path not configured")
            recommendations.append("Set ML model path in config")
    
    except Exception as e:
        print(f"   ❌ Error reading config: {e}")
        issues.append(f"Cannot read bot_config.json: {e}")
    
    # 2. Check if ML modules exist
    print("\n2. Checking ML modules...")
    ml_files = [
        'src/ml_integration.py',
        'src/ml_signal_generator.py',
        'src/sentiment_analyzer.py',
        'src/pattern_recognition.py'
    ]
    
    missing_files = []
    for file in ml_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"   ✅ {file} exists ({len(content)} bytes)")
        except FileNotFoundError:
            print(f"   ❌ {file} NOT FOUND")
            missing_files.append(file)
    
    if missing_files:
        issues.append(f"Missing ML files: {missing_files}")
    
    # 3. Check if bot imports ML modules
    print("\n3. Checking bot integration...")
    bot_files = [
        'src/mt5_trading_bot.py',
        'src/mt5_trading_bot_SIGNAL_FIX.py'
    ]
    
    for bot_file in bot_files:
        try:
            with open(bot_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"\n   {bot_file}:")
            
            # Check for ML imports
            if 'from ml_integration import MLIntegration' in content or 'import ml_integration' in content:
                print("     ✅ ML integration imported")
            else:
                print("     ❌ ML integration NOT imported")
                issues.append(f"{bot_file} does not import ML integration")
            
            # Check for ML usage
            if 'MLIntegration' in content:
                print("     ✅ MLIntegration class used")
            else:
                print("     ❌ MLIntegration class NOT used")
                issues.append(f"{bot_file} does not use MLIntegration")
            
            # Check for get_enhanced_signal
            if 'get_enhanced_signal' in content:
                print("     ✅ get_enhanced_signal() called")
            else:
                print("     ❌ get_enhanced_signal() NOT called")
                issues.append(f"{bot_file} does not call get_enhanced_signal()")
        
        except Exception as e:
            print(f"     ⚠️  Error reading {bot_file}: {e}")
    
    # 4. Check if ML model exists
    print("\n4. Checking ML model...")
    try:
        import os
        model_path = config.get('ml_model_path', 'models/ml_signal_model.pkl')
        
        if os.path.exists(model_path):
            print(f"   ✅ ML model found: {model_path}")
        else:
            print(f"   ⚠️  ML model NOT found: {model_path}")
            recommendations.append("Train ML model using: python train_ml_model.py")
    except Exception as e:
        print(f"   ⚠️  Error checking model: {e}")
    
    # Summary
    print("\n" + "=" * 70)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 70)
    
    if not issues:
        print("\n✅ ML Integration Status: CONFIGURED")
        print("\nHowever, ML features are NOT being used by the bot!")
        print("\n🔧 MAIN ISSUE:")
        print("   The bot code does not call ML integration functions.")
        print("   ML modules exist but are not integrated into trading logic.")
    else:
        print(f"\n❌ FOUND {len(issues)} ISSUE(S):")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
    
    if recommendations:
        print(f"\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
    
    print("\n" + "=" * 70)
    print("HOW TO FIX")
    print("=" * 70)
    print("\nThe ML features need to be integrated into the bot's trading logic.")
    print("\nRequired changes:")
    print("  1. Import MLIntegration in bot file")
    print("  2. Initialize MLIntegration in __init__()")
    print("  3. Call get_enhanced_signal() before placing trades")
    print("  4. Use enhanced signals for trading decisions")
    print("  5. Train ML model with historical data")
    print("\nWould you like me to integrate ML into the bot? (Y/N)")
    
    return len(issues) == 0

if __name__ == "__main__":
    success = diagnose_ml_integration()
    sys.exit(0 if success else 1)
