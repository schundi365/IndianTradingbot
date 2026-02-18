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
    --hidden-import=xgboost.compat ^
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
    --exclude-module=pytest ^
    --exclude-module=xgboost.testing ^
    --collect-all=flask ^
    --collect-all=werkzeug ^
    --collect-all=jinja2 ^
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

REM Copy START_HERE.txt template
echo Creating START_HERE.txt...
copy "START_HERE_TEMPLATE.txt" "dist\GEM_Trading_Bot_Windows\START_HERE.txt" >nul
if errorlevel 1 (
    echo WARNING: Failed to copy START_HERE.txt template
) else (
    echo START_HERE.txt created successfully
)

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
