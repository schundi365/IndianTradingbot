@echo off
REM ================================================================
REM GEM Trading Bot - Windows Standalone Build Script
REM ================================================================

echo.
echo ================================================================
echo GEM TRADING BOT - WINDOWS BUILD
echo ================================================================
echo.
echo This will create a standalone Windows executable (.exe)
echo Users can run it without installing Python or dependencies.
echo.
echo Build time: 5-10 minutes
echo Final size: ~150-200 MB
echo.
pause

REM Check Python version
echo.
echo Checking Python version...
python --version
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Install/upgrade PyInstaller
echo.
echo Step 1: Installing build dependencies...
pip install --upgrade pyinstaller
if errorlevel 1 (
    echo ERROR: Failed to install PyInstaller
    pause
    exit /b 1
)

REM Install web dependencies
echo.
echo Step 2: Installing web dependencies...
pip install -r requirements_web.txt
if errorlevel 1 (
    echo ERROR: Failed to install web dependencies
    pause
    exit /b 1
)

REM Clean previous builds
echo.
echo Step 3: Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist GEM_Trading_Bot.spec del GEM_Trading_Bot.spec

REM Create build directory
if not exist build mkdir build
if not exist dist mkdir dist

REM Build executable
echo.
echo Step 4: Building Windows executable...
echo This may take 5-10 minutes, please wait...
echo.

pyinstaller ^
    --name="GEM_Trading_Bot" ^
    --onefile ^
    --windowed ^
    --icon=NONE ^
    --add-data="templates;templates" ^
    --add-data="src;src" ^
    --add-data="models;models" ^
    --add-data="bot_config.json;." ^
    --hidden-import=MetaTrader5 ^
    --hidden-import=pandas ^
    --hidden-import=numpy ^
    --hidden-import=flask ^
    --hidden-import=werkzeug ^
    --hidden-import=jinja2 ^
    --hidden-import=click ^
    --hidden-import=itsdangerous ^
    --hidden-import=markupsafe ^
    --hidden-import=logging ^
    --hidden-import=threading ^
    --hidden-import=datetime ^
    --hidden-import=pathlib ^
    --hidden-import=json ^
    --hidden-import=pickle ^
    --hidden-import=xgboost ^
    --hidden-import=xgboost.sklearn ^
    --hidden-import=xgboost.core ^
    --hidden-import=sklearn ^
    --hidden-import=sklearn.ensemble ^
    --hidden-import=sklearn.tree ^
    --hidden-import=joblib ^
    --hidden-import=src.mt5_trading_bot ^
    --hidden-import=src.config_manager ^
    --hidden-import=src.adaptive_risk_manager ^
    --hidden-import=src.volume_analyzer ^
    --hidden-import=src.dynamic_sl_manager ^
    --hidden-import=src.dynamic_tp_manager ^
    --hidden-import=src.scalping_manager ^
    --hidden-import=src.split_order_calculator ^
    --hidden-import=src.trailing_strategies ^
    --hidden-import=src.enhanced_indicators ^
    --hidden-import=src.ml_signal_generator ^
    --hidden-import=src.ml_integration ^
    --exclude-module=tensorboard ^
    --exclude-module=tensorflow ^
    --exclude-module=torch ^
    --exclude-module=matplotlib ^
    --exclude-module=scipy ^
    --exclude-module=IPython ^
    --exclude-module=jupyter ^
    --collect-all=flask ^
    --collect-all=werkzeug ^
    --collect-all=jinja2 ^
    --collect-all=xgboost ^
    web_dashboard.py

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    echo Check the error messages above.
    pause
    exit /b 1
)

REM Create distribution package
echo.
echo Step 5: Creating distribution package...

if not exist "dist\GEM_Trading_Bot_Windows" mkdir "dist\GEM_Trading_Bot_Windows"
if not exist "dist\GEM_Trading_Bot_Windows\docs" mkdir "dist\GEM_Trading_Bot_Windows\docs"

REM Copy executable
copy "dist\GEM_Trading_Bot.exe" "dist\GEM_Trading_Bot_Windows\" >nul

REM Copy ML model files if they exist
echo Checking for ML model files...
if exist "models\ml_signal_model.pkl" (
    echo Found ML model file, copying...
    if not exist "dist\GEM_Trading_Bot_Windows\models" mkdir "dist\GEM_Trading_Bot_Windows\models"
    copy "models\ml_signal_model.pkl" "dist\GEM_Trading_Bot_Windows\models\" >nul
    echo ML model included in package
) else (
    echo WARNING: ML model file not found - bot will run without ML features
)

REM Copy bot configuration
if exist "bot_config.json" (
    copy "bot_config.json" "dist\GEM_Trading_Bot_Windows\" >nul
    echo Configuration file included
)

REM Copy essential documentation
copy "USER_GUIDE.md" "dist\GEM_Trading_Bot_Windows\" >nul
copy "QUICK_START.md" "dist\GEM_Trading_Bot_Windows\" >nul
copy "QUICK_REFERENCE_CARD.md" "dist\GEM_Trading_Bot_Windows\" >nul
copy "TROUBLESHOOTING.md" "dist\GEM_Trading_Bot_Windows\" >nul
copy "README.md" "dist\GEM_Trading_Bot_Windows\" >nul
copy "CHANGELOG.md" "dist\GEM_Trading_Bot_Windows\" >nul
copy "WINDOWS_INSTALLATION_GUIDE.md" "dist\GEM_Trading_Bot_Windows\" >nul
copy "FEATURES_GUIDE.md" "dist\GEM_Trading_Bot_Windows\" >nul

REM Copy user guides from docs
copy "docs\INSTALLATION_GUIDE_FOR_USERS.md" "dist\GEM_Trading_Bot_Windows\docs\" >nul
copy "docs\DASHBOARD_CONFIGURATION_GUIDE.md" "dist\GEM_Trading_Bot_Windows\docs\" >nul
copy "docs\PROFITABLE_STRATEGY_GUIDE.md" "dist\GEM_Trading_Bot_Windows\docs\" >nul
copy "docs\WEB_DASHBOARD_GUIDE.md" "dist\GEM_Trading_Bot_Windows\docs\" >nul
copy "docs\CONFIGURATION_QUICK_REFERENCE.md" "dist\GEM_Trading_Bot_Windows\docs\" >nul

REM Copy ML training documentation if it exists
if exist "ml_training\README.md" (
    if not exist "dist\GEM_Trading_Bot_Windows\ml_training" mkdir "dist\GEM_Trading_Bot_Windows\ml_training"
    copy "ml_training\README.md" "dist\GEM_Trading_Bot_Windows\ml_training\" >nul
    copy "ml_training\DATA_EXTRACTION_GUIDE.md" "dist\GEM_Trading_Bot_Windows\ml_training\" >nul 2>nul
    echo ML training documentation included
)

REM Create START_HERE.txt for distribution
echo Creating START_HERE.txt...
(
echo ================================================================================
echo    GEM TRADING BOT - WINDOWS EDITION
echo ================================================================================
echo.
echo Thank you for downloading GEM Trading Bot!
echo.
echo This version includes ML (Machine Learning) signal prediction for enhanced
echo trading decisions. The ML model analyzes patterns and provides additional
echo confirmation for trade signals.
echo.
echo ================================================================================
echo    QUICK START - 3 STEPS
echo ================================================================================
echo.
echo STEP 1: Install MetaTrader 5
echo    - Download MT5 from your broker's website
echo    - Install and login to your account
echo    - Enable Algo Trading: Tools ^> Options ^> Expert Advisors
echo    - Check "Allow algorithmic trading"
echo    - Keep MT5 running!
echo.
echo STEP 2: Run the Bot
echo    - Double-click: GEM_Trading_Bot.exe
echo    - Wait 30 seconds for dashboard to open
echo    - Browser opens automatically to http://localhost:5000
echo.
echo STEP 3: Configure and Start
echo    - Click "Configuration" tab
echo    - Select symbols (XAUUSD, GBPUSD recommended^)
echo    - Choose timeframe (M5 recommended^)
echo    - Enable "Auto" for all settings
echo    - Click "Save Configuration"
echo    - Click "Start Bot"
echo    - Monitor your trades!
echo.
echo ================================================================================
echo    SYSTEM REQUIREMENTS
echo ================================================================================
echo.
echo    - Windows 10 or 11 (64-bit^)
echo    - MetaTrader 5 installed
echo    - 4GB RAM minimum
echo    - Internet connection
echo    - 500MB free disk space
echo.
echo ================================================================================
echo    DOCUMENTATION
echo ================================================================================
echo.
echo    README.md - Project overview
echo    USER_GUIDE.md - Complete user manual (READ THIS FIRST!^)
echo    QUICK_START.md - 5-minute getting started
echo    TROUBLESHOOTING.md - Common issues and solutions
echo    CHANGELOG.md - Version history
echo.
echo    docs\ folder:
echo    - INSTALLATION_GUIDE_FOR_USERS.md - Detailed setup
echo    - DASHBOARD_CONFIGURATION_GUIDE.md - All settings explained
echo    - PROFITABLE_STRATEGY_GUIDE.md - Trading strategy details
echo    - WEB_DASHBOARD_GUIDE.md - Dashboard features
echo    - CONFIGURATION_QUICK_REFERENCE.md - Quick settings guide
echo.
echo    ml_training\ folder (if included):
echo    - README.md - ML model training guide
echo    - DATA_EXTRACTION_GUIDE.md - How to extract training data
echo.
echo ================================================================================
echo    ML FEATURES
echo ================================================================================
echo.
echo    This bot includes Machine Learning capabilities:
echo    - ML model analyzes 8 technical features
echo    - Provides BUY/SELL/NEUTRAL predictions
echo    - Confidence-based signal filtering
echo    - Works alongside technical analysis
echo    - Can be enabled/disabled in dashboard
echo.
echo    ML Settings in Dashboard:
echo    - Enable ML: Turn ML predictions on/off
echo    - ML Confidence: Minimum confidence threshold (60%% recommended^)
echo    - Require Agreement: How many signals must agree
echo.
echo ================================================================================
echo    IMPORTANT NOTES
echo ================================================================================
echo.
echo    WARNING: Trading involves risk. Use at your own risk.
echo.
echo    - Test on DEMO account first (at least 1 week^)
echo    - Start with low risk (0.3%% per trade^)
echo    - Monitor regularly
echo    - Keep MT5 running while bot is active
echo    - Read USER_GUIDE.md before trading
echo.
echo ================================================================================
echo    TROUBLESHOOTING
echo ================================================================================
echo.
echo    Dashboard won't open?
echo    - Wait 30 seconds on first run
echo    - Try manually: http://localhost:5000
echo    - Check Windows Firewall (allow access^)
echo.
echo    Bot won't start?
echo    - Make sure MT5 is running
echo    - Verify MT5 is logged in
echo    - Check algo trading is enabled
echo.
echo    No trades executing?
echo    - Lower confidence level to 40%%
echo    - Check symbols are selected
echo    - Verify account has sufficient balance
echo.
echo    For more help, see TROUBLESHOOTING.md
echo.
echo ================================================================================
echo    SUPPORT
echo ================================================================================
echo.
echo    - Read USER_GUIDE.md for detailed instructions
echo    - Check TROUBLESHOOTING.md for common issues
echo    - Review documentation in docs\ folder
echo.
echo ================================================================================
echo    VERSION INFORMATION
echo ================================================================================
echo.
echo    Version: 2.1.0
echo    Platform: Windows 64-bit
echo    Python: Embedded (no installation needed^)
echo.
echo ================================================================================
echo.
echo Ready to start? Double-click GEM_Trading_Bot.exe!
echo.
echo Happy Trading! 💎🚀
echo.
echo ================================================================================
) > "dist\GEM_Trading_Bot_Windows\START_HERE.txt"

REM Get file size
echo.
echo ================================================================
echo BUILD COMPLETE!
echo ================================================================
echo.
echo Executable: dist\GEM_Trading_Bot.exe
for %%A in ("dist\GEM_Trading_Bot.exe") do echo File Size: %%~zA bytes
echo.
echo Distribution package: dist\GEM_Trading_Bot_Windows\
echo.
echo Package contents:
dir /b "dist\GEM_Trading_Bot_Windows"
echo.
echo ================================================================
echo NEXT STEPS
echo ================================================================
echo.
echo 1. TEST THE EXECUTABLE:
echo    cd dist
echo    GEM_Trading_Bot.exe
echo.
echo 2. VERIFY IT WORKS:
echo    - Opens browser to http://localhost:5000
echo    - Dashboard loads correctly
echo    - Can connect to MT5
echo.
echo 3. CREATE ZIP FOR DISTRIBUTION:
echo    - Right-click dist\GEM_Trading_Bot_Windows
echo    - Send to ^> Compressed (zipped) folder
echo    - Name it: GEM_Trading_Bot_v2.0_Windows.zip
echo.
echo 4. DISTRIBUTE:
echo    - Upload to file sharing service
echo    - Share download link with users
echo    - Include installation instructions
echo.
echo ================================================================
echo.
pause
