@echo off
REM Simple Dashboard Restart
REM Just restarts Flask server - use Incognito mode to bypass cache

echo ========================================
echo RESTARTING DASHBOARD
echo ========================================
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0restart_dashboard.ps1"

pause
