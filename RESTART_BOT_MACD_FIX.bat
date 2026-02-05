@echo off
echo ================================================================================
echo RESTARTING BOT WITH MACD FIX
echo ================================================================================
echo.
echo This will:
echo 1. Clear all Python cache
echo 2. Restart the bot with the MACD filter fix
echo.
echo The MACD filter is now DISABLED in your config.
echo You should see: "⚪ MACD filter: DISABLED (skipping check)" in the logs
echo.
echo ================================================================================
echo.

echo Step 1: Clearing cache...
python clear_all_cache.py
echo.

echo Step 2: Waiting 3 seconds...
timeout /t 3 /nobreak > nul
echo.

echo Step 3: Starting bot...
echo Press Ctrl+C to stop the bot when you want to exit
echo.
python run_bot.py

pause
