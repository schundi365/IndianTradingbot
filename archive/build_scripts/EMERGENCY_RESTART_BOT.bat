@echo off
echo ================================================================================
echo EMERGENCY BOT RESTART - CRITICAL CONFIG FIX
echo ================================================================================
echo.
echo CRITICAL BUG FIXED: Bot was loading WRONG config file!
echo.
echo The bot was loading from src/config.py (hardcoded)
echo instead of bot_config.json (your dashboard settings)
echo.
echo This is why MACD filter (and ALL settings) were ignored!
echo.
echo ================================================================================
echo.

echo Step 1: Force stopping any running bot processes...
python force_stop_and_restart.py
echo.

echo Step 2: Clearing all Python cache...
python clear_all_cache.py
echo.

echo Step 3: Waiting 5 seconds for cleanup...
timeout /t 5 /nobreak
echo.

echo Step 4: Verifying the fix is in place...
python verify_macd_fix.py
echo.

echo ================================================================================
echo READY TO START BOT WITH CORRECT CONFIG LOADING
echo ================================================================================
echo.
echo The bot will now load from bot_config.json (your dashboard settings)
echo.
echo You should see at startup:
echo   "MACD Filter: Disabled"
echo.
echo And in logs:
echo   "⚪ MACD filter: DISABLED (skipping check)"
echo.
echo Press Ctrl+C to stop the bot when needed
echo.
echo ================================================================================
echo.

python run_bot.py

pause
