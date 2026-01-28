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
echo Step 1: Installing PyInstaller...
pip install --upgrade pyinstaller
if errorlevel 1 (
    echo ERROR: Failed to install PyInstaller
    pause
    exit /b 1
)

REM Clean previous builds
echo.
echo Step 2: Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist GEM_Trading_Bot.spec del GEM_Trading_Bot.spec

REM Create build directory
if not exist build mkdir build
if not exist dist mkdir dist

REM Build executable
echo.
echo Step 3: Building Windows executable...
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
echo Step 4: Creating distribution package...

if not exist "dist\GEM_Trading_Bot_Windows" mkdir "dist\GEM_Trading_Bot_Windows"

copy "dist\GEM_Trading_Bot.exe" "dist\GEM_Trading_Bot_Windows\" >nul
copy "USER_GUIDE.md" "dist\GEM_Trading_Bot_Windows\" >nul
copy "QUICK_START_CARD.md" "dist\GEM_Trading_Bot_Windows\" >nul
copy "INSTALLATION_GUIDE_FOR_USERS.md" "dist\GEM_Trading_Bot_Windows\" >nul
copy "TROUBLESHOOTING.md" "dist\GEM_Trading_Bot_Windows\" >nul
copy "README.md" "dist\GEM_Trading_Bot_Windows\" >nul

REM Create README for distribution
echo Creating distribution README...
(
echo # GEM Trading Bot - Windows Edition
echo.
echo ## Quick Start
echo.
echo 1. Make sure MT5 is installed and running
echo 2. Double-click GEM_Trading_Bot.exe
echo 3. Open browser to http://localhost:5000
echo 4. Configure and start trading!
echo.
echo ## Documentation
echo.
echo - USER_GUIDE.md - Complete user manual
echo - QUICK_START_CARD.md - Quick reference
echo - INSTALLATION_GUIDE_FOR_USERS.md - Setup instructions
echo - TROUBLESHOOTING.md - Common issues and solutions
echo.
echo ## System Requirements
echo.
echo - Windows 10 or higher
echo - MT5 installed
echo - 4GB RAM minimum
echo - Internet connection
echo.
echo ## Support
echo.
echo For help, check TROUBLESHOOTING.md or contact support.
echo.
echo ## Version
echo.
echo Version: 2.0
echo Build Date: %date%
echo.
) > "dist\GEM_Trading_Bot_Windows\README.txt"

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
