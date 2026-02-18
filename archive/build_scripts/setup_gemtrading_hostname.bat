@echo off
echo ================================================================
echo GEM Trading - Hostname Setup
echo ================================================================
echo.
echo This will add "gemtrading" to your hosts file.
echo You will be able to access the dashboard at: http://gemtrading:5000
echo.
echo NOTE: This requires Administrator privileges!
echo.
pause

echo.
echo Adding entry to hosts file...
echo 127.0.0.1    gemtrading >> C:\Windows\System32\drivers\etc\hosts

if %errorlevel% equ 0 (
    echo.
    echo ================================================================
    echo SUCCESS! Hostname configured.
    echo ================================================================
    echo.
    echo You can now access GEM Trading at:
    echo   http://gemtrading:5000
    echo.
    echo If the dashboard is not running, start it with:
    echo   python web_dashboard.py
    echo.
) else (
    echo.
    echo ================================================================
    echo ERROR: Failed to update hosts file.
    echo ================================================================
    echo.
    echo Please run this batch file as Administrator:
    echo   1. Right-click on setup_gemtrading_hostname.bat
    echo   2. Select "Run as administrator"
    echo.
)

pause
