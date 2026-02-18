@echo off
REM Deployment Test Runner for Windows
REM Runs all deployment tests and generates reports

echo ============================================================
echo Indian Market Dashboard - Deployment Test Suite
echo ============================================================
echo.

REM Change to dashboard directory
cd /d "%~dp0"

echo Step 1: Verifying deployment...
echo.
python verify_deployment.py
if errorlevel 1 (
    echo.
    echo ERROR: Deployment verification failed!
    echo Please fix the issues before running tests.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Step 2: Starting dashboard server...
echo ============================================================
echo.

REM Start dashboard in background
start /B python run_dashboard.py
set DASHBOARD_PID=%ERRORLEVEL%

REM Wait for server to start
echo Waiting for server to start...
timeout /t 10 /nobreak > nul

echo.
echo ============================================================
echo Step 3: Running deployment tests...
echo ============================================================
echo.

cd tests
python test_deployment.py --url http://localhost:8080
set TEST_RESULT=%ERRORLEVEL%

echo.
echo ============================================================
echo Step 4: Running broker tests...
echo ============================================================
echo.

python test_broker_deployment.py --url http://localhost:8080
set BROKER_TEST_RESULT=%ERRORLEVEL%

echo.
echo ============================================================
echo Test Results
echo ============================================================
echo.

if %TEST_RESULT%==0 (
    echo [PASS] Deployment tests passed
) else (
    echo [FAIL] Deployment tests failed
)

if %BROKER_TEST_RESULT%==0 (
    echo [PASS] Broker tests passed
) else (
    echo [FAIL] Broker tests failed
)

echo.
echo Test reports saved to:
echo - tests\deployment_test_report.json
echo - tests\broker_deployment_test_report.json
echo.

REM Stop dashboard server
echo Stopping dashboard server...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq run_dashboard.py*" > nul 2>&1

echo.
echo ============================================================
echo Deployment testing complete!
echo ============================================================
echo.

if %TEST_RESULT%==0 if %BROKER_TEST_RESULT%==0 (
    echo All tests PASSED!
    echo The dashboard is ready for deployment.
) else (
    echo Some tests FAILED!
    echo Please review the test reports and fix issues.
)

echo.
pause
