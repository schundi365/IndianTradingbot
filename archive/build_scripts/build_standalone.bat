@echo off
echo ================================================================
echo GEM Trading Bot - Standalone Build Script
echo ================================================================
echo.
echo This will create a standalone executable that users can run
echo without installing Python or any dependencies.
echo.
pause

echo.
echo Step 1: Installing PyInstaller...
pip install pyinstaller

echo.
echo Step 2: Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo Step 3: Building executable...
echo This may take 5-10 minutes...
echo.

pyinstaller --name="GEM_Trading_Bot" ^
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
    web_dashboard.py

echo.
echo ================================================================
echo Build Complete!
echo ================================================================
echo.
echo Executable location: dist\GEM_Trading_Bot.exe
echo File size: ~100-150 MB
echo.
echo Next steps:
echo 1. Test the executable: cd dist ^&^& GEM_Trading_Bot.exe
echo 2. Create distribution package
echo 3. Share with users!
echo.
echo Distribution package should include:
echo - dist\GEM_Trading_Bot.exe
echo - USER_GUIDE.md
echo - QUICK_START_CARD.md
echo - INSTALLATION_GUIDE.md (create this)
echo.
pause
