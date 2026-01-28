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

REM Create START_HERE.txt for distribution
echo Creating START_HERE.txt...
(
echo ================================================================================
echo    GEM TRADING BOT - WINDOWS EDITION
echo ================================================================================
echo.
echo Thank you for downloading GEM Trading Bot!
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
echo    Build Date: %date%
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
