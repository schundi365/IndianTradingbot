@echo off
echo ================================================================================
echo BUILDING MT5 TRADING BOT EXECUTABLE
echo ================================================================================
echo.

echo Installing PyInstaller if needed...
pip install pyinstaller --quiet
echo.

echo Building executable...
pyinstaller --onefile --name=MT5_Trading_Bot run_bot.py
echo.

echo ================================================================================
echo BUILD COMPLETE!
echo ================================================================================
echo.
echo Executable location: dist\MT5_Trading_Bot.exe
echo.
echo To distribute:
echo   1. Copy dist\MT5_Trading_Bot.exe
echo   2. Copy src\ folder (for config.py)
echo   3. User needs MT5 installed
echo.
echo ================================================================================

pause
