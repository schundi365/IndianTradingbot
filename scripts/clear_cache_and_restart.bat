@echo off
REM Clear Cache and Restart Dashboard
REM This batch file runs the PowerShell script to clear cache and restart

echo ========================================
echo CLEARING CACHE AND RESTARTING DASHBOARD
echo ========================================
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0clear_cache_and_restart.ps1"

pause
