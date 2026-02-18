@echo off
REM ================================================================
REM Deploy Fixed ML Model
REM ================================================================

echo.
echo ================================================================
echo DEPLOY FIXED ML MODEL
echo ================================================================
echo.
echo This will replace the overfitted model with the fixed version.
echo.
echo BEFORE: 99.99%% accuracy (overfitted, approves everything)
echo AFTER:  62.87%% accuracy (realistic, filters 35-40%% of signals)
echo.
pause

REM Check if fixed model exists
if not exist "models\ml_signal_model_fixed.pkl" (
    echo.
    echo ERROR: Fixed model not found!
    echo Please run: python ml_training/FIX_OVERFITTING.py
    echo.
    pause
    exit /b 1
)

REM Backup old model
echo.
echo Step 1: Backing up old model...
if exist "models\ml_signal_model.pkl" (
    copy "models\ml_signal_model.pkl" "models\ml_signal_model_old.pkl" >nul
    echo OK: Old model backed up to ml_signal_model_old.pkl
) else (
    echo WARNING: No existing model found (first time setup)
)

REM Deploy fixed model
echo.
echo Step 2: Deploying fixed model...
copy "models\ml_signal_model_fixed.pkl" "models\ml_signal_model.pkl" >nul
echo OK: Fixed model deployed

REM Verify
echo.
echo Step 3: Verifying deployment...
if exist "models\ml_signal_model.pkl" (
    echo OK: Model file exists
    for %%A in ("models\ml_signal_model.pkl") do echo File size: %%~zA bytes
) else (
    echo ERROR: Deployment failed!
    pause
    exit /b 1
)

echo.
echo ================================================================
echo DEPLOYMENT COMPLETE!
echo ================================================================
echo.
echo The fixed ML model is now active.
echo.
echo NEXT STEPS:
echo.
echo 1. RESTART THE BOT:
echo    - Stop the bot if running
echo    - Wait 5 seconds
echo    - Start the bot
echo.
echo 2. CHECK THE LOGS:
echo    - Look for "ML PREDICTION" messages
echo    - Verify predictions are working
echo    - Check approval rate (should be 60-65%%)
echo.
echo 3. MONITOR FOR 1 WEEK:
echo    - Track ML approval rate
echo    - Compare win rate with/without ML
echo    - Watch for false positives
echo    - Adjust confidence if needed
echo.
echo 4. DASHBOARD SETTINGS:
echo    - Enable ML: Yes
echo    - ML Confidence: 60%% (default)
echo    - Require Agreement: 2 components
echo.
echo ================================================================
echo.
echo MODEL PERFORMANCE:
echo   Test Accuracy: 62.87%%
echo   Overfitting Gap: 2.34%% (under control)
echo   Filters: 35-40%% of signals
echo   Value: Real risk protection
echo.
echo ================================================================
echo.
echo Read ML_MODEL_FIXED_SUMMARY.md for complete details.
echo.
pause
