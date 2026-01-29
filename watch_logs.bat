@echo off
echo ================================================================================
echo LIVE LOG VIEWER - Trading Bot
echo ================================================================================
echo Watching: trading_bot.log
echo Press Ctrl+C to stop
echo ================================================================================
echo.

powershell -Command "Get-Content trading_bot.log -Wait -Tail 30 | Where-Object { $_ -notmatch '127.0.0.1|GET /api/|No trades found' }"
