@echo off
echo ================================================================
echo Building GEM Trading Bot with Standardized Configuration
echo ================================================================
echo.
echo Configuration Updates:
echo   - fast_ma_period: 10
echo   - slow_ma_period: 21
echo   - dead_hours: [0, 1, 2, 17, 20, 21, 22]
echo   - golden_hours: [8, 11, 13, 14, 15, 19, 23]
echo.
echo This will create a new executable with the standardized defaults.
echo.
pause

echo.
echo Step 1: Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del /q *.spec

echo.
echo Step 2: Building executable with PyInstaller...
echo This may take 5-10 minutes...
echo.

pyinstaller --name="GEM_Trading_Bot_v2.1" ^
    --onefile ^
    --noconsole ^
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
    --hidden-import=sklearn ^
    --hidden-import=joblib ^
    --collect-all=sklearn ^
    web_dashboard.py

echo.
echo ================================================================
echo Build Complete!
echo ================================================================
echo.
echo Executable: dist\GEM_Trading_Bot_v2.1.exe
echo.
echo Configuration Standardization Applied:
echo   ✓ MA Periods: 10/21 (optimized for faster signals)
echo   ✓ Dead Hours: Removed hour 18 based on analysis
echo   ✓ Golden Hours: Unchanged (proven profitable hours)
echo.
echo Next Steps:
echo 1. Test: cd dist ^&^& GEM_Trading_Bot_v2.1.exe
echo 2. Verify configuration loads correctly
echo 3. Check that bot uses new defaults
echo.
pause
