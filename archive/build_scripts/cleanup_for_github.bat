@echo off
REM Cleanup script for preparing repository for GitHub
REM This removes sensitive data and temporary files

echo ================================================================
echo CLEANING UP REPOSITORY FOR GITHUB
echo ================================================================
echo.

echo Deleting configuration files with API keys...
del /Q config_nifty_futures.json 2>nul
del /Q config_banknifty_futures.json 2>nul
del /Q config_equity_intraday.json 2>nul
del /Q config_options_trading.json 2>nul
del /Q config_test_paper_trading.json 2>nul
del /Q config_paper_trading.json 2>nul
del /Q config_indian_migrated.json 2>nul
del /Q config_more_signals.json 2>nul
del /Q config_testing_mode.json 2>nul
del /Q bot_config.json 2>nul
del /Q config_backup_*.json 2>nul
del /Q bot_config_backup_*.json 2>nul

echo Deleting sensitive files...
del /Q kite_token.json 2>nul

echo Deleting log files...
del /Q *.log 2>nul

echo Deleting temporary/test files...
del /Q mock_mt5.py 2>nul
del /Q test_*.html 2>nul
del /Q simple_*.py 2>nul

echo Deleting session/task files...
del /Q SESSION_*.txt 2>nul
del /Q SESSION_*.md 2>nul
del /Q TASK_*.md 2>nul
del /Q *_SUMMARY.txt 2>nul
del /Q *_STATUS.txt 2>nul
del /Q *_COMPLETE.txt 2>nul
del /Q *_FIX*.txt 2>nul
del /Q *_IMPLEMENTATION*.md 2>nul
del /Q *_ANALYSIS*.txt 2>nul
del /Q *_GUIDE.txt 2>nul
del /Q *_REFERENCE*.txt 2>nul

echo Deleting build artifacts...
rmdir /S /Q build 2>nul
rmdir /S /Q dist 2>nul
rmdir /S /Q __pycache__ 2>nul
rmdir /S /Q .pytest_cache 2>nul
rmdir /S /Q cachedir 2>nul
rmdir /S /Q .hypothesis 2>nul

echo Deleting IDE files...
rmdir /S /Q .vscode 2>nul
rmdir /S /Q .idea 2>nul

echo.
echo ================================================================
echo CLEANUP COMPLETE!
echo ================================================================
echo.
echo Template configuration files have been created.
echo You can now safely commit to GitHub.
echo.
echo Next steps:
echo   1. Review the changes
echo   2. git add .
echo   3. git commit -m "Prepare for GitHub: Remove sensitive data"
echo   4. git push origin main
echo.
echo ================================================================

pause
