"""
ML Features Installation Script
Automates installation and setup of ML components
"""

import subprocess
import sys
import os


def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(text)
    print("="*60 + "\n")


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"⏳ {description}...")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✅ {description} - SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(f"Error: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible"""
    print_header("CHECKING PYTHON VERSION")
    
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher required")
        return False
    
    print("✅ Python version compatible")
    return True


def install_dependencies():
    """Install ML dependencies"""
    print_header("INSTALLING ML DEPENDENCIES")
    
    packages = [
        ("xgboost", "XGBoost (ML model)"),
        ("scikit-learn", "scikit-learn (ML utilities)"),
        ("textblob", "TextBlob (sentiment analysis)"),
        ("scipy", "SciPy (pattern recognition)"),
        ("numpy", "NumPy (numerical computing)"),
        ("pandas", "Pandas (data handling)")
    ]
    
    success_count = 0
    
    for package, description in packages:
        if run_command(f"pip install {package}", f"Installing {description}"):
            success_count += 1
    
    print(f"\n✅ Installed {success_count}/{len(packages)} packages")
    return success_count == len(packages)


def download_textblob_corpora():
    """Download TextBlob language corpora"""
    print_header("DOWNLOADING TEXTBLOB CORPORA")
    
    return run_command(
        "python -m textblob.download_corpora",
        "Downloading NLP data"
    )


def create_models_directory():
    """Create directory for ML models"""
    print_header("CREATING MODELS DIRECTORY")
    
    try:
        os.makedirs("models", exist_ok=True)
        print("✅ Models directory created")
        return True
    except Exception as e:
        print(f"❌ Failed to create models directory: {e}")
        return False


def test_installation():
    """Test if ML features work"""
    print_header("TESTING ML FEATURES")
    
    tests = []
    
    # Test XGBoost
    print("Testing XGBoost...")
    try:
        import xgboost
        print(f"✅ XGBoost {xgboost.__version__} imported successfully")
        tests.append(True)
    except ImportError as e:
        print(f"❌ XGBoost import failed: {e}")
        tests.append(False)
    
    # Test scikit-learn
    print("\nTesting scikit-learn...")
    try:
        import sklearn
        print(f"✅ scikit-learn {sklearn.__version__} imported successfully")
        tests.append(True)
    except ImportError as e:
        print(f"❌ scikit-learn import failed: {e}")
        tests.append(False)
    
    # Test TextBlob
    print("\nTesting TextBlob...")
    try:
        from textblob import TextBlob
        test_text = TextBlob("This is a test")
        sentiment = test_text.sentiment
        print(f"✅ TextBlob working (polarity: {sentiment.polarity:.2f})")
        tests.append(True)
    except Exception as e:
        print(f"❌ TextBlob test failed: {e}")
        tests.append(False)
    
    # Test SciPy
    print("\nTesting SciPy...")
    try:
        from scipy.signal import find_peaks
        import numpy as np
        peaks, _ = find_peaks(np.array([1, 2, 1, 2, 1]))
        print(f"✅ SciPy working (found {len(peaks)} peaks)")
        tests.append(True)
    except Exception as e:
        print(f"❌ SciPy test failed: {e}")
        tests.append(False)
    
    # Test ML modules
    print("\nTesting ML modules...")
    try:
        from src.ml_signal_generator import MLSignalGenerator
        from src.sentiment_analyzer import SentimentAnalyzer
        from src.pattern_recognition import PatternRecognition
        from src.ml_integration import MLIntegration
        
        print("✅ All ML modules imported successfully")
        tests.append(True)
    except Exception as e:
        print(f"❌ ML module import failed: {e}")
        tests.append(False)
    
    success_rate = sum(tests) / len(tests) * 100
    print(f"\n✅ Test success rate: {success_rate:.0f}%")
    
    return all(tests)


def run_demo():
    """Run ML features demo"""
    print_header("RUNNING ML FEATURES DEMO")
    
    print("Running test_ml_features.py...")
    print("(This may take a minute...)\n")
    
    return run_command(
        "python test_ml_features.py",
        "ML features demo"
    )


def print_next_steps():
    """Print next steps for user"""
    print_header("INSTALLATION COMPLETE!")
    
    print("✅ ML features are ready to use!\n")
    
    print("📋 NEXT STEPS:\n")
    
    print("1. Enable Pattern Recognition (safest start):")
    print("   Edit bot_config.json:")
    print('   "pattern_enabled": true\n')
    
    print("2. Run the bot:")
    print("   python run_bot.py\n")
    
    print("3. Monitor performance for 1 week\n")
    
    print("4. Optional: Enable sentiment analysis")
    print('   "sentiment_enabled": true\n')
    
    print("5. Optional: Train ML model (after 100+ trades)")
    print("   See docs/ML_FEATURES_GUIDE.md for training\n")
    
    print("📚 DOCUMENTATION:\n")
    print("   - Quick Start: ML_QUICK_START.md")
    print("   - Full Guide: docs/ML_FEATURES_GUIDE.md")
    print("   - Test Demo: python test_ml_features.py\n")
    
    print("🎯 RECOMMENDED CONFIGURATION:\n")
    print("   Start conservative:")
    print("   {")
    print('     "pattern_enabled": true,')
    print('     "sentiment_enabled": false,')
    print('     "ml_enabled": false,')
    print('     "technical_weight": 0.7,')
    print('     "pattern_weight": 0.3')
    print("   }\n")
    
    print("Happy trading with ML! 🤖📈")


def main():
    """Main installation process"""
    print_header("ML FEATURES INSTALLATION")
    print("This script will install and configure ML features for GEM Trading Bot")
    
    # Check Python version
    if not check_python_version():
        print("\n❌ Installation aborted - Python version incompatible")
        return False
    
    # Install dependencies
    if not install_dependencies():
        print("\n⚠️ Some packages failed to install")
        print("Try manually: pip install -r requirements_ml.txt")
    
    # Download TextBlob corpora
    download_textblob_corpora()
    
    # Create models directory
    create_models_directory()
    
    # Test installation
    if not test_installation():
        print("\n⚠️ Some tests failed")
        print("ML features may not work correctly")
        print("Check error messages above")
    
    # Run demo (optional)
    print("\n" + "="*60)
    response = input("Run ML features demo? (y/n): ").lower()
    if response == 'y':
        run_demo()
    
    # Print next steps
    print_next_steps()
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Installation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Installation failed: {e}")
        sys.exit(1)
