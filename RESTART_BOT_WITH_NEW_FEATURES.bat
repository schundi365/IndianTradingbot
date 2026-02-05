@echo off
echo ================================================================================
echo RESTARTING BOT WITH NEW FEATURES
echo ================================================================================
echo.
echo Session 21 Features:
echo   1. ML Confidence Filtering (ml_min_confidence = 0.6)
echo   2. Drawdown Protection (max_drawdown_percent = 10)
echo   3. Fixed Hardcoded Risk Multipliers
echo.
echo ================================================================================
echo.
echo Starting bot...
echo.

python run_bot.py

echo.
echo ================================================================================
echo Bot stopped
echo ================================================================================
pause
