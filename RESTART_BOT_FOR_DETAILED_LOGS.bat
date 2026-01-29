@echo off
echo ========================================
echo CRITICAL: Bot Restart Required
echo ========================================
echo.
echo The detailed logging fix has been applied but the bot
echo is still running the OLD code version.
echo.
echo DETECTED ISSUE:
echo - 15+ crossovers detected in last hour
echo - ALL crashed with AttributeError
echo - Bot trying to access self.rsi_overbought (doesn't exist)
echo.
echo FIX APPLIED:
echo - Changed to self.config.get('rsi_overbought', 70)
echo - Changed to self.config.get('rsi_oversold', 30)
echo.
echo ========================================
echo RESTART STEPS:
echo ========================================
echo.
echo 1. Stop the bot:
echo    - Press Ctrl+C in the bot terminal
echo    - OR click "Stop Bot" in dashboard
echo.
echo 2. Start the bot:
echo    python start_dashboard.py
echo.
echo 3. Verify fix:
echo    - Watch for next crossover (should happen within 5-15 min)
echo    - Check logs show "RSI FILTER CHECK" without errors
echo    - Trades should start placing successfully
echo.
echo ========================================
echo EXPECTED RESULTS AFTER RESTART:
echo ========================================
echo - Detailed calculations shown in logs
echo - RSI filter checks complete successfully
echo - Trades placed when signals meet criteria
echo - With testing config (M1, 10/20 MAs), expect trades quickly
echo.
pause
