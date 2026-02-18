@echo off
echo ================================================================
echo GEM Trading Bot - Standalone Build Script (WITH ML)
echo ================================================================
echo.
echo This will create a standalone executable with ML features
echo that users can run without installing Python or dependencies.
echo.
pause

echo.
echo Step 1: Installing build dependencies...
pip install pyinstaller

echo.
echo Step 2: Installing ML dependencies...
echo This ensures ML modules are available during build...
pip install -r requirements_ml.txt

echo.
echo Step 3: Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo Step 4: Building executable with ML support...
echo This may take 10-15 minutes due to ML libraries...
echo.

pyinstaller --name="GEM_Trading_Bot_ML" ^
    --onefile ^
    --noconsole ^
    --add-data="templates;templates" ^
    --add-data="src;src" ^
    --add-data="models;models" ^
    --hidden-import=MetaTrader5 ^
    --hidden-import=pandas ^
    --hidden-import=numpy ^
    --hidden-import=flask ^
    --hidden-import=werkzeug ^
    --hidden-import=jinja2 ^
    --hidden-import=click ^
    --hidden-import=itsdangerous ^
    --hidden-import=markupsafe ^
    --hidden-import=xgboost ^
    --hidden-import=sklearn ^
    --hidden-import=sklearn.ensemble ^
    --hidden-import=sklearn.tree ^
    --hidden-import=textblob ^
    --hidden-import=scipy ^
    --hidden-import=scipy.signal ^
    --hidden-import=scipy.stats ^
    --collect-all=xgboost ^
    --collect-all=sklearn ^
    --collect-all=textblob ^
    web_dashboard.py

echo.
echo ================================================================
echo Build Complete!
echo ================================================================
echo.
echo Executable location: dist\GEM_Trading_Bot_ML.exe
echo File size: ~200-300 MB (larger due to ML libraries)
echo.
echo Next steps:
echo 1. Test the executable: cd dist ^&^& GEM_Trading_Bot_ML.exe
echo 2. Verify ML features work
echo 3. Create distribution package
echo.
echo Distribution package should include:
echo - dist\GEM_Trading_Bot_ML.exe
echo - models\ folder (ML model files)
echo - USER_GUIDE.md
echo - ML_QUICK_START.md
echo - INSTALLATION_GUIDE.md
echo.
echo IMPORTANT: The models folder must be in the same directory
echo as the executable for ML features to work!
echo.
pause
